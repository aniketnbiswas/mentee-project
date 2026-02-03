import os

class Config:
    # Key for securing cookies (keep this secret in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-mentee'
    # SQLite database location
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mentee.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False