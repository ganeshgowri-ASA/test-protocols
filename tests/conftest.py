"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.models import Base, Protocol, TestRun, Measurement
from src.core.protocol_loader import ProtocolLoader


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def protocol_loader():
    """Create protocol loader instance."""
    return ProtocolLoader()


@pytest.fixture
def sample_perf002_protocol():
    """Sample PERF-002 protocol definition."""
    return {
        "protocol_id": "PERF-002",
        "version": "1.0.0",
        "name": "Performance Testing at Different Irradiances",
        "category": "Performance",
        "description": "Test protocol for irradiance testing",
        "test_configuration": {
            "irradiance_levels": [
                {"level": 100, "unit": "W/m²", "tolerance": 2},
                {"level": 200, "unit": "W/m²", "tolerance": 2},
                {"level": 400, "unit": "W/m²", "tolerance": 2},
                {"level": 600, "unit": "W/m²", "tolerance": 2},
                {"level": 800, "unit": "W/m²", "tolerance": 2},
                {"level": 1000, "unit": "W/m²", "tolerance": 2},
                {"level": 1100, "unit": "W/m²", "tolerance": 2}
            ]
        },
        "data_collection": {
            "fields": [
                {
                    "name": "irradiance",
                    "type": "float",
                    "unit": "W/m²",
                    "required": True,
                    "validation": {"min": 50, "max": 1200}
                },
                {
                    "name": "voltage",
                    "type": "float",
                    "unit": "V",
                    "required": True,
                    "validation": {"min": 0, "max": 1500}
                },
                {
                    "name": "current",
                    "type": "float",
                    "unit": "A",
                    "required": True,
                    "validation": {"min": 0, "max": 50}
                }
            ]
        },
        "analysis": {
            "calculations": [
                {"name": "pmax", "formula": "max(V * I)"},
                {"name": "efficiency", "formula": "Pmax / (Irr * Area) * 100"}
            ]
        },
        "qc_checks": [
            {
                "name": "irradiance_tolerance",
                "type": "range",
                "parameter": "irradiance",
                "tolerance_value": 2
            }
        ],
        "visualization": {
            "charts": []
        }
    }


@pytest.fixture
def sample_iv_curve():
    """Generate sample I-V curve data."""
    # Generate realistic I-V curve
    voc = 45.0  # Open circuit voltage
    isc = 9.5   # Short circuit current

    voltages = np.linspace(0, voc, 100)
    # Simplified I-V model
    currents = isc * (1 - voltages / voc) ** 0.5

    return {
        'voltages': voltages.tolist(),
        'currents': currents.tolist()
    }


@pytest.fixture
def sample_measurements():
    """Generate sample measurement data."""
    measurements = []

    irradiance_levels = [100, 200, 400, 600, 800, 1000, 1100]

    for irr in irradiance_levels:
        # Generate 5 measurements per irradiance level
        for i in range(5):
            measurements.append({
                'timestamp': f"2025-11-13T12:{i:02d}:00",
                'target_irradiance': irr,
                'irradiance': irr + np.random.uniform(-1, 1),
                'module_temperature': 25.0 + np.random.uniform(-0.5, 0.5),
                'voltage': 36.0 + np.random.uniform(-1, 1),
                'current': (irr / 1000.0) * 9.0 + np.random.uniform(-0.2, 0.2),
                'power': None,  # Will be calculated
                'position_x': (i % 5) + 1,
                'position_y': (i // 5) + 1
            })

    # Calculate power
    for m in measurements:
        m['power'] = m['voltage'] * m['current']

    return measurements


@pytest.fixture
def sample_test_run_data(sample_measurements):
    """Generate complete test run data."""
    return {
        'test_run': {
            'protocol_id': 'PERF-002',
            'run_number': 'PERF-002-2025-001',
            'operator': 'Test Operator',
            'module_serial': 'MOD-12345',
            'start_time': '2025-11-13T12:00:00',
            'ambient_temperature': 25.0,
            'ambient_humidity': 45.0
        },
        'measurements': sample_measurements
    }
