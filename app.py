from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from markupsafe import Markup
from config import config
from models import db, User, TrainingSession
from scenario_manager import scenario_manager
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

    with app.app_context():
        db.create_all()

        if User.query.filter_by(role='admin').first() is None:
            from models import create_default_admin
            create_default_admin()
            print("✅ Default admin created")

    register_blueprints(app)

    register_error_handlers(app)

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

        sessions = TrainingSession.query.filter_by(user_id=current_user.id, status='completed').order_by(TrainingSession.completed_at.desc()).all()
        completed_count = len(sessions)
        avg_score = sum(s.score for s in sessions if s.score) / len([s for s in sessions if s.score]) if sessions else 0

        for session in sessions:
            scenario_data = scenario_manager.get_scenario(str(session.scenario_id))
            session.scenario_title = scenario_data.get('title', f'Scenario {session.scenario_id}') if scenario_data else f'Scenario {session.scenario_id}'

        return render_template('dashboard.html', user=current_user, sessions=sessions, completed_count=completed_count, avg_score=avg_score)

    @app.context_processor
    def inject_user():
        """Inject current user and config into all templates"""
        return dict(
            current_user=current_user,
            timezone_offset=app.config.get('TIMEZONE_OFFSET', 1)
        )

    return app

def register_blueprints(app):

    try:
        from routes.auth import auth_bp
        from routes.scenarios import scenario_bp
        from routes.admin import admin_bp
        from assistant.routes import assistant_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(scenario_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(assistant_bp)

        print("Blueprints registered successfully")
    except ImportError as e:
        print(f"Could not import blueprints: {e}")
        print("   Creating basic routes instead...")

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

if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*50)
    print("🚀 Don't Panic - Incident Response Training")
    print("="*50)
    print(f"🌐 Running on: http://localhost:5000")
    print(f"🔧 Environment: {app.config['ENV']}")
    print(f"🐛 Debug mode: {app.config['DEBUG']}")
    print("="*50 + "\n")

    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))

    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )
