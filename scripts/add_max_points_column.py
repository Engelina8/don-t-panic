#!/usr/bin/env python3
"""
One-off script to add the `max_points` column to the `scenarios` table
for an existing SQLite database at `instance/dont_panic.db`.

Usage (PowerShell):
  cd <repo-root>
  python .\scripts\add_max_points_column.py

This script will:
- Back up the DB to `instance/dont_panic.db.bak` (only if not already present)
- Check if `max_points` exists; if not:
  - ALTER TABLE ADD COLUMN max_points INTEGER
  - UPDATE existing rows to set max_points = 100 where NULL

It is safe to run multiple times.
"""

import os
import shutil
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, 'instance', 'dont_panic.db')
BACKUP_PATH = DB_PATH + '.bak'

if not os.path.exists(DB_PATH):
    print(f"ERROR: Database not found at {DB_PATH}")
    sys.exit(1)

# Backup DB if backup doesn't exist
if not os.path.exists(BACKUP_PATH):
    try:
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    except Exception as e:
        print(f"Failed to create backup: {e}")
        sys.exit(1)
else:
    print(f"Backup already exists at {BACKUP_PATH}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check if column exists
cur.execute("PRAGMA table_info('scenarios')")
cols_info = cur.fetchall()
cols = [c[1] for c in cols_info]

if 'max_points' in cols:
    print("Column 'max_points' already exists. No action needed.")
    conn.close()
    sys.exit(0)

# Add column
try:
    cur.execute("ALTER TABLE scenarios ADD COLUMN max_points INTEGER")
    conn.commit()
    print("Added column 'max_points' to scenarios table.")
except sqlite3.OperationalError as e:
    print(f"ALTER TABLE failed: {e}")
    conn.close()
    sys.exit(1)

# Set default for existing rows where NULL
try:
    cur.execute("UPDATE scenarios SET max_points = 100 WHERE max_points IS NULL")
    conn.commit()
    print("Updated existing scenario rows with max_points = 100 where NULL.")
except Exception as e:
    print(f"Failed to update existing rows: {e}")
    conn.rollback()
    conn.close()
    sys.exit(1)

conn.close()
print("Migration completed successfully.")
