import os
from datetime import timedelta
from cryptography.fernet import Fernet

basedir = os.path.abspath(os.path.dirname(__file__))

# Load or create encryption key
def get_or_create_encryption_key():
    """Get encryption key from environment or create/load from file"""
    # First check environment variable
    if os.environ.get('ENCRYPTION_KEY'):
        return os.environ.get('ENCRYPTION_KEY')
    
    # Then check if key file exists
    key_file = os.path.join(basedir, 'instance', '.encryption_key')
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read().strip()
    
    # Generate new key and save it
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    new_key = Fernet.generate_key().decode()
    with open(key_file, 'w') as f:
        f.write(new_key)
    print(f"✅ Generated and saved encryption key to {key_file}")
    return new_key

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    ENCRYPTION_KEY = get_or_create_encryption_key()

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'users_training.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SCENARIOS_FOLDER = os.path.join(basedir, 'scenarios')

    TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET', 1))

    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
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
    SESSION_COOKIE_SECURE = True

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
