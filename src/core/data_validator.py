"""
Data Validator Module

Provides quality control and data validation functionality.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime


class DataValidator:
    """Validates test data against protocol QC criteria."""

    def __init__(self, protocol: Dict[str, Any]):
        """
        Initialize the data validator.

        Args:
            protocol: Protocol definition containing QC criteria
        """
        self.protocol = protocol
        self.qc_criteria = protocol.get('qc_criteria', {})
        self.measurements_spec = {
            m['measurement_id']: m for m in protocol.get('measurements', [])
        }

    def validate_measurement(self, measurement_id: str, value: float) -> Tuple[bool, Optional[str]]:
        """
        Validate a single measurement value.

        Args:
            measurement_id: Measurement identifier
            value: Measured value

        Returns:
            Tuple of (is_valid, error_message)
        """
        spec = self.measurements_spec.get(measurement_id)
        if not spec:
            return False, f"Unknown measurement ID: {measurement_id}"

        # Range validation
        if 'range' in spec:
            range_spec = spec['range']
            if 'min' in range_spec and value < range_spec['min']:
                return False, f"Value {value} below minimum {range_spec['min']}"
            if 'max' in range_spec and value > range_spec['max']:
                return False, f"Value {value} above maximum {range_spec['max']}"

        return True, None

    def validate_completeness(self, measurements: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Check if all required measurements are present.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Tuple of (is_complete, missing_measurements)
        """
        if not self.qc_criteria.get('data_validation', {}).get('completeness_check', False):
            return True, []

        measured_ids = {m['measurement_id'] for m in measurements}
        required_ids = set(self.measurements_spec.keys())
        missing = list(required_ids - measured_ids)

        return len(missing) == 0, missing

    def detect_outliers(self, measurements: List[Dict],
                       measurement_id: str,
                       method: str = 'iqr',
                       threshold: float = 1.5) -> List[int]:
        """
        Detect outliers in measurement data.

        Args:
            measurements: List of measurements
            measurement_id: ID of measurement to check
            method: Detection method ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection

        Returns:
            List of indices of outlier measurements
        """
        if not self.qc_criteria.get('data_validation', {}).get('outlier_detection', False):
            return []

        # Extract values for this measurement
        values = [
            m['value'] for m in measurements
            if m['measurement_id'] == measurement_id
        ]

        if len(values) < 3:
            return []  # Not enough data for outlier detection

        values_array = np.array(values)

        if method == 'iqr':
            q1, q3 = np.percentile(values_array, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            outliers = [
                i for i, v in enumerate(values)
                if v < lower_bound or v > upper_bound
            ]

        elif method == 'zscore':
            mean = np.mean(values_array)
            std = np.std(values_array)
            if std == 0:
                return []
            z_scores = np.abs((values_array - mean) / std)
            outliers = [i for i, z in enumerate(z_scores) if z > threshold]

        elif method == 'modified_zscore':
            median = np.median(values_array)
            mad = np.median(np.abs(values_array - median))
            if mad == 0:
                return []
            modified_z_scores = 0.6745 * (values_array - median) / mad
            outliers = [i for i, z in enumerate(np.abs(modified_z_scores)) if z > threshold]

        else:
            raise ValueError(f"Unknown outlier detection method: {method}")

        return outliers

    def evaluate_acceptance_criteria(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all acceptance criteria for a test.

        Args:
            test_data: Dictionary containing test results and metrics

        Returns:
            Dictionary with evaluation results for each criterion
        """
        results = {
            'criteria_results': [],
            'overall_pass': True,
            'critical_failures': [],
            'major_failures': [],
            'minor_failures': []
        }

        acceptance_criteria = self.qc_criteria.get('acceptance_criteria', [])

        for criterion in acceptance_criteria:
            criterion_id = criterion['criterion_id']
            description = criterion['description']
            condition = criterion['condition']
            severity = criterion['severity']

            # Evaluate condition
            passed, actual_value = self._evaluate_condition(condition, test_data)

            result = {
                'criterion_id': criterion_id,
                'description': description,
                'severity': severity,
                'passed': passed,
                'condition': condition,
                'actual_value': actual_value,
                'timestamp': datetime.now()
            }

            results['criteria_results'].append(result)

            if not passed:
                results['overall_pass'] = False
                if severity == 'critical':
                    results['critical_failures'].append(result)
                elif severity == 'major':
                    results['major_failures'].append(result)
                elif severity == 'minor':
                    results['minor_failures'].append(result)

        return results

    def _evaluate_condition(self, condition: Dict[str, Any],
                           test_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Evaluate a single condition.

        Args:
            condition: Condition specification
            test_data: Test data dictionary

        Returns:
            Tuple of (passed, actual_value)
        """
        metric = condition.get('metric')
        operator = condition.get('operator')
        threshold = condition.get('threshold')

        # Get actual value from test data
        actual_value = test_data.get(metric)

        if actual_value is None:
            return False, None

        # Evaluate based on operator
        if operator == '<=':
            passed = actual_value <= threshold
        elif operator == '>=':
            passed = actual_value >= threshold
        elif operator == '<':
            passed = actual_value < threshold
        elif operator == '>':
            passed = actual_value > threshold
        elif operator == '==':
            passed = actual_value == threshold
        elif operator == '!=':
            passed = actual_value != threshold
        else:
            raise ValueError(f"Unknown operator: {operator}")

        return passed, actual_value

    def calculate_degradation_metrics(self, initial_measurements: Dict[str, float],
                                     final_measurements: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate degradation metrics comparing initial and final measurements.

        Args:
            initial_measurements: Dictionary of initial measurement values
            final_measurements: Dictionary of final measurement values

        Returns:
            Dictionary of degradation metrics
        """
        metrics = {}

        for measurement_id in initial_measurements:
            if measurement_id in final_measurements:
                initial = initial_measurements[measurement_id]
                final = final_measurements[measurement_id]

                # Absolute change
                absolute_change = final - initial
                metrics[f"{measurement_id}_absolute_change"] = absolute_change

                # Percentage change
                if initial != 0:
                    percentage_change = ((final - initial) / abs(initial)) * 100
                    metrics[f"{measurement_id}_percentage_change"] = percentage_change
                else:
                    metrics[f"{measurement_id}_percentage_change"] = None

                # Store final values
                metrics[f"{measurement_id}_final"] = final
                metrics[f"{measurement_id}_initial"] = initial

        # Calculate specific degradation metrics for JBOX-001
        if 'M5' in initial_measurements and 'M5' in final_measurements:
            # Power degradation percentage
            metrics['power_degradation_percentage'] = abs(
                metrics.get('M5_percentage_change', 0)
            )

        if 'M1' in initial_measurements and 'M1' in final_measurements:
            # Contact resistance increase percentage
            metrics['resistance_increase_percentage'] = abs(
                metrics.get('M1_percentage_change', 0)
            )

        if 'M3' in final_measurements:
            # Insulation resistance final value
            metrics['insulation_resistance_final'] = final_measurements['M3']

        if 'M2' in initial_measurements and 'M2' in final_measurements:
            # Diode voltage drift percentage
            metrics['diode_voltage_drift_percentage'] = abs(
                metrics.get('M2_percentage_change', 0)
            )

        return metrics

    def generate_validation_report(self, test_run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.

        Args:
            test_run_data: Complete test run data

        Returns:
            Validation report dictionary
        """
        report = {
            'test_run_id': test_run_data.get('test_run_id'),
            'protocol_id': self.protocol['protocol_id'],
            'validation_timestamp': datetime.now(),
            'data_quality': {},
            'qc_results': {},
            'recommendations': []
        }

        measurements = test_run_data.get('measurements', [])

        # Completeness check
        is_complete, missing = self.validate_completeness(measurements)
        report['data_quality']['completeness'] = {
            'complete': is_complete,
            'missing_measurements': missing
        }

        if not is_complete:
            report['recommendations'].append(
                f"Missing measurements: {', '.join(missing)}"
            )

        # Range validation
        out_of_range = []
        for measurement in measurements:
            is_valid, error = self.validate_measurement(
                measurement['measurement_id'],
                measurement['value']
            )
            if not is_valid:
                out_of_range.append({
                    'measurement': measurement,
                    'error': error
                })

        report['data_quality']['range_validation'] = {
            'all_in_range': len(out_of_range) == 0,
            'out_of_range_count': len(out_of_range),
            'out_of_range_measurements': out_of_range
        }

        # Outlier detection
        outliers_detected = {}
        for measurement_id in self.measurements_spec:
            outliers = self.detect_outliers(measurements, measurement_id)
            if outliers:
                outliers_detected[measurement_id] = outliers

        report['data_quality']['outliers'] = outliers_detected

        # QC criteria evaluation (if test_data includes metrics)
        if 'metrics' in test_run_data:
            qc_results = self.evaluate_acceptance_criteria(test_run_data['metrics'])
            report['qc_results'] = qc_results

            if not qc_results['overall_pass']:
                report['recommendations'].append(
                    f"Test FAILED: {len(qc_results['critical_failures'])} critical, "
                    f"{len(qc_results['major_failures'])} major failures"
                )

        return report


if __name__ == "__main__":
    # Example usage
    from protocol_loader import ProtocolLoader

    # Load protocol
    loader = ProtocolLoader()
    protocol = loader.load_protocol("JBOX-001")

    # Create validator
    validator = DataValidator(protocol)

    # Test measurement validation
    is_valid, error = validator.validate_measurement("M1", 5.2)
    print(f"Measurement validation: {is_valid}, {error}")

    # Test degradation metrics
    initial = {'M1': 5.0, 'M5': 300.0}
    final = {'M1': 5.5, 'M5': 288.0}
    metrics = validator.calculate_degradation_metrics(initial, final)
    print(f"Degradation metrics: {metrics}")

    # Test QC evaluation
    test_data = {
        'power_degradation_percentage': 4.0,
        'resistance_increase_percentage': 10.0,
        'insulation_resistance_final': 50.0,
        'diode_voltage_drift_percentage': 5.0,
        'visual_defects_critical': 0,
        'weight_gain_percentage': 0.5,
        'max_temperature_rise': 35.0
    }
    qc_results = validator.evaluate_acceptance_criteria(test_data)
    print(f"QC Results: Pass={qc_results['overall_pass']}")
    print(f"Failures: {len(qc_results['critical_failures'])} critical, "
          f"{len(qc_results['major_failures'])} major")
