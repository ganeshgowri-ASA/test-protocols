#!/usr/bin/env python3
"""
Database initialization script for PV Testing Protocol Framework
Creates database and initializes schema
"""

import sqlite3
import argparse
from pathlib import Path


def init_sqlite_database(db_path: str, schema_path: str) -> None:
    """
    Initialize SQLite database with schema

    Args:
        db_path: Path to SQLite database file
        schema_path: Path to SQL schema file
    """
    print(f"Initializing SQLite database: {db_path}")

    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read schema file
    print(f"Loading schema from: {schema_path}")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Execute schema (split by semicolon for multiple statements)
    statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

    for i, statement in enumerate(statements, 1):
        # Skip CREATE OR REPLACE VIEW for SQLite (not supported)
        if 'CREATE OR REPLACE VIEW' in statement:
            statement = statement.replace('CREATE OR REPLACE VIEW', 'CREATE VIEW IF NOT EXISTS')

        # Skip SERIAL for SQLite (use INTEGER PRIMARY KEY AUTOINCREMENT)
        statement = statement.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')

        # Skip STDDEV for SQLite (not supported in basic SQLite)
        if 'STDDEV(' in statement:
            print(f"Skipping statement {i} (contains STDDEV - not supported in SQLite)")
            continue

        try:
            cursor.execute(statement)
            print(f"Executed statement {i}")
        except sqlite3.Error as e:
            print(f"Warning: Error executing statement {i}: {e}")
            print(f"Statement: {statement[:100]}...")

    conn.commit()
    conn.close()

    print(f"Database initialized successfully: {db_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize PV Testing Protocol Database')
    parser.add_argument(
        '--db-path',
        default='test_protocols.db',
        help='Path to database file (default: test_protocols.db)'
    )
    parser.add_argument(
        '--schema',
        default='db/schemas/hail_001_schema.sql',
        help='Path to schema file (default: db/schemas/hail_001_schema.sql)'
    )

    args = parser.parse_args()

    # Check if schema file exists
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        return 1

    # Initialize database
    init_sqlite_database(args.db_path, str(schema_path))

    print("\nDatabase initialization complete!")
    print(f"\nTo use the database:")
    print(f"  python -c 'from src.analysis.database import TestDatabase; db = TestDatabase(\"{args.db_path}\"); print(db.list_sessions())'")

    return 0


if __name__ == '__main__':
    exit(main())
