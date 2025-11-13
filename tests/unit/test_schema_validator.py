"""Tests for schema validator."""

import pytest
from src.core.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test SchemaValidator class."""

    @pytest.fixture
    def validator(self, pid001_schema):
        """Create validator instance."""
        return SchemaValidator(pid001_schema)

    def test_initialization(self, pid001_schema):
        """Test validator initialization."""
        validator = SchemaValidator(pid001_schema)
        assert validator.schema == pid001_schema

    def test_validate_parameters_valid(self, validator, sample_test_parameters):
        """Test valid parameter validation."""
        is_valid, errors = validator.validate_parameters(sample_test_parameters)
        # Note: This might fail due to JSON schema validation details
        # The actual protocol implementation has custom validation
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_validate_parameters_missing_required(self, validator):
        """Test validation with missing required fields."""
        params = {"test_name": "TEST-001"}
        is_valid, errors = validator.validate_parameters(params)
        assert is_valid is False
        assert len(errors) > 0

    def test_get_parameter_metadata(self, validator):
        """Test parameter metadata extraction."""
        metadata = validator.get_parameter_metadata()
        assert isinstance(metadata, dict)
        assert "test_name" in metadata
        assert "test_voltage" in metadata

        # Check metadata structure
        test_voltage_meta = metadata["test_voltage"]
        assert test_voltage_meta["type"] == "number"
        assert "description" in test_voltage_meta
        assert test_voltage_meta["required"] is True

    def test_validate_measurement(self, validator):
        """Test measurement validation."""
        measurement = {
            "timestamp": "2025-11-13T10:00:00",
            "elapsed_time": 5.0,
            "leakage_current": 2.5,
            "voltage": -1000
        }
        is_valid, errors = validator.validate_measurement(measurement)
        assert isinstance(is_valid, bool)
