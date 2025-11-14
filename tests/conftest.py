"""PyTest configuration and fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import SessionManager
from database.models import Base
from utils.config import Config


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    config = Config()
    config.load()
    # Override for testing
    config.set('database.type', 'sqlite')
    config.set('database.path', ':memory:')
    return config


@pytest.fixture(scope="function")
def db_session(test_config):
    """Create a test database session."""
    # Initialize database manager
    manager = SessionManager()
    manager.initialize('sqlite:///:memory:')
    manager.create_tables()

    # Create session
    session = manager.get_session()

    yield session

    # Cleanup
    session.close()
    manager.drop_tables()


@pytest.fixture
def sample_wet001_params():
    """Sample valid parameters for WET-001 protocol."""
    return {
        "sample_information": {
            "sample_id": "TEST-001",
            "module_type": "Monocrystalline 400W",
            "manufacturer": "Test Solar Corp",
            "serial_number": "SN123456",
            "rated_power": 400.0,
        },
        "test_conditions": {
            "test_voltage": 1500.0,
            "electrode_configuration": "A",
            "test_duration": 168.0,
            "measurement_interval": 60.0,
            "polarity": "positive",
        },
        "environmental_conditions": {
            "temperature": 25.0,
            "temperature_tolerance": 5.0,
            "relative_humidity": 90.0,
            "humidity_tolerance": 5.0,
            "barometric_pressure": 101.3,
        },
        "acceptance_criteria": {
            "max_leakage_current": 0.25,
            "min_insulation_resistance": 400.0,
            "max_voltage_variation": 5.0,
            "no_surface_tracking": True,
            "no_visible_damage": True,
        }
    }


@pytest.fixture
def sample_measurements():
    """Generate sample measurement data."""
    from datetime import datetime, timedelta
    from protocols.base import MeasurementPoint

    measurements = []
    start_time = datetime.now()

    # Generate 10 measurement points
    for i in range(10):
        timestamp = start_time + timedelta(minutes=i * 60)
        measurement = MeasurementPoint(
            timestamp=timestamp,
            values={
                'leakage_current': 0.15 + (i * 0.01),  # Increasing slightly
                'voltage': 1500.0,
                'temperature': 25.0 + (i * 0.1),
                'humidity': 90.0,
                'insulation_resistance': 600.0 - (i * 10),  # Decreasing slightly
            },
            notes=None
        )
        measurements.append(measurement)

    return measurements
