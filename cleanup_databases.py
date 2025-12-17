#!/usr/bin/env python
"""Cleanup old database files - can be run after closing VS Code or file explorer"""

import os
from pathlib import Path

def cleanup_old_databases():
    """Remove old unused database files"""
    
    instance_dir = Path('instance')
    files_to_remove = [
        'scenarios.db',
        'scenarios.db.old',
        'dont_panic.db.bak',
        'dont_panic.db.backup',
        'dont_panic.db'
    ]
    
    print("🧹 Cleaning up old database files...")
    print("=" * 60)
    
    removed_count = 0
    
    for filename in files_to_remove:
        filepath = instance_dir / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except PermissionError:
                print(f"⚠️  Cannot remove {filename} - file is locked")
            except Exception as e:
                print(f"❌ Error removing {filename}: {e}")
        else:
            print(f"⏭️  Skipped: {filename} - not found")
    
    print("=" * 60)
    
    # Show remaining database files
    remaining_dbs = list(instance_dir.glob('*.db*'))
    print(f"\n📊 Remaining database files ({len(remaining_dbs)}):")
    for db_file in remaining_dbs:
        print(f"  - {db_file.name}")
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} file(s).")
    print("\n📝 Important:")
    print("  - users_training.db is the active database (KEEP)")
    print("  - scenarios/ folder contains all scenarios as JSON (KEEP)")
    print("  - Old .db files are ignored by git (.gitignore)")

if __name__ == '__main__':
    cleanup_old_databases()
