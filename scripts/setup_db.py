#!/usr/bin/env python3
"""Database initialization script."""

import json
from pathlib import Path

from test_protocols.database.connection import db
from test_protocols.logger import setup_logger
from test_protocols.models.schema import Protocol

logger = setup_logger(__name__)


def load_protocol_template(template_path: Path) -> dict:
    """Load protocol template from JSON file.

    Args:
        template_path: Path to protocol template JSON file

    Returns:
        dict: Protocol template data
    """
    with open(template_path, "r") as f:
        return json.load(f)


def initialize_database():
    """Initialize database with tables and default data."""
    logger.info("Initializing database...")

    # Connect to database (creates tables)
    db.connect()

    # Load and insert protocol templates
    templates_dir = Path(__file__).parent.parent / "templates" / "protocols"

    if not templates_dir.exists():
        logger.warning(f"Templates directory not found: {templates_dir}")
        return

    with db.session_scope() as session:
        # Load SALT-001 template
        salt_001_path = templates_dir / "salt-001.json"
        if salt_001_path.exists():
            logger.info(f"Loading protocol template: {salt_001_path}")
            template_data = load_protocol_template(salt_001_path)
            protocol_info = template_data["protocol"]

            # Check if protocol already exists
            existing = session.query(Protocol).filter_by(code=protocol_info["code"]).first()

            if existing:
                logger.info(f"Protocol {protocol_info['code']} already exists, updating...")
                existing.name = protocol_info["name"]
                existing.version = protocol_info["version"]
                existing.description = protocol_info["description"]
                existing.category = protocol_info["category"]
                existing.standard = protocol_info.get("standard")
                existing.template = template_data
            else:
                logger.info(f"Creating new protocol: {protocol_info['code']}")
                protocol = Protocol(
                    code=protocol_info["code"],
                    name=protocol_info["name"],
                    version=protocol_info["version"],
                    description=protocol_info["description"],
                    category=protocol_info["category"],
                    standard=protocol_info.get("standard"),
                    template=template_data,
                    active=True,
                )
                session.add(protocol)

        session.commit()
        logger.info("Protocol templates loaded successfully")

    # Verify database
    with db.session_scope() as session:
        protocol_count = session.query(Protocol).count()
        logger.info(f"Database initialized with {protocol_count} protocol(s)")

    db.disconnect()
    logger.info("Database initialization complete")


if __name__ == "__main__":
    initialize_database()
