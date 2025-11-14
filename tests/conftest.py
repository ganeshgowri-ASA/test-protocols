"""
Pytest Configuration and Fixtures

Shared fixtures for all tests.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_data():
    """Sample test data."""
    return {
        'sample_id': 'EVA_TEST_001',
        'material_type': 'EVA',
        'sample_dimensions': {
            'length_mm': 100,
            'width_mm': 100,
            'thickness_mm': 3
        },
        'batch_code': 'BATCH_TEST_001'
    }


@pytest.fixture
def protocol_path():
    """Path to YELLOW-001 protocol."""
    base_path = Path(__file__).parent.parent
    return str(base_path / "protocols" / "yellow" / "YELLOW-001.json")


@pytest.fixture
def mock_baseline_measurements():
    """Mock baseline measurements."""
    return {
        'yellow_index': 0.5,
        'L_star': 95.0,
        'a_star': -0.8,
        'b_star': 0.2,
        'light_transmittance': 95.0
    }


@pytest.fixture
def mock_time_points():
    """Mock measurement time points."""
    return [
        {
            'time_point_hours': 0,
            'yellow_index': 0.5,
            'color_shift': 0.0,
            'light_transmittance': 95.0,
            'L_star': 95.0,
            'a_star': -0.8,
            'b_star': 0.2
        },
        {
            'time_point_hours': 100,
            'yellow_index': 2.3,
            'color_shift': 1.8,
            'light_transmittance': 93.5,
            'L_star': 94.2,
            'a_star': -0.6,
            'b_star': 1.5
        },
        {
            'time_point_hours': 200,
            'yellow_index': 4.1,
            'color_shift': 3.2,
            'light_transmittance': 92.0,
            'L_star': 93.5,
            'a_star': -0.4,
            'b_star': 2.8
        }
    ]
