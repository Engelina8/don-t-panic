# Database Operations Reference

## Complete List of All Database Functions

---

## **USER OPERATIONS** 

### 1. **Register User (Create)**
**File:** `routes/auth.py` - Line 55  
**Function:** `register()`  
**Route:** `POST /register`  
**What it does:**
- Creates new trainee user
- Validates username, email, password
- Encrypts username/email
- Hashes password with werkzeug
- Saves to `users` table

**Database Operation:**
```python
new_user = User(username=username, email=email, role='trainee')
new_user.set_password(password)
db.session.add(new_user)
db.session.commit()
```

---

### 2. **Add User (Admin)**
**File:** `routes/admin.py` - Line 243  
**Function:** `add_user()`  
**Route:** `POST /users/add`  
**What it does:**
- Admin creates new user
- Can set role (trainee/instructor)
- Same encryption/hashing as register

**Database Operation:**
```python
new_user = User(username=username, email=email, role=role)
new_user.set_password(password)
db.session.add(new_user)
db.session.commit()
```

---

### 3. **Delete User**
**File:** `routes/admin.py` - Line 343  
**Function:** `delete_user(user_id)`  
**Route:** `POST /users/<user_id>/delete`  
**What it does:**
- Delete user and all their training sessions
- Cascade delete all TrainingSession records

**Database Operation:**
```python
user = User.query.get_or_404(user_id)
TrainingSession.query.filter_by(user_id=user_id).delete()
db.session.delete(user)
db.session.commit()
```

---

### 4. **Reset User Logs**
**File:** `routes/admin.py` - Line 359  
**Function:** `reset_user_logs(user_id)`  
**Route:** `POST /users/<user_id>/reset-logs`  
**What it does:**
- Delete all training sessions for a user
- Keep user account intact

**Database Operation:**
```python
TrainingSession.query.filter_by(user_id=user_id).delete()
db.session.commit()
```

---

### 5. **Login User**
**File:** `routes/auth.py` - Line 10  
**Function:** `login()`  
**Route:** `POST /login`  
**What it does:**
- Find user by username
- Check password hash
- Create session with Flask-Login

**Database Operation:**
```python
user = User.find_by_username(username)
if user and user.check_password(password):
    login_user(user)
```

---

### 6. **View User Details**
**File:** `routes/admin.py` - Line 311  
**Function:** `user_detail(user_id)`  
**Route:** `GET /users/<user_id>`  
**What it does:**
- Get user info and all their training sessions

**Database Operation:**
```python
user = User.query.get_or_404(user_id)
sessions = TrainingSession.query.filter_by(user_id=user_id).order_by(...)
```

---

### 7. **Change Password**
**File:** `routes/auth.py` - Line 123  
**Function:** `change_password()`  
**Route:** `POST /change-password`  
**What it does:**
- Update user password hash

**Database Operation:**
```python
current_user.set_password(new_password)
db.session.commit()
```

---

### 8. **Assign User to Group**
**File:** `routes/admin.py` - Line 863 (NEW ENDPOINT)  
**Function:** `assign_user_to_group(user_id, group_id)`  
**Route:** `POST /users/<user_id>/assign-to-group/<group_id>`  
**What it does:**
- Assign trainee to a group

**Database Operation:**
```python
user = User.query.get_or_404(user_id)
user.group_id = group_id
db.session.commit()
```

---

## **GROUP OPERATIONS**

### 1. **Create Group**
**File:** `routes/admin.py` - Line 695  
**Function:** `add_group()`  
**Route:** `POST /groups/add`  
**What it does:**
- Create new training group
- Set group creator as admin

**Database Operation:**
```python
new_group = Group(name=name, description=description, created_by=current_user.id)
db.session.add(new_group)
db.session.commit()
```

---

### 2. **View Groups**
**File:** `routes/admin.py` - Line 689  
**Function:** `groups()`  
**Route:** `GET /admin/groups`  
**What it does:**
- List all groups

**Database Operation:**
```python
all_groups = Group.query.order_by(Group.created_at.desc()).all()
```

---

### 3. **View Group Details**
**File:** `routes/admin.py` - Line 728  
**Function:** `view_group(id)`  
**Route:** `GET /admin/groups/<id>`  
**What it does:**
- Get group members (instructors and trainees)
- Show available users to add

**Database Operation:**
```python
group = Group.query.get_or_404(id)
available_users = User.query.filter(
    or_(User.group_id.is_(None), User.group_id != id),
    User.role.in_(['trainee', 'instructor'])
)
```

---

### 4. **Add Member to Group**
**File:** `routes/admin.py` - Line 745  
**Function:** `add_group_member(id)`  
**Route:** `POST /groups/<id>/add-member`  
**What it does:**
- Assign user to group (from group detail page)

**Database Operation:**
```python
user = User.query.get_or_404(user_id)
user.group_id = group_id
db.session.commit()
```

---

### 5. **Remove Member from Group**
**File:** `routes/admin.py` - Line 773  
**Function:** `remove_group_member(group_id, user_id)`  
**Route:** `POST /groups/<group_id>/remove-member/<user_id>`  
**What it does:**
- Remove user from group (set group_id to NULL)

**Database Operation:**
```python
user = User.query.get_or_404(user_id)
user.group_id = None
db.session.commit()
```

---

### 6. **Delete Group**
**File:** `routes/admin.py` - Line 795  
**Function:** `delete_group(id)`  
**Route:** `POST /groups/<id>/delete`  
**What it does:**
- Delete group (keeps users, just removes group_id)

**Database Operation:**
```python
group = Group.query.get_or_404(id)
# Remove all users from group
User.query.filter_by(group_id=id).update({'group_id': None})
db.session.delete(group)
db.session.commit()
```

---

## **SCENARIO OPERATIONS**

### 1. **Create Scenario**
**File:** `routes/admin.py` - Line 457  
**Function:** `create_scenario()`  
**Route:** `GET, POST /scenarios/create`  
**What it does:**
- Create new scenario (saves as JSON file, NOT in database)
- Uses ScenarioManager

**Database Operation:**
```python
# NO database insert - uses file system
scenario_manager.create_scenario(scenario_data, category)
# Saves to: scenarios/<category>/<title>_<id>.json
```

---

### 2. **Delete Scenario**
**File:** `routes/admin.py` - Line 629  
**Function:** `delete_scenario(scenario_id)`  
**Route:** `POST /scenarios/<scenario_id>/delete`  
**What it does:**
- Delete scenario JSON file

**Database Operation:**
```python
# NO database delete - uses file system
scenario_manager.delete_scenario(scenario_id)
# Deletes file from: scenarios/<id>.json
```

---

### 3. **List Scenarios**
**File:** `routes/scenarios.py` - Line 11  
**Function:** `list()`  
**Route:** `GET /scenarios`  
**What it does:**
- Load all scenario JSON files
- Group by category

**Database Operation:**
```python
# NO database query - reads from file system
scenarios_data = scenario_manager.get_all_scenarios()
# Gets all *.json files from scenarios/
```

---

### 4. **Create Folder**
**File:** `routes/admin.py` - Line 378  
**Function:** `create_folder()`  
**Route:** `POST /scenarios/create-folder`  
**What it does:**
- Create new category folder for organizing scenarios

**Database Operation:**
```python
# NO database operation - file system only
os.makedirs(scenarios_dir / folder_name, exist_ok=True)
```

---

### 5. **Manage Scenarios**
**File:** `routes/admin.py` - Line 427  
**Function:** `manage_scenarios()`  
**Route:** `GET /admin/scenarios`  
**What it does:**
- Show all scenarios and their stats

**Database Operation:**
```python
# Load scenarios from files
all_scenarios = scenario_manager.get_all_scenarios()
# Query database for play stats
plays = TrainingSession.query.filter_by(scenario_id=...)
```

---

## **TRAINING SESSION OPERATIONS**

### 1. **Start Training Session**
**File:** `routes/scenarios.py` - Line 78  
**Function:** `start(scenario_id)`  
**Route:** `POST /scenarios/<scenario_id>/start`  
**What it does:**
- Create new TrainingSession record
- Check for active session
- Set status to 'in_progress'

**Database Operation:**
```python
new_session = TrainingSession(
    user_id=current_user.id,
    scenario_id=scenario_id,
    status='in_progress',
    started_at=datetime.utcnow()
)
db.session.add(new_session)
db.session.commit()
```

---

### 2. **Submit Decision During Gameplay**
**File:** `routes/scenarios.py` - Line 155  
**Function:** `submit_decision(session_id)`  
**Route:** `POST /scenarios/session/<session_id>/submit`  
**What it does:**
- Save user's decision
- Calculate points
- Update session_data JSON

**Database Operation:**
```python
session = TrainingSession.query.get_or_404(session_id)
# Append decision to session_data
session.session_data = json.dumps(decisions_list)
db.session.commit()
```

---

### 3. **Complete Training Session**
**File:** `routes/scenarios.py` - (In submit_decision)  
**Function:** `submit_decision(session_id)`  
**Route:** `POST /scenarios/session/<session_id>/submit`  
**What it does:**
- Mark session as completed
- Save final score
- Calculate individual scores (detection, containment, etc.)

**Database Operation:**
```python
session = TrainingSession.query.get_or_404(session_id)
session.complete_session(final_score, outcome)
session.detection_score = detection
session.containment_score = containment
session.eradication_score = eradication
session.recovery_score = recovery
session.communication_score = communication
db.session.commit()
```

---

### 4. **View Session Results**
**File:** `routes/scenarios.py` - Line 240  
**Function:** `results(session_id)`  
**Route:** `GET /scenarios/session/<session_id>/results`  
**What it does:**
- Get completed session details
- Show score breakdown

**Database Operation:**
```python
session = TrainingSession.query.get_or_404(session_id)
# Get performance breakdown
breakdown = session.get_performance_breakdown()
```

---

### 5. **Export Results (CSV)**
**File:** `routes/admin.py` - Line 660  
**Function:** `export_results()`  
**Route:** `GET /admin/export-csv`  
**What it does:**
- Query all completed sessions
- Generate CSV file

**Database Operation:**
```python
completed_sessions = TrainingSession.query.filter_by(
    status='completed'
).all()
# Convert to CSV format
```

---

## **ADMIN DASHBOARD**

### Dashboard Statistics
**File:** `routes/admin.py` - Line 50  
**Function:** `dashboard()`  
**Route:** `GET /admin/dashboard`  
**What it does:**
- Get all statistics for dashboard

**Database Operations:**
```python
# For admins (all trainees):
total_users = User.query.filter_by(role='trainee').count()
total_sessions = TrainingSession.query.join(User).filter(
    User.role == 'trainee'
).count()
completed_sessions = TrainingSession.query.join(User).filter(
    User.role == 'trainee',
    TrainingSession.status == 'completed'
).count()

# For instructors (their group only):
total_users = User.query.filter(
    User.group_id == current_user.group_id,
    User.role == 'trainee'
).count()
```

---

## **QUICK LOOKUP TABLE**

| Operation | File | Function | Route | Table |
|-----------|------|----------|-------|-------|
| **Register User** | auth.py | register() | POST /register | users |
| **Add User** | admin.py | add_user() | POST /users/add | users |
| **Delete User** | admin.py | delete_user() | POST /users/<id>/delete | users, training_sessions |
| **Reset User Logs** | admin.py | reset_user_logs() | POST /users/<id>/reset-logs | training_sessions |
| **Login** | auth.py | login() | POST /login | users |
| **Change Password** | auth.py | change_password() | POST /change-password | users |
| **Assign to Group** | admin.py | assign_user_to_group() | POST /users/<id>/assign-to-group/<gid> | users |
| **Create Group** | admin.py | add_group() | POST /groups/add | groups |
| **Delete Group** | admin.py | delete_group() | POST /groups/<id>/delete | groups, users |
| **Add to Group** | admin.py | add_group_member() | POST /groups/<id>/add-member | users |
| **Remove from Group** | admin.py | remove_group_member() | POST /groups/<gid>/remove-member/<uid> | users |
| **Create Scenario** | admin.py | create_scenario() | POST /scenarios/create | (file system) |
| **Delete Scenario** | admin.py | delete_scenario() | POST /scenarios/<id>/delete | (file system) |
| **Start Session** | scenarios.py | start() | POST /scenarios/<id>/start | training_sessions |
| **Submit Decision** | scenarios.py | submit_decision() | POST /scenarios/session/<id>/submit | training_sessions |
| **Complete Session** | scenarios.py | submit_decision() | (automatic) | training_sessions |
| **View Results** | scenarios.py | results() | GET /scenarios/session/<id>/results | training_sessions |
| **Export CSV** | admin.py | export_results() | GET /admin/export-csv | training_sessions |
| **Dashboard** | admin.py | dashboard() | GET /admin/dashboard | users, training_sessions, groups |

---

## **Database Tables Summary**

**users** - User accounts (encrypted fields, password hashes)
**groups** - Training groups/organizations  
**training_sessions** - Individual gameplay records  
(Scenarios are stored as JSON files, not in database)

---

**Generated:** January 26, 2026
