"""
Unit Tests for TEMP-001 Validator

Tests the validation module for data quality checks according to IEC 60891.

Author: ASA PV Testing
Date: 2025-11-14
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.validator import TEMP001Validator, Severity, ValidationResult


@pytest.fixture
def validator():
    """Create validator instance"""
    return TEMP001Validator()


@pytest.fixture
def valid_data():
    """Valid measurement data that should pass all checks"""
    return pd.DataFrame({
        'module_temperature': [20.0, 30.0, 40.0, 50.0, 60.0, 70.0],
        'ambient_temperature': [18.5, 28.2, 38.1, 47.9, 57.8, 67.5],
        'irradiance': [1000, 1005, 998, 1002, 997, 1001],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'vmp': [31.5, 30.85, 30.2, 29.55, 28.9, 28.25],
        'imp': [8.25, 8.17, 8.09, 8.01, 7.93, 7.85],
        'pmax': [259.88, 252.05, 244.32, 236.70, 229.18, 221.76]
    })


@pytest.fixture
def insufficient_temp_range_data():
    """Data with insufficient temperature range (<30°C)"""
    return pd.DataFrame({
        'module_temperature': [20.0, 25.0, 30.0, 35.0, 40.0],
        'pmax': [260, 254, 248, 242, 236],
        'voc': [38.5, 38.1, 37.7, 37.3, 36.9],
        'isc': [9.20, 9.23, 9.26, 9.29, 9.32],
        'irradiance': [1000, 1000, 1000, 1000, 1000]
    })


@pytest.fixture
def insufficient_measurements_data():
    """Data with too few measurements"""
    return pd.DataFrame({
        'module_temperature': [20.0, 30.0, 40.0],
        'pmax': [260, 252, 244],
        'voc': [38.5, 37.8, 37.1],
        'isc': [9.20, 9.25, 9.30],
        'irradiance': [1000, 1000, 1000]
    })


class TestFieldValidation:
    """Test individual field validation"""

    def test_valid_temperature(self, validator):
        """Test validation of valid temperature value"""
        result = validator.validate_field_value('module_temperature', 25.0)
        assert result.status == 'pass'

    def test_temperature_out_of_range_low(self, validator):
        """Test validation of temperature below minimum"""
        result = validator.validate_field_value('module_temperature', -30.0)
        assert result.status in ['fail', 'warning']

    def test_temperature_out_of_range_high(self, validator):
        """Test validation of temperature above maximum"""
        result = validator.validate_field_value('module_temperature', 100.0)
        assert result.status in ['fail', 'warning']

    def test_missing_required_field(self, validator):
        """Test validation of missing required field"""
        result = validator.validate_field_value('module_temperature', None)
        assert result.status == 'fail'
        assert result.severity == Severity.CRITICAL

    def test_valid_voltage(self, validator):
        """Test validation of valid voltage value"""
        result = validator.validate_field_value('voc', 37.5)
        assert result.status == 'pass'

    def test_valid_current(self, validator):
        """Test validation of valid current value"""
        result = validator.validate_field_value('isc', 9.25)
        assert result.status == 'pass'

    def test_valid_power(self, validator):
        """Test validation of valid power value"""
        result = validator.validate_field_value('pmax', 250.0)
        assert result.status == 'pass'


class TestDataCompletenessCheck:
    """Test data completeness validation"""

    def test_complete_data(self, validator, valid_data):
        """Test that complete data passes"""
        result = validator._check_data_completeness(valid_data)
        assert result.status == 'pass'

    def test_missing_columns(self, validator):
        """Test detection of missing required columns"""
        incomplete_data = pd.DataFrame({
            'module_temperature': [20, 30, 40],
            'pmax': [260, 252, 244]
            # Missing voc, isc
        })

        result = validator._check_data_completeness(incomplete_data)
        assert result.status == 'fail'
        assert result.severity == Severity.CRITICAL

    def test_missing_values(self, validator, valid_data):
        """Test detection of missing values in required fields"""
        data_with_nan = valid_data.copy()
        data_with_nan.loc[2, 'voc'] = np.nan

        result = validator._check_data_completeness(data_with_nan)
        assert result.status in ['warning', 'fail']


class TestTemperatureRangeCheck:
    """Test temperature range validation"""

    def test_sufficient_temperature_range(self, validator, valid_data):
        """Test that sufficient temperature range passes"""
        result = validator._check_temperature_range(valid_data)
        assert result.status == 'pass'

        # Check that temperature range is reported correctly
        assert result.details['actual_range'] >= 30.0

    def test_insufficient_temperature_range(self, validator, insufficient_temp_range_data):
        """Test that insufficient temperature range fails"""
        result = validator._check_temperature_range(insufficient_temp_range_data)
        assert result.status == 'fail'
        assert result.severity == Severity.CRITICAL

        # Should report the actual insufficient range
        assert result.details['actual_range'] < 30.0

    def test_exact_minimum_range(self, validator):
        """Test with exactly minimum temperature range (30°C)"""
        exact_data = pd.DataFrame({
            'module_temperature': [20.0, 30.0, 40.0, 50.0],
            'pmax': [260, 252, 244, 236],
            'voc': [38.5, 37.8, 37.1, 36.4],
            'isc': [9.20, 9.25, 9.30, 9.35]
        })

        result = validator._check_temperature_range(exact_data)
        assert result.status == 'pass'


class TestMeasurementCountCheck:
    """Test measurement count validation"""

    def test_sufficient_measurements(self, validator, valid_data):
        """Test that sufficient measurements pass"""
        result = validator._check_measurement_count(valid_data)
        assert result.status == 'pass'

    def test_insufficient_measurements(self, validator, insufficient_measurements_data):
        """Test that insufficient measurements fail"""
        result = validator._check_measurement_count(insufficient_measurements_data)
        assert result.status == 'fail'
        assert result.severity == Severity.CRITICAL

    def test_exact_minimum_measurements(self, validator):
        """Test with exactly minimum number of measurements (5)"""
        exact_data = pd.DataFrame({
            'module_temperature': [20, 30, 40, 50, 60],
            'pmax': [260, 252, 244, 236, 228],
            'voc': [38.5, 37.8, 37.1, 36.4, 35.7],
            'isc': [9.20, 9.25, 9.30, 9.35, 9.40]
        })

        result = validator._check_measurement_count(exact_data)
        assert result.status == 'pass'


class TestIrradianceStabilityCheck:
    """Test irradiance stability validation"""

    def test_stable_irradiance(self, validator, valid_data):
        """Test that stable irradiance passes"""
        result = validator._check_irradiance_stability(valid_data)
        assert result.status == 'pass'

        # Variation should be within threshold
        assert result.details['variation_percent'] < 2.0

    def test_unstable_irradiance(self, validator):
        """Test that unstable irradiance triggers warning"""
        unstable_data = pd.DataFrame({
            'module_temperature': [20, 30, 40, 50, 60],
            'pmax': [260, 252, 244, 236, 228],
            'voc': [38.5, 37.8, 37.1, 36.4, 35.7],
            'isc': [9.20, 9.25, 9.30, 9.35, 9.40],
            'irradiance': [1000, 1050, 950, 1000, 980]  # High variation
        })

        result = validator._check_irradiance_stability(unstable_data)
        assert result.status == 'warning'
        assert result.severity == Severity.WARNING

    def test_missing_irradiance_data(self, validator):
        """Test handling when irradiance data is missing"""
        data_no_irrad = pd.DataFrame({
            'module_temperature': [20, 30, 40],
            'pmax': [260, 252, 244],
            'voc': [38.5, 37.8, 37.1],
            'isc': [9.20, 9.25, 9.30]
        })

        result = validator._check_irradiance_stability(data_no_irrad)
        assert result.status == 'info'


class TestCoefficientValidation:
    """Test temperature coefficient validation"""

    def test_valid_coefficients(self, validator):
        """Test that valid coefficients pass"""
        results = validator.validate_coefficients(
            alpha_pmp=-0.40,
            beta_voc=-0.32,
            alpha_isc=0.05,
            r_squared_pmp=0.998,
            r_squared_voc=0.999,
            r_squared_isc=0.997
        )

        # Should have results for each coefficient
        assert len(results) > 0

        # All R² checks should pass
        r_squared_results = [r for r in results if 'r_squared' in r.check_id]
        assert all(r.status == 'pass' for r in r_squared_results)

    def test_low_r_squared_warning(self, validator):
        """Test that low R² triggers warning"""
        results = validator.validate_coefficients(
            alpha_pmp=-0.40,
            beta_voc=-0.32,
            alpha_isc=0.05,
            r_squared_pmp=0.90,  # Below 0.95 threshold
            r_squared_voc=0.92,
            r_squared_isc=0.88
        )

        r_squared_results = [r for r in results if 'r_squared' in r.check_id]
        assert any(r.status == 'warning' for r in r_squared_results)

    def test_out_of_range_power_coefficient(self, validator):
        """Test power coefficient outside typical range"""
        results = validator.validate_coefficients(
            alpha_pmp=-0.80,  # Outside typical range
            beta_voc=-0.32,
            alpha_isc=0.05,
            r_squared_pmp=0.998,
            r_squared_voc=0.999,
            r_squared_isc=0.997
        )

        power_coeff_results = [r for r in results if 'alpha_pmp' in r.check_id]
        assert any(r.status == 'warning' for r in power_coeff_results)

    def test_out_of_range_voltage_coefficient(self, validator):
        """Test voltage coefficient outside typical range"""
        results = validator.validate_coefficients(
            alpha_pmp=-0.40,
            beta_voc=-0.60,  # Outside typical range
            alpha_isc=0.05,
            r_squared_pmp=0.998,
            r_squared_voc=0.999,
            r_squared_isc=0.997
        )

        voc_coeff_results = [r for r in results if 'beta_voc' in r.check_id]
        assert any(r.status == 'warning' for r in voc_coeff_results)

    def test_out_of_range_current_coefficient(self, validator):
        """Test current coefficient outside typical range"""
        results = validator.validate_coefficients(
            alpha_pmp=-0.40,
            beta_voc=-0.32,
            alpha_isc=0.15,  # Outside typical range
            r_squared_pmp=0.998,
            r_squared_voc=0.999,
            r_squared_isc=0.997
        )

        isc_coeff_results = [r for r in results if 'alpha_isc' in r.check_id]
        assert any(r.status == 'warning' for r in isc_coeff_results)


class TestDatasetValidation:
    """Test complete dataset validation"""

    def test_valid_dataset(self, validator, valid_data):
        """Test that valid dataset passes all checks"""
        report = validator.validate_dataset(valid_data)

        assert report.overall_status in ['pass', 'warning']
        assert report.num_critical_failures == 0

    def test_dataset_with_multiple_issues(self, validator, insufficient_measurements_data):
        """Test dataset with multiple validation issues"""
        report = validator.validate_dataset(insufficient_measurements_data)

        # Should have at least one failure
        assert report.num_critical_failures > 0
        assert report.overall_status == 'fail'

    def test_validation_report_structure(self, validator, valid_data):
        """Test that validation report has correct structure"""
        report = validator.validate_dataset(valid_data)

        # Check report structure
        assert hasattr(report, 'overall_status')
        assert hasattr(report, 'num_passed')
        assert hasattr(report, 'num_warnings')
        assert hasattr(report, 'num_critical_failures')
        assert hasattr(report, 'results')

        # Should be able to convert to dict
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert 'overall_status' in report_dict
        assert 'summary' in report_dict

    def test_validation_report_json(self, validator, valid_data):
        """Test that validation report can be exported to JSON"""
        report = validator.validate_dataset(valid_data)
        json_str = report.to_json()

        assert isinstance(json_str, str)
        assert 'overall_status' in json_str


class TestRecordValidation:
    """Test single record validation"""

    def test_valid_record(self, validator):
        """Test validation of a valid record"""
        record = {
            'module_temperature': 25.0,
            'ambient_temperature': 23.0,
            'irradiance': 1000.0,
            'voc': 37.5,
            'isc': 9.25,
            'vmp': 31.0,
            'imp': 8.15,
            'pmax': 252.65
        }

        results = validator.validate_record(record)

        # Should have results for each field
        assert len(results) > 0

        # Most should pass (some optional fields might be missing)
        passed = sum(1 for r in results if r.status == 'pass')
        assert passed > 0

    def test_record_with_invalid_values(self, validator):
        """Test validation of record with invalid values"""
        record = {
            'module_temperature': 150.0,  # Too high
            'ambient_temperature': 23.0,
            'irradiance': 1000.0,
            'voc': 37.5,
            'isc': 9.25
        }

        results = validator.validate_record(record)

        # Should have at least one failure/warning for temperature
        temp_results = [r for r in results if 'temperature' in r.check_id.lower()]
        assert any(r.status in ['fail', 'warning'] for r in temp_results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
