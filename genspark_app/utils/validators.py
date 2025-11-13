"""
Data and Parameter Validation Utilities

Handles validation of input parameters, measurement data, and test conditions
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ParameterValidator:
    """Validates input parameters against protocol specifications"""

    @staticmethod
    def validate_parameter(value: Any, param_spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a single parameter against its specification

        Args:
            value: Parameter value to validate
            param_spec: Parameter specification from protocol template

        Returns:
            Tuple of (is_valid, error_message)
        """
        param_type = param_spec.get('type')
        required = param_spec.get('required', False)
        validation = param_spec.get('validation', {})

        # Check if required
        if required and value is None:
            return False, f"Parameter is required"

        if value is None and not required:
            return True, None

        # Type checking
        if param_type == 'string':
            if not isinstance(value, str):
                return False, f"Expected string, got {type(value).__name__}"

            # Pattern validation
            if 'pattern' in validation:
                pattern = validation['pattern']
                if not re.match(pattern, value):
                    return False, validation.get('message', f"Value doesn't match pattern: {pattern}")

        elif param_type == 'float':
            try:
                value = float(value)
            except (TypeError, ValueError):
                return False, f"Cannot convert to float: {value}"

            # Range validation
            if 'min' in validation and value < validation['min']:
                return False, validation.get('message', f"Value must be >= {validation['min']}")
            if 'max' in validation and value > validation['max']:
                return False, validation.get('message', f"Value must be <= {validation['max']}")

        elif param_type == 'integer':
            try:
                value = int(value)
            except (TypeError, ValueError):
                return False, f"Cannot convert to integer: {value}"

            # Range validation
            if 'min' in validation and value < validation['min']:
                return False, validation.get('message', f"Value must be >= {validation['min']}")
            if 'max' in validation and value > validation['max']:
                return False, validation.get('message', f"Value must be <= {validation['max']}")

        elif param_type == 'boolean':
            if not isinstance(value, bool):
                return False, f"Expected boolean, got {type(value).__name__}"

        # Options validation
        if 'options' in param_spec and value not in param_spec['options']:
            return False, f"Value must be one of: {param_spec['options']}"

        return True, None

    @staticmethod
    def validate_all_parameters(parameters: Dict[str, Any],
                               parameter_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate all parameters

        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'errors': {},
            'warnings': []
        }

        for spec in parameter_specs:
            param_name = spec['name']
            value = parameters.get(param_name)

            is_valid, error_msg = ParameterValidator.validate_parameter(value, spec)

            if not is_valid:
                results['valid'] = False
                results['errors'][param_name] = error_msg
                logger.warning(f"Validation failed for {param_name}: {error_msg}")

        return results

    @staticmethod
    def check_conditional_parameters(parameters: Dict[str, Any],
                                    parameter_specs: List[Dict[str, Any]]) -> List[str]:
        """
        Check which conditional parameters should be shown/validated

        Returns:
            List of parameter names that should be active
        """
        active_params = []

        for spec in parameter_specs:
            param_name = spec['name']

            # Check if parameter has conditional rules
            if 'conditional' not in spec:
                active_params.append(param_name)
                continue

            conditional = spec['conditional']
            depends_on = conditional.get('depends_on')
            show_when = conditional.get('show_when')

            if depends_on and depends_on in parameters:
                dependency_value = parameters[depends_on]
                if dependency_value == show_when:
                    active_params.append(param_name)
            else:
                # If dependency not met, parameter is inactive
                pass

        return active_params


class DataValidator:
    """Validates measurement data and test conditions"""

    @staticmethod
    def check_data_quality(data: np.ndarray) -> Dict[str, Any]:
        """
        Check quality of measurement data

        Returns:
            Dict with quality metrics
        """
        results = {
            'valid': True,
            'issues': [],
            'metrics': {}
        }

        # Check for NaN values
        nan_count = np.sum(np.isnan(data))
        if nan_count > 0:
            results['issues'].append(f"Found {nan_count} NaN values")
            results['valid'] = False

        # Check for infinite values
        inf_count = np.sum(np.isinf(data))
        if inf_count > 0:
            results['issues'].append(f"Found {inf_count} infinite values")
            results['valid'] = False

        # Check for outliers (using IQR method)
        if len(data) > 4:
            q1, q3 = np.percentile(data[~np.isnan(data)], [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr
            outliers = np.sum((data < lower_bound) | (data > upper_bound))
            outlier_percentage = (outliers / len(data)) * 100

            results['metrics']['outlier_percentage'] = outlier_percentage
            if outlier_percentage > 5:
                results['issues'].append(f"High outlier percentage: {outlier_percentage:.1f}%")

        # Calculate coefficient of variation
        if len(data) > 0:
            mean = np.mean(data[~np.isnan(data)])
            std = np.std(data[~np.isnan(data)])
            if mean != 0:
                cv = (std / mean) * 100
                results['metrics']['coefficient_of_variation'] = cv

        results['metrics']['completeness'] = (len(data) - nan_count) / len(data) * 100 if len(data) > 0 else 0

        return results

    @staticmethod
    def validate_test_conditions(conditions: Dict[str, float],
                                 acceptance_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate test conditions against acceptance criteria

        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'violations': []
        }

        env_compliance = acceptance_criteria.get('environmental_compliance', {})

        for param_name, criteria in env_compliance.items():
            if param_name not in conditions:
                continue

            value = conditions[param_name]
            min_val = criteria.get('min')
            max_val = criteria.get('max')
            unit = criteria.get('unit', '')

            if min_val is not None and value < min_val:
                results['valid'] = False
                results['violations'].append(
                    f"{param_name} ({value}{unit}) below minimum ({min_val}{unit})"
                )

            if max_val is not None and value > max_val:
                results['valid'] = False
                results['violations'].append(
                    f"{param_name} ({value}{unit}) above maximum ({max_val}{unit})"
                )

        return results

    @staticmethod
    def check_measurement_stability(data: np.ndarray,
                                   criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if measurements meet stability criteria

        Returns:
            Dict with stability check results
        """
        max_variation = criteria.get('temperature_variation', {}).get('max')
        period_minutes = criteria.get('temperature_variation', {}).get('period', 'last_10_minutes')

        # For simplicity, check last N points
        window_size = 10  # Last 10 measurements

        if len(data) < window_size:
            return {
                'stable': False,
                'reason': 'Insufficient data points',
                'variation': None
            }

        recent_data = data[-window_size:]
        variation = np.std(recent_data)

        is_stable = variation <= max_variation

        return {
            'stable': is_stable,
            'variation': float(variation),
            'threshold': max_variation,
            'data_points_checked': window_size
        }

    @staticmethod
    def validate_min_data_points(measurement_count: int,
                                min_required: int) -> Tuple[bool, str]:
        """
        Check if minimum number of data points collected

        Returns:
            Tuple of (is_valid, message)
        """
        if measurement_count < min_required:
            return False, f"Only {measurement_count} data points collected, need {min_required}"
        return True, f"Sufficient data points: {measurement_count} >= {min_required}"
