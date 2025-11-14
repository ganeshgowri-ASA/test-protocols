"""Degradation test protocols."""

from pathlib import Path
from protocols.base import Protocol

# Load UVID-001 protocol
UVID_001_PATH = Path(__file__).parent / "uvid_001.json"


def load_uvid_001() -> Protocol:
    """Load the UVID-001 UV degradation protocol.

    Returns:
        Protocol instance for UVID-001
    """
    return Protocol(UVID_001_PATH)


__all__ = ['load_uvid_001', 'UVID_001_PATH']
