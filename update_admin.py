"""
Quick script to update the admin user's role
"""
import sqlite3
import os

db_path = os.path.join('instance', 'dont_panic.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
conn.commit()


cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
result = cursor.fetchone()

if result:
    print(f"✅ Updated: {result[0]} -> role: {result[1]}")
else:
    print("❌ Admin user not found")

conn.close()
