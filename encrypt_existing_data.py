#!/usr/bin/env python
"""
Migration script to encrypt existing username and email fields
Run this ONCE after updating models.py to encrypt existing user data
"""
import os
import sys
from app import app, db
from models import User, encrypt_field

def encrypt_existing_data():
    """Encrypt username and email for all existing users"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"Found {len(users)} users. Starting encryption...")
        
        for user in users:
            try:
                if user._username and not user._username.startswith('gAAAAAB'):
                    original_username = user._username
                    user._username = encrypt_field(user._username)
                    print(f"  Encrypted username for user ID {user.id}")
                
                if user._email and not user._email.startswith('gAAAAAB'):
                    original_email = user._email
                    user._email = encrypt_field(user._email)
                    print(f"  Encrypted email for user ID {user.id}")
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"  ERROR encrypting user ID {user.id}: {e}")
                return False
        
        print("\nEncryption complete! All usernames and emails are now encrypted.")
        return True

if __name__ == '__main__':
    print("Starting encryption migration...")
    print("-" * 50)
    success = encrypt_existing_data()
    if not success:
        sys.exit(1)
