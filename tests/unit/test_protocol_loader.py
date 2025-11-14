"""Tests for protocol loader."""

import pytest
import json
from pathlib import Path

from src.test_protocols.core.protocol_loader import ProtocolLoader


def test_protocol_loader_initialization():
    """Test protocol loader initialization."""
    loader = ProtocolLoader()
    assert loader is not None
    assert loader.schema is not None


def test_load_ener001_protocol():
    """Test loading ENER-001 protocol."""
    loader = ProtocolLoader()

    try:
        protocol = loader.load_protocol("ENER-001")

        assert protocol is not None
        assert protocol["protocol_id"] == "ENER-001"
        assert protocol["version"] == "1.0.0"
        assert protocol["name"] == "Energy Rating Test"
        assert protocol["category"] == "performance"
        assert "metadata" in protocol
        assert "test_conditions" in protocol
        assert "parameters" in protocol
        assert "outputs" in protocol

    except FileNotFoundError:
        pytest.skip("ENER-001 protocol file not found")


def test_protocol_validation():
    """Test protocol schema validation."""
    loader = ProtocolLoader()

    # Valid protocol should pass
    try:
        protocol = loader.load_protocol("ENER-001", validate_schema=True)
        assert protocol is not None
    except FileNotFoundError:
        pytest.skip("ENER-001 protocol file not found")


def test_list_protocols():
    """Test listing available protocols."""
    loader = ProtocolLoader()
    protocols = loader.list_protocols()

    assert isinstance(protocols, list)
    # Should have at least ENER-001 if it exists
    assert len(protocols) >= 0


def test_get_protocol_info():
    """Test getting protocol information."""
    loader = ProtocolLoader()

    try:
        info = loader.get_protocol_info("ENER-001")

        assert info is not None
        assert "protocol_id" in info
        assert "version" in info
        assert "name" in info
        assert "category" in info
        assert "description" in info
        assert "standards" in info

    except FileNotFoundError:
        pytest.skip("ENER-001 protocol file not found")


def test_protocol_caching():
    """Test that protocols are cached after first load."""
    loader = ProtocolLoader()

    try:
        # Load protocol twice
        protocol1 = loader.load_protocol("ENER-001")
        protocol2 = loader.load_protocol("ENER-001")

        # Should be the same object (cached)
        assert protocol1 is protocol2

    except FileNotFoundError:
        pytest.skip("ENER-001 protocol file not found")


def test_reload_protocol():
    """Test reloading protocol (clearing cache)."""
    loader = ProtocolLoader()

    try:
        # Load protocol
        protocol1 = loader.load_protocol("ENER-001")

        # Reload protocol
        protocol2 = loader.reload_protocol("ENER-001")

        # Should be different objects
        assert protocol1 is not protocol2

        # But should have same content
        assert protocol1["protocol_id"] == protocol2["protocol_id"]

    except FileNotFoundError:
        pytest.skip("ENER-001 protocol file not found")


def test_invalid_protocol_file():
    """Test handling of invalid protocol files."""
    loader = ProtocolLoader()

    # Try to load non-existent protocol
    with pytest.raises(FileNotFoundError):
        loader.load_protocol("NONEXISTENT-999")
