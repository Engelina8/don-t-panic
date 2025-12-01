from app import create_app
from models import db, User, Scenario, TrainingSession

def check_database():
    """Check database contents"""
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "="*60)
        print("📊 DATABASE STATUS")
        print("="*60)
        
        # Check users
        users = User.query.all()
        print(f"\n👥 USERS ({len(users)} total):")
        for user in users:
            print(f"   - {user.username} ({user.role}) - {user.email}")
        
        # Check scenarios
        scenarios = Scenario.query.all()
        print(f"\n📖 SCENARIOS ({len(scenarios)} total):")
        for scenario in scenarios:
            print(f"   - {scenario.title}")
            print(f"     Type: {scenario.incident_type} | Level: {scenario.difficulty_level}")
            print(f"     Played: {scenario.times_played} times")
        
        # Check sessions
        sessions = TrainingSession.query.all()
        print(f"\n🎮 TRAINING SESSIONS ({len(sessions)} total):")
        for session in sessions:
            user = User.query.get(session.user_id)
            scenario = Scenario.query.get(session.scenario_id)
            print(f"   - {user.username} played '{scenario.title}'")
            print(f"     Score: {session.score} | Status: {session.status}")
        
        print("\n" + "="*60)
        print("✅ Database check complete!")
        print("="*60 + "\n")

if __name__ == '__main__':
    check_database()
