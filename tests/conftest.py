"""Pytest configuration and fixtures"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.core.protocol_validator import load_protocol_definition
from protocols.implementations.backsheet_chalking import BacksheetChalkingProtocol


@pytest.fixture
def protocol_definition():
    """Load CHALK-001 protocol definition"""
    protocol_path = (
        Path(__file__).parent.parent
        / "protocols"
        / "templates"
        / "backsheet_chalking"
        / "protocol.json"
    )
    return load_protocol_definition(str(protocol_path))


@pytest.fixture
def protocol_schema():
    """Load CHALK-001 protocol schema"""
    schema_path = (
        Path(__file__).parent.parent
        / "protocols"
        / "templates"
        / "backsheet_chalking"
        / "schema.json"
    )
    with open(schema_path, "r") as f:
        return json.load(f)


@pytest.fixture
def chalking_protocol(protocol_definition):
    """Create BacksheetChalkingProtocol instance"""
    return BacksheetChalkingProtocol(protocol_definition)


@pytest.fixture
def sample_info():
    """Sample information for testing"""
    return {
        "sample_id": "TEST-001",
        "module_type": "Monocrystalline 400W",
        "backsheet_material": "PET",
        "backsheet_manufacturer": "Test Manufacturer",
        "exposure_duration": 5000,
        "exposure_type": "Field",
    }


@pytest.fixture
def test_conditions():
    """Test conditions for testing"""
    return {
        "temperature": 25.0,
        "humidity": 50.0,
        "test_date": "2025-11-14",
        "test_start_time": "09:00:00",
        "operator_id": "OP-001",
        "measurement_locations": 9,
        "tape_type": "ASTM_Standard",
        "tape_lot_number": "LOT-12345",
    }


@pytest.fixture
def sample_measurements():
    """Sample measurement data"""
    return [
        {
            "location_id": "LOC-01",
            "chalking_rating": 2.0,
            "location_x": 100.0,
            "location_y": 100.0,
            "visual_observations": "Slight chalking observed",
        },
        {
            "location_id": "LOC-02",
            "chalking_rating": 2.5,
            "location_x": 500.0,
            "location_y": 100.0,
            "visual_observations": "Moderate chalking",
        },
        {
            "location_id": "LOC-03",
            "chalking_rating": 1.5,
            "location_x": 900.0,
            "location_y": 100.0,
            "visual_observations": "Minimal chalking",
        },
        {
            "location_id": "LOC-04",
            "chalking_rating": 3.0,
            "location_x": 100.0,
            "location_y": 500.0,
            "visual_observations": "Noticeable chalking",
        },
        {
            "location_id": "LOC-05",
            "chalking_rating": 2.0,
            "location_x": 500.0,
            "location_y": 500.0,
            "visual_observations": "Slight chalking",
        },
        {
            "location_id": "LOC-06",
            "chalking_rating": 2.5,
            "location_x": 900.0,
            "location_y": 500.0,
            "visual_observations": "Moderate chalking",
        },
        {
            "location_id": "LOC-07",
            "chalking_rating": 1.0,
            "location_x": 100.0,
            "location_y": 900.0,
            "visual_observations": "Very minimal chalking",
        },
        {
            "location_id": "LOC-08",
            "chalking_rating": 2.0,
            "location_x": 500.0,
            "location_y": 900.0,
            "visual_observations": "Slight chalking",
        },
        {
            "location_id": "LOC-09",
            "chalking_rating": 2.5,
            "location_x": 900.0,
            "location_y": 900.0,
            "visual_observations": "Moderate chalking",
        },
    ]


@pytest.fixture
def passing_measurements():
    """Measurements that should result in PASS"""
    return [
        {"location_id": f"LOC-{i:02d}", "chalking_rating": 1.5 + i * 0.1, "location_x": float(i * 100), "location_y": 100.0}
        for i in range(1, 10)
    ]


@pytest.fixture
def failing_measurements():
    """Measurements that should result in FAIL"""
    return [
        {"location_id": f"LOC-{i:02d}", "chalking_rating": 6.0 + i * 0.5, "location_x": float(i * 100), "location_y": 100.0}
        for i in range(1, 10)
    ]


@pytest.fixture
def warning_measurements():
    """Measurements that should result in WARNING"""
    return [
        {"location_id": f"LOC-{i:02d}", "chalking_rating": 3.5 + i * 0.1, "location_x": float(i * 100), "location_y": 100.0}
        for i in range(1, 10)
    ]
