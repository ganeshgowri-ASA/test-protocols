"""Quality control checker for test data validation."""

from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime, timedelta


class QCChecker:
    """Quality control checker for test execution data."""

    def __init__(self, protocol_definition: Dict[str, Any]):
        """Initialize QC checker with protocol definition.

        Args:
            protocol_definition: Protocol definition dictionary
        """
        self.protocol_def = protocol_definition
        self.qc_rules = protocol_definition.get('qc_rules', {})

    def check_measurement_repeatability(
        self,
        measurements: List[float],
        parameter_name: str
    ) -> Dict[str, Any]:
        """Check measurement repeatability using coefficient of variation.

        Args:
            measurements: List of repeated measurements
            parameter_name: Name of the parameter being measured

        Returns:
            Dictionary with QC check results
        """
        rule = self.qc_rules.get('measurement_repeatability', {})
        max_cv = rule.get('max_cv', 0.02)

        if len(measurements) < 2:
            return {
                'pass': True,
                'message': 'Insufficient data for repeatability check',
                'cv': None
            }

        measurements_array = np.array(measurements)
        mean = np.mean(measurements_array)
        std = np.std(measurements_array, ddof=1)

        if mean == 0:
            cv = 0
        else:
            cv = std / mean

        passes = cv <= max_cv

        return {
            'pass': passes,
            'cv': float(cv),
            'max_cv': max_cv,
            'mean': float(mean),
            'std': float(std),
            'n_measurements': len(measurements),
            'message': f"CV = {cv:.4f} ({'pass' if passes else 'FAIL'} - limit: {max_cv})"
        }

    def check_temperature_stability(
        self,
        temperature_readings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check chamber temperature stability.

        Args:
            temperature_readings: List of dictionaries with 'timestamp' and 'temperature'

        Returns:
            Dictionary with QC check results
        """
        rule = self.qc_rules.get('temperature_stability', {})
        max_deviation = rule.get('max_deviation', 2.0)

        if not temperature_readings:
            return {
                'pass': False,
                'message': 'No temperature readings available'
            }

        temps = [r['temperature'] for r in temperature_readings]
        temps_array = np.array(temps)

        mean_temp = np.mean(temps_array)
        max_temp = np.max(temps_array)
        min_temp = np.min(temps_array)
        max_dev = max(abs(max_temp - mean_temp), abs(mean_temp - min_temp))

        passes = max_dev <= max_deviation

        return {
            'pass': passes,
            'mean_temperature': float(mean_temp),
            'min_temperature': float(min_temp),
            'max_temperature': float(max_temp),
            'max_deviation': float(max_dev),
            'limit': max_deviation,
            'message': f"Temperature deviation: ±{max_dev:.2f}°C ({'pass' if passes else 'FAIL'} - limit: ±{max_deviation}°C)"
        }

    def check_irradiance_stability(
        self,
        irradiance_readings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check UV irradiance stability.

        Args:
            irradiance_readings: List of dictionaries with 'timestamp' and 'irradiance'

        Returns:
            Dictionary with QC check results
        """
        rule = self.qc_rules.get('irradiance_stability', {})
        max_deviation = rule.get('max_deviation', 0.1)

        if not irradiance_readings:
            return {
                'pass': False,
                'message': 'No irradiance readings available'
            }

        irradiances = [r['irradiance'] for r in irradiance_readings]
        irradiance_array = np.array(irradiances)

        mean_irr = np.mean(irradiance_array)
        max_irr = np.max(irradiance_array)
        min_irr = np.min(irradiance_array)
        max_dev = max(abs(max_irr - mean_irr), abs(mean_irr - min_irr))

        passes = max_dev <= max_deviation

        return {
            'pass': passes,
            'mean_irradiance': float(mean_irr),
            'min_irradiance': float(min_irr),
            'max_irradiance': float(max_irr),
            'max_deviation': float(max_dev),
            'limit': max_deviation,
            'message': f"Irradiance deviation: ±{max_dev:.3f} W/m² ({'pass' if passes else 'FAIL'} - limit: ±{max_deviation} W/m²)"
        }

    def check_data_completeness(
        self,
        expected_measurements: int,
        actual_measurements: int
    ) -> Dict[str, Any]:
        """Check data completeness.

        Args:
            expected_measurements: Number of expected measurements
            actual_measurements: Number of actual measurements recorded

        Returns:
            Dictionary with QC check results
        """
        rule = self.qc_rules.get('data_completeness', {})
        min_completeness = rule.get('min_completeness', 0.95)

        if expected_measurements == 0:
            return {
                'pass': True,
                'completeness': 1.0,
                'message': 'No measurements expected'
            }

        completeness = actual_measurements / expected_measurements
        passes = completeness >= min_completeness

        return {
            'pass': passes,
            'completeness': float(completeness),
            'expected_measurements': expected_measurements,
            'actual_measurements': actual_measurements,
            'min_completeness': min_completeness,
            'message': f"Data completeness: {completeness:.1%} ({'pass' if passes else 'FAIL'} - requirement: {min_completeness:.1%})"
        }

    def check_outliers(
        self,
        values: List[float],
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """Check for outliers in measurement data.

        Args:
            values: List of measurement values
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection

        Returns:
            Dictionary with outlier analysis results
        """
        if len(values) < 4:
            return {
                'outliers_detected': False,
                'outlier_indices': [],
                'message': 'Insufficient data for outlier detection'
            }

        values_array = np.array(values)

        if method == 'iqr':
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            outlier_mask = (values_array < lower_bound) | (values_array > upper_bound)
            outlier_indices = np.where(outlier_mask)[0].tolist()

        else:  # zscore method
            mean = np.mean(values_array)
            std = np.std(values_array)

            if std == 0:
                outlier_indices = []
            else:
                z_scores = np.abs((values_array - mean) / std)
                outlier_mask = z_scores > threshold
                outlier_indices = np.where(outlier_mask)[0].tolist()

        outliers_detected = len(outlier_indices) > 0

        return {
            'outliers_detected': outliers_detected,
            'outlier_indices': outlier_indices,
            'n_outliers': len(outlier_indices),
            'method': method,
            'threshold': threshold,
            'message': f"{'Outliers detected' if outliers_detected else 'No outliers'} ({method} method)"
        }

    def run_all_checks(
        self,
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run all QC checks on test data.

        Args:
            test_data: Complete test data dictionary

        Returns:
            Dictionary with all QC check results
        """
        qc_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'overall_pass': True,
            'warnings': [],
            'failures': []
        }

        # Check measurement repeatability for key parameters
        for param in ['pmax', 'voc', 'isc']:
            if param in test_data.get('measurements', {}):
                measurements = test_data['measurements'][param]
                result = self.check_measurement_repeatability(measurements, param)
                qc_results['checks'][f'{param}_repeatability'] = result

                if not result['pass']:
                    qc_results['overall_pass'] = False
                    qc_results['failures'].append(f"{param} repeatability failed")

        # Check temperature stability
        if 'temperature_readings' in test_data:
            result = self.check_temperature_stability(test_data['temperature_readings'])
            qc_results['checks']['temperature_stability'] = result

            if not result['pass']:
                qc_results['warnings'].append("Temperature stability issue")

        # Check irradiance stability
        if 'irradiance_readings' in test_data:
            result = self.check_irradiance_stability(test_data['irradiance_readings'])
            qc_results['checks']['irradiance_stability'] = result

            if not result['pass']:
                qc_results['warnings'].append("Irradiance stability issue")

        # Check data completeness
        if 'expected_measurements' in test_data and 'actual_measurements' in test_data:
            result = self.check_data_completeness(
                test_data['expected_measurements'],
                test_data['actual_measurements']
            )
            qc_results['checks']['data_completeness'] = result

            if not result['pass']:
                qc_results['overall_pass'] = False
                qc_results['failures'].append("Data completeness check failed")

        return qc_results
