"""
Database Models for SkillBridge AI
Defines all database tables and relationships for the application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

# Initialize SQLAlchemy (will be imported in app.py)
db = SQLAlchemy()


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin, db.Model):
    """User account model - supports both students and faculty"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'faculty'
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_full_name(self):
        return self.name
    
    def get_initials(self):
        return ''.join([n[0].upper() for n in self.name.split()[:2]])
    
    def calculate_level(self):
        """Calculate level based on total XP (100 XP per level)"""
        return 1 + (self.total_xp // 100)
    
    def get_xp_for_next_level(self):
        """Get XP needed for next level"""
        current_level_xp = (self.level - 1) * 100
        return 100 - (self.total_xp - current_level_xp)
    
    def get_progress_percentage(self):
        """Get progress percentage to next level"""
        current_level_xp = (self.level - 1) * 100
        progress = self.total_xp - current_level_xp
        return min(100, int((progress / 100) * 100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'total_xp': self.total_xp,
            'level': self.level,
            'streak_days': self.streak_days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================
# ASSESSMENT MODEL
# ============================================================

class Assessment(db.Model):
    """Skill assessment model - stores user's skill ratings"""
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    profile_name = db.Column(db.String(50), nullable=False, default='Current Profile')
    goal = db.Column(db.String(200))
    scores = db.Column(db.Text, nullable=False)  # JSON string of skill scores
    readiness_score = db.Column(db.Float, default=0.0)
    roadmap = db.Column(db.Text, nullable=True)  # Store generated roadmap
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_scores_dict(self):
        """Parse JSON scores into dictionary"""
        if self.scores:
            return json.loads(self.scores)
        return {}
    
    def set_scores_dict(self, scores_dict):
        """Store scores dictionary as JSON string"""
        self.scores = json.dumps(scores_dict)
    
    def get_top_gaps(self, industry_benchmarks):
        """Calculate top 3 skill gaps based on industry benchmarks"""
        scores = self.get_scores_dict()
        gaps = {}
        for skill, student_score in scores.items():
            industry_score = industry_benchmarks.get(skill, 3.0)
            gap = industry_score - student_score
            gaps[skill] = round(gap, 2)
        
        # Sort by gap descending and return top 3
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
        return sorted_gaps[:3]
    
    def get_weakest_skills(self, top_n=3):
        """Get the lowest rated skills"""
        scores = self.get_scores_dict()
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        return sorted_scores[:top_n]
    
    def get_strongest_skills(self, top_n=3):
        """Get the highest rated skills"""
        scores = self.get_scores_dict()
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_name': self.profile_name,
            'goal': self.goal,
            'scores': self.get_scores_dict(),
            'readiness_score': self.readiness_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================
# BADGE MODEL
# ============================================================

class Badge(db.Model):
    """Achievement badge model"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(10), default='🏆')
    xp_reward = db.Column(db.Integer, default=50)
    condition_type = db.Column(db.String(50))  # 'assessment_count', 'gap_closed', 'streak', etc.
    condition_value = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('UserBadge', backref='badge', lazy='dynamic')
    
    def __repr__(self):
        return f'<Badge {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'xp_reward': self.xp_reward
        }


# ============================================================
# USER BADGE MODEL (Junction Table)
# ============================================================

class UserBadge(db.Model):
    """Tracks which badges each user has earned"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),
    )
    
    def to_dict(self):
        return {
            'badge': self.badge.to_dict() if self.badge else None,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }


# ============================================================
# LEARNING PROGRESS MODEL
# ============================================================

class LearningProgress(db.Model):
    """Tracks weekly learning progress for each assessment"""
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)  # Week number (1-12)
    skills_improved = db.Column(db.Text, nullable=True)  # JSON of skills and improvements
    completed_tasks = db.Column(db.Text, nullable=True)  # JSON of completed tasks
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_skills_improved_dict(self):
        """Parse JSON skills_improved into dictionary"""
        if self.skills_improved:
            return json.loads(self.skills_improved)
        return {}
    
    def set_skills_improved_dict(self, skills_dict):
        """Store skills_improved as JSON string"""
        self.skills_improved = json.dumps(skills_dict)
    
    def get_completed_tasks_list(self):
        """Parse JSON completed_tasks into list"""
        if self.completed_tasks:
            return json.loads(self.completed_tasks)
        return []
    
    def set_completed_tasks_list(self, tasks_list):
        """Store completed_tasks as JSON string"""
        self.completed_tasks = json.dumps(tasks_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'week': self.week,
            'skills_improved': self.get_skills_improved_dict(),
            'completed_tasks': self.get_completed_tasks_list(),
            'notes': self.notes,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============================================================
# SKILL GAP HISTORY MODEL (for tracking improvement over time)
# ============================================================

class SkillGapHistory(db.Model):
    """Historical record of skill gaps for trend analysis"""
    __tablename__ = 'skill_gap_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    student_score = db.Column(db.Float, default=0.0)
    industry_benchmark = db.Column(db.Float, default=0.0)
    gap = db.Column(db.Float, default=0.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'skill_name': self.skill_name,
            'student_score': self.student_score,
            'industry_benchmark': self.industry_benchmark,
            'gap': self.gap,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }


# ============================================================
# RESOURCE RECOMMENDATION MODEL (for future expansion)
# ============================================================

class ResourceRecommendation(db.Model):
    """Recommended learning resources for specific skills"""
    __tablename__ = 'resource_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500))
    platform = db.Column(db.String(50))  # YouTube, Coursera, Udemy, etc.
    type = db.Column(db.String(20))  # video, article, course, practice
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration_mins = db.Column(db.Integer)
    is_free = db.Column(db.Boolean, default=True)
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'title': self.title,
            'url': self.url,
            'platform': self.platform,
            'type': self.type,
            'difficulty': self.difficulty,
            'duration_mins': self.duration_mins,
            'is_free': self.is_free,
            'upvotes': self.upvotes
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def init_default_badges():
    """Create default badges if they don't exist"""
    default_badges = [
        {
            'name': 'First Assessment',
            'description': 'Complete your first skill assessment',
            'icon': '🎯',
            'xp_reward': 50,
            'condition_type': 'assessment_count',
            'condition_value': '1'
        },
        {
            'name': 'Gap Closer',
            'description': 'Reduce a critical skill gap by 1.5+ points',
            'icon': '📊',
            'xp_reward': 100,
            'condition_type': 'gap_closed',
            'condition_value': '1.5'
        },
        {
            'name': 'Roadmap Explorer',
            'description': 'Generate 3 learning roadmaps',
            'icon': '🗺️',
            'xp_reward': 60,
            'condition_type': 'roadmap_count',
            'condition_value': '3'
        },
        {
            'name': 'Skill Master',
            'description': 'Reach Expert level (4/4) in any skill',
            'icon': '🏆',
            'xp_reward': 150,
            'condition_type': 'skill_level',
            'condition_value': '4'
        },
        {
            'name': 'Consistent Learner',
            'description': 'Track progress for 4 consecutive weeks',
            'icon': '📅',
            'xp_reward': 80,
            'condition_type': 'weeks_tracked',
            'condition_value': '4'
        },
        {
            'name': 'Job Ready',
            'description': 'Achieve 70%+ industry readiness score',
            'icon': '💼',
            'xp_reward': 200,
            'condition_type': 'readiness_score',
            'condition_value': '70'
        },
        {
            'name': 'Streak Master',
            'description': 'Maintain a 7-day learning streak',
            'icon': '🔥',
            'xp_reward': 75,
            'condition_type': 'streak',
            'condition_value': '7'
        },
        {
            'name': 'All-Rounder',
            'description': 'Score 3+ in all 14 skills',
            'icon': '🌟',
            'xp_reward': 300,
            'condition_type': 'all_skills',
            'condition_value': '3'
        }
    ]
    
    for badge_data in default_badges:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()