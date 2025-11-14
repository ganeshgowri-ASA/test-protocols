"""
Data Validator Module
=====================

Validates test data against protocol requirements and performs quality checks.
"""

import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a single validation error"""
    field: str
    error_type: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    validated_data: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, field: str, error_type: str, message: str):
        """Add an error to the validation result"""
        self.errors.append(ValidationError(field, error_type, message, "error"))
        self.is_valid = False

    def add_warning(self, field: str, error_type: str, message: str):
        """Add a warning to the validation result"""
        self.warnings.append(ValidationError(field, error_type, message, "warning"))

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_error_messages(self) -> List[str]:
        """Get all error messages"""
        return [f"{e.field}: {e.message}" for e in self.errors]

    def get_warning_messages(self) -> List[str]:
        """Get all warning messages"""
        return [f"{w.field}: {w.message}" for w in self.warnings]


class DataValidator:
    """
    Data Validator class for validating test data against protocol requirements.

    Features:
    - Validate required fields
    - Type validation
    - Range validation
    - Pattern matching (regex)
    - Custom validation rules
    - Calculate derived fields
    """

    def __init__(self, protocol_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Data Validator.

        Args:
            protocol_config: Protocol configuration dictionary
        """
        self.protocol_config = protocol_config
        self.data_points = protocol_config.get('data_points', []) if protocol_config else []

    def validate(self, data: Dict[str, Any], protocol_config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate data against protocol configuration.

        Args:
            data: Data dictionary to validate
            protocol_config: Protocol configuration (overrides instance config)

        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True, validated_data=data.copy())

        # Use provided config or instance config
        config = protocol_config or self.protocol_config
        if not config:
            result.add_error("_config", "missing_config", "No protocol configuration provided")
            return result

        data_points = config.get('data_points', [])

        # Validate each data point
        for data_point in data_points:
            field_name = data_point['field']
            field_value = data.get(field_name)

            # Check required fields
            if data_point.get('required', False):
                if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                    result.add_error(
                        field_name,
                        "required_field",
                        f"Field '{data_point.get('label', field_name)}' is required"
                    )
                    continue

            # Skip validation if field is not provided and not required
            if field_value is None:
                continue

            # Type validation
            self._validate_type(field_name, field_value, data_point, result)

            # Range validation for numbers
            if data_point['type'] == 'number':
                self._validate_number_range(field_name, field_value, data_point, result)

            # Pattern validation for strings
            if data_point['type'] == 'string' and 'validation' in data_point:
                self._validate_pattern(field_name, field_value, data_point, result)

            # Store validated value
            result.validated_data[field_name] = field_value

        # Calculate derived fields
        self._calculate_derived_fields(result.validated_data, data_points, result)

        # Validate acceptance criteria
        self._validate_acceptance_criteria(result.validated_data, config, result)

        return result

    def _validate_type(
        self,
        field_name: str,
        value: Any,
        data_point: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate field type"""
        expected_type = data_point['type']

        type_validators = {
            'string': lambda v: isinstance(v, str),
            'number': lambda v: isinstance(v, (int, float)),
            'boolean': lambda v: isinstance(v, bool),
            'date': lambda v: isinstance(v, (date, datetime, str)),
            'array': lambda v: isinstance(v, list),
        }

        validator = type_validators.get(expected_type)
        if validator and not validator(value):
            result.add_error(
                field_name,
                "type_mismatch",
                f"Expected type {expected_type}, got {type(value).__name__}"
            )

    def _validate_number_range(
        self,
        field_name: str,
        value: Any,
        data_point: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate number range"""
        if not isinstance(value, (int, float)):
            return

        min_value = data_point.get('min')
        max_value = data_point.get('max')

        if min_value is not None and value < min_value:
            result.add_error(
                field_name,
                "range_error",
                f"Value {value} is below minimum {min_value}"
            )

        if max_value is not None and value > max_value:
            result.add_error(
                field_name,
                "range_error",
                f"Value {value} exceeds maximum {max_value}"
            )

    def _validate_pattern(
        self,
        field_name: str,
        value: Any,
        data_point: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate string pattern using regex"""
        if not isinstance(value, str):
            return

        validation_rule = data_point.get('validation', '')

        # Handle regex validation
        if validation_rule.startswith('regex:'):
            pattern = validation_rule.replace('regex:', '')
            try:
                if not re.match(pattern, value):
                    result.add_error(
                        field_name,
                        "pattern_mismatch",
                        f"Value does not match required pattern: {pattern}"
                    )
            except re.error as e:
                logger.error(f"Invalid regex pattern: {e}")

    def _calculate_derived_fields(
        self,
        data: Dict[str, Any],
        data_points: List[Dict[str, Any]],
        result: ValidationResult
    ):
        """Calculate fields marked as calculated"""
        for data_point in data_points:
            if data_point.get('calculated', False) and 'formula' in data_point:
                field_name = data_point['field']
                formula = data_point['formula']

                try:
                    calculated_value = self._evaluate_formula(formula, data)
                    data[field_name] = calculated_value
                    result.validated_data[field_name] = calculated_value
                except Exception as e:
                    result.add_warning(
                        field_name,
                        "calculation_error",
                        f"Could not calculate field: {e}"
                    )

    def _evaluate_formula(self, formula: str, data: Dict[str, Any]) -> float:
        """
        Evaluate a formula string with data values.

        Args:
            formula: Formula string (e.g., "1000 + (2 * max_system_voltage)")
            data: Data dictionary with field values

        Returns:
            Calculated value
        """
        # Create a safe evaluation context with only data values
        eval_context = {k: v for k, v in data.items() if isinstance(v, (int, float))}

        # Add math functions if needed
        import math
        eval_context['abs'] = abs
        eval_context['round'] = round
        eval_context['min'] = min
        eval_context['max'] = max
        eval_context['sqrt'] = math.sqrt
        eval_context['pow'] = math.pow

        try:
            result = eval(formula, {"__builtins__": {}}, eval_context)
            return float(result)
        except Exception as e:
            logger.error(f"Formula evaluation error: {e}")
            raise

    def _validate_acceptance_criteria(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any],
        result: ValidationResult
    ):
        """Validate data against acceptance criteria"""
        acceptance_criteria = config.get('acceptance_criteria', {})

        for criterion_name, criterion in acceptance_criteria.items():
            # Check if criterion is applicable
            if isinstance(criterion, dict):
                self._check_criterion(criterion_name, criterion, data, result)

    def _check_criterion(
        self,
        criterion_name: str,
        criterion: Dict[str, Any],
        data: Dict[str, Any],
        result: ValidationResult
    ):
        """Check a single acceptance criterion"""
        condition = criterion.get('condition')

        # Map field name from criterion (handles name differences)
        # For example, insulation_resistance_initial maps to data field
        data_field = criterion_name
        if data_field not in data:
            # Try to find matching field in data
            for key in data.keys():
                if criterion_name in key:
                    data_field = key
                    break

        if data_field not in data:
            return  # Skip if field not in data

        value = data[data_field]
        if value is None:
            return

        # Validate based on condition
        if condition == 'greater_than_or_equal':
            min_value = criterion.get('min_value')
            if min_value is not None:
                # For area-normalized values, need to check if we need to normalize
                if 'unit' in criterion and '/' in criterion['unit']:
                    # This is an area-normalized criterion
                    # Check if we need to normalize the value
                    if 'module_area' in data:
                        normalized_value = value / data['module_area']
                        if normalized_value < min_value:
                            result.add_error(
                                data_field,
                                "acceptance_criteria",
                                f"{criterion_name}: {normalized_value:.2f} {criterion['unit']} is below minimum {min_value} {criterion['unit']}"
                            )
                else:
                    if value < min_value:
                        result.add_error(
                            data_field,
                            "acceptance_criteria",
                            f"{criterion_name}: {value} is below minimum {min_value}"
                        )

        elif condition == 'less_than_or_equal':
            max_value = criterion.get('max_value')
            if max_value is not None and value > max_value:
                result.add_error(
                    data_field,
                    "acceptance_criteria",
                    f"{criterion_name}: {value} exceeds maximum {max_value}"
                )

        elif condition == 'equal':
            expected_value = criterion.get('value')
            if expected_value is not None and value != expected_value:
                result.add_error(
                    data_field,
                    "acceptance_criteria",
                    f"{criterion_name}: expected {expected_value}, got {value}"
                )

        # Boolean criteria
        if 'allowed' in criterion:
            allowed = criterion['allowed']
            if isinstance(value, bool) and value != allowed:
                result.add_error(
                    data_field,
                    "acceptance_criteria",
                    f"{criterion_name}: {criterion.get('description', 'Check failed')}"
                )

    def validate_environmental_conditions(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate environmental conditions against requirements.

        Args:
            data: Data with environmental measurements
            config: Protocol configuration

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        env_conditions = config.get('environmental_conditions', {})

        condition_mappings = {
            'temperature': 'ambient_temperature',
            'relative_humidity': 'relative_humidity'
        }

        for env_param, data_field in condition_mappings.items():
            if env_param in env_conditions and data_field in data:
                requirements = env_conditions[env_param]
                value = data[data_field]

                if value is None:
                    continue

                min_val = requirements.get('min')
                max_val = requirements.get('max')
                unit = requirements.get('unit', '')

                if min_val is not None and value < min_val:
                    result.add_warning(
                        data_field,
                        "environmental_condition",
                        f"{env_param} ({value}{unit}) is below minimum ({min_val}{unit})"
                    )

                if max_val is not None and value > max_val:
                    result.add_warning(
                        data_field,
                        "environmental_condition",
                        f"{env_param} ({value}{unit}) exceeds maximum ({max_val}{unit})"
                    )

        return result

    def validate_equipment_calibration(
        self,
        equipment_ids: List[str],
        equipment_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate equipment calibration status.

        Args:
            equipment_ids: List of equipment IDs used
            equipment_data: Equipment calibration data

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)

        for eq_id in equipment_ids:
            if eq_id not in equipment_data:
                result.add_warning(
                    "equipment",
                    "missing_data",
                    f"No calibration data found for equipment {eq_id}"
                )
                continue

            eq_info = equipment_data[eq_id]

            # Check calibration status
            cal_required = eq_info.get('calibration_required', False)
            if cal_required:
                next_cal_date = eq_info.get('next_calibration_date')
                if next_cal_date:
                    if isinstance(next_cal_date, str):
                        try:
                            next_cal_date = datetime.fromisoformat(next_cal_date).date()
                        except ValueError:
                            pass

                    if isinstance(next_cal_date, date) and next_cal_date < date.today():
                        result.add_error(
                            "equipment",
                            "calibration_overdue",
                            f"Equipment {eq_id} calibration is overdue (due: {next_cal_date})"
                        )

        return result


# Helper functions

def validate_data(data: Dict[str, Any], protocol_config: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate data.

    Args:
        data: Data dictionary
        protocol_config: Protocol configuration

    Returns:
        ValidationResult
    """
    validator = DataValidator(protocol_config)
    return validator.validate(data)


def is_data_valid(data: Dict[str, Any], protocol_config: Dict[str, Any]) -> bool:
    """
    Check if data is valid (convenience function).

    Args:
        data: Data dictionary
        protocol_config: Protocol configuration

    Returns:
        True if valid, False otherwise
    """
    result = validate_data(data, protocol_config)
    return result.is_valid and not result.has_errors()
