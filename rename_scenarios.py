import json
import os
from pathlib import Path

scenarios_dir = Path('scenarios')

# Get all JSON files in scenarios directory
scenario_files = list(scenarios_dir.glob('*.json'))

print(f"Found {len(scenario_files)} scenario files\n")

for file_path in scenario_files:
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get title and id
        title = data.get('title', 'Untitled')
        scenario_id = data.get('id', file_path.stem)
        
        # Sanitize title for filename (remove special characters, replace spaces with underscores)
        sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
        sanitized_title = sanitized_title.replace(' ', '_').lower()
        
        # Create new filename: "title_id.json"
        new_filename = f"{sanitized_title}_{scenario_id}.json"
        new_file_path = scenarios_dir / new_filename
        
        # Only rename if different
        if file_path.name != new_filename:
            # Rename the file
            os.rename(str(file_path), str(new_file_path))
            print(f"✅ Renamed: {file_path.name} → {new_filename}")
        else:
            print(f"⊘ Already named correctly: {new_filename}")
            
    except json.JSONDecodeError as e:
        print(f"❌ Error reading {file_path.name}: Invalid JSON - {e}")
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")

print("\n✅ Scenario renaming complete!")
