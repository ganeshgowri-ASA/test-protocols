"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
import json


@pytest.fixture
def protocols_dir():
    """Get protocols directory."""
    return Path(__file__).parent.parent / "protocols"


@pytest.fixture
def ml_001_protocol_path(protocols_dir):
    """Get ML-001 protocol file path."""
    return protocols_dir / "mechanical_load" / "ml_001_protocol.json"


@pytest.fixture
def ml_001_protocol_data(ml_001_protocol_path):
    """Load ML-001 protocol JSON data."""
    with open(ml_001_protocol_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def schema_path():
    """Get protocol schema file path."""
    return Path(__file__).parent.parent / "src" / "test_protocols" / "schemas" / "protocol_schema.json"


@pytest.fixture
def sample_measurement_data():
    """Sample measurement data for testing."""
    return {
        "measurement_type": "applied_pressure",
        "unit": "Pa",
        "interval_seconds": 10,
        "sensor_id": "PRESSURE_01",
        "target_value": 2400,
        "tolerance": 50,
    }
