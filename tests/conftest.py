"""
Pytest Configuration and Fixtures

Common test fixtures and configuration.
"""

import pytest
from pathlib import Path
import json
from datetime import datetime


@pytest.fixture
def protocols_root():
    """Get the root protocols directory"""
    return Path(__file__).parent.parent / "protocols"


@pytest.fixture
def corr_001_definition_path(protocols_root):
    """Get path to CORR-001 protocol definition"""
    return protocols_root / "definitions" / "corrosion" / "corr-001.json"


@pytest.fixture
def corr_001_definition(corr_001_definition_path):
    """Load CORR-001 protocol definition"""
    with open(corr_001_definition_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_test_data():
    """Sample test data for CORR-001"""
    return {
        "sample_id": "TEST-SAMPLE-001",
        "serial_number": "SN-12345",
        "operator": "Test Operator",
        "test_date": "2025-01-15",
        "baseline_voc": 45.5,
        "baseline_isc": 9.2,
        "baseline_pmax": 350.0,
        "baseline_ff": 78.5,
        "salt_solution_concentration": 5.0,
        "salt_solution_ph": 6.8,
        "spray_temp": 35.0,
        "spray_duration": 48,
        "humidity_temp": 85.0,
        "humidity_rh": 85.0,
        "humidity_duration": 96,
        "cycle_number": 1,
        "visual_corrosion": "None",
        "corrosion_location": [],
        "delamination": False,
        "discoloration": False,
        "interim_voc": 45.3,
        "interim_isc": 9.1,
        "interim_pmax": 348.0,
        "insulation_resistance": 50.0,
        "final_voc": 44.8,
        "final_isc": 9.0,
        "final_pmax": 342.0,
        "final_ff": 77.8,
        "wet_leakage_current": 0.5,
        "ground_continuity": True,
        "test_result": "Pass"
    }


@pytest.fixture
def sample_test_data_with_failures():
    """Sample test data with QC failures"""
    return {
        "sample_id": "TEST-SAMPLE-002",
        "serial_number": "SN-67890",
        "operator": "Test Operator",
        "baseline_voc": 45.5,
        "baseline_isc": 9.2,
        "baseline_pmax": 350.0,
        "baseline_ff": 78.5,
        "salt_solution_concentration": 5.0,
        "salt_solution_ph": 6.8,
        "spray_temp": 35.0,
        "humidity_temp": 85.0,
        "humidity_rh": 85.0,
        "cycle_number": 1,
        "visual_corrosion": "Severe",  # QC failure
        "delamination": False,
        "discoloration": False,
        "interim_voc": 43.0,
        "interim_isc": 8.5,
        "interim_pmax": 320.0,  # >5% degradation
        "insulation_resistance": 30.0,  # Below 40 MΩ - QC failure
        "final_voc": 42.0,
        "final_isc": 8.3,
        "final_pmax": 310.0,  # >10% degradation - QC failure
        "final_ff": 76.0,
        "wet_leakage_current": 1.2,
        "ground_continuity": False,  # QC failure
        "test_result": "Fail"
    }


@pytest.fixture
def mock_protocol_definition():
    """Mock simplified protocol definition for testing"""
    return {
        "protocol_id": "TEST-001",
        "name": "Test Protocol",
        "category": "degradation",
        "version": "1.0.0",
        "description": "Test protocol for unit testing",
        "steps": [
            {
                "step_number": 1,
                "name": "Test Step 1",
                "type": "preparation",
                "description": "First test step",
                "automated": False,
                "quality_checks": []
            },
            {
                "step_number": 2,
                "name": "Test Step 2",
                "type": "measurement",
                "description": "Second test step",
                "automated": True,
                "quality_checks": ["Check data quality"]
            }
        ],
        "data_fields": [
            {
                "field_id": "test_field_1",
                "name": "Test Field 1",
                "type": "number",
                "unit": "V",
                "required": True,
                "validation": {"min": 0, "max": 100},
                "step_number": 1
            },
            {
                "field_id": "test_field_2",
                "name": "Test Field 2",
                "type": "text",
                "required": False,
                "step_number": 2
            }
        ],
        "qc_criteria": [
            {
                "criterion_id": "qc_test_1",
                "name": "Test QC 1",
                "type": "range",
                "field_id": "test_field_1",
                "condition": {"min": 10, "max": 90},
                "severity": "warning"
            }
        ],
        "analysis": {
            "calculations": [
                {
                    "name": "Test Calculation",
                    "formula": "test_field_1 * 2",
                    "unit": "V"
                }
            ]
        }
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir
