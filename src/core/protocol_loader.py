"""
Protocol Loader Module
Loads and validates JSON protocol definitions
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProtocolLoader:
    """Load and validate test protocol definitions from JSON files"""

    def __init__(self, protocols_dir: Optional[Path] = None):
        """
        Initialize the protocol loader

        Args:
            protocols_dir: Path to the protocols directory. If None, uses default.
        """
        if protocols_dir is None:
            # Default to protocols directory in project root
            self.protocols_dir = Path(__file__).parent.parent.parent / "protocols"
        else:
            self.protocols_dir = Path(protocols_dir)

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol by its ID

        Args:
            protocol_id: The protocol identifier (e.g., "TROP-001")

        Returns:
            Dictionary containing the protocol definition

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            ValueError: If protocol JSON is invalid
        """
        protocol_file = self._find_protocol_file(protocol_id)

        if not protocol_file:
            raise FileNotFoundError(
                f"Protocol {protocol_id} not found in {self.protocols_dir}"
            )

        with open(protocol_file, 'r') as f:
            protocol_data = json.load(f)

        # Validate basic structure
        self._validate_protocol(protocol_data)

        return protocol_data

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """
        Find the protocol JSON file by ID

        Args:
            protocol_id: The protocol identifier

        Returns:
            Path to the protocol file, or None if not found
        """
        # Search all subdirectories for the protocol
        for json_file in self.protocols_dir.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if data.get('protocol_id') == protocol_id:
                        return json_file
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def _validate_protocol(self, protocol: Dict[str, Any]) -> None:
        """
        Validate protocol structure and required fields

        Args:
            protocol: Protocol dictionary to validate

        Raises:
            ValueError: If protocol is invalid
        """
        required_fields = [
            'protocol_id',
            'version',
            'name',
            'category',
            'test_sequence',
            'acceptance_criteria'
        ]

        missing_fields = [
            field for field in required_fields
            if field not in protocol
        ]

        if missing_fields:
            raise ValueError(
                f"Protocol missing required fields: {', '.join(missing_fields)}"
            )

        # Validate test sequence
        if 'steps' not in protocol['test_sequence']:
            raise ValueError("Test sequence must contain 'steps'")

        if not protocol['test_sequence']['steps']:
            raise ValueError("Test sequence must have at least one step")

    def list_protocols(self, category: Optional[str] = None) -> list:
        """
        List all available protocols

        Args:
            category: Optional category filter

        Returns:
            List of protocol summaries
        """
        protocols = []

        for json_file in self.protocols_dir.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                    # Filter by category if specified
                    if category and data.get('category') != category:
                        continue

                    protocols.append({
                        'protocol_id': data.get('protocol_id'),
                        'name': data.get('name'),
                        'category': data.get('category'),
                        'version': data.get('version'),
                        'file_path': str(json_file)
                    })
            except (json.JSONDecodeError, KeyError):
                continue

        return sorted(protocols, key=lambda x: x['protocol_id'])

    def get_protocol_info(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get summary information about a protocol

        Args:
            protocol_id: The protocol identifier

        Returns:
            Dictionary with protocol summary
        """
        protocol = self.load_protocol(protocol_id)

        return {
            'protocol_id': protocol['protocol_id'],
            'name': protocol['name'],
            'version': protocol['version'],
            'category': protocol['category'],
            'subcategory': protocol.get('subcategory'),
            'standard': protocol.get('standard'),
            'description': protocol.get('description'),
            'total_duration': protocol['test_sequence'].get('total_test_duration'),
            'duration_unit': protocol['test_sequence'].get('total_test_duration_unit'),
            'sample_size': protocol['test_requirements']['sample_size']
        }
