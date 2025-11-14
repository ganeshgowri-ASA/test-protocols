"""
Unit tests for SOLDER-001 Handler
Tests data processing and analysis functions
"""

import unittest
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handler import SolderBondHandler


class TestSolderBondHandler(unittest.TestCase):
    """Test cases for SolderBondHandler"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol_config = {
            "protocol_id": "SOLDER-001",
            "acceptance_criteria": {
                "power_degradation": {"200_cycles": 2.0, "600_cycles": 5.0},
                "resistance_increase": {"200_cycles": 10.0, "600_cycles": 20.0}
            }
        }
        self.handler = SolderBondHandler(self.protocol_config)

    def test_initialization(self):
        """Test handler initialization"""
        self.assertEqual(self.handler.config, self.protocol_config)
        self.assertEqual(self.handler.results, {})
        self.assertEqual(self.handler.checkpoints, [])
        self.assertIsNone(self.handler.baseline_data)

    def test_process_initial_characterization(self):
        """Test initial characterization processing"""
        measurements = {
            'flash_test': {
                'pmax': 400.0,
                'voc': 48.5,
                'isc': 10.2,
                'fill_factor': 0.82
            },
            'resistance_map': {
                'cell_1_pos': 3.2,
                'cell_1_neg': 3.5,
                'cell_2_pos': 3.3,
                'cell_2_neg': 3.4,
                'busbar_1': 7.5
            },
            'ir_imaging': {
                'hotspot_count': 0,
                'max_delta_t': 5.0
            },
            'visual_inspection': {},
            'el_imaging': {}
        }

        result = self.handler.process_initial_characterization(measurements)

        self.assertIn('initial_power', result)
        self.assertEqual(result['initial_power'], 400.0)
        self.assertIn('avg_cell_resistance', result)
        self.assertAlmostEqual(result['avg_cell_resistance'], 3.35, places=2)
        self.assertIsNotNone(self.handler.baseline_data)

    def test_analyze_resistance_change(self):
        """Test resistance change analysis"""
        # Set baseline
        self.handler.baseline_data = {
            'resistance_map': {
                'joint_1': 3.0,
                'joint_2': 3.2,
                'joint_3': 3.1
            },
            'flash_test': {},
            'timestamp': datetime.now().isoformat()
        }

        # Current resistance (increased)
        current_resistance = {
            'joint_1': 3.3,
            'joint_2': 3.5,
            'joint_3': 3.4
        }

        result = self.handler.analyze_resistance_change(current_resistance, 200)

        self.assertEqual(result['checkpoint'], 200)
        self.assertIn('percentage_change', result)
        self.assertGreater(result['percentage_change'], 0)
        self.assertIn('worst_joints', result)
        self.assertEqual(result['joints_analyzed'], 3)

    def test_analyze_power_degradation(self):
        """Test power degradation analysis"""
        # Set baseline
        self.handler.baseline_data = {
            'flash_test': {
                'pmax': 400.0,
                'series_resistance': 0.50,
                'fill_factor': 0.82
            },
            'resistance_map': {},
            'timestamp': datetime.now().isoformat()
        }

        # Current flash test (degraded)
        flash_test = {
            'pmax': 392.0,
            'series_resistance': 0.55,
            'fill_factor': 0.80
        }

        result = self.handler.analyze_power_degradation(flash_test, 200)

        self.assertEqual(result['checkpoint'], 200)
        self.assertEqual(result['baseline_power_w'], 400.0)
        self.assertEqual(result['current_power_w'], 392.0)
        self.assertEqual(result['power_loss_w'], 8.0)
        self.assertEqual(result['power_loss_pct'], 2.0)
        self.assertGreater(result['rs_increase_pct'], 0)

    def test_calculate_degradation_rate(self):
        """Test degradation rate calculation"""
        # Add checkpoints
        self.handler.checkpoints = [
            {
                'checkpoint': 50,
                'resistance': {'percentage_change': 2.5},
                'power': {'power_loss_pct': 0.5}
            },
            {
                'checkpoint': 100,
                'resistance': {'percentage_change': 5.0},
                'power': {'power_loss_pct': 1.0}
            },
            {
                'checkpoint': 200,
                'resistance': {'percentage_change': 10.0},
                'power': {'power_loss_pct': 2.0}
            }
        ]

        result = self.handler.calculate_degradation_rate()

        self.assertIn('resistance_degradation', result)
        self.assertIn('power_degradation', result)
        self.assertIn('rate_per_100_cycles', result['resistance_degradation'])
        self.assertIn('r_squared', result['resistance_degradation'])
        self.assertGreater(result['resistance_degradation']['r_squared'], 0.9)

    def test_predict_lifetime(self):
        """Test lifetime prediction"""
        # Add checkpoints for prediction
        self.handler.checkpoints = [
            {
                'checkpoint': 100,
                'resistance': {'percentage_change': 3.0},
                'power': {'power_loss_pct': 0.8}
            },
            {
                'checkpoint': 200,
                'resistance': {'percentage_change': 6.0},
                'power': {'power_loss_pct': 1.6}
            },
            {
                'checkpoint': 400,
                'resistance': {'percentage_change': 12.0},
                'power': {'power_loss_pct': 3.2}
            }
        ]

        result = self.handler.predict_lifetime(failure_threshold=20.0)

        self.assertIn('predicted_lifetime_years', result)
        self.assertIn('cycles_to_failure', result)
        self.assertIn('year_25_projection', result)
        self.assertGreater(result['predicted_lifetime_years'], 0)

    def test_process_pull_test_results(self):
        """Test pull test results processing"""
        pull_test_data = [
            {'sample_type': 'fresh', 'force': 32.5},
            {'sample_type': 'fresh', 'force': 33.0},
            {'sample_type': 'fresh', 'force': 31.8},
            {'sample_type': 'aged', 'force': 26.0},
            {'sample_type': 'aged', 'force': 25.5},
            {'sample_type': 'aged', 'force': 26.3}
        ]

        result = self.handler.process_pull_test_results(pull_test_data)

        self.assertIn('fresh_samples', result)
        self.assertIn('aged_samples', result)
        self.assertIn('degradation', result)
        self.assertAlmostEqual(result['fresh_samples']['mean_force_n'], 32.43, places=1)
        self.assertAlmostEqual(result['aged_samples']['mean_force_n'], 25.93, places=1)
        self.assertGreater(result['degradation']['percentage_loss'], 0)

    def test_analyze_thermal_imaging(self):
        """Test thermal imaging analysis"""
        self.handler.baseline_data = {
            'ir_imaging': {'hotspot_count': 1},
            'flash_test': {},
            'resistance_map': {}
        }

        ir_data = {
            'hotspot_count': 3,
            'max_delta_t': 18.5,
            'avg_cell_temp': 65.0
        }

        result = self.handler.analyze_thermal_imaging(ir_data, 200)

        self.assertEqual(result['checkpoint'], 200)
        self.assertEqual(result['hotspot_count'], 3)
        self.assertEqual(result['new_hotspots'], 2)
        self.assertEqual(result['max_delta_t'], 18.5)

    def test_analyze_visual_defects(self):
        """Test visual defect analysis"""
        visual_data = {
            'defects': [
                {'type': 'discoloration', 'severity': 'MINOR'},
                {'type': 'discoloration', 'severity': 'MINOR'},
                {'type': 'solder_crack', 'severity': 'CRITICAL'}
            ]
        }

        result = self.handler.analyze_visual_defects(visual_data, 400)

        self.assertEqual(result['checkpoint'], 400)
        self.assertEqual(result['total_defects'], 3)
        self.assertEqual(result['critical_count'], 1)
        self.assertEqual(result['minor_count'], 2)
        self.assertIn('discoloration', result['defect_types'])

    def test_generate_statistical_summary(self):
        """Test statistical summary generation"""
        self.handler.checkpoints = [
            {
                'checkpoint': 100,
                'resistance': {'percentage_change': 3.0},
                'power': {'power_loss_pct': 0.8}
            },
            {
                'checkpoint': 200,
                'resistance': {'percentage_change': 6.0},
                'power': {'power_loss_pct': 1.6}
            }
        ]

        result = self.handler.generate_statistical_summary()

        self.assertIn('resistance_statistics', result)
        self.assertIn('power_statistics', result)
        self.assertIn('mean', result['resistance_statistics'])
        self.assertIn('std_dev', result['resistance_statistics'])
        self.assertEqual(result['checkpoints_analyzed'], 2)

    def test_calculate_avg_resistance(self):
        """Test average resistance calculation"""
        resistance_map = {
            'joint_1': 3.0,
            'joint_2': 3.5,
            'joint_3': 4.0,
            'joint_4': 3.2
        }

        avg = self.handler._calculate_avg_resistance(resistance_map)
        self.assertAlmostEqual(avg, 3.425, places=3)

    def test_calculate_max_resistance(self):
        """Test maximum resistance calculation"""
        resistance_map = {
            'joint_1': 3.0,
            'joint_2': 3.5,
            'joint_3': 4.2,
            'joint_4': 3.8
        }

        max_r = self.handler._calculate_max_resistance(resistance_map)
        self.assertEqual(max_r, 4.2)

    def test_categorize_defect_types(self):
        """Test defect categorization"""
        defects = [
            {'type': 'solder_crack'},
            {'type': 'discoloration'},
            {'type': 'solder_crack'},
            {'type': 'delamination'}
        ]

        categories = self.handler._categorize_defect_types(defects)

        self.assertEqual(categories['solder_crack'], 2)
        self.assertEqual(categories['discoloration'], 1)
        self.assertEqual(categories['delamination'], 1)

    def test_generate_report_data(self):
        """Test report data generation"""
        # Set up minimal data
        self.handler.baseline_data = {
            'flash_test': {'pmax': 400},
            'resistance_map': {},
            'timestamp': datetime.now().isoformat()
        }
        self.handler.checkpoints = []

        result = self.handler.generate_report_data()

        self.assertEqual(result['protocol_id'], 'SOLDER-001')
        self.assertIn('test_date', result)
        self.assertIn('baseline', result)
        self.assertIn('overall_status', result)


if __name__ == '__main__':
    unittest.main()
