"""
Unit tests for test data generators.
"""
import pytest
from test_data import (
    ProtocolGenerator,
    MeasurementGenerator,
    EdgeCaseGenerator,
)


@pytest.mark.unit
class TestProtocolGenerator:
    """Test ProtocolGenerator."""

    def test_generate_protocol(self):
        """Test generating a single protocol."""
        generator = ProtocolGenerator(seed=42)
        protocol = generator.generate_protocol()

        assert "protocol_id" in protocol
        assert "protocol_name" in protocol
        assert "protocol_type" in protocol
        assert "version" in protocol
        assert "parameters" in protocol

    def test_generate_specific_protocol_type(self):
        """Test generating protocol of specific type."""
        generator = ProtocolGenerator(seed=42)
        protocol = generator.generate_protocol(protocol_type="electrical")

        assert protocol["protocol_type"] == "electrical"

    def test_generate_batch(self):
        """Test generating multiple protocols."""
        generator = ProtocolGenerator(seed=42)
        protocols = generator.generate_batch(count=10)

        assert len(protocols) == 10
        assert all("protocol_id" in p for p in protocols)

    def test_generate_invalid_protocol(self):
        """Test generating invalid protocol."""
        generator = ProtocolGenerator(seed=42)
        invalid = generator.generate_invalid_protocol()

        # Should be missing required fields or have invalid values
        assert isinstance(invalid, dict)


@pytest.mark.unit
class TestMeasurementGenerator:
    """Test MeasurementGenerator."""

    def test_generate_measurement(self):
        """Test generating a single measurement."""
        generator = MeasurementGenerator(seed=42)
        measurement = generator.generate_measurement()

        assert "measurement_id" in measurement
        assert "parameter" in measurement
        assert "value" in measurement
        assert "unit" in measurement

    def test_generate_specific_parameter(self):
        """Test generating measurement for specific parameter."""
        generator = MeasurementGenerator(seed=42)
        measurement = generator.generate_measurement(parameter="voltage")

        assert measurement["parameter"] == "voltage"
        assert measurement["unit"] == "V"

    def test_generate_iv_curve(self):
        """Test generating I-V curve data."""
        generator = MeasurementGenerator(seed=42)
        measurements = generator.generate_iv_curve(num_points=50)

        # Should have voltage, current, and power for each point
        assert len(measurements) == 50 * 3  # 3 measurements per point

        # Check for voltage, current, power measurements
        params = set(m["parameter"] for m in measurements)
        assert "voltage" in params
        assert "current" in params
        assert "power" in params

    def test_generate_time_series(self):
        """Test generating time series data."""
        generator = MeasurementGenerator(seed=42)
        measurements = generator.generate_time_series(
            parameter="temperature",
            duration_seconds=600,
            interval_seconds=60,
        )

        assert len(measurements) == 10  # 600 / 60
        assert all(m["parameter"] == "temperature" for m in measurements)

    def test_generate_batch(self):
        """Test generating batch of measurements."""
        generator = MeasurementGenerator(seed=42)
        measurements = generator.generate_batch(count=20)

        assert len(measurements) == 20

    def test_generate_invalid_measurement(self):
        """Test generating invalid measurement."""
        generator = MeasurementGenerator(seed=42)
        invalid = generator.generate_invalid_measurement()

        assert isinstance(invalid, dict)

    def test_add_custom_measurement_type(self):
        """Test adding custom measurement type."""
        generator = MeasurementGenerator(seed=42)
        generator.add_measurement_type(
            name="custom_param",
            unit="units",
            value_range=(0, 100),
            precision=2,
        )

        measurement = generator.generate_measurement(parameter="custom_param")

        assert measurement["parameter"] == "custom_param"
        assert measurement["unit"] == "units"
        assert 0 <= measurement["value"] <= 100


@pytest.mark.unit
class TestEdgeCaseGenerator:
    """Test EdgeCaseGenerator."""

    def test_generate_boundary_values(self):
        """Test generating boundary value test cases."""
        generator = EdgeCaseGenerator()
        cases = generator.generate_boundary_values("temperature")

        assert len(cases) > 0
        # Should include min, max, and various boundary points
        values = [c["value"] for c in cases]
        assert -40 in values  # Min
        assert 150 in values  # Max

    def test_generate_null_empty_cases(self):
        """Test generating null/empty test cases."""
        generator = EdgeCaseGenerator()
        cases = generator.generate_null_empty_cases()

        assert len(cases) > 0
        assert any(c["description"].lower().startswith("null") for c in cases)
        assert any(c["description"].lower().startswith("empty") for c in cases)

    def test_generate_type_mismatch_cases(self):
        """Test generating type mismatch test cases."""
        generator = EdgeCaseGenerator()
        cases = generator.generate_type_mismatch_cases()

        assert len(cases) > 0
        assert all("expected_type" in c for c in cases)

    def test_generate_large_data_cases(self):
        """Test generating large data test cases."""
        generator = EdgeCaseGenerator()
        cases = generator.generate_large_data_cases()

        assert len(cases) > 0
        # Should include very long strings, large arrays, etc.

    def test_generate_special_character_cases(self):
        """Test generating special character test cases."""
        generator = EdgeCaseGenerator()
        cases = generator.generate_special_character_cases()

        assert len(cases) > 0

    def test_generate_all_edge_cases(self):
        """Test generating all edge case categories."""
        generator = EdgeCaseGenerator()
        all_cases = generator.generate_all_edge_cases()

        assert isinstance(all_cases, dict)
        assert "boundary_temperature" in all_cases
        assert "null_empty" in all_cases
        assert "type_mismatch" in all_cases
        assert "large_data" in all_cases
