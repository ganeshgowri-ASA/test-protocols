#!/usr/bin/env python3
"""
Database Migration Runner for Railway PostgreSQL
=================================================
Automatically runs pending database migrations on deployment.

Features:
- Idempotent: Safe to run multiple times (uses IF NOT EXISTS)
- Tracks migration state in database
- Supports all migrations in database/migrations/
- Logs all operations for debugging

Usage:
    python scripts/run_migration.py              # Run all pending migrations
    python scripts/run_migration.py --check      # Check migration status only
    python scripts/run_migration.py --migration 005  # Run specific migration

Environment:
    DATABASE_URL - PostgreSQL connection string (set by Railway)
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / 'database' / 'migrations'


def get_database_url():
    """Get database URL from environment, handling Railway format"""
    url = os.getenv('DATABASE_URL')
    if not url:
        logger.error("DATABASE_URL environment variable not set")
        return None

    # Railway uses postgres:// but psycopg2 needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)

    return url


def connect_database(database_url):
    """Connect to PostgreSQL database"""
    try:
        import psycopg2
    except ImportError:
        logger.info("Installing psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary")
        import psycopg2

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        logger.info("Connected to database successfully")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None


def ensure_migration_table(conn):
    """Create migration tracking table if not exists"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(100) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT
        )
    """)
    conn.commit()
    cursor.close()
    logger.info("Migration tracking table ready")


def get_applied_migrations(conn):
    """Get list of already applied migrations"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT migration_name FROM _migrations
        WHERE status = 'success'
        ORDER BY migration_name
    """)
    applied = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return applied


def get_pending_migrations():
    """Get list of pending UP migration files"""
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return []

    migrations = []
    for f in sorted(MIGRATIONS_DIR.glob('*_UP.sql')):
        # Extract migration number (e.g., "005" from "005_fix_missing_columns_UP.sql")
        name = f.stem.replace('_UP', '')
        migrations.append({
            'name': name,
            'file': f,
            'number': name.split('_')[0]
        })

    return migrations


def run_migration(conn, migration):
    """Execute a single migration file"""
    migration_name = migration['name']
    migration_file = migration['file']

    logger.info(f"Running migration: {migration_name}")

    try:
        # Read SQL file
        with open(migration_file, 'r') as f:
            sql = f.read()

        cursor = conn.cursor()

        # Execute migration
        cursor.execute(sql)

        # Record successful migration
        cursor.execute("""
            INSERT INTO _migrations (migration_name, status)
            VALUES (%s, 'success')
            ON CONFLICT (migration_name) DO UPDATE SET
                applied_at = CURRENT_TIMESTAMP,
                status = 'success',
                error_message = NULL
        """, (migration_name,))

        conn.commit()
        cursor.close()

        logger.info(f"Migration {migration_name} completed successfully")
        return True

    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        logger.error(f"Migration {migration_name} failed: {error_msg}")

        # Record failed migration
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO _migrations (migration_name, status, error_message)
                VALUES (%s, 'failed', %s)
                ON CONFLICT (migration_name) DO UPDATE SET
                    applied_at = CURRENT_TIMESTAMP,
                    status = 'failed',
                    error_message = %s
            """, (migration_name, error_msg, error_msg))
            conn.commit()
            cursor.close()
        except:
            pass

        return False


def run_all_migrations(check_only=False, specific_migration=None):
    """Run all pending migrations"""
    print("=" * 60)
    print("Database Migration Runner")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Get database URL
    database_url = get_database_url()
    if not database_url:
        return False

    # Connect to database
    conn = connect_database(database_url)
    if not conn:
        return False

    try:
        # Ensure migration tracking table exists
        ensure_migration_table(conn)

        # Get applied and pending migrations
        applied = get_applied_migrations(conn)
        pending = get_pending_migrations()

        logger.info(f"Applied migrations: {len(applied)}")
        logger.info(f"Available migrations: {len(pending)}")

        # Filter to only pending migrations
        to_run = [m for m in pending if m['name'] not in applied]

        # Filter to specific migration if requested
        if specific_migration:
            to_run = [m for m in to_run if specific_migration in m['name']]

        if not to_run:
            logger.info("No pending migrations to run")
            print("\n All migrations are up to date!")
            return True

        logger.info(f"Pending migrations to run: {[m['name'] for m in to_run]}")

        if check_only:
            print(f"\n{len(to_run)} pending migration(s):")
            for m in to_run:
                print(f"  - {m['name']}")
            return True

        # Run each pending migration
        success_count = 0
        fail_count = 0

        for migration in to_run:
            if run_migration(conn, migration):
                success_count += 1
            else:
                fail_count += 1
                # Stop on first failure
                logger.error("Stopping due to migration failure")
                break

        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")

        return fail_count == 0

    finally:
        conn.close()
        logger.info("Database connection closed")


def verify_columns(conn):
    """Verify critical columns exist after migration"""
    cursor = conn.cursor()

    checks = [
        ("users", "password_hash"),
        ("samples", "status"),
        ("samples", "project_id"),
        ("incoming_inspections", "allocation_triggered"),
    ]

    print("\nColumn Verification:")
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
    return all_ok


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('--check', action='store_true', help='Check pending migrations only')
    parser.add_argument('--migration', type=str, help='Run specific migration (e.g., 005)')
    parser.add_argument('--verify', action='store_true', help='Verify columns after migration')

    args = parser.parse_args()

    success = run_all_migrations(
        check_only=args.check,
        specific_migration=args.migration
    )

    if args.verify and success:
        database_url = get_database_url()
        if database_url:
            conn = connect_database(database_url)
            if conn:
                verify_columns(conn)
                conn.close()

    sys.exit(0 if success else 1)
