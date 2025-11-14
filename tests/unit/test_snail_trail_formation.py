"""
Unit Tests for SNAIL-001 - Snail Trail Formation Protocol
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from protocols.degradation.snail_trail_formation import SnailTrailFormationProtocol
from protocols.base_protocol import ProtocolConfig, ProtocolResult


@pytest.fixture
def protocol():
    """Fixture to create a protocol instance"""
    config_path = Path(__file__).parent.parent.parent / "protocols" / "degradation" / "snail_trail_formation.json"
    return SnailTrailFormationProtocol(config_path)


@pytest.fixture
def sample_input_data():
    """Fixture for sample input parameters"""
    return {
        'module_id': 'TEST-MODULE-001',
        'manufacturer': 'Test Solar Inc.',
        'model_number': 'TS-400W',
        'cell_technology': 'mono-PERC',
        'nameplate_power_w': 400.0,
        'initial_isc_a': 10.5,
        'initial_voc_v': 48.2,
        'initial_pmax_w': 400.0,
        'initial_ff_percent': 79.2,
        'test_start_date': '2025-01-14',
        'operator_id': 'OP-123'
    }


@pytest.fixture
def sample_measurements():
    """Fixture for sample measurement data"""
    return [
        {
            'inspection_hour': 0,
            'visual_snail_trail_severity': 'none',
            'affected_cells_count': 0,
            'affected_area_percent': 0.0,
            'pmax_w': 400.0,
            'isc_a': 10.5,
            'voc_v': 48.2,
            'ff_percent': 79.2,
            'notes': 'Initial measurement'
        },
        {
            'inspection_hour': 168,
            'visual_snail_trail_severity': 'minor',
            'affected_cells_count': 2,
            'affected_area_percent': 1.5,
            'pmax_w': 398.0,
            'isc_a': 10.45,
            'voc_v': 48.1,
            'ff_percent': 79.0,
            'notes': 'First inspection - minor trails visible'
        },
        {
            'inspection_hour': 336,
            'visual_snail_trail_severity': 'minor',
            'affected_cells_count': 4,
            'affected_area_percent': 3.0,
            'pmax_w': 396.5,
            'isc_a': 10.42,
            'voc_v': 48.0,
            'ff_percent': 78.9,
            'notes': 'Trail progression observed'
        },
        {
            'inspection_hour': 504,
            'visual_snail_trail_severity': 'moderate',
            'affected_cells_count': 7,
            'affected_area_percent': 5.2,
            'pmax_w': 394.0,
            'isc_a': 10.38,
            'voc_v': 47.9,
            'ff_percent': 78.7,
            'notes': 'Moderate trails developing'
        },
        {
            'inspection_hour': 1000,
            'visual_snail_trail_severity': 'moderate',
            'affected_cells_count': 10,
            'affected_area_percent': 8.5,
            'pmax_w': 390.0,
            'isc_a': 10.3,
            'voc_v': 47.8,
            'ff_percent': 78.5,
            'notes': 'Final measurement - moderate trail formation'
        }
    ]


class TestProtocolInitialization:
    """Test protocol initialization and configuration loading"""

    def test_protocol_loads_config(self, protocol):
        """Test that protocol loads configuration correctly"""
        assert protocol.config is not None
        assert protocol.config.protocol_id == "SNAIL-001"
        assert protocol.config.name == "Snail Trail Formation Test"
        assert protocol.config.category == "Degradation"

    def test_protocol_config_has_required_fields(self, protocol):
        """Test that configuration has all required fields"""
        assert hasattr(protocol.config, 'test_conditions')
        assert hasattr(protocol.config, 'input_parameters')
        assert hasattr(protocol.config, 'measurements')
        assert hasattr(protocol.config, 'qc_checks')

    def test_protocol_info_method(self, protocol):
        """Test get_protocol_info method"""
        info = protocol.get_protocol_info()
        assert info['protocol_id'] == "SNAIL-001"
        assert info['category'] == "Degradation"
        assert 'test_conditions' in info


class TestInputValidation:
    """Test input parameter validation"""

    def test_valid_input_passes_validation(self, protocol, sample_input_data):
        """Test that valid input data passes validation"""
        is_valid, errors = protocol.validate_input(sample_input_data)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_field_fails(self, protocol, sample_input_data):
        """Test that missing required field fails validation"""
        incomplete_data = sample_input_data.copy()
        del incomplete_data['module_id']

        is_valid, errors = protocol.validate_input(incomplete_data)
        assert not is_valid
        assert any('module_id' in error for error in errors)

    def test_wrong_type_fails_validation(self, protocol, sample_input_data):
        """Test that wrong data type fails validation"""
        invalid_data = sample_input_data.copy()
        invalid_data['initial_pmax_w'] = "not a number"  # Should be float

        is_valid, errors = protocol.validate_input(invalid_data)
        assert not is_valid

    def test_optional_field_can_be_missing(self, protocol, sample_input_data):
        """Test that optional fields can be omitted"""
        data = sample_input_data.copy()
        # chamber_id is optional
        is_valid, errors = protocol.validate_input(data)
        assert is_valid


class TestProtocolExecution:
    """Test protocol execution"""

    def test_protocol_runs_successfully(self, protocol, sample_input_data, sample_measurements):
        """Test that protocol runs successfully with valid data"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)

        assert result is not None
        assert result.status == "completed"
        assert result.protocol_id == "SNAIL-001"
        assert len(result.errors) == 0

    def test_protocol_fails_with_no_measurements(self, protocol, sample_input_data):
        """Test that protocol fails when no measurements provided"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': []
        }

        result = protocol.run(test_data)

        assert result.status == "failed"
        assert len(result.errors) > 0

    def test_protocol_fails_with_invalid_input(self, protocol, sample_measurements):
        """Test that protocol fails with invalid input data"""
        test_data = {
            'input_params': {'module_id': 'TEST'},  # Missing required fields
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)

        assert result.status == "failed"
        assert len(result.errors) > 0


class TestAnalysis:
    """Test analysis functionality"""

    def test_analysis_calculates_degradation(self, protocol, sample_input_data, sample_measurements):
        """Test that analysis correctly calculates degradation"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        analysis = result.analysis_results

        assert 'power_degradation' in analysis
        assert 'isc_degradation' in analysis
        assert 'voc_degradation' in analysis
        assert 'ff_degradation' in analysis

        # Check power degradation calculation
        power_deg = analysis['power_degradation']
        expected_deg = ((400.0 - 390.0) / 400.0) * 100  # 2.5%
        assert abs(power_deg['degradation_percent'] - expected_deg) < 0.01

    def test_analysis_tracks_snail_trail_progression(self, protocol, sample_input_data, sample_measurements):
        """Test that analysis tracks snail trail progression"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        analysis = result.analysis_results

        assert 'snail_trail_metrics' in analysis
        metrics = analysis['snail_trail_metrics']

        assert metrics['final_affected_area_percent'] == 8.5
        assert metrics['final_affected_cells'] == 10
        assert metrics['final_severity'] == 'moderate'

    def test_analysis_calculates_progression_rate(self, protocol, sample_input_data, sample_measurements):
        """Test that progression rate is calculated"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        analysis = result.analysis_results

        metrics = analysis['snail_trail_metrics']
        expected_rate = 8.5 / 1000  # 0.0085 %/hour
        assert abs(metrics['progression_rate_percent_per_hour'] - expected_rate) < 0.0001

    def test_analysis_includes_correlation(self, protocol, sample_input_data, sample_measurements):
        """Test that correlation analysis is performed"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        analysis = result.analysis_results

        assert 'correlation_snail_trail_power_loss' in analysis
        correlation = analysis['correlation_snail_trail_power_loss']
        assert 'pearson_correlation' in correlation
        assert 'interpretation' in correlation


class TestQualityControl:
    """Test quality control checks"""

    def test_qc_passes_with_good_data(self, protocol, sample_input_data, sample_measurements):
        """Test that QC passes with good quality data"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)

        assert result.qc_passed
        assert 'data_completeness' in result.qc_details
        assert 'measurement_consistency' in result.qc_details

    def test_qc_checks_data_completeness(self, protocol, sample_input_data, sample_measurements):
        """Test data completeness check"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        qc = result.qc_details['data_completeness']

        assert 'passed' in qc
        assert 'expected_intervals' in qc
        assert 'actual_intervals' in qc

    def test_qc_checks_measurement_consistency(self, protocol, sample_input_data, sample_measurements):
        """Test measurement consistency check"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        qc = result.qc_details['measurement_consistency']

        assert qc['passed']

    def test_qc_fails_with_inconsistent_data(self, protocol, sample_input_data):
        """Test that QC fails with physically impossible measurements"""
        bad_measurements = [
            {
                'inspection_hour': 0,
                'visual_snail_trail_severity': 'none',
                'affected_cells_count': 0,
                'affected_area_percent': 0.0,
                'pmax_w': 500.0,  # Pmax > Isc * Voc (impossible)
                'isc_a': 10.0,
                'voc_v': 40.0,
                'ff_percent': 150.0,  # FF > 100% (impossible)
                'notes': 'Bad data'
            }
        ]

        test_data = {
            'input_params': sample_input_data,
            'measurements': bad_measurements
        }

        result = protocol.run(test_data)
        assert not result.qc_passed


class TestPassFailCriteria:
    """Test pass/fail evaluation"""

    def test_passing_module(self, protocol, sample_input_data, sample_measurements):
        """Test that module with acceptable degradation passes"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)
        pass_fail = result.analysis_results['pass_fail']

        # With 2.5% power degradation and 8.5% area, should pass
        assert pass_fail['power_degradation_criterion']['passed']
        assert pass_fail['affected_area_criterion']['passed']
        assert pass_fail['overall']['passed']

    def test_failing_module_power_degradation(self, protocol, sample_input_data):
        """Test that module with excessive power degradation fails"""
        failing_measurements = [
            {
                'inspection_hour': 0,
                'visual_snail_trail_severity': 'none',
                'affected_cells_count': 0,
                'affected_area_percent': 0.0,
                'pmax_w': 400.0,
                'isc_a': 10.5,
                'voc_v': 48.2,
                'ff_percent': 79.2,
                'notes': 'Initial'
            },
            {
                'inspection_hour': 1000,
                'visual_snail_trail_severity': 'severe',
                'affected_cells_count': 30,
                'affected_area_percent': 15.0,
                'pmax_w': 370.0,  # 7.5% degradation - exceeds 5% limit
                'isc_a': 10.0,
                'voc_v': 47.5,
                'ff_percent': 77.0,
                'notes': 'Final - severe degradation'
            }
        ]

        test_data = {
            'input_params': sample_input_data,
            'measurements': failing_measurements
        }

        result = protocol.run(test_data)
        pass_fail = result.analysis_results['pass_fail']

        assert not pass_fail['power_degradation_criterion']['passed']
        assert not pass_fail['affected_area_criterion']['passed']
        assert not pass_fail['overall']['passed']


class TestReportGeneration:
    """Test report generation"""

    def test_report_generation_creates_file(self, protocol, sample_input_data, sample_measurements, tmp_path):
        """Test that report generation creates a PDF file"""
        test_data = {
            'input_params': sample_input_data,
            'measurements': sample_measurements
        }

        result = protocol.run(test_data)

        # Generate report
        report_path = protocol.generate_report(tmp_path)

        assert report_path.exists()
        assert report_path.suffix == '.pdf'
        assert report_path.stat().st_size > 0

    def test_report_generation_fails_without_results(self, protocol, tmp_path):
        """Test that report generation fails without running protocol first"""
        with pytest.raises(ValueError, match="No results available"):
            protocol.generate_report(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
