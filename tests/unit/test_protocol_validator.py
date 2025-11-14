"""
Unit Tests for Protocol Validator

Tests protocol and data validation functionality.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core import ProtocolValidator, ValidationError


class TestProtocolValidator:
    """Test cases for ProtocolValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a ProtocolValidator instance."""
        return ProtocolValidator()

    @pytest.fixture
    def valid_protocol(self):
        """Create a valid protocol definition."""
        return {
            "protocol_id": "TEST-001",
            "name": "Test Protocol",
            "version": "1.0.0",
            "category": "test",
            "test_sequence": {
                "steps": [
                    {
                        "step_id": 1,
                        "name": "Test Step",
                        "type": "measurement",
                        "substeps": [
                            {
                                "substep_id": 1.1,
                                "name": "Test Substep",
                                "type": "measurement",
                                "data_fields": []
                            }
                        ]
                    }
                ]
            }
        }

    def test_validate_protocol_structure_valid(self, validator, valid_protocol):
        """Test validation of a valid protocol."""
        is_valid, errors = validator.validate_protocol_structure(valid_protocol)

        assert is_valid
        assert errors == []

    def test_validate_protocol_structure_missing_field(self, validator):
        """Test validation with missing required field."""
        protocol = {
            "protocol_id": "TEST-001",
            "name": "Test Protocol",
            # Missing version
            "category": "test"
        }

        is_valid, errors = validator.validate_protocol_structure(protocol)

        assert not is_valid
        assert any("version" in error for error in errors)

    def test_validate_protocol_id_format(self, validator):
        """Test protocol ID format validation."""
        # Valid format
        assert validator._validate_protocol_id("TEST-001")
        assert validator._validate_protocol_id("PID-002")
        assert validator._validate_protocol_id("ABC-123")

        # Invalid format
        assert not validator._validate_protocol_id("test-001")  # lowercase
        assert not validator._validate_protocol_id("TEST001")   # no dash
        assert not validator._validate_protocol_id("TEST-")     # no number
        assert not validator._validate_protocol_id("123-TEST")  # reversed

    def test_validate_version_format(self, validator):
        """Test version format validation (semver)."""
        # Valid format
        assert validator._validate_version("1.0.0")
        assert validator._validate_version("2.3.4")
        assert validator._validate_version("10.20.30")

        # Invalid format
        assert not validator._validate_version("1.0")       # missing patch
        assert not validator._validate_version("v1.0.0")    # has 'v' prefix
        assert not validator._validate_version("1.0.0-rc1") # has suffix

    def test_validate_test_sequence(self, validator):
        """Test test sequence validation."""
        # Valid sequence
        valid_sequence = {
            "steps": [
                {
                    "step_id": 1,
                    "name": "Step 1",
                    "type": "measurement",
                    "substeps": []
                }
            ]
        }

        errors = validator._validate_test_sequence(valid_sequence)
        assert errors == []

        # Missing steps field
        invalid_sequence = {}
        errors = validator._validate_test_sequence(invalid_sequence)
        assert any("steps" in error for error in errors)

    def test_validate_test_data_valid(self, validator, valid_protocol):
        """Test validation of valid test data."""
        # Add data fields to substep
        substep = valid_protocol['test_sequence']['steps'][0]['substeps'][0]
        substep['data_fields'] = [
            {
                "field_id": "test_value",
                "label": "Test Value",
                "type": "number",
                "required": True
            }
        ]

        data = {"test_value": 42.5}

        is_valid, errors = validator.validate_test_data(
            valid_protocol,
            step_id=1,
            substep_id=1.1,
            data=data
        )

        assert is_valid
        assert errors == []

    def test_validate_test_data_missing_required(self, validator, valid_protocol):
        """Test validation with missing required field."""
        # Add required field to substep
        substep = valid_protocol['test_sequence']['steps'][0]['substeps'][0]
        substep['data_fields'] = [
            {
                "field_id": "test_value",
                "label": "Test Value",
                "type": "number",
                "required": True
            }
        ]

        data = {}  # Missing required field

        is_valid, errors = validator.validate_test_data(
            valid_protocol,
            step_id=1,
            substep_id=1.1,
            data=data
        )

        assert not is_valid
        assert any("required" in error.lower() for error in errors)

    def test_validate_field_number(self, validator):
        """Test number field validation."""
        field_def = {
            "field_id": "power",
            "type": "number",
            "min": 0,
            "max": 100
        }

        # Valid value
        errors = validator._validate_field_data(field_def, 50)
        assert errors == []

        # Below minimum
        errors = validator._validate_field_data(field_def, -10)
        assert len(errors) > 0

        # Above maximum
        errors = validator._validate_field_data(field_def, 150)
        assert len(errors) > 0

        # Wrong type
        errors = validator._validate_field_data(field_def, "not a number")
        assert len(errors) > 0

    def test_validate_field_text(self, validator):
        """Test text field validation."""
        field_def = {
            "field_id": "notes",
            "type": "text"
        }

        # Valid value
        errors = validator._validate_field_data(field_def, "Test notes")
        assert errors == []

        # Wrong type
        errors = validator._validate_field_data(field_def, 123)
        assert len(errors) > 0

    def test_validate_field_boolean(self, validator):
        """Test boolean field validation."""
        field_def = {
            "field_id": "completed",
            "type": "boolean"
        }

        # Valid values
        errors = validator._validate_field_data(field_def, True)
        assert errors == []

        errors = validator._validate_field_data(field_def, False)
        assert errors == []

        # Wrong type
        errors = validator._validate_field_data(field_def, "yes")
        assert len(errors) > 0

    def test_validate_field_multiselect(self, validator):
        """Test multiselect field validation."""
        field_def = {
            "field_id": "defects",
            "type": "multiselect",
            "options": ["None", "Crack", "Discoloration"]
        }

        # Valid value
        errors = validator._validate_field_data(field_def, ["None"])
        assert errors == []

        # Invalid option
        errors = validator._validate_field_data(field_def, ["InvalidOption"])
        assert len(errors) > 0

    def test_validate_equipment_requirements(self, validator):
        """Test equipment requirements validation."""
        # Valid equipment
        valid_equipment = [
            {
                "equipment_id": "EQ-001",
                "name": "Test Equipment",
                "specifications": {}
            }
        ]

        errors = validator._validate_equipment_requirements(valid_equipment)
        assert errors == []

        # Missing required field
        invalid_equipment = [
            {
                "equipment_id": "EQ-001"
                # Missing name and specifications
            }
        ]

        errors = validator._validate_equipment_requirements(invalid_equipment)
        assert len(errors) > 0

    def test_validate_qc_rules(self, validator):
        """Test QC rules validation."""
        # Valid QC rule
        valid_rules = [
            {
                "rule_id": "QC001",
                "name": "Test Rule",
                "severity": "warning",
                "condition": "value > 10",
                "message": "Test message"
            }
        ]

        errors = validator._validate_qc_rules(valid_rules)
        assert errors == []

        # Invalid severity
        invalid_rules = [
            {
                "rule_id": "QC001",
                "name": "Test Rule",
                "severity": "invalid",  # Invalid severity
                "condition": "value > 10",
                "message": "Test message"
            }
        ]

        errors = validator._validate_qc_rules(invalid_rules)
        assert len(errors) > 0

        # Duplicate rule ID
        duplicate_rules = [
            {
                "rule_id": "QC001",
                "name": "Rule 1",
                "severity": "warning",
                "condition": "value > 10",
                "message": "Message 1"
            },
            {
                "rule_id": "QC001",  # Duplicate
                "name": "Rule 2",
                "severity": "error",
                "condition": "value < 0",
                "message": "Message 2"
            }
        ]

        errors = validator._validate_qc_rules(duplicate_rules)
        assert any("duplicate" in error.lower() for error in errors)
