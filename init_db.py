"""
Database Initialization Script
Run this file once to create the database and tables
"""

from app import app, db
from database import User, Assessment, Badge, UserBadge, LearningProgress
from flask_bcrypt import Bcrypt
from datetime import datetime

def init_database():
    """Create all tables and populate with initial data"""
    
    with app.app_context():
        # Drop all existing tables (comment this out if you want to keep existing data)
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables fresh
        print("📦 Creating database tables...")
        db.create_all()
        
        # Initialize bcrypt for password hashing
        bcrypt = Bcrypt(app)
        
        # ============ Create Badges ============
        print("🏆 Creating achievement badges...")
        
        badges = [
            Badge(
                name="First Assessment",
                description="Complete your first skill assessment",
                icon="🎯",
                xp_reward=50,
                condition_type="assessment_count",
                condition_value="1"
            ),
            Badge(
                name="Gap Closer",
                description="Close a critical skill gap (reduce gap by 1.5+ points)",
                icon="📊",
                xp_reward=100,
                condition_type="gap_closed",
                condition_value="1.5"
            ),
            Badge(
                name="Roadmap Explorer",
                description="Generate 3 learning roadmaps",
                icon="🗺️",
                xp_reward=60,
                condition_type="roadmap_count",
                condition_value="3"
            ),
            Badge(
                name="Skill Master",
                description="Reach Expert level (4/4) in any technical skill",
                icon="🏆",
                xp_reward=150,
                condition_type="skill_level",
                condition_value="4"
            ),
            Badge(
                name="Consistent Learner",
                description="Track your progress for 4 weeks",
                icon="📅",
                xp_reward=80,
                condition_type="weeks_tracked",
                condition_value="4"
            ),
            Badge(
                name="Job Ready",
                description="Achieve 70%+ industry readiness score",
                icon="💼",
                xp_reward=200,
                condition_type="readiness_score",
                condition_value="70"
            ),
        ]
        
        for badge in badges:
            db.session.add(badge)
        
        # ============ Create Demo Users ============
        print("👥 Creating demo user accounts...")
        
        # Faculty Account
        faculty_password = bcrypt.generate_password_hash("faculty123").decode('utf-8')
        faculty = User(
            name="Professor Sharma",
            email="faculty@skillbridge.com",
            password=faculty_password,
            role="faculty",
            total_xp=0,
            level=1
        )
        db.session.add(faculty)
        
        # Student Account 1
        student1_password = bcrypt.generate_password_hash("student123").decode('utf-8')
        student1 = User(
            name="Anushka Pathak",
            email="student@skillbridge.com",
            password=student1_password,
            role="student",
            total_xp=120,
            level=2
        )
        db.session.add(student1)
        
        # Student Account 2 (for faculty dashboard demo)
        student2_password = bcrypt.generate_password_hash("test123").decode('utf-8')
        student2 = User(
            name="Nandini Naik",
            email="nandini@example.com",
            password=student2_password,
            role="student",
            total_xp=80,
            level=1
        )
        db.session.add(student2)
        
        # Student Account 3
        student3_password = bcrypt.generate_password_hash("test123").decode('utf-8')
        student3 = User(
            name="Prerna Panda",
            email="prerna@example.com",
            password=student3_password,
            role="student",
            total_xp=200,
            level=2
        )
        db.session.add(student3)
        
        db.session.commit()
        
        # ============ Create Sample Assessments ============
        print("📝 Creating sample skill assessments...")
        
        # Sample scores for Student 1 (Anushka)
        sample_scores_1 = {
            "Programming": 1.7,
            "Data Structures & Algorithms": 1.3,
            "Database Management": 1.0,
            "Web Development": 2.5,
            "Artificial Intelligence / ML": 1.4,
            "DevOps Tools": 1.0,
            "Cloud Computing": 1.2,
            "Networking & Linux": 1.3,
            "Cyber Security": 1.0,
            "Data Analytics": 1.6,
            "Problem Solving": 2.4,
            "Analytical Thinking": 2.5,
            "Communication Skills": 2.5,
            "Teamwork & Collaboration": 3.0
        }
        
        import json
        assessment1 = Assessment(
            user_id=student1.id,
            profile_name="Current Profile",
            goal="Full Stack Developer",
            readiness_score=38.5
        )
        assessment1.set_scores_dict(sample_scores_1)
        db.session.add(assessment1)
        
        # Target assessment for Student 1
        target_scores = {
            "Programming": 3.0,
            "Data Structures & Algorithms": 2.8,
            "Database Management": 3.2,
            "Web Development": 3.5,
            "Artificial Intelligence / ML": 2.5,
            "DevOps Tools": 2.5,
            "Cloud Computing": 2.8,
            "Networking & Linux": 2.5,
            "Cyber Security": 2.5,
            "Data Analytics": 2.8,
            "Problem Solving": 3.5,
            "Analytical Thinking": 3.5,
            "Communication Skills": 3.8,
            "Teamwork & Collaboration": 4.0
        }
        
        assessment2 = Assessment(
            user_id=student1.id,
            profile_name="Target Profile (8 weeks)",
            goal="Full Stack Developer",
            readiness_score=72.0
        )
        assessment2.set_scores_dict(target_scores)
        db.session.add(assessment2)
        
        # Sample scores for Student 2 (Nandini)
        sample_scores_2 = {
            "Programming": 2.0,
            "Data Structures & Algorithms": 1.8,
            "Database Management": 2.2,
            "Web Development": 2.0,
            "Artificial Intelligence / ML": 1.5,
            "DevOps Tools": 1.2,
            "Cloud Computing": 1.5,
            "Networking & Linux": 1.8,
            "Cyber Security": 1.5,
            "Data Analytics": 1.8,
            "Problem Solving": 2.8,
            "Analytical Thinking": 2.8,
            "Communication Skills": 3.0,
            "Teamwork & Collaboration": 3.5
        }
        
        assessment3 = Assessment(
            user_id=student2.id,
            profile_name="Current",
            goal="Data Analyst",
            readiness_score=45.0
        )
        assessment3.set_scores_dict(sample_scores_2)
        db.session.add(assessment3)
        
        # Sample scores for Student 3 (Prerna)
        sample_scores_3 = {
            "Programming": 1.2,
            "Data Structures & Algorithms": 1.0,
            "Database Management": 0.8,
            "Web Development": 1.5,
            "Artificial Intelligence / ML": 1.0,
            "DevOps Tools": 0.8,
            "Cloud Computing": 1.0,
            "Networking & Linux": 1.0,
            "Cyber Security": 0.8,
            "Data Analytics": 1.2,
            "Problem Solving": 2.0,
            "Analytical Thinking": 2.0,
            "Communication Skills": 2.2,
            "Teamwork & Collaboration": 2.5
        }
        
        assessment4 = Assessment(
            user_id=student3.id,
            profile_name="Current",
            goal="DevOps Engineer",
            readiness_score=28.0
        )
        assessment4.set_scores_dict(sample_scores_3)
        db.session.add(assessment4)
        
        db.session.commit()
        
        # ============ Award some sample badges ============
        print("🎖️ Awarding sample badges...")
        
        # Award First Assessment badge to Student 1
        badge1 = Badge.query.filter_by(condition_type="assessment_count", condition_value="1").first()
        if badge1:
            user_badge = UserBadge(user_id=student1.id, badge_id=badge1.id)
            db.session.add(user_badge)
        
        # Award Gap Closer badge to Student 1 (they improved in target)
        badge2 = Badge.query.filter_by(condition_type="gap_closed", condition_value="1.5").first()
        if badge2:
            user_badge = UserBadge(user_id=student1.id, badge_id=badge2.id)
            db.session.add(user_badge)
        
        db.session.commit()
        
        # ============ Summary ============
        print("\n" + "="*50)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print("\n📊 Database created at: instance/skillbridge.db")
        print("\n👥 DEMO ACCOUNTS:")
        print("   ┌─────────────────────────────────────────────────┐")
        print("   │ STUDENT ACCOUNTS:                               │")
        print("   │   📧 student@skillbridge.com / student123       │")
        print("   │   📧 nandini@example.com / test123              │")
        print("   │   📧 prerna@example.com / test123               │")
        print("   │                                                 │")
        print("   │ FACULTY ACCOUNT:                                │")
        print("   │   📧 faculty@skillbridge.com / faculty123       │")
        print("   └─────────────────────────────────────────────────┘")
        print("\n🏆 BADGES CREATED: 6")
        print("📝 SAMPLE ASSESSMENTS: 4")
        print("\n🚀 Next step: Run 'python app.py' to start the server!")
        print("="*50)

if __name__ == "__main__":
    init_database()