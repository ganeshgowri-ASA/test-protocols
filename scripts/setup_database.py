#!/usr/bin/env python3
"""
Database setup script.

This script initializes the database schema for the test protocol framework.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from test_protocols.database.models import Base


def setup_database(connection_string: str = None):
    """
    Set up database schema.

    Args:
        connection_string: Database connection string. If None, reads from DATABASE_URL env var.
    """
    if connection_string is None:
        connection_string = os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/test_protocols"
        )

    print(f"Connecting to database...")
    engine = create_engine(connection_string, echo=True)

    print("Creating database schema...")
    Base.metadata.create_all(engine)

    print("Database setup complete!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Set up test protocol database")
    parser.add_argument(
        "--connection-string",
        type=str,
        help="Database connection string (default: from DATABASE_URL env var)"
    )

    args = parser.parse_args()

    try:
        setup_database(args.connection_string)
    except Exception as e:
        print(f"Error setting up database: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
