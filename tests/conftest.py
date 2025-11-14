"""Pytest configuration and fixtures."""

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from test_protocols.models.schema import Base


@pytest.fixture(scope="session")
def db_engine():
    """Create in-memory test database engine."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_salt_001_data():
    """Sample SALT-001 protocol data."""
    return {
        "specimen_id": "TEST-PV-001",
        "module_type": "Crystalline Silicon",
        "manufacturer": "Test Manufacturer",
        "rated_power": 300.0,
        "severity_level": "Level 3 - 240 hours",
        "salt_concentration": 5.0,
        "chamber_temperature": 35.0,
        "relative_humidity": 95.0,
        "spray_duration": 2.0,
        "dry_duration": 22.0,
        "iv_measurement_intervals": [0, 60, 120, 180, 240],
        "visual_inspection_intervals": [0, 24, 48, 96, 144, 192, 240],
    }


@pytest.fixture
def sample_iv_curve():
    """Sample I-V curve data."""
    return {
        "voltage": [0, 5, 10, 15, 20, 25, 30, 35, 40],
        "current": [8.5, 8.4, 8.3, 8.1, 7.5, 6.0, 3.0, 1.0, 0],
        "irradiance": 1000.0,
        "temperature": 25.0,
    }


@pytest.fixture
def protocol_template():
    """Load SALT-001 protocol template."""
    template_path = (
        Path(__file__).parent.parent / "templates" / "protocols" / "salt-001.json"
    )

    if template_path.exists():
        with open(template_path, "r") as f:
            return json.load(f)

    return {}


@pytest.fixture
def invalid_salt_001_data():
    """Invalid SALT-001 protocol data for validation testing."""
    return [
        # Missing required field
        {
            "module_type": "Crystalline Silicon",
            "salt_concentration": 5.0,
            "chamber_temperature": 35.0,
            "relative_humidity": 95.0,
        },
        # Salt concentration out of range
        {
            "specimen_id": "TEST-001",
            "severity_level": "Level 3 - 240 hours",
            "salt_concentration": 7.0,  # Invalid: too high
            "chamber_temperature": 35.0,
            "relative_humidity": 95.0,
        },
        # Temperature out of range
        {
            "specimen_id": "TEST-001",
            "severity_level": "Level 3 - 240 hours",
            "salt_concentration": 5.0,
            "chamber_temperature": 40.0,  # Invalid: too high
            "relative_humidity": 95.0,
        },
        # Humidity out of range
        {
            "specimen_id": "TEST-001",
            "severity_level": "Level 3 - 240 hours",
            "salt_concentration": 5.0,
            "chamber_temperature": 35.0,
            "relative_humidity": 80.0,  # Invalid: too low
        },
        # Invalid cycle duration
        {
            "specimen_id": "TEST-001",
            "severity_level": "Level 3 - 240 hours",
            "salt_concentration": 5.0,
            "chamber_temperature": 35.0,
            "relative_humidity": 95.0,
            "spray_duration": 3.0,
            "dry_duration": 20.0,  # Total != 24 hours
        },
    ]
