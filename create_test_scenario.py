import json
from app import create_app
from models import db, Scenario, User

app = create_app()

with app.app_context():
    # Get the first admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("No admin user found")
        exit(1)
    
    # Create test scenario JSON
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
    
    # Check if test scenario already exists
    existing = Scenario.query.filter_by(title="Ransomware Outbreak Response").first()
    if existing:
        print(f"Test scenario already exists (ID: {existing.id})")
        print("URL: http://localhost:5000/scenarios/play/{0}".format(existing.id))
        exit(0)
    
    # Create the scenario
    scenario = Scenario(
        title=scenario_data['title'],
        description=scenario_data['description'],
        incident_type=scenario_data['incident_type'],
        difficulty_level=scenario_data['difficulty_level'],
        estimated_time=scenario_data['estimated_time'],
        max_points=scenario_data['max_points'],
        scenario_content=json.dumps(scenario_data, indent=2),
        created_by=admin.id
    )
    
    db.session.add(scenario)
    db.session.commit()
    
    print("Test scenario created successfully!")
    print("Scenario ID: {0}".format(scenario.id))
    print("Title: {0}".format(scenario.title))
    print("Max Points: {0}".format(scenario.max_points))
    print("\nPlay URL: http://localhost:5000/scenarios/play/{0}".format(scenario.id))
    print("Detail URL: http://localhost:5000/scenarios/{0}".format(scenario.id))
