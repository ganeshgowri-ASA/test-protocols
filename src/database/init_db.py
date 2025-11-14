"""
Database Initialization Script

Creates database tables and optionally seeds with initial data.
"""

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Protocol
import json

logger = logging.getLogger(__name__)


def create_database(database_url: str = "sqlite:///pv_protocols.db") -> None:
    """
    Create database tables.

    Args:
        database_url: SQLAlchemy database URL
    """
    logger.info(f"Creating database: {database_url}")

    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)

    logger.info("Database tables created successfully")


def seed_protocols(database_url: str = "sqlite:///pv_protocols.db",
                   protocols_dir: Path = None) -> None:
    """
    Seed database with protocol definitions.

    Args:
        database_url: SQLAlchemy database URL
        protocols_dir: Directory containing protocol JSON files
    """
    if protocols_dir is None:
        protocols_dir = Path(__file__).parent.parent.parent / "protocols"

    logger.info(f"Seeding protocols from: {protocols_dir}")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find all protocol.json files
        protocol_files = protocols_dir.rglob("protocol.json")

        for protocol_file in protocol_files:
            logger.info(f"Loading protocol: {protocol_file}")

            with open(protocol_file, 'r') as f:
                definition = json.load(f)

            # Check if protocol already exists
            existing = session.query(Protocol).filter_by(
                protocol_id=definition['protocol_id']
            ).first()

            if existing:
                logger.info(f"Protocol {definition['protocol_id']} already exists, updating...")
                existing.version = definition['version']
                existing.name = definition['name']
                existing.category = definition['category']
                existing.description = definition['description']
                existing.definition_json = definition
            else:
                logger.info(f"Adding new protocol: {definition['protocol_id']}")
                protocol = Protocol(
                    protocol_id=definition['protocol_id'],
                    name=definition['name'],
                    version=definition['version'],
                    category=definition['category'],
                    description=definition['description'],
                    definition_json=definition
                )
                session.add(protocol)

        session.commit()
        logger.info("Protocols seeded successfully")

    except Exception as e:
        logger.error(f"Error seeding protocols: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create database
    create_database()

    # Seed with protocols
    seed_protocols()
