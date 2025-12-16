#!/usr/bin/env python3
"""
Database Reset Script
=====================
Drops all tables and recreates the database schema from models.
Includes safety confirmations and backup recommendations.

Usage:
    python scripts/reset_database.py

Environment:
    DATABASE_URL: PostgreSQL connection string (required)

WARNING: This script will DELETE ALL DATA in the database!
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_database_url() -> str:
    """Get DATABASE_URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("  Set it with: export DATABASE_URL='postgresql://user:pass@host:port/db'")
        sys.exit(1)
    return database_url


def confirm_reset() -> bool:
    """Get user confirmation for destructive operation."""
    print()
    print("!" * 60)
    print("!!! WARNING: DESTRUCTIVE OPERATION !!!")
    print("!" * 60)
    print()
    print("This script will:")
    print("  1. DROP ALL TABLES in the database")
    print("  2. Delete ALL existing data")
    print("  3. Recreate all tables from models")
    print("  4. Seed 54 test protocols")
    print()
    print("RECOMMENDATION: Run backup first!")
    print("  python scripts/backup_database.py")
    print()

    # Check for --yes flag for non-interactive mode
    if "--yes" in sys.argv or "-y" in sys.argv:
        print("Non-interactive mode: --yes flag detected")
        return True

    try:
        response = input("Type 'RESET' to confirm database reset: ").strip()
        return response == "RESET"
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        return False


def drop_all_tables(engine):
    """Drop all tables using DROP SCHEMA CASCADE."""
    from sqlalchemy import text

    print("  Dropping all tables...")

    with engine.connect() as conn:
        # Disable foreign key checks temporarily
        conn.execute(text("SET session_replication_role = 'replica';"))

        # Drop and recreate public schema
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))

        # Restore default permissions
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))

        # Re-enable foreign key checks
        conn.execute(text("SET session_replication_role = 'origin';"))

        conn.commit()

    print("  All tables dropped successfully")


def create_all_tables(engine, Base):
    """Create all tables from SQLAlchemy models."""
    from sqlalchemy.orm import configure_mappers

    print("  Configuring ORM mappers...")
    try:
        configure_mappers()
    except Exception as e:
        print(f"  Warning: Mapper configuration issue: {e}")

    print("  Creating all tables from models...")
    Base.metadata.create_all(bind=engine)
    print("  Tables created successfully")


def get_table_count(engine) -> int:
    """Get count of tables in database."""
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
        ))
        return result.scalar()


def list_tables(engine) -> list:
    """List all tables in database."""
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
            "ORDER BY table_name"
        ))
        return [row[0] for row in result.fetchall()]


def seed_protocols(db_session) -> int:
    """Seed the 54 test protocols."""
    from database.seed_data import seed_test_protocols

    print("  Seeding 54 test protocols...")
    count = seed_test_protocols(db_session)
    print(f"  Seeded {count} protocols")
    return count


def validate_reset(engine, db_session) -> bool:
    """Validate the reset was successful."""
    from database import TestProtocol

    print("  Validating reset...")

    # Check tables exist
    tables = list_tables(engine)
    if len(tables) < 10:
        print(f"  ERROR: Only {len(tables)} tables created, expected more")
        return False

    # Check protocols were seeded
    protocol_count = db_session.query(TestProtocol).count()
    if protocol_count != 54:
        print(f"  ERROR: {protocol_count} protocols found, expected 54")
        return False

    print(f"  Validation passed: {len(tables)} tables, {protocol_count} protocols")
    return True


def print_summary(engine):
    """Print summary of created tables."""
    tables = list_tables(engine)

    print()
    print("=" * 60)
    print("DATABASE RESET SUMMARY")
    print("=" * 60)
    print()
    print(f"Total tables created: {len(tables)}")
    print()
    print("Tables:")
    for i, table in enumerate(tables, 1):
        print(f"  {i:2}. {table}")
    print()


def main():
    """Main reset function."""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print()

    # Step 1: Get database URL
    print("[1/6] Checking DATABASE_URL...")
    database_url = get_database_url()

    # Mask password for display
    if "@" in database_url:
        display_url = database_url.split("@")[1]
    else:
        display_url = database_url[:50]
    print(f"  Database: {display_url}")
    print()

    # Step 2: Confirm reset
    print("[2/6] Confirming operation...")
    if not confirm_reset():
        print()
        print("Operation cancelled by user.")
        sys.exit(0)
    print()

    # Step 3: Initialize database connection
    print("[3/6] Connecting to database...")
    try:
        from config.database import get_engine, get_session_local, Base

        # Import all models to register them with Base
        from database.models import (
            User, ServiceRequest, IncomingInspection, Equipment,
            EquipmentBooking, TestProtocol, TestExecution, TestData,
            AuditLog, QRCode, CompanyProfile, Sample, SampleReceipt,
            SampleStatusHistory, RouteCard, SampleTestAssignment,
            SampleInventory, SampleAllocation, StorageLocation,
            StaffTraining, StaffTrainingRecord, Document, DocumentAccessLog,
            BOMItem, BOMProtocolRequirement, BOMUsageLog, QRScanLog,
            CalibrationRecord, AnalysisResult, DataExport, ReportTemplate,
            GeneratedReport
        )

        engine = get_engine()
        print("  Connected successfully")
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)
    print()

    # Step 4: Drop all tables
    print("[4/6] Dropping all tables...")
    try:
        drop_all_tables(engine)
    except Exception as e:
        print(f"ERROR: Failed to drop tables: {e}")
        print()
        print("RESET FAILED - Database may be in inconsistent state!")
        sys.exit(1)
    print()

    # Step 5: Create all tables
    print("[5/6] Creating tables from models...")
    try:
        create_all_tables(engine, Base)
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        print()
        print("RESET FAILED - Database may be in inconsistent state!")
        sys.exit(1)
    print()

    # Step 6: Seed protocols
    print("[6/6] Seeding data...")
    try:
        SessionLocal = get_session_local()
        db_session = SessionLocal()

        seed_protocols(db_session)
        db_session.commit()

        # Validate
        if not validate_reset(engine, db_session):
            print()
            print("RESET COMPLETED WITH WARNINGS - Please verify manually")
            db_session.close()
            sys.exit(1)

        db_session.close()
    except Exception as e:
        print(f"ERROR: Failed to seed data: {e}")
        print()
        print("RESET PARTIALLY FAILED - Tables created but seeding failed")
        sys.exit(1)

    # Print summary
    print_summary(engine)

    print("=" * 60)
    print("DATABASE RESET COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print()
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
