from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'faculty'
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    badges = db.relationship('UserBadge', backref='user', lazy=True)

# Assessment Model (saved skill profiles)
class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_name = db.Column(db.String(50), nullable=False)  # 'Current', 'Target', etc.
    goal = db.Column(db.String(200))
    scores = db.Column(db.Text, nullable=False)  # JSON string
    readiness_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_scores_dict(self):
        return json.loads(self.scores)
    
    def set_scores_dict(self, scores_dict):
        self.scores = json.dumps(scores_dict)

# Badges Model
class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(10))
    xp_reward = db.Column(db.Integer, default=50)
    condition_type = db.Column(db.String(50))  # 'first_assessment', 'gap_closed', etc.
    condition_value = db.Column(db.String(100))

# User Badges (earned)
class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Learning Progress Tracking
class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'))
    week = db.Column(db.Integer)  # 1-12
    skills_improved = db.Column(db.Text)  # JSON of improvements
    completed_tasks = db.Column(db.Text)  # JSON of completed tasks
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)