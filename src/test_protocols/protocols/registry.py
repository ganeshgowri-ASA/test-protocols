"""Protocol registry for managing available test protocols."""

from typing import Dict, List, Optional, Type

from test_protocols.logger import setup_logger
from test_protocols.protocols.base import BaseProtocol
from test_protocols.protocols.salt_001 import SALT001Protocol

logger = setup_logger(__name__)


class ProtocolRegistry:
    """Registry for managing available test protocols.

    This class maintains a registry of all available protocol implementations
    and provides methods for protocol discovery and instantiation.
    """

    def __init__(self):
        """Initialize protocol registry."""
        self._protocols: Dict[str, Type[BaseProtocol]] = {}
        self._register_builtin_protocols()

    def _register_builtin_protocols(self) -> None:
        """Register built-in protocol implementations."""
        self.register("SALT-001", SALT001Protocol)
        logger.info("Registered built-in protocols")

    def register(self, code: str, protocol_class: Type[BaseProtocol]) -> None:
        """Register a protocol implementation.

        Args:
            code: Protocol code (e.g., 'SALT-001')
            protocol_class: Protocol class implementing BaseProtocol

        Raises:
            ValueError: If protocol code is already registered
            TypeError: If protocol_class is not a subclass of BaseProtocol
        """
        if not issubclass(protocol_class, BaseProtocol):
            raise TypeError(f"{protocol_class} must be a subclass of BaseProtocol")

        if code in self._protocols:
            raise ValueError(f"Protocol '{code}' is already registered")

        self._protocols[code] = protocol_class
        logger.info(f"Registered protocol: {code}")

    def unregister(self, code: str) -> None:
        """Unregister a protocol implementation.

        Args:
            code: Protocol code to unregister

        Raises:
            KeyError: If protocol code is not registered
        """
        if code not in self._protocols:
            raise KeyError(f"Protocol '{code}' is not registered")

        del self._protocols[code]
        logger.info(f"Unregistered protocol: {code}")

    def get_protocol(self, code: str) -> BaseProtocol:
        """Get a protocol instance by code.

        Args:
            code: Protocol code (e.g., 'SALT-001')

        Returns:
            BaseProtocol: Protocol instance

        Raises:
            KeyError: If protocol code is not registered
        """
        if code not in self._protocols:
            raise KeyError(
                f"Protocol '{code}' is not registered. "
                f"Available protocols: {self.list_protocols()}"
            )

        protocol_class = self._protocols[code]
        return protocol_class()

    def list_protocols(self) -> List[str]:
        """List all registered protocol codes.

        Returns:
            List[str]: List of protocol codes
        """
        return sorted(self._protocols.keys())

    def get_protocol_info(self, code: str) -> Dict[str, str]:
        """Get protocol metadata information.

        Args:
            code: Protocol code

        Returns:
            Dict[str, str]: Protocol metadata

        Raises:
            KeyError: If protocol code is not registered
        """
        protocol = self.get_protocol(code)
        return {
            "code": protocol.metadata.code,
            "name": protocol.metadata.name,
            "version": protocol.metadata.version,
            "description": protocol.metadata.description,
            "category": protocol.metadata.category.value,
            "standard": protocol.metadata.standard or "N/A",
        }

    def search_protocols(
        self,
        category: Optional[str] = None,
        standard: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[str]:
        """Search protocols by criteria.

        Args:
            category: Filter by category
            standard: Filter by standard
            keyword: Search in name/description

        Returns:
            List[str]: List of matching protocol codes
        """
        matching = []

        for code in self._protocols:
            protocol = self.get_protocol(code)

            # Category filter
            if category and protocol.metadata.category.value != category:
                continue

            # Standard filter
            if standard and protocol.metadata.standard != standard:
                continue

            # Keyword search
            if keyword:
                keyword_lower = keyword.lower()
                if not (
                    keyword_lower in protocol.metadata.name.lower()
                    or keyword_lower in protocol.metadata.description.lower()
                ):
                    continue

            matching.append(code)

        return sorted(matching)

    def __contains__(self, code: str) -> bool:
        """Check if protocol is registered.

        Args:
            code: Protocol code

        Returns:
            bool: True if protocol is registered
        """
        return code in self._protocols

    def __len__(self) -> int:
        """Get number of registered protocols.

        Returns:
            int: Number of protocols
        """
        return len(self._protocols)

    def __repr__(self) -> str:
        """String representation of registry.

        Returns:
            str: Registry representation
        """
        return f"ProtocolRegistry(protocols={len(self._protocols)})"


# Global protocol registry instance
protocol_registry = ProtocolRegistry()
