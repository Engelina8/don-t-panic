# Don't Panic - Admin Instructions Guide

Welcome to the Don't Panic Incident Response Training Platform! This guide walks you through all admin features and how to use them effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Admin Dashboard](#admin-dashboard)
3. [Managing Scenarios](#managing-scenarios)
4. [Managing Users](#managing-users)
5. [Viewing Reports](#viewing-reports)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Logging In

1. Navigate to the login page at `http://localhost:5000/login`
2. Use your instructor credentials:
   - **Default Username:** `instructor`
   - **Default Password:** `instructor123`
3. Click **Login**
4. You will be redirected to your **Admin Dashboard**

### Accessing Admin Features

Once logged in, you have access to:
- **Dashboard** - Overview of platform activity and statistics
- **Admin** - Main navigation menu in the header (visible to instructors only)
- **Manage Scenarios** - Create, edit, and delete training scenarios
- **Manage Users** - View and manage trainee accounts
- **Reports** - View analytics and training performance data

---

## Admin Dashboard

### Overview

The Admin Dashboard provides a quick snapshot of your training platform:

- **Total Users** - Number of trainees registered
- **Total Scenarios** - Number of training scenarios available
- **Total Sessions** - Number of training sessions started
- **Completion Rate** - Percentage of sessions completed
- **Recent Activity** - Table showing recent trainee sessions

### Quick Actions

From the dashboard, you can quickly:
- **Manage Users** - Go to the user management page
- **Manage Scenarios** - Go to scenario management
- **View Reports** - Access detailed analytics

### Understanding the Metrics

| Metric | Description |
|--------|-------------|
| **Total Users** | Count of trainee accounts in the system |
| **Total Scenarios** | Count of available training scenarios |
| **Total Sessions** | Total number of times trainees have started any scenario |
| **Completed Sessions** | Sessions where trainee reached the end and got a score |
| **Completion Rate** | (Completed Sessions / Total Sessions) × 100% |

---

## Managing Scenarios

### Overview

Scenarios are training exercises where trainees respond to incident response situations. Each scenario contains:
- **Title** - Name of the scenario (e.g., "Ransomware Attack Response")
- **Description** - Brief summary of what the scenario teaches
- **Incident Type** - Category (Ransomware, Data Breach, DDoS, Phishing, Insider Threat, Malware)
- **Difficulty Level** - 1-5 stars (1=Beginner, 5=Expert)
- **Estimated Time** - Expected completion time in minutes
- **Scenario Content** - The actual story, stages, and decision options (JSON format)

### Accessing Scenario Management

1. Click **Admin** in the header
2. Select **Manage Scenarios**
3. You'll see a grid of all existing scenarios

### Creating a Scenario

#### Method 1: Quick Create (Simple)

For simple scenarios without complex branching:

1. On the Manage Scenarios page, click **Quick Create Scenario** to expand the form
2. Fill in:
   - **Title** - e.g., "Phishing Attack Detection"
   - **Description** - What trainees will learn
   - **Incident Type** - Select from dropdown
   - **Difficulty Level** - Choose 1-5
   - **Estimated Time** - Minutes to complete
3. Leave "Advanced (JSON)" unchecked
4. Click **Create**
5. Scenario is created with the description as a simple intro

#### Method 2: Full Editor (Advanced)

For complete control over scenarios with multiple stages and decision branches:

1. Click **+ Create New Scenario** (top of Manage Scenarios page)
2. Fill in basic metadata:
   - Title, Description, Incident Type, Difficulty, Time
3. **Use the Scenario Builder** (recommended):
   - Enter **Intro** - Initial incident description
   - Click **+ Add Stage** for each decision point
   - For each stage:
     - Enter **Stage name** (optional) - e.g., "Detection Phase"
     - Enter **Question** - What should the trainee do? e.g., "How do you respond?"
     - Click **+ Add Option** for each choice
       - **Option text** - e.g., "Escalate to Security Team"
       - **Points** - Score for choosing this option (positive = good, negative = bad)
   - Click **Remove Option** to delete wrong choices
   - Click **Remove Stage** to delete entire stages
4. **Or use Advanced Mode** (raw JSON):
   - Check **Show raw JSON**
   - Edit the JSON directly (see JSON Format below)
   - Must be valid JSON or submission will fail
5. Click **Format JSON** to auto-format
6. Click **Validate** to check structure
7. Click **✓ Create Scenario** to save

### Understanding Scenario JSON Format

Scenarios are stored as JSON with this structure:

```json
{
  "intro": "Your company's systems have been compromised. You are the incident response lead. What do you do?",
  "stages": [
    {
      "stage": "detection",
      "question": "What is your first action?",
      "options": [
        {"text": "Escalate to Security Team immediately", "points": 25},
        {"text": "Investigate on your own first", "points": 15},
        {"text": "Ignore it and continue work", "points": -30}
      ]
    },
    {
      "stage": "containment",
      "question": "How do you contain the threat?",
      "options": [
        {"text": "Isolate affected systems from network", "points": 30},
        {"text": "Shut down all systems", "points": 10},
        {"text": "Just monitor the situation", "points": -20}
      ]
    }
  ]
}
```

**Key Fields:**
- **intro** - Opening narrative (string)
- **stages** - Array of decision points
  - **stage** - Name of phase (string, optional)
  - **question** - What choice faces the trainee (string)
  - **options** - Array of possible decisions
    - **text** - Choice description (string)
    - **points** - Score impact: positive=correct, negative=incorrect, 0=neutral (integer)

### Editing a Scenario

1. On Manage Scenarios, click **✏️ Edit** on any scenario card
2. Make changes using the Scenario Builder or raw JSON
3. Click **✓ Update Scenario** to save
4. Redirects to Manage Scenarios on success

### Deleting a Scenario

1. On Manage Scenarios, click **🗑️ Delete** on any scenario
2. Confirm the deletion in the popup dialog
3. Scenario is removed and page reloads

**Note:** Deleting a scenario does **not** delete existing training sessions or scores from that scenario.

### Loading a Template

To quickly create a scenario from a template:

1. Click **+ Create New Scenario**
2. In the Scenario Builder section, click **Load Template**
3. A pre-built scenario with multiple stages and realistic options loads
4. Edit the template to match your needs
5. Save

---

## Managing Users

### Accessing User Management

1. Click **Admin** in the header
2. Select **Manage Users**
3. View all trainee accounts in a table

### User Management Table

Columns displayed:
- **Username** - Trainee's login name
- **Email** - Trainee's email address
- **Progress** - Shows format "X/Y" (X completed, Y started)
- **Status** - Indicator showing Active or Inactive
- **Actions** - View and Delete buttons

### Viewing User Details

1. Click **View** on any user row
2. See:
   - User profile info
   - Training history (all sessions)
   - Overall statistics (completion rate, average score)
   - List of previous attempts at scenarios with dates and scores

### Searching for Users

1. Use the **Search** box at the top of the users table
2. Type username or email
3. Table filters in real-time

### Deleting a User

1. Click **Delete** button on any user row
2. Confirm deletion in popup
3. User account is permanently removed
4. **Note:** All associated training sessions and data are also deleted

---

## Viewing Reports

### Accessing Reports

1. Click **Admin** in the header
2. Select **View Reports** (or from dashboard Quick Actions)

### Report Features

Reports show:
- **All Completed Training Sessions** - Every trainee's completed session with:
  - Trainee username
  - Scenario name
  - Start date/time
  - Status (Completed, In Progress, Abandoned)
  - Final score
  - Time taken

- **Scenario Performance Stats** - For each scenario:
  - Number of attempts
  - Average score across all attempts

### Using Reports

- Identify which scenarios are most challenging (low average scores)
- See which trainees are progressing well
- Monitor completion rates
- Identify struggling trainees who may need extra support

---

## Best Practices

### Scenario Design

1. **Keep Questions Clear** - Make it obvious what decision the trainee must make
2. **Realistic Scenarios** - Base on real incidents trainees might face
3. **Progressive Difficulty** - Build scenarios that increase in complexity as trainees advance
4. **Balance Rewards** - Use point spreads (e.g., +30 for best, +10 for okay, -20 for bad) to incentivize learning
5. **Multiple Stages** - Create 2-5 decision points per scenario for engagement
6. **Realistic Options** - Include one clearly correct choice, one questionable choice, and one clearly wrong choice

### Scenario Points Guidelines

| Point Value | Meaning | Example |
|---|---|---|
| +25 to +50 | Excellent decision | "Escalate immediately to security team" |
| +10 to +20 | Good decision | "Check logs before deciding" |
| 0 | Neutral decision | "Wait and see what happens" |
| -10 to -20 | Poor decision | "Ignore the warning" |
| -30 to -50 | Dangerous decision | "Delete all logs to cover tracks" |

### User Management

1. **Monitor Progress** - Regularly check reports to see who's struggling
2. **Clean Up Inactive** - Remove test accounts after creating scenarios
3. **Track Completions** - Use progress tracking to identify high performers for advanced training

### Regular Maintenance

1. **Update Scenarios** - Refresh scenarios to match current threats
2. **Review Performance** - Check reports monthly to identify gaps
3. **Collect Feedback** - Ask trainees which scenarios are most useful
4. **Archive Old Data** - Delete completed sessions periodically (currently no archival feature)

---

## Troubleshooting

### Delete Button Not Working

**Problem:** Clicking delete doesn't remove the scenario/user

**Solutions:**
1. **Refresh the page** and try again
2. **Check browser console** (F12 → Console) for errors
3. **Verify you're logged in** - Session may have expired
4. **Check server logs** - Restart Flask and try again
5. **Try again** - Sometimes network hiccups cause failures

### Scenario Not Saving

**Problem:** After clicking Create/Update, nothing happens

**Solutions:**
1. **Check JSON validity** - Click "Validate" button to check for errors
2. **Fill all required fields** - Title, Description, and Scenario Content are required
3. **Check browser console** for error messages
4. **Use simpler JSON** - Try the Quick Create method instead

### Points Not Calculating in Play View

**Problem:** Trainee completes scenario but score doesn't reflect choices

**Solutions:**
1. **Verify JSON format** - Ensure all options have "points" field (integer)
2. **Check points are numeric** - They should be numbers, not strings
3. **Reload page** - Browser may have cached old scenario

### Can't Edit Scenario

**Problem:** Edit button not working or changes don't save

**Solutions:**
1. **Verify instructor role** - Only instructors can edit
2. **Check your login** - You may have been logged out
3. **Try creating new scenario** - If edit fails, create a duplicate and delete the original

### Users Table Empty

**Problem:** No trainees appear in user management

**Solutions:**
1. **This is normal if no trainees have registered** - Have test users register first
2. **Check filters** - Make sure search box is empty
3. **Refresh page** - (Ctrl+Shift+R on Windows)

### Server Error When Starting Flask

**Problem:** `python run.py` produces errors

**Solutions:**
1. **Check Python version** - Requires Python 3.7+
2. **Install dependencies** - Run: `pip install -r requirements.txt`
3. **Check database** - Delete `instance/dont_panic.db` and restart (will create fresh DB)
4. **Port in use** - If port 5000 is taken, edit `run.py` to use different port

---

## Quick Reference

### Navigation Menu (Logged in as Instructor)

| Menu Item | Purpose | URL |
|-----------|---------|-----|
| Home | Return to homepage | `/` |
| Dashboard | View user dashboard | `/dashboard` |
| Scenarios | View all scenarios | `/scenarios` |
| Admin | Go to admin dashboard | `/admin/dashboard` |
| Logout | End session | `/logout` |

### Admin Submenu

| Menu Item | Purpose | URL |
|-----------|---------|-----|
| Admin Dashboard | Platform overview | `/admin/dashboard` |
| Manage Users | View/delete trainees | `/admin/users` |
| Manage Scenarios | CRUD scenarios | `/admin/scenarios/manage` |
| View Reports | Analytics dashboard | `/admin/reports` |

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search users | Click search box on Users page |
| Format JSON | Click "Format JSON" button in editor |
| Validate JSON | Click "Validate" button in editor |
| Quick confirmation | Click "Load Template" to start with example |

---

## Support & Next Steps

### Common Tasks

- **Create first scenario** → Go to Manage Scenarios → Click "Create New Scenario" → Use Scenario Builder
- **Check trainee progress** → Go to Manage Users → Click "View" on a trainee name
- **See overall stats** → Go to Admin Dashboard (homepage for admins)
- **Find low performers** → Go to Reports and sort by scenario/average score

### Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. Review server logs (terminal where Flask runs)
3. Clear browser cache and refresh (Ctrl+Shift+R)
4. Try a different browser if issues persist

---

## Version Info

- **Platform:** Don't Panic v1.0
- **Last Updated:** December 1, 2025
- **Requirements:** Python 3.7+, Flask, SQLAlchemy

**Happy training! 🎯**
