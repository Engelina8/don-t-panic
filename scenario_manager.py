"""Scenario Manager - Handle file-based scenario storage"""

import os
import json
from datetime import datetime
from pathlib import Path

class ScenarioManager:
    """Manages scenarios stored as JSON files in folder structure"""
    
    def __init__(self, scenarios_dir='scenarios'):
        """Initialize with scenarios directory"""
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios_dir.mkdir(exist_ok=True)
    
    def get_all_scenarios(self):
        """Get all scenarios from all folders (recursive)"""
        scenarios = []
        
        for scenario_file in self.scenarios_dir.rglob('*.json'):
            try:
                scenario = self._load_scenario_from_file(scenario_file)
                if scenario:
                    scenarios.append(scenario)
            except Exception as e:
                print(f"Error loading scenario {scenario_file}: {e}")
        
        return sorted(scenarios, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_scenario(self, scenario_id):
        """Get a specific scenario by ID"""
        for scenario_file in self.scenarios_dir.rglob('*.json'):
            try:
                scenario = self._load_scenario_from_file(scenario_file)
                if scenario and scenario.get('id') == scenario_id:
                    return scenario
            except Exception as e:
                print(f"Error loading scenario {scenario_file}: {e}")
        
        return None
    
    def get_scenarios_by_category(self, category):
        """Get scenarios in a specific category (folder)"""
        category_dir = self.scenarios_dir / category
        
        if not category_dir.exists():
            return []
        
        scenarios = []
        for scenario_file in category_dir.glob('*.json'):
            try:
                scenario = self._load_scenario_from_file(scenario_file)
                if scenario:
                    scenarios.append(scenario)
            except Exception as e:
                print(f"Error loading scenario {scenario_file}: {e}")
        
        return sorted(scenarios, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_categories(self):
        """Get all category folders"""
        categories = []
        
        for item in self.scenarios_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                categories.append(item.name)
        
        return sorted(categories)
    
    def create_scenario(self, scenario_data, category=''):
        """Create a new scenario file"""
        # Generate ID if not provided
        if 'id' not in scenario_data:
            scenario_data['id'] = self._generate_scenario_id()
        
        # Add timestamps if not present
        if 'created_at' not in scenario_data:
            scenario_data['created_at'] = datetime.utcnow().isoformat()
        
        if 'updated_at' not in scenario_data:
            scenario_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Determine file path
        if category:
            category_dir = self.scenarios_dir / category
            category_dir.mkdir(exist_ok=True)
            file_path = category_dir / f"{scenario_data['id']}.json"
        else:
            file_path = self.scenarios_dir / f"{scenario_data['id']}.json"
        
        # Write JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)
        
        return scenario_data
    
    def update_scenario(self, scenario_id, scenario_data):
        """Update an existing scenario"""
        scenario_file = self._find_scenario_file(scenario_id)
        
        if not scenario_file:
            raise FileNotFoundError(f"Scenario {scenario_id} not found")
        
        # Keep original metadata
        original = self._load_scenario_from_file(scenario_file)
        scenario_data['id'] = scenario_id
        scenario_data['created_at'] = original.get('created_at', datetime.utcnow().isoformat())
        scenario_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Write updated JSON
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)
        
        return scenario_data
    
    def delete_scenario(self, scenario_id):
        """Delete a scenario file"""
        scenario_file = self._find_scenario_file(scenario_id)
        
        if not scenario_file:
            raise FileNotFoundError(f"Scenario {scenario_id} not found")
        
        scenario_file.unlink()
        return True
    
    def create_category(self, category_name):
        """Create a new category folder"""
        category_dir = self.scenarios_dir / category_name
        category_dir.mkdir(exist_ok=True)
        return category_name
    
    def move_scenario_to_category(self, scenario_id, category):
        """Move a scenario to a different category"""
        scenario_file = self._find_scenario_file(scenario_id)
        
        if not scenario_file:
            raise FileNotFoundError(f"Scenario {scenario_id} not found")
        
        # Load scenario data
        scenario_data = self._load_scenario_from_file(scenario_file)
        
        # Create target directory if needed
        category_dir = self.scenarios_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Move file
        new_path = category_dir / scenario_file.name
        scenario_file.rename(new_path)
        
        return scenario_data
    
    # Private helper methods
    
    def _generate_scenario_id(self):
        """Generate a unique scenario ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _find_scenario_file(self, scenario_id):
        """Find the file path for a scenario by ID"""
        for scenario_file in self.scenarios_dir.rglob('*.json'):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('id') == scenario_id:
                        return scenario_file
            except Exception:
                continue
        
        return None
    
    def _load_scenario_from_file(self, file_path):
        """Load a scenario from a JSON file and set category from folder path"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Set category based on folder location (not from JSON)
        file_path = Path(file_path)
        relative_path = file_path.parent.relative_to(self.scenarios_dir)
        
        # If file is in root scenarios folder, category is empty
        # If file is in a subfolder, category is the folder name
        if str(relative_path) != '.':
            data['category'] = str(relative_path)
        else:
            data['category'] = ''
        
        return data


# Global instance
scenario_manager = ScenarioManager()
