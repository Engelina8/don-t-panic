"""
Database Migration Script
Add admin role support and groups table to existing database
"""

import sqlite3
import os

def migrate_database():
    """Run database migrations directly on SQLite"""
    db_path = os.path.join('instance', 'dont_panic.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Run the app first to create the database")
        return
    
    print("🔧 Starting database migration...")
    print(f"📁 Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if groups table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
        groups_exists = cursor.fetchone() is not None
        
        if not groups_exists:
            print("📦 Creating groups table...")
            cursor.execute("""
                CREATE TABLE groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            print("✅ Groups table created")
        else:
            print("✅ Groups table already exists")
        
        # Check if group_id column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'group_id' not in columns:
            print("📦 Adding group_id column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN group_id INTEGER")
            print("✅ group_id column added")
        else:
            print("✅ group_id column already exists")
        
        # Update default admin user to admin role
        cursor.execute("SELECT id, role FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            admin_id, admin_role = admin
            if admin_role != 'admin':
                print("📦 Updating default admin user to admin role...")
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                print("✅ Default admin user updated to admin role")
            else:
                print("✅ Admin user already has admin role")
        else:
            print("⚠️ No default admin user found")
        
        conn.commit()
        print("\n🎯 Database migration complete!")
        print("\n📝 Next steps:")
        print("1. Restart your Flask application")
        print("2. Login as admin (username: admin, password: admin123)")
        print("3. Create groups from the Groups menu in navigation")
        print("4. Assign users to groups from the group detail page")
        print("5. Only admins can access group management")
        
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
