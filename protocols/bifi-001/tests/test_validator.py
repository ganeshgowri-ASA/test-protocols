"""
Unit tests for BifacialValidator
"""

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.validator import BifacialValidator


class TestBifacialValidator(unittest.TestCase):
    """Test cases for BifacialValidator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = BifacialValidator()

        # Load template data
        template_path = Path(__file__).parent.parent / "schemas" / "data_template.json"
        with open(template_path, 'r') as f:
            self.valid_data = json.load(f)

        # Add minimal valid measurement data
        self.valid_data["measurements"]["front_side"]["isc"] = 10.0
        self.valid_data["measurements"]["front_side"]["voc"] = 45.0
        self.valid_data["measurements"]["front_side"]["pmax"] = 350.0
        self.valid_data["measurements"]["front_side"]["imp"] = 9.5
        self.valid_data["measurements"]["front_side"]["vmp"] = 36.8
        self.valid_data["measurements"]["front_side"]["fill_factor"] = 0.78
        self.valid_data["measurements"]["front_side"]["iv_curve"] = [
            {"voltage": i * 5, "current": 10 - i * 1} for i in range(10)
        ]

        self.valid_data["measurements"]["rear_side"]["isc"] = 7.0
        self.valid_data["measurements"]["rear_side"]["voc"] = 43.0
        self.valid_data["measurements"]["rear_side"]["pmax"] = 245.0
        self.valid_data["measurements"]["rear_side"]["imp"] = 6.7
        self.valid_data["measurements"]["rear_side"]["vmp"] = 36.6
        self.valid_data["measurements"]["rear_side"]["fill_factor"] = 0.81
        self.valid_data["measurements"]["rear_side"]["iv_curve"] = [
            {"voltage": i * 5, "current": 7 - i * 0.7} for i in range(10)
        ]

        self.valid_data["measurements"]["bifacial_measurements"]["measured_bifaciality"] = 0.70

    def test_schema_validation_valid_data(self):
        """Test schema validation with valid data"""
        is_valid, errors = self.validator.validate_schema(self.valid_data)
        self.assertTrue(is_valid, f"Expected valid data but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_schema_validation_missing_required_field(self):
        """Test schema validation with missing required field"""
        invalid_data = self.valid_data.copy()
        del invalid_data["metadata"]["operator"]

        is_valid, errors = self.validator.validate_schema(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_irradiance_conditions_valid(self):
        """Test irradiance validation with valid conditions"""
        is_valid, errors = self.validator.validate_irradiance_conditions(self.valid_data)
        self.assertTrue(is_valid, f"Expected valid but got: {errors}")

    def test_validate_irradiance_rear_exceeds_front(self):
        """Test validation fails when rear > front irradiance"""
        invalid_data = self.valid_data.copy()
        invalid_data["test_conditions"]["rear_irradiance"]["value"] = 1200

        is_valid, errors = self.validator.validate_irradiance_conditions(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("exceeds front" in err for err in errors))

    def test_validate_irradiance_low_value(self):
        """Test validation warns on very low irradiance"""
        low_irr_data = self.valid_data.copy()
        low_irr_data["test_conditions"]["front_irradiance"]["value"] = 50

        is_valid, errors = self.validator.validate_irradiance_conditions(low_irr_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("too low" in err for err in errors))

    def test_validate_stc_conditions(self):
        """Test STC condition validation"""
        # Valid STC
        self.valid_data["test_conditions"]["stc_conditions"] = True
        self.valid_data["test_conditions"]["front_irradiance"]["value"] = 1000
        self.valid_data["test_conditions"]["temperature"]["value"] = 25

        is_valid, errors = self.validator.validate_irradiance_conditions(self.valid_data)
        self.assertTrue(is_valid, f"STC validation failed: {errors}")

        # Invalid STC temperature
        self.valid_data["test_conditions"]["temperature"]["value"] = 30
        is_valid, errors = self.validator.validate_irradiance_conditions(self.valid_data)
        self.assertFalse(is_valid)

    def test_validate_iv_curve_valid(self):
        """Test I-V curve validation with valid data"""
        iv_curve = [{"voltage": i * 5, "current": 10 - i * 1} for i in range(15)]
        is_valid, errors = self.validator.validate_iv_curve(iv_curve, "front")
        self.assertTrue(is_valid, f"Expected valid but got: {errors}")

    def test_validate_iv_curve_insufficient_points(self):
        """Test I-V curve validation with too few points"""
        iv_curve = [{"voltage": i, "current": 5 - i} for i in range(5)]
        is_valid, errors = self.validator.validate_iv_curve(iv_curve, "front")
        self.assertFalse(is_valid)
        self.assertTrue(any("insufficient" in err.lower() for err in errors))

    def test_validate_iv_curve_non_monotonic(self):
        """Test I-V curve validation with non-monotonic voltages"""
        iv_curve = [
            {"voltage": 0, "current": 10},
            {"voltage": 10, "current": 8},
            {"voltage": 5, "current": 7},  # Out of order
        ] + [{"voltage": i * 5, "current": 10 - i} for i in range(3, 10)]

        is_valid, errors = self.validator.validate_iv_curve(iv_curve, "front")
        self.assertFalse(is_valid)
        self.assertTrue(any("monotonic" in err.lower() for err in errors))

    def test_validate_measurements_valid(self):
        """Test measurement validation with valid data"""
        is_valid, errors = self.validator.validate_measurements(self.valid_data)
        self.assertTrue(is_valid, f"Expected valid but got: {errors}")

    def test_validate_measurements_pmax_exceeds_limit(self):
        """Test that Pmax cannot exceed Isc × Voc"""
        invalid_data = self.valid_data.copy()
        invalid_data["measurements"]["front_side"]["pmax"] = 1000  # Exceeds Isc × Voc

        is_valid, errors = self.validator.validate_measurements(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("cannot exceed" in err for err in errors))

    def test_validate_fill_factor_out_of_range(self):
        """Test fill factor must be between 0 and 1"""
        invalid_data = self.valid_data.copy()
        invalid_data["measurements"]["front_side"]["fill_factor"] = 1.5

        is_valid, errors = self.validator.validate_measurements(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("fill factor" in err.lower() for err in errors))

    def test_validate_bifaciality_consistency(self):
        """Test bifaciality factor consistency check"""
        self.valid_data["measurements"]["bifacial_measurements"]["measured_bifaciality"] = 0.5

        is_valid, errors = self.validator.validate_measurements(self.valid_data)
        # Should fail because calculated bifaciality (245/350 = 0.70) != 0.5
        self.assertFalse(is_valid)
        self.assertTrue(any("bifaciality" in err.lower() for err in errors))

    def test_validate_all_comprehensive(self):
        """Test comprehensive validation"""
        results = self.validator.validate_all(self.valid_data)

        self.assertIn("overall_valid", results)
        self.assertIn("errors", results)
        self.assertIn("warnings", results)
        self.assertIn("checks", results)
        self.assertGreater(len(results["checks"]), 0)

    def test_validate_calibration_valid(self):
        """Test calibration validation"""
        is_valid, warnings = self.validator.validate_calibration(self.valid_data)
        # Should pass since dates are in future
        self.assertTrue(is_valid or len(warnings) == 0)

    def test_validate_calibration_overdue(self):
        """Test calibration overdue detection"""
        overdue_data = self.valid_data.copy()
        overdue_data["quality_control"]["calibration_status"]["next_calibration_due"] = "2020-01-01"

        is_valid, warnings = self.validator.validate_calibration(overdue_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("overdue" in warn.lower() for warn in warnings))


class TestValidatorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.validator = BifacialValidator()

    def test_validate_empty_data(self):
        """Test validation with empty data"""
        is_valid, errors = self.validator.validate_schema({})
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_none_data(self):
        """Test validation with None"""
        with self.assertRaises(Exception):
            self.validator.validate_schema(None)

    def test_validate_iv_curve_empty(self):
        """Test I-V curve validation with empty list"""
        is_valid, errors = self.validator.validate_iv_curve([], "front")
        self.assertFalse(is_valid)

    def test_validate_negative_values(self):
        """Test that negative Isc/Voc are caught"""
        data = {
            "measurements": {
                "front_side": {
                    "isc": -5.0,
                    "voc": 45.0,
                    "pmax": 100,
                    "fill_factor": 0.7,
                    "iv_curve": [{"voltage": i, "current": 5-i} for i in range(10)]
                },
                "rear_side": {
                    "isc": 3.0,
                    "voc": 43.0,
                    "pmax": 80,
                    "fill_factor": 0.7,
                    "iv_curve": [{"voltage": i, "current": 3-i*0.3} for i in range(10)]
                }
            }
        }

        is_valid, errors = self.validator.validate_measurements(data)
        self.assertFalse(is_valid)
        self.assertTrue(any("positive" in err.lower() for err in errors))


if __name__ == '__main__':
    unittest.main()
