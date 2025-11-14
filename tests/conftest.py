"""Pytest configuration and fixtures for test suite"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from protocols.environmental.hf_001 import HumidityFreezeProtocol
from database.models import Base
from database.connection import get_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def protocol_instance():
    """Create HF-001 protocol instance for testing"""
    protocol = HumidityFreezeProtocol()
    return protocol


@pytest.fixture
def sample_data():
    """Sample module data for testing"""
    return {
        'module_serial': 'TEST-MODULE-001',
        'manufacturer': 'Test Solar Inc.',
        'model': 'TS-300-60',
        'rated_power': 300.0,
        'voc': 45.5,
        'isc': 9.2
    }


@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    # Use in-memory SQLite for testing
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:', echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_iv_curve_data():
    """Mock I-V curve measurement data"""
    import numpy as np

    Voc = 45.5
    Isc = 9.2
    voltage = np.linspace(0, Voc, 100)
    current = Isc * (1 - np.exp((voltage / Voc - 1) / 0.06))

    power = voltage * current
    max_idx = np.argmax(power)

    return {
        'timestamp': datetime.now(),
        'irradiance': 1000.0,
        'module_temp': 25.0,
        'voltage': voltage.tolist(),
        'current': current.tolist(),
        'Voc': float(Voc),
        'Isc': float(Isc),
        'Vmp': float(voltage[max_idx]),
        'Imp': float(current[max_idx]),
        'Pmax': float(power[max_idx]),
        'FF': float(power[max_idx] / (Voc * Isc))
    }


@pytest.fixture
def mock_cycle_data():
    """Mock cycle monitoring data"""
    from datetime import timedelta

    start_time = datetime.now()
    temperature_log = []
    humidity_log = []

    # Simulate 6-hour cycle
    for minute in range(0, 360, 5):
        timestamp = start_time + timedelta(minutes=minute)

        if minute < 240:  # High temp phase
            temp = 85.0 + ((-1) ** minute) * 0.5  # Small oscillation
            humidity = 85.0 + ((-1) ** minute) * 1.0
        else:  # Low temp phase
            temp = -40.0 + ((-1) ** minute) * 0.5
            humidity = None

        temperature_log.append((timestamp, temp))
        if humidity is not None:
            humidity_log.append((timestamp, humidity))

    return {
        'cycle_number': 1,
        'start_time': start_time,
        'end_time': start_time + timedelta(hours=6),
        'temperature_log': temperature_log,
        'humidity_log': humidity_log,
        'excursions': [],
        'status': 'completed'
    }
