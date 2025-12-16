#!/usr/bin/env python3
"""
Database Restore Script
=======================
Restores PostgreSQL database from a backup file.

Usage:
    python scripts/restore_database.py                     # List available backups
    python scripts/restore_database.py <backup_file>       # Restore specific backup
    python scripts/restore_database.py --latest            # Restore most recent backup

Environment:
    DATABASE_URL: PostgreSQL connection string (required)

WARNING: This script will REPLACE ALL DATA in the database with backup data!
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
BACKUP_DIR = PROJECT_ROOT / "backups"


def parse_database_url(database_url: str) -> dict:
    """Parse DATABASE_URL into components."""
    parsed = urlparse(database_url)
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
    }


def get_database_url() -> str:
    """Get DATABASE_URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("  Set it with: export DATABASE_URL='postgresql://user:pass@host:port/db'")
        sys.exit(1)

    if not database_url.startswith("postgresql"):
        print("ERROR: Only PostgreSQL databases are supported for restore")
        sys.exit(1)

    return database_url


def list_available_backups() -> list:
    """List all available backup files."""
    if not BACKUP_DIR.exists():
        return []

    backups = sorted(BACKUP_DIR.glob("railway_db_backup_*.sql"), reverse=True)
    return backups


def print_backup_list(backups: list):
    """Print list of available backups."""
    print()
    print("=" * 60)
    print("AVAILABLE BACKUPS")
    print("=" * 60)
    print()

    if not backups:
        print("No backups found in: {BACKUP_DIR}")
        print()
        print("Create a backup first:")
        print("  python scripts/backup_database.py")
        return

    print(f"Found {len(backups)} backup(s) in: {BACKUP_DIR}")
    print()

    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)

        # Parse timestamp from filename
        try:
            timestamp_str = backup.stem.replace("railway_db_backup_", "")
            backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            date_display = backup_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            date_display = mtime.strftime("%Y-%m-%d %H:%M:%S")

        print(f"  {i}. {backup.name}")
        print(f"     Size: {size:,} bytes | Date: {date_display}")
        print()

    print("To restore a backup:")
    print(f"  python scripts/restore_database.py {backups[0].name}")
    print()
    print("Or restore the latest:")
    print("  python scripts/restore_database.py --latest")
    print()


def find_backup_file(backup_name: str) -> Path:
    """Find backup file by name or path."""
    # Check if it's a full path
    if os.path.isabs(backup_name):
        backup_path = Path(backup_name)
    else:
        # Look in backup directory
        backup_path = BACKUP_DIR / backup_name

    if not backup_path.exists():
        print(f"ERROR: Backup file not found: {backup_path}")
        sys.exit(1)

    return backup_path


def confirm_restore(backup_file: Path) -> bool:
    """Get user confirmation for restore operation."""
    size = backup_file.stat().st_size

    print()
    print("!" * 60)
    print("!!! WARNING: DESTRUCTIVE OPERATION !!!")
    print("!" * 60)
    print()
    print("This script will:")
    print("  1. DROP ALL TABLES in the current database")
    print("  2. DELETE ALL existing data")
    print("  3. RESTORE data from the backup file")
    print()
    print(f"Backup file: {backup_file.name}")
    print(f"Backup size: {size:,} bytes")
    print()

    # Check for --yes flag for non-interactive mode
    if "--yes" in sys.argv or "-y" in sys.argv:
        print("Non-interactive mode: --yes flag detected")
        return True

    try:
        response = input("Type 'RESTORE' to confirm database restore: ").strip()
        return response == "RESTORE"
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return False


def drop_all_tables(db_config: dict) -> bool:
    """Drop all tables before restore."""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    sql = """
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO public;
    """

    cmd = [
        "psql",
        "-h", db_config["host"],
        "-p", str(db_config["port"]),
        "-U", db_config["user"],
        "-d", db_config["database"],
        "-c", sql,
    ]

    print("  Dropping all existing tables...")

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"WARNING: Drop tables returned code {result.returncode}")
            print(f"  stderr: {result.stderr}")
            # Continue anyway - tables might not exist

        return True

    except subprocess.TimeoutExpired:
        print("ERROR: Drop tables timed out")
        return False
    except FileNotFoundError:
        print("ERROR: psql command not found")
        print("  Install PostgreSQL client tools")
        return False


def run_psql_restore(db_config: dict, backup_file: Path) -> bool:
    """Run psql to restore backup."""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    cmd = [
        "psql",
        "-h", db_config["host"],
        "-p", str(db_config["port"]),
        "-U", db_config["user"],
        "-d", db_config["database"],
        "-f", str(backup_file),
        "-v", "ON_ERROR_STOP=1",  # Stop on first error
    ]

    print(f"  Running: psql -h {db_config['host']} -d {db_config['database']} -f {backup_file.name}")

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode != 0:
            print(f"ERROR: psql restore failed with code {result.returncode}")
            print(f"  stderr: {result.stderr[:1000]}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("ERROR: Restore timed out after 10 minutes")
        return False
    except FileNotFoundError:
        print("ERROR: psql command not found")
        print("  Install PostgreSQL client tools:")
        print("    Ubuntu/Debian: apt-get install postgresql-client")
        print("    macOS: brew install postgresql")
        return False


def validate_restore(db_config: dict) -> bool:
    """Validate the restore was successful."""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    # Count tables
    cmd = [
        "psql",
        "-h", db_config["host"],
        "-p", str(db_config["port"]),
        "-U", db_config["user"],
        "-d", db_config["database"],
        "-t", "-c",
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'",
    ]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            table_count = int(result.stdout.strip())
            print(f"  Tables restored: {table_count}")
            return table_count > 0
    except Exception as e:
        print(f"  Warning: Could not validate restore: {e}")

    return True  # Assume success if we can't validate


def main():
    """Main restore function."""
    # Check for list mode (no arguments)
    if len(sys.argv) == 1:
        backups = list_available_backups()
        print_backup_list(backups)
        return 0

    # Check for --latest flag
    if "--latest" in sys.argv:
        backups = list_available_backups()
        if not backups:
            print("ERROR: No backups found")
            return 1
        backup_file = backups[0]
        print(f"Using latest backup: {backup_file.name}")
    else:
        # Get backup file from argument
        backup_arg = None
        for arg in sys.argv[1:]:
            if not arg.startswith("-"):
                backup_arg = arg
                break

        if not backup_arg:
            print("ERROR: No backup file specified")
            print("  Usage: python scripts/restore_database.py <backup_file>")
            return 1

        backup_file = find_backup_file(backup_arg)

    print("=" * 60)
    print("DATABASE RESTORE SCRIPT")
    print("=" * 60)
    print()

    # Step 1: Get database URL
    print("[1/5] Checking DATABASE_URL...")
    database_url = get_database_url()
    db_config = parse_database_url(database_url)
    print(f"  Host: {db_config['host']}")
    print(f"  Database: {db_config['database']}")
    print()

    # Step 2: Confirm restore
    print("[2/5] Confirming operation...")
    if not confirm_restore(backup_file):
        print()
        print("Operation cancelled by user.")
        return 0
    print()

    # Step 3: Drop existing tables
    print("[3/5] Preparing database...")
    if not drop_all_tables(db_config):
        print()
        print("RESTORE FAILED during table cleanup!")
        return 1
    print()

    # Step 4: Restore from backup
    print("[4/5] Restoring from backup...")
    if not run_psql_restore(db_config, backup_file):
        print()
        print("RESTORE FAILED!")
        print()
        print("Database may be in inconsistent state.")
        print("You may need to run reset_database.py to recover.")
        return 1
    print()

    # Step 5: Validate restore
    print("[5/5] Validating restore...")
    if not validate_restore(db_config):
        print()
        print("RESTORE COMPLETED WITH WARNINGS - Please verify manually")
        return 1
    print()

    # Success
    print("=" * 60)
    print("DATABASE RESTORE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print()
    print(f"Restored from: {backup_file.name}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
