
"""Test the file-based scenario system"""

from app import create_app
from scenario_manager import scenario_manager

app = create_app('development')
print('✅ App initialized successfully')

scenarios = scenario_manager.get_all_scenarios()
print(f'📁 Found {len(scenarios)} scenarios:')

for s in scenarios:
    print(f'  - ID: {s.get("id")}, Title: {s.get("title")}')

print('\n✅ File-based scenario system is working!')
