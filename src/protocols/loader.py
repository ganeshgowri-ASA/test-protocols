"""
Protocol loader for loading and validating JSON protocol definitions
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProtocolLoader:
    """Loads and validates protocol definitions from JSON files"""

    def __init__(self, protocols_dir: str = "protocols"):
        """
        Initialize the protocol loader

        Args:
            protocols_dir: Directory containing protocol JSON files
        """
        self.protocols_dir = Path(protocols_dir)
        if not self.protocols_dir.exists():
            raise ValueError(f"Protocols directory not found: {protocols_dir}")

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol definition by ID

        Args:
            protocol_id: Protocol identifier (e.g., 'HAIL-001')

        Returns:
            Dictionary containing protocol definition

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            ValueError: If protocol JSON is invalid
        """
        protocol_file = self.protocols_dir / f"{protocol_id}.json"

        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        try:
            with open(protocol_file, 'r') as f:
                protocol_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in protocol file: {e}")

        # Validate required fields
        self._validate_protocol(protocol_data)

        return protocol_data

    def _validate_protocol(self, protocol_data: Dict[str, Any]) -> None:
        """
        Validate that protocol contains required fields

        Args:
            protocol_data: Protocol dictionary to validate

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            'protocol_id',
            'version',
            'title',
            'category',
            'standard',
            'test_parameters',
            'test_procedure',
            'pass_fail_criteria'
        ]

        missing_fields = [field for field in required_fields if field not in protocol_data]

        if missing_fields:
            raise ValueError(f"Protocol missing required fields: {', '.join(missing_fields)}")

    def list_protocols(self) -> list:
        """
        List all available protocols

        Returns:
            List of protocol IDs
        """
        return [f.stem for f in self.protocols_dir.glob("*.json")]

    def get_protocol_info(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get basic information about a protocol without loading full definition

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary with protocol metadata
        """
        protocol = self.load_protocol(protocol_id)

        return {
            'protocol_id': protocol['protocol_id'],
            'version': protocol['version'],
            'title': protocol['title'],
            'category': protocol['category'],
            'standard': protocol['standard']['name']
        }
