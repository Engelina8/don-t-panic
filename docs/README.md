# 🛡️ Don't Panic - Incident Response Training Platform

> Master incident response through interactive, real-world cybersecurity scenarios

**Don't Panic** is a Flask-based training platform that simulates realistic cybersecurity incidents and guides learners through the critical stages of incident response. Users navigate branching decision trees where their choices determine the outcome of unfolding security crises.

## 🎯 Overview

**Don't Panic** teaches incident response decision-making through:

- **Interactive Scenarios**: Branching story-driven incidents (data breaches, ransomware, DDoS, phishing, insider threats, malware)
- **Real-world Decisions**: Choose your response path and see the consequences unfold
- **Performance Metrics**: Track detection, containment, eradication, recovery, and communication scores
- **Multi-stage Learning**: Progress through intro → multiple chapter stages with context-rich narratives
- **Admin Dashboard**: Instructors can create custom scenarios, manage users, and view analytics
- **Scoring System**: Configurable points per scenario with customizable max points

## ✨ Key Features

### For Trainees
- 🎮 **Interactive Scenarios**: Play through realistic cybersecurity incidents
- 📊 **Performance Tracking**: View scores, metrics, and outcomes
- 📚 **Rich Narratives**: Multi-chapter scenarios with detailed context at each stage
- ⏱️ **Time Tracking**: Monitor time spent and duration metrics
- 🏆 **Progress Dashboard**: Track completed scenarios and average performance

### For Instructors
- ✏️ **Scenario Builder**: Create custom scenarios with visual UI or raw JSON editor
- 📋 **Quick Create**: Build scenarios with minimal effort or use the advanced editor
- 👥 **User Management**: Create, view, and manage trainee accounts
- 📊 **Analytics & Reports**: View training sessions, completion rates, and performance metrics
- 🎯 **Branching Support**: Define multi-stage scenarios with optional branching between stages
- 📈 **Customizable Points**: Set max points per scenario and track normalized scores

## 🏗️ Architecture

```
don-t-panic-1/
├── app.py                 # Flask application initialization
├── run.py                 # Application entry point
├── config.py              # Configuration settings
├── models.py              # SQLAlchemy database models
├── routes/
│   ├── admin.py           # Admin routes
│   ├── auth.py            # Authentication routes
│   └── scenarios.py       # Gameplay routes
├── templates/
│   ├── base.html
│   ├── admin/
│   ├── scenarios/
│   └── auth/
├── static/
│   ├── css/main.css
│   └── js/main.js
├── instance/
│   └── dont_panic.db
└── docs/README.md
```

## 📊 Database Models

### User
- Username, email, password hash
- Role: trainee, instructor, admin
- Training sessions, created scenarios

### Scenario
- Title, description, incident type
- Difficulty (1-5), estimated time
- **max_points** (customizable, default 100)
- **scenario_content** (JSON with intro + multi-stage structure)
- Statistics: times_played, average_score

### TrainingSession
- User & scenario references
- Timestamps, duration
- Score, outcome (success/partial/failure)
- Performance metrics: detection, containment, eradication, recovery, communication

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone and navigate
cd don-t-panic-1

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

Open browser: `http://localhost:5000`

### Default Admin Account
- **Username**: admin
- **Password**: admin123
- ⚠️ **Change in production!**

## 📖 Creating Scenarios

### JSON Structure

```json
{
  "intro": "Initial incident summary (shows once at start)",
  "stages": [
    {
      "stage": "detection",
      "content": "Detailed chapter text shown at this stage",
      "question": "What do you do?",
      "options": [
        {
          "text": "Action description",
          "points": 25,
          "next": 1
        }
      ]
    }
  ]
}
```

### Key Fields
- **intro**: Brief incident summary (displays only at first stage)
- **stage**: Chapter identifier
- **content**: Rich narrative text (updates per stage)
- **question**: Decision prompt
- **options**: Choice array
  - `text`: Choice description
  - `points`: Score (positive/negative)
  - `next`: (Optional) Next stage index, name, or "END"

### Creating Scenarios

1. **Admin Dashboard** → **Manage Scenarios**
2. **Quick Create**: Fill basic info or use **Create New Scenario** for full editor
3. **Builder UI**: Add stages with content and questions
4. **Raw JSON**: Paste JSON directly into advanced editor

## 🎮 Playing Scenarios

1. Login as trainee
2. **Scenarios** → Select → **Start**
3. Read incident context and chapters
4. Make decisions by selecting options
5. Follow branching paths (if defined)
6. View results with score breakdown

## 📊 Admin Features

### Manage Scenarios
- Create, edit, delete scenarios
- Quick create or JSON editor
- Set difficulty, time, max points
- View statistics

### Manage Users
- View trainee accounts
- See training progress
- View session history
- Delete users

### Reports & Analytics
- Key statistics dashboard
- Per-scenario performance
- Session history with scores
- User progression tracking

## 🔐 Authentication

- Flask-Login based
- Password hashing with werkzeug
- Role-based access control
- Secure session management

## 🎨 UI/UX Features

- Dark theme with CSS variables
- Mobile-responsive design
- Smooth animations
- Scrollable tables and content boxes
- Accessible contrast ratios

## 📱 Core Features

### Scoring
- Configurable max points per scenario
- Normalized metrics (0-100)
- Final score from metric average
- Outcome classification

### Branching
- Optional `next` field per option
- Skip to specific stage or end early
- Sequential by default

### Session Tracking
- Start/completion timestamps
- Duration calculation
- 5 performance metrics
- Status tracking

## 🛠️ Database Migration

After model changes:
```bash
python scripts/add_max_points_column.py
```

## 📝 Configuration

Edit `config.py`:
```python
SECRET_KEY = 'your-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/dont_panic.db'
DEBUG = True  # False in production
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| TemplateNotFound | Check template file exists in correct path |
| OperationalError | Run migration script or check DB exists |
| 'scenario' undefined | Ensure routes pass scenario context |
| Import errors | Run `pip install -r requirements.txt` |

## 🚀 Deployment

For production:
1. Set `DEBUG = False`
2. Use Gunicorn/uWSGI
3. Set secure `SECRET_KEY`
4. Use environment variables
5. Set up HTTPS
6. Use PostgreSQL (not SQLite)

## 📚 Example Scenarios

See `example_scenario.json` for a complete 6-chapter data breach response scenario.

## 📄 License

BTS Cybersecurity Training Curriculum

## 👥 Support

Contact your instructor for issues or questions.
