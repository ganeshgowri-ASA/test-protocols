"""
Unit tests for PERF-001 validation module

Test coverage:
- Validation result structures
- Individual validation checks
- Complete test validation
- IEC 61853 compliance checks
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from validation import (
    ValidationLevel, ValidationResult, ValidationReport,
    PERF001Validator, validate_test_data
)
from perf_001_engine import create_sample_data


class TestValidationStructures(unittest.TestCase):
    """Test validation data structures"""

    def test_validation_result_creation(self):
        """Test ValidationResult creation"""
        result = ValidationResult(
            check_name="test_check",
            passed=True,
            level=ValidationLevel.INFO,
            message="Test passed"
        )
        self.assertEqual(result.check_name, "test_check")
        self.assertTrue(result.passed)
        self.assertEqual(result.level, ValidationLevel.INFO)

    def test_validation_result_to_dict(self):
        """Test ValidationResult conversion to dict"""
        result = ValidationResult(
            check_name="test_check",
            passed=False,
            level=ValidationLevel.ERROR,
            message="Test failed",
            details={'error_code': 123}
        )
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['check_name'], "test_check")
        self.assertFalse(d['passed'])
        self.assertEqual(d['level'], 'error')

    def test_validation_report_creation(self):
        """Test ValidationReport creation and summary"""
        results = [
            ValidationResult("check1", True, ValidationLevel.INFO, "Pass"),
            ValidationResult("check2", False, ValidationLevel.WARNING, "Warning"),
            ValidationResult("check3", False, ValidationLevel.ERROR, "Error"),
        ]

        report = ValidationReport(test_id="TEST-001", overall_passed=True, results=results)

        self.assertEqual(report.summary['total_checks'], 3)
        self.assertEqual(report.summary['passed'], 1)
        self.assertEqual(report.summary['failed'], 2)
        self.assertEqual(report.summary['warnings'], 1)
        self.assertEqual(report.summary['errors'], 1)

    def test_validation_report_overall_status(self):
        """Test overall pass/fail determination"""
        # All passing
        results_pass = [
            ValidationResult("check1", True, ValidationLevel.INFO, "Pass"),
            ValidationResult("check2", True, ValidationLevel.INFO, "Pass"),
        ]
        report_pass = ValidationReport(test_id="TEST-001", overall_passed=True, results=results_pass)
        self.assertTrue(report_pass.overall_passed)

        # Has error
        results_error = [
            ValidationResult("check1", True, ValidationLevel.INFO, "Pass"),
            ValidationResult("check2", False, ValidationLevel.ERROR, "Error"),
        ]
        report_error = ValidationReport(test_id="TEST-001", overall_passed=True, results=results_error)
        self.assertFalse(report_error.overall_passed)

    def test_get_errors_and_warnings(self):
        """Test filtering errors and warnings"""
        results = [
            ValidationResult("check1", True, ValidationLevel.INFO, "Pass"),
            ValidationResult("check2", False, ValidationLevel.WARNING, "Warning"),
            ValidationResult("check3", False, ValidationLevel.ERROR, "Error"),
            ValidationResult("check4", False, ValidationLevel.CRITICAL, "Critical"),
        ]

        report = ValidationReport(test_id="TEST-001", overall_passed=True, results=results)

        errors = report.get_errors()
        self.assertEqual(len(errors), 2)  # ERROR and CRITICAL

        warnings = report.get_warnings()
        self.assertEqual(len(warnings), 1)


class TestPERF001ValidatorBasic(unittest.TestCase):
    """Test basic validator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()
        self.sample_data = create_sample_data()

    def test_validator_creation(self):
        """Test validator instantiation"""
        validator = PERF001Validator()
        self.assertIsInstance(validator, PERF001Validator)
        self.assertEqual(len(validator.results), 0)

    def test_validate_complete_test(self):
        """Test complete test validation"""
        report = self.validator.validate_complete_test(self.sample_data)

        self.assertIsInstance(report, ValidationReport)
        self.assertGreater(len(report.results), 0)
        self.assertIsNotNone(report.test_id)


class TestProtocolInfoValidation(unittest.TestCase):
    """Test protocol information validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_valid_protocol_info(self):
        """Test validation of correct protocol info"""
        protocol_info = {
            'protocol_id': 'PERF-001',
            'protocol_name': 'Performance at Different Temperatures',
            'standard': 'IEC 61853',
            'version': '1.0.0'
        }
        self.validator._validate_protocol_info(protocol_info)

        # Check for protocol_id result
        protocol_result = [r for r in self.validator.results if r.check_name == 'protocol_id'][0]
        self.assertTrue(protocol_result.passed)

    def test_invalid_protocol_id(self):
        """Test detection of invalid protocol ID"""
        protocol_info = {
            'protocol_id': 'WRONG-001',
            'standard': 'IEC 61853'
        }
        self.validator._validate_protocol_info(protocol_info)

        protocol_result = [r for r in self.validator.results if r.check_name == 'protocol_id'][0]
        self.assertFalse(protocol_result.passed)
        self.assertEqual(protocol_result.level, ValidationLevel.CRITICAL)

    def test_invalid_standard(self):
        """Test warning for non-IEC standard"""
        protocol_info = {
            'protocol_id': 'PERF-001',
            'standard': 'ASTM E1234'
        }
        self.validator._validate_protocol_info(protocol_info)

        standard_result = [r for r in self.validator.results if r.check_name == 'standard'][0]
        self.assertFalse(standard_result.passed)


class TestTestSpecimenValidation(unittest.TestCase):
    """Test specimen information validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_valid_specimen(self):
        """Test validation of complete specimen info"""
        specimen = {
            'module_id': 'TEST-001',
            'manufacturer': 'Test Mfg',
            'model': 'TEST-320',
            'technology': 'mono-Si',
            'rated_power_stc': 320.0,
            'area': 1.96
        }
        self.validator._validate_test_specimen(specimen)

        # Should have passing results for required fields
        module_id_result = [r for r in self.validator.results
                           if r.check_name == 'specimen_module_id'][0]
        self.assertTrue(module_id_result.passed)

    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        specimen = {
            'module_id': 'TEST-001',
            # Missing manufacturer, model, technology
        }
        self.validator._validate_test_specimen(specimen)

        # Should have errors for missing fields
        errors = [r for r in self.validator.results if not r.passed]
        self.assertGreater(len(errors), 0)

    def test_unusual_rated_power(self):
        """Test warning for unusual rated power"""
        specimen = {
            'module_id': 'TEST-001',
            'manufacturer': 'Test',
            'model': 'TEST',
            'technology': 'mono-Si',
            'rated_power_stc': 5000.0  # Unusually high
        }
        self.validator._validate_test_specimen(specimen)

        power_result = [r for r in self.validator.results
                       if r.check_name == 'rated_power'][0]
        self.assertFalse(power_result.passed)
        self.assertEqual(power_result.level, ValidationLevel.WARNING)


class TestConditionsValidation(unittest.TestCase):
    """Test conditions validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_valid_conditions(self):
        """Test validation of correct test conditions"""
        conditions = {
            'irradiance': 1000.0,
            'spectrum': 'AM1.5G',
            'temperature_points': [15, 25, 50, 75]
        }
        self.validator._validate_test_conditions(conditions)

        irradiance_result = [r for r in self.validator.results
                            if r.check_name == 'irradiance'][0]
        self.assertTrue(irradiance_result.passed)

    def test_invalid_irradiance(self):
        """Test detection of incorrect irradiance"""
        conditions = {
            'irradiance': 800.0,  # Wrong value
            'temperature_points': [15, 25, 50, 75]
        }
        self.validator._validate_test_conditions(conditions)

        irradiance_result = [r for r in self.validator.results
                            if r.check_name == 'irradiance'][0]
        self.assertFalse(irradiance_result.passed)
        self.assertEqual(irradiance_result.level, ValidationLevel.ERROR)

    def test_insufficient_temp_points(self):
        """Test detection of insufficient temperature points"""
        conditions = {
            'irradiance': 1000.0,
            'temperature_points': [15, 25, 50]  # Only 3 points
        }
        self.validator._validate_test_conditions(conditions)

        temp_result = [r for r in self.validator.results
                      if r.check_name == 'temperature_points_count'][0]
        self.assertFalse(temp_result.passed)
        self.assertEqual(temp_result.level, ValidationLevel.CRITICAL)

    def test_small_temperature_range(self):
        """Test warning for small temperature range"""
        conditions = {
            'irradiance': 1000.0,
            'temperature_points': [20, 25, 30, 35]  # Only 15°C range
        }
        self.validator._validate_test_conditions(conditions)

        range_result = [r for r in self.validator.results
                       if r.check_name == 'temperature_range'][0]
        self.assertFalse(range_result.passed)
        self.assertEqual(range_result.level, ValidationLevel.WARNING)


class TestMeasurementsValidation(unittest.TestCase):
    """Test measurements validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_valid_measurements(self):
        """Test validation of correct measurements"""
        measurements = [
            {'temperature': 15, 'pmax': 330, 'voc': 46.8, 'isc': 9.12, 'vmp': 38.2, 'imp': 8.64},
            {'temperature': 25, 'pmax': 320, 'voc': 45.2, 'isc': 9.18, 'vmp': 37.0, 'imp': 8.65},
            {'temperature': 50, 'pmax': 290, 'voc': 41.5, 'isc': 9.30, 'vmp': 34.2, 'imp': 8.48},
            {'temperature': 75, 'pmax': 260, 'voc': 38.0, 'isc': 9.42, 'vmp': 31.5, 'imp': 8.26},
        ]
        self.validator._validate_measurements(measurements)

        count_result = [r for r in self.validator.results
                       if r.check_name == 'measurements_count'][0]
        self.assertTrue(count_result.passed)

    def test_insufficient_measurements(self):
        """Test detection of insufficient measurements"""
        measurements = [
            {'temperature': 15, 'pmax': 330, 'voc': 46.8, 'isc': 9.12, 'vmp': 38.2, 'imp': 8.64},
            {'temperature': 25, 'pmax': 320, 'voc': 45.2, 'isc': 9.18, 'vmp': 37.0, 'imp': 8.65},
        ]
        self.validator._validate_measurements(measurements)

        count_result = [r for r in self.validator.results
                       if r.check_name == 'measurements_count'][0]
        self.assertFalse(count_result.passed)
        self.assertEqual(count_result.level, ValidationLevel.CRITICAL)

    def test_invalid_measurement_values(self):
        """Test detection of invalid measurement values"""
        measurements = [
            {'temperature': 15, 'pmax': 0, 'voc': 0, 'isc': 0, 'vmp': 0, 'imp': 0},  # Invalid
            {'temperature': 25, 'pmax': 320, 'voc': 45.2, 'isc': 9.18, 'vmp': 37.0, 'imp': 8.65},
            {'temperature': 50, 'pmax': 290, 'voc': 41.5, 'isc': 9.30, 'vmp': 34.2, 'imp': 8.48},
            {'temperature': 75, 'pmax': 260, 'voc': 38.0, 'isc': 9.42, 'vmp': 31.5, 'imp': 8.26},
        ]
        self.validator._validate_measurements(measurements)

        errors = [r for r in self.validator.results
                 if not r.passed and r.level == ValidationLevel.ERROR]
        self.assertGreater(len(errors), 0)


class TestCalculatedResultsValidation(unittest.TestCase):
    """Test validation of calculated results"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_valid_calculated_results(self):
        """Test validation of typical coefficient values"""
        results = {
            'temp_coefficient_pmax': {
                'value': -0.42,
                'unit': '%/°C',
                'r_squared': 0.98
            },
            'temp_coefficient_voc': {
                'value': -0.30,
                'unit': '%/°C',
                'r_squared': 0.99
            },
            'temp_coefficient_isc': {
                'value': 0.05,
                'unit': '%/°C',
                'r_squared': 0.97
            }
        }
        self.validator._validate_calculated_results(results)

        linearity_result = [r for r in self.validator.results
                           if r.check_name == 'temp_coef_pmax_linearity'][0]
        self.assertTrue(linearity_result.passed)

    def test_poor_linearity(self):
        """Test detection of poor linearity"""
        results = {
            'temp_coefficient_pmax': {
                'value': -0.42,
                'unit': '%/°C',
                'r_squared': 0.85  # Poor linearity
            }
        }
        self.validator._validate_calculated_results(results)

        linearity_result = [r for r in self.validator.results
                           if r.check_name == 'temp_coef_pmax_linearity'][0]
        self.assertFalse(linearity_result.passed)

    def test_unusual_coefficient_values(self):
        """Test warning for unusual coefficient values"""
        results = {
            'temp_coefficient_pmax': {
                'value': -1.5,  # Unusually large
                'unit': '%/°C',
                'r_squared': 0.98
            },
            'temp_coefficient_voc': {
                'value': 0.5,  # Wrong sign (should be negative)
                'unit': '%/°C',
                'r_squared': 0.99
            },
            'temp_coefficient_isc': {
                'value': -0.05,  # Wrong sign (should be positive)
                'unit': '%/°C',
                'r_squared': 0.97
            }
        }
        self.validator._validate_calculated_results(results)

        warnings = [r for r in self.validator.results
                   if not r.passed and r.level == ValidationLevel.WARNING]
        self.assertGreater(len(warnings), 0)


class TestIEC61853Compliance(unittest.TestCase):
    """Test IEC 61853 compliance validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = PERF001Validator()

    def test_compliant_data(self):
        """Test validation of compliant test data"""
        sample_data = create_sample_data()
        self.validator._validate_iec61853_compliance(sample_data)

        compliance_result = [r for r in self.validator.results
                            if r.check_name == 'iec61853_compliance'][0]
        self.assertTrue(compliance_result.passed)

    def test_non_compliant_irradiance(self):
        """Test detection of non-compliant irradiance"""
        test_data = create_sample_data()
        test_data['test_conditions']['irradiance'] = 800  # Non-compliant

        self.validator._validate_iec61853_compliance(test_data)

        compliance_result = [r for r in self.validator.results
                            if r.check_name == 'iec61853_compliance'][0]
        self.assertFalse(compliance_result.passed)


class TestConvenienceFunction(unittest.TestCase):
    """Test convenience validation function"""

    def test_validate_test_data_function(self):
        """Test validate_test_data convenience function"""
        sample_data = create_sample_data()
        report = validate_test_data(sample_data)

        self.assertIsInstance(report, ValidationReport)
        self.assertIsNotNone(report.test_id)
        self.assertGreater(len(report.results), 0)


class TestCompleteValidation(unittest.TestCase):
    """Test complete validation workflow"""

    def test_sample_data_validation(self):
        """Test validation of generated sample data"""
        sample_data = create_sample_data()
        report = validate_test_data(sample_data)

        # Sample data should pass all validations
        self.assertTrue(report.overall_passed)
        self.assertEqual(report.summary['critical'], 0)
        self.assertEqual(report.summary['errors'], 0)

    def test_validation_report_export(self):
        """Test validation report export to dict"""
        sample_data = create_sample_data()
        report = validate_test_data(sample_data)

        report_dict = report.to_dict()
        self.assertIsInstance(report_dict, dict)
        self.assertIn('test_id', report_dict)
        self.assertIn('overall_passed', report_dict)
        self.assertIn('summary', report_dict)
        self.assertIn('results', report_dict)


def run_tests():
    """Run all validation tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
