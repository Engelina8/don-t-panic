from app import create_app
from models import User

app = create_app('development')
with app.app_context():
    users = User.query.all()
    print("All users in database:")
    for user in users:
        print(f'  Username: {user.username}, Email: {user.email}, Role: {user.role}')
    
    # Check specifically for instructor
    instructor = User.query.filter_by(username='instructor').first()
    if instructor:
        print(f'\nInstructor user found: {instructor.username}')
    else:
        print('\nNo user with username "instructor" found')
