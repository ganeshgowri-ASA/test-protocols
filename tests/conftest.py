"""Pytest Configuration and Fixtures

Shared fixtures for protocol testing.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from protocols.environmental.hot_001 import HotSpotEnduranceProtocol
from database.connection import Base, engine, SessionLocal
from database.models import Protocol, TestRun, Equipment


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Get database session for tests"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_iv_data():
    """Generate sample I-V curve data"""
    voc = 40.0
    isc = 9.0
    num_points = 100

    voltage = np.linspace(0, voc, num_points)
    current = isc * (1 - voltage / voc) ** 1.5

    return {
        'voltage': voltage,
        'current': current,
        'voc': voc,
        'isc': isc,
        'irradiance': 1000.0,
        'temperature': 25.0
    }


@pytest.fixture
def sample_iv_data_degraded():
    """Generate sample degraded I-V curve data (3% power loss)"""
    voc = 40.0 * 0.98  # 2% Voc drop
    isc = 9.0 * 0.97   # 3% Isc drop
    num_points = 100

    voltage = np.linspace(0, voc, num_points)
    current = isc * (1 - voltage / voc) ** 1.5

    return {
        'voltage': voltage,
        'current': current,
        'voc': voc,
        'isc': isc,
        'irradiance': 1000.0,
        'temperature': 25.0
    }


@pytest.fixture
def sample_temperature_profile():
    """Generate sample temperature profile for hot spot test"""
    start_time = datetime.now()
    num_points = 120  # 2-minute intervals for 4 hours
    target_temp = 85.0

    timestamps = [start_time + timedelta(minutes=i*2) for i in range(num_points)]
    # Simulate temperature ramp-up and stabilization
    temps = [
        25 + (target_temp - 25) * (1 - np.exp(-i / 20)) + np.random.normal(0, 0.5)
        for i in range(num_points)
    ]

    return list(zip(timestamps, temps))


@pytest.fixture
def hot_spot_protocol():
    """Create HOT-001 protocol instance"""
    return HotSpotEnduranceProtocol()


@pytest.fixture
def module_info():
    """Sample module information"""
    return {
        'module_serial_number': 'TEST-MODULE-001',
        'module_manufacturer': 'Test Solar Inc.',
        'module_model': 'TEST-300W-MONO',
        'nameplate_power': 300.0,
        'operator_name': 'Test Operator',
        'test_facility': 'Test Lab'
    }


@pytest.fixture
def sample_defects_minor():
    """Sample minor defects list"""
    return [
        {
            'type': 'Discoloration',
            'description': 'Slight yellowing at junction box'
        }
    ]


@pytest.fixture
def sample_defects_major():
    """Sample major defects list"""
    return [
        {
            'type': 'Crack',
            'description': 'Cell crack in position A5'
        },
        {
            'type': 'Melting',
            'description': 'Backsheet melting at hot spot location'
        }
    ]


@pytest.fixture
def temp_directory():
    """Create temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def protocol_json_path(tmp_path):
    """Create temporary protocol JSON file"""
    json_path = tmp_path / "hot-001.json"
    # Copy from actual template
    template_path = Path(__file__).parent.parent / "templates" / "protocols" / "hot-001.json"
    if template_path.exists():
        shutil.copy(template_path, json_path)
    return str(json_path)


@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed for reproducible tests"""
    np.random.seed(42)
    yield
