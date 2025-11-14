"""
Pytest configuration and fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from src.models import Base, Sample, Equipment, Protocol, ProtocolVersion


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    # Use in-memory SQLite for testing
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for a test"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_data(db_session):
    """Create test sample data"""
    sample = Sample(
        sample_id="TEST-001",
        serial_number="SN123456",
        module_type="Monocrystalline",
        rated_power_pmax=400.0,
        rated_voltage_vmp=40.0,
        rated_current_imp=10.0,
        open_circuit_voltage_voc=48.0,
        short_circuit_current_isc=10.5,
        max_overcurrent_protection=15.0,
        is_active=True
    )
    db_session.add(sample)
    db_session.commit()
    db_session.refresh(sample)
    return sample


@pytest.fixture
def equipment_data(db_session):
    """Create test equipment data"""
    equipment = Equipment(
        equipment_id="EQ-001",
        name="Test Ground Continuity Tester",
        equipment_type="Ground Continuity Tester",
        manufacturer="Test Manufacturer",
        model="TC-1000",
        serial_number="EQ123456",
        calibration_required=True,
        is_active=True
    )
    db_session.add(equipment)
    db_session.commit()
    db_session.refresh(equipment)
    return equipment
