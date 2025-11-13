"""Database initialization script."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import init_db, engine
from src.models.protocol import Base
import json


def initialize_database():
    """Initialize database and load default protocols."""
    print("Initializing database...")

    # Create all tables
    init_db()
    print("✓ Database tables created")

    # Load PID-001 protocol
    from sqlalchemy.orm import Session
    from src.models.protocol import Protocol, ProtocolStatus

    protocol_schema_path = Path(__file__).parent.parent / "protocols" / "pid-001" / "schema.json"

    if protocol_schema_path.exists():
        with open(protocol_schema_path) as f:
            schema = json.load(f)

        with Session(engine) as session:
            # Check if protocol already exists
            existing = session.query(Protocol).filter_by(pid="pid-001").first()

            if not existing:
                protocol = Protocol(
                    pid=schema["metadata"]["pid"],
                    name=schema["metadata"]["name"],
                    version=schema["metadata"]["version"],
                    standard=schema["metadata"].get("standard"),
                    description=schema["metadata"].get("description"),
                    schema=schema,
                    status=ProtocolStatus.ACTIVE,
                )
                session.add(protocol)
                session.commit()
                print(f"✓ Loaded protocol: {protocol.name} (v{protocol.version})")
            else:
                print(f"  Protocol pid-001 already exists, skipping...")

    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    initialize_database()
