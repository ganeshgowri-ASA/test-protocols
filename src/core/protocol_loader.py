"""
Protocol Loader Module

Utility module for loading and managing protocol definitions.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging


class ProtocolLoader:
    """
    Handles loading and caching of protocol definitions.
    """

    def __init__(self, protocols_dir: str = "protocols"):
        """
        Initialize the protocol loader.

        Args:
            protocols_dir: Base directory containing protocol definitions
        """
        self.protocols_dir = Path(protocols_dir)
        self.logger = logging.getLogger(__name__)
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol definition by ID.

        Args:
            protocol_id: Protocol identifier (e.g., "YELLOW-001")

        Returns:
            Dictionary containing protocol data

        Raises:
            FileNotFoundError: If protocol file not found
            ValueError: If protocol data is invalid
        """
        # Check cache first
        if protocol_id in self._protocol_cache:
            self.logger.debug(f"Loading {protocol_id} from cache")
            return self._protocol_cache[protocol_id]

        # Find protocol file
        protocol_file = self._find_protocol_file(protocol_id)

        if not protocol_file:
            raise FileNotFoundError(f"Protocol {protocol_id} not found")

        # Load and validate
        with open(protocol_file, 'r') as f:
            protocol_data = json.load(f)

        self._validate_protocol(protocol_data)

        # Cache it
        self._protocol_cache[protocol_id] = protocol_data

        return protocol_data

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """
        Find the JSON file for a given protocol ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Path to protocol file, or None if not found
        """
        # Search in protocols directory
        for json_file in self.protocols_dir.rglob(f"{protocol_id}.json"):
            return json_file

        return None

    def _validate_protocol(self, protocol_data: Dict[str, Any]) -> None:
        """
        Validate protocol data structure.

        Args:
            protocol_data: Protocol data dictionary

        Raises:
            ValueError: If protocol is invalid
        """
        required_fields = [
            'protocol_id',
            'protocol_name',
            'version',
            'test_parameters',
            'measurements'
        ]

        for field in required_fields:
            if field not in protocol_data:
                raise ValueError(f"Missing required field: {field}")

    def list_protocols(self) -> List[Dict[str, str]]:
        """
        List all available protocols.

        Returns:
            List of protocol metadata dictionaries
        """
        protocols = []

        for json_file in self.protocols_dir.rglob("*.json"):
            if json_file.name == "schema.json":
                continue

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                protocols.append({
                    'protocol_id': data.get('protocol_id'),
                    'protocol_name': data.get('protocol_name'),
                    'version': data.get('version'),
                    'category': data.get('category'),
                    'description': data.get('description')
                })
            except Exception as e:
                self.logger.error(f"Error loading {json_file}: {e}")

        return protocols

    def get_protocol_path(self, protocol_id: str) -> Optional[str]:
        """
        Get the file path for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            String path to protocol file
        """
        protocol_file = self._find_protocol_file(protocol_id)
        return str(protocol_file) if protocol_file else None
