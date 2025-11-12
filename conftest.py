"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return TEST_DATA_DIR


@pytest.fixture(scope="session")
def protocol_schemas_dir() -> Path:
    """Provide path to protocol schemas directory."""
    return Path(__file__).parent / "protocols" / "schemas"


@pytest.fixture(scope="session")
def protocol_templates_dir() -> Path:
    """Provide path to protocol templates directory."""
    return Path(__file__).parent / "protocols" / "templates"


@pytest.fixture
def sample_protocol_data() -> Dict[str, Any]:
    """Provide sample protocol data for testing."""
    return {
        "protocol_id": "IEC61215-10-1",
        "protocol_name": "Visual Inspection",
        "protocol_type": "inspection",
        "version": "1.0",
        "parameters": {
            "inspection_type": "pre-test",
            "module_id": "TEST-001",
            "inspector": "QA Team"
        },
        "measurements": [],
        "metadata": {
            "timestamp": "2025-11-12T00:00:00Z",
            "operator": "test_user"
        }
    }


@pytest.fixture
def sample_measurement_data() -> Dict[str, Any]:
    """Provide sample measurement data for testing."""
    return {
        "measurement_id": "MEAS-001",
        "parameter": "voltage",
        "value": 24.5,
        "unit": "V",
        "timestamp": "2025-11-12T00:00:00Z",
        "status": "pass"
    }


@pytest.fixture
def sample_validation_result() -> Dict[str, Any]:
    """Provide sample validation result for testing."""
    return {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "validated_at": "2025-11-12T00:00:00Z"
    }


@pytest.fixture
def mock_protocol_handler(mocker):
    """Provide a mock protocol handler."""
    handler = mocker.Mock()
    handler.validate.return_value = True
    handler.execute.return_value = {"status": "success"}
    return handler


@pytest.fixture
def mock_validator(mocker):
    """Provide a mock validator."""
    validator = mocker.Mock()
    validator.validate.return_value = {"is_valid": True, "errors": []}
    return validator


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    yield
    # Add cleanup code here if needed


@pytest.fixture
def temp_protocol_file(tmp_path):
    """Create a temporary protocol file for testing."""
    protocol_file = tmp_path / "test_protocol.json"
    protocol_data = {
        "protocol_id": "TEST-001",
        "protocol_name": "Test Protocol",
        "version": "1.0",
        "parameters": {}
    }
    protocol_file.write_text(json.dumps(protocol_data, indent=2))
    return protocol_file


def pytest_configure(config):
    """Pytest configuration hook."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers",
        "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers",
        "validation: JSON schema and data validation tests"
    )
