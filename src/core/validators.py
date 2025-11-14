"""Validators module for parameter and data validation."""

import re
from typing import Any, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ParameterValidator:
    """Validate parameter values against protocol definitions."""

    @staticmethod
    def validate(param_def: Dict[str, Any], value: Any) -> Tuple[bool, str]:
        """
        Validate a value against parameter definition.

        Args:
            param_def: Parameter definition from protocol
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        param_name = param_def.get("name", "Parameter")

        # Check required
        if param_def.get("required", False) and value is None:
            error_msg = f"{param_name} is required"
            logger.warning(error_msg)
            return False, error_msg

        # If not required and value is None, it's valid
        if value is None:
            return True, ""

        # Type validation
        param_type = param_def.get("type")
        if not ParameterValidator._validate_type(param_type, value):
            error_msg = f"Invalid type for {param_name}. Expected {param_type}"
            logger.warning(error_msg)
            return False, error_msg

        # Numeric range validation
        if param_type in ["float", "integer"]:
            if "min_value" in param_def and value < param_def["min_value"]:
                error_msg = (
                    f"{param_name} value {value} is below minimum "
                    f"{param_def['min_value']}"
                )
                logger.warning(error_msg)
                return False, error_msg

            if "max_value" in param_def and value > param_def["max_value"]:
                error_msg = (
                    f"{param_name} value {value} exceeds maximum "
                    f"{param_def['max_value']}"
                )
                logger.warning(error_msg)
                return False, error_msg

        # String pattern validation
        if param_type == "string" and "validation" in param_def:
            validation = param_def["validation"]
            if validation.get("type") == "pattern":
                pattern = validation.get("pattern")
                if pattern and not re.match(pattern, str(value)):
                    error_msg = f"{param_name} format is invalid. Expected pattern: {pattern}"
                    logger.warning(error_msg)
                    return False, error_msg

            # String length validation
            if "min_length" in validation:
                if len(str(value)) < validation["min_length"]:
                    error_msg = (
                        f"{param_name} is too short. "
                        f"Minimum length: {validation['min_length']}"
                    )
                    logger.warning(error_msg)
                    return False, error_msg

            if "max_length" in validation:
                if len(str(value)) > validation["max_length"]:
                    error_msg = (
                        f"{param_name} is too long. "
                        f"Maximum length: {validation['max_length']}"
                    )
                    logger.warning(error_msg)
                    return False, error_msg

        logger.debug(f"Validation passed for {param_name}")
        return True, ""

    @staticmethod
    def _validate_type(expected_type: str, value: Any) -> bool:
        """
        Validate value type.

        Args:
            expected_type: Expected type name
            value: Value to check

        Returns:
            True if type matches
        """
        type_map = {
            "float": (float, int),  # Accept int for float
            "integer": int,
            "string": str,
            "boolean": bool,
            "date": (str, datetime),
            "time": (str, datetime),
        }

        expected = type_map.get(expected_type)
        if expected is None:
            logger.warning(f"Unknown type: {expected_type}")
            return True  # Unknown types pass validation

        return isinstance(value, expected)

    @staticmethod
    def validate_all(
        parameters_def: list[Dict[str, Any]], values: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate all parameters against their definitions.

        Args:
            parameters_def: List of parameter definitions
            values: Dictionary of parameter values

        Returns:
            Tuple of (all_valid, error_messages_dict)
        """
        all_valid = True
        errors = {}

        for param_def in parameters_def:
            param_id = param_def.get("param_id")
            value = values.get(param_id)

            is_valid, error_msg = ParameterValidator.validate(param_def, value)
            if not is_valid:
                all_valid = False
                errors[param_id] = error_msg

        if all_valid:
            logger.info("All parameters validated successfully")
        else:
            logger.warning(f"Parameter validation failed with {len(errors)} errors")

        return all_valid, errors


class MeasurementValidator:
    """Validate measurement values against QC rules."""

    @staticmethod
    def validate_range(value: float, min_value: float, max_value: float) -> bool:
        """
        Validate value is within range.

        Args:
            value: Value to check
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value

        Returns:
            True if value is in range
        """
        return min_value <= value <= max_value

    @staticmethod
    def detect_outliers(
        values: list[float], method: str = "iqr", threshold: float = 1.5
    ) -> list[int]:
        """
        Detect outliers in a list of values.

        Args:
            values: List of numeric values
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection

        Returns:
            List of indices of outlier values
        """
        if not values or len(values) < 4:
            return []

        import numpy as np

        outliers = []

        if method == "iqr":
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            outliers = [
                i
                for i, v in enumerate(values)
                if v < lower_bound or v > upper_bound
            ]

        elif method == "zscore":
            mean = np.mean(values)
            std = np.std(values)

            if std > 0:
                outliers = [
                    i
                    for i, v in enumerate(values)
                    if abs((v - mean) / std) > threshold
                ]

        logger.info(f"Detected {len(outliers)} outliers using {method} method")
        return outliers

    @staticmethod
    def validate_qc_rule(
        rule: Dict[str, Any], value: float, all_values: list[float] = None
    ) -> Tuple[bool, str]:
        """
        Validate a value against a QC rule.

        Args:
            rule: QC rule definition
            value: Value to check
            all_values: All values (for outlier detection)

        Returns:
            Tuple of (passes_qc, message)
        """
        rule_type = rule.get("type")

        if rule_type == "range":
            min_val = rule.get("min_value", float("-inf"))
            max_val = rule.get("max_value", float("inf"))

            if not MeasurementValidator.validate_range(value, min_val, max_val):
                msg = (
                    f"{rule.get('description', 'Value')} out of range: "
                    f"{value} not in [{min_val}, {max_val}]"
                )
                logger.warning(msg)
                return False, msg

        elif rule_type == "outlier" and all_values:
            method = rule.get("method", "iqr")
            threshold = rule.get("threshold", 1.5)

            outliers = MeasurementValidator.detect_outliers(
                all_values, method, threshold
            )
            value_index = len(all_values) - 1  # Assume checking latest value

            if value_index in outliers:
                msg = f"{rule.get('description', 'Value')} is an outlier: {value}"
                logger.warning(msg)
                return False, msg

        return True, ""
