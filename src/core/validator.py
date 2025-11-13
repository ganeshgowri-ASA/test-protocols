"""Data validation against protocol schemas."""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

from src.core.protocol_loader import ProtocolLoader


class DataValidator:
    """Validates measurement data against protocol schemas."""

    def __init__(self, protocol_id: str):
        """Initialize validator for a specific protocol.

        Args:
            protocol_id: Protocol identifier
        """
        self.protocol_id = protocol_id
        self.loader = ProtocolLoader()
        self.protocol = self.loader.load(protocol_id)
        try:
            self.schema = self.loader.load_schema(protocol_id)
        except FileNotFoundError:
            self.schema = None

    def validate_measurement(self, measurement: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single measurement against protocol specification.

        Args:
            measurement: Measurement data dictionary

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Get field definitions from protocol
        fields = self.protocol['data_collection']['fields']
        field_map = {f['name']: f for f in fields}

        # Check required fields
        for field_def in fields:
            field_name = field_def['name']
            if field_def.get('required', False) and not field_def.get('calculated', False):
                if field_name not in measurement or measurement[field_name] is None:
                    errors.append(f"Required field '{field_name}' is missing")

        # Validate field values
        for field_name, value in measurement.items():
            if field_name not in field_map:
                continue  # Skip unknown fields (may be metadata)

            field_def = field_map[field_name]

            # Type validation
            expected_type = field_def.get('type')
            if not self._validate_type(value, expected_type):
                errors.append(
                    f"Field '{field_name}' has wrong type. "
                    f"Expected {expected_type}, got {type(value).__name__}"
                )
                continue

            # Range validation
            validation = field_def.get('validation', {})
            if 'min' in validation and value < validation['min']:
                errors.append(
                    f"Field '{field_name}' value {value} is below minimum {validation['min']}"
                )

            if 'max' in validation and value > validation['max']:
                errors.append(
                    f"Field '{field_name}' value {value} is above maximum {validation['max']}"
                )

            # Enum validation
            if 'enum' in field_def and value not in field_def['enum']:
                errors.append(
                    f"Field '{field_name}' value {value} not in allowed values {field_def['enum']}"
                )

        return len(errors) == 0, errors

    def validate_test_run(self, test_run_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete test run data.

        Args:
            test_run_data: Complete test run data including metadata and measurements

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # If JSON schema is available, use it
        if self.schema:
            try:
                validate(instance=test_run_data, schema=self.schema)
            except ValidationError as e:
                errors.append(f"Schema validation error: {e.message}")
                return False, errors

        # Additional custom validation
        # Check protocol_id matches
        if test_run_data.get('test_run', {}).get('protocol_id') != self.protocol_id:
            errors.append(f"Protocol ID mismatch. Expected {self.protocol_id}")

        # Validate all measurements
        measurements = test_run_data.get('measurements', [])
        if not measurements:
            errors.append("No measurements found in test run data")
        else:
            for idx, measurement in enumerate(measurements):
                is_valid, measurement_errors = self.validate_measurement(measurement)
                if not is_valid:
                    errors.append(f"Measurement {idx}: {', '.join(measurement_errors)}")

        # Check irradiance levels coverage (PERF-002 specific)
        if self.protocol_id == 'PERF-002':
            expected_levels = self.loader.get_irradiance_levels(self.protocol_id)
            measured_levels = set(
                m.get('target_irradiance') for m in measurements
                if m.get('target_irradiance') is not None
            )
            missing_levels = set(expected_levels) - measured_levels
            if missing_levels:
                errors.append(
                    f"Missing measurements for irradiance levels: {sorted(missing_levels)}"
                )

        return len(errors) == 0, errors

    def validate_irradiance_tolerance(
        self,
        target: float,
        actual: float,
        tolerance_percent: float = 2.0
    ) -> Tuple[bool, Optional[str]]:
        """Validate irradiance is within tolerance of target.

        Args:
            target: Target irradiance level (W/m²)
            actual: Actual measured irradiance (W/m²)
            tolerance_percent: Acceptable tolerance percentage

        Returns:
            Tuple of (is_valid, error_message)
        """
        tolerance = target * (tolerance_percent / 100.0)
        min_value = target - tolerance
        max_value = target + tolerance

        if min_value <= actual <= max_value:
            return True, None
        else:
            error = (
                f"Irradiance {actual} W/m² outside tolerance of "
                f"{target} ± {tolerance_percent}% ({min_value:.1f} - {max_value:.1f} W/m²)"
            )
            return False, error

    def validate_temperature_tolerance(
        self,
        target: float,
        actual: float,
        tolerance: float = 2.0
    ) -> Tuple[bool, Optional[str]]:
        """Validate temperature is within tolerance of target.

        Args:
            target: Target temperature (°C)
            actual: Actual measured temperature (°C)
            tolerance: Acceptable tolerance (°C)

        Returns:
            Tuple of (is_valid, error_message)
        """
        min_value = target - tolerance
        max_value = target + tolerance

        if min_value <= actual <= max_value:
            return True, None
        else:
            error = (
                f"Temperature {actual}°C outside tolerance of "
                f"{target} ± {tolerance}°C ({min_value:.1f} - {max_value:.1f}°C)"
            )
            return False, error

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type matches expected type.

        Args:
            value: Value to validate
            expected_type: Expected type string

        Returns:
            True if type matches
        """
        type_map = {
            'string': str,
            'integer': int,
            'float': (int, float),  # Allow int for float fields
            'number': (int, float),
            'boolean': bool,
            'datetime': (str, datetime),  # Accept ISO string or datetime object
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_python_type)


class QCValidator:
    """Performs quality control checks based on protocol specifications."""

    def __init__(self, protocol_id: str):
        """Initialize QC validator.

        Args:
            protocol_id: Protocol identifier
        """
        self.protocol_id = protocol_id
        self.loader = ProtocolLoader()
        self.protocol = self.loader.load(protocol_id)
        self.qc_checks = self.loader.get_qc_checks(protocol_id)

    def run_all_checks(
        self,
        measurements: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run all QC checks for the protocol.

        Args:
            measurements: List of measurement data
            analysis_results: Calculated analysis results

        Returns:
            List of QC check results
        """
        results = []

        for check_def in self.qc_checks:
            check_name = check_def['name']
            check_type = check_def['type']

            if check_type == 'range':
                result = self._check_range(check_def, measurements, analysis_results)
            elif check_type == 'threshold':
                result = self._check_threshold(check_def, measurements, analysis_results)
            elif check_type == 'completeness':
                result = self._check_completeness(check_def, measurements)
            elif check_type == 'correlation':
                result = self._check_correlation(check_def, analysis_results)
            else:
                result = {
                    'check_name': check_name,
                    'status': 'na',
                    'message': f"Unknown check type: {check_type}"
                }

            result['severity'] = check_def.get('severity', 'normal')
            results.append(result)

        return results

    def _check_range(
        self,
        check_def: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if parameter is within acceptable range."""
        check_name = check_def['name']
        parameter = check_def['parameter']

        # Determine where to find the parameter
        if check_def.get('per_measurement', False):
            # Check each measurement
            failures = []
            for idx, m in enumerate(measurements):
                value = m.get(parameter)
                if value is not None:
                    if 'tolerance_type' in check_def:
                        # Percentage tolerance
                        target = m.get(f"target_{parameter}", check_def.get('target'))
                        tolerance_pct = check_def['tolerance_value']
                        tolerance = target * (tolerance_pct / 100)
                        if not (target - tolerance <= value <= target + tolerance):
                            failures.append(f"Measurement {idx}: {value}")
                    else:
                        # Absolute range
                        min_val = check_def.get('min', float('-inf'))
                        max_val = check_def.get('max', float('inf'))
                        if not (min_val <= value <= max_val):
                            failures.append(f"Measurement {idx}: {value}")

            if failures:
                return {
                    'check_name': check_name,
                    'status': 'fail',
                    'message': f"Values out of range: {', '.join(failures[:5])}"
                }
            else:
                return {
                    'check_name': check_name,
                    'status': 'pass',
                    'message': 'All measurements within range'
                }
        else:
            # Check analysis result
            value = analysis_results.get(parameter)
            if value is None:
                return {
                    'check_name': check_name,
                    'status': 'na',
                    'message': f"Parameter '{parameter}' not found"
                }

            min_val = check_def.get('min', float('-inf'))
            max_val = check_def.get('max', float('inf'))

            if min_val <= value <= max_val:
                return {
                    'check_name': check_name,
                    'status': 'pass',
                    'message': f"{parameter} = {value} within range [{min_val}, {max_val}]"
                }
            else:
                return {
                    'check_name': check_name,
                    'status': 'fail',
                    'message': f"{parameter} = {value} outside range [{min_val}, {max_val}]"
                }

    def _check_threshold(
        self,
        check_def: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if parameter meets threshold requirement."""
        check_name = check_def['name']
        parameter = check_def['parameter']

        value = analysis_results.get(parameter)
        if value is None:
            return {
                'check_name': check_name,
                'status': 'na',
                'message': f"Parameter '{parameter}' not found"
            }

        min_val = check_def.get('min', float('-inf'))
        max_val = check_def.get('max', float('inf'))

        if min_val <= value <= max_val:
            return {
                'check_name': check_name,
                'status': 'pass',
                'message': f"{parameter} = {value} meets threshold"
            }
        else:
            return {
                'check_name': check_name,
                'status': 'fail',
                'message': f"{parameter} = {value} fails threshold requirement"
            }

    def _check_completeness(
        self,
        check_def: Dict[str, Any],
        measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if all required measurements are present."""
        check_name = check_def['name']
        required_count = check_def.get('required_measurements', 0)
        actual_count = len(measurements)

        if actual_count >= required_count:
            return {
                'check_name': check_name,
                'status': 'pass',
                'message': f"All {actual_count} required measurements present"
            }
        else:
            return {
                'check_name': check_name,
                'status': 'fail',
                'message': f"Only {actual_count}/{required_count} measurements present"
            }

    def _check_correlation(
        self,
        check_def: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check correlation coefficient meets requirement."""
        check_name = check_def['name']
        r_squared = analysis_results.get('r_squared', 0)
        min_r_squared = check_def.get('min_r_squared', 0.95)

        if r_squared >= min_r_squared:
            return {
                'check_name': check_name,
                'status': 'pass',
                'message': f"R² = {r_squared:.4f} meets requirement (≥{min_r_squared})"
            }
        else:
            return {
                'check_name': check_name,
                'status': 'fail',
                'message': f"R² = {r_squared:.4f} below requirement (≥{min_r_squared})"
            }
