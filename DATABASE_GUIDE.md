# 📊 Database Architecture - Complete Explanation

## Current Setup (After Migration)

### **1. Active Database: `users_training.db` ✅**
**Location:** `instance/users_training.db` (36 KB)  
**Purpose:** Stores all user-related data and training session records  
**Status:** LIVE - Currently in use

#### **Tables in users_training.db:**

---

##### **📋 USERS Table**
Stores all user accounts and authentication information.

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER PRIMARY KEY | Unique user identifier |
| `username` | VARCHAR(80) | Unique login name |
| `email` | VARCHAR(120) | User email address |
| `password_hash` | VARCHAR(255) | Hashed password (bcrypt) |
| `role` | VARCHAR(20) | User role: 'admin', 'instructor', or 'trainee' |
| `group_id` | INTEGER | Foreign key to Groups table (nullable) |
| `created_at` | DATETIME | Account creation timestamp |
| `last_login` | DATETIME | Last login timestamp (nullable) |
| `is_active` | BOOLEAN | Account active status |

**Current Data:** 1 user (admin account)

**Relationships:**
- Belongs to a **Group** (many-to-one)
- Has many **TrainingSession** records

---

##### **📋 GROUPS Table**
Stores training groups/organizations for organizing users.

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER PRIMARY KEY | Unique group identifier |
| `name` | VARCHAR(100) | Group name |
| `description` | TEXT | Group description |
| `created_by` | INTEGER | User ID who created the group |
| `created_at` | DATETIME | Group creation timestamp |
| `is_active` | BOOLEAN | Group active status |

**Current Data:** 0 groups (empty)

**Purpose:**
- Organize trainees and instructors into teams
- Each instructor manages one group
- Trainees belong to a group for their instructor

**Relationships:**
- Created by a **User** (foreign key)
- Has many **Users** as members

---

##### **📋 TRAINING_SESSIONS Table**
Stores records of each user's training session (playing a scenario).

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER PRIMARY KEY | Unique session identifier |
| `user_id` | INTEGER | User playing the scenario |
| `scenario_id` | INTEGER | Scenario being played |
| `started_at` | DATETIME | Session start time |
| `completed_at` | DATETIME | Session completion time (nullable) |
| `time_taken` | INTEGER | Total time in seconds |
| `score` | INTEGER | Final score (0-100) |
| `outcome` | VARCHAR(50) | Result: 'success', 'failure', etc. |
| `status` | VARCHAR(20) | 'in_progress', 'completed', 'abandoned' |
| `session_data` | TEXT | JSON: user decisions and actions |
| `detection_score` | INTEGER | Points for detection phase |
| `containment_score` | INTEGER | Points for containment phase |
| `eradication_score` | INTEGER | Points for eradication phase |
| `recovery_score` | INTEGER | Points for recovery phase |
| `communication_score` | INTEGER | Points for communication phase |
| `created_at` | DATETIME | Record creation timestamp |

**Current Data:** 0 sessions (empty after fresh migration)

**Purpose:**
- Track every training session a user plays
- Store performance metrics
- Record user decisions throughout the scenario
- Enable analytics and reporting

**Relationships:**
- Belongs to a **User**
- References a **Scenario** (by ID only - no foreign key)

---

### **2. Unused Databases (Ignored)**

#### **❌ scenarios.db (8 KB) - DEPRECATED**
**Status:** No longer used (locked, needs manual deletion)

**Previous Purpose:** Stored scenarios in SQLite database  
**Why Replaced:** Migrated to JSON files for easier management and version control  
**Migration Date:** December 15, 2025

**Old Table (no longer used):**
- `scenarios` - Previously stored all scenario data

---

#### **❌ dont_panic.db (deleted) - OLD BACKUP**
**Status:** Removed

**Previous Purpose:** Original combined database with all data  
**Why Removed:** Superseded by split database structure (users_training.db + JSON scenarios)

---

### **3. File-Based Scenarios (NEW) ✅**
**Location:** `scenarios/` folder  
**Purpose:** Version-controlled scenario storage  
**Status:** LIVE - Primary scenario storage

#### **Folder Structure:**
```
scenarios/
├── 1.json                          # Scenario ID 1
├── 2.json                          # Scenario ID 2
└── test_incidents/                 # Category folder
    └── 5fe68f7d.json              # Scenario in category
```

#### **JSON Scenario Format:**
```json
{
  "id": "1",
  "title": "Ransomware Attack Response",
  "description": "Handle a ransomware incident...",
  "category": "",
  "incident_type": "ransomware",
  "difficulty_level": 3,
  "estimated_time": 30,
  "max_points": 100,
  "scenario_content": {
    "intro": "Your systems are encrypted...",
    "stages": [
      {
        "stage": "detection",
        "question": "What's your first action?",
        "options": [
          {"text": "Disconnect network", "points": 20},
          {"text": "Pay ransom", "points": -10}
        ]
      }
    ]
  },
  "created_by": 1,
  "created_at": "2025-12-15T11:20:00",
  "updated_at": "2025-12-15T11:20:00",
  "is_active": true,
  "times_played": 0,
  "average_score": 0.0
}
```

**Advantages:**
✅ Version controlled in git  
✅ Organized by category folders  
✅ Human-readable and editable  
✅ Self-contained (all metadata in one file)  
✅ Easy to share between projects  

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   DON'T PANIC APPLICATION                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  users_training.db   │         │   scenarios/ folder  │
├──────────────────────┤         ├──────────────────────┤
│ • USERS              │         │ • *.json files       │
│ • GROUPS             │         │ • Category folders   │
│ • TRAINING_SESSIONS  │         │ • Version controlled │
├──────────────────────┤         └──────────────────────┘
│ Live Database        │
│ SQLite               │
│ (36 KB)              │
└──────────────────────┘
         ▲                                ▲
         │                                │
         └────────────┬───────────────────┘
                      │
              ┌───────▼─────────┐
              │  Flask App      │
              │                 │
              │  • Auth Routes  │
              │  • Scenario     │
              │    Routes       │
              │  • Admin Routes │
              └─────────────────┘
                      ▲
                      │
            ┌─────────▼─────────┐
            │  Web Interface    │
            │  (Templates/HTML) │
            └───────────────────┘
```

---

## Key Statistics

| Item | Count | Status |
|------|-------|--------|
| **Users** | 1 | Active (admin) |
| **Groups** | 0 | Empty |
| **Training Sessions** | 0 | Fresh database |
| **Scenarios (JSON)** | 3 | Migrated from DB |
| **Scenario Categories** | 1 | test_incidents |

---

## Access Permissions (Role Hierarchy)

```
┌─────────────────────────────────────────┐
│         ADMIN (Top)                     │
├─────────────────────────────────────────┤
│ • See all users                         │
│ • See all training logs                 │
│ • Create/edit/delete scenarios          │
│ • Manage groups and instructors         │
│ • View all reports                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      INSTRUCTOR (Middle)                │
├─────────────────────────────────────────┤
│ • See own logs                          │
│ • See trainees in their group           │
│ • See trainee logs (NOT admin logs)     │
│ • View reports for their group          │
│ • Cannot create/edit scenarios          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       TRAINEE (Bottom)                  │
├─────────────────────────────────────────┤
│ • See own profile                       │
│ • Play scenarios                        │
│ • See own training logs                 │
│ • Cannot see other users' data          │
└─────────────────────────────────────────┘
```

---

## Important Notes

### ✅ What's Tracked in Database
- User accounts and authentication
- Group memberships
- Training session records (scores, status, timing)
- User decisions during scenarios (session_data)

### ✅ What's Tracked in JSON Files
- Scenario content (decision tree, questions, options)
- Scenario metadata (title, description, difficulty)
- Scenario organization (category folders)

### ❌ What's NOT Tracked Yet
- Scenario play statistics (times_played, average_score)
- These are stored in JSON but not actively updated

### 🔒 Git Configuration
- **Tracked:** `scenarios/` folder (version control)
- **Ignored:** `instance/` directory (database files)
- **Exception:** `users_training.db` is NOT tracked (local only)

---

## Maintenance

### To Backup
```bash
# Backup user/session data
cp instance/users_training.db backups/users_training.db.bak

# Scenarios are already in git
git status scenarios/
```

### To Restore
```bash
# Restore database
cp backups/users_training.db.bak instance/users_training.db

# Scenarios pull from git
git pull
```

### To Migrate Old Data
```bash
python migrate_scenarios.py  # Re-run if needed
```

---

## Summary

**Current Active Database:** `users_training.db`
- Contains: Users, Groups, Training Sessions
- Size: 36 KB
- Format: SQLite
- Status: LIVE ✅

**Scenario Storage:** JSON Files in `scenarios/` folder
- Format: Human-readable JSON
- Organized: By category subfolders
- Version Control: Git tracked ✅
- Status: LIVE ✅

**Old Databases:** Deprecated
- scenarios.db: No longer used
- dont_panic.db: Deleted
- Status: Can be safely deleted

The application is fully operational with a clean, efficient database structure! 🎉
