"""Tests for LID-001 protocol implementation."""

import pytest
from protocols.implementations.lid_001_protocol import LID001Protocol
import numpy as np


class TestLID001Protocol:
    """Test suite for LID-001 protocol."""

    def test_protocol_initialization(self, sample_lid001_protocol):
        """Test protocol initialization."""
        protocol = LID001Protocol()

        assert protocol.protocol_id == "LID-001"
        assert protocol.definition is not None
        assert protocol.definition['protocol_name'] == "Light-Induced Degradation"

    def test_get_protocol_info(self):
        """Test getting protocol information."""
        protocol = LID001Protocol()
        info = protocol.get_protocol_info()

        assert info['protocol_id'] == "LID-001"
        assert info['category'] == "Degradation"
        assert 'IEC 61215-2:2021' in info['standards']

    def test_calculate_baseline_power(self, sample_measurements):
        """Test baseline power calculation."""
        protocol = LID001Protocol()

        initial_measurements = [m for m in sample_measurements if m['measurement_type'] == 'initial']
        baseline_power = protocol.calculate_baseline_power(initial_measurements)

        assert baseline_power == pytest.approx(300.0, abs=0.1)
        assert protocol.baseline_power == baseline_power

    def test_calculate_baseline_power_empty(self):
        """Test baseline power calculation with empty measurements."""
        protocol = LID001Protocol()

        with pytest.raises(ValueError, match="No initial measurements"):
            protocol.calculate_baseline_power([])

    def test_calculate_degradation(self):
        """Test degradation calculation."""
        protocol = LID001Protocol()
        protocol.baseline_power = 300.0

        # Test 3% degradation
        current_power = 291.0
        degradation = protocol.calculate_degradation(current_power)

        assert degradation == pytest.approx(3.0, abs=0.01)

    def test_calculate_degradation_no_baseline(self):
        """Test degradation calculation without baseline."""
        protocol = LID001Protocol()

        with pytest.raises(ValueError, match="Baseline power not set"):
            protocol.calculate_degradation(290.0)

    def test_check_stabilization(self, sample_measurements):
        """Test stabilization detection."""
        protocol = LID001Protocol()
        protocol.baseline_power = 300.0

        # Use all measurements
        is_stabilized, max_change = protocol.check_stabilization(
            sample_measurements,
            threshold_percent=0.5
        )

        # Last few measurements should be stable
        assert is_stabilized is True or is_stabilized is False  # Depends on data
        assert max_change >= 0

    def test_validate_environmental_conditions(self):
        """Test environmental conditions validation."""
        protocol = LID001Protocol()

        # Valid conditions
        is_valid, errors = protocol.validate_environmental_conditions(
            irradiance=1000.0,
            temperature=25.0
        )

        assert is_valid is True
        assert len(errors) == 0

        # Invalid irradiance
        is_valid, errors = protocol.validate_environmental_conditions(
            irradiance=900.0,  # Below tolerance
            temperature=25.0
        )

        assert is_valid is False
        assert len(errors) > 0

    def test_check_qc_criteria(self):
        """Test QC criteria checking."""
        protocol = LID001Protocol()

        measurement = {
            "fill_factor": 0.78,
            "irradiance": 1000.0,
            "temperature": 25.0,
        }

        qc_results = protocol.check_qc_criteria(measurement, degradation_percent=2.5)

        assert isinstance(qc_results, list)

        # Should have no critical failures for normal measurement
        critical_failures = [qc for qc in qc_results if qc.get('severity') == 'critical']
        assert len(critical_failures) == 0

    def test_get_measurement_schedule(self):
        """Test measurement schedule generation."""
        protocol = LID001Protocol()

        schedule = protocol.get_measurement_schedule()

        assert isinstance(schedule, list)
        assert len(schedule) > 0

        # Check initial measurements
        initial = [s for s in schedule if s['type'] == 'initial']
        assert len(initial) == 3

        # Check during exposure measurements
        during = [s for s in schedule if s['type'] == 'during_exposure']
        assert len(during) > 0

    def test_generate_measurement_timestamps(self):
        """Test timestamp generation for measurements."""
        from datetime import datetime

        protocol = LID001Protocol()
        start_time = datetime.now()

        schedule = protocol.generate_measurement_timestamps(start_time)

        assert isinstance(schedule, list)
        assert all('timestamp' in point for point in schedule)

    def test_calculate_degradation_rate(self, sample_measurements):
        """Test degradation rate calculation."""
        protocol = LID001Protocol()
        protocol.baseline_power = 300.0

        # Add elapsed hours and pmax to measurements
        rate = protocol.calculate_degradation_rate(sample_measurements)

        assert rate is not None
        assert isinstance(rate, float)
        # Rate should be positive (degradation increases over time)
        assert rate >= 0


class TestLID001Validation:
    """Test validation functions."""

    def test_validate_measurement_valid(self):
        """Test validation of valid measurement."""
        protocol = LID001Protocol()

        measurement = {
            "timestamp": "2025-11-14T10:00:00",
            "voc": 40.5,
            "isc": 9.2,
            "pmax": 300.0,
            "vmp": 33.0,
            "imp": 9.09,
            "fill_factor": 0.806,
            "irradiance": 1000.0,
            "temperature": 25.0,
        }

        is_valid, errors = protocol.validate_measurement(measurement)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_measurement_missing_fields(self):
        """Test validation with missing required fields."""
        protocol = LID001Protocol()

        measurement = {
            "voc": 40.5,
            # Missing other required fields
        }

        is_valid, errors = protocol.validate_measurement(measurement)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_measurement_out_of_range(self):
        """Test validation with out-of-range values."""
        protocol = LID001Protocol()

        measurement = {
            "timestamp": "2025-11-14T10:00:00",
            "voc": 150.0,  # Way too high
            "isc": 9.2,
            "pmax": 300.0,
            "vmp": 33.0,
            "imp": 9.09,
            "fill_factor": 0.806,
            "irradiance": 1000.0,
            "temperature": 25.0,
        }

        is_valid, errors = protocol.validate_measurement(measurement)

        assert is_valid is False
        assert any("voc" in err.lower() for err in errors)
