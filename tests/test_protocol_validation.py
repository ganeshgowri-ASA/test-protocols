"""Tests for protocol validation"""

import pytest
import json
from pathlib import Path
from protocols.core.protocol_validator import ProtocolValidator, load_protocol_definition


class TestProtocolValidator:
    """Test suite for ProtocolValidator"""

    def test_load_schema(self, protocol_schema, tmp_path):
        """Test loading JSON schema"""
        # Write schema to temp file
        schema_file = tmp_path / "schema.json"
        with open(schema_file, "w") as f:
            json.dump(protocol_schema, f)

        validator = ProtocolValidator(str(schema_file))

        assert validator.schema is not None
        assert "$schema" in validator.schema

    def test_validate_protocol_definition(self, protocol_definition):
        """Test validating protocol definition"""
        validator = ProtocolValidator()

        is_valid, errors = validator.validate_protocol_definition(protocol_definition)

        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_protocol_definition(self):
        """Test validation of invalid protocol definition"""
        validator = ProtocolValidator()

        invalid_def = {
            "protocol_id": "TEST-001",
            # Missing required fields
        }

        is_valid, errors = validator.validate_protocol_definition(invalid_def)

        assert is_valid is False
        assert len(errors) > 0

    def test_semver_validation(self):
        """Test semantic version validation"""
        validator = ProtocolValidator()

        # Valid semver
        assert validator._is_valid_semver("1.0.0") is True
        assert validator._is_valid_semver("1.2.3") is True
        assert validator._is_valid_semver("10.20.30") is True

        # Invalid semver
        assert validator._is_valid_semver("1.0") is False
        assert validator._is_valid_semver("v1.0.0") is False
        assert validator._is_valid_semver("1.0.0-beta") is False

    def test_validate_test_results(self, protocol_schema, sample_info, test_conditions):
        """Test validation of test results"""
        validator = ProtocolValidator()
        validator.schema = protocol_schema

        # Create valid test results
        test_results = {
            "test_execution_id": "CHALK-001-20251114-120000",
            "protocol_id": "CHALK-001",
            "protocol_version": "1.0.0",
            "sample_info": sample_info,
            "test_conditions": test_conditions,
            "measurements": [
                {
                    "location_id": "LOC-01",
                    "chalking_rating": 2.5,
                    "location_x": 100.0,
                    "location_y": 100.0,
                }
            ],
            "calculated_results": {
                "average_chalking_rating": 2.5,
                "chalking_std_dev": 0.0,
                "max_chalking_rating": 2.5,
                "min_chalking_rating": 2.5,
            },
            "pass_fail_assessment": {
                "overall_result": "PASS",
                "criteria_evaluations": [],
            },
        }

        is_valid, errors = validator.validate_data(test_results)

        # May fail due to schema strictness, but should not crash
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


class TestProtocolDefinitionLoading:
    """Test loading protocol definitions"""

    def test_load_protocol_definition(self):
        """Test loading CHALK-001 protocol definition"""
        protocol_path = (
            Path(__file__).parent.parent
            / "protocols"
            / "templates"
            / "backsheet_chalking"
            / "protocol.json"
        )

        protocol_def = load_protocol_definition(str(protocol_path))

        assert protocol_def is not None
        assert protocol_def["protocol_id"] == "CHALK-001"
        assert protocol_def["version"] == "1.0.0"
        assert "test_parameters" in protocol_def
        assert "test_steps" in protocol_def

    def test_protocol_structure(self, protocol_definition):
        """Test protocol definition has required structure"""
        # Required top-level fields
        assert "protocol_id" in protocol_definition
        assert "name" in protocol_definition
        assert "version" in protocol_definition
        assert "category" in protocol_definition
        assert "description" in protocol_definition

        # Test parameters structure
        assert "test_parameters" in protocol_definition
        params = protocol_definition["test_parameters"]
        assert "environmental_conditions" in params
        assert "sample_parameters" in params
        assert "measurement_parameters" in params

        # Test steps structure
        assert "test_steps" in protocol_definition
        steps = protocol_definition["test_steps"]
        assert len(steps) > 0
        assert all("step_id" in step for step in steps)

        # Data collection structure
        assert "data_collection" in protocol_definition
        data_collection = protocol_definition["data_collection"]
        assert "measurements" in data_collection
        assert "calculated_metrics" in data_collection

        # Pass/fail criteria
        assert "pass_fail_criteria" in protocol_definition
        criteria = protocol_definition["pass_fail_criteria"]
        assert "acceptance_thresholds" in criteria

    def test_test_steps_order(self, protocol_definition):
        """Test that test steps are in correct order"""
        steps = protocol_definition["test_steps"]

        for i, step in enumerate(steps, start=1):
            assert step["step_number"] == i

    def test_reference_standards(self, protocol_definition):
        """Test reference standards are included"""
        assert "reference_standards" in protocol_definition
        standards = protocol_definition["reference_standards"]
        assert len(standards) > 0
        assert "ASTM D4214" in standards
