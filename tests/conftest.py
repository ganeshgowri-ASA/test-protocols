"""Pytest configuration and fixtures for test protocol tests."""

import pytest
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.base import Protocol, ProtocolRegistry
from protocols.degradation import UVID_001_PATH


@pytest.fixture
def uvid_001_protocol():
    """Fixture providing UVID-001 protocol instance."""
    return Protocol(UVID_001_PATH)


@pytest.fixture
def protocol_registry():
    """Fixture providing a fresh protocol registry."""
    return ProtocolRegistry()


@pytest.fixture
def sample_test_parameters():
    """Fixture providing sample test parameters for UVID-001."""
    return {
        'uv_irradiance': 1.0,
        'chamber_temperature': 60.0,
        'exposure_duration': 1000,
        'measurement_interval': 250,
        'relative_humidity': 50.0
    }


@pytest.fixture
def sample_initial_measurements():
    """Fixture providing sample initial measurements."""
    return {
        'pmax': 250.5,
        'voc': 38.2,
        'isc': 8.95,
        'vmp': 31.5,
        'imp': 7.95,
        'fill_factor': 73.2,
        'efficiency': 16.8
    }


@pytest.fixture
def sample_final_measurements_pass():
    """Fixture providing sample final measurements that pass criteria."""
    return {
        'pmax': 241.2,  # 96.3% retention - PASS
        'voc': 37.8,    # 98.9% retention - PASS
        'isc': 8.78,    # 98.1% retention - PASS
        'vmp': 31.1,
        'imp': 7.76,
        'fill_factor': 71.8,  # 98.1% retention - PASS
        'efficiency': 16.2    # 96.4% retention - PASS
    }


@pytest.fixture
def sample_final_measurements_fail():
    """Fixture providing sample final measurements that fail criteria."""
    return {
        'pmax': 230.0,  # 91.8% retention - FAIL (< 95%)
        'voc': 37.0,    # 96.9% retention - PASS
        'isc': 8.50,    # 95.0% retention - PASS
        'vmp': 30.5,
        'imp': 7.54,
        'fill_factor': 70.0,  # 95.6% retention - PASS
        'efficiency': 15.4    # 91.7% retention - FAIL (< 95%)
    }


@pytest.fixture
def sample_test_execution():
    """Fixture providing sample test execution data."""
    return {
        'test_number': 'UVID-001-2025-001',
        'specimen_code': 'MOD-12345',
        'specimen_type': 'PV Module',
        'operator_name': 'John Doe',
        'operator_id': 'jdoe',
        'start_datetime': datetime(2025, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2025, 2, 12, 17, 0, 0),
        'test_parameters': {
            'uv_irradiance': 1.0,
            'chamber_temperature': 60.0,
            'exposure_duration': 1000,
            'relative_humidity': 50.0
        }
    }


@pytest.fixture
def sample_measurement_series():
    """Fixture providing a time series of measurements."""
    return [
        {
            'timestamp': datetime(2025, 1, 1, 9, 0, 0),
            'pmax': 250.5,
            'voc': 38.2,
            'isc': 8.95
        },
        {
            'timestamp': datetime(2025, 1, 11, 9, 0, 0),
            'pmax': 248.2,
            'voc': 38.1,
            'isc': 8.91
        },
        {
            'timestamp': datetime(2025, 1, 21, 9, 0, 0),
            'pmax': 245.8,
            'voc': 38.0,
            'isc': 8.86
        },
        {
            'timestamp': datetime(2025, 2, 1, 9, 0, 0),
            'pmax': 243.5,
            'voc': 37.9,
            'isc': 8.82
        },
        {
            'timestamp': datetime(2025, 2, 12, 17, 0, 0),
            'pmax': 241.2,
            'voc': 37.8,
            'isc': 8.78
        }
    ]


@pytest.fixture
def sample_temperature_readings():
    """Fixture providing sample temperature readings."""
    return [
        {'timestamp': datetime(2025, 1, 1, i), 'temperature': 60.0 + (i % 3) * 0.3}
        for i in range(24)
    ]


@pytest.fixture
def sample_irradiance_readings():
    """Fixture providing sample irradiance readings."""
    return [
        {'timestamp': datetime(2025, 1, 1, i), 'irradiance': 1.0 + (i % 5) * 0.02}
        for i in range(24)
    ]
