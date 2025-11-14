"""Tests for analysis modules."""

import pytest
import numpy as np

from src.analysis.statistical import (
    calculate_degradation,
    calculate_statistics,
    calculate_confidence_interval,
    calculate_power_parameters_summary,
    calculate_psd_metrics
)


def test_calculate_degradation():
    """Test degradation calculation."""
    # 10% degradation
    deg = calculate_degradation(100.0, 90.0, percentage=True)
    assert deg == pytest.approx(10.0)

    # No degradation
    deg = calculate_degradation(100.0, 100.0, percentage=True)
    assert deg == pytest.approx(0.0)

    # Improvement (negative degradation)
    deg = calculate_degradation(100.0, 110.0, percentage=True)
    assert deg == pytest.approx(-10.0)


def test_calculate_statistics():
    """Test statistics calculation."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]

    stats = calculate_statistics(values)

    assert stats['mean'] == pytest.approx(30.0)
    assert stats['median'] == pytest.approx(30.0)
    assert stats['min'] == pytest.approx(10.0)
    assert stats['max'] == pytest.approx(50.0)
    assert stats['range'] == pytest.approx(40.0)
    assert stats['count'] == 5


def test_calculate_statistics_empty():
    """Test statistics with empty list."""
    stats = calculate_statistics([])
    assert stats == {}


def test_calculate_confidence_interval():
    """Test confidence interval calculation."""
    values = [10.0, 12.0, 11.0, 13.0, 12.5]

    lower, upper = calculate_confidence_interval(values, confidence=0.95)

    assert lower < upper
    assert lower < np.mean(values) < upper


def test_calculate_power_parameters_summary():
    """Test power parameters summary."""
    electrical_data = {
        'Pmax': 300.0,
        'Voc': 45.0,
        'Isc': 9.0,
        'Vmp': 38.0,
        'Imp': 7.89
    }

    summary = calculate_power_parameters_summary(electrical_data)

    assert 'Pmax' in summary
    assert 'Voc' in summary
    assert 'FF' in summary  # Should be calculated

    # Check calculated fill factor
    expected_ff = (300.0 / (45.0 * 9.0)) * 100
    assert summary['FF'] == pytest.approx(expected_ff, rel=0.01)


def test_calculate_power_parameters_with_efficiency():
    """Test power parameters with efficiency calculation."""
    electrical_data = {
        'Pmax': 300.0,
        'area_m2': 1.6,
        'irradiance_wm2': 1000.0
    }

    summary = calculate_power_parameters_summary(electrical_data)

    assert 'efficiency' in summary
    expected_efficiency = (300.0 / (1.6 * 1000.0)) * 100
    assert summary['efficiency'] == pytest.approx(expected_efficiency, rel=0.01)


def test_calculate_psd_metrics():
    """Test PSD metrics calculation."""
    # Simple test case
    frequencies = [5, 10, 20, 50, 100, 200]
    psd_values = [0.001, 0.005, 0.01, 0.015, 0.01, 0.005]

    metrics = calculate_psd_metrics(frequencies, psd_values)

    assert 'grms' in metrics
    assert 'peak_frequency_hz' in metrics
    assert 'peak_psd_value' in metrics

    # Peak should be at 50 Hz
    assert metrics['peak_frequency_hz'] == 50.0
    assert metrics['peak_psd_value'] == 0.015


def test_calculate_psd_metrics_empty():
    """Test PSD metrics with empty data."""
    metrics = calculate_psd_metrics([], [])
    assert metrics == {}


def test_calculate_psd_metrics_mismatched():
    """Test PSD metrics with mismatched arrays."""
    frequencies = [5, 10, 20]
    psd_values = [0.001, 0.005]  # Different length

    metrics = calculate_psd_metrics(frequencies, psd_values)
    assert metrics == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
