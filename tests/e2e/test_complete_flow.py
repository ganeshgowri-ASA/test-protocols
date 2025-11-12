"""
End-to-end tests for complete protocol testing flow.
"""
import pytest
from pathlib import Path
from protocols.handler import ProtocolHandler
from protocols.loader import ProtocolLoader
from validators import (
    SchemaValidator,
    DataValidator,
    RangeValidator,
    ComplianceValidator,
    CrossFieldValidator,
)
from test_data import ProtocolGenerator, MeasurementGenerator


@pytest.mark.e2e
class TestCompleteProtocolFlow:
    """Test complete end-to-end protocol testing flow."""

    def test_full_protocol_lifecycle(self, tmp_path):
        """Test complete protocol lifecycle from creation to result storage."""
        # Step 1: Generate protocol
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Step 2: Validate schema
        schema_validator = SchemaValidator()
        schema_result = schema_validator.validate_protocol(protocol_data)
        assert schema_result["is_valid"], f"Schema validation failed: {schema_result['errors']}"

        # Step 3: Validate ranges
        range_validator = RangeValidator()
        if "temperature" in protocol_data["parameters"]:
            temp_result = range_validator.validate_value(
                "temperature",
                protocol_data["parameters"]["temperature"]
            )
            assert temp_result["is_valid"], f"Temperature validation failed: {temp_result['errors']}"

        # Step 4: Execute protocol
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        # Step 5: Verify execution
        assert result.protocol_id == protocol_data["protocol_id"]
        assert result.execution_time is not None

        # Step 6: Save result
        output_dir = tmp_path / "results"
        handler.save_result(result, output_dir)

        # Step 7: Verify saved result
        result_files = list(output_dir.glob("*.json"))
        assert len(result_files) == 1

    def test_batch_protocol_processing(self):
        """Test processing multiple protocols in batch."""
        # Generate batch of protocols
        generator = ProtocolGenerator(seed=42)
        protocols = generator.generate_batch(count=5)

        # Process each protocol
        handler = ProtocolHandler()
        results = []

        for protocol_data in protocols:
            # Validate
            validator = SchemaValidator()
            validation = validator.validate_protocol(protocol_data)

            if validation["is_valid"]:
                # Execute
                protocol = handler.load_protocol(protocol_data)
                result = handler.execute_protocol(protocol)
                results.append(result)

        # Verify all protocols processed
        assert len(results) == 5

    def test_protocol_with_iv_curve_measurement(self):
        """Test protocol with I-V curve measurement data."""
        # Generate protocol
        protocol_gen = ProtocolGenerator(seed=42)
        protocol_data = protocol_gen.generate_protocol(protocol_type="electrical")

        # Generate I-V curve measurements
        measurement_gen = MeasurementGenerator(seed=42)
        iv_measurements = measurement_gen.generate_iv_curve(num_points=50)

        # Add measurements to protocol
        protocol_data["measurements"] = iv_measurements

        # Execute complete flow
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        # Verify measurements were processed
        assert len(protocol.measurements) > 0

    def test_compliance_validation_flow(self):
        """Test compliance validation in complete flow."""
        # Generate IEC 61215 protocol
        protocol_data = {
            "protocol_id": "IEC61215-10-10",
            "protocol_name": "Thermal Cycling Test",
            "protocol_type": "thermal",
            "version": "1.0",
            "parameters": {
                "module_id": "TEST-001",
                "test_type": "thermal_cycling",
                "number_of_cycles": 200,
                "temperature_profile": {
                    "min_temp": -40,
                    "max_temp": 85,
                },
            },
        }

        # Validate compliance
        compliance_validator = ComplianceValidator()
        compliance_result = compliance_validator.validate_protocol_compliance(
            protocol_data, standard="IEC61215"
        )

        # Execute protocol
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        # Verify execution
        assert result is not None

    def test_error_handling_flow(self):
        """Test error handling in complete flow."""
        # Create invalid protocol
        invalid_protocol = {
            "protocol_id": "INVALID",
            "protocol_name": "X",  # Too short
            "protocol_type": "invalid_type",
            "version": "bad",
            "parameters": {},
        }

        # Validate (should fail)
        validator = SchemaValidator()
        result = validator.validate_protocol(invalid_protocol)

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

    def test_multi_validator_comprehensive_flow(self):
        """Test comprehensive validation with all validators."""
        # Generate protocol
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Ensure required parameters for testing
        protocol_data["parameters"]["temperature"] = 25
        protocol_data["parameters"]["irradiance"] = 1000
        protocol_data["parameters"]["voltage_range"] = {"min": 0, "max": 50}

        # Run all validators
        validation_results = {}

        # 1. Schema validation
        schema_val = SchemaValidator()
        validation_results["schema"] = schema_val.validate_protocol(protocol_data)

        # 2. Range validation
        range_val = RangeValidator()
        validation_results["temperature"] = range_val.validate_value(
            "temperature", protocol_data["parameters"]["temperature"]
        )
        validation_results["irradiance"] = range_val.validate_value(
            "irradiance", protocol_data["parameters"]["irradiance"]
        )

        # 3. Cross-field validation
        cross_val = CrossFieldValidator()
        validation_results["cross_field"] = cross_val.validate(protocol_data)

        # Check all validations passed
        assert validation_results["schema"]["is_valid"]
        assert validation_results["temperature"]["is_valid"]
        assert validation_results["irradiance"]["is_valid"]

        # Execute protocol
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        assert result is not None


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceFlow:
    """Test performance characteristics of complete flow."""

    def test_large_batch_processing(self):
        """Test processing large batch of protocols."""
        import time

        # Generate large batch
        generator = ProtocolGenerator(seed=42)
        protocols = generator.generate_batch(count=100)

        # Process with timing
        start_time = time.time()

        handler = ProtocolHandler()
        results = []

        for protocol_data in protocols:
            try:
                protocol = handler.load_protocol(protocol_data)
                result = handler.execute_protocol(protocol)
                results.append(result)
            except Exception as e:
                pass  # Skip invalid protocols

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify performance (should process 100 protocols in reasonable time)
        assert len(results) > 0
        assert elapsed < 60  # Should complete within 60 seconds

    def test_large_measurement_dataset(self):
        """Test handling large measurement datasets."""
        # Generate protocol
        generator = ProtocolGenerator(seed=42)
        protocol_data = generator.generate_protocol(protocol_type="electrical")

        # Generate large measurement dataset
        measurement_gen = MeasurementGenerator(seed=42)
        large_dataset = measurement_gen.generate_batch(count=1000)

        protocol_data["measurements"] = large_dataset

        # Execute
        handler = ProtocolHandler()
        protocol = handler.load_protocol(protocol_data)
        result = handler.execute_protocol(protocol)

        assert len(protocol.measurements) == 1000
