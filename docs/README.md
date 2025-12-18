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
      "content": "Detailed chapter text shown at this stage",
      "question": "What do you do?",
      "metrics": ["detection", "containment"],
      "options": [
        {
          "text": "Action description",
          "points": 30,
          "detection": 20,
          "containment": 10,
          "eradication": 0,
          "recovery": 0,
          "communication": 0,
          "correctness": {
            "detection": 85,
            "containment": 75
          },
          "next_stage": 1
        }
      ]
    }
  ]
}
```

### Root Level Fields
- **intro**: Brief incident summary (displays only at first stage)

### Stage Fields
- **content**: Rich narrative text (updates per stage)
- **question**: Decision prompt
- **metrics**: Array of metrics tested at this stage (`["detection", "containment", "eradication", "recovery", "communication"]`)
- **options**: Choice array

### Option Fields
- **text**: Choice description
- **points**: Total points for this option (0-100)
- **detection**: Points allocated to detection metric (0-100)
- **containment**: Points allocated to containment metric (0-100)
- **eradication**: Points allocated to eradication metric (0-100)
- **recovery**: Points allocated to recovery metric (0-100)
- **communication**: Points allocated to communication metric (0-100)
- **correctness**: Object with correctness percentages for each metric (0-100)
  - `detection`: 0-100 correctness percentage
  - `containment`: 0-100 correctness percentage
  - `eradication`: 0-100 correctness percentage
  - `recovery`: 0-100 correctness percentage
  - `communication`: 0-100 correctness percentage
- **next_stage**: (Optional) Index of next stage (0-based), or omit for sequential

### Performance Metrics Explained
- **Detection**: Ability to identify the incident occurred
- **Containment**: Ability to limit incident scope and impact
- **Eradication**: Ability to remove the threat completely
- **Recovery**: Ability to restore systems and operations
- **Communication**: Ability to inform stakeholders appropriately

### Creating Scenarios

1. **Admin Dashboard** → **Manage Scenarios** → **Create New Scenario**
2. **Basic Info**: Enter title, description, difficulty (1-5), estimated time, max points
3. **Scenario Builder**: Use visual UI to add stages and options
   - Add stage with content and question
   - Add options with point allocations
   - Select metrics tested at each stage
   - Set correctness percentages for each metric
   - Define next_stage for branching (optional)
4. **Raw JSON Editor**: Toggle to paste/edit JSON directly
5. **Save**: Click Save to create scenario

### Builder Features
- **Quick Add Stage**: Add stages with numbered content areas
- **Metrics Button**: Select which 5 metrics apply to this stage
- **Points Editor**: Allocate points across detection, containment, eradication, recovery, communication
- **Correctness Editor**: Set correctness percentages (represents how correct each metric decision was)
- **Branching**: Optional next_stage field skips to specific stage or continues sequentially

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
