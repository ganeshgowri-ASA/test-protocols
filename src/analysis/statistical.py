"""Statistical analysis functions for test data."""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats


def calculate_degradation(
    pre_value: float,
    post_value: float,
    percentage: bool = True
) -> float:
    """Calculate degradation between pre and post values.

    Args:
        pre_value: Pre-test value
        post_value: Post-test value
        percentage: Return as percentage if True

    Returns:
        Degradation value (positive means degradation, negative means improvement)
    """
    if pre_value == 0:
        return 0.0

    degradation = (pre_value - post_value) / pre_value

    if percentage:
        return degradation * 100

    return degradation


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with statistical measures
    """
    if not values:
        return {}

    values_array = np.array(values)

    return {
        'mean': float(np.mean(values_array)),
        'median': float(np.median(values_array)),
        'std': float(np.std(values_array, ddof=1)) if len(values) > 1 else 0.0,
        'min': float(np.min(values_array)),
        'max': float(np.max(values_array)),
        'range': float(np.ptp(values_array)),
        'count': len(values),
        'cv': float(np.std(values_array, ddof=1) / np.mean(values_array) * 100)
            if len(values) > 1 and np.mean(values_array) != 0 else 0.0
    }


def calculate_confidence_interval(
    values: List[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """Calculate confidence interval for values.

    Args:
        values: List of numeric values
        confidence: Confidence level (default 0.95 for 95%)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(values) < 2:
        return (0.0, 0.0)

    values_array = np.array(values)
    mean = np.mean(values_array)
    se = stats.sem(values_array)
    interval = se * stats.t.ppf((1 + confidence) / 2, len(values) - 1)

    return (mean - interval, mean + interval)


def perform_t_test(
    group1: List[float],
    group2: List[float],
    paired: bool = False
) -> Dict[str, Any]:
    """Perform t-test between two groups.

    Args:
        group1: First group of values
        group2: Second group of values
        paired: Whether to perform paired t-test

    Returns:
        Dictionary with t-test results
    """
    if len(group1) < 2 or len(group2) < 2:
        return {
            'statistic': None,
            'p_value': None,
            'significant': None,
            'error': 'Insufficient data points'
        }

    try:
        if paired:
            if len(group1) != len(group2):
                return {
                    'statistic': None,
                    'p_value': None,
                    'significant': None,
                    'error': 'Paired test requires equal sample sizes'
                }
            statistic, p_value = stats.ttest_rel(group1, group2)
        else:
            statistic, p_value = stats.ttest_ind(group1, group2)

        return {
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'test_type': 'paired' if paired else 'independent'
        }

    except Exception as e:
        return {
            'statistic': None,
            'p_value': None,
            'significant': None,
            'error': str(e)
        }


def calculate_power_parameters_summary(
    electrical_data: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate summary of power parameters.

    Args:
        electrical_data: Dictionary with electrical parameters
                        (Pmax, Voc, Isc, Vmp, Imp, FF)

    Returns:
        Dictionary with calculated parameters
    """
    summary = {}

    # Basic parameters
    for param in ['Pmax', 'Voc', 'Isc', 'Vmp', 'Imp', 'FF']:
        if param in electrical_data:
            summary[param] = electrical_data[param]

    # Calculate fill factor if not provided
    if 'FF' not in summary and all(k in electrical_data for k in ['Pmax', 'Voc', 'Isc']):
        voc = electrical_data['Voc']
        isc = electrical_data['Isc']
        pmax = electrical_data['Pmax']

        if voc > 0 and isc > 0:
            summary['FF'] = (pmax / (voc * isc)) * 100

    # Calculate efficiency if area is provided
    if 'area_m2' in electrical_data and 'Pmax' in electrical_data:
        irradiance = electrical_data.get('irradiance_wm2', 1000)  # Default STC
        area = electrical_data['area_m2']

        if area > 0 and irradiance > 0:
            summary['efficiency'] = (electrical_data['Pmax'] / (area * irradiance)) * 100

    return summary


def analyze_time_series(
    timestamps: List[float],
    values: List[float]
) -> Dict[str, Any]:
    """Analyze time series data.

    Args:
        timestamps: List of timestamps (seconds)
        values: List of values

    Returns:
        Dictionary with time series analysis
    """
    if len(timestamps) != len(values) or len(timestamps) < 2:
        return {}

    df = pd.DataFrame({
        'timestamp': timestamps,
        'value': values
    })

    df['time_delta'] = df['timestamp'].diff()

    analysis = {
        'duration': float(timestamps[-1] - timestamps[0]),
        'sample_count': len(values),
        'mean': float(np.mean(values)),
        'std': float(np.std(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'range': float(np.ptp(values)),
        'avg_sampling_rate': float(1.0 / df['time_delta'].mean()) if df['time_delta'].mean() > 0 else 0.0
    }

    # Detect peaks
    values_array = np.array(values)
    peaks_high = []
    peaks_low = []

    for i in range(1, len(values_array) - 1):
        if values_array[i] > values_array[i-1] and values_array[i] > values_array[i+1]:
            peaks_high.append(i)
        elif values_array[i] < values_array[i-1] and values_array[i] < values_array[i+1]:
            peaks_low.append(i)

    analysis['peak_count_high'] = len(peaks_high)
    analysis['peak_count_low'] = len(peaks_low)

    return analysis


def calculate_uncertainty(
    value: float,
    instrument_uncertainty: float,
    resolution: Optional[float] = None,
    confidence: float = 0.95
) -> Dict[str, float]:
    """Calculate measurement uncertainty.

    Args:
        value: Measured value
        instrument_uncertainty: Instrument uncertainty (%)
        resolution: Instrument resolution
        confidence: Confidence level

    Returns:
        Dictionary with uncertainty analysis
    """
    # Type A uncertainty (statistical)
    type_a_uncertainty = 0.0  # Would be calculated from repeated measurements

    # Type B uncertainty (systematic)
    # Instrument uncertainty
    u_instrument = (value * instrument_uncertainty / 100) / np.sqrt(3)

    # Resolution uncertainty
    u_resolution = 0.0
    if resolution:
        u_resolution = resolution / (2 * np.sqrt(3))

    # Combined uncertainty
    u_combined = np.sqrt(u_instrument**2 + u_resolution**2 + type_a_uncertainty**2)

    # Coverage factor for confidence level
    k = stats.t.ppf((1 + confidence) / 2, 10)  # Assuming 10 degrees of freedom

    # Expanded uncertainty
    u_expanded = k * u_combined

    return {
        'value': float(value),
        'u_instrument': float(u_instrument),
        'u_resolution': float(u_resolution),
        'u_combined': float(u_combined),
        'u_expanded': float(u_expanded),
        'relative_uncertainty_percent': float(u_expanded / value * 100) if value != 0 else 0.0,
        'confidence_level': confidence
    }


def calculate_psd_metrics(
    frequencies: List[float],
    psd_values: List[float]
) -> Dict[str, float]:
    """Calculate Power Spectral Density metrics.

    Args:
        frequencies: Frequency values (Hz)
        psd_values: PSD values (g²/Hz)

    Returns:
        Dictionary with PSD metrics
    """
    if len(frequencies) != len(psd_values) or len(frequencies) < 2:
        return {}

    freq_array = np.array(frequencies)
    psd_array = np.array(psd_values)

    # Calculate RMS acceleration from PSD
    # Integrate PSD over frequency range
    df = np.diff(freq_array)
    avg_psd = (psd_array[:-1] + psd_array[1:]) / 2
    grms_squared = np.sum(avg_psd * df)
    grms = np.sqrt(grms_squared)

    # Find peak frequency
    peak_idx = np.argmax(psd_array)
    peak_frequency = freq_array[peak_idx]
    peak_psd = psd_array[peak_idx]

    return {
        'grms': float(grms),
        'peak_frequency_hz': float(peak_frequency),
        'peak_psd_value': float(peak_psd),
        'frequency_range': (float(freq_array[0]), float(freq_array[-1])),
        'mean_psd': float(np.mean(psd_array)),
        'total_energy': float(grms_squared)
    }
