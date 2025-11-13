"""
PV Testing Protocols Package
============================
Complete collection of PV testing protocol implementations.

Categories:
- Performance (12 protocols): STC, NOCT, LIC, PERF, IAM, SPEC, TEMP, ENER, BIFI, TRACK, CONC
- Degradation (15 protocols): LID, LETID, PID, UVID, SPONGE, SNAIL, DELAM, CORR, CHALK, YELLOW, CRACK, SOLDER, JBOX, SEAL
- Environmental (12 protocols): TC, DH, HF, UV, SALT, SAND, AMMON, SO2, H2S, TROP, DESERT
- Mechanical (8 protocols): ML, HAIL, WIND, SNOW, VIBR, TWIST, TERM
- Safety (7 protocols): INSU, WET, DIEL, GROUND, HOT, BYPASS, FIRE

Total: 54 protocols

Author: GenSpark PV Testing Framework
Version: 1.0.0
"""

from .base_protocol import (
    BaseProtocol,
    ProtocolMetadata,
    ProtocolStatus,
    ValidationLevel,
    ValidationResult,
    ProtocolFactory
)

# Import all protocol categories
from . import performance
from . import degradation
from . import environmental
from . import mechanical
from . import safety

__version__ = "1.0.0"
__author__ = "GenSpark PV Testing Team"

__all__ = [
    'BaseProtocol',
    'ProtocolMetadata',
    'ProtocolStatus',
    'ValidationLevel',
    'ValidationResult',
    'ProtocolFactory',
    'performance',
    'degradation',
    'environmental',
    'mechanical',
    'safety'
]


def list_all_protocols():
    """List all available protocols"""
    return ProtocolFactory.list_protocols()


def get_protocol(protocol_id: str):
    """Get protocol instance by ID"""
    return ProtocolFactory.create(protocol_id)


def get_protocols_by_category(category: str):
    """Get all protocols in a category"""
    all_protocols = list_all_protocols()
    return [p for p in all_protocols if category.lower() in p.lower()]
