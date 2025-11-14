"""Protocol registry for managing available protocols"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from .protocol_base import ProtocolBase

logger = logging.getLogger(__name__)


class ProtocolRegistry:
    """
    Registry for managing and discovering test protocols.
    """

    _instance = None
    _protocols: Dict[str, Type[ProtocolBase]] = {}
    _definitions: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(ProtocolRegistry, cls).__new__(cls)
        return cls._instance

    def register(
        self,
        protocol_id: str,
        protocol_class: Type[ProtocolBase],
        definition: Dict[str, Any] = None,
    ) -> None:
        """
        Register a protocol implementation.

        Args:
            protocol_id: Unique protocol identifier
            protocol_class: Protocol class (subclass of ProtocolBase)
            definition: Optional protocol definition dictionary
        """
        if not issubclass(protocol_class, ProtocolBase):
            raise TypeError(f"{protocol_class} must be a subclass of ProtocolBase")

        self._protocols[protocol_id] = protocol_class
        if definition:
            self._definitions[protocol_id] = definition

        logger.info(f"Registered protocol: {protocol_id}")

    def get_protocol_class(self, protocol_id: str) -> Optional[Type[ProtocolBase]]:
        """
        Get protocol class by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol class or None if not found
        """
        return self._protocols.get(protocol_id)

    def get_protocol_definition(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get protocol definition by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol definition dictionary or None if not found
        """
        return self._definitions.get(protocol_id)

    def create_protocol(self, protocol_id: str) -> Optional[ProtocolBase]:
        """
        Create an instance of a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol instance or None if not found
        """
        protocol_class = self.get_protocol_class(protocol_id)
        definition = self.get_protocol_definition(protocol_id)

        if not protocol_class or not definition:
            logger.error(f"Protocol not found: {protocol_id}")
            return None

        return protocol_class(definition)

    def list_protocols(self) -> List[str]:
        """
        Get list of all registered protocol IDs.

        Returns:
            List of protocol IDs
        """
        return list(self._protocols.keys())

    def get_protocols_by_category(self, category: str) -> List[str]:
        """
        Get protocols filtered by category.

        Args:
            category: Category name (e.g., 'Degradation')

        Returns:
            List of protocol IDs in the category
        """
        result = []
        for protocol_id, definition in self._definitions.items():
            if definition.get("category") == category:
                result.append(protocol_id)
        return result

    def load_protocols_from_directory(self, templates_dir: str) -> None:
        """
        Scan directory for protocol definitions and load them.

        Args:
            templates_dir: Path to templates directory
        """
        templates_path = Path(templates_dir)

        if not templates_path.exists():
            logger.warning(f"Templates directory not found: {templates_dir}")
            return

        for protocol_dir in templates_path.iterdir():
            if protocol_dir.is_dir():
                protocol_json = protocol_dir / "protocol.json"
                if protocol_json.exists():
                    try:
                        with open(protocol_json, "r") as f:
                            definition = json.load(f)
                            protocol_id = definition.get("protocol_id")
                            if protocol_id:
                                self._definitions[protocol_id] = definition
                                logger.info(f"Loaded protocol definition: {protocol_id}")
                    except Exception as e:
                        logger.error(f"Error loading protocol from {protocol_json}: {e}")

    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get metadata for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Metadata dictionary
        """
        definition = self.get_protocol_definition(protocol_id)
        if not definition:
            return {}

        return {
            "protocol_id": protocol_id,
            "name": definition.get("name", ""),
            "version": definition.get("version", ""),
            "category": definition.get("category", ""),
            "description": definition.get("description", ""),
            "tags": definition.get("metadata", {}).get("tags", []),
        }


# Global registry instance
registry = ProtocolRegistry()
