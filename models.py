from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ========================
# 1. USERS TABLE
# ========================
class User(UserMixin, db.Model):
    """User accounts - both trainees and instructors"""
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User credentials
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User role
    role = db.Column(db.String(20), nullable=False, default='trainee')
    # Options: 'trainee' or 'instructor'
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    training_sessions = db.relationship('TrainingSession', 
                                       backref='user', 
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    
    created_scenarios = db.relationship('Scenario',
                                       backref='creator',
                                       lazy='dynamic',
                                       foreign_keys='Scenario.created_by')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_instructor(self):
        """Check if user is an instructor"""
        return self.role == 'instructor'
    
    def get_completed_scenarios_count(self):
        """Get number of completed scenarios"""
        return self.training_sessions.filter_by(status='completed').count()
    
    def get_average_score(self):
        """Calculate average score across all completed sessions"""
        completed = self.training_sessions.filter_by(status='completed').all()
        if not completed:
            return 0
        total = sum(session.score for session in completed if session.score)
        return round(total / len(completed), 2)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


# ========================
# 2. SCENARIOS TABLE
# ========================
class Scenario(db.Model):
    """Training scenarios/exercises"""
    __tablename__ = 'scenarios'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Scenario information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Categorization
    incident_type = db.Column(db.String(50), nullable=False)
    # Options: 'ransomware', 'data_breach', 'ddos', 'phishing', 'insider_threat', etc.
    
    difficulty_level = db.Column(db.Integer, nullable=False, default=1)
    # Scale: 1 (easy) to 5 (very hard)
    
    estimated_time = db.Column(db.Integer, nullable=False, default=30)
    # Time in minutes
    
    # Maximum points for the scenario (used to scale final score)
    max_points = db.Column(db.Integer, nullable=False, default=100)
    
    # Scenario content (JSON stored as text)
    scenario_content = db.Column(db.Text, nullable=False)
    # This will store the decision tree/story branches as JSON
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Statistics
    times_played = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    
    # Relationships
    training_sessions = db.relationship('TrainingSession',
                                       backref='scenario',
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    
    def increment_play_count(self):
        """Increment the times_played counter"""
        self.times_played += 1
    
    def update_average_score(self):
        """Recalculate average score from all completed sessions"""
        completed = self.training_sessions.filter_by(status='completed').all()
        if not completed:
            self.average_score = 0.0
            return
        
        total = sum(session.score for session in completed if session.score)
        self.average_score = round(total / len(completed), 2)
    
    def get_completion_rate(self):
        """Calculate percentage of started sessions that were completed"""
        total = self.training_sessions.count()
        if total == 0:
            return 0
        completed = self.training_sessions.filter_by(status='completed').count()
        return round((completed / total) * 100, 2)
    
    def __repr__(self):
        return f'<Scenario {self.title} (Level {self.difficulty_level})>'


# ========================
# 3. TRAINING SESSIONS TABLE
# ========================
class TrainingSession(db.Model):
    """Individual training session records"""
    __tablename__ = 'training_sessions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False, index=True)
    
    # Session timing
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # Time in seconds
    
    # Results
    score = db.Column(db.Integer, default=0)  # Score out of 100
    outcome = db.Column(db.String(50))
    # Options: 'success', 'partial_success', 'neutral', 'failure', 'catastrophic'
    
    # Session status
    status = db.Column(db.String(20), nullable=False, default='in_progress')
    # Options: 'in_progress', 'completed', 'abandoned'
    
    # Session data (JSON stored as text)
    session_data = db.Column(db.Text)
    # Stores decisions made, path taken, etc. as JSON
    
    # Performance metrics
    detection_score = db.Column(db.Integer, default=0)
    containment_score = db.Column(db.Integer, default=0)
    eradication_score = db.Column(db.Integer, default=0)
    recovery_score = db.Column(db.Integer, default=0)
    communication_score = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def complete_session(self, final_score, outcome):
        """Mark session as completed"""
        self.completed_at = datetime.utcnow()
        self.score = final_score
        self.outcome = outcome
        self.status = 'completed'
        
        # Calculate time taken
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.time_taken = int(delta.total_seconds())
    
    def get_duration_minutes(self):
        """Get session duration in minutes"""
        if self.time_taken:
            return round(self.time_taken / 60, 1)
        return 0
    
    def is_completed(self):
        """Check if session is completed"""
        return self.status == 'completed'
    
    def get_performance_breakdown(self):
        """Get dictionary of performance scores by category"""
        return {
            'detection': self.detection_score,
            'containment': self.containment_score,
            'eradication': self.eradication_score,
            'recovery': self.recovery_score,
            'communication': self.communication_score
        }
    
    def __repr__(self):
        return f'<TrainingSession user={self.user_id} scenario={self.scenario_id} status={self.status}>'


# ========================
# OPTIONAL: Helper Functions
# ========================
def init_db(app):
    """Initialize the database"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create default instructor if none exists
        if User.query.filter_by(role='instructor').first() is None:
            create_default_instructor()

def create_default_instructor():
    """Create a default instructor account for testing"""
    instructor = User(
        username='admin',
        email='admin@dontpanic.com',
        role='instructor'
    )
    instructor.set_password('admin123')  # Change this in production!
    
    db.session.add(instructor)
    db.session.commit()
    print("✅ Default instructor created: username='admin', password='admin123'")
