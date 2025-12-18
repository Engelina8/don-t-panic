from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()




def get_local_time(utc_datetime, timezone_offset=1):
    """Convert UTC datetime to local time with timezone offset
    
    Args:
        utc_datetime: datetime object in UTC
        timezone_offset: hours offset from UTC (default 1 for UTC+1)
    
    Returns:
        datetime object in local time
    """
    if not utc_datetime:
        return None
    return utc_datetime + timedelta(hours=timezone_offset)




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
    # Options: 'trainee', 'instructor', or 'admin'
    
    # Group membership (for trainee and instructor)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    training_sessions = db.relationship('TrainingSession', 
                                       backref='user', 
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_instructor(self):
        """Check if user is an instructor"""
        return self.role == 'instructor'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def is_instructor_or_admin(self):
        """Check if user is an instructor or admin"""
        return self.role in ('instructor', 'admin')
    
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





class Group(db.Model):
    """Training groups/organizations"""
    __tablename__ = 'groups'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Group info
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Admin who created this group
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    members = db.relationship('User', 
                            backref='group', 
                            lazy='dynamic',
                            foreign_keys='User.group_id')
    
    admin = db.relationship('User',
                           foreign_keys=[created_by],
                           backref='created_groups')
    
    def get_instructors(self):
        """Get all instructors in this group"""
        return self.members.filter_by(role='instructor').all()
    
    def get_trainees(self):
        """Get all trainees in this group"""
        return self.members.filter_by(role='trainee').all()
    
    def get_member_count(self):
        """Get total member count"""
        return self.members.count()
    
    def get_instructor_count(self):
        """Get instructor count"""
        return self.members.filter_by(role='instructor').count()
    
    def get_trainee_count(self):
        """Get trainee count"""
        return self.members.filter_by(role='trainee').count()
    
    def __repr__(self):
        return f'<Group {self.name}>'





class Scenario:
    """Scenario class - loaded from JSON files in scenarios folder
    
    Attributes loaded from JSON:
    - id: Unique scenario identifier
    - title: Scenario title
    - description: Full description
    - category: Scenario category/folder
    - incident_type: Type of incident (ransomware, data_breach, etc.)
    - difficulty_level: 1-5 difficulty scale
    - estimated_time: Estimated completion time in minutes
    - max_points: Maximum points possible
    - scenario_content: Decision tree/story branches as JSON
    - created_by: User ID who created the scenario
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - is_active: Whether scenario is active
    - times_played: Number of times played (tracked separately)
    - average_score: Average score (tracked separately)
    """
    
    def __init__(self, data=None):
        """Initialize from dictionary (loaded from JSON)"""
        if data is None:
            data = {}
        
        import json
        
        # Store all data
        self.data = data
        
        # Provide direct access to common attributes
        self.id = data.get('id')
        self.title = data.get('title', 'Untitled Scenario')
        self.description = data.get('description', '')
        self.category = data.get('category', '')
        self.incident_type = data.get('incident_type', '')
        self.difficulty_level = data.get('difficulty_level', 1)
        self.estimated_time = data.get('estimated_time', 30)
        self.max_points = data.get('max_points', 100)
        
        # Convert scenario_content to JSON string if it's a dict
        content = data.get('scenario_content', '{}')
        if isinstance(content, dict):
            self.scenario_content = json.dumps(content, indent=2)
        else:
            self.scenario_content = content if content else '{}'
        
        self.created_by = data.get('created_by')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.is_active = data.get('is_active', True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'incident_type': self.incident_type,
            'difficulty_level': self.difficulty_level,
            'estimated_time': self.estimated_time,
            'max_points': self.max_points,
            'scenario_content': self.scenario_content,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Scenario {self.title} (Level {self.difficulty_level})>'
    
    def __getitem__(self, key):
        """Allow dict-like access"""
        return self.data.get(key)
    
    def get(self, key, default=None):
        """Allow dict-like get method"""
        return self.data.get(key, default)





class TrainingSession(db.Model):
    """Individual training session records"""
    __tablename__ = 'training_sessions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    scenario_id = db.Column(db.Integer, nullable=False, index=True)  # Scenario ID from scenarios.db - no foreign key
    
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
        

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.time_taken = int(delta.total_seconds())
    
    def get_duration_minutes(self):
        """Get session duration in minutes"""
        # For completed sessions, use stored time_taken
        if self.status == 'completed' and self.time_taken is not None:
            return round(self.time_taken / 60, 1)
        
        # For in-progress sessions, calculate from started_at to now
        if self.started_at:
            if self.status == 'completed' and self.completed_at:
                delta = self.completed_at - self.started_at
            else:
                delta = datetime.utcnow() - self.started_at
            return round(delta.total_seconds() / 60, 1)
        
        return 0
    
    def get_local_started_at(self, timezone_offset=1):
        """Get started_at time converted to local timezone"""
        return get_local_time(self.started_at, timezone_offset)
    
    def get_local_completed_at(self, timezone_offset=1):
        """Get completed_at time converted to local timezone"""
        return get_local_time(self.completed_at, timezone_offset)
    
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

        db.create_all()
        print("✅ Database tables created successfully!")
        

        if User.query.filter_by(role='admin').first() is None:
            create_default_admin()

def create_default_admin():
    """Create a default admin account for testing"""
    admin = User(
        username='admin',
        email='admin@dontpanic.com',
        role='admin'
    )
    admin.set_password('admin123')  # Change this in production!
    
    db.session.add(admin)
    db.session.commit()
    print("✅ Default admin created: username='admin', password='admin123'")
