"""
Data Analysis Module
Statistical analysis and trend detection for test data
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime
import statistics


class DataAnalyzer:
    """Analyze test data for trends, anomalies, and statistics"""

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical summary

        Args:
            values: List of numerical values

        Returns:
            Dictionary with statistical measures
        """
        if not values:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'std_dev': 0,
                'min': 0,
                'max': 0,
                'range': 0
            }

        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }

    @staticmethod
    def detect_outliers(
        values: List[float],
        threshold: float = 3.0
    ) -> List[Tuple[int, float]]:
        """
        Detect outliers using z-score method

        Args:
            values: List of numerical values
            threshold: Z-score threshold (default 3.0)

        Returns:
            List of (index, value) tuples for outliers
        """
        if len(values) < 3:
            return []

        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)

        if std_dev == 0:
            return []

        outliers = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / std_dev)
            if z_score > threshold:
                outliers.append((i, value))

        return outliers

    @staticmethod
    def calculate_trend(
        values: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """
        Calculate trend using linear regression

        Args:
            values: List of numerical values
            timestamps: List of timestamps

        Returns:
            Trend analysis results
        """
        if len(values) < 2:
            return {
                'slope': 0,
                'intercept': 0,
                'r_squared': 0,
                'trend': 'insufficient_data'
            }

        # Convert timestamps to hours since start
        start_time = timestamps[0]
        x = np.array([
            (ts - start_time).total_seconds() / 3600
            for ts in timestamps
        ])
        y = np.array(values)

        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)

        # R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Determine trend direction
        if abs(slope) < 0.01:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'

        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_squared),
            'trend': trend
        }

    @staticmethod
    def analyze_chamber_uniformity(
        measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze environmental chamber uniformity

        Args:
            measurements: List of environmental measurements

        Returns:
            Uniformity analysis
        """
        # Group by timestamp
        by_timestamp: Dict[datetime, List[float]] = {}

        for m in measurements:
            ts = m['timestamp']
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)

            if ts not in by_timestamp:
                by_timestamp[ts] = []

            by_timestamp[ts].append(m['temperature'])

        # Calculate uniformity for each timestamp
        uniformity_results = []

        for ts, temps in by_timestamp.items():
            if len(temps) > 1:
                uniformity_results.append({
                    'timestamp': ts,
                    'mean': statistics.mean(temps),
                    'std_dev': statistics.stdev(temps),
                    'range': max(temps) - min(temps),
                    'sensor_count': len(temps)
                })

        if not uniformity_results:
            return {
                'average_std_dev': 0,
                'average_range': 0,
                'max_std_dev': 0,
                'max_range': 0,
                'uniformity_grade': 'N/A'
            }

        avg_std_dev = statistics.mean([r['std_dev'] for r in uniformity_results])
        avg_range = statistics.mean([r['range'] for r in uniformity_results])
        max_std_dev = max([r['std_dev'] for r in uniformity_results])
        max_range = max([r['range'] for r in uniformity_results])

        # Grade uniformity
        if max_range <= 1.0:
            grade = 'Excellent'
        elif max_range <= 2.0:
            grade = 'Good'
        elif max_range <= 3.0:
            grade = 'Acceptable'
        else:
            grade = 'Poor'

        return {
            'average_std_dev': round(avg_std_dev, 2),
            'average_range': round(avg_range, 2),
            'max_std_dev': round(max_std_dev, 2),
            'max_range': round(max_range, 2),
            'uniformity_grade': grade,
            'detail': uniformity_results
        }

    @staticmethod
    def calculate_degradation_rate(
        measurements: List[Dict[str, Any]],
        parameter: str = 'pmax'
    ) -> Dict[str, Any]:
        """
        Calculate degradation rate over time

        Args:
            measurements: List of electrical measurements
            parameter: Parameter to analyze (default 'pmax')

        Returns:
            Degradation analysis
        """
        if len(measurements) < 2:
            return {
                'initial_value': 0,
                'final_value': 0,
                'total_degradation': 0,
                'degradation_rate_per_hour': 0
            }

        # Sort by timestamp
        sorted_measurements = sorted(
            measurements,
            key=lambda x: x['timestamp'] if isinstance(x['timestamp'], datetime)
            else datetime.fromisoformat(x['timestamp'])
        )

        initial = sorted_measurements[0]
        final = sorted_measurements[-1]

        initial_value = initial.get(parameter, 0)
        final_value = final.get(parameter, 0)

        if initial_value == 0:
            return {
                'initial_value': initial_value,
                'final_value': final_value,
                'total_degradation': 0,
                'degradation_rate_per_hour': 0
            }

        total_degradation = ((initial_value - final_value) / initial_value) * 100

        # Calculate time duration
        initial_time = initial['timestamp']
        final_time = final['timestamp']

        if isinstance(initial_time, str):
            initial_time = datetime.fromisoformat(initial_time)
        if isinstance(final_time, str):
            final_time = datetime.fromisoformat(final_time)

        duration_hours = (final_time - initial_time).total_seconds() / 3600

        degradation_rate = total_degradation / duration_hours if duration_hours > 0 else 0

        return {
            'initial_value': round(initial_value, 2),
            'final_value': round(final_value, 2),
            'total_degradation': round(total_degradation, 2),
            'degradation_rate_per_hour': round(degradation_rate, 6),
            'test_duration_hours': round(duration_hours, 2)
        }

    @staticmethod
    def detect_anomalies(
        measurements: List[Dict[str, Any]],
        parameter: str,
        window_size: int = 10,
        threshold: float = 2.5
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using rolling statistics

        Args:
            measurements: List of measurements
            parameter: Parameter to analyze
            window_size: Rolling window size
            threshold: Standard deviation threshold

        Returns:
            List of detected anomalies
        """
        if len(measurements) < window_size:
            return []

        values = [m.get(parameter, 0) for m in measurements]
        anomalies = []

        for i in range(window_size, len(values)):
            window = values[i - window_size:i]
            current = values[i]

            mean = statistics.mean(window)
            std_dev = statistics.stdev(window) if len(window) > 1 else 0

            if std_dev > 0:
                z_score = abs((current - mean) / std_dev)

                if z_score > threshold:
                    anomalies.append({
                        'index': i,
                        'timestamp': measurements[i]['timestamp'],
                        'value': current,
                        'expected_mean': round(mean, 2),
                        'z_score': round(z_score, 2),
                        'deviation': round(current - mean, 2)
                    })

        return anomalies
