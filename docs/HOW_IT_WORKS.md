# Don't Panic - How It Works (High-Level Overview)

## One-Sentence Summary
**Don't Panic is an interactive incident response training platform where trainees play branching decision-tree scenarios, make choices about security incidents, get scored on their decisions, and admins track their progress through analytics.**

---

## The Flow (Step-by-Step)

### 1. **User Registers & Logs In**
- Trainee signs up with encrypted username/email and hashed password
- Login validates credentials against database
- Flask-Login creates a secure session cookie

### 2. **Browse Scenarios**
- Trainee views available scenarios loaded from JSON files in `scenarios/` folder
- Scenarios are grouped by incident type (ransomware, phishing, insider threat, etc.)
- Each scenario shows difficulty, estimated time, and max points

### 3. **Play a Scenario (Core Game Loop)**
```
START SCENARIO
    ↓
READ INITIAL SITUATION (intro text)
    ↓
READ CURRENT STAGE (problem description)
    ↓
SEE QUESTION & OPTIONS (decision choices)
    ↓
USER SELECTS OPTION
    ↓
CALCULATE POINTS (based on correctness)
    ↓
ADVANCE TO NEXT STAGE
    ↓
SCENARIO COMPLETE? → YES: Show results → NO: Go back to stage
    ↓
END: Save score to database, show feedback
```

### 4. **Scoring & Feedback**
- Each decision option has points (0-100+)
- Points based on correctness factors: detection, containment, eradication, recovery, communication
- Final score = total points earned / max possible points
- AI assistant provides real-time guidance

### 5. **Admin Dashboard**
- Admins see analytics: total trainees, total sessions, completion rate, average scores
- Charts show most-played scenarios and top performers
- Can manage users, assign them to groups, create/edit scenarios
- Can view individual trainee progress and export results as CSV

### 6. **Group Management**
- Instructors create groups (e.g., "Security Team A")
- Assign trainees to groups
- Each group can have multiple instructors/trainees
- Admins see group-level performance metrics

---

## Technical Architecture

```
USER BROWSER
    ↓ (HTTP Requests)
FLASK WEB SERVER (app.py)
    ├─ Routes (Blueprints)
    │  ├─ auth.py → Login/Register
    │  ├─ scenarios.py → Browse & Play
    │  ├─ admin.py → Management
    │  └─ assistant/routes.py → AI Chat
    │
    ├─ Database (SQLAlchemy)
    │  ├─ User (trainees, instructors, admins)
    │  ├─ Group (training organizations)
    │  └─ TrainingSession (gameplay records)
    │
    ├─ Scenario Manager
    │  └─ Loads JSON files from disk
    │
    └─ Assistant (AI)
       └─ Provides real-time help
    ↓ (HTML/CSS/JS)
USER BROWSER (displays results)
```

---

## Key Components Explained

### **Models (Database)**
- **User**: Stores trainee/instructor/admin accounts with encrypted credentials
- **Group**: Stores training cohorts and membership
- **TrainingSession**: Records each time a user plays a scenario (score, decisions, time, status)
- **Scenario**: Loaded from JSON files (not stored in DB, file-based)

### **Routes (Features)**
- **auth.py**: Handles login, logout, registration with validation
- **scenarios.py**: Loads scenarios from files, starts sessions, handles gameplay decisions, calculates scores
- **admin.py**: Dashboard analytics, user management, group management, scenario CRUD
- **assistant/routes.py**: AI chatbot that helps during training

### **Scenario Manager**
- Reads scenario JSON files from `scenarios/` folder
- Each scenario has: title, description, incident type, difficulty, decision tree with branches
- Admin can create/edit/delete scenarios (saved as JSON files, version-controllable)

### **Security**
- Passwords hashed with werkzeug (bcrypt)
- Username/email encrypted with Fernet encryption
- Secure session cookies (HTTPOnly, SameSite)
- All database queries use SQLAlchemy ORM (prevents SQL injection)
- Authentication required on all sensitive routes

---

## Example Scenario Flow

**Scenario: "Ransomware Attack"**

```
Stage 1: Initial Alert
┌─────────────────────────────────────────────┐
│ Your systems report a critical event:       │
│ Multiple computers are encrypting files.    │
│                                             │
│ Question: What's your first action?         │
│ A) Isolate network immediately → +100 pts  │
│ B) Check files for ransomware → +20 pts    │
│ C) Continue normal operations → -10 pts    │
└─────────────────────────────────────────────┘
User selects: A) Isolate network
Score: +100 points
↓
Stage 2: Containment
┌─────────────────────────────────────────────┐
│ Network isolated. Ransomware contained.     │
│ Now: Notify stakeholders or investigate?    │
│                                             │
│ A) Notify C-level immediately → +50 pts    │
│ B) Investigate scope first → +80 pts       │
└─────────────────────────────────────────────┘
User selects: B) Investigate scope first
Score: +80 points
↓
Stage 3: Results
Final Score: 180/300 points = 60%
Feedback: "Good containment, but communication with leadership earlier would have been better."
```

---

## Data Flow Summary

```
1. REGISTRATION
   Form input → Validate → Encrypt username/email → Hash password → Save to DB

2. LOGIN
   Username/Password → Query DB → Decrypt username → Check password hash → Create session

3. PLAY SCENARIO
   Load JSON file → Parse decision tree → Display stage → User chooses option
   → Calculate points → Update session in DB → Show next stage or results

4. ADMIN VIEW
   Query DB (trainees) → Query DB (sessions) → Calculate stats → Generate charts → Display dashboard

5. MANAGE USERS
   Fetch all users → Allow admin to edit role/group → Update DB → Show success message

6. MANAGE GROUPS
   Create group → Assign users to group → Query group members → Calculate group stats
```

---

## Why This Architecture?

✅ **Modularity**: Each feature in separate blueprint files (auth, scenarios, admin)  
✅ **Security**: All passwords hashed, credentials encrypted, SQL injection proof  
✅ **Scalability**: JSON scenarios can grow without database bloat  
✅ **Analytics**: Database tracks all sessions for reporting  
✅ **Simplicity**: Clear separation between frontend (templates), backend (routes), and data (models)

---

## In One Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    Don't Panic Platform                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER REGISTERS/LOGS IN                                     │
│         ↓                                                    │
│  CHOOSES SCENARIO (from JSON files)                         │
│         ↓                                                    │
│  PLAYS SCENARIO (makes decisions)                           │
│         ↓                                                    │
│  GETS SCORE (points saved to database)                      │
│         ↓                                                    │
│  ADMIN SEES ANALYTICS (views on dashboard)                  │
│         ↓                                                    │
│  ADMIN MANAGES USERS/GROUPS (updates database)              │
│         ↓                                                    │
│  REPORTS & EXPORT (CSV of all results)                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Perfect For Your Presentation

**Opening slide:** "Don't Panic is an interactive training platform where security teams practice incident response by making decisions in realistic scenarios."

**Key points to emphasize:**
1. Decision-tree based scenarios (branching narratives)
2. Real-time scoring on incident response choices
3. Admin analytics to track team training progress
4. Group management for organizational structure
5. Encrypted credentials and secure design

