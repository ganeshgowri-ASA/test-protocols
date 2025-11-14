"""
Unit Tests for DIEL-001 Calculations
=====================================

Tests for dielectric withstand test calculations.
"""

import pytest
from src.analysis.calculators import DielectricCalculator


class TestDielectricCalculator:
    """Test suite for DielectricCalculator"""

    def test_calculate_test_voltage(self):
        """Test voltage calculation formula"""
        # Test case 1: 600V system
        result = DielectricCalculator.calculate_test_voltage(600.0)
        assert result == 2200.0  # 1000 + (2 * 600)

        # Test case 2: 1000V system
        result = DielectricCalculator.calculate_test_voltage(1000.0)
        assert result == 3000.0  # 1000 + (2 * 1000)

        # Test case 3: 1500V system
        result = DielectricCalculator.calculate_test_voltage(1500.0)
        assert result == 4000.0  # 1000 + (2 * 1500)

    def test_calculate_insulation_resistance_per_area(self):
        """Test area-normalized resistance calculation"""
        # Test case 1: 60 MΩ resistance, 1.5 m² area
        result = DielectricCalculator.calculate_insulation_resistance_per_area(60.0, 1.5)
        assert result == 40.0

        # Test case 2: 100 MΩ resistance, 2.0 m² area
        result = DielectricCalculator.calculate_insulation_resistance_per_area(100.0, 2.0)
        assert result == 50.0

    def test_calculate_insulation_resistance_per_area_zero_area(self):
        """Test that zero area raises ValueError"""
        with pytest.raises(ValueError, match="Module area must be positive"):
            DielectricCalculator.calculate_insulation_resistance_per_area(60.0, 0.0)

    def test_check_voltage_tolerance(self):
        """Test voltage tolerance checking"""
        # Within tolerance
        within, deviation = DielectricCalculator.check_voltage_tolerance(3000.0, 3040.0)
        assert within is True
        assert deviation == 40.0

        # Outside tolerance
        within, deviation = DielectricCalculator.check_voltage_tolerance(3000.0, 3100.0)
        assert within is False
        assert deviation == 100.0

    def test_check_insulation_resistance_minimum(self):
        """Test insulation resistance minimum check"""
        # Pass case
        passed, value = DielectricCalculator.check_insulation_resistance_minimum(100.0, 2.0)
        assert passed is True
        assert value == 50.0

        # Fail case
        passed, value = DielectricCalculator.check_insulation_resistance_minimum(50.0, 2.0)
        assert passed is False
        assert value == 25.0  # Below 40 MΩ/m²

    def test_check_leakage_current(self):
        """Test leakage current checking"""
        # Within limit
        acceptable, margin = DielectricCalculator.check_leakage_current(30.0)
        assert acceptable is True
        assert margin == 20.0

        # Exceeds limit
        acceptable, margin = DielectricCalculator.check_leakage_current(60.0)
        assert acceptable is False
        assert margin == -10.0

    def test_calculate_voltage_ramp_time(self):
        """Test voltage ramp time calculation"""
        # 3000V at 500 V/s
        ramp_time = DielectricCalculator.calculate_voltage_ramp_time(3000.0, 0.0, 500.0)
        assert ramp_time == 6.0  # 3000 / 500 = 6 seconds

    def test_evaluate_test_result_pass(self, sample_test_data):
        """Test comprehensive evaluation with passing data"""
        result = DielectricCalculator.evaluate_test_result(sample_test_data)

        assert result['overall_pass'] is True
        assert 'initial_insulation_resistance' in result['checks']
        assert 'final_insulation_resistance' in result['checks']
        assert 'leakage_current' in result['checks']
        assert len(result['failures']) == 0

    def test_evaluate_test_result_fail_breakdown(self, sample_test_data):
        """Test evaluation with breakdown failure"""
        sample_test_data['breakdown_occurred'] = True

        result = DielectricCalculator.evaluate_test_result(sample_test_data)

        assert result['overall_pass'] is False
        assert 'Dielectric breakdown occurred during test' in result['failures']

    def test_evaluate_test_result_fail_leakage(self, sample_test_data):
        """Test evaluation with high leakage current"""
        sample_test_data['leakage_current_max'] = 75.0  # Exceeds 50 mA limit

        result = DielectricCalculator.evaluate_test_result(sample_test_data)

        assert result['overall_pass'] is False
        assert 'Leakage current exceeds maximum' in result['failures']

    def test_evaluate_test_result_fail_resistance(self, sample_test_data):
        """Test evaluation with low insulation resistance"""
        sample_test_data['insulation_resistance_initial'] = 40.0  # 40/1.5 = 26.67 MΩ/m² < 40

        result = DielectricCalculator.evaluate_test_result(sample_test_data)

        assert result['overall_pass'] is False
        assert 'Initial insulation resistance below minimum' in result['failures']
