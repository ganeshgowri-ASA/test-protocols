"""
Unit tests for SOLDER-001 Validator
Tests validation logic and acceptance criteria checking
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validator import SolderBondValidator


class TestSolderBondValidator(unittest.TestCase):
    """Test cases for SolderBondValidator"""

    def setUp(self):
        """Set up test fixtures"""
        self.acceptance_criteria = {
            "power_degradation": {
                "200_cycles": {"max": 2.0},
                "600_cycles": {"max": 5.0}
            },
            "resistance_increase": {
                "200_cycles": {"max": 10.0},
                "600_cycles": {"max": 20.0}
            }
        }
        self.validator = SolderBondValidator(self.acceptance_criteria)

    def test_initialization(self):
        """Test validator initialization"""
        self.assertEqual(self.validator.criteria, self.acceptance_criteria)
        self.assertEqual(self.validator.violations, [])

    def test_validate_power_degradation_pass(self):
        """Test power degradation validation - passing case"""
        power_data = {
            'power_loss_200_cycles': 1.5,
            'power_loss_600_cycles': 4.0
        }

        result = self.validator.validate_power_degradation(power_data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.violations), 0)

    def test_validate_power_degradation_fail_200(self):
        """Test power degradation validation - fail at 200 cycles"""
        power_data = {
            'power_loss_200_cycles': 2.5,
            'power_loss_600_cycles': 4.0
        }

        result = self.validator.validate_power_degradation(power_data)
        self.assertFalse(result)
        self.assertGreater(len(self.validator.violations), 0)
        self.assertEqual(self.validator.violations[0]['severity'], 'MINOR')

    def test_validate_power_degradation_fail_600(self):
        """Test power degradation validation - fail at 600 cycles"""
        power_data = {
            'power_loss_200_cycles': 1.5,
            'power_loss_600_cycles': 6.0
        }

        result = self.validator.validate_power_degradation(power_data)
        self.assertFalse(result)
        self.assertGreater(len(self.validator.violations), 0)
        self.assertEqual(self.validator.violations[0]['severity'], 'CRITICAL')

    def test_validate_resistance_increase_pass(self):
        """Test resistance increase validation - passing case"""
        resistance_data = {
            'resistance_increase_200_cycles': 8.0,
            'resistance_increase_600_cycles': 15.0
        }

        result = self.validator.validate_resistance_increase(resistance_data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.violations), 0)

    def test_validate_resistance_increase_fail(self):
        """Test resistance increase validation - fail at 600 cycles"""
        resistance_data = {
            'resistance_increase_200_cycles': 8.0,
            'resistance_increase_600_cycles': 22.0
        }

        result = self.validator.validate_resistance_increase(resistance_data)
        self.assertFalse(result)
        self.assertEqual(self.validator.violations[0]['severity'], 'CRITICAL')

    def test_validate_cell_interconnect_resistance(self):
        """Test cell interconnect resistance validation"""
        # Test initial resistance check
        result1 = self.validator.validate_cell_interconnect_resistance(4.5)
        self.assertTrue(result1)

        # Test exceeding initial limit
        result2 = self.validator.validate_cell_interconnect_resistance(5.5)
        self.assertFalse(result2)

        # Test with baseline
        self.validator.violations = []
        result3 = self.validator.validate_cell_interconnect_resistance(3.5, baseline=3.0)
        self.assertTrue(result3)

        # Test exceeding percentage increase
        self.validator.violations = []
        result4 = self.validator.validate_cell_interconnect_resistance(3.9, baseline=3.0)
        self.assertFalse(result4)

    def test_validate_mechanical_strength_pass(self):
        """Test mechanical strength validation - passing case"""
        pull_test_data = {
            'fresh_mean_force': 32.0,
            'aged_mean_force': 26.0,
            'percentage_loss': 18.75
        }

        result = self.validator.validate_mechanical_strength(pull_test_data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.violations), 0)

    def test_validate_mechanical_strength_fail_fresh(self):
        """Test mechanical strength validation - fail fresh minimum"""
        pull_test_data = {
            'fresh_mean_force': 28.0,
            'aged_mean_force': 24.0,
            'percentage_loss': 14.3
        }

        result = self.validator.validate_mechanical_strength(pull_test_data)
        self.assertFalse(result)
        self.assertEqual(self.validator.violations[0]['parameter'], 'pull_test_fresh')
        self.assertEqual(self.validator.violations[0]['severity'], 'CRITICAL')

    def test_validate_mechanical_strength_fail_aged(self):
        """Test mechanical strength validation - fail aged minimum"""
        pull_test_data = {
            'fresh_mean_force': 32.0,
            'aged_mean_force': 22.0,
            'percentage_loss': 31.25
        }

        result = self.validator.validate_mechanical_strength(pull_test_data)
        self.assertFalse(result)
        # Should have violations for both aged force and degradation
        self.assertGreaterEqual(len(self.validator.violations), 2)

    def test_validate_visual_inspection_pass(self):
        """Test visual inspection validation - passing case"""
        visual_data = {
            'solder_cracks': 0,
            'ribbon_detachment': 0,
            'delamination_percentage': 0,
            'discoloration_percentage': 5.0
        }

        result = self.validator.validate_visual_inspection(visual_data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.violations), 0)

    def test_validate_visual_inspection_fail_cracks(self):
        """Test visual inspection validation - fail on cracks"""
        visual_data = {
            'solder_cracks': 2,
            'ribbon_detachment': 0,
            'delamination_percentage': 0,
            'discoloration_percentage': 5.0
        }

        result = self.validator.validate_visual_inspection(visual_data)
        self.assertFalse(result)
        self.assertEqual(self.validator.violations[0]['severity'], 'CRITICAL')

    def test_validate_thermal_imaging_pass(self):
        """Test thermal imaging validation - passing case"""
        thermal_data = {
            'max_delta_t': 12.0
        }

        result = self.validator.validate_thermal_imaging(thermal_data)
        self.assertTrue(result)

    def test_validate_thermal_imaging_fail(self):
        """Test thermal imaging validation - fail"""
        thermal_data = {
            'max_delta_t': 18.0
        }

        result = self.validator.validate_thermal_imaging(thermal_data)
        self.assertFalse(result)
        self.assertEqual(self.validator.violations[0]['severity'], 'MAJOR')

    def test_validate_lifetime_prediction_pass(self):
        """Test lifetime prediction validation - passing case"""
        lifetime_data = {
            'predicted_lifetime_years': 28.0,
            'year_25_projection': {
                'resistance_increase_pct': 15.0,
                'power_loss_pct': 18.0
            }
        }

        result = self.validator.validate_lifetime_prediction(lifetime_data)
        self.assertTrue(result)

    def test_validate_lifetime_prediction_fail(self):
        """Test lifetime prediction validation - fail"""
        lifetime_data = {
            'predicted_lifetime_years': 22.0,
            'year_25_projection': {
                'resistance_increase_pct': 25.0,
                'power_loss_pct': 22.0
            }
        }

        result = self.validator.validate_lifetime_prediction(lifetime_data)
        self.assertFalse(result)
        self.assertGreater(len(self.validator.violations), 0)

    def test_validate_checkpoint_compliance_200(self):
        """Test checkpoint compliance at 200 cycles"""
        checkpoint_data = {
            'power_loss_pct': 1.8,
            'resistance_increase_pct': 9.0
        }

        result = self.validator.validate_checkpoint_compliance(checkpoint_data, 200)
        self.assertTrue(result)

    def test_validate_checkpoint_compliance_600_fail(self):
        """Test checkpoint compliance at 600 cycles - fail"""
        checkpoint_data = {
            'power_loss_pct': 5.5,
            'resistance_increase_pct': 22.0
        }

        result = self.validator.validate_checkpoint_compliance(checkpoint_data, 600)
        self.assertFalse(result)
        # Should have critical violations
        critical_violations = [v for v in self.validator.violations if v['severity'] == 'CRITICAL']
        self.assertGreater(len(critical_violations), 0)

    def test_get_violations_by_severity(self):
        """Test getting violations by severity"""
        # Add some violations
        self.validator.violations = [
            {'severity': 'CRITICAL', 'message': 'Test 1'},
            {'severity': 'MAJOR', 'message': 'Test 2'},
            {'severity': 'CRITICAL', 'message': 'Test 3'},
            {'severity': 'MINOR', 'message': 'Test 4'}
        ]

        critical = self.validator.get_violations_by_severity('CRITICAL')
        major = self.validator.get_violations_by_severity('MAJOR')
        minor = self.validator.get_violations_by_severity('MINOR')

        self.assertEqual(len(critical), 2)
        self.assertEqual(len(major), 1)
        self.assertEqual(len(minor), 1)

    def test_get_violation_summary(self):
        """Test violation summary generation"""
        self.validator.violations = [
            {'severity': 'CRITICAL', 'message': 'Test 1'},
            {'severity': 'MAJOR', 'message': 'Test 2'},
            {'severity': 'CRITICAL', 'message': 'Test 3'},
            {'severity': 'MINOR', 'message': 'Test 4'},
            {'severity': 'MINOR', 'message': 'Test 5'}
        ]

        summary = self.validator.get_violation_summary()

        self.assertEqual(summary['CRITICAL'], 2)
        self.assertEqual(summary['MAJOR'], 1)
        self.assertEqual(summary['MINOR'], 2)
        self.assertEqual(summary['TOTAL'], 5)

    def test_passes_acceptance_criteria_pass(self):
        """Test overall acceptance criteria check - pass"""
        self.validator.violations = [
            {'severity': 'MAJOR', 'message': 'Test 1'},
            {'severity': 'MINOR', 'message': 'Test 2'}
        ]

        result = self.validator.passes_acceptance_criteria()
        self.assertTrue(result)

    def test_passes_acceptance_criteria_fail_critical(self):
        """Test overall acceptance criteria check - fail on critical"""
        self.validator.violations = [
            {'severity': 'CRITICAL', 'message': 'Test 1'},
            {'severity': 'MINOR', 'message': 'Test 2'}
        ]

        result = self.validator.passes_acceptance_criteria()
        self.assertFalse(result)

    def test_passes_acceptance_criteria_fail_too_many_major(self):
        """Test overall acceptance criteria check - fail on too many major"""
        self.validator.violations = [
            {'severity': 'MAJOR', 'message': 'Test 1'},
            {'severity': 'MAJOR', 'message': 'Test 2'},
            {'severity': 'MAJOR', 'message': 'Test 3'},
            {'severity': 'MAJOR', 'message': 'Test 4'}
        ]

        result = self.validator.passes_acceptance_criteria()
        self.assertFalse(result)

    def test_get_overall_status_pass(self):
        """Test overall status determination - PASS"""
        self.validator.violations = []
        status = self.validator.get_overall_status()
        self.assertEqual(status, 'PASS')

    def test_get_overall_status_marginal(self):
        """Test overall status determination - MARGINAL"""
        self.validator.violations = [
            {'severity': 'MINOR', 'message': 'Test 1'}
        ]
        status = self.validator.get_overall_status()
        self.assertEqual(status, 'MARGINAL')

    def test_get_overall_status_fail(self):
        """Test overall status determination - FAIL"""
        self.validator.violations = [
            {'severity': 'CRITICAL', 'message': 'Test 1'}
        ]
        status = self.validator.get_overall_status()
        self.assertEqual(status, 'FAIL')

    def test_validate_all(self):
        """Test complete validation"""
        test_data = {
            'power_analysis': {
                'power_loss_200_cycles': 1.5,
                'power_loss_600_cycles': 4.0
            },
            'resistance_analysis': {
                'resistance_increase_200_cycles': 8.0,
                'resistance_increase_600_cycles': 15.0
            },
            'series_resistance': {
                'increase_percentage': 12.0
            },
            'pull_test_results': {
                'fresh_mean_force': 32.0,
                'aged_mean_force': 26.0,
                'percentage_loss': 18.75
            },
            'visual_defects': {
                'solder_cracks': 0,
                'ribbon_detachment': 0,
                'delamination_percentage': 0,
                'discoloration_percentage': 5.0
            },
            'thermal_imaging': {
                'max_delta_t': 12.0,
                'hotspot_count': 2,
                'new_hotspots': 1
            }
        }

        is_valid, violations = self.validator.validate_all(test_data)

        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_generate_compliance_report(self):
        """Test compliance report generation"""
        self.validator.violations = [
            {'severity': 'MAJOR', 'message': 'Test 1'},
            {'severity': 'MINOR', 'message': 'Test 2'}
        ]

        report = self.validator.generate_compliance_report()

        self.assertIn('overall_status', report)
        self.assertIn('passes_criteria', report)
        self.assertIn('violation_summary', report)
        self.assertEqual(report['overall_status'], 'MARGINAL')
        self.assertTrue(report['passes_criteria'])


if __name__ == '__main__':
    unittest.main()
