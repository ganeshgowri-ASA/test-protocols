"""
Pytest Configuration and Fixtures
Shared test fixtures and configuration
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from database.session import DatabaseManager
from database.models import Protocol, Module, TestExecution
from protocols.environmental.h2s_001 import H2S001Protocol


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    db_manager = DatabaseManager(db_url)
    db_manager.init_db()

    yield db_manager

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def db_session(temp_db):
    """Get a database session for testing"""
    with temp_db.session_scope() as session:
        yield session


@pytest.fixture
def sample_protocol_path():
    """Get path to sample H2S-001 protocol JSON"""
    return Path(__file__).parent.parent / "protocols" / "environmental" / "P37-54_H2S-001.json"


@pytest.fixture
def h2s_protocol(sample_protocol_path):
    """Create H2S-001 protocol instance"""
    return H2S001Protocol(sample_protocol_path)


@pytest.fixture
def sample_module_info():
    """Sample module information for testing"""
    return {
        "module_id": "TEST-001",
        "manufacturer": "Test Manufacturer",
        "model": "TEST-MODEL-100",
        "technology": "mono-Si",
        "nameplate_power": 400.0,
        "serial_number": "SN123456",
        "test_date": datetime.now().isoformat(),
        "operator": "Test Operator",
        "severity_level": 2
    }


@pytest.fixture
def sample_electrical_data():
    """Sample electrical measurement data"""
    return {
        "baseline": {
            "voc": 47.5,
            "isc": 10.8,
            "vmp": 39.2,
            "imp": 10.2,
            "pmax": 400.0,
            "ff": 0.78
        },
        "post_test": {
            "voc": 47.2,
            "isc": 10.6,
            "vmp": 38.8,
            "imp": 10.0,
            "pmax": 388.0,
            "ff": 0.77
        }
    }


@pytest.fixture
def sample_environmental_data():
    """Sample environmental log data"""
    return [
        {
            "timestamp": datetime(2025, 11, 14, 10, 0),
            "h2s_ppm": 10.2,
            "temperature_c": 40.5,
            "humidity_rh": 85.2
        },
        {
            "timestamp": datetime(2025, 11, 14, 10, 15),
            "h2s_ppm": 10.1,
            "temperature_c": 40.3,
            "humidity_rh": 84.8
        },
        {
            "timestamp": datetime(2025, 11, 14, 10, 30),
            "h2s_ppm": 9.8,
            "temperature_c": 40.2,
            "humidity_rh": 85.5
        }
    ]


@pytest.fixture
def populated_protocol(h2s_protocol, sample_module_info, sample_electrical_data):
    """Protocol with sample data populated"""
    protocol = h2s_protocol
    protocol.set_module_info(sample_module_info)

    # Add baseline measurements
    baseline = sample_electrical_data["baseline"]
    protocol.record_baseline_electrical(
        baseline["voc"], baseline["isc"], baseline["vmp"],
        baseline["imp"], baseline["pmax"], baseline["ff"]
    )

    # Add post-test measurements
    post = sample_electrical_data["post_test"]
    protocol.record_post_test_electrical(
        post["voc"], post["isc"], post["vmp"],
        post["imp"], post["pmax"], post["ff"]
    )

    # Add insulation measurements
    protocol.record_insulation_resistance(500.0, 480.0)

    # Add weight measurements
    protocol.record_weight_measurements(22.5, 22.6)

    return protocol
