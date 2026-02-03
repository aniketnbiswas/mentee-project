from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Index

# Universal JSON type (Safe for SQLite & Postgres)
JSON_TYPE = db.JSON

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    identity = db.relationship('UserIdentity', backref='user', uselist=False)

class UserIdentity(db.Model):
    __tablename__ = 'user_identities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    archetype_name = db.Column(db.String(64))
    core_traits = db.Column(JSON_TYPE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    # Structured Data
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    
    # Visuals
    mood = db.Column(db.String(20)) 
    performance_score = db.Column(db.Integer) 
    
    # Content
    content = db.Column(JSON_TYPE)
    
    is_gap_day = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uix_user_journal_date'),
        Index('idx_user_date', 'user_id', 'date'),
    )

    def to_dict(self):
        return {
            "date": self.date,
            "mood": self.mood,
            "score": self.performance_score,
            "content": self.content or {},
            "updated_at": self.updated_at.isoformat()
        }

class DrillSession(db.Model):
    __tablename__ = 'drill_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drill_id = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float)
    level_reached = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    meta_data = db.Column(JSON_TYPE) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)