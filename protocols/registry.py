"""Protocol registry for managing available test protocols."""

from typing import Dict, List, Optional, Type

from .base import BaseProtocol
from utils.logging import get_logger

logger = get_logger(__name__)


class ProtocolRegistry:
    """Registry for managing available test protocols."""

    _instance: Optional['ProtocolRegistry'] = None
    _protocols: Dict[str, Type[BaseProtocol]] = {}

    def __new__(cls) -> 'ProtocolRegistry':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        protocol_id: str,
        protocol_class: Type[BaseProtocol]
    ) -> None:
        """Register a protocol class.

        Args:
            protocol_id: Unique protocol identifier
            protocol_class: Protocol class (must inherit from BaseProtocol)

        Raises:
            ValueError: If protocol_id already registered or invalid class
        """
        if protocol_id in self._protocols:
            raise ValueError(f"Protocol {protocol_id} already registered")

        if not issubclass(protocol_class, BaseProtocol):
            raise ValueError(
                f"Protocol class must inherit from BaseProtocol, "
                f"got {protocol_class}"
            )

        self._protocols[protocol_id] = protocol_class
        logger.info(f"Registered protocol: {protocol_id}")

    def unregister(self, protocol_id: str) -> None:
        """Unregister a protocol.

        Args:
            protocol_id: Protocol identifier to unregister

        Raises:
            KeyError: If protocol not found
        """
        if protocol_id not in self._protocols:
            raise KeyError(f"Protocol {protocol_id} not found")

        del self._protocols[protocol_id]
        logger.info(f"Unregistered protocol: {protocol_id}")

    def get(self, protocol_id: str) -> Type[BaseProtocol]:
        """Get a protocol class by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol class

        Raises:
            KeyError: If protocol not found
        """
        if protocol_id not in self._protocols:
            raise KeyError(f"Protocol {protocol_id} not found")

        return self._protocols[protocol_id]

    def list_protocols(self) -> List[str]:
        """List all registered protocol IDs.

        Returns:
            List of protocol identifiers
        """
        return list(self._protocols.keys())

    def get_all(self) -> Dict[str, Type[BaseProtocol]]:
        """Get all registered protocols.

        Returns:
            Dictionary mapping protocol IDs to classes
        """
        return self._protocols.copy()

    def instantiate(self, protocol_id: str, **kwargs) -> BaseProtocol:
        """Instantiate a protocol by ID.

        Args:
            protocol_id: Protocol identifier
            **kwargs: Additional arguments to pass to protocol constructor

        Returns:
            Protocol instance

        Raises:
            KeyError: If protocol not found
        """
        protocol_class = self.get(protocol_id)
        instance = protocol_class(**kwargs)
        logger.info(f"Instantiated protocol: {protocol_id}")
        return instance


# Global registry instance
_registry = ProtocolRegistry()


def get_protocol(protocol_id: str) -> Type[BaseProtocol]:
    """Get a protocol class from the global registry.

    Args:
        protocol_id: Protocol identifier

    Returns:
        Protocol class
    """
    return _registry.get(protocol_id)


def list_protocols() -> List[str]:
    """List all registered protocols.

    Returns:
        List of protocol identifiers
    """
    return _registry.list_protocols()


def register_protocol(protocol_id: str, protocol_class: Type[BaseProtocol]) -> None:
    """Register a protocol in the global registry.

    Args:
        protocol_id: Unique protocol identifier
        protocol_class: Protocol class
    """
    _registry.register(protocol_id, protocol_class)
