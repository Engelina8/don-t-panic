# Scenario File-Based Storage Migration - Summary

## Overview
Scenarios are now stored as JSON files in the `scenarios/` folder instead of in a database. This allows for:
- Easy version control of scenarios
- Support for category folders (organize scenarios by type)
- Complete metadata included in each JSON file
- No database dependency for scenarios

## Changes Made

### 1. **New ScenarioManager Class** (`scenario_manager.py`)
- Manages all file-based scenario operations
- Methods:
  - `get_all_scenarios()` - Load all scenarios recursively
  - `get_scenario(id)` - Get a specific scenario
  - `get_scenarios_by_category(category)` - Get scenarios in a folder
  - `get_categories()` - List all category folders
  - `create_scenario(data, category)` - Create new scenario file
  - `update_scenario(id, data)` - Update existing scenario
  - `delete_scenario(id)` - Delete scenario file
  - `create_category(name)` - Create category folder
  - `move_scenario_to_category(id, category)` - Organize scenarios

### 2. **Updated Scenario Model** (`models.py`)
- Changed from database model to simple Python class
- Stores all scenario information from JSON
- Attributes:
  - `id` - Unique identifier
  - `title` - Scenario title
  - `description` - Full description
  - `category` - Folder/category name
  - `incident_type` - Type of incident
  - `difficulty_level` - 1-5 difficulty scale
  - `estimated_time` - Time in minutes
  - `max_points` - Maximum points possible
  - `scenario_content` - Decision tree/story branches (JSON object)
  - `created_by` - Creator user ID
  - `created_at` - Creation timestamp
  - `updated_at` - Last update timestamp
  - `is_active` - Active status

### 3. **Updated Routes** 

#### `routes/scenarios.py`
- Updated to load scenarios from files instead of database
- Uses `scenario_manager` to get scenario data
- Converts scenario data dict to `Scenario` objects for templates

#### `routes/admin.py`
- Import added: `from scenario_manager import scenario_manager`
- Updated functions:
  - `manage_scenarios()` - Lists all JSON scenarios
  - `create_scenario()` - Creates new JSON file with metadata
  - `edit_scenario()` - Updates JSON file
  - `delete_scenario()` - Deletes JSON file
  - `reports()` - Updated to work with file-based scenarios
- Now admin-only (changed from instructor-required)

### 4. **Configuration** (`config.py`)
- Removed `SQLALCHEMY_BINDS` for scenarios database
- Added `SCENARIOS_FOLDER` config pointing to `scenarios/` directory
- Single database now contains only: Users, Groups, Training Sessions

### 5. **Migration Script** (`migrate_scenarios.py`)
- Exports existing scenarios from old `scenarios.db` database
- Creates JSON files for each scenario
- Preserves all metadata and scenario content
- Run: `python migrate_scenarios.py`

### 6. **Git Configuration** (`.gitignore`)
- Updated to ignore `instance/` directory
- Ignores `.db` files except `users_training.db`
- **Does NOT ignore** `scenarios/` folder (version-controlled)

## File Structure

```
project/
├── scenarios/                 # Version-controlled scenario storage
│   ├── 1.json                # Scenario ID 1
│   ├── 2.json                # Scenario ID 2
│   ├── ransomware/           # Category folder
│   │   ├── 3.json
│   │   └── 4.json
│   └── data_breach/          # Another category
│       └── 5.json
├── instance/
│   └── users_training.db     # Single database file (tracked)
└── [other files]
```

## JSON Scenario Format

```json
{
  "id": "1",
  "title": "Ransomware Attack Response",
  "description": "Handle a critical ransomware incident...",
  "category": "ransomware",
  "incident_type": "ransomware",
  "difficulty_level": 3,
  "estimated_time": 30,
  "max_points": 100,
  "scenario_content": {
    "intro": "Your company's systems have been encrypted...",
    "stages": [
      {
        "stage": "detection",
        "question": "What is your first action?",
        "options": [
          {"text": "Disconnect from network", "points": 20},
          {"text": "Pay the ransom", "points": -10}
        ]
      }
    ]
  },
  "created_by": 1,
  "created_at": "2025-11-25T13:17:10.149775",
  "updated_at": "2025-11-25T13:17:10.149775",
  "is_active": true,
  "times_played": 0,
  "average_score": 0.0
}
```

## Benefits

✅ **Version Control Friendly** - Scenarios tracked in git
✅ **Easy Organization** - Category folders for different incident types
✅ **Self-Contained** - All scenario data in one JSON file
✅ **No Database Overhead** - Scenarios independent from database
✅ **Easy Sharing** - Can share scenario files between projects
✅ **Readable Format** - Human-editable JSON files
✅ **Scalable** - Supports unlimited categories and scenarios

## Migration Instructions

1. Run migration script:
   ```bash
   python migrate_scenarios.py
   ```

2. Verify scenarios migrated:
   ```bash
   python test_scenarios.py
   ```

3. Test the application (old scenarios.db can be deleted):
   ```bash
   python run.py
   ```

## Database Structure (After Migration)

### users_training.db (single database)
- `users` table - User accounts
- `groups` table - Training groups
- `training_sessions` table - Training session records
- ~~`scenarios` table~~ - **REMOVED (now in JSON files)**

### scenarios/ folder (file system)
- Individual `.json` files for each scenario
- Organized in category subfolders
- All scenario metadata included in JSON

## Backward Compatibility

- Old `scenarios.db` file can be kept for reference
- Migration script ensures no data loss
- All existing functionality preserved
- Templates work with both old and new structure

## Future Enhancements

- Web UI for creating categories
- Bulk scenario uploads
- Scenario versioning
- Scenario templates
- Scenario export/import functionality
