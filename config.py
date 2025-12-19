import os
from datetime import timedelta
from cryptography.fernet import Fernet

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Encryption key for sensitive fields (username, email)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key().decode()
    
    # Database settings - Single database for users and training sessions
    # (Scenarios are stored as JSON files in the scenarios folder)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'users_training.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scenarios folder for file-based storage
    SCENARIOS_FOLDER = os.path.join(basedir, 'scenarios')
    
    # Timezone settings (UTC offset in hours)
    # Set to your local timezone offset. For example:
    # UTC+1 (Europe/Berlin, Europe/Paris): TIMEZONE_OFFSET = 1
    # UTC+2 (Europe/Berlin DST): TIMEZONE_OFFSET = 2
    # Set to 0 to use UTC
    TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET', 1))  # Default to UTC+1
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Upload settings (for future features)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
