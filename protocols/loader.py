"""
Protocol Loader
Utility for loading and instantiating protocol classes
"""

import json
from pathlib import Path
from typing import Dict, Type, Optional

from .base import BaseProtocol


class ProtocolLoader:
    """Loads and manages protocol instances"""

    _protocol_registry: Dict[str, Type[BaseProtocol]] = {}

    @classmethod
    def register_protocol(cls, protocol_code: str, protocol_class: Type[BaseProtocol]):
        """
        Register a protocol class

        Args:
            protocol_code: Protocol code (e.g., 'H2S-001')
            protocol_class: Protocol class to register
        """
        cls._protocol_registry[protocol_code] = protocol_class

    @classmethod
    def load_protocol(cls, protocol_path: Path) -> Optional[BaseProtocol]:
        """
        Load a protocol from JSON file and instantiate appropriate class

        Args:
            protocol_path: Path to protocol JSON file

        Returns:
            Instantiated protocol object or None if not found
        """
        # Read protocol metadata to determine type
        with open(protocol_path, 'r') as f:
            config = json.load(f)

        protocol_code = config.get("protocol", {}).get("code")

        if protocol_code in cls._protocol_registry:
            protocol_class = cls._protocol_registry[protocol_code]
            return protocol_class(protocol_path)
        else:
            # Return generic BaseProtocol implementation if specific not found
            return None

    @classmethod
    def list_registered_protocols(cls) -> Dict[str, Type[BaseProtocol]]:
        """Get all registered protocols"""
        return cls._protocol_registry.copy()

    @classmethod
    def find_protocol_files(cls, base_dir: Path) -> list[Path]:
        """
        Find all protocol JSON files in directory tree

        Args:
            base_dir: Base directory to search

        Returns:
            List of protocol file paths
        """
        return list(base_dir.rglob("*.json"))
