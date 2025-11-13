"""
PV Testing Protocol Framework - Protocol Definitions
"""

from typing import Dict, Any

__version__ = "1.0.0"

# Protocol registry
PROTOCOL_REGISTRY: Dict[str, Any] = {}


def register_protocol(protocol_id: str, protocol_class):
    """Register a protocol in the global registry"""
    PROTOCOL_REGISTRY[protocol_id] = protocol_class


def get_protocol(protocol_id: str):
    """Get a protocol class from the registry"""
    return PROTOCOL_REGISTRY.get(protocol_id)
