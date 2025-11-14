#!/usr/bin/env python3
"""Initialize database with schema and optionally load sample data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.schema import init_database
from src.database.models import Protocol, Equipment, ProtocolStatus
import json


def load_protocols_to_db(db_manager):
    """Load protocol definitions into database."""
    session = db_manager.get_session()

    # Load CONC-001 protocol
    protocol_file = Path("protocols/conc-001/schema/conc-001-schema.json")

    if protocol_file.exists():
        with open(protocol_file, 'r') as f:
            protocol_data = json.load(f)

        protocol = Protocol(
            id=protocol_data['protocol_id'],
            name=protocol_data['name'],
            version=protocol_data['version'],
            description=protocol_data['description'],
            category=protocol_data.get('metadata', {}).get('category', 'General'),
            status=ProtocolStatus.ACTIVE,
            schema_json=protocol_data.get('schema', {}),
            qc_criteria_json=protocol_data.get('qc_criteria', {}),
            created_by="system"
        )

        session.add(protocol)
        print(f"✓ Loaded protocol: {protocol.id}")

    session.commit()
    session.close()


def load_sample_equipment(db_manager):
    """Load sample equipment records."""
    session = db_manager.get_session()

    equipment_list = [
        {
            "id": "SIM-001-ClassAAA",
            "name": "Solar Simulator 1",
            "equipment_type": "solar_simulator",
            "manufacturer": "Example Corp",
            "model": "AAA-1000",
            "calibration_status": "valid"
        },
        {
            "id": "REF-CELL-001",
            "name": "Reference Cell 1",
            "equipment_type": "reference_cell",
            "manufacturer": "Example Corp",
            "model": "RC-100",
            "calibration_status": "valid"
        }
    ]

    for eq_data in equipment_list:
        equipment = Equipment(**eq_data)
        session.add(equipment)
        print(f"✓ Loaded equipment: {equipment.id}")

    session.commit()
    session.close()


def main():
    """Main setup function."""
    print("=" * 60)
    print("Test Protocols Framework - Database Setup")
    print("=" * 60)

    # Initialize database
    print("\n1. Creating database tables...")
    db_manager = init_database()
    print("✓ Database tables created")

    # Load protocols
    print("\n2. Loading protocol definitions...")
    try:
        load_protocols_to_db(db_manager)
        print("✓ Protocol definitions loaded")
    except Exception as e:
        print(f"⚠ Warning: Could not load protocols: {e}")

    # Load sample equipment
    print("\n3. Loading sample equipment...")
    try:
        load_sample_equipment(db_manager)
        print("✓ Sample equipment loaded")
    except Exception as e:
        print(f"⚠ Warning: Could not load equipment: {e}")

    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)

    db_manager.close()


if __name__ == "__main__":
    main()
