"""
Protocol loader service - loads and validates protocol JSON definitions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ProtocolLoader:
    """Loads and validates protocol definitions"""

    def __init__(self, protocols_dir: str = "protocols"):
        self.protocols_dir = Path(protocols_dir)
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load protocol definition by ID

        Args:
            protocol_id: Protocol identifier (e.g., 'CORR-001')

        Returns:
            Protocol definition dictionary

        Raises:
            FileNotFoundError: If protocol file not found
            ValueError: If protocol is invalid
        """
        if protocol_id in self._protocol_cache:
            return self._protocol_cache[protocol_id]

        # Find protocol file
        protocol_path = self._find_protocol_file(protocol_id)
        if not protocol_path:
            raise FileNotFoundError(f"Protocol {protocol_id} not found")

        # Load JSON
        with open(protocol_path, 'r') as f:
            protocol = json.load(f)

        # Basic validation
        self._validate_protocol(protocol)

        # Cache and return
        self._protocol_cache[protocol_id] = protocol
        logger.info(f"Loaded protocol {protocol_id} from {protocol_path}")

        return protocol

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """Find protocol JSON file by ID"""
        # Try lowercase directory name
        protocol_dir = protocol_id.lower()
        protocol_file = self.protocols_dir / protocol_dir / "json" / "protocol.json"

        if protocol_file.exists():
            return protocol_file

        # Search all subdirectories
        for protocol_file in self.protocols_dir.rglob("protocol.json"):
            with open(protocol_file, 'r') as f:
                try:
                    data = json.load(f)
                    if data.get("protocol_id") == protocol_id:
                        return protocol_file
                except Exception:
                    continue

        return None

    def _validate_protocol(self, protocol: Dict[str, Any]):
        """Basic protocol validation"""
        required_fields = ["protocol_id", "name", "version", "type"]

        for field in required_fields:
            if field not in protocol:
                raise ValueError(f"Missing required field: {field}")

        logger.info(f"Protocol {protocol['protocol_id']} validation passed")

    def list_protocols(self) -> List[str]:
        """List all available protocol IDs"""
        protocols = []

        for protocol_file in self.protocols_dir.rglob("protocol.json"):
            try:
                with open(protocol_file, 'r') as f:
                    data = json.load(f)
                    protocol_id = data.get("protocol_id")
                    if protocol_id:
                        protocols.append(protocol_id)
            except Exception as e:
                logger.warning(f"Error reading {protocol_file}: {e}")

        return sorted(protocols)

    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]:
        """Get protocol metadata without full definition"""
        protocol = self.load_protocol(protocol_id)

        return {
            "protocol_id": protocol["protocol_id"],
            "name": protocol["name"],
            "version": protocol["version"],
            "type": protocol["type"],
            "description": protocol.get("description", ""),
            "metadata": protocol.get("metadata", {})
        }
