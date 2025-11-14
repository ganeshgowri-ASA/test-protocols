"""Protocol loader module for loading and validating JSON protocol definitions."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class ProtocolLoader:
    """Load and validate JSON protocol definitions."""

    def __init__(self, protocols_dir: Optional[Path] = None):
        """
        Initialize the ProtocolLoader.

        Args:
            protocols_dir: Path to the protocols directory.
                          If None, uses default location.
        """
        if protocols_dir is None:
            protocols_dir = Path(__file__).parent.parent / "protocols"
        self.protocols_dir = protocols_dir
        self.schema = self._load_schema()
        logger.info(f"ProtocolLoader initialized with directory: {self.protocols_dir}")

    def _load_schema(self) -> Dict[str, Any]:
        """
        Load the JSON schema for protocol validation.

        Returns:
            JSON schema dictionary
        """
        # For now, we'll define the schema inline
        # In production, this could be loaded from a separate schema.json file
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Test Protocol Schema",
            "type": "object",
            "required": ["protocol"],
            "properties": {
                "protocol": {
                    "type": "object",
                    "required": ["id", "name", "version", "test_phases"],
                    "properties": {
                        "id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                        "name": {"type": "string", "minLength": 1, "maxLength": 255},
                        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                        "description": {"type": "string"},
                        "test_phases": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "object"},
                        },
                    },
                }
            },
        }
        return schema

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol by ID.

        Args:
            protocol_id: The protocol identifier

        Returns:
            Protocol data dictionary

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            ValueError: If protocol validation fails
        """
        protocol_path = self.protocols_dir / protocol_id / "protocol.json"

        if not protocol_path.exists():
            logger.error(f"Protocol not found: {protocol_id} at {protocol_path}")
            raise FileNotFoundError(f"Protocol not found: {protocol_id}")

        logger.info(f"Loading protocol: {protocol_id}")

        with open(protocol_path, "r") as f:
            protocol_data = json.load(f)

        # Validate against schema
        try:
            validate(instance=protocol_data, schema=self.schema)
            logger.info(f"Protocol {protocol_id} validated successfully")
        except ValidationError as e:
            logger.error(f"Protocol validation failed: {e.message}")
            raise ValueError(f"Protocol validation failed: {e.message}")

        return protocol_data

    def list_protocols(self) -> List[Dict[str, Any]]:
        """
        List all available protocols.

        Returns:
            List of protocol metadata dictionaries
        """
        protocols = []

        if not self.protocols_dir.exists():
            logger.warning(f"Protocols directory does not exist: {self.protocols_dir}")
            return protocols

        for protocol_dir in self.protocols_dir.iterdir():
            if protocol_dir.is_dir() and (protocol_dir / "protocol.json").exists():
                try:
                    # Try to load metadata if it exists, otherwise use protocol.json
                    metadata_path = protocol_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                    else:
                        with open(protocol_dir / "protocol.json") as f:
                            protocol_data = json.load(f)
                            metadata = {
                                "id": protocol_data["protocol"]["id"],
                                "name": protocol_data["protocol"]["name"],
                                "version": protocol_data["protocol"]["version"],
                                "description": protocol_data["protocol"].get(
                                    "description", ""
                                ),
                            }

                    protocols.append(
                        {
                            "id": protocol_dir.name,
                            "name": metadata.get("name"),
                            "version": metadata.get("version"),
                            "description": metadata.get("description", ""),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to load protocol {protocol_dir.name}: {e}")

        logger.info(f"Found {len(protocols)} protocols")
        return protocols

    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific protocol.

        Args:
            protocol_id: The protocol identifier

        Returns:
            Protocol metadata dictionary
        """
        protocol_data = self.load_protocol(protocol_id)
        return {
            "id": protocol_data["protocol"]["id"],
            "name": protocol_data["protocol"]["name"],
            "version": protocol_data["protocol"]["version"],
            "description": protocol_data["protocol"].get("description", ""),
            "created_at": protocol_data["protocol"].get("created_at", ""),
            "updated_at": protocol_data["protocol"].get("updated_at", ""),
            "author": protocol_data["protocol"].get("author", ""),
        }
