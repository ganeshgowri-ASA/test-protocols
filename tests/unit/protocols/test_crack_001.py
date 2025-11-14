"""
Unit tests for CRACK-001 protocol implementation.
"""

import unittest
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from protocols.base import ProtocolDefinition, SampleMetadata
from protocols.degradation.crack_001 import CrackPropagationProtocol


class TestCrackPropagationProtocol(unittest.TestCase):
    """Test cases for CRACK-001 protocol."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Load protocol definition
        protocol_path = Path(__file__).parent.parent.parent.parent / \
                       "protocols" / "degradation" / "crack-001" / "protocol.json"

        if not protocol_path.exists():
            raise FileNotFoundError(f"Protocol definition not found: {protocol_path}")

        cls.definition = ProtocolDefinition(protocol_path)
        cls.protocol = CrackPropagationProtocol(cls.definition)

    def setUp(self):
        """Set up each test."""
        # Create sample metadata
        self.sample = SampleMetadata(
            sample_id="TEST-001",
            manufacturer="Test Corp",
            cell_type="mono-PERC",
            cell_efficiency=22.0,
            cell_area=243.36,
            manufacturing_date="2025-11-14",
            initial_pmax=5.0,
            initial_voc=0.68,
            initial_isc=9.5,
            initial_ff=0.80
        )

        # Test parameters
        self.params = {
            'stress_type': 'thermal_cycling',
            'thermal_cycles': 200,
            'chamber_temp_low': -40.0,
            'chamber_temp_high': 85.0,
            'measurement_interval': 50,
            'dwell_time': 30
        }

    def test_protocol_initialization(self):
        """Test protocol initialization."""
        self.assertEqual(self.protocol.definition.protocol_id, "CRACK-001")
        self.assertEqual(self.protocol.definition.name, "Cell Crack Propagation")
        self.assertEqual(self.protocol.definition.category, "degradation")

    def test_validate_setup_valid(self):
        """Test validation with valid setup."""
        errors = self.protocol.validate_setup([self.sample], self.params)
        self.assertEqual(len(errors), 0, f"Unexpected validation errors: {errors}")

    def test_validate_setup_insufficient_samples(self):
        """Test validation with insufficient samples."""
        errors = self.protocol.validate_setup([], self.params)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('samples required' in e.lower() for e in errors))

    def test_validate_setup_missing_parameters(self):
        """Test validation with missing parameters."""
        incomplete_params = {'stress_type': 'thermal_cycling'}
        errors = self.protocol.validate_setup([self.sample], incomplete_params)
        self.assertGreater(len(errors), 0)

    def test_validate_setup_invalid_parameter_range(self):
        """Test validation with out-of-range parameters."""
        invalid_params = self.params.copy()
        invalid_params['thermal_cycles'] = 2000  # Exceeds max of 1000

        errors = self.protocol.validate_setup([self.sample], invalid_params)
        self.assertGreater(len(errors), 0)

    def test_validate_setup_missing_metadata(self):
        """Test validation with incomplete sample metadata."""
        incomplete_sample = SampleMetadata(
            sample_id="TEST-002",
            manufacturer="",  # Missing required field
            cell_type="mono-PERC",
            cell_efficiency=22.0,
            cell_area=243.36,
            manufacturing_date="2025-11-14",
            initial_pmax=5.0,
            initial_voc=0.68,
            initial_isc=9.5,
            initial_ff=0.80
        )

        errors = self.protocol.validate_setup([incomplete_sample], self.params)
        self.assertGreater(len(errors), 0)

    def test_analyze_measurements(self):
        """Test analysis of measurements."""
        # Create mock measurement data
        measurements = {
            'initial': {
                'iv_curve': {
                    'pmax': 5.0,
                    'voc': 0.68,
                    'isc': 9.5,
                    'ff': 0.80
                }
            },
            'final': {
                'iv_curve': {
                    'pmax': 4.78,
                    'voc': 0.665,
                    'isc': 9.3,
                    'ff': 0.795
                }
            },
            'interim': []
        }

        analysis = self.protocol.analyze(measurements)

        # Check analysis structure
        self.assertIn('power_degradation', analysis)
        self.assertIn('fill_factor', analysis)
        self.assertIn('crack_propagation', analysis)

        # Check power degradation calculation
        self.assertEqual(analysis['power_degradation']['initial_pmax'], 5.0)
        self.assertEqual(analysis['power_degradation']['final_pmax'], 4.78)
        self.assertAlmostEqual(
            analysis['power_degradation']['degradation_percent'],
            4.4,
            places=1
        )

    def test_evaluate_pass_fail_passing(self):
        """Test pass/fail evaluation with passing results."""
        analysis_results = {
            'power_degradation': {
                'initial_pmax': 5.0,
                'final_pmax': 4.78,
                'degradation_percent': 4.4
            },
            'fill_factor': {
                'initial_ff': 0.80,
                'final_ff': 0.795,
                'degradation_percent': 0.6
            },
            'crack_propagation': {
                'crack_growth_percent': 8.2,
                'isolated_cells': 0
            },
            'isolated_cells': 0
        }

        result = self.protocol.evaluate_pass_fail(analysis_results)
        self.assertTrue(result)

    def test_evaluate_pass_fail_power_degradation_failure(self):
        """Test pass/fail evaluation with excessive power degradation."""
        analysis_results = {
            'power_degradation': {
                'degradation_percent': 6.0  # Exceeds 5% limit
            },
            'fill_factor': {
                'degradation_percent': 1.0
            },
            'crack_propagation': {
                'crack_growth_percent': 10.0,
                'isolated_cells': 0
            },
            'isolated_cells': 0
        }

        result = self.protocol.evaluate_pass_fail(analysis_results)
        self.assertFalse(result)

    def test_evaluate_pass_fail_crack_growth_failure(self):
        """Test pass/fail evaluation with excessive crack growth."""
        analysis_results = {
            'power_degradation': {
                'degradation_percent': 3.0
            },
            'fill_factor': {
                'degradation_percent': 1.0
            },
            'crack_propagation': {
                'crack_growth_percent': 25.0,  # Exceeds 20% limit
                'isolated_cells': 0
            },
            'isolated_cells': 0
        }

        result = self.protocol.evaluate_pass_fail(analysis_results)
        self.assertFalse(result)

    def test_evaluate_pass_fail_isolated_cells_failure(self):
        """Test pass/fail evaluation with isolated cells."""
        analysis_results = {
            'power_degradation': {
                'degradation_percent': 3.0
            },
            'fill_factor': {
                'degradation_percent': 1.0
            },
            'crack_propagation': {
                'crack_growth_percent': 10.0,
                'isolated_cells': 1  # Should be 0
            },
            'isolated_cells': 1
        }

        result = self.protocol.evaluate_pass_fail(analysis_results)
        self.assertFalse(result)


class TestProtocolDefinition(unittest.TestCase):
    """Test cases for ProtocolDefinition class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        protocol_path = Path(__file__).parent.parent.parent.parent / \
                       "protocols" / "degradation" / "crack-001" / "protocol.json"

        if not protocol_path.exists():
            raise FileNotFoundError(f"Protocol definition not found: {protocol_path}")

        cls.definition = ProtocolDefinition(protocol_path)

    def test_load_protocol_definition(self):
        """Test loading protocol definition from JSON."""
        self.assertEqual(self.definition.protocol_id, "CRACK-001")
        self.assertEqual(self.definition.version, "1.0.0")
        self.assertEqual(self.definition.category, "degradation")

    def test_get_parameter(self):
        """Test getting parameter default values."""
        thermal_cycles = self.definition.get_parameter('thermal_cycles')
        self.assertEqual(thermal_cycles, 200)

        measurement_interval = self.definition.get_parameter('measurement_interval')
        self.assertEqual(measurement_interval, 50)

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        params = {
            'stress_type': 'thermal_cycling',
            'thermal_cycles': 200,
            'chamber_temp_low': -40.0,
            'chamber_temp_high': 85.0
        }

        errors = self.definition.validate_parameters(params)
        self.assertEqual(len(errors), 0)

    def test_validate_parameters_invalid_enum(self):
        """Test parameter validation with invalid enum value."""
        params = {
            'stress_type': 'invalid_type'
        }

        errors = self.definition.validate_parameters(params)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('stress_type' in e for e in errors))

    def test_validate_parameters_out_of_range(self):
        """Test parameter validation with out-of-range values."""
        params = {
            'thermal_cycles': 5000  # Exceeds max
        }

        errors = self.definition.validate_parameters(params)
        self.assertGreater(len(errors), 0)

    def test_validate_parameters_unknown(self):
        """Test parameter validation with unknown parameters."""
        params = {
            'unknown_parameter': 'value'
        }

        errors = self.definition.validate_parameters(params)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('Unknown parameter' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
