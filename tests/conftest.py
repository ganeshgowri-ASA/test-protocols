"""pytest configuration and fixtures for test protocols."""

import pytest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from protocols.degradation.seal_001 import SEAL001Protocol
from core.protocol_loader import ProtocolLoader


@pytest.fixture
def protocols_dir():
    """Get protocols directory path."""
    return Path(__file__).parent.parent / 'protocols'


@pytest.fixture
def sample_protocol_json(protocols_dir):
    """Load sample SEAL-001 protocol JSON."""
    json_path = protocols_dir / 'degradation' / 'SEAL-001-edge-seal.json'
    with open(json_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def seal_001_protocol(sample_protocol_json):
    """Create SEAL-001 protocol instance."""
    return SEAL001Protocol(sample_protocol_json)


@pytest.fixture
def protocol_loader(protocols_dir):
    """Create protocol loader instance."""
    return ProtocolLoader(protocols_dir=protocols_dir)


@pytest.fixture
def mock_initial_inspection_data():
    """Mock initial inspection data."""
    return {
        'edge_seal_width_top_1': 12.5,
        'edge_seal_width_top_2': 12.3,
        'edge_seal_width_bottom_1': 12.4,
        'edge_seal_width_bottom_2': 12.6,
        'edge_seal_width_left_1': 12.2,
        'edge_seal_width_left_2': 12.7,
        'edge_seal_width_right_1': 12.5,
        'edge_seal_width_right_2': 12.4,
        'initial_defects_count': 0,
        'initial_defect_description': '',
        'baseline_image_top': 'baseline_top.jpg',
        'baseline_image_bottom': 'baseline_bottom.jpg',
        'baseline_image_left': 'baseline_left.jpg',
        'baseline_image_right': 'baseline_right.jpg'
    }


@pytest.fixture
def mock_chamber_data():
    """Mock environmental chamber data."""
    return {
        'temp_damp_heat': 85.2,
        'humidity_damp_heat': 84.5,
        'temp_freeze': -40.1,
        'deviation_flag': False,
        'deviation_notes': ''
    }


@pytest.fixture
def mock_final_inspection_data():
    """Mock final inspection data."""
    return {
        'delamination_top': 0.8,
        'delamination_bottom': 0.5,
        'delamination_left': 0.6,
        'delamination_right': 0.7,
        'moisture_detected': False,
        'moisture_location': '',
        'adhesion_loss': 5.0,
        'image_top': 'final_top.jpg',
        'image_bottom': 'final_bottom.jpg',
        'image_left': 'final_left.jpg',
        'image_right': 'final_right.jpg',
        'notes': 'Test completed successfully'
    }


@pytest.fixture
def mock_failed_inspection_data():
    """Mock failed inspection data (moisture ingress)."""
    return {
        'delamination_top': 5.2,
        'delamination_bottom': 4.8,
        'delamination_left': 5.1,
        'delamination_right': 4.9,
        'moisture_detected': True,
        'moisture_location': 'Bottom edge, center',
        'adhesion_loss': 35.0,
        'image_top': 'final_top.jpg',
        'image_bottom': 'final_bottom.jpg',
        'image_left': 'final_left.jpg',
        'image_right': 'final_right.jpg',
        'notes': 'Significant moisture ingress detected'
    }
