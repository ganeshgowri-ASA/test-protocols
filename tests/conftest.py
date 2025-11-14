"""
PyTest Configuration and Fixtures
Common test fixtures and configuration
"""

import pytest
import os
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Protocol, TestRun


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def desert_protocol_file(test_data_dir):
    """Return path to DESERT-001 protocol file"""
    protocol_path = Path(__file__).parent.parent / "protocols" / "environmental" / "desert-001.json"
    return protocol_path


@pytest.fixture(scope="session")
def desert_protocol_data(desert_protocol_file):
    """Load DESERT-001 protocol data"""
    with open(desert_protocol_file, 'r') as f:
        return json.load(f)


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_protocol(test_db_session, desert_protocol_data):
    """Create a sample protocol in the database"""
    protocol = Protocol(
        id=desert_protocol_data['metadata']['id'],
        protocol_number=desert_protocol_data['metadata']['protocol_number'],
        name=desert_protocol_data['metadata']['name'],
        category=desert_protocol_data['metadata']['category'],
        subcategory=desert_protocol_data['metadata'].get('subcategory', ''),
        version=desert_protocol_data['metadata']['version'],
        description=desert_protocol_data['metadata']['description'],
        definition=desert_protocol_data,
        test_parameters=desert_protocol_data.get('test_parameters'),
        test_procedure=desert_protocol_data.get('test_procedure'),
        qc_checks=desert_protocol_data.get('qc_checks'),
        pass_fail_criteria=desert_protocol_data.get('pass_fail_criteria'),
        author=desert_protocol_data['metadata'].get('author')
    )

    test_db_session.add(protocol)
    test_db_session.commit()

    return protocol


@pytest.fixture
def sample_test_run(test_db_session, sample_protocol):
    """Create a sample test run in the database"""
    test_run = TestRun(
        id="test-run-001",
        protocol_id=sample_protocol.id,
        module_serial_number="MOD-12345",
        batch_id="BATCH-001",
        operator="test_operator",
        start_time=datetime.utcnow(),
        total_cycles=200,
        parameters={
            "daytime_temperature": 65,
            "nighttime_temperature": 5,
            "daytime_humidity": 15,
            "nighttime_humidity": 40,
            "uv_irradiance": 1000,
            "total_cycles": 200
        }
    )

    test_db_session.add(test_run)
    test_db_session.commit()

    return test_run


@pytest.fixture
def sample_parameters():
    """Sample test parameters for DESERT-001"""
    return {
        "daytime_temperature": 65,
        "nighttime_temperature": 5,
        "daytime_humidity": 15,
        "nighttime_humidity": 40,
        "uv_irradiance": 1000,
        "cycle_duration": 24,
        "total_cycles": 200,
        "ramp_rate": 10
    }
