#!/usr/bin/env python3
"""
Migration Runner: 005_fix_missing_columns
==========================================
Run this script to add missing columns to Railway PostgreSQL.

Usage:
    # Set DATABASE_URL and run
    DATABASE_URL=postgres://... python run_migration_005.py

    # Or on Railway, it will use the environment variable automatically
    python run_migration_005.py
"""

import os
import sys

def run_migration():
    """Execute migration 005 to fix missing columns"""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Set it with: export DATABASE_URL=postgres://...")
        sys.exit(1)

    # Check if this is PostgreSQL
    if not database_url.startswith(("postgres://", "postgresql://")):
        print(f"WARNING: This migration is designed for PostgreSQL")
        print(f"Current DATABASE_URL starts with: {database_url[:20]}...")

    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        os.system("pip install psycopg2-binary")
        import psycopg2

    # Read migration SQL
    migration_path = "database/migrations/005_fix_missing_columns_UP.sql"

    if not os.path.exists(migration_path):
        print(f"ERROR: Migration file not found: {migration_path}")
        sys.exit(1)

    with open(migration_path, 'r') as f:
        migration_sql = f.read()

    print("=" * 60)
    print("Migration 005: Fix Missing Columns for Railway PostgreSQL")
    print("=" * 60)

    # Connect and execute
    try:
        # Fix Railway URL format if needed (postgres:// -> postgresql://)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("\nConnected to database successfully!")
        print("\nExecuting migration...")

        # Execute the migration
        cursor.execute(migration_sql)

        print("\n✅ Migration completed successfully!")

        # Verify the columns were added
        print("\n" + "=" * 60)
        print("Verification: Checking added columns...")
        print("=" * 60)

        verification_query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name IN ('users', 'samples', 'incoming_inspections')
        AND column_name IN ('password_hash', 'status', 'project_id', 'allocation_triggered', 'sample_id')
        ORDER BY table_name, column_name;
        """

        cursor.execute(verification_query)
        results = cursor.fetchall()

        if results:
            print("\nColumns verified:")
            for row in results:
                print(f"  ✓ {row[0]}.{row[1]} ({row[2]})")
        else:
            print("\nWARNING: No columns found in verification query")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("Migration 005 completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: Migration failed!")
        print(f"   {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
