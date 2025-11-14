"""Tests for calculation functions."""

import pytest
import numpy as np
from analysis.calculations import (
    calculate_fill_factor,
    calculate_efficiency,
    normalize_to_stc,
    calculate_degradation_rate,
    detect_outliers
)


class TestCalculations:
    """Test suite for calculation functions."""

    def test_calculate_fill_factor(self):
        """Test fill factor calculation."""
        voc = 40.5
        isc = 9.2
        pmax = 300.0

        ff = calculate_fill_factor(voc, isc, pmax)

        expected_ff = pmax / (voc * isc)
        assert ff == pytest.approx(expected_ff, abs=0.0001)

    def test_calculate_fill_factor_zero_values(self):
        """Test fill factor with zero values."""
        ff = calculate_fill_factor(0, 9.2, 300.0)
        assert ff == 0.0

        ff = calculate_fill_factor(40.5, 0, 300.0)
        assert ff == 0.0

    def test_calculate_efficiency(self):
        """Test efficiency calculation."""
        pmax = 300.0
        area = 1.6  # m²
        irradiance = 1000.0  # W/m²

        efficiency = calculate_efficiency(pmax, area, irradiance)

        expected_eff = 100 * pmax / (irradiance * area)
        assert efficiency == pytest.approx(expected_eff, abs=0.01)

    def test_normalize_to_stc(self):
        """Test power normalization to STC."""
        pmax = 290.0
        irradiance = 1000.0
        temperature = 25.0

        pmax_stc = normalize_to_stc(pmax, irradiance, temperature)

        # At STC conditions, should return same value
        assert pmax_stc == pytest.approx(pmax, abs=0.1)

    def test_normalize_to_stc_high_temp(self):
        """Test normalization at high temperature."""
        pmax = 290.0
        irradiance = 1000.0
        temperature = 45.0  # 20°C above STC
        temp_coeff = -0.4  # %/°C

        pmax_stc = normalize_to_stc(pmax, irradiance, temperature, temp_coeff)

        # Should be higher than measured (positive correction)
        assert pmax_stc > pmax

    def test_calculate_degradation_rate_linear(self):
        """Test linear degradation rate calculation."""
        time_hours = np.array([0, 24, 48, 72, 96])
        degradation_percent = np.array([0.0, 0.5, 1.0, 1.5, 2.0])

        rate, r_squared = calculate_degradation_rate(
            time_hours,
            degradation_percent,
            method="linear"
        )

        # Should have positive rate
        assert rate > 0

        # Should have good fit (high R²)
        assert r_squared > 0.95

    def test_calculate_degradation_rate_insufficient_data(self):
        """Test degradation rate with insufficient data."""
        time_hours = np.array([0])
        degradation_percent = np.array([0.0])

        rate, r_squared = calculate_degradation_rate(
            time_hours,
            degradation_percent
        )

        assert rate == 0.0
        assert r_squared == 0.0

    def test_detect_outliers_iqr(self):
        """Test outlier detection with IQR method."""
        data = np.array([1.0, 1.1, 1.2, 1.1, 1.0, 5.0, 1.1, 1.2])

        outliers = detect_outliers(data, method="iqr", threshold=1.5)

        assert isinstance(outliers, np.ndarray)
        assert outliers.dtype == bool
        assert outliers[5] is True  # 5.0 should be an outlier

    def test_detect_outliers_zscore(self):
        """Test outlier detection with z-score method."""
        data = np.array([1.0, 1.1, 1.2, 1.1, 1.0, 10.0, 1.1, 1.2])

        outliers = detect_outliers(data, method="zscore", threshold=3.0)

        assert isinstance(outliers, np.ndarray)
        # 10.0 should be an outlier with z-score method
        assert np.any(outliers)

    def test_detect_outliers_mad(self):
        """Test outlier detection with MAD method."""
        data = np.array([1.0, 1.1, 1.2, 1.1, 1.0, 10.0, 1.1, 1.2])

        outliers = detect_outliers(data, method="mad", threshold=3.5)

        assert isinstance(outliers, np.ndarray)
        assert np.any(outliers)

    def test_detect_outliers_empty(self):
        """Test outlier detection with empty data."""
        data = np.array([])

        outliers = detect_outliers(data)

        assert len(outliers) == 0
