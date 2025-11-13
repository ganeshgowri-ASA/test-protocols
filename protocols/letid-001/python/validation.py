"""
LETID-001 Test Protocol Validation Module

This module provides validation functions for Light and Elevated Temperature
Induced Degradation (LeTID) test data according to IEC 61215-2:2021.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path
import re


class LETID001Validator:
    """Validator for LETID-001 test protocol data."""

    def __init__(self, protocol_schema_path: str = None):
        """
        Initialize validator with protocol schema.

        Args:
            protocol_schema_path: Path to protocol.json schema file
        """
        if protocol_schema_path is None:
            protocol_schema_path = Path(__file__).parent.parent / "schemas" / "protocol.json"

        with open(protocol_schema_path, 'r') as f:
            self.schema = json.load(f)

        self.errors = []
        self.warnings = []

    def validate_sample_info(self, sample_data: Dict[str, Any]) -> bool:
        """
        Validate sample information fields.

        Args:
            sample_data: Dictionary containing sample information

        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        fields = self.schema['test_parameters']['sample_info']['fields']

        for field in fields:
            field_name = field['name']

            # Check required fields
            if field.get('required', False) and field_name not in sample_data:
                self.errors.append(f"Missing required field: {field_name}")
                continue

            if field_name not in sample_data:
                continue

            value = sample_data[field_name]

            # Type validation
            if field['type'] == 'string' and not isinstance(value, str):
                self.errors.append(f"{field_name} must be a string")
            elif field['type'] == 'number' and not isinstance(value, (int, float)):
                self.errors.append(f"{field_name} must be a number")

            # Enum validation
            if field['type'] == 'enum' and value not in field['values']:
                self.errors.append(
                    f"{field_name} must be one of {field['values']}, got '{value}'"
                )

        return len(self.errors) == 0

    def validate_measurement(self, measurement_data: Dict[str, Any],
                            measurement_type: str) -> bool:
        """
        Validate measurement data.

        Args:
            measurement_data: Dictionary containing measurement values
            measurement_type: Type of measurement (initial_characterization,
                            periodic_monitoring, final_characterization)

        Returns:
            True if valid, False otherwise
        """
        self.errors = []

        if measurement_type not in self.schema['test_parameters']['measurements']:
            self.errors.append(f"Unknown measurement type: {measurement_type}")
            return False

        parameters = self.schema['test_parameters']['measurements'][measurement_type]['parameters']

        for param in parameters:
            param_name = param['name']

            # Check required parameters
            if param.get('required', False) and param_name not in measurement_data:
                self.errors.append(
                    f"Missing required parameter in {measurement_type}: {param_name}"
                )
                continue

            if param_name not in measurement_data:
                continue

            value = measurement_data[param_name]

            # Type validation
            if param['type'] == 'number':
                if not isinstance(value, (int, float)):
                    self.errors.append(f"{param_name} must be a number")
                elif value < 0:
                    self.warnings.append(f"{param_name} is negative: {value}")

            elif param['type'] == 'datetime':
                if isinstance(value, str):
                    try:
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        self.errors.append(f"{param_name} is not a valid ISO datetime")

        return len(self.errors) == 0

    def validate_test_conditions(self, actual_conditions: Dict[str, float]) -> bool:
        """
        Validate that actual test conditions are within tolerance.

        Args:
            actual_conditions: Dictionary with actual temperature, irradiance, etc.

        Returns:
            True if conditions are within tolerance, False otherwise
        """
        self.errors = []
        self.warnings = []

        spec_conditions = self.schema['test_conditions']

        for condition_name, condition_spec in spec_conditions.items():
            if condition_name not in actual_conditions:
                continue

            actual_value = actual_conditions[condition_name]
            target_value = condition_spec['value']
            tolerance = condition_spec.get('tolerance', 0)

            if abs(actual_value - target_value) > tolerance:
                self.warnings.append(
                    f"{condition_name}: {actual_value}{condition_spec['unit']} "
                    f"is outside tolerance (target: {target_value} ± {tolerance})"
                )

        return len(self.errors) == 0

    def validate_time_series(self, time_series_data: List[Dict[str, Any]]) -> bool:
        """
        Validate time series measurement data.

        Args:
            time_series_data: List of periodic measurements

        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []

        if not time_series_data:
            self.errors.append("Time series data is empty")
            return False

        # Validate each measurement
        for i, measurement in enumerate(time_series_data):
            if not self.validate_measurement(measurement, 'periodic_monitoring'):
                self.errors.append(f"Invalid measurement at index {i}")

        # Check temporal ordering
        elapsed_hours = [m.get('elapsed_hours', 0) for m in time_series_data]
        if elapsed_hours != sorted(elapsed_hours):
            self.warnings.append("Time series measurements are not in chronological order")

        # Check for missing intervals
        interval = self.schema['test_parameters']['measurements']['periodic_monitoring']['interval_hours']
        for i in range(1, len(elapsed_hours)):
            gap = elapsed_hours[i] - elapsed_hours[i-1]
            if gap > interval * 1.5:  # Allow 50% margin
                self.warnings.append(
                    f"Large time gap detected: {gap} hours between measurements "
                    f"at {elapsed_hours[i-1]}h and {elapsed_hours[i]}h"
                )

        return len(self.errors) == 0

    def check_acceptance_criteria(self, initial_pmax: float,
                                  final_pmax: float) -> Dict[str, Any]:
        """
        Check if test results meet acceptance criteria.

        Args:
            initial_pmax: Initial maximum power (W)
            final_pmax: Final maximum power (W)

        Returns:
            Dictionary with pass/fail status and details
        """
        degradation = ((final_pmax - initial_pmax) / initial_pmax) * 100

        criteria = self.schema['acceptance_criteria']
        results = {
            'power_degradation_percent': round(degradation, 2),
            'pass': True,
            'failures': [],
            'warnings': []
        }

        # Check maximum degradation
        max_deg = criteria['max_power_degradation']['threshold']
        if degradation < max_deg:
            results['pass'] = False
            results['failures'].append(
                f"Power degradation {degradation:.2f}% exceeds limit of {max_deg}%"
            )

        # Check stabilized degradation (warning)
        max_stab = criteria['max_stabilized_degradation']['threshold']
        if degradation < max_stab:
            results['warnings'].append(
                f"Power degradation {degradation:.2f}% exceeds warning threshold of {max_stab}%"
            )

        return results

    def validate_complete_test(self, test_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate complete test data package.

        Args:
            test_data: Complete test data including sample info, measurements, etc.

        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sections_validated': []
        }

        # Validate sample information
        if 'sample_info' in test_data:
            if self.validate_sample_info(test_data['sample_info']):
                report['sections_validated'].append('sample_info')
            else:
                report['valid'] = False
                report['errors'].extend(self.errors)
        else:
            report['valid'] = False
            report['errors'].append("Missing sample_info section")

        # Validate initial characterization
        if 'initial_characterization' in test_data:
            if self.validate_measurement(
                test_data['initial_characterization'],
                'initial_characterization'
            ):
                report['sections_validated'].append('initial_characterization')
            else:
                report['valid'] = False
                report['errors'].extend(self.errors)
        else:
            report['valid'] = False
            report['errors'].append("Missing initial_characterization section")

        # Validate time series
        if 'time_series' in test_data:
            if self.validate_time_series(test_data['time_series']):
                report['sections_validated'].append('time_series')
            else:
                report['valid'] = False
                report['errors'].extend(self.errors)
            report['warnings'].extend(self.warnings)
        else:
            report['warnings'].append("No time series data provided")

        # Validate final characterization
        if 'final_characterization' in test_data:
            if self.validate_measurement(
                test_data['final_characterization'],
                'final_characterization'
            ):
                report['sections_validated'].append('final_characterization')
            else:
                report['valid'] = False
                report['errors'].extend(self.errors)
        else:
            report['valid'] = False
            report['errors'].append("Missing final_characterization section")

        # Check acceptance criteria if both initial and final data exist
        if 'initial_characterization' in test_data and 'final_characterization' in test_data:
            initial_pmax = test_data['initial_characterization'].get('pmax')
            final_pmax = test_data['final_characterization'].get('pmax')

            if initial_pmax and final_pmax:
                criteria_results = self.check_acceptance_criteria(initial_pmax, final_pmax)
                report['acceptance_criteria'] = criteria_results
                if not criteria_results['pass']:
                    report['warnings'].append("Test failed acceptance criteria")

        return report['valid'], report


def validate_module_id(module_id: str) -> bool:
    """
    Validate module ID format.

    Args:
        module_id: Module identifier string

    Returns:
        True if valid format, False otherwise
    """
    # Example validation: alphanumeric with hyphens, 5-50 chars
    pattern = r'^[A-Za-z0-9\-]{5,50}$'
    return bool(re.match(pattern, module_id))


def validate_serial_number(serial_number: str) -> bool:
    """
    Validate serial number format.

    Args:
        serial_number: Serial number string

    Returns:
        True if valid format, False otherwise
    """
    # Example validation: alphanumeric, 5-30 chars
    pattern = r'^[A-Za-z0-9\-]{5,30}$'
    return bool(re.match(pattern, serial_number))
