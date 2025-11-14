"""
YELLOW-001 Data Analyzer

Advanced analysis module for EVA yellowing test data.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from scipy import stats
from datetime import datetime
import logging


class YellowingAnalyzer:
    """
    Analyzer for EVA yellowing test data.

    Provides advanced statistical analysis, trend analysis, and
    degradation modeling capabilities.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.logger = logging.getLogger(__name__)

    def analyze_degradation_kinetics(self, time_points: List[Dict[str, Any]],
                                     parameter: str = 'yellow_index') -> Dict[str, Any]:
        """
        Analyze degradation kinetics using exponential fitting.

        Fits data to exponential model: y = A + B*(1 - exp(-t/tau))

        Args:
            time_points: List of measurement data points
            parameter: Parameter to analyze ('yellow_index', 'color_shift', etc.)

        Returns:
            Dictionary with kinetic analysis results
        """
        times = np.array([tp['time_point_hours'] for tp in time_points])
        values = np.array([tp[parameter] for tp in time_points])

        try:
            # Fit exponential model
            from scipy.optimize import curve_fit

            def exp_model(t, A, B, tau):
                return A + B * (1 - np.exp(-t / tau))

            # Initial guess
            p0 = [values[0], values[-1] - values[0], 200]

            params, covariance = curve_fit(exp_model, times, values, p0=p0, maxfev=5000)

            A, B, tau = params
            r_squared = self._calculate_r_squared(values, exp_model(times, A, B, tau))

            # Extrapolate to 2000 hours
            extrapolated_value = exp_model(2000, A, B, tau)

            result = {
                'model': 'exponential',
                'parameters': {
                    'baseline': round(A, 3),
                    'max_change': round(B, 3),
                    'time_constant_hours': round(tau, 1)
                },
                'fit_quality': {
                    'r_squared': round(r_squared, 4),
                    'rmse': round(float(np.sqrt(np.mean((values - exp_model(times, A, B, tau))**2))), 3)
                },
                'extrapolation': {
                    'at_2000h': round(extrapolated_value, 2),
                    'time_to_threshold': self._estimate_time_to_threshold(A, B, tau, parameter)
                }
            }

        except Exception as e:
            self.logger.warning(f"Exponential fit failed: {e}. Using linear approximation.")

            # Fallback to linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(times, values)

            result = {
                'model': 'linear',
                'parameters': {
                    'slope': round(slope, 5),
                    'intercept': round(intercept, 3)
                },
                'fit_quality': {
                    'r_squared': round(r_value**2, 4),
                    'p_value': round(p_value, 6)
                },
                'extrapolation': {
                    'at_2000h': round(slope * 2000 + intercept, 2)
                }
            }

        return result

    def _calculate_r_squared(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R² value."""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)

    def _estimate_time_to_threshold(self, A: float, B: float, tau: float,
                                    parameter: str) -> Optional[int]:
        """
        Estimate time to reach failure threshold.

        Args:
            A, B, tau: Exponential model parameters
            parameter: Parameter name

        Returns:
            Estimated hours to threshold, or None if not applicable
        """
        thresholds = {
            'yellow_index': 15,
            'color_shift': 8,
            'light_transmittance': 75
        }

        if parameter not in thresholds:
            return None

        threshold = thresholds[parameter]

        # Solve: threshold = A + B*(1 - exp(-t/tau)) for t
        # t = -tau * ln(1 - (threshold - A)/B)

        try:
            ratio = (threshold - A) / B

            if ratio >= 1:
                return None  # Already at or past threshold

            if ratio <= 0:
                return None  # Will never reach threshold

            t = -tau * np.log(1 - ratio)

            return int(round(t))

        except Exception:
            return None

    def compare_samples(self, samples_data: List[Dict[str, Any]],
                       parameter: str = 'yellow_index') -> Dict[str, Any]:
        """
        Compare degradation across multiple samples.

        Args:
            samples_data: List of sample data dictionaries
            parameter: Parameter to compare

        Returns:
            Comparison statistics and rankings
        """
        sample_values = {}

        for sample in samples_data:
            sample_id = sample['sample_id']
            final_value = sample['time_points'][-1][parameter]
            sample_values[sample_id] = final_value

        # Calculate statistics
        values = list(sample_values.values())

        comparison = {
            'parameter': parameter,
            'statistics': {
                'mean': round(float(np.mean(values)), 2),
                'median': round(float(np.median(values)), 2),
                'std_dev': round(float(np.std(values)), 2),
                'coefficient_of_variation': round(float(np.std(values) / np.mean(values) * 100), 2),
                'range': round(float(np.max(values) - np.min(values)), 2)
            },
            'rankings': self._rank_samples(sample_values),
            'outliers': self._detect_outliers(sample_values)
        }

        return comparison

    def _rank_samples(self, sample_values: Dict[str, float]) -> List[Dict[str, Any]]:
        """Rank samples by degradation (lower is better for YI and DE)."""
        ranked = sorted(sample_values.items(), key=lambda x: x[1])

        return [
            {
                'rank': i + 1,
                'sample_id': sample_id,
                'value': round(value, 2)
            }
            for i, (sample_id, value) in enumerate(ranked)
        ]

    def _detect_outliers(self, sample_values: Dict[str, float],
                        threshold: float = 2.0) -> List[str]:
        """
        Detect outlier samples using Z-score method.

        Args:
            sample_values: Dictionary of sample IDs to values
            threshold: Z-score threshold (default: 2.0)

        Returns:
            List of sample IDs identified as outliers
        """
        values = np.array(list(sample_values.values()))
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        outliers = []
        for sample_id, value in sample_values.items():
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                outliers.append(sample_id)

        return outliers

    def calculate_stability_index(self, time_points: List[Dict[str, Any]],
                                  parameter: str = 'yellow_index') -> float:
        """
        Calculate stability index based on rate of change.

        Lower values indicate better stability (slower degradation).

        Args:
            time_points: List of measurement data points
            parameter: Parameter to analyze

        Returns:
            Stability index (0-100, lower is better)
        """
        values = np.array([tp[parameter] for tp in time_points])

        # Calculate point-to-point changes
        changes = np.diff(values)

        # Stability index based on mean absolute change rate
        mean_change_rate = np.mean(np.abs(changes))

        # Normalize to 0-100 scale (arbitrary scaling factor)
        stability_index = min(100, mean_change_rate * 10)

        return round(stability_index, 2)

    def generate_color_trajectory(self, time_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate color trajectory analysis in L*a*b* color space.

        Args:
            time_points: List of measurement data points

        Returns:
            Color trajectory analysis
        """
        trajectory = {
            'path_length': 0.0,
            'direction': {},
            'velocity': []
        }

        # Calculate total path length in color space
        for i in range(1, len(time_points)):
            prev = time_points[i - 1]
            curr = time_points[i]

            # Euclidean distance in L*a*b* space
            distance = np.sqrt(
                (curr['L_star'] - prev['L_star'])**2 +
                (curr['a_star'] - prev['a_star'])**2 +
                (curr['b_star'] - prev['b_star'])**2
            )

            trajectory['path_length'] += distance

            # Calculate velocity (distance per 100 hours)
            time_delta = curr['time_point_hours'] - prev['time_point_hours']
            velocity = distance / (time_delta / 100)
            trajectory['velocity'].append(round(velocity, 3))

        # Overall direction in L*a*b* space
        first = time_points[0]
        last = time_points[-1]

        trajectory['direction'] = {
            'delta_L': round(last['L_star'] - first['L_star'], 2),
            'delta_a': round(last['a_star'] - first['a_star'], 2),
            'delta_b': round(last['b_star'] - first['b_star'], 2)
        }

        trajectory['path_length'] = round(trajectory['path_length'], 2)
        trajectory['average_velocity'] = round(float(np.mean(trajectory['velocity'])), 3)

        return trajectory
