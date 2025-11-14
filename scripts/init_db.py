#!/usr/bin/env python3
"""Initialize the test protocols database."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.db import DatabaseManager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Initialize database with schema."""
    logger.info("Initializing database...")

    # Create database manager
    db_manager = DatabaseManager()

    # Initialize schema
    schema_file = Path(__file__).parent.parent / 'data' / 'db' / 'schema.sql'

    if not schema_file.exists():
        logger.error(f"Schema file not found: {schema_file}")
        sys.exit(1)

    try:
        db_manager.init_database(str(schema_file))
        logger.info("Database initialized successfully!")

        # Load example protocol
        logger.info("Loading example protocol...")
        example_protocol = Path(__file__).parent.parent / 'schemas' / 'examples' / 'track_001_example.json'

        if example_protocol.exists():
            import json
            with open(example_protocol, 'r') as f:
                protocol_data = json.load(f)

            db_manager.insert_protocol(protocol_data)
            logger.info(f"Loaded protocol: {protocol_data['protocol_id']}")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
