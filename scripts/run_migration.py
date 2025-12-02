#!/usr/bin/env python3
"""
One-time migration script to run Phase 1 database migration.
Run this script once to create equipment_phase1 and calibration_records_phase1 tables.

Usage:
    python scripts/run_migration.py
"""

import os
import psycopg2
from pathlib import Path

def run_migration():
    """Execute the Phase 1 UP migration."""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    # Read migration SQL file
    migration_file = Path(__file__).parent.parent / 'docs' / 'migrations' / '001_equipment_management_UP.sql'
    
    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Connect and execute
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Executing Phase 1 UP migration...")
        cursor.execute(migration_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("Created tables: equipment_phase1, calibration_records_phase1")
        print("Created views: equipment_calibration_status")
        print("Inserted seed data for 8 equipment items")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
