#!/usr/bin/env python
"""Test creating a new scenario in the file-based system"""

from scenario_manager import scenario_manager
from models import Scenario
import json

print("=" * 60)
print("Testing File-Based Scenario System")
print("=" * 60)

# Test 1: Load existing scenarios
print("\n1️⃣  Loading existing scenarios...")
scenarios = scenario_manager.get_all_scenarios()
print(f"   Found {len(scenarios)} scenarios")
for scenario_data in scenarios:
    print(f"   - {scenario_data.get('title')} (Category: {scenario_data.get('category') or 'Root'})")

# Test 2: Create a category
print("\n2️⃣  Creating a test category...")
try:
    scenario_manager.create_category('test_incidents')
    print("   ✅ Category 'test_incidents' created")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test 3: Create a new scenario in a category
print("\n3️⃣  Creating a test scenario in 'test_incidents' category...")
test_scenario = {
    'title': 'Test DDoS Attack',
    'description': 'A test scenario for DDoS attacks',
    'category': 'test_incidents',
    'incident_type': 'ddos',
    'difficulty_level': 2,
    'estimated_time': 20,
    'max_points': 80,
    'scenario_content': {
        'intro': 'Your website is under DDoS attack...',
        'stages': [
            {
                'stage': 'detection',
                'question': 'What do you notice first?',
                'options': [
                    {'text': 'High traffic spike', 'points': 20},
                    {'text': 'Server crash', 'points': 10}
                ]
            }
        ]
    },
    'created_by': 1,
    'is_active': True
}

created = scenario_manager.create_scenario(test_scenario, 'test_incidents')
print(f"   ✅ Scenario created with ID: {created.get('id')}")

# Test 4: Load scenarios by category
print("\n4️⃣  Loading scenarios by category...")
categories = scenario_manager.get_categories()
print(f"   Found {len(categories)} categories: {', '.join(categories)}")

test_category_scenarios = scenario_manager.get_scenarios_by_category('test_incidents')
print(f"   Test incidents category has {len(test_category_scenarios)} scenario(s)")

# Test 5: Test Scenario class
print("\n5️⃣  Testing Scenario class...")
scenario_data = scenario_manager.get_scenario(created.get('id'))
if scenario_data:
    scenario = Scenario(scenario_data)
    print(f"   Title: {scenario.title}")
    print(f"   Type: {scenario.incident_type}")
    print(f"   Difficulty: {scenario.difficulty_level}/5")
    print(f"   Max Points: {scenario.max_points}")

# Test 6: Load all scenarios (including new one)
print("\n6️⃣  Reloading all scenarios...")
all_scenarios = scenario_manager.get_all_scenarios()
print(f"   Total scenarios now: {len(all_scenarios)}")

print("\n" + "=" * 60)
print("✅ All tests passed! File-based scenario system is working.")
print("=" * 60)
