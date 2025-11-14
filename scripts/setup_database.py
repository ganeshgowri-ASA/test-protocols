#!/usr/bin/env python3
"""
Database Setup Script
=====================

Sets up the PostgreSQL database for the Test Protocols Framework.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_sql_file(file_path: Path, db_name: str = "postgres"):
    """Run a SQL file using psql"""
    print(f"Running {file_path.name}...")
    try:
        result = subprocess.run(
            ["psql", "-U", "postgres", "-d", db_name, "-f", str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {file_path.name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {file_path.name}")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ psql command not found. Please install PostgreSQL client.")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("Test Protocols Framework - Database Setup")
    print("=" * 60)

    # Get project root
    project_root = Path(__file__).parent.parent
    migrations_dir = project_root / "database" / "migrations"

    # Check if migrations directory exists
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        return 1

    print("\nThis script will:")
    print("1. Create database 'test_protocols'")
    print("2. Run initial schema migration")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        return 1

    # Create database
    print("\n📦 Creating database...")
    try:
        subprocess.run(
            ["psql", "-U", "postgres", "-c", "CREATE DATABASE test_protocols;"],
            capture_output=True,
            check=False  # Don't fail if database already exists
        )
        print("✅ Database created (or already exists)")
    except Exception as e:
        print(f"⚠️  Warning: {e}")

    # Run migration
    migration_file = migrations_dir / "001_initial_schema.sql"
    if migration_file.exists():
        success = run_sql_file(migration_file, "test_protocols")
        if not success:
            print("\n❌ Migration failed!")
            return 1
    else:
        print(f"❌ Migration file not found: {migration_file}")
        return 1

    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Configure database connection in config/app_config.yaml")
    print("2. Set database password in .env file")
    print("3. Run the application: streamlit run ui/app.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
