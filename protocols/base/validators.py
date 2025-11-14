"""Common validation functions for test protocols"""

from typing import Any, List, Optional, Union
import re
from datetime import datetime


class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass


def validate_range(
    name: str,
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None
) -> None:
    """
    Validate that a value is within a specified range.

    Args:
        name: Name of the parameter being validated
        value: Value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Raises:
        ValidationError: If value is out of range
    """
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{name} must be >= {min_value}, got {value}"
        )
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{name} must be <= {max_value}, got {value}"
        )


def validate_positive(name: str, value: Union[int, float]) -> None:
    """
    Validate that a value is positive.

    Args:
        name: Name of the parameter being validated
        value: Value to validate

    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")


def validate_non_negative(name: str, value: Union[int, float]) -> None:
    """
    Validate that a value is non-negative.

    Args:
        name: Name of the parameter being validated
        value: Value to validate

    Raises:
        ValidationError: If value is negative
    """
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")


def validate_required(name: str, value: Any) -> None:
    """
    Validate that a required value is provided.

    Args:
        name: Name of the parameter being validated
        value: Value to validate

    Raises:
        ValidationError: If value is None or empty
    """
    if value is None:
        raise ValidationError(f"{name} is required")
    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{name} cannot be empty")
    if isinstance(value, (list, dict)) and not value:
        raise ValidationError(f"{name} cannot be empty")


def validate_enum(name: str, value: Any, allowed_values: List[Any]) -> None:
    """
    Validate that a value is one of the allowed values.

    Args:
        name: Name of the parameter being validated
        value: Value to validate
        allowed_values: List of allowed values

    Raises:
        ValidationError: If value is not in allowed values
    """
    if value not in allowed_values:
        raise ValidationError(
            f"{name} must be one of {allowed_values}, got {value}"
        )


def validate_pattern(name: str, value: str, pattern: str) -> None:
    """
    Validate that a string matches a regex pattern.

    Args:
        name: Name of the parameter being validated
        value: String to validate
        pattern: Regex pattern to match

    Raises:
        ValidationError: If value doesn't match pattern
    """
    if not re.match(pattern, value):
        raise ValidationError(
            f"{name} must match pattern '{pattern}', got '{value}'"
        )


def validate_measurement(
    measurement_type: str,
    value: float,
    unit: str,
    expected_unit: Optional[str] = None
) -> None:
    """
    Validate a measurement value and unit.

    Args:
        measurement_type: Type of measurement
        value: Measured value
        unit: Unit of measurement
        expected_unit: Expected unit (optional)

    Raises:
        ValidationError: If measurement is invalid
    """
    validate_required("measurement_type", measurement_type)
    validate_required("unit", unit)

    if expected_unit and unit != expected_unit:
        raise ValidationError(
            f"Expected unit '{expected_unit}' for {measurement_type}, got '{unit}'"
        )


def validate_date(name: str, date_str: str) -> datetime:
    """
    Validate and parse a date string.

    Args:
        name: Name of the parameter being validated
        date_str: Date string in ISO format

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValidationError: If date is invalid
    """
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        raise ValidationError(
            f"{name} must be a valid ISO date string, got '{date_str}': {e}"
        )


def validate_protocol_id(protocol_id: str) -> None:
    """
    Validate protocol ID format.

    Args:
        protocol_id: Protocol ID to validate

    Raises:
        ValidationError: If protocol ID is invalid
    """
    validate_pattern(
        "protocol_id",
        protocol_id,
        r"^[A-Z]{2,4}-\d{3,4}$"
    )


def validate_version(version: str) -> None:
    """
    Validate semantic version format.

    Args:
        version: Version string to validate

    Raises:
        ValidationError: If version is invalid
    """
    validate_pattern(
        "version",
        version,
        r"^\d+\.\d+\.\d+$"
    )
