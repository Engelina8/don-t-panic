from app import create_app
from models import User, Scenario, TrainingSession
from scenario_manager import scenario_manager

def check_database():
    """Check database contents"""
    app = create_app('development')

    with app.app_context():
        print("\n" + "="*60)
        print("📊 DATABASE STATUS")
        print("="*60)

        users = User.query.all()
        print(f"\n👥 USERS ({len(users)} total):")
        for user in users:
            print(f"   - {user.username} ({user.role}) - {user.email}")

        scenarios_data = scenario_manager.get_all_scenarios()
        print(f"\n📖 SCENARIOS ({len(scenarios_data)} total):")
        for scenario_data in scenarios_data:
            scenario = Scenario(scenario_data)
            print(f"   - {scenario.title}")
            print(f"     Type: {scenario.incident_type} | Level: {scenario.difficulty_level}")
            print(f"     Played: {scenario_data.get('times_played', 0)} times")

        sessions = TrainingSession.query.all()
        print(f"\n🎮 TRAINING SESSIONS ({len(sessions)} total):")
        for session in sessions:
            user = User.query.get(session.user_id)
            scenario_data = scenario_manager.get_scenario(str(session.scenario_id))
            scenario_title = scenario_data.get('title', 'Unknown') if scenario_data else 'Unknown'
            print(f"   - {user.username} played '{scenario_title}'")
            print(f"     Score: {session.score} | Status: {session.status}")

        print("\n" + "="*60)
        print("✅ Database check complete!")
        print("="*60 + "\n")

if __name__ == '__main__':
    check_database()
