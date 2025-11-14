"""Test data analyzer for protocol execution analysis."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from protocols.base import Protocol


class TestAnalyzer:
    """Analyzes test execution data and evaluates results."""

    def __init__(self, protocol: Protocol):
        """Initialize analyzer with protocol definition.

        Args:
            protocol: Protocol instance defining the test
        """
        self.protocol = protocol

    def calculate_retention(
        self,
        initial_value: float,
        final_value: float
    ) -> float:
        """Calculate percentage retention.

        Args:
            initial_value: Initial measurement value
            final_value: Final measurement value

        Returns:
            Retention percentage (0-100)
        """
        if initial_value == 0:
            return 0.0
        return (final_value / initial_value) * 100

    def calculate_degradation_rate(
        self,
        measurements: List[Dict[str, Any]],
        parameter: str
    ) -> Optional[float]:
        """Calculate degradation rate from time-series measurements.

        Args:
            measurements: List of measurement dictionaries with 'timestamp' and parameter
            parameter: Name of the parameter to analyze

        Returns:
            Degradation rate (% per hour) or None if insufficient data
        """
        if len(measurements) < 2:
            return None

        # Sort by timestamp
        sorted_meas = sorted(measurements, key=lambda m: m['timestamp'])

        # Extract values and timestamps
        values = []
        times = []
        first_time = sorted_meas[0]['timestamp']

        for m in sorted_meas:
            if parameter in m:
                values.append(m[parameter])
                # Calculate hours since first measurement
                time_diff = (m['timestamp'] - first_time).total_seconds() / 3600
                times.append(time_diff)

        if len(values) < 2:
            return None

        # Linear regression to find degradation rate
        coefficients = np.polyfit(times, values, 1)
        slope = coefficients[0]

        # Convert to percentage per hour
        initial_value = values[0]
        if initial_value == 0:
            return 0.0

        degradation_rate_pct = (slope / initial_value) * 100

        return degradation_rate_pct

    def analyze_measurement_series(
        self,
        measurements: List[Dict[str, float]],
        parameter: str
    ) -> Dict[str, Any]:
        """Analyze a series of measurements for a parameter.

        Args:
            measurements: List of measurement dictionaries
            parameter: Parameter name to analyze

        Returns:
            Dictionary with statistical analysis
        """
        values = [m[parameter] for m in measurements if parameter in m]

        if not values:
            return {
                'count': 0,
                'mean': None,
                'std': None,
                'min': None,
                'max': None,
                'cv': None
            }

        values_array = np.array(values)

        analysis = {
            'count': len(values),
            'mean': float(np.mean(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'median': float(np.median(values_array))
        }

        # Coefficient of variation
        if analysis['mean'] != 0:
            analysis['cv'] = analysis['std'] / analysis['mean']
        else:
            analysis['cv'] = None

        return analysis

    def evaluate_test_results(
        self,
        measurements_by_point: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Evaluate complete test results against protocol criteria.

        Args:
            measurements_by_point: Dictionary mapping measurement point IDs to
                                  dictionaries of parameter measurements

        Returns:
            Complete evaluation results
        """
        # Get initial and final measurements
        initial_measurements = measurements_by_point.get('initial', {})
        final_measurements = measurements_by_point.get('final', {})

        if not initial_measurements or not final_measurements:
            return {
                'success': False,
                'error': 'Missing initial or final measurements'
            }

        # Evaluate pass/fail criteria
        pass_fail_results = self.protocol.evaluate_pass_fail(
            initial_measurements,
            final_measurements
        )

        # Calculate summary statistics for all parameters
        summary_stats = {}
        for param in initial_measurements.keys():
            if param in final_measurements:
                initial = initial_measurements[param]
                final = final_measurements[param]
                change = final - initial
                retention = self.calculate_retention(initial, final)

                summary_stats[param] = {
                    'initial': initial,
                    'final': final,
                    'change': change,
                    'change_pct': ((final - initial) / initial * 100) if initial != 0 else 0,
                    'retention_pct': retention
                }

        # Compile complete results
        results = {
            'success': True,
            'pass_fail': pass_fail_results,
            'summary_stats': summary_stats,
            'evaluation_timestamp': datetime.utcnow().isoformat()
        }

        return results

    def generate_degradation_trends(
        self,
        all_measurements: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate degradation trend data for charting.

        Args:
            all_measurements: All measurements from all measurement points

        Returns:
            Dictionary mapping parameters to trend data points
        """
        trends = {}

        # Group measurements by parameter
        params_by_time = {}

        for measurement in all_measurements:
            timestamp = measurement.get('timestamp')
            if not timestamp:
                continue

            for param, value in measurement.items():
                if param == 'timestamp':
                    continue

                if param not in params_by_time:
                    params_by_time[param] = []

                params_by_time[param].append({
                    'timestamp': timestamp,
                    'value': value
                })

        # Sort each parameter's measurements by time
        for param, data_points in params_by_time.items():
            sorted_points = sorted(data_points, key=lambda x: x['timestamp'])

            # Calculate retention percentages if we have initial value
            if sorted_points:
                initial_value = sorted_points[0]['value']

                trends[param] = [
                    {
                        'timestamp': dp['timestamp'].isoformat(),
                        'value': dp['value'],
                        'retention_pct': (dp['value'] / initial_value * 100) if initial_value != 0 else 100
                    }
                    for dp in sorted_points
                ]

        return trends
