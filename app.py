from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from markupsafe import Markup
from config import config
from models import db, User
import os
import json

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    

    @app.template_filter('format_json')
    def format_json(json_string):
        """Format JSON string with proper indentation - mark as safe to prevent escaping"""
        try:
            parsed = json.loads(json_string)
            formatted = json.dumps(parsed, indent=2)
            return Markup(formatted)
        except (json.JSONDecodeError, TypeError):
            return Markup(json_string)
    
    # Create database tables
    with app.app_context():
        db.create_all()  # Creates tables in both databases based on __bind_key__
        
        # Create default admin if none exists
        if User.query.filter_by(role='admin').first() is None:
            from models import create_default_admin
            create_default_admin()
            print("✅ Default admin created")
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Main routes
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard - redirects based on role"""
        if current_user.role in ['instructor', 'admin']:
            return redirect(url_for('admin.dashboard'))
        return render_template('dashboard.html', user=current_user)
    
    # Context processor - makes variables available to all templates
    @app.context_processor
    def inject_user():
        """Inject current user and config into all templates"""
        return dict(
            current_user=current_user,
            timezone_offset=app.config.get('TIMEZONE_OFFSET', 1)
        )
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    
    try:
        from routes.auth import auth_bp
        from routes.scenarios import scenario_bp
        from routes.admin import admin_bp
        from assistant.routes import assistant_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(scenario_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(assistant_bp)
        
        print("✅ Blueprints registered successfully")
    except ImportError as e:
        print(f"⚠️  Could not import blueprints: {e}")
        print("   Creating basic routes instead...")
        
        # Fallback: Create basic routes if blueprints don't exist
        @app.route('/login')
        def login():
            return "Login page - Blueprint not yet created"
        
        @app.route('/scenarios')
        def scenarios():
            return "Scenarios page - Blueprint not yet created"

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        return render_template('errors/403.html'), 403

# Run the application
if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*50)
    print("🚀 Don't Panic - Incident Response Training")
    print("="*50)
    print(f"🌐 Running on: http://localhost:5000")
    print(f"🔧 Environment: {app.config['ENV']}")
    print(f"🐛 Debug mode: {app.config['DEBUG']}")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',  # Accessible from network
        port=5000,
        debug=True
    )
