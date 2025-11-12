"""
Integration tests for protocol workflow.
"""
import pytest
from pathlib import Path
from protocols.handler import ProtocolHandler
from protocols.loader import ProtocolLoader
from validators import SchemaValidator, RangeValidator
from test_data import ProtocolGenerator, MeasurementGenerator


@pytest.mark.integration
class TestProtocolWorkflow:
    """Test complete protocol workflow integration."""

    def test_load_validate_execute_workflow(self, protocol_templates_dir):
        """Test complete workflow: load -> validate -> execute."""
        # Load protocol template
        loader = ProtocolLoader(templates_dir=protocol_templates_dir)
        template = loader.load_template("IEC61215-10-1")

        # Validate protocol
        validator = SchemaValidator()
        validation_result = validator.validate_protocol(template)
        assert validation_result["is_valid"]

        # Execute protocol
        handler = ProtocolHandler()
        protocol = handler.load_protocol(template)
        result = handler.execute_protocol(protocol)

        assert result.protocol_id == template["protocol_id"]
        assert result.execution_time is not None

    def test_generate_validate_execute_workflow(self):
        """Test workflow with generated data."""
        # Generate protocol
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Validate
        validator = SchemaValidator()
        validation_result = validator.validate_protocol(protocol_data)

        if validation_result["is_valid"]:
            # Execute
            handler = ProtocolHandler()
            protocol = handler.load_protocol(protocol_data)
            result = handler.execute_protocol(protocol)

            assert result is not None

    def test_protocol_with_measurements_workflow(self):
        """Test protocol workflow with measurements."""
        # Generate protocol and measurements
        protocol_gen = ProtocolGenerator(seed=42)
        measurement_gen = MeasurementGenerator(seed=42)

        protocol_data = protocol_gen.generate_protocol(protocol_type="electrical")
        measurements = measurement_gen.generate_batch(count=10)

        # Add measurements to protocol
        protocol_data["measurements"] = measurements

        # Execute workflow
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        assert len(protocol.measurements) == 10

    def test_validation_chain_workflow(self):
        """Test chaining multiple validators."""
        # Generate protocol
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Schema validation
        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate_protocol(protocol_data)

        # Range validation for parameters
        if "temperature" in protocol_data["parameters"]:
            range_validator = RangeValidator()
            range_result = range_validator.validate_value(
                "temperature",
                protocol_data["parameters"]["temperature"]
            )
            assert "is_valid" in range_result

        assert schema_result["is_valid"]


@pytest.mark.integration
class TestProtocolLoaderIntegration:
    """Test protocol loader integration."""

    def test_list_and_load_protocols(self, protocol_templates_dir):
        """Test listing and loading available protocols."""
        loader = ProtocolLoader(templates_dir=protocol_templates_dir)

        # List available protocols
        protocols = loader.list_available_protocols()
        assert len(protocols) > 0

        # Load first protocol
        first_protocol_id = protocols[0]["protocol_id"]
        template = loader.load_template(first_protocol_id)

        assert template["protocol_id"] == first_protocol_id

    def test_load_schema_and_validate(self, protocol_schemas_dir):
        """Test loading schema and using for validation."""
        loader = ProtocolLoader(schemas_dir=protocol_schemas_dir)

        # Load base schema
        schema = loader.load_schema("base_protocol_schema")
        assert "$schema" in schema

        # Use schema for validation
        validator = SchemaValidator(schemas_dir=protocol_schemas_dir)
        generator = ProtocolGenerator(seed=42)
        protocol = generator.generate_protocol()

        result = validator.validate_protocol(protocol)
        assert "is_valid" in result


@pytest.mark.integration
class TestValidatorIntegration:
    """Test validator integration."""

    def test_multi_validator_pipeline(self):
        """Test running multiple validators in pipeline."""
        from validators import (
            SchemaValidator,
            RangeValidator,
            CrossFieldValidator,
        )

        # Generate test data
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Add measurements with values
        protocol_data["parameters"]["temperature"] = 25
        protocol_data["parameters"]["irradiance"] = 1000

        # Validation pipeline
        results = {}

        # 1. Schema validation
        schema_validator = SchemaValidator()
        results["schema"] = schema_validator.validate_protocol(protocol_data)

        # 2. Range validation
        range_validator = RangeValidator()
        if "temperature" in protocol_data["parameters"]:
            results["temperature_range"] = range_validator.validate_value(
                "temperature",
                protocol_data["parameters"]["temperature"]
            )

        # 3. Cross-field validation
        cross_validator = CrossFieldValidator()
        results["cross_field"] = cross_validator.validate(protocol_data)

        # Check all validations
        assert results["schema"]["is_valid"]
        if "temperature_range" in results:
            assert results["temperature_range"]["is_valid"]

    def test_validation_error_aggregation(self):
        """Test aggregating validation errors from multiple validators."""
        from validators import SchemaValidator, RangeValidator

        # Create invalid protocol
        invalid_protocol = {
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "protocol_type": "electrical",
            "version": "1.0",
            "parameters": {
                "temperature": 999,  # Out of range
            },
        }

        errors = []

        # Schema validation
        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate_protocol(invalid_protocol)
        errors.extend(schema_result.get("errors", []))

        # Range validation
        range_validator = RangeValidator()
        range_result = range_validator.validate_value("temperature", 999)
        errors.extend(range_result.get("errors", []))

        assert len(errors) > 0
