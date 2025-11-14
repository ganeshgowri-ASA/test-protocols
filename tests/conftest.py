"""Pytest configuration and fixtures."""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import ProtocolManager, SchemaValidator, DataProcessor
from src.database.schema import DatabaseManager


@pytest.fixture
def protocol_manager():
    """Fixture for ProtocolManager instance."""
    return ProtocolManager()


@pytest.fixture
def schema_validator(protocol_manager):
    """Fixture for SchemaValidator instance."""
    return SchemaValidator(protocol_manager)


@pytest.fixture
def data_processor(protocol_manager):
    """Fixture for DataProcessor instance."""
    return DataProcessor(protocol_manager)


@pytest.fixture
def sample_conc001_data():
    """Fixture for sample CONC-001 test data."""
    return {
        "test_run_id": "CONC-001-20251114-0001",
        "sample_id": "PV-SAMPLE-001",
        "timestamp": datetime.now().isoformat(),
        "operator": "Test Operator",
        "equipment": {
            "solar_simulator_id": "SIM-001-ClassAAA",
            "reference_cell_id": "REF-CELL-001",
            "calibration_date": "2025-06-01"
        },
        "measurements": [
            {
                "concentration_suns": 1.0,
                "temperature_c": 25.0,
                "voc": 0.650,
                "isc": 8.5,
                "vmp": 0.550,
                "imp": 8.0,
                "fill_factor": 0.846,
                "efficiency": 22.5,
                "spectral_mismatch": 0.02
            },
            {
                "concentration_suns": 10.0,
                "temperature_c": 25.0,
                "voc": 0.750,
                "isc": 85.0,
                "vmp": 0.650,
                "imp": 80.0,
                "fill_factor": 0.815,
                "efficiency": 26.8,
                "spectral_mismatch": 0.02
            },
            {
                "concentration_suns": 100.0,
                "temperature_c": 25.0,
                "voc": 0.850,
                "isc": 850.0,
                "vmp": 0.750,
                "imp": 800.0,
                "fill_factor": 0.830,
                "efficiency": 31.2,
                "spectral_mismatch": 0.03
            }
        ],
        "environmental_conditions": {
            "ambient_temperature_c": 22.5,
            "humidity_percent": 45.0,
            "atmospheric_pressure_kpa": 101.3
        },
        "notes": "Test measurement - all parameters nominal"
    }


@pytest.fixture
def invalid_conc001_data():
    """Fixture for invalid CONC-001 test data."""
    return {
        "test_run_id": "INVALID-FORMAT",
        "sample_id": "",
        "measurements": []
    }


@pytest.fixture
def db_manager():
    """Fixture for in-memory database manager."""
    db = DatabaseManager("sqlite:///:memory:")
    db.create_all_tables()
    yield db
    db.close()


@pytest.fixture
def temp_protocol_dir(tmp_path):
    """Fixture for temporary protocol directory with test protocols."""
    # Create CONC-001 structure
    conc001_dir = tmp_path / "conc-001"
    conc001_dir.mkdir()

    schema_dir = conc001_dir / "schema"
    schema_dir.mkdir()

    config_dir = conc001_dir / "config"
    config_dir.mkdir()

    # Minimal schema
    schema = {
        "protocol_id": "conc-001",
        "version": "1.0.0",
        "name": "Test Protocol",
        "schema": {
            "type": "object",
            "required": ["test_run_id", "sample_id"]
        }
    }

    schema_file = schema_dir / "conc-001-schema.json"
    with open(schema_file, 'w') as f:
        json.dump(schema, f)

    return tmp_path
