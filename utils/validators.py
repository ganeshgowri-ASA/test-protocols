"""Data validation utilities."""

from datetime import datetime
from typing import Any, Dict, Optional, Union
import numpy as np


def validate_measurement(
    value: Union[int, float],
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_negative: bool = True,
    allow_nan: bool = False
) -> bool:
    """
    Validate a measurement value against specified criteria.

    Args:
        value: The measurement value to validate
        min_value: Minimum acceptable value
        max_value: Maximum acceptable value
        allow_negative: Whether negative values are allowed
        allow_nan: Whether NaN values are allowed

    Returns:
        True if validation passes, False otherwise
    """
    # Check for NaN
    if np.isnan(value):
        return allow_nan

    # Check for infinite values
    if np.isinf(value):
        return False

    # Check negative values
    if not allow_negative and value < 0:
        return False

    # Check range
    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True


def validate_timestamp(
    timestamp: Union[str, datetime],
    allow_future: bool = False,
    max_age_days: Optional[int] = None
) -> bool:
    """
    Validate a timestamp.

    Args:
        timestamp: The timestamp to validate (string or datetime object)
        allow_future: Whether future timestamps are allowed
        max_age_days: Maximum age of timestamp in days

    Returns:
        True if validation passes, False otherwise
    """
    try:
        # Convert string to datetime if needed
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()

        # Check future timestamps
        if not allow_future and dt > now:
            return False

        # Check maximum age
        if max_age_days is not None:
            age_days = (now - dt).days
            if age_days > max_age_days:
                return False

        return True

    except (ValueError, AttributeError):
        return False


def validate_protocol_data(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate protocol data against a schema.

    Args:
        data: The data to validate
        schema: The schema to validate against

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check field types and ranges
    properties = schema.get('properties', {})
    for field, value in data.items():
        if field in properties:
            field_schema = properties[field]

            # Type validation
            expected_type = field_schema.get('type')
            if expected_type:
                if expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' must be a number")
                elif expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field '{field}' must be a string")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Field '{field}' must be an array")

            # Range validation for numbers
            if isinstance(value, (int, float)):
                if 'minimum' in field_schema and value < field_schema['minimum']:
                    errors.append(
                        f"Field '{field}' value {value} is below minimum {field_schema['minimum']}"
                    )
                if 'maximum' in field_schema and value > field_schema['maximum']:
                    errors.append(
                        f"Field '{field}' value {value} exceeds maximum {field_schema['maximum']}"
                    )

    return len(errors) == 0, errors


def validate_environmental_conditions(
    irradiance: float,
    temperature: float,
    config: Dict[str, Any]
) -> tuple[bool, list[str]]:
    """
    Validate environmental test conditions.

    Args:
        irradiance: Irradiance in W/m²
        temperature: Temperature in °C
        config: Configuration with nominal values and tolerances

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    env_config = config.get('environmental_conditions', {})

    # Validate irradiance
    irr_config = env_config.get('irradiance', {})
    nominal_irr = irr_config.get('nominal', 1000.0)
    tolerance_irr = irr_config.get('tolerance', 2.0)
    min_irr = nominal_irr * (1 - tolerance_irr / 100)
    max_irr = nominal_irr * (1 + tolerance_irr / 100)

    if not (min_irr <= irradiance <= max_irr):
        errors.append(
            f"Irradiance {irradiance} W/m² outside acceptable range "
            f"[{min_irr:.1f}, {max_irr:.1f}] W/m²"
        )

    # Validate temperature
    temp_config = env_config.get('temperature', {})
    nominal_temp = temp_config.get('nominal', 25.0)
    tolerance_temp = temp_config.get('tolerance', 2.0)
    min_temp = nominal_temp - tolerance_temp
    max_temp = nominal_temp + tolerance_temp

    if not (min_temp <= temperature <= max_temp):
        errors.append(
            f"Temperature {temperature}°C outside acceptable range "
            f"[{min_temp:.1f}, {max_temp:.1f}]°C"
        )

    return len(errors) == 0, errors
