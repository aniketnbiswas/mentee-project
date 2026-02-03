from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions globally
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURATION ---
    # In production, change this to a secure random string
    app.config['SECRET_KEY'] = 'dev-secret-key-mental-gym'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mentee.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INIT EXTENSIONS ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure Login Behavior
    login_manager.login_view = 'auth.login'  # Where to send non-logged-in users
    login_manager.login_message_category = 'info'

    # --- USER LOADER ---
    # This tells Flask-Login how to find a specific user from the ID stored in the session
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- REGISTER BLUEPRINTS ---
    from .blueprints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .blueprints.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .blueprints.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    # --- CREATE DATABASE ---
    with app.app_context():
        db.create_all()

    return app