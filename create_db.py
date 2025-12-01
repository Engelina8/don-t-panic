from app import create_app
from models import db, User, Scenario, TrainingSession
import json

def create_sample_data():
    """Create some sample data for testing"""
    app = create_app('development')
    
    with app.app_context():
        # Clear existing data (be careful with this!)
        db.drop_all()
        db.create_all()
        
        print("🗄️  Creating database tables...")
        
        # Create instructor
        instructor = User(
            username='instructor1',
            email='instructor@dontpanic.com',
            role='instructor'
        )
        instructor.set_password('password123')
        db.session.add(instructor)
        
        # Create trainees
        trainee1 = User(
            username='tom',
            email='tom@student.com',
            role='trainee'
        )
        trainee1.set_password('password123')
        
        trainee2 = User(
            username='joshua',
            email='joshua@student.com',
            role='trainee'
        )
        trainee2.set_password('password123')
        
        db.session.add_all([trainee1, trainee2])
        db.session.commit()
        
        print("✅ Users created!")
        
        # Create sample scenario
        scenario_content = {
            "intro": "Your company's systems have been encrypted by ransomware...",
            "stages": [
                {
                    "stage": "detection",
                    "question": "What is your first action?",
                    "options": [
                        {"text": "Disconnect from network", "points": 20},
                        {"text": "Pay the ransom immediately", "points": -10},
                        {"text": "Ignore it", "points": 0}
                    ]
                }
            ]
        }
        
        scenario = Scenario(
            title='Ransomware Attack Response',
            description='Handle a critical ransomware incident affecting your infrastructure',
            incident_type='ransomware',
            difficulty_level=3,
            estimated_time=30,
            scenario_content=json.dumps(scenario_content),
            created_by=instructor.id
        )
        db.session.add(scenario)
        db.session.commit()
        
        print("✅ Sample scenario created!")
        
        # Create a sample completed session
        session = TrainingSession(
            user_id=trainee1.id,
            scenario_id=scenario.id,
            status='completed',
            score=85,
            outcome='success',
            detection_score=90,
            containment_score=80,
            eradication_score=85,
            recovery_score=85,
            communication_score=80
        )
        session.complete_session(85, 'success')
        
        db.session.add(session)
        db.session.commit()
        
        print("✅ Sample training session created!")
        print("\n" + "="*50)
        print("🎉 Database created successfully!")
        print("="*50)
        print("\n📊 Database Summary:")
        print(f"   Users: {User.query.count()}")
        print(f"   Scenarios: {Scenario.query.count()}")
        print(f"   Training Sessions: {TrainingSession.query.count()}")
        print("\n🔐 Test Credentials:")
        print("   Instructor: instructor1 / password123")
        print("   Trainee 1: tom / password123")
        print("   Trainee 2: joshua / password123")
        print("="*50)

if __name__ == '__main__':
    create_sample_data()
