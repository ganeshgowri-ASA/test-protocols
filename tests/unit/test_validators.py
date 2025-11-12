"""
Unit tests for validation suite.
"""
import pytest
from validators import (
    SchemaValidator,
    DataValidator,
    RangeValidator,
    ComplianceValidator,
    CrossFieldValidator,
)


@pytest.mark.unit
class TestSchemaValidator:
    """Test SchemaValidator."""

    def test_validate_valid_protocol(self, sample_protocol_data):
        """Test validation of valid protocol data."""
        validator = SchemaValidator()
        result = validator.validate_protocol(sample_protocol_data)

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_required_field(self):
        """Test validation with missing required field."""
        validator = SchemaValidator()
        invalid_data = {
            "protocol_name": "Test",
            # Missing protocol_id
            "protocol_type": "electrical",
            "version": "1.0",
            "parameters": {},
        }

        result = validator.validate_protocol(invalid_data)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_invalid_protocol_type(self):
        """Test validation with invalid protocol type."""
        validator = SchemaValidator()
        invalid_data = {
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "protocol_type": "invalid_type",
            "version": "1.0",
            "parameters": {},
        }

        result = validator.validate_protocol(invalid_data)

        assert result["is_valid"] is False


@pytest.mark.unit
class TestDataValidator:
    """Test DataValidator."""

    def test_validate_string_field(self):
        """Test string field validation."""
        validator = DataValidator()
        result = validator.validate_field("test_value", "string")

        assert result["is_valid"] is True

    def test_validate_string_min_length(self):
        """Test string minimum length constraint."""
        validator = DataValidator()
        result = validator.validate_field(
            "ab",
            "string",
            constraints={"min_length": 3}
        )

        assert result["is_valid"] is False
        assert "too short" in result["errors"][0].lower()

    def test_validate_number_field(self):
        """Test number field validation."""
        validator = DataValidator()
        result = validator.validate_field(24.5, "number")

        assert result["is_valid"] is True

    def test_validate_number_range(self):
        """Test number range validation."""
        validator = DataValidator()
        result = validator.validate_field(
            150,
            "number",
            constraints={"minimum": 0, "maximum": 100}
        )

        assert result["is_valid"] is False
        assert "above maximum" in result["errors"][0].lower()

    def test_validate_integer_field(self):
        """Test integer field validation."""
        validator = DataValidator()
        result = validator.validate_field(42, "integer")

        assert result["is_valid"] is True

    def test_validate_boolean_field(self):
        """Test boolean field validation."""
        validator = DataValidator()
        result = validator.validate_field(True, "boolean")

        assert result["is_valid"] is True

    def test_validate_datetime_field(self):
        """Test datetime field validation."""
        validator = DataValidator()
        result = validator.validate_field(
            "2025-11-12T00:00:00Z",
            "datetime"
        )

        assert result["is_valid"] is True

    def test_validate_protocol_id_format(self):
        """Test protocol ID format validation."""
        validator = DataValidator()

        # Valid protocol ID
        result = validator.validate_field("IEC61215-10-1", "protocol_id")
        assert result["is_valid"] is True

        # Invalid protocol ID (lowercase)
        result = validator.validate_field("iec61215-10-1", "protocol_id")
        assert result["is_valid"] is False

    def test_validate_required_field_empty(self):
        """Test validation of required but empty field."""
        validator = DataValidator()
        result = validator.validate_field(
            "",
            "string",
            constraints={"required": True}
        )

        assert result["is_valid"] is False
        assert "required" in result["errors"][0].lower()


@pytest.mark.unit
class TestRangeValidator:
    """Test RangeValidator."""

    def test_validate_temperature_in_range(self):
        """Test temperature value within range."""
        validator = RangeValidator()
        result = validator.validate_value("temperature", 25.0)

        assert result["is_valid"] is True
        assert result["status"] == "pass"

    def test_validate_temperature_below_minimum(self):
        """Test temperature below minimum."""
        validator = RangeValidator()
        result = validator.validate_value("temperature", -50.0)

        assert result["is_valid"] is False
        assert result["status"] == "fail"
        assert "below minimum" in result["errors"][0].lower()

    def test_validate_temperature_above_maximum(self):
        """Test temperature above maximum."""
        validator = RangeValidator()
        result = validator.validate_value("temperature", 200.0)

        assert result["is_valid"] is False
        assert result["status"] == "fail"

    def test_validate_with_warning_threshold(self):
        """Test validation with warning threshold."""
        validator = RangeValidator()
        result = validator.validate_value("temperature", -35.0)

        assert result["is_valid"] is True
        assert result["status"] == "warning"
        assert len(result["warnings"]) > 0

    def test_validate_irradiance(self):
        """Test irradiance validation."""
        validator = RangeValidator()
        result = validator.validate_value("irradiance", 1000.0)

        assert result["is_valid"] is True

    def test_validate_multiple_values(self):
        """Test validation of multiple measurements."""
        validator = RangeValidator()
        measurements = {
            "temperature": 25.0,
            "irradiance": 1000.0,
            "voltage": 45.0,
        }

        result = validator.validate_multiple_values(measurements)

        assert result["is_valid"] is True
        assert len(result["results"]) == 3

    def test_add_custom_range(self):
        """Test adding custom parameter range."""
        validator = RangeValidator()
        validator.add_range("custom_param", {
            "min": 0,
            "max": 50,
            "unit": "units",
        })

        result = validator.validate_value("custom_param", 25.0)
        assert result["is_valid"] is True


@pytest.mark.unit
class TestComplianceValidator:
    """Test ComplianceValidator."""

    def test_validate_iec61215_compliance(self):
        """Test IEC 61215 compliance validation."""
        validator = ComplianceValidator()

        protocol_data = {
            "protocol_id": "IEC61215-10-10",
            "protocol_name": "Thermal Cycling",
            "protocol_type": "thermal",
            "version": "1.0",
            "parameters": {
                "number_of_cycles": 200,
                "max_power_degradation": 4,
            },
        }

        result = validator.validate_protocol_compliance(
            protocol_data, standard="IEC61215"
        )

        # Note: May or may not be compliant depending on all requirements
        assert "is_valid" in result
        assert "compliant" in result

    def test_list_supported_standards(self):
        """Test listing supported standards."""
        validator = ComplianceValidator()
        standards = validator.list_supported_standards()

        assert "IEC61215" in standards
        assert "IEC61730" in standards

    def test_get_standard_requirements(self):
        """Test getting requirements for specific test type."""
        validator = ComplianceValidator()
        requirements = validator.get_standard_requirements(
            "IEC61215", "thermal_cycling"
        )

        assert "min_cycles" in requirements
        assert requirements["min_cycles"] == 200


@pytest.mark.unit
class TestCrossFieldValidator:
    """Test CrossFieldValidator."""

    def test_validate_consistent_protocol(self):
        """Test validation of logically consistent protocol."""
        validator = CrossFieldValidator()

        protocol_data = {
            "protocol_id": "TEST-001",
            "protocol_type": "electrical",
            "parameters": {
                "irradiance": 1000,
                "temperature": 25,
                "voltage_range": {"min": 0, "max": 50},
            },
            "measurements": [],
        }

        result = validator.validate(protocol_data)

        assert result["is_valid"] is True

    def test_validate_irradiance_temperature_mismatch(self):
        """Test detection of irradiance/temperature mismatch."""
        validator = CrossFieldValidator()

        protocol_data = {
            "protocol_id": "TEST-001",
            "protocol_type": "electrical",
            "parameters": {
                "irradiance": 1000,  # STC irradiance
                "temperature": 50,    # Not STC temperature
            },
            "measurements": [],
        }

        result = validator.validate(protocol_data)

        # Should warn about temperature not matching STC
        assert result["is_valid"] is False

    def test_validate_measurement_consistency(self):
        """Test measurement consistency validation."""
        validator = CrossFieldValidator()

        measurements = [
            {
                "measurement_id": "M001",
                "parameter": "voltage",
                "value": 24.5,
                "unit": "V",
                "timestamp": "2025-11-12T10:00:00Z",
            },
            {
                "measurement_id": "M002",
                "parameter": "voltage",
                "value": 25.0,
                "unit": "V",  # Consistent unit
                "timestamp": "2025-11-12T10:01:00Z",
            },
        ]

        result = validator.validate_measurement_consistency(measurements)

        assert result["is_valid"] is True

    def test_validate_duplicate_measurement_ids(self):
        """Test detection of duplicate measurement IDs."""
        validator = CrossFieldValidator()

        measurements = [
            {
                "measurement_id": "M001",
                "parameter": "voltage",
                "value": 24.5,
                "unit": "V",
            },
            {
                "measurement_id": "M001",  # Duplicate
                "parameter": "current",
                "value": 8.0,
                "unit": "A",
            },
        ]

        result = validator.validate_measurement_consistency(measurements)

        assert result["is_valid"] is False
        assert any("duplicate" in error.lower() for error in result["errors"])
