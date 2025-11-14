"""Protocol loader for loading and validating JSON protocol definitions."""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..models import Protocol
from ..models.base import get_session


class ProtocolLoader:
    """Handles loading and validation of protocol JSON files."""

    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize the protocol loader.

        Args:
            schema_path: Path to the JSON schema file. If None, uses default location.
        """
        if schema_path is None:
            # Default schema location
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "protocol_schema.json"

        self.schema_path = schema_path
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for protocol validation.

        Returns:
            The loaded JSON schema as a dictionary.

        Raises:
            FileNotFoundError: If schema file doesn't exist.
            json.JSONDecodeError: If schema file is invalid JSON.
        """
        with open(self.schema_path, 'r') as f:
            return json.load(f)

    def load_protocol_file(self, protocol_path: Path) -> Dict[str, Any]:
        """Load a protocol JSON file.

        Args:
            protocol_path: Path to the protocol JSON file.

        Returns:
            The loaded protocol data as a dictionary.

        Raises:
            FileNotFoundError: If protocol file doesn't exist.
            json.JSONDecodeError: If protocol file is invalid JSON.
        """
        with open(protocol_path, 'r') as f:
            return json.load(f)

    def validate_protocol(self, protocol_data: Dict[str, Any]) -> bool:
        """Validate a protocol against the JSON schema.

        Args:
            protocol_data: The protocol data to validate.

        Returns:
            True if validation succeeds.

        Raises:
            jsonschema.ValidationError: If validation fails.
        """
        jsonschema.validate(instance=protocol_data, schema=self.schema)
        return True

    def load_and_validate(self, protocol_path: Path) -> Dict[str, Any]:
        """Load and validate a protocol file.

        Args:
            protocol_path: Path to the protocol JSON file.

        Returns:
            The validated protocol data.

        Raises:
            FileNotFoundError: If protocol file doesn't exist.
            json.JSONDecodeError: If protocol file is invalid JSON.
            jsonschema.ValidationError: If validation fails.
        """
        protocol_data = self.load_protocol_file(protocol_path)
        self.validate_protocol(protocol_data)
        return protocol_data

    def import_to_database(self, protocol_data: Dict[str, Any], session) -> Protocol:
        """Import a protocol into the database.

        Args:
            protocol_data: The validated protocol data.
            session: Database session.

        Returns:
            The created Protocol database object.
        """
        # Check if protocol already exists
        existing = session.query(Protocol).filter_by(
            protocol_id=protocol_data["protocol_id"]
        ).first()

        if existing:
            # Update existing protocol
            existing.protocol_name = protocol_data["protocol_name"]
            existing.version = protocol_data["version"]
            existing.category = protocol_data["category"]
            existing.description = protocol_data["description"]
            existing.protocol_data = protocol_data
            existing.author = protocol_data.get("metadata", {}).get("author")
            existing.tags = ",".join(protocol_data.get("metadata", {}).get("tags", []))
            protocol = existing
        else:
            # Create new protocol
            protocol = Protocol(
                protocol_id=protocol_data["protocol_id"],
                protocol_name=protocol_data["protocol_name"],
                version=protocol_data["version"],
                category=protocol_data["category"],
                description=protocol_data["description"],
                protocol_data=protocol_data,
                author=protocol_data.get("metadata", {}).get("author"),
                tags=",".join(protocol_data.get("metadata", {}).get("tags", []))
            )
            session.add(protocol)

        session.commit()
        return protocol

    def load_protocol_directory(self, directory_path: Path) -> List[Protocol]:
        """Load all protocol JSON files from a directory.

        Args:
            directory_path: Path to directory containing protocol JSON files.

        Returns:
            List of loaded Protocol objects.
        """
        protocols = []

        # Recursively find all JSON files
        for json_file in directory_path.rglob("*.json"):
            try:
                protocol_data = self.load_and_validate(json_file)
                # Note: This would need a session to import to database
                # For now, just return the data
                protocols.append(protocol_data)
                print(f"Loaded protocol: {protocol_data['protocol_id']} - {protocol_data['protocol_name']}")
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue

        return protocols

    @staticmethod
    def get_protocol_by_id(protocol_id: str, session) -> Optional[Protocol]:
        """Retrieve a protocol from the database by ID.

        Args:
            protocol_id: The protocol ID (e.g., 'TWIST-001').
            session: Database session.

        Returns:
            The Protocol object if found, None otherwise.
        """
        return session.query(Protocol).filter_by(
            protocol_id=protocol_id,
            is_active=True
        ).first()

    @staticmethod
    def list_protocols(session, category: Optional[str] = None) -> List[Protocol]:
        """List all active protocols, optionally filtered by category.

        Args:
            session: Database session.
            category: Optional category filter.

        Returns:
            List of Protocol objects.
        """
        query = session.query(Protocol).filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)

        return query.order_by(Protocol.protocol_id).all()
