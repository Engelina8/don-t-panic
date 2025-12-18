import json
from app import create_app
from scenario_manager import scenario_manager

app = create_app()

with app.app_context():

    scenario_data = {
        "title": "Ransomware Outbreak Response",
        "description": "A company discovers that multiple workstations have been infected with ransomware. You need to respond quickly to contain the threat.",
        "incident_type": "ransomware",
        "difficulty_level": 2,
        "estimated_time": 20,
        "max_points": 100,
        "intro": "It's 9 AM on a Monday morning. Your SOC team reports that 15 workstations are displaying a ransom note. The attackers are demanding $100,000 in Bitcoin. Time to respond!",
        "stages": [
            {
                "stage": "Detection & Analysis",
                "content": "The incident has just been detected. What's your first action?",
                "question": "What should be your immediate response?",
                "metrics": ["detection"],
                "options": [
                    {
                        "text": "Isolate affected systems from the network immediately",
                        "points": 25,
                        "detection": 10,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Pay the ransom to minimize downtime",
                        "points": -20,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Notify management and wait for instructions",
                        "points": 5,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 5
                    }
                ]
            },
            {
                "stage": "Containment",
                "content": "You've isolated the infected machines. Now what?",
                "question": "How do you prevent spread to other systems?",
                "metrics": ["detection", "containment"],
                "options": [
                    {
                        "text": "Activate network segmentation and block lateral movement paths",
                        "points": 30,
                        "detection": 5,
                        "containment": 15,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Shut down the entire network",
                        "points": 10,
                        "detection": 0,
                        "containment": 10,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Monitor for suspicious activity",
                        "points": 15,
                        "detection": 10,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    }
                ]
            },
            {
                "stage": "Eradication",
                "content": "Time to remove the malware.",
                "question": "What's the best approach to eradicate the ransomware?",
                "metrics": ["eradication", "recovery"],
                "options": [
                    {
                        "text": "Wipe and rebuild affected systems from clean backups",
                        "points": 30,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 15,
                        "recovery": 10,
                        "communication": 0
                    },
                    {
                        "text": "Run antivirus scans and hope for the best",
                        "points": 5,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 5,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Decrypt with a free decryption tool",
                        "points": 0,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    }
                ]
            },
            {
                "stage": "Recovery & Communication",
                "content": "Systems are clean. Time to recover and communicate.",
                "question": "How do you handle recovery and stakeholder communication?",
                "metrics": ["recovery", "communication"],
                "options": [
                    {
                        "text": "Restore from backups, notify stakeholders transparently, and brief leadership",
                        "points": 15,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 8,
                        "communication": 8
                    },
                    {
                        "text": "Quietly restore systems without informing anyone",
                        "points": -10,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 0
                    },
                    {
                        "text": "Wait 24 hours before any communication",
                        "points": 5,
                        "detection": 0,
                        "containment": 0,
                        "eradication": 0,
                        "recovery": 0,
                        "communication": 2
                    }
                ]
            }
        ]
    }
    

    existing_scenarios = scenario_manager.get_all_scenarios()
    for scenario_data in existing_scenarios:
        if scenario_data.get('title') == "Ransomware Outbreak Response":
            print(f"Test scenario already exists")
            scenario_id = scenario_data.get('id')
            print(f"Scenario ID: {scenario_id}")
            exit(0)
    

    scenario_manager.create_scenario(scenario_data)
    
    print("Test scenario created successfully!")
    print("Title: {0}".format(scenario_data['title']))
    print("Max Points: {0}".format(scenario_data['max_points']))
    all_scenarios = scenario_manager.get_all_scenarios()
    for scenario in all_scenarios:
        if scenario.get('title') == scenario_data['title']:
            scenario_id = scenario.get('id')
            print("\nPlay URL: http://localhost:5000/scenarios/{0}".format(scenario_id))
