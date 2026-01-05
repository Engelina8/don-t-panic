
"""Detailed database analysis"""

import sqlite3
from pathlib import Path

def analyze_database(db_path):
    """Analyze and display database structure and contents"""

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()


    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print('=' * 80)
    print(f'📊 DATABASE: {db_path.name}')
    print('=' * 80)
    print()

    for table_name in tables:
        table = table_name[0]
        print(f'📋 TABLE: {table.upper()}')
        print('-' * 80)


        cursor.execute(f'PRAGMA table_info({table})')
        columns = cursor.fetchall()

        print('Columns:')
        for col in columns:
            col_id, col_name, col_type, notnull, default, pk = col
            pk_marker = ' [PRIMARY KEY]' if pk else ''
            notnull_marker = ' [NOT NULL]' if notnull else ''
            print(f'  • {col_name:<25} ({col_type}){pk_marker}{notnull_marker}')


        cursor.execute(f'SELECT COUNT(*) FROM [{table}]')
        count = cursor.fetchone()[0]
        print(f'\nRecords: {count}')


        if count > 0:
            cursor.execute(f'SELECT * FROM [{table}] LIMIT 3')
            rows = cursor.fetchall()
            if rows:
                print('\nSample data:')
                for i, row in enumerate(rows, 1):
                    print(f'  Row {i}: {row}')

        print()

    conn.close()


db_path = Path('instance/users_training.db')
if db_path.exists():
    analyze_database(db_path)
else:
    print(f"❌ Database not found: {db_path}")
