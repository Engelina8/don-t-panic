"""Migrate scenarios from database to JSON files"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

def migrate_scenarios_to_json():
    """Migrate scenarios from old scenarios.db to JSON files"""
    

    scenarios_db_path = Path('instance/scenarios.db')
    scenarios_dir = Path('scenarios')
    
    if not scenarios_db_path.exists():
        print("❌ Old scenarios.db not found. Nothing to migrate.")
        return
    
    scenarios_dir.mkdir(exist_ok=True)
    
    try:

        conn = sqlite3.connect(str(scenarios_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        

        cursor.execute('SELECT * FROM scenarios')
        scenarios = cursor.fetchall()
        
        migrated_count = 0
        
        for scenario in scenarios:
            try:

                scenario_content = json.loads(scenario['scenario_content'])
                

                scenario_data = {
                    'id': str(scenario['id']),
                    'title': scenario['title'],
                    'description': scenario['description'],
                    'category': '',
                    'incident_type': scenario['incident_type'],
                    'difficulty_level': scenario['difficulty_level'],
                    'estimated_time': scenario['estimated_time'],
                    'max_points': scenario['max_points'],
                    'scenario_content': scenario_content,
                    'created_by': scenario['created_by'],
                    'created_at': scenario['created_at'],
                    'updated_at': scenario['updated_at'],
                    'is_active': bool(scenario['is_active']),
                    'times_played': scenario['times_played'],
                    'average_score': scenario['average_score']
                }
                

                file_path = scenarios_dir / f"{scenario_data['id']}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(scenario_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Migrated: {scenario_data['title']} (ID: {scenario_data['id']})")
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to migrate scenario {scenario['id']}: {e}")
        
        conn.close()
        
        print(f"\n✅ Migration complete! {migrated_count} scenarios migrated to JSON files.")
        print(f"📁 Scenarios stored in: {scenarios_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")


if __name__ == '__main__':
    print("🔄 Migrating scenarios from database to JSON files...")
    print("="*60)
    migrate_scenarios_to_json()
