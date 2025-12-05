#!/usr/bin/env python3
"""
Database Migration Script for Railway PostgreSQL
================================================
Runs database/migrations/005_fix_missing_columns_UP.sql

This script is idempotent - safe to run multiple times.
All SQL uses IF NOT EXISTS patterns.

Usage:
    python scripts/run_db_migration.py

Environment:
    DATABASE_URL - PostgreSQL connection string (set by Railway)
"""

import os
import sys
from pathlib import Path

def run_migration():
    """Execute the 005_fix_missing_columns migration"""

    print("=" * 60)
    print("Railway PostgreSQL Migration Runner")
    print("=" * 60)

    # Get DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("This script must run on Railway where DATABASE_URL is set")
        return False

    # Fix Railway URL format (postgres:// -> postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'connected'}")

    # Import psycopg2
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary")
        import psycopg2

    # Read migration file
    migration_file = Path(__file__).parent.parent / 'database' / 'migrations' / '005_fix_missing_columns_UP.sql'

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    print(f"Migration file: {migration_file.name}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Connect and execute
    try:
        print("\nConnecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Executing migration 005_fix_missing_columns...")
        cursor.execute(migration_sql)

        print("\n" + "=" * 60)
        print("VERIFICATION: Checking columns exist")
        print("=" * 60)

        # Verify critical columns
        checks = [
            ('users', 'password_hash'),
            ('samples', 'status'),
            ('samples', 'project_id'),
            ('incoming_inspections', 'allocation_triggered'),
        ]

        all_ok = True
        for table, column in checks:
            cursor.execute("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            """, (table, column))

            exists = cursor.fetchone() is not None
            status = "OK" if exists else "MISSING"
            print(f"  {table}.{column}: {status}")

            if not exists:
                all_ok = False

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        if all_ok:
            print("Migration completed successfully!")
        else:
            print("WARNING: Some columns still missing")
        print("=" * 60)

        return all_ok

    except Exception as e:
        print(f"\nERROR: Migration failed!")
        print(f"  {type(e).__name__}: {e}")
        return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
