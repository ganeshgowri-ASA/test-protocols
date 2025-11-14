"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_iv_data():
    """Generate sample IV curve data for testing."""
    # Single IV curve at STC (1000 W/m², 25°C)
    voc = 45.0
    isc = 10.0
    voltages = np.linspace(0, voc, 50)
    currents = isc * (1 - (voltages / voc) ** 1.2)

    data = pd.DataFrame(
        {
            "irradiance": 1000,
            "module_temp": 25,
            "ambient_temp": 20,
            "voltage": voltages,
            "current": currents,
            "module_area": 1.65,
            "rated_power": 300,
        }
    )

    return data


@pytest.fixture
def sample_multi_condition_data():
    """Generate sample data with multiple test conditions."""
    irradiances = [100, 200, 400, 600, 800, 1000]
    temperatures = [15, 25, 50, 75]

    data_points = []

    for irr in irradiances:
        for temp in temperatures:
            # Generate IV curve
            voc = 45 - (temp - 25) * 0.15
            isc = irr / 1000 * 10

            voltages = np.linspace(0, voc, 30)

            for v in voltages:
                i = isc * (1 - (v / voc) ** 1.2)

                data_points.append(
                    {
                        "irradiance": irr,
                        "module_temp": temp,
                        "ambient_temp": temp - 20,
                        "voltage": round(v, 2),
                        "current": round(max(0, i), 3),
                        "module_area": 1.65,
                        "rated_power": 300,
                    }
                )

    return pd.DataFrame(data_points)


@pytest.fixture
def protocols_dir():
    """Create temporary protocols directory for testing."""
    temp_dir = tempfile.mkdtemp()
    protocols_path = Path(temp_dir) / "protocols"
    protocols_path.mkdir()

    # Copy protocol files to temp directory
    project_root = Path(__file__).parent.parent
    source_protocols = project_root / "protocols"

    if source_protocols.exists():
        for file in source_protocols.glob("*.json"):
            shutil.copy(file, protocols_path)

    yield protocols_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_database():
    """Create temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    yield f"sqlite:///{db_path}"

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def protocol_config():
    """Sample protocol configuration."""
    return {
        "protocol_id": "TEST-001",
        "version": "1.0.0",
        "name": "Test Protocol",
        "category": "performance",
        "description": "Test protocol for unit testing",
        "metadata": {
            "author": "Test Author",
            "created_date": "2025-01-01",
            "standards": ["TEST-STANDARD-001"],
            "equipment_required": ["Test equipment"],
        },
        "test_conditions": {
            "irradiance_levels": {"values": [100, 500, 1000]},
            "temperature_matrix": {"values": [25, 50, 75]},
        },
        "parameters": [
            {
                "id": "voltage",
                "name": "Voltage",
                "type": "float",
                "unit": "V",
                "required": True,
                "validation": {"min": 0, "max": 100},
            },
            {
                "id": "current",
                "name": "Current",
                "type": "float",
                "unit": "A",
                "required": True,
                "validation": {"min": 0, "max": 20},
            },
        ],
        "outputs": [
            {
                "id": "power",
                "name": "Power",
                "type": "float",
                "unit": "W",
                "calculation": "voltage * current",
            }
        ],
        "quality_checks": [
            {
                "id": "qc_001",
                "name": "Test QC",
                "type": "threshold",
                "parameter": "voltage",
                "condition": "std_dev < 5%",
                "severity": "warning",
            }
        ],
        "charts": [],
        "report_sections": ["summary", "analysis"],
    }
