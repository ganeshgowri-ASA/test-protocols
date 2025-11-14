"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import json
import tempfile
from datetime import datetime

@pytest.fixture
def sample_lid001_protocol():
    """Load LID-001 protocol definition."""
    protocol_file = Path(__file__).parent.parent / "protocols" / "definitions" / "LID-001.json"
    with open(protocol_file, 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_measurements():
    """Generate sample measurement data."""
    measurements = []

    # Initial measurements
    for i in range(3):
        measurements.append({
            "measurement_sequence": i + 1,
            "measurement_type": "initial",
            "timestamp": datetime.now(),
            "elapsed_hours": -0.5 + i * 0.5,
            "voc": 40.5,
            "isc": 9.2,
            "pmax": 300.0,
            "vmp": 33.0,
            "imp": 9.09,
            "fill_factor": 0.806,
            "irradiance": 1000.0,
            "temperature": 25.0,
        })

    # During exposure measurements with degradation
    degradation_values = [0.5, 1.0, 1.5, 2.0, 2.3, 2.5, 2.6, 2.7]
    times = [0.5, 1.0, 2.0, 4.0, 8.0, 24.0, 48.0, 72.0]

    for i, (time, deg) in enumerate(zip(times, degradation_values)):
        pmax = 300.0 * (1 - deg / 100)
        measurements.append({
            "measurement_sequence": i + 4,
            "measurement_type": "during_exposure",
            "timestamp": datetime.now(),
            "elapsed_hours": time,
            "voc": 40.5 * (1 - deg / 200),  # Voc degrades less
            "isc": 9.2 * (1 - deg / 150),   # Isc degrades less
            "pmax": pmax,
            "vmp": 33.0 * (1 - deg / 100),
            "imp": pmax / 33.0,
            "fill_factor": 0.806 * (1 - deg / 300),
            "irradiance": 1000.0,
            "temperature": 25.0,
        })

    return measurements


@pytest.fixture
def temp_database():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_qc_config():
    """Load QC configuration."""
    config_file = Path(__file__).parent.parent / "config" / "qc_rules.yaml"
    import yaml
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
