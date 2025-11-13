"""
Data Processing Utilities

Handles data filtering, smoothing, outlier detection, and statistical analysis
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy import stats, signal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processing and analysis utilities"""

    @staticmethod
    def remove_outliers(data: np.ndarray, method: str = 'zscore', threshold: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Remove outliers from data

        Args:
            data: Input data array
            method: 'zscore' or 'iqr'
            threshold: Z-score threshold or IQR multiplier

        Returns:
            Tuple of (cleaned_data, outlier_mask)
        """
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(data, nan_policy='omit'))
            mask = z_scores < threshold
        elif method == 'iqr':
            q1, q3 = np.percentile(data, [25, 75])
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            mask = (data >= lower) & (data <= upper)
        else:
            raise ValueError(f"Unknown method: {method}")

        return data[mask], mask

    @staticmethod
    def smooth_data(data: np.ndarray, window_size: int = 5, method: str = 'moving_average') -> np.ndarray:
        """
        Smooth data using various methods

        Args:
            data: Input data array
            window_size: Window size for smoothing
            method: 'moving_average', 'savgol', or 'exponential'

        Returns:
            Smoothed data array
        """
        if method == 'moving_average':
            return np.convolve(data, np.ones(window_size)/window_size, mode='valid')
        elif method == 'savgol':
            return signal.savgol_filter(data, window_size, 3)
        elif method == 'exponential':
            alpha = 2 / (window_size + 1)
            result = np.zeros_like(data)
            result[0] = data[0]
            for i in range(1, len(data)):
                result[i] = alpha * data[i] + (1 - alpha) * result[i-1]
            return result
        else:
            raise ValueError(f"Unknown method: {method}")

    @staticmethod
    def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
        """Calculate statistical measures for data"""
        return {
            'mean': float(np.mean(data)),
            'median': float(np.median(data)),
            'std': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'q25': float(np.percentile(data, 25)),
            'q75': float(np.percentile(data, 75)),
            'count': len(data)
        }

    @staticmethod
    def check_stability(data: np.ndarray, window_size: int, threshold: float) -> Tuple[bool, float]:
        """
        Check if data is stable (low variation) over a window

        Args:
            data: Input data array
            window_size: Number of last points to check
            threshold: Maximum allowed standard deviation

        Returns:
            Tuple of (is_stable, variation)
        """
        if len(data) < window_size:
            return False, float('inf')

        window_data = data[-window_size:]
        variation = np.std(window_data)
        is_stable = variation <= threshold

        return is_stable, float(variation)

    @staticmethod
    def linear_regression(x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Perform linear regression

        Returns:
            Dict with slope, intercept, r_squared, and other statistics
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_error': float(std_err)
        }

    @staticmethod
    def interpolate_data(x: np.ndarray, y: np.ndarray, x_new: np.ndarray, method: str = 'linear') -> np.ndarray:
        """Interpolate data to new x values"""
        return np.interp(x_new, x, y)

    @staticmethod
    def resample_timeseries(timestamps: List[datetime], values: List[float],
                          interval_seconds: int) -> Tuple[List[datetime], List[float]]:
        """
        Resample time series data to regular intervals

        Args:
            timestamps: List of datetime objects
            values: List of measurement values
            interval_seconds: Target interval in seconds

        Returns:
            Tuple of (resampled_timestamps, resampled_values)
        """
        # Convert to numpy arrays for easier processing
        times_sec = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
        values_arr = np.array(values)

        # Create regular time grid
        start_time = 0
        end_time = times_sec[-1]
        regular_times = np.arange(start_time, end_time, interval_seconds)

        # Interpolate values
        regular_values = np.interp(regular_times, times_sec, values_arr)

        # Convert back to datetime
        regular_timestamps = [timestamps[0] + pd.Timedelta(seconds=t) for t in regular_times]

        return regular_timestamps, regular_values.tolist()

    @staticmethod
    def calculate_uncertainty(measurements: np.ndarray,
                            instrument_uncertainty: float,
                            confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate measurement uncertainty

        Args:
            measurements: Array of repeated measurements
            instrument_uncertainty: Known instrument uncertainty
            confidence_level: Confidence level for interval

        Returns:
            Dict with various uncertainty metrics
        """
        # Type A uncertainty (from repeatability)
        std_dev = np.std(measurements, ddof=1)
        type_a = std_dev / np.sqrt(len(measurements))

        # Type B uncertainty (from instrument)
        type_b = instrument_uncertainty / np.sqrt(3)  # Assuming rectangular distribution

        # Combined uncertainty
        combined = np.sqrt(type_a**2 + type_b**2)

        # Expanded uncertainty (k=2 for ~95% confidence)
        k_factor = stats.t.ppf((1 + confidence_level) / 2, len(measurements) - 1)
        expanded = k_factor * combined

        return {
            'type_a': float(type_a),
            'type_b': float(type_b),
            'combined': float(combined),
            'expanded': float(expanded),
            'k_factor': float(k_factor),
            'confidence_level': confidence_level
        }

    @staticmethod
    def detect_drift(data: np.ndarray, timestamps: np.ndarray) -> Dict[str, Any]:
        """
        Detect if there's a drift/trend in the data

        Returns:
            Dict with drift detection results
        """
        # Perform linear regression to detect trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, data)

        # Check if slope is significantly different from zero
        is_drifting = p_value < 0.05 and abs(r_value) > 0.5

        return {
            'is_drifting': is_drifting,
            'slope': float(slope),
            'p_value': float(p_value),
            'r_value': float(r_value),
            'drift_per_unit_time': float(slope)
        }
