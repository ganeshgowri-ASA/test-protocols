"""
Unit Tests for STC-001 Protocol

Comprehensive test suite for the Standard Test Conditions testing protocol.
"""

import unittest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import tempfile
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from genspark_app.protocols.performance.stc_001 import STC001Protocol


class TestSTC001Protocol(unittest.TestCase):
    """Test cases for STC001Protocol class."""

    def setUp(self):
        """Set up test fixtures."""
        self.protocol = STC001Protocol()

        # Create sample I-V data
        self.sample_iv_data = self._create_sample_iv_data()

        # Sample setup data
        self.sample_setup = {
            'serial_number': 'PV-TEST-001234',
            'manufacturer': 'JinkoSolar',
            'model': 'JKM400M-72H',
            'technology': 'Mono c-Si',
            'rated_power': 400.0,
            'rated_voc': 48.5,
            'rated_isc': 10.5,
            'irradiance': 1000,
            'cell_temperature': 25.0,
            'ambient_temperature': 20.0,
            'spectrum': 'AM 1.5G',
            'equipment': {
                'solar_simulator': 'SS-001',
                'iv_tracer': 'IV-001',
                'temperature_sensor': 'TS-001'
            }
        }

    def _create_sample_iv_data(self):
        """Create realistic I-V curve data for testing."""
        # Generate 200 points for a typical PV module
        voltage = np.linspace(0, 48, 200)

        # Realistic I-V curve using simplified model
        voc = 48.0
        isc = 10.0
        rs = 0.3  # Series resistance
        rsh = 500  # Shunt resistance

        # Calculate current using simplified single diode model
        current = []
        for v in voltage:
            # Simplified current calculation
            i = isc * (1 - (v / voc) ** 2) - v / rsh
            i = max(0, i)  # No negative current
            current.append(i)

        current = np.array(current)

        return {
            'voltage': voltage,
            'current': current
        }

    def tearDown(self):
        """Clean up after tests."""
        pass

    # ========================================
    # Initialization Tests
    # ========================================

    def test_initialization(self):
        """Test protocol initialization."""
        self.assertEqual(self.protocol.protocol_id, 'STC-001')
        self.assertEqual(self.protocol.protocol_name, 'Standard Test Conditions (STC) Testing')
        self.assertEqual(self.protocol.version, '2.0')
        self.assertIsNotNone(self.protocol.template)

    def test_template_loading(self):
        """Test that JSON template is loaded correctly."""
        self.assertIn('metadata', self.protocol.template)
        self.assertIn('test_conditions', self.protocol.template)
        self.assertIn('ui_configuration', self.protocol.template)
        self.assertIn('measurements', self.protocol.template)
        self.assertIn('acceptance_criteria', self.protocol.template)

    # ========================================
    # UI Rendering Tests
    # ========================================

    def test_render_ui(self):
        """Test UI configuration rendering."""
        ui_config = self.protocol.render_ui()

        self.assertIsInstance(ui_config, dict)
        self.assertIn('tabs', ui_config.get('ui_configuration', {}))
        self.assertIn('dynamic_data', ui_config)

        # Check tabs
        tabs = ui_config['ui_configuration']['tabs']
        tab_names = [tab['name'] for tab in tabs]
        self.assertIn('Setup', tab_names)
        self.assertIn('Data Acquisition', tab_names)
        self.assertIn('Analysis', tab_names)
        self.assertIn('Validation', tab_names)
        self.assertIn('Report', tab_names)

    # ========================================
    # Setup Validation Tests
    # ========================================

    def test_validate_setup_success(self):
        """Test successful setup validation."""
        is_valid, errors = self.protocol.validate_setup(self.sample_setup)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_setup_missing_required_field(self):
        """Test setup validation with missing required field."""
        invalid_setup = self.sample_setup.copy()
        del invalid_setup['serial_number']

        is_valid, errors = self.protocol.validate_setup(invalid_setup)

        self.assertFalse(is_valid)
        self.assertTrue(any('serial_number' in error for error in errors))

    def test_validate_setup_invalid_serial_number(self):
        """Test setup validation with invalid serial number."""
        invalid_setup = self.sample_setup.copy()
        invalid_setup['serial_number'] = 'SHORT'  # Too short

        is_valid, errors = self.protocol.validate_setup(invalid_setup)

        self.assertFalse(is_valid)
        self.assertTrue(any('serial number' in error.lower() for error in errors))

    def test_validate_setup_invalid_power(self):
        """Test setup validation with invalid rated power."""
        invalid_setup = self.sample_setup.copy()
        invalid_setup['rated_power'] = -100  # Negative power

        is_valid, errors = self.protocol.validate_setup(invalid_setup)

        self.assertFalse(is_valid)
        self.assertTrue(any('power' in error.lower() for error in errors))

    def test_validate_setup_irradiance_warning(self):
        """Test that irradiance deviation generates warning."""
        setup_with_deviation = self.sample_setup.copy()
        setup_with_deviation['irradiance'] = 950  # Deviates from STC

        is_valid, errors = self.protocol.validate_setup(setup_with_deviation)

        self.assertTrue(is_valid)  # Still valid
        self.assertTrue(len(self.protocol.warnings) > 0)  # But has warnings

    def test_validate_setup_temperature_warning(self):
        """Test that temperature deviation generates warning."""
        setup_with_deviation = self.sample_setup.copy()
        setup_with_deviation['cell_temperature'] = 30  # Deviates from STC

        is_valid, errors = self.protocol.validate_setup(setup_with_deviation)

        self.assertTrue(is_valid)  # Still valid
        self.assertTrue(len(self.protocol.warnings) > 0)  # But has warnings

    # ========================================
    # Data Validation Tests
    # ========================================

    def test_validate_iv_data_success(self):
        """Test successful I-V data validation."""
        validation_result = self.protocol._validate_iv_data(self.sample_iv_data)

        self.assertTrue(validation_result['valid'])
        self.assertEqual(len(validation_result['errors']), 0)

    def test_validate_iv_data_insufficient_points(self):
        """Test I-V data validation with too few points."""
        insufficient_data = {
            'voltage': np.linspace(0, 48, 50),  # Only 50 points
            'current': np.linspace(10, 0, 50)
        }

        validation_result = self.protocol._validate_iv_data(insufficient_data)

        self.assertFalse(validation_result['valid'])
        self.assertTrue(any('insufficient' in error.lower() for error in validation_result['errors']))

    def test_validate_iv_data_with_nan(self):
        """Test I-V data validation with NaN values."""
        invalid_data = self.sample_iv_data.copy()
        invalid_data['voltage'][50] = np.nan

        validation_result = self.protocol._validate_iv_data(invalid_data)

        self.assertFalse(validation_result['valid'])
        self.assertTrue(any('nan' in error.lower() for error in validation_result['errors']))

    # ========================================
    # Data Processing Tests
    # ========================================

    def test_process_iv_data(self):
        """Test I-V data processing."""
        processed = self.protocol._process_iv_data(self.sample_iv_data)

        self.assertIn('voltage', processed)
        self.assertIn('current', processed)
        self.assertIn('power', processed)
        self.assertEqual(len(processed['voltage']), len(processed['current']))
        self.assertEqual(len(processed['voltage']), len(processed['power']))

        # Check that power is calculated correctly
        expected_power = processed['voltage'] * processed['current']
        np.testing.assert_array_almost_equal(processed['power'], expected_power)

    # ========================================
    # Parameter Extraction Tests
    # ========================================

    def test_extract_parameters(self):
        """Test key parameter extraction."""
        processed_data = self.protocol._process_iv_data(self.sample_iv_data)
        parameters = self.protocol._extract_parameters(processed_data)

        # Check that all required parameters are present
        required_params = ['voc', 'isc', 'vmp', 'imp', 'pmax', 'fill_factor']
        for param in required_params:
            self.assertIn(param, parameters)
            self.assertIsInstance(parameters[param], float)

        # Check parameter ranges
        self.assertGreater(parameters['voc'], 0)
        self.assertGreater(parameters['isc'], 0)
        self.assertGreater(parameters['pmax'], 0)
        self.assertGreater(parameters['fill_factor'], 0)
        self.assertLess(parameters['fill_factor'], 1)

    def test_find_voc(self):
        """Test Voc extraction."""
        voc = self.protocol._find_voc(
            self.sample_iv_data['voltage'],
            self.sample_iv_data['current']
        )

        # Voc should be close to the maximum voltage
        self.assertGreater(voc, 40)
        self.assertLess(voc, 50)

    def test_find_isc(self):
        """Test Isc extraction."""
        isc = self.protocol._find_isc(
            self.sample_iv_data['voltage'],
            self.sample_iv_data['current']
        )

        # Isc should be close to maximum current
        self.assertGreater(isc, 8)
        self.assertLess(isc, 12)

    def test_find_mpp(self):
        """Test MPP identification."""
        power = self.sample_iv_data['voltage'] * self.sample_iv_data['current']

        mpp = self.protocol._find_mpp(
            self.sample_iv_data['voltage'],
            self.sample_iv_data['current'],
            power
        )

        self.assertIn('index', mpp)
        self.assertIn('voltage', mpp)
        self.assertIn('current', mpp)
        self.assertIn('power', mpp)

        # MPP power should be positive
        self.assertGreater(mpp['power'], 0)

    # ========================================
    # Corrections Tests
    # ========================================

    def test_corrections_needed_false(self):
        """Test that corrections are not needed for STC conditions."""
        self.protocol.test_data['setup'] = self.sample_setup

        self.assertFalse(self.protocol._corrections_needed())

    def test_corrections_needed_true_irradiance(self):
        """Test that corrections are needed for non-STC irradiance."""
        setup = self.sample_setup.copy()
        setup['irradiance'] = 950
        self.protocol.test_data['setup'] = setup

        self.assertTrue(self.protocol._corrections_needed())

    def test_corrections_needed_true_temperature(self):
        """Test that corrections are needed for non-STC temperature."""
        setup = self.sample_setup.copy()
        setup['cell_temperature'] = 30
        self.protocol.test_data['setup'] = setup

        self.assertTrue(self.protocol._corrections_needed())

    def test_apply_corrections_temperature(self):
        """Test temperature corrections."""
        setup = self.sample_setup.copy()
        setup['cell_temperature'] = 30  # 5°C above STC
        setup['temp_coeff_isc'] = 0.05  # %/°C
        setup['temp_coeff_voc'] = -0.3  # %/°C
        setup['temp_coeff_pmax'] = -0.4  # %/°C
        self.protocol.test_data['setup'] = setup

        original_params = {
            'voc': 48.0,
            'isc': 10.0,
            'pmax': 400.0
        }

        corrected_params = self.protocol._apply_corrections(original_params)

        # With positive temperature, Isc should increase slightly
        self.assertNotEqual(corrected_params['isc'], original_params['isc'])

        # With positive temperature, Voc should decrease
        self.assertLess(corrected_params['voc'], original_params['voc'])

        # With positive temperature, Pmax should decrease
        self.assertLess(corrected_params['pmax'], original_params['pmax'])

    def test_apply_corrections_irradiance(self):
        """Test irradiance corrections."""
        setup = self.sample_setup.copy()
        setup['irradiance'] = 900  # Below STC
        self.protocol.test_data['setup'] = setup

        original_params = {
            'isc': 9.0,  # Lower due to lower irradiance
            'pmax': 360.0  # Lower due to lower irradiance
        }

        corrected_params = self.protocol._apply_corrections(original_params)

        # Corrected values should be higher (corrected to STC)
        self.assertGreater(corrected_params['isc'], original_params['isc'])
        self.assertGreater(corrected_params['pmax'], original_params['pmax'])

    # ========================================
    # Validation Tests
    # ========================================

    def test_validate_power_tolerance_pass(self):
        """Test power tolerance validation - passing case."""
        self.protocol.test_data['setup'] = self.sample_setup

        results = {'pmax': 398.0}  # Within 3% of 400W

        validation = self.protocol._validate_power_tolerance(results)

        self.assertTrue(validation['pass'])

    def test_validate_power_tolerance_fail(self):
        """Test power tolerance validation - failing case."""
        self.protocol.test_data['setup'] = self.sample_setup

        results = {'pmax': 380.0}  # More than 3% below 400W

        validation = self.protocol._validate_power_tolerance(results)

        self.assertFalse(validation['pass'])

    def test_validate_fill_factor_pass(self):
        """Test fill factor validation - passing case."""
        results = {'fill_factor': 0.78}

        validation = self.protocol._validate_fill_factor(results)

        self.assertTrue(validation['pass'])

    def test_validate_fill_factor_fail(self):
        """Test fill factor validation - failing case."""
        results = {'fill_factor': 0.65}  # Below 0.70 minimum

        validation = self.protocol._validate_fill_factor(results)

        self.assertFalse(validation['pass'])

    def test_validate_results_overall_pass(self):
        """Test overall results validation - passing case."""
        self.protocol.test_data['setup'] = self.sample_setup

        results = {
            'pmax': 398.0,
            'voc': 48.2,
            'isc': 10.3,
            'fill_factor': 0.78
        }

        validation = self.protocol.validate_results(results)

        self.assertEqual(validation['overall_status'], 'PASS')
        self.assertEqual(len(validation['failed_criteria']), 0)

    def test_validate_results_overall_fail(self):
        """Test overall results validation - failing case."""
        self.protocol.test_data['setup'] = self.sample_setup

        results = {
            'pmax': 350.0,  # Too low
            'voc': 48.2,
            'isc': 10.3,
            'fill_factor': 0.65  # Too low
        }

        validation = self.protocol.validate_results(results)

        self.assertEqual(validation['overall_status'], 'FAIL')
        self.assertGreater(len(validation['failed_criteria']), 0)
        self.assertIn('recommendations', validation)

    # ========================================
    # Uncertainty Calculation Tests
    # ========================================

    def test_calculate_uncertainty(self):
        """Test uncertainty calculation."""
        results = {
            'voc': 48.0,
            'isc': 10.0,
            'vmp': 40.0,
            'imp': 9.5,
            'pmax': 380.0,
            'fill_factor': 0.78
        }

        uncertainty = self.protocol.calculate_uncertainty(results)

        self.assertIn('components', uncertainty)
        self.assertIn('method', uncertainty)
        self.assertIn('confidence_level', uncertainty)

        # Check that uncertainty is calculated for all parameters
        for param in ['voc', 'isc', 'vmp', 'imp', 'pmax', 'fill_factor']:
            self.assertIn(param, uncertainty['components'])

            component = uncertainty['components'][param]
            self.assertIn('combined_standard_uncertainty', component)
            self.assertIn('expanded_uncertainty', component)
            self.assertIn('relative_uncertainty_percent', component)

    # ========================================
    # File I/O Tests
    # ========================================

    def test_load_iv_data_from_csv(self):
        """Test loading I-V data from CSV file."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('Voltage,Current\n')
            for v, i in zip(self.sample_iv_data['voltage'][:100],
                          self.sample_iv_data['current'][:100]):
                f.write(f'{v},{i}\n')
            temp_file = f.name

        try:
            loaded_data = self.protocol._load_iv_data_from_file(
                temp_file,
                voltage_col='Voltage',
                current_col='Current'
            )

            self.assertIn('voltage', loaded_data)
            self.assertIn('current', loaded_data)
            self.assertEqual(len(loaded_data['voltage']), 100)

        finally:
            Path(temp_file).unlink()

    # ========================================
    # Execute Test Integration Tests
    # ========================================

    def test_execute_test_integration(self):
        """Test complete test execution flow."""
        # Setup
        self.protocol.validate_setup(self.sample_setup)

        # Create temporary data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('Voltage,Current\n')
            for v, i in zip(self.sample_iv_data['voltage'],
                          self.sample_iv_data['current']):
                f.write(f'{v},{i}\n')
            temp_file = f.name

        try:
            # Execute test
            test_params = {
                'data_source': 'file',
                'file_path': temp_file,
                'voltage_column': 'Voltage',
                'current_column': 'Current'
            }

            result = self.protocol.execute_test(test_params)

            self.assertEqual(result['status'], 'success')
            self.assertIn('parameters', result)
            self.assertIn('pmax', result['parameters'])

        finally:
            Path(temp_file).unlink()

    # ========================================
    # Report Generation Tests
    # ========================================

    def test_generate_json_report(self):
        """Test JSON report generation."""
        # Setup test data
        self.protocol.test_data['setup'] = self.sample_setup
        self.protocol.parameters = {
            'voc': 48.0,
            'isc': 10.0,
            'pmax': 395.0,
            'fill_factor': 0.78
        }

        report_bytes = self.protocol.generate_report(format='json')

        self.assertIsInstance(report_bytes, bytes)

        # Parse JSON
        report_data = json.loads(report_bytes.decode('utf-8'))

        self.assertIn('protocol_id', report_data)
        self.assertIn('parameters', report_data)

    # ========================================
    # Audit Trail Tests
    # ========================================

    def test_audit_trail_logging(self):
        """Test audit trail logging."""
        initial_count = len(self.protocol.audit_trail)

        self.protocol.log_action('test_action', {'test': 'data'}, user_id='user123')

        self.assertEqual(len(self.protocol.audit_trail), initial_count + 1)

        latest_entry = self.protocol.audit_trail[-1]
        self.assertEqual(latest_entry['action'], 'test_action')
        self.assertEqual(latest_entry['user_id'], 'user123')
        self.assertIn('timestamp', latest_entry)
        self.assertIn('data_hash', latest_entry)

    def test_get_audit_trail(self):
        """Test retrieving audit trail."""
        self.protocol.log_action('action1', {'data': 1})
        self.protocol.log_action('action2', {'data': 2})

        audit_trail = self.protocol.get_audit_trail()

        self.assertIsInstance(audit_trail, list)
        self.assertGreaterEqual(len(audit_trail), 2)

    # ========================================
    # State Management Tests
    # ========================================

    def test_save_and_load_state(self):
        """Test saving and loading protocol state."""
        # Set up some state
        self.protocol.test_data['setup'] = self.sample_setup
        self.protocol.parameters = {'pmax': 400.0, 'voc': 48.0}
        self.protocol.log_action('test', {})

        # Save state
        state = self.protocol.save_state()

        # Create new protocol and load state
        new_protocol = STC001Protocol()
        new_protocol.load_state(state)

        # Verify state was loaded
        self.assertEqual(new_protocol.test_data, self.protocol.test_data)
        self.assertEqual(new_protocol.parameters, self.protocol.parameters)
        self.assertEqual(len(new_protocol.audit_trail), len(self.protocol.audit_trail))


class TestSTC001ProtocolEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.protocol = STC001Protocol()

    def test_empty_data(self):
        """Test handling of empty data."""
        empty_data = {'voltage': np.array([]), 'current': np.array([])}

        validation_result = self.protocol._validate_iv_data(empty_data)

        self.assertFalse(validation_result['valid'])

    def test_extreme_values(self):
        """Test handling of extreme values."""
        extreme_data = {
            'voltage': np.array([0, 1e6]),  # Extremely high voltage
            'current': np.array([1e6, 0])   # Extremely high current
        }

        # Should handle without crashing
        validation_result = self.protocol._validate_iv_data(extreme_data)

        # Will fail validation but shouldn't crash
        self.assertFalse(validation_result['valid'])

    def test_division_by_zero(self):
        """Test handling of division by zero in calculations."""
        # Test fill factor calculation with zero Voc or Isc
        parameters = {'pmax': 100, 'voc': 0, 'isc': 10}

        processed_data = {
            'voltage': np.array([0, 1, 2]),
            'current': np.array([0, 0, 0]),
            'power': np.array([0, 0, 0])
        }

        # Should handle gracefully
        try:
            result = self.protocol._extract_parameters(processed_data)
            # Fill factor should be 0 or handle division by zero
            self.assertTrue(result['fill_factor'] >= 0)
        except Exception as e:
            self.fail(f"Division by zero not handled: {e}")


if __name__ == '__main__':
    unittest.main()
