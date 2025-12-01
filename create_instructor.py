from app import create_app
from models import db, User

app = create_app('development')
with app.app_context():
    # Check if instructor user already exists
    existing = User.query.filter_by(username='instructor').first()
    if existing:
        print("User 'instructor' already exists. Updating password...")
        existing.set_password('instructor123')
    else:
        print("Creating new user 'instructor'...")
        instructor = User(
            username='instructor',
            email='instructor@example.com',
            role='instructor'
        )
        instructor.set_password('instructor123')
        db.session.add(instructor)
    
    db.session.commit()
    print("✅ User 'instructor' with password 'instructor123' is ready to use!")
