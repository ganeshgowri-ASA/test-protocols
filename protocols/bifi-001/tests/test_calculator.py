"""
Unit tests for BifacialCalculator
"""

import unittest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.calculator import BifacialCalculator, IVParameters


class TestBifacialCalculator(unittest.TestCase):
    """Test cases for BifacialCalculator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = BifacialCalculator()

        # Create realistic I-V curve data
        self.front_iv_curve = self._generate_iv_curve(voc=45.0, isc=10.0, num_points=50)
        self.rear_iv_curve = self._generate_iv_curve(voc=43.0, isc=7.0, num_points=50)

    def _generate_iv_curve(self, voc, isc, num_points=50):
        """Generate realistic I-V curve using diode equation approximation"""
        voltage = np.linspace(0, voc, num_points)
        # Simple approximation: I = Isc * (1 - (V/Voc)^2)
        current = isc * (1 - (voltage / voc) ** 2)

        return [
            {"voltage": float(v), "current": float(i)}
            for v, i in zip(voltage, current)
        ]

    def test_calculate_iv_parameters_basic(self):
        """Test basic I-V parameter calculation"""
        params = self.calculator.calculate_iv_parameters(self.front_iv_curve)

        self.assertIsInstance(params, IVParameters)
        self.assertGreater(params.isc, 0)
        self.assertGreater(params.voc, 0)
        self.assertGreater(params.pmax, 0)
        self.assertGreater(params.fill_factor, 0)
        self.assertLessEqual(params.fill_factor, 1)

    def test_calculate_iv_parameters_values(self):
        """Test I-V parameter calculation produces reasonable values"""
        params = self.calculator.calculate_iv_parameters(self.front_iv_curve)

        # Check Isc is close to expected (10.0)
        self.assertAlmostEqual(params.isc, 10.0, delta=0.5)

        # Check Voc is close to expected (45.0)
        self.assertAlmostEqual(params.voc, 45.0, delta=1.0)

        # Pmax should be less than Isc × Voc
        self.assertLess(params.pmax, params.isc * params.voc)

        # Fill factor should be reasonable (0.7-0.85 for good cells)
        self.assertGreater(params.fill_factor, 0.6)
        self.assertLess(params.fill_factor, 0.9)

    def test_calculate_iv_parameters_with_area(self):
        """Test efficiency calculation with area"""
        area = 25000  # cm²
        irradiance = 1000  # W/m²

        params = self.calculator.calculate_iv_parameters(
            self.front_iv_curve,
            area=area,
            irradiance=irradiance
        )

        self.assertIsNotNone(params.efficiency)
        self.assertGreater(params.efficiency, 0)
        self.assertLess(params.efficiency, 100)

    def test_calculate_iv_parameters_insufficient_data(self):
        """Test error handling with insufficient data"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_iv_parameters([])

        with self.assertRaises(ValueError):
            self.calculator.calculate_iv_parameters([{"voltage": 0, "current": 5}])

    def test_calculate_bifaciality(self):
        """Test bifaciality factor calculation"""
        front_pmax = 350.0
        rear_pmax = 245.0

        bifaciality = self.calculator.calculate_bifaciality(front_pmax, rear_pmax)

        self.assertAlmostEqual(bifaciality, 0.70, places=2)

    def test_calculate_bifaciality_edge_cases(self):
        """Test bifaciality calculation edge cases"""
        # Zero front power
        self.assertEqual(self.calculator.calculate_bifaciality(0, 100), 0)

        # Equal front and rear
        self.assertEqual(self.calculator.calculate_bifaciality(100, 100), 1.0)

        # Rear exceeds front (possible in some conditions)
        self.assertGreater(self.calculator.calculate_bifaciality(100, 120), 1.0)

    def test_calculate_bifacial_gain(self):
        """Test bifacial gain calculation"""
        front_pmax = 350.0
        rear_pmax = 245.0
        front_irradiance = 1000.0
        rear_irradiance = 150.0

        gain = self.calculator.calculate_bifacial_gain(
            front_pmax, rear_pmax, front_irradiance, rear_irradiance
        )

        self.assertGreater(gain, 0)
        self.assertIsInstance(gain, float)

        # Gain should be positive for bifacial modules
        # Normalized rear contribution should be rear_pmax * (1000/150) / front_pmax
        expected_normalized_rear = rear_pmax * (front_irradiance / rear_irradiance)
        expected_gain = (expected_normalized_rear / front_pmax) * 100
        self.assertAlmostEqual(gain, expected_gain, places=1)

    def test_calculate_bifacial_gain_zero_irradiance(self):
        """Test bifacial gain with zero irradiance"""
        gain = self.calculator.calculate_bifacial_gain(100, 70, 0, 150)
        self.assertEqual(gain, 0)

    def test_calculate_equivalent_efficiency(self):
        """Test equivalent efficiency calculation"""
        front_params = IVParameters(
            isc=10.0, voc=45.0, pmax=350.0, imp=9.5, vmp=36.8, fill_factor=0.78
        )
        rear_params = IVParameters(
            isc=7.0, voc=43.0, pmax=245.0, imp=6.7, vmp=36.6, fill_factor=0.81
        )

        area = 25000  # cm²
        front_irr = 1000  # W/m²
        rear_irr = 150  # W/m²

        equiv_eff = self.calculator.calculate_equivalent_efficiency(
            front_params, rear_params, front_irr, rear_irr, area
        )

        self.assertGreater(equiv_eff, 0)
        self.assertLess(equiv_eff, 100)

        # Should be greater than front-only efficiency
        area_m2 = area / 10000
        front_only_eff = (front_params.pmax / (front_irr * area_m2)) * 100
        self.assertGreater(equiv_eff, front_only_eff)

    def test_calculate_uncertainty(self):
        """Test uncertainty calculation"""
        measurements = {}  # Minimal input

        uncertainty = self.calculator.calculate_uncertainty(measurements)

        self.assertIn("front_pmax_uncertainty", uncertainty)
        self.assertIn("rear_pmax_uncertainty", uncertainty)
        self.assertIn("combined_uncertainty", uncertainty)

        # Check all values are positive
        self.assertGreater(uncertainty["front_pmax_uncertainty"], 0)
        self.assertGreater(uncertainty["rear_pmax_uncertainty"], 0)
        self.assertGreater(uncertainty["combined_uncertainty"], 0)

        # Rear should have higher uncertainty
        self.assertGreater(
            uncertainty["rear_pmax_uncertainty"],
            uncertainty["front_pmax_uncertainty"]
        )

        # Combined should be greater than either individual
        self.assertGreater(
            uncertainty["combined_uncertainty"],
            uncertainty["front_pmax_uncertainty"]
        )

    def test_smooth_iv_curve(self):
        """Test I-V curve smoothing"""
        # Add some noise to the curve
        noisy_curve = []
        for point in self.front_iv_curve:
            noisy_point = point.copy()
            noisy_point["current"] += np.random.normal(0, 0.1)
            noisy_curve.append(noisy_point)

        smoothed = self.calculator.smooth_iv_curve(noisy_curve, window_size=5)

        # Smoothed curve should have fewer points
        self.assertLess(len(smoothed), len(noisy_curve))

        # All points should have voltage and current
        for point in smoothed:
            self.assertIn("voltage", point)
            self.assertIn("current", point)

    def test_smooth_iv_curve_insufficient_points(self):
        """Test smoothing with insufficient points"""
        short_curve = [{"voltage": i, "current": 5-i} for i in range(3)]
        smoothed = self.calculator.smooth_iv_curve(short_curve, window_size=5)

        # Should return original if not enough points
        self.assertEqual(len(smoothed), len(short_curve))

    def test_interpolate_to_stc(self):
        """Test STC interpolation"""
        params = self.calculator.calculate_iv_parameters(self.front_iv_curve)

        # Measured at slightly different conditions
        measured_irradiance = 950  # W/m²
        measured_temp = 28  # °C

        stc_params = self.calculator.interpolate_to_stc(
            params, measured_irradiance, measured_temp
        )

        self.assertIsInstance(stc_params, IVParameters)

        # Corrected values should be different
        self.assertNotEqual(stc_params.isc, params.isc)
        self.assertNotEqual(stc_params.voc, params.voc)

        # Current should increase with irradiance correction (950 -> 1000)
        self.assertGreater(stc_params.isc, params.isc)

    def test_interpolate_to_stc_with_coefficients(self):
        """Test STC interpolation with custom temperature coefficients"""
        params = self.calculator.calculate_iv_parameters(self.front_iv_curve)

        temp_coeffs = {
            "voc_temp_coeff": -0.30,  # %/°C
            "isc_temp_coeff": 0.06,
            "pmax_temp_coeff": -0.40
        }

        stc_params = self.calculator.interpolate_to_stc(
            params, 1000, 30, temp_coeffs
        )

        # At 30°C (5°C above STC), Voc should increase when corrected to 25°C
        # because Voc has negative temp coeff
        self.assertGreater(stc_params.voc, params.voc)

    def test_calculate_temperature_coefficients(self):
        """Test temperature coefficient calculation"""
        # Create measurements at different temperatures
        temps = [25, 30, 35, 40]
        measurements = []

        for temp in temps:
            # Simulate temperature-dependent I-V curve
            voc = 45.0 - 0.15 * (temp - 25)  # Voc decreases with temp
            isc = 10.0 + 0.005 * (temp - 25)  # Isc increases with temp

            iv_curve = self._generate_iv_curve(voc, isc, 50)
            params = self.calculator.calculate_iv_parameters(iv_curve)
            measurements.append((temp, params))

        coeffs = self.calculator.calculate_temperature_coefficients(measurements)

        self.assertIn("voc_temp_coeff", coeffs)
        self.assertIn("isc_temp_coeff", coeffs)
        self.assertIn("pmax_temp_coeff", coeffs)

        # Voc should have negative temp coefficient
        self.assertLess(coeffs["voc_temp_coeff"], 0)

        # Isc should have positive temp coefficient
        self.assertGreater(coeffs["isc_temp_coeff"], 0)

    def test_calculate_temperature_coefficients_insufficient_data(self):
        """Test temperature coefficient calculation with insufficient data"""
        params = self.calculator.calculate_iv_parameters(self.front_iv_curve)
        measurements = [(25, params)]  # Only one measurement

        with self.assertRaises(ValueError):
            self.calculator.calculate_temperature_coefficients(measurements)


class TestIVParameters(unittest.TestCase):
    """Test IVParameters dataclass"""

    def test_iv_parameters_creation(self):
        """Test creating IVParameters object"""
        params = IVParameters(
            isc=10.0,
            voc=45.0,
            pmax=350.0,
            imp=9.5,
            vmp=36.8,
            fill_factor=0.78,
            efficiency=14.0
        )

        self.assertEqual(params.isc, 10.0)
        self.assertEqual(params.voc, 45.0)
        self.assertEqual(params.pmax, 350.0)
        self.assertEqual(params.efficiency, 14.0)

    def test_iv_parameters_without_efficiency(self):
        """Test creating IVParameters without efficiency"""
        params = IVParameters(
            isc=10.0,
            voc=45.0,
            pmax=350.0,
            imp=9.5,
            vmp=36.8,
            fill_factor=0.78
        )

        self.assertIsNone(params.efficiency)


if __name__ == '__main__':
    unittest.main()
