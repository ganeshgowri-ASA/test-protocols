"""
Initial Database Migration for UV-001 Protocol
Version: 001
Date: 2025-11-14
Description: Creates all tables for UV preconditioning protocol tracking
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from database.models import (
    Base,
    create_database_engine,
    create_all_tables
)


def upgrade(connection_string: str):
    """
    Apply migration - create all tables

    Args:
        connection_string: Database connection string
                          Example: 'sqlite:///uv001_test_data.db'
                          Example: 'mysql+pymysql://user:password@localhost/uv001_db'
    """
    print("=" * 80)
    print("UV-001 Protocol Database Migration - Initial Setup")
    print("=" * 80)

    # Create engine
    print(f"\nConnecting to database: {connection_string}")
    engine = create_database_engine(connection_string)

    # Create tables
    print("\nCreating tables...")
    create_all_tables(engine)

    print("\nTables created successfully:")
    print("  - uv001_test_sessions")
    print("  - uv001_irradiance_measurements")
    print("  - uv001_environmental_measurements")
    print("  - uv001_spectral_measurements")
    print("  - uv001_electrical_characterization")
    print("  - uv001_visual_inspections")
    print("  - uv001_test_events")
    print("  - uv001_test_results")
    print("  - uv001_equipment_usage")
    print("  - uv001_data_quality")

    print("\n" + "=" * 80)
    print("Migration completed successfully!")
    print("=" * 80)

    return engine


def downgrade(connection_string: str):
    """
    Rollback migration - drop all tables

    Args:
        connection_string: Database connection string
    """
    print("=" * 80)
    print("UV-001 Protocol Database Migration - Rollback")
    print("=" * 80)

    # Create engine
    print(f"\nConnecting to database: {connection_string}")
    engine = create_database_engine(connection_string)

    # Drop tables
    print("\nDropping all tables...")
    Base.metadata.drop_all(engine)

    print("\nTables dropped successfully!")
    print("=" * 80)

    return engine


if __name__ == '__main__':
    """
    Command-line execution

    Usage:
        python 001_initial_setup.py upgrade <connection_string>
        python 001_initial_setup.py downgrade <connection_string>

    Example:
        python 001_initial_setup.py upgrade sqlite:///uv001_test_data.db
    """
    import argparse

    parser = argparse.ArgumentParser(description='UV-001 Database Migration')
    parser.add_argument(
        'action',
        choices=['upgrade', 'downgrade'],
        help='Migration action (upgrade or downgrade)'
    )
    parser.add_argument(
        'connection_string',
        help='Database connection string'
    )

    args = parser.parse_args()

    if args.action == 'upgrade':
        upgrade(args.connection_string)
    else:
        # Confirm before downgrade
        confirm = input("WARNING: This will drop all UV-001 tables. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            downgrade(args.connection_string)
        else:
            print("Downgrade cancelled.")
