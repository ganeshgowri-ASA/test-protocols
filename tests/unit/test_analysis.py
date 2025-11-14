"""
Unit tests for analysis modules.
"""

import unittest
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analysis.crack_detection import CrackDetector
from analysis.iv_analysis import IVAnalyzer, IVCurveSimulator


class TestCrackDetector(unittest.TestCase):
    """Test cases for crack detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = CrackDetector(sensitivity='medium')

    def test_initialization(self):
        """Test detector initialization."""
        self.assertEqual(self.detector.sensitivity, 'medium')

    def test_detect_cracks_structure(self):
        """Test crack detection returns proper structure."""
        # Mock image path (doesn't need to exist for structure test)
        result = self.detector.detect_cracks(Path("test_image.png"))

        # Check result structure
        self.assertIn('image_path', result)
        self.assertIn('cracks_detected', result)
        self.assertIn('crack_count', result)
        self.assertIn('total_crack_area', result)
        self.assertIn('total_crack_length', result)
        self.assertIn('crack_severity', result)
        self.assertIn('metadata', result)

    def test_calculate_crack_area_percentage(self):
        """Test crack area percentage calculation."""
        crack_area_mm2 = 50.0
        cell_area_cm2 = 243.36

        percentage = self.detector.calculate_crack_area_percentage(
            crack_area_mm2,
            cell_area_cm2
        )

        expected = (50.0 / (243.36 * 100)) * 100
        self.assertAlmostEqual(percentage, expected, places=2)


class TestIVAnalyzer(unittest.TestCase):
    """Test cases for IV curve analysis."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = IVAnalyzer()

        # Generate test IV curve
        self.voltage, self.current = IVCurveSimulator.generate_ideal_curve(
            voc=0.68,
            isc=9.5,
            points=100
        )

    def test_analyze_iv_curve(self):
        """Test IV curve analysis."""
        results = self.analyzer.analyze_iv_curve(
            self.voltage,
            self.current,
            irradiance=1000.0,
            temperature=25.0,
            cell_area=243.36
        )

        # Check result structure
        self.assertIn('pmax', results)
        self.assertIn('vmp', results)
        self.assertIn('imp', results)
        self.assertIn('voc', results)
        self.assertIn('isc', results)
        self.assertIn('ff', results)
        self.assertIn('efficiency', results)
        self.assertIn('rs', results)
        self.assertIn('rsh', results)

        # Check value ranges
        self.assertGreater(results['pmax'], 0)
        self.assertGreater(results['voc'], 0)
        self.assertGreater(results['isc'], 0)
        self.assertGreater(results['ff'], 0)
        self.assertLess(results['ff'], 1)

    def test_find_voc(self):
        """Test Voc detection."""
        voc = self.analyzer._find_voc(self.voltage, self.current)
        self.assertAlmostEqual(voc, 0.68, places=2)

    def test_find_isc(self):
        """Test Isc detection."""
        isc = self.analyzer._find_isc(self.voltage, self.current)
        self.assertAlmostEqual(isc, 9.5, places=1)

    def test_compare_iv_curves(self):
        """Test IV curve comparison."""
        initial = {
            'pmax': 5.0,
            'voc': 0.68,
            'isc': 9.5,
            'ff': 0.80
        }

        final = {
            'pmax': 4.78,
            'voc': 0.665,
            'isc': 9.3,
            'ff': 0.795
        }

        comparison = self.analyzer.compare_iv_curves(initial, final)

        # Check structure
        self.assertIn('pmax', comparison)
        self.assertIn('voc', comparison)
        self.assertIn('isc', comparison)
        self.assertIn('ff', comparison)

        # Check pmax degradation
        self.assertEqual(comparison['pmax']['initial'], 5.0)
        self.assertEqual(comparison['pmax']['final'], 4.78)
        self.assertLess(comparison['pmax']['relative_change'], 0)

    def test_calculate_degradation_rate(self):
        """Test degradation rate calculation."""
        measurements = [
            (0, {'pmax': 5.0}),
            (50, {'pmax': 4.95}),
            (100, {'pmax': 4.88}),
            (150, {'pmax': 4.82}),
            (200, {'pmax': 4.78})
        ]

        rate = self.analyzer.calculate_degradation_rate(measurements, 'pmax')

        # Check structure
        self.assertIn('rate_per_cycle', rate)
        self.assertIn('rate_per_cycle_percent', rate)
        self.assertIn('total_degradation', rate)
        self.assertIn('total_degradation_percent', rate)

        # Check values
        self.assertLess(rate['rate_per_cycle'], 0)  # Should be negative (degradation)
        self.assertLess(rate['total_degradation'], 0)

    def test_temperature_correct(self):
        """Test temperature correction."""
        iv_params = {
            'pmax': 5.0,
            'voc': 0.68,
            'isc': 9.5,
            'ff': 0.80
        }

        corrected = self.analyzer.temperature_correct(
            iv_params,
            measured_temp=30.0,
            target_temp=25.0
        )

        # Check structure
        self.assertIn('voc', corrected)
        self.assertIn('isc', corrected)

        # Voc should decrease with temperature
        # Correcting from 30°C to 25°C should increase Voc
        self.assertGreater(corrected['voc'], iv_params['voc'])


class TestIVCurveSimulator(unittest.TestCase):
    """Test cases for IV curve simulator."""

    def test_generate_ideal_curve(self):
        """Test ideal curve generation."""
        voltage, current = IVCurveSimulator.generate_ideal_curve(
            voc=0.68,
            isc=9.5,
            points=100
        )

        # Check array lengths
        self.assertEqual(len(voltage), 100)
        self.assertEqual(len(current), 100)

        # Check voltage range
        self.assertAlmostEqual(voltage[0], 0.0, places=2)
        self.assertAlmostEqual(voltage[-1], 0.68, places=2)

        # Check current range
        self.assertGreater(current[0], 0)  # Should be near Isc
        self.assertAlmostEqual(current[-1], 0.0, places=1)  # Should be near 0 at Voc

    def test_add_degradation(self):
        """Test degradation simulation."""
        voltage, current = IVCurveSimulator.generate_ideal_curve(
            voc=0.68,
            isc=9.5,
            points=100
        )

        voltage_deg, current_deg = IVCurveSimulator.add_degradation(
            voltage,
            current,
            pmax_loss=0.05,
            ff_loss=0.02
        )

        # Degraded current should be lower
        self.assertTrue(np.all(current_deg <= current))

        # Maximum degraded current should be less than original
        self.assertLess(np.max(current_deg), np.max(current))


if __name__ == '__main__':
    unittest.main()
