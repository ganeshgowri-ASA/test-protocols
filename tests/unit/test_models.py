"""
Unit tests for protocol data models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from protocols.models import (
    Protocol,
    Measurement,
    ProtocolType,
    ProtocolStatus,
    MeasurementStatus,
    ProtocolResult,
)


@pytest.mark.unit
class TestMeasurement:
    """Test Measurement model."""

    def test_valid_measurement(self):
        """Test creating a valid measurement."""
        measurement = Measurement(
            measurement_id="M001",
            parameter="voltage",
            value=24.5,
            unit="V",
            timestamp=datetime.now(),
            status=MeasurementStatus.PASS,
        )

        assert measurement.measurement_id == "M001"
        assert measurement.parameter == "voltage"
        assert measurement.value == 24.5
        assert measurement.unit == "V"
        assert measurement.status == "pass"

    def test_measurement_with_uncertainty(self):
        """Test measurement with uncertainty."""
        measurement = Measurement(
            measurement_id="M002",
            parameter="current",
            value=8.2,
            unit="A",
            uncertainty=0.1,
        )

        assert measurement.uncertainty == 0.1

    def test_measurement_with_conditions(self):
        """Test measurement with test conditions."""
        conditions = {
            "temperature": 25,
            "irradiance": 1000,
        }

        measurement = Measurement(
            measurement_id="M003",
            parameter="power",
            value=200,
            unit="W",
            conditions=conditions,
        )

        assert measurement.conditions == conditions


@pytest.mark.unit
class TestProtocol:
    """Test Protocol model."""

    def test_valid_protocol(self):
        """Test creating a valid protocol."""
        protocol = Protocol(
            protocol_id="IEC61215-10-1",
            protocol_name="Visual Inspection",
            protocol_type=ProtocolType.INSPECTION,
            version="1.0",
            parameters={"module_id": "TEST-001"},
        )

        assert protocol.protocol_id == "IEC61215-10-1"
        assert protocol.protocol_name == "Visual Inspection"
        assert protocol.protocol_type == "inspection"
        assert protocol.version == "1.0"
        assert protocol.status == "pending"

    def test_invalid_protocol_id(self):
        """Test that invalid protocol ID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Protocol(
                protocol_id="invalid id",  # Contains space
                protocol_name="Test",
                protocol_type=ProtocolType.ELECTRICAL,
                version="1.0",
                parameters={},
            )

        assert "protocol_id" in str(exc_info.value)

    def test_invalid_version_format(self):
        """Test that invalid version format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            Protocol(
                protocol_id="TEST-001",
                protocol_name="Test",
                protocol_type=ProtocolType.ELECTRICAL,
                version="invalid",
                parameters={},
            )

        assert "version" in str(exc_info.value).lower()

    def test_protocol_with_measurements(self):
        """Test protocol with measurements."""
        measurements = [
            Measurement(
                measurement_id="M001",
                parameter="voltage",
                value=24.5,
                unit="V",
            )
        ]

        protocol = Protocol(
            protocol_id="TEST-001",
            protocol_name="Test",
            protocol_type=ProtocolType.ELECTRICAL,
            version="1.0",
            parameters={},
            measurements=measurements,
        )

        assert len(protocol.measurements) == 1
        assert protocol.measurements[0].parameter == "voltage"

    @pytest.mark.parametrize("version", [
        "1.0",
        "2.5",
        "1.0.0",
        "10.20.30",
    ])
    def test_valid_version_formats(self, version):
        """Test various valid version formats."""
        protocol = Protocol(
            protocol_id="TEST-001",
            protocol_name="Test",
            protocol_type=ProtocolType.ELECTRICAL,
            version=version,
            parameters={},
        )

        assert protocol.version == version


@pytest.mark.unit
class TestProtocolResult:
    """Test ProtocolResult model."""

    def test_valid_result(self):
        """Test creating a valid protocol result."""
        result = ProtocolResult(
            protocol_id="TEST-001",
            status=ProtocolStatus.COMPLETED,
            passed=True,
            measurements=[],
        )

        assert result.protocol_id == "TEST-001"
        assert result.status == "completed"
        assert result.passed is True

    def test_failed_result_with_errors(self):
        """Test failed result with error messages."""
        errors = ["Temperature out of range", "Voltage below minimum"]

        result = ProtocolResult(
            protocol_id="TEST-001",
            status=ProtocolStatus.FAILED,
            passed=False,
            errors=errors,
        )

        assert result.passed is False
        assert len(result.errors) == 2
        assert "Temperature" in result.errors[0]

    def test_result_with_execution_time(self):
        """Test result with execution time."""
        result = ProtocolResult(
            protocol_id="TEST-001",
            status=ProtocolStatus.COMPLETED,
            passed=True,
            execution_time=45.5,
        )

        assert result.execution_time == 45.5
