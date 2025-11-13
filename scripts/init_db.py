#!/usr/bin/env python3
"""Initialize database and load protocols."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import init_db
from src.database.models import Protocol
from src.core.protocol_loader import get_protocol_loader


def main():
    """Initialize database and load protocols."""
    print("Initializing database...")

    # Initialize database
    init_db()

    print("Database initialized successfully!")
    print("\nLoading protocols...")

    # Load protocols
    loader = get_protocol_loader()
    protocols = loader.list_protocols()

    print(f"Found {len(protocols)} protocol(s):")
    for protocol in protocols:
        print(f"  - {protocol['protocol_id']}: {protocol['name']}")

    print("\nSetup complete!")
    print("\nNext steps:")
    print("  1. Run the UI: streamlit run ui/app.py")
    print("  2. Or import data programmatically")


if __name__ == "__main__":
    main()
