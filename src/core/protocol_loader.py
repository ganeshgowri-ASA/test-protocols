"""
Protocol Loader Module

Handles loading and parsing of JSON protocol templates.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProtocolLoader:
    """Loads and parses protocol JSON files."""

    def __init__(self, protocols_dir: Optional[Path] = None):
        """
        Initialize the ProtocolLoader.

        Args:
            protocols_dir: Directory containing protocol templates.
                          Defaults to protocols/templates/
        """
        if protocols_dir is None:
            protocols_dir = Path(__file__).parent.parent.parent / "protocols" / "templates"

        self.protocols_dir = Path(protocols_dir)
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol by its ID.

        Args:
            protocol_id: Protocol identifier (e.g., "PID-002")

        Returns:
            Dictionary containing protocol definition

        Raises:
            FileNotFoundError: If protocol file not found
            json.JSONDecodeError: If protocol JSON is invalid
        """
        # Check cache first
        if protocol_id in self._protocol_cache:
            logger.debug(f"Loading protocol {protocol_id} from cache")
            return self._protocol_cache[protocol_id]

        # Search for protocol file
        protocol_file = self._find_protocol_file(protocol_id)

        if protocol_file is None:
            raise FileNotFoundError(
                f"Protocol {protocol_id} not found in {self.protocols_dir}"
            )

        # Load and parse JSON
        logger.info(f"Loading protocol {protocol_id} from {protocol_file}")
        with open(protocol_file, 'r', encoding='utf-8') as f:
            protocol_data = json.load(f)

        # Validate basic structure
        if protocol_data.get('protocol_id') != protocol_id:
            logger.warning(
                f"Protocol ID mismatch: file contains {protocol_data.get('protocol_id')}, "
                f"expected {protocol_id}"
            )

        # Cache the protocol
        self._protocol_cache[protocol_id] = protocol_data

        return protocol_data

    def load_protocol_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a protocol from a specific file path.

        Args:
            file_path: Path to protocol JSON file

        Returns:
            Dictionary containing protocol definition
        """
        logger.info(f"Loading protocol from {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            protocol_data = json.load(f)

        # Cache by protocol_id if available
        protocol_id = protocol_data.get('protocol_id')
        if protocol_id:
            self._protocol_cache[protocol_id] = protocol_data

        return protocol_data

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """
        Find protocol file by ID.

        Searches recursively in the protocols directory for a JSON file
        matching the protocol ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Path to protocol file, or None if not found
        """
        # Try direct filename match first
        direct_match = self.protocols_dir / f"{protocol_id.lower()}.json"
        if direct_match.exists():
            return direct_match

        # Search recursively
        for json_file in self.protocols_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('protocol_id') == protocol_id:
                        return json_file
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Error reading {json_file}: {e}")
                continue

        return None

    def list_protocols(self) -> List[Dict[str, Any]]:
        """
        List all available protocols.

        Returns:
            List of protocol metadata (id, name, version, category)
        """
        protocols = []

        for json_file in self.protocols_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    protocols.append({
                        'protocol_id': data.get('protocol_id'),
                        'name': data.get('name'),
                        'version': data.get('version'),
                        'category': data.get('category'),
                        'subcategory': data.get('subcategory'),
                        'file_path': str(json_file)
                    })
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Error reading {json_file}: {e}")
                continue

        return protocols

    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get protocol metadata without loading full protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary containing protocol metadata
        """
        protocol = self.load_protocol(protocol_id)
        return {
            'protocol_id': protocol.get('protocol_id'),
            'name': protocol.get('name'),
            'version': protocol.get('version'),
            'category': protocol.get('category'),
            'subcategory': protocol.get('subcategory'),
            'metadata': protocol.get('metadata', {}),
            'standard_reference': protocol.get('standard_reference')
        }

    def get_test_steps(self, protocol_id: str) -> List[Dict[str, Any]]:
        """
        Get test steps for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of test steps
        """
        protocol = self.load_protocol(protocol_id)
        return protocol.get('test_sequence', {}).get('steps', [])

    def get_equipment_requirements(self, protocol_id: str) -> List[Dict[str, Any]]:
        """
        Get equipment requirements for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of required equipment
        """
        protocol = self.load_protocol(protocol_id)
        return protocol.get('equipment_requirements', [])

    def clear_cache(self):
        """Clear the protocol cache."""
        self._protocol_cache.clear()
        logger.info("Protocol cache cleared")
