"""
Unit Tests for Temperature Coefficient Analyzer

Tests the analyzer module for correct calculation of temperature coefficients
according to IEC 60891:2021.

Author: ASA PV Testing
Date: 2025-11-14
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.analyzer import (
    TemperatureCoefficientAnalyzer,
    TemperatureCoefficients
)


@pytest.fixture
def sample_data():
    """Sample measurement data for testing"""
    return pd.DataFrame({
        'module_temperature': [20.0, 30.0, 40.0, 50.0, 60.0, 70.0],
        'pmax': [260.0, 252.0, 244.0, 236.0, 228.0, 220.0],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'irradiance': [1000, 1000, 1000, 1000, 1000, 1000]
    })


@pytest.fixture
def sample_data_with_irradiance_variation():
    """Sample data with irradiance variation"""
    return pd.DataFrame({
        'module_temperature': [20.0, 30.0, 40.0, 50.0, 60.0, 70.0],
        'pmax': [260.0, 252.0, 244.0, 236.0, 228.0, 220.0],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'irradiance': [1000, 1005, 998, 1002, 997, 1001]
    })


@pytest.fixture
def analyzer():
    """Create analyzer instance"""
    return TemperatureCoefficientAnalyzer()


class TestDataLoading:
    """Test data loading functionality"""

    def test_load_dataframe(self, analyzer, sample_data):
        """Test loading data from DataFrame"""
        result = analyzer.load_data(sample_data)
        assert result is not None
        assert len(result) == 6
        assert 'module_temperature' in result.columns

    def test_load_dict(self, analyzer, sample_data):
        """Test loading data from dictionary"""
        data_dict = sample_data.to_dict(orient='list')
        result = analyzer.load_data(data_dict)
        assert result is not None
        assert len(result) == 6

    def test_missing_columns_error(self, analyzer):
        """Test error when required columns are missing"""
        incomplete_data = pd.DataFrame({
            'module_temperature': [20, 30, 40]
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer.load_data(incomplete_data)


class TestTemperatureCoefficientCalculation:
    """Test temperature coefficient calculations"""

    def test_basic_calculation(self, analyzer, sample_data):
        """Test basic coefficient calculation"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        assert results is not None
        assert isinstance(results, TemperatureCoefficients)

        # Check that all required fields are present
        assert hasattr(results, 'alpha_pmp_relative')
        assert hasattr(results, 'beta_voc_relative')
        assert hasattr(results, 'alpha_isc_relative')

    def test_power_coefficient_calculation(self, analyzer, sample_data):
        """Test power temperature coefficient calculation"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # Expected power coefficient should be negative (decreases with temperature)
        assert results.alpha_pmp_relative < 0
        # Typical range for silicon: -0.65 to -0.25 %/°C
        assert -0.70 <= results.alpha_pmp_relative <= -0.20

        # R² should be very high for linear data
        assert results.r_squared_pmp > 0.99

    def test_voltage_coefficient_calculation(self, analyzer, sample_data):
        """Test voltage temperature coefficient calculation"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # Voltage coefficient should be negative
        assert results.beta_voc_relative < 0
        # Typical range for silicon: -0.50 to -0.20 %/°C
        assert -0.55 <= results.beta_voc_relative <= -0.15

        # R² should be very high
        assert results.r_squared_voc > 0.99

    def test_current_coefficient_calculation(self, analyzer, sample_data):
        """Test current temperature coefficient calculation"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # Current coefficient should be positive (increases with temperature)
        assert results.alpha_isc_relative > 0
        # Typical range for silicon: 0.00 to 0.10 %/°C
        assert 0.00 <= results.alpha_isc_relative <= 0.15

        # R² should be very high
        assert results.r_squared_isc > 0.99

    def test_stc_values(self, analyzer, sample_data):
        """Test STC-corrected values are calculated"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # STC values should be reasonable
        assert results.pmp_at_stc > 0
        assert results.voc_at_stc > 0
        assert results.isc_at_stc > 0

        # STC power should be near middle of measured range for linear data
        min_pmax = sample_data['pmax'].min()
        max_pmax = sample_data['pmax'].max()
        assert min_pmax <= results.pmp_at_stc <= max_pmax


class TestLinearRegression:
    """Test linear regression functionality"""

    def test_perfect_linear_data(self, analyzer):
        """Test regression with perfect linear relationship"""
        x = np.array([0, 1, 2, 3, 4, 5])
        y = 2 * x + 5  # Perfect linear: y = 2x + 5

        slope, intercept, r_squared, _, _ = analyzer.calculate_linear_regression(x, y)

        assert np.isclose(slope, 2.0, atol=1e-10)
        assert np.isclose(intercept, 5.0, atol=1e-10)
        assert np.isclose(r_squared, 1.0, atol=1e-10)

    def test_regression_with_noise(self, analyzer):
        """Test regression with noisy data"""
        x = np.array([20, 30, 40, 50, 60, 70])
        y = -0.8 * x + 260 + np.random.normal(0, 0.5, 6)  # Linear with small noise

        slope, intercept, r_squared, _, _ = analyzer.calculate_linear_regression(x, y)

        # Slope should be close to -0.8
        assert -1.0 < slope < -0.6
        # R² should still be high
        assert r_squared > 0.90

    def test_regression_with_nan_values(self, analyzer):
        """Test regression handles NaN values"""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([2, 4, np.nan, 8, 10])

        slope, intercept, r_squared, _, _ = analyzer.calculate_linear_regression(x, y)

        # Should work with NaN values removed
        assert slope > 0
        assert r_squared > 0.9


class TestIrradianceNormalization:
    """Test irradiance normalization"""

    def test_normalization_to_1000(self, analyzer, sample_data_with_irradiance_variation):
        """Test normalization to 1000 W/m²"""
        analyzer.load_data(sample_data_with_irradiance_variation)
        normalized = analyzer.normalize_to_irradiance(1000.0)

        assert 'isc_normalized' in normalized.columns
        assert 'pmax_normalized' in normalized.columns

        # Normalized values should be close to original when irradiance is close to 1000
        assert np.allclose(
            normalized['isc_normalized'],
            sample_data_with_irradiance_variation['isc'],
            rtol=0.01  # 1% tolerance
        )

    def test_normalization_with_constant_irradiance(self, analyzer, sample_data):
        """Test normalization when irradiance is already constant"""
        analyzer.load_data(sample_data)
        normalized = analyzer.normalize_to_irradiance(1000.0)

        # Should create normalized columns even if irradiance is constant
        assert 'isc_normalized' in normalized.columns
        assert 'pmax_normalized' in normalized.columns


class TestSTCCorrection:
    """Test STC correction functionality"""

    def test_correct_single_measurement(self, analyzer, sample_data):
        """Test correcting a single measurement to STC"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # Correct a measurement at 50°C to STC (25°C)
        corrected = analyzer.correct_to_stc(
            temperature=50.0,
            pmax=236.0,
            voc=36.4,
            isc=9.35,
            irradiance=1000.0
        )

        assert 'pmax_stc' in corrected
        assert 'voc_stc' in corrected
        assert 'isc_stc' in corrected

        # Corrected values should be reasonable
        assert corrected['pmax_stc'] > 0
        assert corrected['voc_stc'] > 0
        assert corrected['isc_stc'] > 0

    def test_no_correction_at_stc(self, analyzer, sample_data):
        """Test that values at STC don't change much"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        # Measure already at STC
        corrected = analyzer.correct_to_stc(
            temperature=25.0,
            pmax=244.0,
            voc=37.1,
            isc=9.30,
            irradiance=1000.0
        )

        # Values should be very close to input (small differences due to coefficients)
        assert np.isclose(corrected['pmax_stc'], 244.0, rtol=0.01)
        assert np.isclose(corrected['voc_stc'], 37.1, rtol=0.01)
        assert np.isclose(corrected['isc_stc'], 9.30, rtol=0.01)


class TestResidualCalculation:
    """Test residual calculation"""

    def test_residuals_calculation(self, analyzer, sample_data):
        """Test that residuals are calculated correctly"""
        analyzer.load_data(sample_data)
        analyzer.calculate_temperature_coefficients()

        residuals = analyzer.calculate_residuals()

        assert 'pmax_residual' in residuals.columns
        assert 'voc_residual' in residuals.columns
        assert 'isc_residual' in residuals.columns

        # For perfect linear data, residuals should be near zero
        assert residuals['pmax_residual'].abs().mean() < 1.0


class TestResultsExport:
    """Test results export functionality"""

    def test_to_dict(self, analyzer, sample_data):
        """Test converting results to dictionary"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        result_dict = results.to_dict()

        assert isinstance(result_dict, dict)
        assert 'alpha_pmp_relative' in result_dict
        assert 'beta_voc_relative' in result_dict
        assert 'alpha_isc_relative' in result_dict

    def test_to_json(self, analyzer, sample_data):
        """Test converting results to JSON"""
        analyzer.load_data(sample_data)
        results = analyzer.calculate_temperature_coefficients()

        json_str = results.to_json()

        assert isinstance(json_str, str)
        assert 'alpha_pmp_relative' in json_str

    def test_export_json(self, analyzer, sample_data, tmp_path):
        """Test exporting results to JSON file"""
        analyzer.load_data(sample_data)
        analyzer.calculate_temperature_coefficients()

        output_file = tmp_path / "results.json"
        analyzer.export_results(output_file, format='json')

        assert output_file.exists()

    def test_export_csv(self, analyzer, sample_data, tmp_path):
        """Test exporting results to CSV file"""
        analyzer.load_data(sample_data)
        analyzer.calculate_temperature_coefficients()

        output_file = tmp_path / "results.csv"
        analyzer.export_results(output_file, format='csv')

        assert output_file.exists()


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_insufficient_data_points(self, analyzer):
        """Test error with insufficient data points"""
        minimal_data = pd.DataFrame({
            'module_temperature': [20],
            'pmax': [260],
            'voc': [38.5],
            'isc': [9.20]
        })

        analyzer.load_data(minimal_data)

        with pytest.raises(ValueError):
            analyzer.calculate_linear_regression(
                np.array([20]),
                np.array([260])
            )

    def test_export_before_analysis(self, analyzer, tmp_path):
        """Test error when exporting before running analysis"""
        output_file = tmp_path / "results.json"

        with pytest.raises(ValueError, match="No results to export"):
            analyzer.export_results(output_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
