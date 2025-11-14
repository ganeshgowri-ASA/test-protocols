"""
Tests for protocol data models.
"""

import pytest
from test_protocols.core.protocol import (
    Protocol, TestStep, Measurement, Standard, Equipment, TestCategory
)


class TestProtocol:
    """Test suite for Protocol class."""

    def test_protocol_creation(self, ml_001_protocol_data):
        """Test creating a Protocol object."""
        protocol = Protocol(**ml_001_protocol_data)

        assert protocol.protocol_id == "ML-001"
        assert protocol.version == "1.0.0"
        assert protocol.name == "Mechanical Load Static Test (2400Pa)"
        assert protocol.category == "mechanical"

    def test_protocol_validation_success(self, ml_001_protocol_data):
        """Test successful protocol validation."""
        protocol = Protocol(**ml_001_protocol_data)
        is_valid, errors = protocol.validate()

        assert is_valid is True
        assert len(errors) == 0

    def test_protocol_validation_missing_id(self):
        """Test validation with missing protocol_id."""
        protocol = Protocol(
            protocol_id="",
            version="1.0.0",
            name="Test",
            category="mechanical",
            standard=Standard(name="IEC", code="61215"),
            tests=[]
        )

        is_valid, errors = protocol.validate()

        assert is_valid is False
        assert any("protocol_id" in err for err in errors)

    def test_get_step_by_id(self, ml_001_protocol_data):
        """Test getting a step by ID."""
        protocol = Protocol(**ml_001_protocol_data)

        step = protocol.get_step("ML-001-S01")

        assert step is not None
        assert step.step_id == "ML-001-S01"
        assert step.name == "Pre-Test Visual Inspection"

    def test_get_step_by_sequence(self, ml_001_protocol_data):
        """Test getting a step by sequence number."""
        protocol = Protocol(**ml_001_protocol_data)

        step = protocol.get_step_by_sequence(1)

        assert step is not None
        assert step.sequence == 1
        assert step.step_id == "ML-001-S01"

    def test_get_total_duration(self, ml_001_protocol_data):
        """Test calculating total duration."""
        protocol = Protocol(**ml_001_protocol_data)

        duration = protocol.get_total_duration()

        assert duration == 180  # As specified in protocol

    def test_get_category_enum(self, ml_001_protocol_data):
        """Test getting category as enum."""
        protocol = Protocol(**ml_001_protocol_data)

        category = protocol.get_category_enum()

        assert category == TestCategory.MECHANICAL


class TestTestStep:
    """Test suite for TestStep class."""

    def test_test_step_creation(self):
        """Test creating a TestStep object."""
        step = TestStep(
            step_id="TEST-001-S01",
            name="Test Step",
            sequence=1,
            parameters={"param1": "value1"},
            duration_minutes=10.0
        )

        assert step.step_id == "TEST-001-S01"
        assert step.name == "Test Step"
        assert step.sequence == 1
        assert step.duration_minutes == 10.0

    def test_get_measurement(self, sample_measurement_data):
        """Test getting a measurement by type."""
        step = TestStep(
            step_id="TEST-001-S01",
            name="Test Step",
            sequence=1,
            parameters={},
            measurements=[Measurement(**sample_measurement_data)]
        )

        measurement = step.get_measurement("applied_pressure")

        assert measurement is not None
        assert measurement.measurement_type == "applied_pressure"
        assert measurement.unit == "Pa"


class TestMeasurement:
    """Test suite for Measurement class."""

    def test_measurement_creation(self, sample_measurement_data):
        """Test creating a Measurement object."""
        measurement = Measurement(**sample_measurement_data)

        assert measurement.measurement_type == "applied_pressure"
        assert measurement.unit == "Pa"
        assert measurement.target_value == 2400
        assert measurement.tolerance == 50

    def test_is_within_limits(self):
        """Test checking if value is within limits."""
        measurement = Measurement(
            measurement_type="pressure",
            unit="Pa",
            min_value=1000,
            max_value=3000
        )

        assert measurement.is_within_limits(2000) is True
        assert measurement.is_within_limits(500) is False
        assert measurement.is_within_limits(4000) is False

    def test_is_within_tolerance(self):
        """Test checking if value is within tolerance."""
        measurement = Measurement(
            measurement_type="pressure",
            unit="Pa",
            target_value=2400,
            tolerance=50
        )

        assert measurement.is_within_tolerance(2400) is True
        assert measurement.is_within_tolerance(2420) is True
        assert measurement.is_within_tolerance(2350) is True
        assert measurement.is_within_tolerance(2500) is False
        assert measurement.is_within_tolerance(2300) is False


class TestEquipment:
    """Test suite for Equipment class."""

    def test_equipment_creation(self):
        """Test creating an Equipment object."""
        equipment = Equipment(
            name="Pressure Sensor",
            type="sensor",
            model="PS-2000",
            calibration_required=True,
            calibration_interval_days=180
        )

        assert equipment.name == "Pressure Sensor"
        assert equipment.type == "sensor"
        assert equipment.calibration_required is True

    def test_needs_calibration(self):
        """Test checking if equipment needs calibration."""
        from datetime import datetime, timedelta

        equipment = Equipment(
            name="Test Equipment",
            type="sensor",
            calibration_required=True,
            calibration_interval_days=365
        )

        # Recently calibrated
        recent_date = datetime.now() - timedelta(days=30)
        assert equipment.needs_calibration(recent_date) is False

        # Needs calibration
        old_date = datetime.now() - timedelta(days=400)
        assert equipment.needs_calibration(old_date) is True
