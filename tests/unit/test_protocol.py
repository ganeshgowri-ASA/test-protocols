"""Unit tests for protocol engine."""

import pytest
from datetime import datetime

from src.core.protocol import ProtocolEngine, ProtocolConfig


def test_protocol_initialization(sample_protocol_config):
    """Test protocol engine initialization."""
    protocol = ProtocolEngine(sample_protocol_config)

    assert protocol.config.protocol_id == "TEST-001"
    assert protocol.config.name == "Test Protocol"
    assert protocol.status == "initialized"
    assert protocol.run_id is None


def test_protocol_validation(sample_protocol_config):
    """Test protocol configuration validation."""
    protocol = ProtocolEngine(sample_protocol_config)

    # Should validate successfully
    is_valid = protocol.validate_protocol()
    assert is_valid is True


def test_start_test_run(sample_protocol_config, test_db):
    """Test starting a test run."""
    protocol = ProtocolEngine(sample_protocol_config, db_manager=test_db)

    run_id = protocol.start_test_run(
        operator="Test Operator",
        sample_id="SAMPLE-001",
        device_id="DEVICE-001"
    )

    assert run_id is not None
    assert protocol.run_id == run_id
    assert protocol.status == "running"
    assert protocol.start_time is not None


def test_record_measurement(sample_protocol_config, test_db):
    """Test recording measurements."""
    protocol = ProtocolEngine(sample_protocol_config, db_manager=test_db)

    # Start a test run first
    protocol.start_test_run(operator="Test Operator")

    # Record measurement
    measurement_id = protocol.record_measurement(
        metric_name="test_metric",
        value=45.5,
        unit="degrees"
    )

    assert measurement_id is not None
    assert isinstance(measurement_id, int)


def test_record_measurement_without_run(sample_protocol_config, test_db):
    """Test that recording measurement without active run raises error."""
    protocol = ProtocolEngine(sample_protocol_config, db_manager=test_db)

    with pytest.raises(ValueError, match="No active test run"):
        protocol.record_measurement(
            metric_name="test_metric",
            value=45.5
        )


def test_complete_test_run(sample_protocol_config, test_db):
    """Test completing a test run."""
    protocol = ProtocolEngine(sample_protocol_config, db_manager=test_db)

    # Start and complete
    protocol.start_test_run(operator="Test Operator")
    protocol.complete_test_run()

    assert protocol.status == "completed"
    assert protocol.end_time is not None


def test_protocol_from_json(test_db):
    """Test creating protocol from JSON file."""
    json_file = "schemas/examples/track_001_example.json"

    protocol = ProtocolEngine.from_json(json_file, db_manager=test_db)

    assert protocol.config.protocol_id == "TRACK-001"
    assert protocol.config.name == "Tracker Performance Test"
