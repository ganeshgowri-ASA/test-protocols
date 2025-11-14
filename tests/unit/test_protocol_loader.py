"""Unit tests for protocol loader."""

import pytest
from src.core.protocol_loader import ProtocolLoader


def test_protocol_loader_init(protocol_loader):
    """Test ProtocolLoader initialization."""
    assert protocol_loader is not None
    assert protocol_loader.schema is not None


def test_load_bypass_protocol(bypass_protocol):
    """Test loading bypass diode testing protocol."""
    assert bypass_protocol is not None
    assert "protocol" in bypass_protocol
    assert bypass_protocol["protocol"]["id"] == "bypass-diode-testing-v1"
    assert bypass_protocol["protocol"]["code"] == "BYPASS-001"


def test_protocol_has_required_fields(bypass_protocol):
    """Test that protocol has all required fields."""
    protocol = bypass_protocol["protocol"]

    assert "id" in protocol
    assert "name" in protocol
    assert "version" in protocol
    assert "test_phases" in protocol
    assert len(protocol["test_phases"]) > 0


def test_protocol_phases_structure(bypass_protocol):
    """Test that protocol phases have correct structure."""
    phases = bypass_protocol["protocol"]["test_phases"]

    for phase in phases:
        assert "phase_id" in phase
        assert "name" in phase
        assert "sequence" in phase
        assert phase["sequence"] >= 1


def test_list_protocols(protocol_loader):
    """Test listing available protocols."""
    protocols = protocol_loader.list_protocols()

    assert isinstance(protocols, list)
    if len(protocols) > 0:
        protocol = protocols[0]
        assert "id" in protocol
        assert "name" in protocol
        assert "version" in protocol


def test_get_protocol_metadata(protocol_loader):
    """Test getting protocol metadata."""
    metadata = protocol_loader.get_protocol_metadata("bypass-diode-testing")

    assert metadata is not None
    assert metadata["id"] == "bypass-diode-testing-v1"
    assert metadata["name"] == "Bypass Diode Testing Protocol"
    assert "version" in metadata


def test_load_nonexistent_protocol(protocol_loader):
    """Test loading non-existent protocol raises error."""
    with pytest.raises(FileNotFoundError):
        protocol_loader.load_protocol("nonexistent-protocol")
