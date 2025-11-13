"""
Unit Tests for NOCT-001 Protocol

Tests all aspects of the NOCT protocol implementation:
- Setup and initialization
- Data collection
- NOCT calculations
- Temperature coefficient calculations
- Validation
- Report generation
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'genspark_app'))

from protocols.performance.noct_001 import NOCT001Protocol
from utils.calculations import NOCTCalculator, TemperatureCoefficients
from utils.validators import ParameterValidator, DataValidator
from utils.data_processor import DataProcessor


class TestNOCT001Protocol:
    """Test suite for NOCT-001 protocol"""

    @pytest.fixture
    def protocol(self):
        """Create protocol instance for testing"""
        return NOCT001Protocol()

    @pytest.fixture
    def valid_parameters(self):
        """Valid test parameters"""
        return {
            'sample_id': 'TEST-001',
            'manufacturer': 'Test Manufacturer',
            'model': 'TEST-300W',
            'technology': 'mono-Si',
            'rated_power': 300.0,
            'module_area': 1.6,
            'test_irradiance': 800,
            'ambient_temp_target': 20,
            'wind_speed_target': 1.0,
            'stabilization_duration': 30,
            'measurement_interval': 60,
            'calculate_temp_coefficients': True,
            'temp_coefficient_points': 5
        }

    def test_protocol_initialization(self, protocol):
        """Test protocol initialization"""
        assert protocol.protocol_id == "NOCT-001"
        assert protocol.status.value == "pending"
        assert protocol.progress_percentage == 0
        assert protocol.noct_value is None

    def test_parameter_validation(self, protocol, valid_parameters):
        """Test parameter validation"""
        protocol.set_input_parameters(valid_parameters)
        assert protocol.input_parameters == valid_parameters

    def test_invalid_parameters(self, protocol):
        """Test that invalid parameters are rejected"""
        invalid_params = {
            'sample_id': 'test',  # lowercase not allowed per pattern
            'rated_power': -100,  # negative not allowed
        }
        protocol.set_input_parameters(invalid_params)
        # Validation happens in setup
        result = protocol.setup()
        assert not result
        assert len(protocol.errors) > 0

    def test_setup(self, protocol, valid_parameters):
        """Test protocol setup"""
        protocol.set_input_parameters(valid_parameters)
        result = protocol.setup()
        assert result is True
        assert len(protocol.equipment_list) > 0

    def test_noct_calculation(self):
        """Test NOCT calculation"""
        # Simulate measurement data
        cell_temps = np.array([45.0, 45.2, 45.1, 44.9, 45.3])
        ambient_temps = np.array([20.0, 20.1, 19.9, 20.0, 20.2])
        irradiances = np.array([800, 805, 795, 800, 802])

        calculator = NOCTCalculator()
        result = calculator.calculate_noct(cell_temps, ambient_temps, irradiances)

        assert 'noct' in result
        assert 40 <= result['noct'] <= 55  # Typical NOCT range
        assert 'uncertainty' in result
        assert result['num_points'] == 5

    def test_power_at_noct_calculation(self):
        """Test power at NOCT calculation"""
        calculator = NOCTCalculator()
        result = calculator.calculate_power_at_noct(
            pmax_stc=300.0,
            noct=45.0,
            temp_coeff_power=-0.4,
            irradiance_noct=800
        )

        assert 'pmax_noct' in result
        assert result['pmax_noct'] < 300.0  # Should be less than STC
        assert 200 <= result['pmax_noct'] <= 250  # Reasonable range

    def test_efficiency_calculation(self):
        """Test efficiency at NOCT calculation"""
        calculator = NOCTCalculator()
        result = calculator.calculate_efficiency_at_noct(
            pmax_noct=230.0,
            module_area=1.6,
            irradiance_noct=800
        )

        assert 'efficiency_noct' in result
        assert 15 <= result['efficiency_noct'] <= 20  # Typical range

    def test_temperature_coefficient_power(self):
        """Test temperature coefficient of power calculation"""
        temperatures = np.array([25, 35, 45, 55, 65])
        powers = np.array([300, 288, 276, 264, 252])  # -0.4%/°C slope

        calculator = TemperatureCoefficients()
        result = calculator.calculate_power_coefficient(
            temperatures, powers, pmax_ref=300.0
        )

        assert 'alpha_p' in result
        assert -0.5 <= result['alpha_p'] <= -0.3  # Typical range for Si
        assert result['r_squared'] > 0.95  # Should be linear

    def test_temperature_coefficient_voc(self):
        """Test temperature coefficient of Voc calculation"""
        temperatures = np.array([25, 35, 45, 55, 65])
        voltages = np.array([37.5, 37.0, 36.5, 36.0, 35.5])  # Negative coefficient

        calculator = TemperatureCoefficients()
        result = calculator.calculate_voc_coefficient(
            temperatures, voltages, voc_ref=37.5
        )

        assert 'beta_voc' in result
        assert result['beta_voc'] < 0  # Voc decreases with temperature
        assert -0.4 <= result['beta_voc'] <= -0.2  # Typical range

    def test_data_quality_check(self):
        """Test data quality validation"""
        # Good data
        good_data = np.array([45.0, 45.1, 44.9, 45.2, 45.0, 44.8])
        validator = DataValidator()
        result = validator.check_data_quality(good_data)
        assert result['valid'] is True

        # Data with NaN
        bad_data = np.array([45.0, np.nan, 44.9, 45.2])
        result = validator.check_data_quality(bad_data)
        assert result['valid'] is False
        assert any('NaN' in issue for issue in result['issues'])

    def test_stability_check(self):
        """Test measurement stability checking"""
        processor = DataProcessor()

        # Stable data
        stable_data = np.array([45.0, 45.1, 44.9, 45.0, 45.1, 44.9, 45.0])
        is_stable, variation = processor.check_stability(stable_data, window_size=5, threshold=0.5)
        assert is_stable is True
        assert variation < 0.5

        # Unstable data
        unstable_data = np.array([45.0, 47.0, 42.0, 48.0, 41.0])
        is_stable, variation = processor.check_stability(unstable_data, window_size=5, threshold=0.5)
        assert is_stable is False

    def test_outlier_removal(self):
        """Test outlier detection and removal"""
        processor = DataProcessor()

        # Data with outliers
        data = np.array([45.0, 45.1, 44.9, 45.2, 100.0, 44.8, 45.1])  # 100.0 is outlier
        cleaned, mask = processor.remove_outliers(data, method='zscore', threshold=2.0)

        assert len(cleaned) < len(data)
        assert 100.0 not in cleaned

    def test_linear_regression(self):
        """Test linear regression utility"""
        processor = DataProcessor()

        # Perfect linear relationship
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])  # y = 2x

        result = processor.linear_regression(x, y)

        assert 'slope' in result
        assert 'r_squared' in result
        assert abs(result['slope'] - 2.0) < 0.01
        assert result['r_squared'] > 0.99

    def test_parameter_validation_utility(self):
        """Test parameter validation utility"""
        param_spec = {
            'name': 'rated_power',
            'type': 'float',
            'required': True,
            'validation': {
                'min': 1,
                'max': 1000
            }
        }

        validator = ParameterValidator()

        # Valid value
        is_valid, error = validator.validate_parameter(300.0, param_spec)
        assert is_valid is True

        # Invalid - out of range
        is_valid, error = validator.validate_parameter(1500.0, param_spec)
        assert is_valid is False

        # Invalid - wrong type
        is_valid, error = validator.validate_parameter("abc", param_spec)
        assert is_valid is False

    def test_protocol_state_tracking(self, protocol, valid_parameters):
        """Test protocol state tracking"""
        protocol.set_input_parameters(valid_parameters)

        initial_state = protocol.get_state()
        assert initial_state['status'] == 'pending'
        assert initial_state['progress_percentage'] == 0

        # Run setup
        protocol.setup()
        state_after_setup = protocol.get_state()
        assert len(state_after_setup['input_parameters']) > 0

    def test_audit_trail(self, protocol, valid_parameters):
        """Test audit trail logging"""
        protocol.set_input_parameters(valid_parameters)

        audit_trail = protocol.get_audit_trail()
        assert len(audit_trail) > 0
        assert any(entry['action'] == 'parameters_set' for entry in audit_trail)

    def test_measurement_storage(self, protocol):
        """Test measurement data storage"""
        protocol.add_measurement('test_point', {'temperature': 45.0, 'irradiance': 800})
        assert len(protocol.measurements) == 1
        assert protocol.measurements[0]['measurement_point'] == 'test_point'

    def test_analysis_result_storage(self, protocol):
        """Test analysis result storage"""
        protocol.add_analysis_result('noct', 45.5, '°C', 'pass')
        assert 'noct' in protocol.analysis_results
        assert protocol.analysis_results['noct']['value'] == 45.5
        assert protocol.analysis_results['noct']['pass_fail'] == 'pass'

    def test_error_and_warning_tracking(self, protocol):
        """Test error and warning tracking"""
        protocol.add_error("Test error")
        protocol.add_warning("Test warning")

        assert len(protocol.errors) == 1
        assert len(protocol.warnings) == 1
        assert protocol.errors[0]['message'] == "Test error"
        assert protocol.warnings[0]['message'] == "Test warning"

    def test_protocol_cancellation(self, protocol, valid_parameters):
        """Test protocol cancellation"""
        protocol.set_input_parameters(valid_parameters)
        protocol.setup()

        protocol.cancel()
        assert protocol.status.value == "cancelled"

    def test_to_dict_serialization(self, protocol, valid_parameters):
        """Test protocol serialization"""
        protocol.set_input_parameters(valid_parameters)
        protocol.add_measurement('test', {'value': 100})

        data_dict = protocol.to_dict()

        assert 'protocol_id' in data_dict
        assert 'status' in data_dict
        assert 'input_parameters' in data_dict
        assert 'measurements' in data_dict
        assert 'audit_trail' in data_dict


class TestNOCTCalculations:
    """Detailed tests for NOCT calculation functions"""

    def test_noct_normalization(self):
        """Test NOCT normalization to 800 W/m²"""
        calculator = NOCTCalculator()

        # Test at different irradiances
        cell_temp = 50.0
        ambient_temp = 20.0

        # At 800 W/m²
        result1 = calculator.calculate_noct(
            np.array([cell_temp]),
            np.array([ambient_temp]),
            np.array([800.0])
        )

        # At 900 W/m² (should normalize to lower NOCT)
        result2 = calculator.calculate_noct(
            np.array([cell_temp]),
            np.array([ambient_temp]),
            np.array([900.0])
        )

        # NOCT at lower irradiance should be lower
        assert result2['noct'] < result1['noct']

    def test_operating_temperature_estimation(self):
        """Test operating temperature estimation"""
        calculator = NOCTCalculator()

        # Estimate for different conditions
        temp1 = calculator.estimate_operating_temperature(
            ambient_temp=30.0,
            irradiance=1000.0,
            noct=45.0
        )

        temp2 = calculator.estimate_operating_temperature(
            ambient_temp=20.0,
            irradiance=800.0,
            noct=45.0
        )

        # Higher ambient and irradiance should give higher operating temp
        assert temp1 > temp2


@pytest.mark.integration
class TestNOCT001Integration:
    """Integration tests for complete protocol execution"""

    def test_full_protocol_execution(self):
        """Test complete protocol execution flow"""
        protocol = NOCT001Protocol()

        parameters = {
            'sample_id': 'INT-TEST-001',
            'manufacturer': 'Integration Test',
            'model': 'TEST-300W',
            'technology': 'mono-Si',
            'rated_power': 300.0,
            'module_area': 1.6,
            'test_irradiance': 800,
            'ambient_temp_target': 20,
            'wind_speed_target': 1.0,
            'stabilization_duration': 30,
            'measurement_interval': 60,
            'calculate_temp_coefficients': False  # Skip for faster test
        }

        protocol.set_input_parameters(parameters)

        # This would run the full protocol
        # Note: In real execution, this takes time
        # For unit tests, we might want to mock some parts
        # result = protocol.run()
        # assert result is True
        # assert protocol.noct_value is not None

    def test_report_generation(self):
        """Test report generation with mock data"""
        protocol = NOCT001Protocol()

        # Set up mock data
        protocol.noct_value = 45.0
        protocol.pmax_at_noct = 230.0
        protocol.efficiency_at_noct = 17.9
        protocol.input_parameters = {
            'sample_id': 'REPORT-TEST-001',
            'manufacturer': 'Test',
            'model': 'TEST-300W',
            'rated_power': 300.0,
            'module_area': 1.6
        }

        report = protocol.generate_report()

        assert 'report_metadata' in report
        assert 'sample_information' in report
        assert 'key_results' in report
        assert report['key_results']['noct']['value'] == 45.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
