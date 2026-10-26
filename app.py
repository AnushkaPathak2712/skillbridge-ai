from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from database import db, User, Assessment, UserBadge, Badge, LearningProgress
import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# ============ DATABASE CONFIGURATION (NEON POSTGRESQL) ============
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Fix for SQLAlchemy requiring the postgresql:// scheme
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Force SQLAlchemy to use psycopg2 instead of psycopg (version 3)
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("🔗 Connected to Neon PostgreSQL Database")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillbridge.db'
    print("💾 Connected to Local SQLite Database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Gemini API setup
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

# ============ Industry Benchmarks ============
INDUSTRY_BENCHMARKS = {
    "Programming": 3.30, "Data Structures & Algorithms": 3.01, "Database Management": 3.55,
    "Web Development": 2.90, "Artificial Intelligence / ML": 2.70, "DevOps Tools": 2.95,
    "Cloud Computing": 2.41, "Networking & Linux": 2.29, "Cyber Security": 2.69,
    "Data Analytics": 2.76, "Problem Solving": 4.49, "Analytical Thinking": 4.23,
    "Communication Skills": 4.57, "Teamwork & Collaboration": 4.41,
}

COHORT_AVG = {
    "Programming": 1.69, "Data Structures & Algorithms": 1.34, "Database Management": 1.77,
    "Web Development": 1.68, "Artificial Intelligence / ML": 1.44, "DevOps Tools": 1.44,
    "Cloud Computing": 1.24, "Networking & Linux": 1.25, "Cyber Security": 1.34,
    "Data Analytics": 1.56, "Problem Solving": 2.37, "Analytical Thinking": 2.46,
    "Communication Skills": 2.46, "Teamwork & Collaboration": 2.70,
}

SKILL_LABELS = list(INDUSTRY_BENCHMARKS.keys())
SOFT_SKILLS = {"Problem Solving", "Analytical Thinking", "Communication Skills", "Teamwork & Collaboration"}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============ Helper Functions ============

def get_level_title(level):
    if level <= 2: return "Beginner"
    elif level <= 5: return "Skill Builder"
    elif level <= 8: return "Advanced Learner"
    else: return "Master"

def calculate_gaps(student_scores):
    gaps = {}
    total_weighted = 0
    total_weight = 0
    
    for skill in SKILL_LABELS:
        industry_val = INDUSTRY_BENCHMARKS[skill]
        student_val = student_scores.get(skill, 0)
        raw_gap = industry_val - student_val
        
        if raw_gap >= 2.5: tier = "Critical"
        elif raw_gap >= 1.5: tier = "High"
        elif raw_gap >= 0.8: tier = "Moderate"
        else: tier = "Low"
        
        gaps[skill] = {
            "student": student_val,
            "industry": industry_val,
            "gap": round(raw_gap, 2),
            "tier": tier
        }
        
        weight = 1.5 if skill not in SOFT_SKILLS else 1.0
        total_weighted += min(student_val / industry_val, 1.0) * weight
        total_weight += weight
    
    readiness_pct = round((total_weighted / total_weight) * 100, 1)
    return gaps, readiness_pct

def generate_roadmap(student_scores, goal, gaps, readiness_pct):
    top_gaps = sorted([(s, d['gap']) for s, d in gaps.items()], key=lambda x: x[1], reverse=True)[:3]
    
    prompt = f"""You are an expert career coach for MCA students.

RESEARCH CONTEXT: Study of 153 participants (87 students + 66 industry professionals)
Student's goal: {goal if goal else "Entry-level IT role"}
Readiness score: {readiness_pct}%

Top skill gaps to address:
{chr(10).join([f'- {skill}: gap={gap}' for skill, gap in top_gaps])}

Generate a personalized 4-week learning roadmap with:
1. Week-by-week plan focusing on top gaps
2. Specific free resources (YouTube, Coursera, etc.)
3. Daily time commitment (2-3 hours/day)
4. Weekly milestones
5. Quick wins (3 things to do today under 30 min)

Be specific, actionable, and encouraging."""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"## ⚠️ Error generating roadmap: {str(e)}\n\nPlease check your API key or try again later."

def check_and_award_badges(user_id, assessment_count=None, gap_closed=None):
    user = User.query.get(user_id)
    if not user: return []
    
    awarded = []
    all_badges = Badge.query.all()
    earned_badge_ids = [ub.badge_id for ub in UserBadge.query.filter_by(user_id=user_id).all()]
    
    for badge in all_badges:
        if badge.id in earned_badge_ids: continue
        
        earned = False
        if badge.condition_type == "assessment_count" and assessment_count:
            if assessment_count >= int(badge.condition_value): earned = True
        elif badge.condition_type == "gap_closed" and gap_closed:
            if gap_closed >= 1.5: earned = True
        elif badge.condition_type == "roadmap_count":
            roadmap_count = Assessment.query.filter_by(user_id=user_id).count()
            if roadmap_count >= int(badge.condition_value): earned = True
        
        if earned:
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
            db.session.add(user_badge)
            user.total_xp += badge.xp_reward
            
            new_level = 1 + (user.total_xp // 200)
            if new_level > user.level:
                user.level = new_level
            awarded.append(badge)
    
    db.session.commit()
    return awarded

# ============ Routes ============

@app.route('/')
def landing(): return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'faculty': return redirect(url_for('faculty_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed, role=role)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student': return redirect(url_for('faculty_dashboard'))
    
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    badges = [Badge.query.get(ub.badge_id) for ub in user_badges]
    
    xp_in_current_level = current_user.total_xp % 200
    xp_needed = 200 - xp_in_current_level
    next_level = current_user.level + 1
    
    return render_template('student_dashboard.html', 
                         assessments=assessments, badges=badges,
                         xp_needed=xp_needed, next_level=next_level,
                         get_level_title=get_level_title)

@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty': return redirect(url_for('student_dashboard'))
    
    students = User.query.filter_by(role='student').all()
    students_data = []
    
    for student in students:
        assessments_list = []
        for assessment in student.assessments:
            assessments_list.append({
                'id': assessment.id,
                'profile_name': assessment.profile_name,
                'goal': assessment.goal,
                'readiness_score': assessment.readiness_score,
                'created_at': assessment.created_at.strftime('%b %d, %Y') if assessment.created_at else 'N/A',
                'created_at_raw': assessment.created_at.isoformat() if assessment.created_at else None,
                'scores': assessment.get_scores_dict()
            })
        
        students_data.append({
            'id': student.id, 'name': student.name, 'email': student.email,
            'total_xp': student.total_xp, 'level': student.level, 'assessments': assessments_list
        })
    
    skill_gaps = {skill: [] for skill in SKILL_LABELS}
    for student in students:
        latest = Assessment.query.filter_by(user_id=student.id).order_by(Assessment.created_at.desc()).first()
        if latest:
            scores = latest.get_scores_dict()
            for skill in SKILL_LABELS:
                skill_gaps[skill].append(INDUSTRY_BENCHMARKS[skill] - scores.get(skill, 0))
    
    avg_gaps = {skill: round(sum(g)/len(g), 2) if g else 0 for skill, g in skill_gaps.items()}
    sorted_gaps = sorted(avg_gaps.items(), key=lambda x: x[1], reverse=True)
    
    return render_template('faculty_dashboard.html', 
                         students=students_data, sorted_gaps=sorted_gaps,
                         total_students=len(students), industry_bench=INDUSTRY_BENCHMARKS)

@app.route('/assessment/new', methods=['GET', 'POST'])
@login_required
def new_assessment():
    if request.method == 'POST':
        profile_name = request.form.get('profile_name', 'Current')
        goal = request.form.get('goal', '')
        
        scores = {}
        for skill in SKILL_LABELS:
            scores[skill] = float(request.form.get(skill, '1'))
        
        gaps, readiness = calculate_gaps(scores)
        
        assessment = Assessment(user_id=current_user.id, profile_name=profile_name, goal=goal, readiness_score=readiness)
        assessment.set_scores_dict(scores)
        db.session.add(assessment)
        db.session.commit()
        
        session['current_assessment_id'] = assessment.id
        assessment_count = Assessment.query.filter_by(user_id=current_user.id).count()
        check_and_award_badges(current_user.id, assessment_count=assessment_count)
        
        return redirect(url_for('gap_analysis'))
    return render_template('assessment.html', skills=SKILL_LABELS)

@app.route('/gap-analysis')
@login_required
def gap_analysis():
    assessment_id = session.get('current_assessment_id')
    if not assessment_id: return redirect(url_for('new_assessment'))
    
    assessment = Assessment.query.get(assessment_id)
    scores = assessment.get_scores_dict()
    gaps, readiness = calculate_gaps(scores)
    
    job_roles = {
        "Frontend Developer": ["Web Development", "Problem Solving"],
        "Backend Developer": ["Programming", "Database Management", "Data Structures & Algorithms"],
        "Full Stack Developer": ["Web Development", "Programming", "Database Management"],
        "Data Analyst": ["Data Analytics", "Database Management", "Problem Solving"],
        "DevOps Engineer": ["DevOps Tools", "Cloud Computing", "Networking & Linux"],
        "AI/ML Engineer": ["Artificial Intelligence / ML", "Programming", "Data Analytics"],
        "Security Analyst": ["Cyber Security", "Networking & Linux", "Programming"],
    }
    
    matches = []
    for role, required in job_roles.items():
        match_score = sum(1 for skill in required if gaps[skill]['gap'] < 1.5)
        if match_score >= len(required) * 0.6:
            matches.append(role)
    
    return render_template('gap_analysis.html', 
                         gaps=gaps, readiness=readiness, scores=scores,
                         matches=matches[:3], skills=SKILL_LABELS,
                         industry_bench=INDUSTRY_BENCHMARKS)

@app.route('/generate-roadmap', methods=['POST'])
@login_required
def generate_roadmap_route():
    assessment_id = session.get('current_assessment_id')
    if not assessment_id: return jsonify({'error': 'No assessment found'}), 400
    
    assessment = Assessment.query.get(assessment_id)
    scores = assessment.get_scores_dict()
    gaps, readiness = calculate_gaps(scores)
    
    roadmap = generate_roadmap(scores, assessment.goal, gaps, readiness)
    assessment.roadmap = roadmap
    db.session.commit()
    
    return jsonify({'roadmap': roadmap})

@app.route('/roadmap')
@login_required
def view_roadmap():
    assessment_id = session.get('current_assessment_id')
    if not assessment_id: return redirect(url_for('new_assessment'))
    
    assessment = Assessment.query.get(assessment_id)
    scores = assessment.get_scores_dict()
    gaps, readiness = calculate_gaps(scores)
    
    return render_template('roadmap.html', assessment=assessment, readiness=readiness, gaps=gaps)

@app.route('/compare/<int:id1>/<int:id2>')
@login_required
def compare_assessments(id1, id2):
    assessment1 = Assessment.query.get_or_404(id1)
    assessment2 = Assessment.query.get_or_404(id2)
    
    if assessment1.user_id != current_user.id or assessment2.user_id != current_user.id:
        flash('You can only compare your own assessments', 'danger')
        return redirect(url_for('student_dashboard'))
    
    scores1 = assessment1.get_scores_dict()
    scores2 = assessment2.get_scores_dict()
    
    differences = {skill: round(scores2.get(skill, 0) - scores1.get(skill, 0), 2) for skill in SKILL_LABELS}
    
    return render_template('compare.html', assessment1=assessment1, assessment2=assessment2, differences=differences)

@app.route('/save-progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    assessment_id = data.get('assessment_id')
    week = data.get('week')
    completed = data.get('completed_tasks', [])
    
    progress = LearningProgress.query.filter_by(user_id=current_user.id, assessment_id=assessment_id, week=week).first()
    if not progress:
        progress = LearningProgress(user_id=current_user.id, assessment_id=assessment_id, week=week)
        db.session.add(progress)
    
    progress.completed_tasks = json.dumps(completed)
    progress.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/export-pdf/<int:assessment_id>')
@login_required
def export_pdf(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    scores = assessment.get_scores_dict()
    gaps, readiness = calculate_gaps(scores)
    return render_template('print_roadmap.html', assessment=assessment, gaps=gaps, readiness=readiness)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎯 SkillBridge AI - Personalized Learning Roadmap Generator")
    print("="*50)
    print(f"🌐 Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)