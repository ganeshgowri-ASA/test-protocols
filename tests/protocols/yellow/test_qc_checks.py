"""
Unit Tests for YELLOW-001 QC Checks

Tests for quality control module.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from protocols.yellow.qc_checks import QualityControl


@pytest.fixture
def protocol_data():
    """Mock protocol data."""
    return {
        'quality_controls': [
            {
                'qc_id': 'baseline_control',
                'type': 'INITIAL_REFERENCE',
                'name': 'Baseline Measurement'
            },
            {
                'qc_id': 'equipment_calibration',
                'type': 'CALIBRATION',
                'name': 'Equipment Calibration Check'
            }
        ]
    }


class TestQualityControl:
    """Test suite for QualityControl class."""

    def test_qc_initialization(self, protocol_data):
        """Test QC checker initialization."""
        qc = QualityControl(protocol_data)

        assert qc is not None
        assert len(qc.qc_config) == 2

    def test_check_baseline_control_pass(self, protocol_data, mock_baseline_measurements):
        """Test baseline control check with good data."""
        qc = QualityControl(protocol_data)

        result = qc.check_baseline_control(mock_baseline_measurements)

        assert result['status'] == 'PASS'
        assert result['qc_id'] == 'baseline_control'

    def test_check_baseline_control_warning(self, protocol_data):
        """Test baseline control check with warning data."""
        qc = QualityControl(protocol_data)

        # High YI for "fresh" EVA
        bad_baseline = {
            'yellow_index': 3.0,
            'light_transmittance': 85.0,
            'L_star': 85.0
        }

        result = qc.check_baseline_control(bad_baseline)

        assert result['status'] == 'WARNING'
        assert len(result['issues']) > 0

    def test_check_equipment_calibration_pass(self, protocol_data):
        """Test equipment calibration check with good data."""
        qc = QualityControl(protocol_data)

        calibration_data = {
            'white_tile': {'deviation_percent': 0.5},
            'green_tile': {'deviation_percent': -0.8},
            'gray_tile': {'deviation_percent': 0.3}
        }

        result = qc.check_equipment_calibration(calibration_data)

        assert result['status'] == 'PASS'

    def test_check_equipment_calibration_fail(self, protocol_data):
        """Test equipment calibration check with bad data."""
        qc = QualityControl(protocol_data)

        calibration_data = {
            'white_tile': {'deviation_percent': 3.0}  # Exceeds ±2% tolerance
        }

        result = qc.check_equipment_calibration(calibration_data)

        assert result['status'] == 'FAIL'
        assert len(result['issues']) > 0

    def test_check_environmental_conditions_pass(self, protocol_data):
        """Test environmental conditions check with good data."""
        qc = QualityControl(protocol_data)

        conditions = {
            'temperature': 85.5,
            'humidity': 61.0,
            'uv_intensity': 98.0
        }

        test_parameters = {
            'temperature_celsius': 85,
            'temperature_tolerance': 2,
            'humidity_percent': 60,
            'humidity_tolerance': 5,
            'light_intensity_mw_cm2': 100
        }

        result = qc.check_environmental_conditions(conditions, test_parameters)

        assert result['status'] == 'PASS'

    def test_check_environmental_conditions_fail(self, protocol_data):
        """Test environmental conditions check with out-of-spec data."""
        qc = QualityControl(protocol_data)

        conditions = {
            'temperature': 90.0,  # Too high
            'humidity': 70.0,  # Too high
            'uv_intensity': 120.0  # Too high
        }

        test_parameters = {
            'temperature_celsius': 85,
            'temperature_tolerance': 2,
            'humidity_percent': 60,
            'humidity_tolerance': 5,
            'light_intensity_mw_cm2': 100
        }

        result = qc.check_environmental_conditions(conditions, test_parameters)

        assert result['status'] == 'FAIL'
        assert len(result['issues']) > 0

    def test_check_reference_sample_stability_pass(self, protocol_data, mock_baseline_measurements):
        """Test reference sample stability check with stable data."""
        qc = QualityControl(protocol_data)

        reference_current = mock_baseline_measurements.copy()
        reference_current['yellow_index'] *= 1.02  # 2% change - within tolerance

        result = qc.check_reference_sample_stability(
            mock_baseline_measurements,
            reference_current
        )

        assert result['status'] == 'PASS'

    def test_check_reference_sample_stability_fail(self, protocol_data, mock_baseline_measurements):
        """Test reference sample stability check with unstable data."""
        qc = QualityControl(protocol_data)

        reference_current = mock_baseline_measurements.copy()
        reference_current['yellow_index'] *= 1.10  # 10% change - exceeds tolerance

        result = qc.check_reference_sample_stability(
            mock_baseline_measurements,
            reference_current
        )

        assert result['status'] == 'FAIL'
        assert len(result['issues']) > 0

    def test_check_measurement_repeatability_pass(self, protocol_data):
        """Test measurement repeatability with good data."""
        qc = QualityControl(protocol_data)

        measurements = [10.0, 10.1, 9.9, 10.2]  # Low variation

        result = qc.check_measurement_repeatability(measurements, 'yellow_index', 5.0)

        assert result['status'] == 'PASS'

    def test_check_measurement_repeatability_fail(self, protocol_data):
        """Test measurement repeatability with high variation."""
        qc = QualityControl(protocol_data)

        measurements = [10.0, 12.0, 8.0, 15.0]  # High variation

        result = qc.check_measurement_repeatability(measurements, 'yellow_index', 5.0)

        assert result['status'] == 'FAIL'

    def test_get_qc_summary(self, protocol_data):
        """Test QC summary generation."""
        qc = QualityControl(protocol_data)

        # Run some checks
        qc.check_baseline_control({'yellow_index': 0.5, 'light_transmittance': 95, 'L_star': 95})
        qc.check_equipment_calibration({'white_tile': {'deviation_percent': 0.5}})

        summary = qc.get_qc_summary()

        assert summary['total_checks'] == 2
        assert 'status_counts' in summary
        assert 'overall_status' in summary
        assert 'pass_rate' in summary
