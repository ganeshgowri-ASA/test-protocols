"""
Pytest Configuration and Fixtures
==================================

Shared fixtures for test suite.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_diel001_protocol():
    """Sample DIEL-001 protocol configuration"""
    return {
        "protocol_id": "DIEL-001",
        "protocol_name": "Dielectric Withstand Test",
        "version": "1.0.0",
        "standard": "IEC 61730 MST 15",
        "category": "safety",
        "data_points": [
            {
                "field": "module_id",
                "label": "Module ID",
                "type": "string",
                "required": True
            },
            {
                "field": "max_system_voltage",
                "label": "Max System Voltage",
                "type": "number",
                "unit": "V",
                "required": True,
                "min": 0,
                "max": 1500
            },
            {
                "field": "module_area",
                "label": "Module Area",
                "type": "number",
                "unit": "m²",
                "required": True,
                "min": 0.1
            }
        ],
        "acceptance_criteria": {
            "insulation_resistance_initial": {
                "min_value": 40,
                "unit": "MΩ/m²",
                "condition": "greater_than_or_equal"
            }
        }
    }


@pytest.fixture
def sample_test_data():
    """Sample test data for DIEL-001"""
    return {
        "module_id": "TEST-001",
        "max_system_voltage": 1000.0,
        "module_area": 1.5,
        "test_voltage_calculated": 3000.0,
        "test_voltage_applied": 3000.0,
        "test_duration": 60,
        "insulation_resistance_initial": 100.0,
        "insulation_resistance_final": 95.0,
        "leakage_current_max": 25.0,
        "breakdown_occurred": False,
        "visual_inspection_pass": True,
        "ambient_temperature": 25.0,
        "relative_humidity": 50.0
    }
