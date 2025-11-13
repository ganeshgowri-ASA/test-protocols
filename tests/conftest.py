"""Pytest fixtures and configuration."""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime
import numpy as np

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_measurements():
    """Generate sample measurements for testing (0-90° in 10° steps)."""
    measurements = []

    for angle in range(0, 91, 10):
        # Simulate realistic IAM behavior
        # Power decreases with angle, following approximate cosine relationship
        angle_rad = np.radians(angle)
        iam_effect = 1.0 - 0.05 * (1.0 / np.cos(angle_rad) - 1.0) if angle < 90 else 0.1

        # Base values at 0°
        isc_base = 10.0
        voc_base = 48.0
        pmax_base = 400.0

        # Apply angle effect
        isc = isc_base * iam_effect * np.cos(angle_rad)
        voc = voc_base * (1.0 - 0.002 * angle)  # Slight voltage decrease
        pmax = pmax_base * iam_effect * np.cos(angle_rad)

        # Fill factor
        ff = (pmax / (isc * voc)) if (isc * voc) > 0 else 0.75

        # Current and voltage at max power
        imp = pmax / voc if voc > 0 else 0
        vmp = pmax / imp if imp > 0 else 0

        measurements.append({
            "angle": float(angle),
            "isc": float(isc),
            "voc": float(voc),
            "pmax": float(pmax),
            "imp": float(imp),
            "vmp": float(vmp),
            "ff": float(ff),
            "irradiance_actual": 1000.0,
            "temperature_actual": 25.0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    return measurements


@pytest.fixture
def sample_protocol_data(sample_measurements):
    """Generate complete sample protocol data."""
    return {
        "protocol_info": {
            "protocol_id": "IAM-001",
            "protocol_version": "1.0.0",
            "standard": "IEC 61853",
            "test_date": datetime.utcnow().isoformat() + "Z",
            "operator": "Test Operator",
            "facility": "Test Lab"
        },
        "sample_info": {
            "sample_id": "TEST-001",
            "module_type": "Mono-Si 400W",
            "manufacturer": "Test Manufacturer",
            "serial_number": "SN12345",
            "technology": "mono-Si",
            "rated_power": 400.0,
            "area": 2.0
        },
        "test_configuration": {
            "angle_range": {
                "min": 0,
                "max": 90
            },
            "angle_step": 10,
            "irradiance": 1000,
            "temperature": 25,
            "spectrum": "AM1.5G"
        },
        "measurements": sample_measurements,
        "metadata": {
            "equipment": {
                "simulator": "Test Simulator",
                "iv_tracer": "Test Tracer"
            },
            "environmental_conditions": {
                "ambient_temperature": 25,
                "relative_humidity": 50
            }
        }
    }


@pytest.fixture
def protocol_schema():
    """Load protocol schema."""
    schema_path = Path(__file__).parent.parent / "protocols" / "iam-001" / "schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)


@pytest.fixture
def protocol_config():
    """Load protocol configuration."""
    config_path = Path(__file__).parent.parent / "protocols" / "iam-001" / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)


@pytest.fixture
def protocol_template():
    """Load protocol template."""
    template_path = Path(__file__).parent.parent / "protocols" / "iam-001" / "template.json"
    with open(template_path, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_iam_curve():
    """Generate sample IAM curve data."""
    iam_curve = []

    for angle in range(0, 91, 10):
        angle_rad = np.radians(angle)
        # Simple ASHRAE model with b0 = 0.05
        iam = 1.0 - 0.05 * (1.0 / np.cos(angle_rad) - 1.0) if angle < 90 else 0.1
        iam = max(0.0, min(1.0, iam))

        iam_curve.append({
            "angle": float(angle),
            "iam": float(iam)
        })

    return iam_curve
