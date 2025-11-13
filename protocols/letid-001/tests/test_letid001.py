"""
Test Suite for LETID-001 Protocol

Tests for validation and processing modules.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from validation import LETID001Validator, validate_module_id, validate_serial_number
from processor import LETID001Processor


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def validator():
    """Create validator instance."""
    schema_path = Path(__file__).parent.parent / 'schemas' / 'protocol.json'
    return LETID001Validator(str(schema_path))


@pytest.fixture
def processor():
    """Create processor instance."""
    schema_path = Path(__file__).parent.parent / 'schemas' / 'protocol.json'
    return LETID001Processor(str(schema_path))


@pytest.fixture
def valid_sample_info():
    """Valid sample information."""
    return {
        'module_id': 'MOD-12345',
        'manufacturer': 'SampleSolar Inc.',
        'model': 'SS-360-PERC',
        'serial_number': 'SN-2025-001',
        'cell_technology': 'mono-PERC',
        'rated_power': 360.0
    }


@pytest.fixture
def valid_initial_measurement():
    """Valid initial characterization measurement."""
    return {
        'pmax': 360.5,
        'voc': 48.2,
        'isc': 9.8,
        'vmp': 40.1,
        'imp': 8.99,
        'fill_factor': 76.5
    }


@pytest.fixture
def valid_periodic_measurement():
    """Valid periodic measurement."""
    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'elapsed_hours': 24.0,
        'pmax': 358.2,
        'voc': 48.1,
        'isc': 9.75,
        'module_temp': 75.5,
        'irradiance': 1005.0
    }


@pytest.fixture
def sample_time_series():
    """Sample time series data."""
    initial_pmax = 360.5
    data = []

    for hour in range(0, 301, 24):  # Every 24 hours for 300 hours
        # Simulate degradation
        degradation = -0.01 * hour  # -0.01% per hour
        pmax = initial_pmax * (1 + degradation / 100)

        data.append({
            'timestamp': (datetime.utcnow() + timedelta(hours=hour)).isoformat() + 'Z',
            'elapsed_hours': float(hour),
            'pmax': round(pmax, 2),
            'voc': 48.0 + np.random.normal(0, 0.1),
            'isc': 9.8 + np.random.normal(0, 0.05),
            'module_temp': 75.0 + np.random.normal(0, 1.5),
            'irradiance': 1000.0 + np.random.normal(0, 20)
        })

    return data


# =============================================================================
# Validation Tests
# =============================================================================

class TestSampleInfoValidation:
    """Test sample information validation."""

    def test_valid_sample_info(self, validator, valid_sample_info):
        """Test validation of valid sample info."""
        assert validator.validate_sample_info(valid_sample_info)
        assert len(validator.errors) == 0

    def test_missing_required_field(self, validator, valid_sample_info):
        """Test validation fails with missing required field."""
        del valid_sample_info['module_id']
        assert not validator.validate_sample_info(valid_sample_info)
        assert any('module_id' in error for error in validator.errors)

    def test_invalid_cell_technology(self, validator, valid_sample_info):
        """Test validation fails with invalid cell technology."""
        valid_sample_info['cell_technology'] = 'invalid-tech'
        assert not validator.validate_sample_info(valid_sample_info)
        assert any('cell_technology' in error for error in validator.errors)

    def test_invalid_type(self, validator, valid_sample_info):
        """Test validation fails with invalid type."""
        valid_sample_info['rated_power'] = 'not-a-number'
        assert not validator.validate_sample_info(valid_sample_info)
        assert any('rated_power' in error for error in validator.errors)


class TestMeasurementValidation:
    """Test measurement validation."""

    def test_valid_initial_measurement(self, validator, valid_initial_measurement):
        """Test validation of valid initial measurement."""
        assert validator.validate_measurement(
            valid_initial_measurement,
            'initial_characterization'
        )
        assert len(validator.errors) == 0

    def test_valid_periodic_measurement(self, validator, valid_periodic_measurement):
        """Test validation of valid periodic measurement."""
        assert validator.validate_measurement(
            valid_periodic_measurement,
            'periodic_monitoring'
        )
        assert len(validator.errors) == 0

    def test_missing_required_parameter(self, validator, valid_initial_measurement):
        """Test validation fails with missing required parameter."""
        del valid_initial_measurement['pmax']
        assert not validator.validate_measurement(
            valid_initial_measurement,
            'initial_characterization'
        )
        assert any('pmax' in error for error in validator.errors)

    def test_negative_value_warning(self, validator, valid_initial_measurement):
        """Test warning for negative value."""
        valid_initial_measurement['pmax'] = -10.0
        validator.validate_measurement(
            valid_initial_measurement,
            'initial_characterization'
        )
        assert any('pmax' in warning for warning in validator.warnings)

    def test_invalid_datetime(self, validator, valid_periodic_measurement):
        """Test validation fails with invalid datetime."""
        valid_periodic_measurement['timestamp'] = 'invalid-date'
        assert not validator.validate_measurement(
            valid_periodic_measurement,
            'periodic_monitoring'
        )
        assert any('timestamp' in error for error in validator.errors)


class TestTimeSeriesValidation:
    """Test time series validation."""

    def test_valid_time_series(self, validator, sample_time_series):
        """Test validation of valid time series."""
        assert validator.validate_time_series(sample_time_series)
        assert len(validator.errors) == 0

    def test_empty_time_series(self, validator):
        """Test validation fails with empty time series."""
        assert not validator.validate_time_series([])
        assert any('empty' in error.lower() for error in validator.errors)

    def test_time_ordering_warning(self, validator, sample_time_series):
        """Test warning for non-chronological ordering."""
        # Swap two measurements
        sample_time_series[1], sample_time_series[5] = \
            sample_time_series[5], sample_time_series[1]

        validator.validate_time_series(sample_time_series)
        assert any('chronological' in warning.lower() for warning in validator.warnings)


class TestAcceptanceCriteria:
    """Test acceptance criteria checking."""

    def test_pass_criteria(self, validator):
        """Test passing acceptance criteria."""
        result = validator.check_acceptance_criteria(360.0, 357.0)
        assert result['pass']
        assert result['power_degradation_percent'] > -5.0

    def test_fail_criteria(self, validator):
        """Test failing acceptance criteria."""
        result = validator.check_acceptance_criteria(360.0, 340.0)
        assert not result['pass']
        assert len(result['failures']) > 0

    def test_warning_criteria(self, validator):
        """Test warning threshold."""
        result = validator.check_acceptance_criteria(360.0, 349.0)
        assert len(result['warnings']) > 0


class TestCompleteValidation:
    """Test complete test data validation."""

    def test_complete_valid_test(self, validator, valid_sample_info,
                                 valid_initial_measurement, sample_time_series):
        """Test validation of complete valid test data."""
        test_data = {
            'sample_info': valid_sample_info,
            'initial_characterization': valid_initial_measurement,
            'time_series': sample_time_series,
            'final_characterization': {
                'pmax': 357.0,
                'voc': 48.0,
                'isc': 9.75,
                'vmp': 40.0,
                'imp': 8.93,
                'fill_factor': 76.2
            }
        }

        is_valid, report = validator.validate_complete_test(test_data)
        assert is_valid
        assert len(report['errors']) == 0

    def test_incomplete_test_data(self, validator, valid_sample_info):
        """Test validation fails with incomplete data."""
        test_data = {
            'sample_info': valid_sample_info
        }

        is_valid, report = validator.validate_complete_test(test_data)
        assert not is_valid
        assert len(report['errors']) > 0


class TestModuleIDValidation:
    """Test module ID format validation."""

    def test_valid_module_id(self):
        """Test valid module IDs."""
        assert validate_module_id('MOD-12345')
        assert validate_module_id('MODULE-ABC-123')
        assert validate_module_id('12345')

    def test_invalid_module_id(self):
        """Test invalid module IDs."""
        assert not validate_module_id('MOD')  # Too short
        assert not validate_module_id('A' * 51)  # Too long
        assert not validate_module_id('MOD@123')  # Invalid characters


# =============================================================================
# Processing Tests
# =============================================================================

class TestDegradationCalculations:
    """Test degradation calculations."""

    def test_calculate_degradation(self, processor):
        """Test degradation calculation."""
        deg = processor.calculate_degradation(360.0, 357.0)
        assert abs(deg - (-0.833)) < 0.01

    def test_calculate_degradation_rate(self, processor):
        """Test degradation rate calculation."""
        rate = processor.calculate_degradation_rate(-3.0, 300.0)
        assert abs(rate - (-0.01)) < 0.001

    def test_normalize_power(self, processor):
        """Test power normalization."""
        norm = processor.normalize_power(357.0, 360.0)
        assert abs(norm - 99.167) < 0.01


class TestTimeSeriesProcessing:
    """Test time series processing."""

    def test_process_time_series(self, processor, sample_time_series):
        """Test time series processing."""
        df = processor.process_time_series(sample_time_series, 360.5)

        assert 'normalized_power' in df.columns
        assert 'degradation_percent' in df.columns
        assert len(df) == len(sample_time_series)

    def test_detect_stabilization(self, processor):
        """Test stabilization detection."""
        # Create time series with stabilization at 200h
        data = []
        for hour in range(0, 301, 24):
            if hour < 200:
                pmax = 360.5 * (1 - 0.01 * hour / 100)
            else:
                pmax = 360.5 * 0.98  # Stable at 98%

            data.append({
                'elapsed_hours': float(hour),
                'pmax': pmax,
                'voc': 48.0,
                'isc': 9.8,
                'module_temp': 75.0,
                'irradiance': 1000.0
            })

        df = processor.process_time_series(data, 360.5)
        stabilization = processor.detect_stabilization(df)

        assert stabilization is not None
        assert stabilization >= 150  # Should detect around 200h


class TestStatistics:
    """Test statistical calculations."""

    def test_calculate_statistics(self, processor, sample_time_series):
        """Test statistics calculation."""
        df = processor.process_time_series(sample_time_series, 360.5)
        stats = processor.calculate_statistics(df)

        assert 'total_measurements' in stats
        assert 'duration_hours' in stats
        assert 'power_stats' in stats
        assert stats['total_measurements'] == len(sample_time_series)


class TestDegradationModel:
    """Test degradation model fitting."""

    def test_linear_model_fit(self, processor, sample_time_series):
        """Test linear model fitting."""
        df = processor.process_time_series(sample_time_series, 360.5)
        model = processor.fit_degradation_model(df)

        assert 'model_type' in model
        assert 'slope' in model or 'decay_rate' in model
        assert 'r_squared' in model

    def test_insufficient_data(self, processor):
        """Test model fitting with insufficient data."""
        data = [
            {'elapsed_hours': 0.0, 'pmax': 360.5, 'voc': 48.0, 'isc': 9.8,
             'module_temp': 75.0, 'irradiance': 1000.0}
        ]
        df = processor.process_time_series(data, 360.5)
        model = processor.fit_degradation_model(df)

        assert 'error' in model


class TestAnalysisReport:
    """Test analysis report generation."""

    def test_generate_report(self, processor, valid_sample_info,
                            valid_initial_measurement, sample_time_series):
        """Test complete analysis report generation."""
        test_data = {
            'sample_info': valid_sample_info,
            'initial_characterization': valid_initial_measurement,
            'time_series': sample_time_series,
            'final_characterization': {
                'pmax': 357.0,
                'voc': 48.0,
                'isc': 9.75,
                'vmp': 40.0,
                'imp': 8.93,
                'fill_factor': 76.2
            }
        }

        report = processor.generate_analysis_report(test_data)

        assert 'protocol_id' in report
        assert 'results' in report
        assert 'sample_info' in report
        assert report['results']['initial_pmax'] == valid_initial_measurement['pmax']


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests combining validation and processing."""

    def test_complete_workflow(self, validator, processor, valid_sample_info,
                              valid_initial_measurement, sample_time_series):
        """Test complete validation and processing workflow."""
        # Create complete test data
        test_data = {
            'sample_info': valid_sample_info,
            'initial_characterization': valid_initial_measurement,
            'time_series': sample_time_series,
            'final_characterization': {
                'pmax': 357.0,
                'voc': 48.0,
                'isc': 9.75,
                'vmp': 40.0,
                'imp': 8.93,
                'fill_factor': 76.2
            }
        }

        # Validate
        is_valid, validation_report = validator.validate_complete_test(test_data)
        assert is_valid

        # Process
        analysis_report = processor.generate_analysis_report(test_data)
        assert 'results' in analysis_report

        # Check acceptance criteria
        criteria = validator.check_acceptance_criteria(
            test_data['initial_characterization']['pmax'],
            test_data['final_characterization']['pmax']
        )
        assert 'pass' in criteria


# =============================================================================
# Run tests
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
