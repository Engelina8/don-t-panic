# Don't Panic - Python Code Documentation

**Incident Response Training Platform**  
A comprehensive incident response simulation and training system built with Flask.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Modules](#core-modules)
4. [Database Models](#database-models)
5. [Application Flow](#application-flow)
6. [Key Features](#key-features)
7. [Security Features](#security-features)

---

## System Overview

**Don't Panic** is an interactive training platform for incident response teams. It provides:

- **Scenario-based training** with branching decision trees
- **Real-time feedback** on trainee decisions
- **Progress tracking** with scoring and analytics
- **Group management** for organized training cohorts
- **Admin dashboard** with comprehensive reporting
- **AI-powered assistant** for real-time help during training

### Tech Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-Login with encrypted credentials
- **Security**: Fernet encryption for sensitive data
- **Frontend**: Jinja2 templates with modern CSS

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application (app.py)             │
│                   - Application Factory Pattern              │
│                   - Blueprint Registration                   │
│                   - Error Handling                           │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐  ┌──────▼──────┐  ┌─────▼──────┐
   │ Database │  │   Managers  │  │   Routes   │
   │ (SQLAlchemy) │  │           │  │            │
   └──────────┘  └─────────────┘  └────────────┘
        │             │                 │
   ┌────▼─────┐  ┌────▼──────────┐ ┌────▼────┐
   │ Models.py│  │ScenarioManager│ │ Auth    │
   │           │  │               │ │ Admin   │
   │ - User    │  │ - Load JSON   │ │ Scenario│
   │ - Group   │  │ - Create      │ │ Other   │
   │ - Scenario│  │ - Delete      │ │         │
   │ - Training│  │ - Update      │ │         │
   └───────────┘  └───────────────┘ └─────────┘
```

### Module Structure

```
don-t-panic-1/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── scenario_manager.py       # Scenario file management
├── run.py                    # Entry point
│
├── routes/                   # Blueprint routes
│   ├── __init__.py
│   ├── auth.py              # Login/Logout/Register
│   ├── admin.py             # Admin dashboard & management
│   └── scenarios.py         # Scenario gameplay
│
├── assistant/               # AI Assistant module
│   ├── __init__.py
│   ├── routes.py            # Assistant API endpoints
│   ├── chatbot.py           # Chatbot logic
│   ├── knowledge_base.py    # Incident response knowledge
│
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── admin/
│   └── scenarios/
│
├── static/                  # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── img/
│
├── scenarios/               # Training scenarios (JSON files)
│   ├── ransomware/
│   ├── data_breach/
│   └── [other categories]/
│
└── instance/                # Instance-specific files
    └── dont_panic.db        # SQLite database
```

---

## Core Modules

### 1. **app.py** - Application Factory

The main Flask application using the **factory pattern**.

```python
def create_app(config_name=None):
    """Create and configure the Flask application"""
    # - Initialize Flask app
    # - Configure database
    # - Setup authentication
    # - Register blueprints
    # - Handle errors
```

**Key Responsibilities:**
- Application initialization
- Database setup
- Login manager configuration
- Blueprint registration (auth, admin, scenarios, assistant)
- Error handler registration
- Template filters

**Key Functions:**
- `create_app()` - Factory function for app creation
- `register_blueprints()` - Load all route blueprints
- `register_error_handlers()` - Setup custom error pages

---

### 2. **config.py** - Configuration Management

Environment-based configuration for development, testing, and production.

```python
class Config:
    """Base configuration"""
    SECRET_KEY = 'secret-key-for-sessions'
    ENCRYPTION_KEY = Fernet.generate_key()  # Data encryption
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dont_panic.db'
    TIMEZONE_OFFSET = 1  # UTC+1
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set True in production
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
```

**Configuration Classes:**
- `Config` - Base configuration
- `DevelopmentConfig` - Debug enabled
- `ProductionConfig` - Debug disabled, secure cookies
- `TestingConfig` - In-memory database

---

### 3. **models.py** - Database Models

Defines all database entities and relationships.

#### **User Model**
Represents trainee and instructor accounts.

```python
class User(UserMixin, db.Model):
    id: Integer (primary key)
    _username: String (encrypted)
    _email: String (encrypted)
    password_hash: String (hashed with werkzeug)
    role: String ('admin', 'instructor', 'trainee')
    group_id: Integer (foreign key to Group)
    created_at: DateTime
    last_login: DateTime
    is_active: Boolean
    training_sessions: Relationship → TrainingSession
```

**Key Methods:**
- `set_password()` - Hash and store password
- `check_password()` - Verify password
- `is_admin()` / `is_instructor()` - Role checks
- `get_average_score()` - Calculate training score average
- `get_completed_scenarios_count()` - Count completed trainings
- `find_by_username()` / `find_by_email()` - Static lookup methods

**Security Features:**
- Username and email encrypted using Fernet
- Password hashed with werkzeug.security
- Secure properties for decryption on access

---

#### **Group Model**
Represents training organizations/cohorts.

```python
class Group(db.Model):
    id: Integer (primary key)
    name: String (unique)
    description: Text
    created_by: Integer (foreign key to User - admin)
    created_at: DateTime
    is_active: Boolean
    members: Relationship → User
```

**Key Methods:**
- `get_instructors()` - Get all instructors in group
- `get_trainees()` - Get all trainees in group
- `get_member_count()` - Total members
- `get_instructor_count()` - Total instructors
- `get_trainee_count()` - Total trainees

---

#### **TrainingSession Model**
Tracks individual scenario playthrough sessions.

```python
class TrainingSession(db.Model):
    id: Integer (primary key)
    user_id: Integer (foreign key to User)
    scenario_id: String
    status: String ('in_progress', 'completed', 'abandoned')
    started_at: DateTime
    completed_at: DateTime
    score: Integer (0-100)
    decisions_made: Integer (count)
    correct_decisions: Integer (count)
    session_data: Text (JSON with user responses)
    feedback: Text (AI-generated feedback)
```

**Key Methods:**
- `get_accuracy_percentage()` - Calculate accuracy
- `get_local_started_at()` - Get local timezone datetime
- `get_local_completed_at()` - Get local timezone datetime

---

#### **Scenario Class** (In-Memory)
Loaded from JSON files, not stored in database.

```python
class Scenario:
    id: String (unique identifier)
    title: String
    description: String
    category: String (folder name)
    incident_type: String ('ransomware', 'data_breach', etc.)
    difficulty_level: Integer (1-5)
    estimated_time: Integer (minutes)
    max_points: Integer (max possible score)
    scenario_content: JSON (decision tree)
    created_by: Integer (creator ID)
    created_at: DateTime
    updated_at: DateTime
    is_active: Boolean
```

---

#### **Data Relationships**
```
User (1) ──────────────────────────────────── (N) TrainingSession
         └──── group_id (Foreign Key)

User (1) ──────────────── (N) Group (created_by)

Group (1) ────────────────────────────────── (N) User (group_id)
```

---

### 4. **scenario_manager.py** - Scenario Management

File-based scenario storage and management. Scenarios are stored as JSON files in the `scenarios/` directory.

```python
class ScenarioManager:
    def __init__(self, scenarios_dir='scenarios'):
        """Initialize scenario manager"""
        self.scenarios_dir = Path(scenarios_dir)
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `get_all_scenarios()` | Return all scenarios from all categories |
| `get_scenario(scenario_id)` | Get single scenario by ID |
| `get_scenarios_by_category(category)` | Get scenarios in a category |
| `get_categories()` | List all category folders |
| `create_scenario(data, category)` | Create new scenario JSON file |
| `update_scenario(scenario_id, data)` | Update existing scenario |
| `delete_scenario(scenario_id)` | Delete scenario file |
| `_load_scenario_from_file(file_path)` | Load and parse JSON |
| `_generate_scenario_id()` | Generate unique ID |
| `_slugify_title(title)` | Create filename from title |

**Scenario JSON Structure:**
```json
{
  "id": "scenario-001",
  "title": "Ransomware Attack Response",
  "description": "A critical system has been encrypted...",
  "category": "ransomware",
  "incident_type": "ransomware",
  "difficulty_level": 3,
  "estimated_time": 45,
  "max_points": 100,
  "scenario_content": {
    "initial": {
      "text": "Your systems report a critical event...",
      "options": [
        {"text": "Isolate the network", "next": "isolation_step", "points": 20},
        {"text": "Continue normal operations", "next": "mistake", "points": -10}
      ]
    },
    "isolation_step": { ... },
    "mistake": { ... }
  },
  "created_by": 1,
  "created_at": "2026-01-25T10:30:00",
  "is_active": true
}
```

---

### 5. **routes/auth.py** - Authentication Routes

User authentication and registration.

**Routes:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/login` | GET, POST | User login page |
| `/logout` | GET | Logout user |
| `/register` | GET, POST | New user registration |

**Key Features:**
- Login with username/password
- "Remember me" functionality (7-day duration)
- Validation of passwords and usernames
- New trainee registration
- Duplicate prevention (username/email)
- Session management with Flask-Login

---

### 6. **routes/scenarios.py** - Scenario Routes

Scenario browsing and gameplay.

**Routes:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/scenarios/` | GET | List all scenarios grouped by category |
| `/scenarios/<scenario_id>` | GET | Scenario detail/info page |
| `/scenarios/<scenario_id>/start` | POST | Start new training session |
| `/scenarios/session/<session_id>` | GET | Play scenario (gameplay page) |
| `/scenarios/session/<session_id>/submit` | POST | Submit decision during play |
| `/scenarios/session/<session_id>/results` | GET | Show results after completion |
| `/scenarios/export-csv` | GET | Export results as CSV |

**Key Gameplay Features:**
- Track active sessions (prevent duplicates)
- Real-time decision submission
- Score calculation based on choices
- Session completion with results
- Export training results

---

### 7. **routes/admin.py** - Admin Management

Administrative dashboard and group management.

**Routes Include:**

| Route | Purpose |
|-------|---------|
| `/admin/dashboard` | Main admin analytics dashboard |
| `/admin/users` | Manage all users |
| `/admin/users/<user_id>` | View user details |
| `/admin/groups` | Manage training groups |
| `/admin/groups/<id>` | View group details |
| `/admin/groups/<id>/add-member` | Add user to group |
| `/admin/scenarios` | Manage scenarios |
| `/admin/scenarios/create` | Create new scenario |
| `/admin/scenarios/<id>/edit` | Edit scenario |
| `/admin/scenarios/<id>/delete` | Delete scenario |

**Key Features:**
- Dashboard with analytics and charts
- User management and role assignment
- Group creation and member assignment
- Scenario management (CRUD operations)
- Training session reports
- Performance analytics

---

### 8. **assistant/chatbot.py** - AI Assistant

Real-time assistance during training.

**Features:**
- Context-aware suggestions
- Incident response guidance
- Decision validation
- Real-time feedback
- Knowledge base integration

---

## Database Models

### Entity Relationship Diagram

```
┌──────────┐                    ┌───────────┐
│  User    │                    │  Group    │
├──────────┤                    ├───────────┤
│ id (PK)  │◄─────created_by─────│ id (PK) │
│ username │                    │ name     │
│ email    │                    │ description
│ role     │                    │ created_at
│ group_id │◄────member────────────members
│ password │                    │ is_active
│ created  │                    └───────────┘
└──────────┘
    ▲
    │ sessions
    │
┌───┴─────────────────┐
│ TrainingSession     │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ scenario_id         │
│ status              │
│ started_at          │
│ completed_at        │
│ score               │
│ decisions_made      │
│ correct_decisions   │
│ session_data (JSON) │
│ feedback            │
└─────────────────────┘
```

### Data Flow

```
1. USER REGISTRATION/LOGIN
   ↓
   User → Database (User model)
   ↓
   Authentication Check
   ↓
   Session Created (Flask-Login)

2. VIEWING SCENARIOS
   ↓
   Load JSON files (ScenarioManager)
   ↓
   Convert to Scenario objects
   ↓
   Display to trainee

3. PLAYING SCENARIO
   ↓
   Create TrainingSession (in_progress)
   ↓
   User makes decisions
   ↓
   Submit decision → Calculate points
   ↓
   Update session_data
   ↓
   Scenario complete?
   ├─ YES → Calculate final score → Mark completed
   └─ NO → Continue

4. ADMIN DASHBOARD
   ↓
   Query TrainingSession (all trainees)
   ↓
   Aggregate statistics
   ↓
   Generate charts and reports
```

---

## Application Flow

### 1. User Registration & Login Flow

```
[Trainee] 
    ↓
[/register] → Validate input → Create User → Hash Password → Save to DB
    ↓
[/login] → Find User by Username → Check Password Hash → Create Session
    ↓
[Authenticated] → Redirect to /dashboard
```

### 2. Scenario Training Flow

```
[Trainee Views Scenarios]
    ↓
[/scenarios] → Load from scenarios/ folder → Group by category → Display
    ↓
[Trainee Selects Scenario]
    ↓
[/scenarios/<id>/start] → Create TrainingSession (in_progress)
    ↓
[/scenarios/session/<id>] → Display scenario content
    ↓
[Trainee Makes Decisions]
    ↓
[/scenarios/session/<id>/submit] → Validate choice → Calculate points
    ↓
[Decision Recorded in session_data]
    ↓
[Scenario Complete?]
    ├─ YES → Calculate final score → Record completed_at
    └─ NO → Load next decision node → Return to step 5
    ↓
[/scenarios/session/<id>/results] → Show score and feedback
```

### 3. Admin Dashboard Flow

```
[Admin Logs In]
    ↓
[/admin/dashboard] → Query TrainingSession (role='trainee')
    ↓
[Aggregate Data]
    ├─ Total trainees count
    ├─ Total sessions count
    ├─ Completed vs in-progress
    ├─ Average scores
    ├─ Performance by trainee
    └─ Performance by scenario
    ↓
[Generate Charts] → Render dashboard
```

---

## Key Features

### 1. User Management
- **Registration**: New trainees can self-register
- **Authentication**: Secure login with password hashing
- **Roles**: Admin, Instructor, Trainee with different permissions
- **Encryption**: Username and email encrypted at rest

### 2. Scenario Management
- **JSON-based**: Scenarios stored as JSON files (version-controllable)
- **Categories**: Organize scenarios by incident type
- **Decision Trees**: Branching scenarios with multiple outcomes
- **Scoring**: Points awarded based on decisions
- **Difficulty Levels**: 1-5 scale for training progression

### 3. Training Sessions
- **Active Session Tracking**: Prevent duplicate concurrent sessions
- **Progress Saving**: Session data saved with each decision
- **Real-time Feedback**: AI assistant provides guidance
- **Results**: Score, accuracy, and feedback after completion
- **History**: All sessions saved for reporting

### 4. Group Management
- **Organization**: Organize trainees into groups
- **Instructor Assignment**: Instructors manage their groups
- **Bulk Operations**: Manage multiple members per group
- **Analytics**: Group-level performance tracking

### 5. Analytics & Reporting
- **Dashboard**: Comprehensive overview of training metrics
- **Charts**: Visual representation of performance
- **Scenario Analytics**: Most-played scenarios, average scores
- **User Analytics**: Top performers, completion rates
- **CSV Export**: Download training results

### 6. Security
- **Encrypted Fields**: Username and email encrypted with Fernet
- **Password Hashing**: Werkzeug security for passwords
- **Session Security**: HTTPOnly, Secure, SameSite cookies
- **CSRF Protection**: Built-in Flask-WTF CSRF protection
- **Login Required**: Decorators enforce authentication

---

## Security Features

### 1. Data Encryption
```python
from cryptography.fernet import Fernet

# Sensitive fields encrypted at rest
User._username → encrypt_field() → stored encrypted
User._email → encrypt_field() → stored encrypted

# Decryption on access
@property
def username(self):
    return decrypt_field(self._username)
```

### 2. Password Security
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing
user.set_password(password) → generate_password_hash()

# Verification
user.check_password(password) → check_password_hash()
```

### 3. Session Management
```python
# Secure session configuration
SESSION_COOKIE_HTTPONLY = True  # JS cannot access
SESSION_COOKIE_SECURE = True    # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection
PERMANENT_SESSION_LIFETIME = 2 hours
```

### 4. Authentication & Authorization
```python
# Login required decorator
@login_required
def dashboard():
    return render_template('dashboard.html')

# Admin required decorator
@admin_required
def create_scenario():
    return render_template('admin/scenarios.html')

# Role checking
if current_user.is_admin():
    # Admin operations
```

---

## Deployment Considerations

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<fernet-key>
DATABASE_URL=postgresql://...
TIMEZONE_OFFSET=1
```

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Use production database (PostgreSQL)
- [ ] Enable HTTPS
- [ ] Rotate SECRET_KEY and ENCRYPTION_KEY
- [ ] Setup logging and monitoring
- [ ] Configure email for notifications
- [ ] Backup scenarios and database regularly
- [ ] Setup automated tests
- [ ] Use environment-based configuration

---

## Development Workflow

### Running Locally
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export FLASK_ENV=development
export FLASK_DEBUG=True

# Run application
python run.py
```

### Project Structure Best Practices
- **Models**: Database entities in `models.py`
- **Routes**: Feature-based in `routes/` directory
- **Templates**: Mirror route structure in `templates/`
- **Static**: Organized by asset type (css/, js/, img/)
- **Scenarios**: Organized by category in `scenarios/`

---

## Summary

**Don't Panic** is a well-architected Flask application using:
- **Factory Pattern** for flexible application creation
- **Blueprint System** for modular route organization
- **SQLAlchemy ORM** for clean database operations
- **Fernet Encryption** for sensitive data protection
- **JSON Files** for version-controllable scenarios
- **Flask-Login** for robust authentication

The system is designed to be:
- **Scalable**: Modular architecture supports growth
- **Secure**: Encryption, hashing, and session management
- **Maintainable**: Clean code structure and separation of concerns
- **Extensible**: Easy to add new features (scenarios, routes, etc.)

Perfect for incident response training with comprehensive analytics and real-time feedback!

---

**For Questions or Issues:**
- Check route documentation for endpoint details
- Review model relationships for data structure
- See scenario JSON format for creating custom scenarios
- Refer to security features for best practices
