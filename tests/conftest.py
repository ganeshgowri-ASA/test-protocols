"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.protocol_loader import ProtocolLoader
from src.core.data_processor import DataProcessor, Measurement
from src.database.connection import DatabaseManager
from src.database.models import Protocol, TestRun


@pytest.fixture
def protocols_dir():
    """Return path to test protocols directory."""
    return Path(__file__).parent.parent / "src" / "protocols"


@pytest.fixture
def protocol_loader(protocols_dir):
    """Return ProtocolLoader instance."""
    return ProtocolLoader(protocols_dir)


@pytest.fixture
def bypass_protocol(protocol_loader):
    """Load bypass diode testing protocol."""
    return protocol_loader.load_protocol("bypass-diode-testing")


@pytest.fixture
def db_manager():
    """Return in-memory database manager for testing."""
    manager = DatabaseManager("sqlite:///:memory:")
    manager.init_db()
    yield manager
    manager.close()


@pytest.fixture
def sample_protocol_dict():
    """Return sample protocol dictionary."""
    return {
        "protocol": {
            "id": "test-protocol-v1",
            "name": "Test Protocol",
            "version": "1.0.0",
            "test_phases": [
                {
                    "phase_id": "p1_test",
                    "name": "Test Phase",
                    "sequence": 1,
                    "parameters": [
                        {
                            "param_id": "test_param",
                            "name": "Test Parameter",
                            "type": "float",
                            "min_value": 0,
                            "max_value": 100,
                            "required": True,
                        }
                    ],
                }
            ],
            "qc_rules": [
                {
                    "rule_id": "qc_test_range",
                    "type": "range",
                    "min_value": 10,
                    "max_value": 90,
                    "action": "flag_warning",
                    "description": "Test value out of range",
                }
            ],
        }
    }


@pytest.fixture
def sample_measurements():
    """Return sample measurements list."""
    measurements = []
    for i in range(10):
        measurements.append(
            Measurement(
                measurement_id="test_voltage",
                phase_id="p1_test",
                timestamp=datetime.now(),
                value=50.0 + i,
                unit="V",
            )
        )
    return measurements


@pytest.fixture
def data_processor(sample_protocol_dict):
    """Return DataProcessor instance with sample protocol."""
    return DataProcessor(sample_protocol_dict)
