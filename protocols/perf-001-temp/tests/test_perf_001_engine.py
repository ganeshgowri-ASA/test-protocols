"""
Unit tests for PERF-001 calculation engine

Test coverage:
- Measurement data structures
- Temperature coefficient calculations
- Data quality validation
- Edge cases and error handling
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from perf_001_engine import (
    Measurement, TemperatureCoefficient, PERF001Calculator,
    PERF001Validator, create_sample_data
)


class TestMeasurement(unittest.TestCase):
    """Test Measurement dataclass"""

    def test_measurement_creation(self):
        """Test basic measurement creation"""
        m = Measurement(
            temperature=25.0,
            pmax=320.0,
            voc=45.2,
            isc=9.18,
            vmp=37.0,
            imp=8.65
        )
        self.assertEqual(m.temperature, 25.0)
        self.assertEqual(m.pmax, 320.0)
        self.assertIsNotNone(m.fill_factor)
        self.assertIsNotNone(m.timestamp)

    def test_fill_factor_calculation(self):
        """Test automatic fill factor calculation"""
        m = Measurement(
            temperature=25.0,
            pmax=320.0,
            voc=45.2,
            isc=9.18,
            vmp=37.0,
            imp=8.65
        )
        expected_ff = 320.0 / (45.2 * 9.18)
        self.assertAlmostEqual(m.fill_factor, expected_ff, places=4)

    def test_efficiency_calculation(self):
        """Test efficiency calculation"""
        m = Measurement(
            temperature=25.0,
            pmax=320.0,
            voc=45.2,
            isc=9.18,
            vmp=37.0,
            imp=8.65
        )
        efficiency = m.calculate_efficiency(module_area=1.96, irradiance=1000)
        expected_efficiency = (320.0 / (1000 * 1.96)) * 100
        self.assertAlmostEqual(efficiency, expected_efficiency, places=2)
        self.assertAlmostEqual(m.efficiency, expected_efficiency, places=2)

    def test_measurement_to_dict(self):
        """Test conversion to dictionary"""
        m = Measurement(
            temperature=25.0,
            pmax=320.0,
            voc=45.2,
            isc=9.18,
            vmp=37.0,
            imp=8.65
        )
        d = m.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['temperature'], 25.0)
        self.assertEqual(d['pmax'], 320.0)
        self.assertIn('fill_factor', d)


class TestTemperatureCoefficient(unittest.TestCase):
    """Test TemperatureCoefficient dataclass"""

    def test_coefficient_creation(self):
        """Test coefficient creation"""
        coef = TemperatureCoefficient(
            value=-0.45,
            unit="%/°C",
            r_squared=0.98
        )
        self.assertEqual(coef.value, -0.45)
        self.assertEqual(coef.unit, "%/°C")
        self.assertEqual(coef.r_squared, 0.98)

    def test_coefficient_to_dict(self):
        """Test conversion to dictionary"""
        coef = TemperatureCoefficient(
            value=-0.45,
            unit="%/°C",
            r_squared=0.98,
            std_error=0.01
        )
        d = coef.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['value'], -0.45)
        self.assertEqual(d['r_squared'], 0.98)


class TestPERF001Calculator(unittest.TestCase):
    """Test PERF001Calculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calc = PERF001Calculator(reference_temperature=25.0)

        # Create realistic test data
        self.measurements = [
            Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
            Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
            Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
            Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
        ]

    def test_add_measurement(self):
        """Test adding measurements"""
        self.calc.add_measurement(self.measurements[0])
        self.assertEqual(len(self.calc.measurements), 1)

    def test_add_multiple_measurements(self):
        """Test adding multiple measurements"""
        self.calc.add_measurements(self.measurements)
        self.assertEqual(len(self.calc.measurements), 4)

    def test_temp_coefficient_pmax(self):
        """Test Pmax temperature coefficient calculation"""
        self.calc.add_measurements(self.measurements)
        coef = self.calc.calculate_temp_coefficient_pmax()

        self.assertIsInstance(coef, TemperatureCoefficient)
        self.assertEqual(coef.unit, "%/°C")

        # Coefficient should be negative for crystalline silicon
        self.assertLess(coef.value, 0)

        # R² should be high for linear relationship
        self.assertGreater(coef.r_squared, 0.90)

        # Typical range for c-Si: -0.3 to -0.5 %/°C
        self.assertGreater(coef.value, -1.0)
        self.assertLess(coef.value, 0)

    def test_temp_coefficient_voc(self):
        """Test Voc temperature coefficient calculation"""
        self.calc.add_measurements(self.measurements)

        # Test V/°C
        coef_v = self.calc.calculate_temp_coefficient_voc(unit="V/°C")
        self.assertEqual(coef_v.unit, "V/°C")
        self.assertLess(coef_v.value, 0)  # Should be negative

        # Test mV/°C
        coef_mv = self.calc.calculate_temp_coefficient_voc(unit="mV/°C")
        self.assertEqual(coef_mv.unit, "mV/°C")
        self.assertAlmostEqual(coef_mv.value, coef_v.value * 1000, places=2)

        # Test %/°C
        coef_pct = self.calc.calculate_temp_coefficient_voc(unit="%/°C")
        self.assertEqual(coef_pct.unit, "%/°C")
        self.assertLess(coef_pct.value, 0)

    def test_temp_coefficient_isc(self):
        """Test Isc temperature coefficient calculation"""
        self.calc.add_measurements(self.measurements)

        # Test A/°C
        coef_a = self.calc.calculate_temp_coefficient_isc(unit="A/°C")
        self.assertEqual(coef_a.unit, "A/°C")
        self.assertGreater(coef_a.value, 0)  # Should be positive

        # Test mA/°C
        coef_ma = self.calc.calculate_temp_coefficient_isc(unit="mA/°C")
        self.assertEqual(coef_ma.unit, "mA/°C")
        self.assertAlmostEqual(coef_ma.value, coef_a.value * 1000, places=2)

        # Test %/°C
        coef_pct = self.calc.calculate_temp_coefficient_isc(unit="%/°C")
        self.assertEqual(coef_pct.unit, "%/°C")
        self.assertGreater(coef_pct.value, 0)

    def test_insufficient_measurements(self):
        """Test error handling with insufficient measurements"""
        self.calc.add_measurements(self.measurements[:3])  # Only 3 measurements

        with self.assertRaises(ValueError) as context:
            self.calc.calculate_temp_coefficient_pmax()

        self.assertIn("Minimum 4 measurements", str(context.exception))

    def test_normalized_power_calculation(self):
        """Test normalized power at specific temperature"""
        self.calc.add_measurements(self.measurements)

        # Calculate power at 25°C
        power_25c = self.calc.calculate_normalized_power_at_temp(25.0)

        # Should be close to measured value at 25°C
        measured_25c = [m.pmax for m in self.measurements if m.temperature == 25.0][0]
        self.assertAlmostEqual(power_25c, measured_25c, delta=10.0)

    def test_calculate_all_coefficients(self):
        """Test calculation of all coefficients"""
        self.calc.add_measurements(self.measurements)
        results = self.calc.calculate_all_coefficients()

        self.assertIn('temp_coefficient_pmax', results)
        self.assertIn('temp_coefficient_voc', results)
        self.assertIn('temp_coefficient_isc', results)
        self.assertIn('reference_temperature', results)
        self.assertIn('normalized_power_25C', results)

        self.assertEqual(results['reference_temperature'], 25.0)

    def test_data_quality_validation(self):
        """Test data quality validation"""
        self.calc.add_measurements(self.measurements)
        quality = self.calc.validate_data_quality()

        self.assertIsInstance(quality, dict)
        self.assertIn('data_completeness', quality)
        self.assertIn('linearity_check', quality)
        self.assertIn('range_validation', quality)
        self.assertIn('warnings', quality)
        self.assertIn('errors', quality)

        # Should pass completeness
        self.assertTrue(quality['data_completeness'])

        # Should have good linearity
        self.assertTrue(quality['linearity_check'])

    def test_generate_report_data(self):
        """Test report data generation"""
        self.calc.add_measurements(self.measurements)
        report = self.calc.generate_report_data()

        self.assertIn('measurements', report)
        self.assertIn('calculated_results', report)
        self.assertIn('quality_checks', report)

        self.assertEqual(len(report['measurements']), 4)


class TestPERF001Validator(unittest.TestCase):
    """Test PERF001Validator"""

    def test_validate_against_schema(self):
        """Test schema validation"""
        # This test requires jsonschema package
        test_data = create_sample_data()

        # Load schema
        import json
        schema_path = Path(__file__).parent.parent / "schema" / "perf-001-schema.json"

        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)

            is_valid, errors = PERF001Validator.validate_against_schema(test_data, schema)

            if errors and 'jsonschema' not in str(errors[0]):
                self.assertTrue(is_valid, f"Validation errors: {errors}")

    def test_validate_physical_constraints(self):
        """Test physical constraint validation"""
        measurements = [
            Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
        ]

        is_valid, errors = PERF001Validator.validate_physical_constraints(measurements)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

    def test_invalid_power_equation(self):
        """Test detection of invalid power equation"""
        measurements = [
            Measurement(
                temperature=25.0,
                pmax=320.0,  # Inconsistent with Vmp*Imp
                voc=45.2,
                isc=9.18,
                vmp=30.0,  # Would give 30*8 = 240W, not 320W
                imp=8.0
            ),
        ]

        is_valid, errors = PERF001Validator.validate_physical_constraints(measurements)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestSampleDataGeneration(unittest.TestCase):
    """Test sample data generation"""

    def test_create_sample_data(self):
        """Test sample data creation"""
        sample_data = create_sample_data()

        self.assertIsInstance(sample_data, dict)
        self.assertIn('protocol_info', sample_data)
        self.assertIn('test_specimen', sample_data)
        self.assertIn('test_conditions', sample_data)
        self.assertIn('measurements', sample_data)
        self.assertIn('calculated_results', sample_data)
        self.assertIn('quality_checks', sample_data)
        self.assertIn('metadata', sample_data)

    def test_sample_data_structure(self):
        """Test sample data structure"""
        sample_data = create_sample_data()

        # Check protocol info
        self.assertEqual(sample_data['protocol_info']['protocol_id'], 'PERF-001')
        self.assertEqual(sample_data['protocol_info']['standard'], 'IEC 61853')

        # Check measurements
        measurements = sample_data['measurements']
        self.assertGreaterEqual(len(measurements), 4)

        # Check calculated results
        results = sample_data['calculated_results']
        self.assertIn('temp_coefficient_pmax', results)
        self.assertIn('temp_coefficient_voc', results)
        self.assertIn('temp_coefficient_isc', results)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_zero_values(self):
        """Test handling of zero values"""
        m = Measurement(
            temperature=25.0,
            pmax=0.0,
            voc=0.0,
            isc=0.0,
            vmp=0.0,
            imp=0.0
        )
        self.assertEqual(m.fill_factor, 0.0)

    def test_negative_temperature(self):
        """Test handling of negative temperatures"""
        m = Measurement(
            temperature=-40.0,  # Valid for some PV tests
            pmax=350.0,
            voc=50.0,
            isc=9.0,
            vmp=42.0,
            imp=8.33
        )
        self.assertEqual(m.temperature, -40.0)

    def test_high_temperature(self):
        """Test handling of high temperatures"""
        m = Measurement(
            temperature=85.0,  # Valid for thermal stress testing
            pmax=250.0,
            voc=36.0,
            isc=9.5,
            vmp=30.0,
            imp=8.33
        )
        self.assertEqual(m.temperature, 85.0)

    def test_empty_calculator(self):
        """Test calculator with no measurements"""
        calc = PERF001Calculator()

        with self.assertRaises(ValueError):
            calc.calculate_temp_coefficient_pmax()


class TestNumericalAccuracy(unittest.TestCase):
    """Test numerical accuracy of calculations"""

    def test_linear_regression_accuracy(self):
        """Test accuracy of linear regression"""
        # Create perfectly linear data
        temps = np.array([15, 25, 50, 75])
        # Pmax = -1.0 * T + 340 (perfect linear relationship)
        pmax_values = -1.0 * temps + 340

        measurements = [
            Measurement(
                temperature=float(t),
                pmax=float(p),
                voc=45.0,
                isc=9.0,
                vmp=37.0,
                imp=float(p/37.0)
            )
            for t, p in zip(temps, pmax_values)
        ]

        calc = PERF001Calculator(reference_temperature=25.0)
        calc.add_measurements(measurements)

        coef = calc.calculate_temp_coefficient_pmax()

        # R² should be exactly 1.0 for perfect linear data
        self.assertAlmostEqual(coef.r_squared, 1.0, places=10)

    def test_coefficient_units_consistency(self):
        """Test consistency across different units"""
        measurements = [
            Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
            Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
            Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
            Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
        ]

        calc = PERF001Calculator()
        calc.add_measurements(measurements)

        # VOC in different units
        coef_v = calc.calculate_temp_coefficient_voc(unit="V/°C")
        coef_mv = calc.calculate_temp_coefficient_voc(unit="mV/°C")

        # Check conversion accuracy
        self.assertAlmostEqual(coef_v.value * 1000, coef_mv.value, places=1)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
