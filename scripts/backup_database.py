#!/usr/bin/env python3
"""
Database Backup Script
======================
Creates timestamped PostgreSQL database backups using pg_dump.

Usage:
    python scripts/backup_database.py

Environment:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
BACKUP_DIR = PROJECT_ROOT / "backups"
MAX_BACKUPS = 10  # Keep last N backups


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
        print("ERROR: Only PostgreSQL databases are supported for backup")
        print(f"  Got: {database_url[:30]}...")
        sys.exit(1)

    return database_url


def ensure_backup_dir():
    """Create backup directory if it doesn't exist."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Create .gitignore to prevent committing backups
    gitignore = BACKUP_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Ignore all backup files\n*.sql\n*.sql.gz\n")

    print(f"  Backup directory: {BACKUP_DIR}")


def generate_backup_filename() -> Path:
    """Generate timestamped backup filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return BACKUP_DIR / f"railway_db_backup_{timestamp}.sql"


def run_pg_dump(db_config: dict, backup_file: Path) -> bool:
    """Run pg_dump to create backup."""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    cmd = [
        "pg_dump",
        "-h", db_config["host"],
        "-p", str(db_config["port"]),
        "-U", db_config["user"],
        "-d", db_config["database"],
        "-F", "p",  # Plain SQL format
        "--no-owner",
        "--no-privileges",
        "-f", str(backup_file),
    ]

    print(f"  Running: pg_dump -h {db_config['host']} -d {db_config['database']} ...")

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            print(f"ERROR: pg_dump failed with code {result.returncode}")
            print(f"  stderr: {result.stderr}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("ERROR: pg_dump timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("ERROR: pg_dump command not found")
        print("  Install PostgreSQL client tools:")
        print("    Ubuntu/Debian: apt-get install postgresql-client")
        print("    macOS: brew install postgresql")
        return False


def validate_backup(backup_file: Path) -> bool:
    """Validate the backup file was created successfully."""
    if not backup_file.exists():
        print("ERROR: Backup file was not created")
        return False

    size = backup_file.stat().st_size
    if size < 100:
        print(f"ERROR: Backup file is too small ({size} bytes)")
        return False

    # Check for SQL content
    with open(backup_file, "r") as f:
        header = f.read(500)
        if "PostgreSQL" not in header and "pg_dump" not in header:
            print("WARNING: Backup file may not be valid SQL")

    print(f"  Backup size: {size:,} bytes ({size / 1024:.1f} KB)")
    return True


def cleanup_old_backups():
    """Remove old backups, keeping only MAX_BACKUPS most recent."""
    backups = sorted(BACKUP_DIR.glob("railway_db_backup_*.sql"), reverse=True)

    if len(backups) > MAX_BACKUPS:
        old_backups = backups[MAX_BACKUPS:]
        for old_backup in old_backups:
            print(f"  Removing old backup: {old_backup.name}")
            old_backup.unlink()


def main():
    """Main backup function."""
    print("=" * 60)
    print("DATABASE BACKUP SCRIPT")
    print("=" * 60)
    print()

    # Step 1: Get database URL
    print("[1/5] Checking DATABASE_URL...")
    database_url = get_database_url()
    db_config = parse_database_url(database_url)
    print(f"  Host: {db_config['host']}")
    print(f"  Database: {db_config['database']}")
    print(f"  User: {db_config['user']}")
    print()

    # Step 2: Ensure backup directory exists
    print("[2/5] Preparing backup directory...")
    ensure_backup_dir()
    print()

    # Step 3: Generate backup filename
    print("[3/5] Creating backup...")
    backup_file = generate_backup_filename()
    print(f"  Backup file: {backup_file.name}")

    # Step 4: Run pg_dump
    if not run_pg_dump(db_config, backup_file):
        print()
        print("BACKUP FAILED!")
        sys.exit(1)
    print()

    # Step 5: Validate backup
    print("[4/5] Validating backup...")
    if not validate_backup(backup_file):
        print()
        print("BACKUP VALIDATION FAILED!")
        sys.exit(1)
    print()

    # Step 6: Cleanup old backups
    print("[5/5] Cleaning up old backups...")
    cleanup_old_backups()
    print()

    # Success
    print("=" * 60)
    print("BACKUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"  File: {backup_file}")
    print(f"  Size: {backup_file.stat().st_size:,} bytes")
    print()
    print("To restore this backup, run:")
    print(f"  python scripts/restore_database.py {backup_file.name}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
