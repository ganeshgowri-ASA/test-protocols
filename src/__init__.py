"""
PV Test Protocol Framework

A modular framework for photovoltaic testing protocols with JSON-based
definitions, automated analysis, and integrated reporting.
"""

__version__ = "1.0.0"
__author__ = "GenSpark Labs"

from .protocols.base import (
    BaseProtocol,
    ProtocolDefinition,
    ProtocolResult,
    ProtocolStatus,
    SampleMetadata,
    protocol_registry
)

__all__ = [
    'BaseProtocol',
    'ProtocolDefinition',
    'ProtocolResult',
    'ProtocolStatus',
    'SampleMetadata',
    'protocol_registry'
]
