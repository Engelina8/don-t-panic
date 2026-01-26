"""Scenario Manager - Handle file-based scenario storage"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

class ScenarioManager:
    """Manages scenarios stored as JSON files in folder structure"""

    def __init__(self, scenarios_dir='scenarios'):
        """Initialize with scenarios directory"""
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios_dir.mkdir(exist_ok=True)

    def get_all_scenarios(self):
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
        for scenario_file in self.scenarios_dir.rglob('*.json'):
            try:
                scenario = self._load_scenario_from_file(scenario_file)
                if scenario and scenario.get('id') == scenario_id:
                    return scenario
            except Exception as e:
                print(f"Error loading scenario {scenario_file}: {e}")

        return None

    def get_scenarios_by_category(self, category):
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
        categories = []

        for item in self.scenarios_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                categories.append(item.name)

        return sorted(categories)

    def create_scenario(self, scenario_data, category=''):

        if 'id' not in scenario_data:
            scenario_data['id'] = self._generate_scenario_id()


        if 'created_at' not in scenario_data:
            scenario_data['created_at'] = datetime.utcnow().isoformat()

        if 'updated_at' not in scenario_data:
            scenario_data['updated_at'] = datetime.utcnow().isoformat()


        filename = self._slugify_title(scenario_data.get('title', 'scenario'))
        filename = f"{filename}_{scenario_data['id']}"


        if category:
            category_dir = self.scenarios_dir / category
            category_dir.mkdir(exist_ok=True)
            file_path = category_dir / f"{filename}.json"
        else:
            file_path = self.scenarios_dir / f"{filename}.json"


        counter = 1
        original_file_path = file_path
        while file_path.exists():
            name, ext = os.path.splitext(original_file_path)
            file_path = Path(f"{name}_{counter}{ext}")
            counter += 1


        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)

        return scenario_data

    def _slugify_title(self, title):
        slug = re.sub(r'[^\w\s-]', '', title).lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def update_scenario(self, scenario_id, scenario_data):
        scenario_file = self._find_scenario_file(scenario_id)

        if not scenario_file:
            raise FileNotFoundError(f"Scenario {scenario_id} not found")

        original = self._load_scenario_from_file(scenario_file)
        scenario_data['id'] = scenario_id
        scenario_data['created_at'] = original.get('created_at', datetime.utcnow().isoformat())
        scenario_data['updated_at'] = datetime.utcnow().isoformat()

        new_filename = self._slugify_title(scenario_data.get('title', 'scenario'))
        new_filename = f"{new_filename}_{scenario_id}"
        new_file_path = scenario_file.parent / f"{new_filename}.json"

        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)

        if scenario_file != new_file_path and not new_file_path.exists():
            scenario_file.rename(new_file_path)

        return scenario_data

    def delete_scenario(self, scenario_id):
        print(f"[ScenarioManager] Searching for scenario to delete: {scenario_id}")
        scenario_file = self._find_scenario_file(scenario_id)

        if not scenario_file:
            print(f"[ScenarioManager] Scenario file not found for ID: {scenario_id}")
            raise FileNotFoundError(f"Scenario {scenario_id} not found")

        try:
            print(f"[ScenarioManager] Deleting file: {scenario_file}")
            scenario_file.unlink()
            print(f"[ScenarioManager] Successfully deleted file: {scenario_file}")
            return True
        except Exception as e:
            print(f"[ScenarioManager] Error deleting file: {e}")
            raise

    def create_category(self, category_name):
        category_dir = self.scenarios_dir / category_name
        category_dir.mkdir(exist_ok=True)
        return category_name

    def move_scenario_to_category(self, scenario_id, category):
        scenario_file = self._find_scenario_file(scenario_id)

        if not scenario_file:
            raise FileNotFoundError(f"Scenario {scenario_id} not found")


        scenario_data = self._load_scenario_from_file(scenario_file)


        category_dir = self.scenarios_dir / category
        category_dir.mkdir(exist_ok=True)


        new_path = category_dir / scenario_file.name
        scenario_file.rename(new_path)

        return scenario_data



    def _generate_scenario_id(self):
        """Generate a unique scenario ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def _find_scenario_file(self, scenario_id):
        """Find the file path for a scenario by ID"""
        print(f"[ScenarioManager] _find_scenario_file searching for ID: '{scenario_id}' (type: {type(scenario_id)})")
        for scenario_file in self.scenarios_dir.rglob('*.json'):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_id = data.get('id')
                    print(f"[ScenarioManager] Found file {scenario_file.name} with ID: '{file_id}' (type: {type(file_id)})")
                    if file_id == scenario_id:
                        print(f"[ScenarioManager] MATCH FOUND: {scenario_file}")
                        return scenario_file
            except Exception as e:
                print(f"[ScenarioManager] Error reading file {scenario_file}: {e}")
                continue

        print(f"[ScenarioManager] No matching file found for ID: {scenario_id}")
        return None

    def _load_scenario_from_file(self, file_path):
        """Load a scenario from a JSON file and set category from folder path"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_path = Path(file_path)
        relative_path = file_path.parent.relative_to(self.scenarios_dir)

        if str(relative_path) != '.':
            data['category'] = str(relative_path)
        else:
            data['category'] = ''

        return data


scenario_manager = ScenarioManager()
