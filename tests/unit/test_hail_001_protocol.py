"""
Unit tests for HAIL-001 Hail Impact Test Protocol
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.protocols.loader import ProtocolLoader
from src.protocols.hail_001 import HAIL001Protocol
from src.analysis.calculations import PowerDegradationCalculator, StatisticalAnalyzer


class TestProtocolLoader(unittest.TestCase):
    """Test protocol loader functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocols_dir = Path(__file__).parent.parent.parent / "protocols"

    def test_load_hail_001_protocol(self):
        """Test loading HAIL-001 protocol"""
        loader = ProtocolLoader(str(self.protocols_dir))
        protocol_data = loader.load_protocol("HAIL-001")

        self.assertIsNotNone(protocol_data)
        self.assertEqual(protocol_data['protocol_id'], "HAIL-001")
        self.assertEqual(protocol_data['category'], "Mechanical")
        self.assertEqual(protocol_data['standard']['name'], "IEC 61215 MQT 17")

    def test_protocol_validation(self):
        """Test protocol data validation"""
        loader = ProtocolLoader(str(self.protocols_dir))

        # Valid protocol should not raise
        protocol_data = loader.load_protocol("HAIL-001")
        self.assertIn('protocol_id', protocol_data)
        self.assertIn('test_parameters', protocol_data)
        self.assertIn('pass_fail_criteria', protocol_data)

    def test_invalid_protocol(self):
        """Test loading non-existent protocol"""
        loader = ProtocolLoader(str(self.protocols_dir))

        with self.assertRaises(FileNotFoundError):
            loader.load_protocol("NONEXISTENT-001")


class TestHAIL001Protocol(unittest.TestCase):
    """Test HAIL-001 protocol implementation"""

    def setUp(self):
        """Set up test fixtures"""
        protocols_dir = Path(__file__).parent.parent.parent / "protocols"
        loader = ProtocolLoader(str(protocols_dir))
        protocol_data = loader.load_protocol("HAIL-001")
        self.protocol = HAIL001Protocol(protocol_data)

    def test_protocol_initialization(self):
        """Test protocol initialization"""
        self.assertEqual(self.protocol.protocol_id, "HAIL-001")
        self.assertEqual(self.protocol.title, "Hail Impact Test")
        self.assertEqual(self.protocol.category, "Mechanical")

    def test_validate_complete_test_data(self):
        """Test validation of complete test data"""
        test_data = self._create_valid_test_data()

        is_valid, errors = self.protocol.validate_test_data(test_data)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_missing_pre_test_data(self):
        """Test validation with missing pre-test data"""
        test_data = self._create_valid_test_data()
        del test_data['pre_test_data']['Pmax_initial']

        is_valid, errors = self.protocol.validate_test_data(test_data)

        self.assertFalse(is_valid)
        self.assertTrue(any('Pmax' in error for error in errors))

    def test_validate_incorrect_impact_count(self):
        """Test validation with incorrect number of impacts"""
        test_data = self._create_valid_test_data()
        test_data['test_execution_data']['impacts'] = \
            test_data['test_execution_data']['impacts'][:5]  # Only 5 impacts

        is_valid, errors = self.protocol.validate_test_data(test_data)

        self.assertFalse(is_valid)
        self.assertTrue(any('11 impacts' in error for error in errors))

    def test_validate_velocity_out_of_tolerance(self):
        """Test validation with velocity out of tolerance"""
        test_data = self._create_valid_test_data()
        test_data['test_execution_data']['impacts'][0]['actual_velocity_kmh'] = 90.0

        is_valid, errors = self.protocol.validate_test_data(test_data)

        self.assertFalse(is_valid)
        self.assertTrue(any('velocity' in error.lower() for error in errors))

    def test_analyze_results(self):
        """Test results analysis"""
        test_data = self._create_valid_test_data()

        analysis_results = self.protocol.analyze_results(test_data)

        self.assertIn('power_analysis', analysis_results)
        self.assertIn('impact_analysis', analysis_results)
        self.assertIn('visual_analysis', analysis_results)
        self.assertIn('insulation_analysis', analysis_results)

    def test_power_degradation_calculation(self):
        """Test power degradation calculation in analysis"""
        test_data = self._create_valid_test_data()
        test_data['pre_test_data']['Pmax_initial'] = 300.0
        test_data['post_test_data']['Pmax_final'] = 285.0  # 5% degradation

        analysis_results = self.protocol.analyze_results(test_data)

        self.assertEqual(analysis_results['power_analysis']['Pmax_initial'], 300.0)
        self.assertEqual(analysis_results['power_analysis']['Pmax_final'], 285.0)
        self.assertAlmostEqual(analysis_results['power_analysis']['degradation_percent'], 5.0, places=1)

    def test_evaluate_pass_fail_passing_test(self):
        """Test pass/fail evaluation for passing test"""
        test_data = self._create_valid_test_data()
        analysis_results = self.protocol.analyze_results(test_data)

        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)

        self.assertEqual(pass_fail_results['overall_result'], 'PASS')
        self.assertTrue(pass_fail_results['criteria']['power_degradation']['pass'])
        self.assertTrue(pass_fail_results['criteria']['visual_inspection']['pass'])
        self.assertTrue(pass_fail_results['criteria']['insulation_resistance']['pass'])
        self.assertTrue(pass_fail_results['criteria']['open_circuit']['pass'])

    def test_evaluate_pass_fail_failing_power_degradation(self):
        """Test pass/fail evaluation with excessive power degradation"""
        test_data = self._create_valid_test_data()
        test_data['pre_test_data']['Pmax_initial'] = 300.0
        test_data['post_test_data']['Pmax_final'] = 270.0  # 10% degradation (fails)

        analysis_results = self.protocol.analyze_results(test_data)
        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)

        self.assertEqual(pass_fail_results['overall_result'], 'FAIL')
        self.assertFalse(pass_fail_results['criteria']['power_degradation']['pass'])

    def test_evaluate_pass_fail_visual_defects(self):
        """Test pass/fail evaluation with visual defects"""
        test_data = self._create_valid_test_data()
        test_data['post_test_data']['visual_defects']['backsheet_cracks'] = True

        analysis_results = self.protocol.analyze_results(test_data)
        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)

        self.assertEqual(pass_fail_results['overall_result'], 'FAIL')
        self.assertFalse(pass_fail_results['criteria']['visual_inspection']['pass'])

    def test_evaluate_pass_fail_open_circuit(self):
        """Test pass/fail evaluation with open circuit detection"""
        test_data = self._create_valid_test_data()
        test_data['test_execution_data']['impacts'][0]['open_circuit_detected'] = True

        analysis_results = self.protocol.analyze_results(test_data)
        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)

        self.assertEqual(pass_fail_results['overall_result'], 'FAIL')
        self.assertFalse(pass_fail_results['criteria']['open_circuit']['pass'])

    def test_generate_impact_locations(self):
        """Test impact location generation"""
        locations = self.protocol.generate_impact_locations()

        self.assertEqual(len(locations), 11)
        self.assertEqual(locations[0]['description'], 'Center')
        self.assertEqual(locations[0]['x'], 0.5)
        self.assertEqual(locations[0]['y'], 0.5)

    def _create_valid_test_data(self):
        """Create valid test data for testing"""
        return {
            'pre_test_data': {
                'Pmax_initial': 300.0,
                'Voc': 40.5,
                'Isc': 9.2,
                'Vmp': 33.6,
                'Imp': 8.93,
                'fill_factor': 0.804,
                'insulation_resistance_initial': 500.0
            },
            'test_execution_data': {
                'impacts': [
                    {
                        'impact_number': i,
                        'impact_location': i,
                        'actual_velocity_kmh': 80.0 + (i % 3 - 1) * 0.5,
                        'time_delta_seconds': 45 + i,
                        'open_circuit_detected': False
                    }
                    for i in range(1, 12)
                ]
            },
            'post_test_data': {
                'Pmax_final': 295.0,
                'Voc': 40.3,
                'Isc': 9.1,
                'Vmp': 33.5,
                'Imp': 8.85,
                'fill_factor': 0.802,
                'insulation_resistance_final': 490.0,
                'visual_defects': {
                    'front_glass_cracks': False,
                    'cell_cracks': False,
                    'backsheet_cracks': False,
                    'delamination': False,
                    'junction_box_damage': False,
                    'frame_damage': False
                }
            }
        }


class TestCalculations(unittest.TestCase):
    """Test calculation utilities"""

    def test_power_degradation_calculator(self):
        """Test power degradation calculation"""
        calc = PowerDegradationCalculator()

        degradation = calc.calculate_degradation(300.0, 285.0)
        self.assertEqual(degradation, 5.0)

        degradation = calc.calculate_degradation(300.0, 300.0)
        self.assertEqual(degradation, 0.0)

    def test_power_degradation_zero_initial(self):
        """Test power degradation with zero initial power"""
        calc = PowerDegradationCalculator()

        with self.assertRaises(ValueError):
            calc.calculate_degradation(0.0, 285.0)

    def test_power_degradation_watts(self):
        """Test absolute power degradation calculation"""
        calc = PowerDegradationCalculator()

        degradation_watts = calc.calculate_degradation_watts(300.0, 285.0)
        self.assertEqual(degradation_watts, 15.0)

    def test_is_within_tolerance(self):
        """Test tolerance checking"""
        calc = PowerDegradationCalculator()

        self.assertTrue(calc.is_within_tolerance(4.5))
        self.assertTrue(calc.is_within_tolerance(5.0))
        self.assertFalse(calc.is_within_tolerance(5.1))

    def test_statistical_analyzer(self):
        """Test statistical analysis"""
        analyzer = StatisticalAnalyzer()
        data = [78.5, 79.0, 80.0, 80.5, 81.0, 79.5, 80.2, 79.8, 80.3, 79.9, 80.1]

        stats = analyzer.calculate_statistics(data)

        self.assertAlmostEqual(stats['mean'], 79.89, places=1)
        self.assertGreater(stats['std'], 0)
        self.assertEqual(stats['min'], 78.5)
        self.assertEqual(stats['max'], 81.0)
        self.assertEqual(stats['count'], 11)

    def test_statistical_analyzer_empty_data(self):
        """Test statistical analysis with empty dataset"""
        analyzer = StatisticalAnalyzer()
        stats = analyzer.calculate_statistics([])

        self.assertEqual(stats['mean'], 0)
        self.assertEqual(stats['count'], 0)

    def test_compliance_rate(self):
        """Test compliance rate calculation"""
        analyzer = StatisticalAnalyzer()

        rate = analyzer.calculate_compliance_rate(9, 11)
        self.assertAlmostEqual(rate, 81.82, places=2)

        rate = analyzer.calculate_compliance_rate(11, 11)
        self.assertEqual(rate, 100.0)

        rate = analyzer.calculate_compliance_rate(0, 0)
        self.assertEqual(rate, 0.0)


if __name__ == '__main__':
    unittest.main()
