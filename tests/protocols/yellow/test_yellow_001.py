"""
Unit Tests for YELLOW-001 Protocol

Tests for the EVA Yellowing Assessment Protocol implementation.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from protocols.yellow.yellow_001 import Yellow001Protocol, Sample
from utils.errors import ProtocolValidationError


class TestYellow001Protocol:
    """Test suite for Yellow001Protocol class."""

    def test_protocol_initialization(self, protocol_path):
        """Test protocol initialization."""
        protocol = Yellow001Protocol(protocol_path)

        assert protocol.protocol_id == "YELLOW-001"
        assert protocol.protocol_data is not None
        assert protocol.test_duration_hours == 1000
        assert protocol.temperature == 85
        assert protocol.humidity == 60

    def test_protocol_initialization_default_path(self):
        """Test protocol initialization with default path."""
        protocol = Yellow001Protocol()

        assert protocol.protocol_id == "YELLOW-001"
        assert protocol.protocol_data is not None

    def test_validate_inputs_valid(self, sample_data):
        """Test input validation with valid data."""
        protocol = Yellow001Protocol()

        result = protocol.validate_inputs(sample_data)

        assert result is True

    def test_validate_inputs_missing_field(self):
        """Test input validation with missing required field."""
        protocol = Yellow001Protocol()

        invalid_data = {'sample_id': 'TEST_001'}

        with pytest.raises(ProtocolValidationError, match="Missing required field"):
            protocol.validate_inputs(invalid_data)

    def test_validate_inputs_invalid_dimensions(self, sample_data):
        """Test input validation with invalid dimensions."""
        protocol = Yellow001Protocol()

        sample_data['sample_dimensions'] = {'length_mm': 100}  # Missing width and thickness

        with pytest.raises(ProtocolValidationError, match="Missing dimension"):
            protocol.validate_inputs(sample_data)

    def test_validate_inputs_negative_dimension(self, sample_data):
        """Test input validation with negative dimension."""
        protocol = Yellow001Protocol()

        sample_data['sample_dimensions']['length_mm'] = -10

        with pytest.raises(ProtocolValidationError, match="Invalid dimension value"):
            protocol.validate_inputs(sample_data)

    def test_execute_test_single_sample(self):
        """Test executing protocol with a single sample."""
        protocol = Yellow001Protocol()

        sample = Sample(
            sample_id='EVA_001',
            material_type='EVA',
            dimensions={'length_mm': 100, 'width_mm': 100, 'thickness_mm': 3}
        )

        results = protocol.execute_test([sample])

        assert results is not None
        assert 'session_id' in results
        assert results['protocol_id'] == 'YELLOW-001'
        assert results['total_samples'] == 1
        assert len(results['samples']) == 1
        assert 'start_time' in results
        assert 'end_time' in results

    def test_execute_test_multiple_samples(self):
        """Test executing protocol with multiple samples."""
        protocol = Yellow001Protocol()

        samples = [
            Sample(sample_id=f'EVA_{i:03d}', material_type='EVA')
            for i in range(1, 4)
        ]

        results = protocol.execute_test(samples)

        assert results['total_samples'] == 3
        assert len(results['samples']) == 3

    def test_measurement_collection(self):
        """Test that measurements are collected correctly."""
        protocol = Yellow001Protocol()

        sample = Sample(sample_id='EVA_001', material_type='EVA')
        results = protocol.execute_test([sample])

        sample_data = results['samples'][0]
        time_points = sample_data['time_points']

        # Should have 11 time points (0, 100, 200, ..., 1000)
        assert len(time_points) == 11

        # Check first time point (baseline)
        baseline = time_points[0]
        assert baseline['time_point_hours'] == 0
        assert 'yellow_index' in baseline
        assert 'color_shift' in baseline
        assert 'light_transmittance' in baseline
        assert 'L_star' in baseline
        assert 'a_star' in baseline
        assert 'b_star' in baseline

        # Color shift should be 0 at baseline
        assert baseline['color_shift'] == 0.0

        # Check that values increase/decrease as expected
        final = time_points[-1]
        assert final['yellow_index'] > baseline['yellow_index']
        assert final['color_shift'] > 0
        assert final['light_transmittance'] < baseline['light_transmittance']

    def test_baseline_measurements(self):
        """Test baseline measurement collection."""
        protocol = Yellow001Protocol()

        sample = Sample(sample_id='EVA_001', material_type='EVA')
        baseline = protocol._get_baseline(sample)

        assert baseline is not None
        assert 'yellow_index' in baseline
        assert 'light_transmittance' in baseline
        assert 'L_star' in baseline
        assert 'a_star' in baseline
        assert 'b_star' in baseline
        assert baseline['color_shift'] == 0.0

        # Check reasonable baseline values for fresh EVA
        assert 0 <= baseline['yellow_index'] <= 2
        assert 90 <= baseline['light_transmittance'] <= 100
        assert 90 <= baseline['L_star'] <= 100

    def test_analyze_results(self):
        """Test results analysis."""
        protocol = Yellow001Protocol()

        sample = Sample(sample_id='EVA_001', material_type='EVA')
        protocol.execute_test([sample])

        analysis = protocol.analyze_results()

        assert analysis is not None
        assert 'protocol_id' in analysis
        assert 'test_session_id' in analysis
        assert 'sample_summaries' in analysis
        assert 'batch_statistics' in analysis
        assert 'overall_status' in analysis

        # Check sample summary
        summary = analysis['sample_summaries']['EVA_001']
        assert 'final_values' in summary
        assert 'degradation_rates' in summary
        assert 'status' in summary
        assert summary['status'] in ['PASS', 'WARNING', 'FAIL']

    def test_pass_fail_evaluation(self):
        """Test pass/fail evaluation logic."""
        protocol = Yellow001Protocol()

        # Test PASS case
        result_pass = protocol.evaluate_pass_fail(12.0, 'yellow_index')
        assert result_pass['status'] == 'PASS'

        # Test WARNING case
        result_warning = protocol.evaluate_pass_fail(11.0, 'yellow_index')
        assert result_warning['status'] == 'WARNING'

        # Test FAIL case
        result_fail = protocol.evaluate_pass_fail(16.0, 'yellow_index')
        assert result_fail['status'] == 'FAIL'

    def test_determine_status(self):
        """Test status determination logic."""
        protocol = Yellow001Protocol()

        # PASS
        assert protocol._determine_status(8.0, 4.0, 85.0) == "PASS"

        # WARNING
        assert protocol._determine_status(11.0, 4.0, 85.0) == "WARNING"
        assert protocol._determine_status(8.0, 6.0, 78.0) == "WARNING"

        # FAIL
        assert protocol._determine_status(16.0, 4.0, 85.0) == "FAIL"
        assert protocol._determine_status(8.0, 9.0, 85.0) == "FAIL"
        assert protocol._determine_status(8.0, 4.0, 70.0) == "FAIL"

    def test_batch_statistics(self):
        """Test batch statistics calculation."""
        protocol = Yellow001Protocol()

        samples = [
            Sample(sample_id=f'EVA_{i:03d}', material_type='EVA')
            for i in range(1, 4)
        ]

        protocol.execute_test(samples)
        analysis = protocol.analyze_results()

        stats = analysis['batch_statistics']

        assert 'yellow_index' in stats
        assert 'color_shift' in stats
        assert 'light_transmittance' in stats

        # Check that each stat has required fields
        for param in ['yellow_index', 'color_shift', 'light_transmittance']:
            assert 'mean' in stats[param]
            assert 'std_dev' in stats[param]
            assert 'min' in stats[param]
            assert 'max' in stats[param]

    def test_delta_e_calculation(self):
        """Test Delta E color difference calculation."""
        protocol = Yellow001Protocol()

        # Test with identical colors (Delta E should be 0)
        de_zero = protocol._calculate_delta_e(95.0, -0.5, 0.5, 95.0, -0.5, 0.5)
        assert abs(de_zero) < 0.01

        # Test with different colors (Delta E should be > 0)
        de_nonzero = protocol._calculate_delta_e(95.0, -0.5, 0.5, 90.0, 0.0, 5.0)
        assert de_nonzero > 0

    def test_generate_report(self):
        """Test report generation."""
        protocol = Yellow001Protocol()

        sample = Sample(sample_id='EVA_001', material_type='EVA')
        protocol.execute_test([sample])

        # Generate JSON report
        report = protocol.generate_report('JSON')

        assert report is not None
        assert isinstance(report, str)
        assert 'YELLOW-001' in report

    def test_get_protocol_info(self):
        """Test getting protocol information."""
        protocol = Yellow001Protocol()

        info = protocol.get_protocol_info()

        assert info['protocol_id'] == 'YELLOW-001'
        assert info['protocol_name'] == 'EVA Yellowing Assessment'
        assert 'version' in info
        assert 'description' in info
        assert 'category' in info
        assert 'test_duration_hours' in info
        assert 'measurement_parameters' in info

    def test_session_id_generation(self):
        """Test that session IDs are unique."""
        protocol1 = Yellow001Protocol()
        protocol2 = Yellow001Protocol()

        session_id1 = protocol1._generate_session_id()
        session_id2 = protocol2._generate_session_id()

        assert session_id1 != session_id2
        assert 'YELLOW-001' in session_id1
        assert 'YELLOW-001' in session_id2


class TestSampleClass:
    """Test suite for Sample class."""

    def test_sample_creation(self):
        """Test creating a sample."""
        sample = Sample(
            sample_id='EVA_001',
            material_type='EVA',
            dimensions={'length_mm': 100, 'width_mm': 100, 'thickness_mm': 3},
            batch_code='BATCH_001'
        )

        assert sample.sample_id == 'EVA_001'
        assert sample.material_type == 'EVA'
        assert sample.batch_code == 'BATCH_001'
        assert sample.dimensions['length_mm'] == 100

    def test_sample_defaults(self):
        """Test sample creation with defaults."""
        sample = Sample(sample_id='EVA_001')

        assert sample.material_type == 'EVA'
        assert 'length_mm' in sample.dimensions
        assert sample.batch_code.startswith('BATCH_')
