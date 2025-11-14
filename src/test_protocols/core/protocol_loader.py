"""Protocol loader module for loading and validating JSON protocol definitions."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError


class ProtocolLoader:
    """Loads and validates protocol JSON definitions."""

    def __init__(self, protocols_dir: Optional[str] = None, schema_path: Optional[str] = None):
        """
        Initialize the protocol loader.

        Args:
            protocols_dir: Directory containing protocol JSON files
            schema_path: Path to the JSON schema file for validation
        """
        if protocols_dir is None:
            # Default to protocols directory at project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.protocols_dir = project_root / "protocols"
        else:
            self.protocols_dir = Path(protocols_dir)

        if schema_path is None:
            self.schema_path = self.protocols_dir / "schema.json"
        else:
            self.schema_path = Path(schema_path)

        self.schema = self._load_schema()
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for protocol validation."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, "r") as f:
            return json.load(f)

    def load_protocol(self, protocol_id: str, validate_schema: bool = True) -> Dict[str, Any]:
        """
        Load a protocol definition from JSON file.

        Args:
            protocol_id: Protocol identifier (e.g., 'ENER-001')
            validate_schema: Whether to validate against JSON schema

        Returns:
            Dictionary containing protocol definition

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            ValidationError: If protocol doesn't match schema
        """
        # Check cache first
        if protocol_id in self._protocol_cache:
            return self._protocol_cache[protocol_id]

        # Construct file path
        protocol_file = self.protocols_dir / f"{protocol_id}.json"

        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        # Load JSON
        with open(protocol_file, "r") as f:
            protocol_data = json.load(f)

        # Validate against schema
        if validate_schema:
            try:
                validate(instance=protocol_data, schema=self.schema)
            except ValidationError as e:
                raise ValidationError(
                    f"Protocol {protocol_id} validation failed: {e.message}"
                )

        # Cache the protocol
        self._protocol_cache[protocol_id] = protocol_data

        return protocol_data

    def list_protocols(self) -> list[str]:
        """
        List all available protocols.

        Returns:
            List of protocol IDs
        """
        protocol_files = self.protocols_dir.glob("*.json")
        protocols = []

        for file in protocol_files:
            if file.name != "schema.json" and not file.name.startswith("_"):
                protocol_id = file.stem
                protocols.append(protocol_id)

        return sorted(protocols)

    def get_protocol_info(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get basic information about a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary with protocol metadata
        """
        protocol = self.load_protocol(protocol_id)

        return {
            "protocol_id": protocol["protocol_id"],
            "version": protocol["version"],
            "name": protocol["name"],
            "category": protocol["category"],
            "description": protocol["description"],
            "standards": protocol["metadata"]["standards"],
        }

    def reload_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Reload a protocol from disk, clearing cache.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Reloaded protocol definition
        """
        if protocol_id in self._protocol_cache:
            del self._protocol_cache[protocol_id]

        return self.load_protocol(protocol_id)

    def validate_protocol_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate a protocol JSON file against the schema.

        Args:
            file_path: Path to protocol JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, "r") as f:
                protocol_data = json.load(f)

            validate(instance=protocol_data, schema=self.schema)
            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"


def load_protocol(protocol_id: str) -> Dict[str, Any]:
    """
    Convenience function to load a protocol.

    Args:
        protocol_id: Protocol identifier

    Returns:
        Protocol definition dictionary
    """
    loader = ProtocolLoader()
    return loader.load_protocol(protocol_id)
