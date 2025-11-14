"""Data formatting utilities."""

from typing import Optional, Union
import numpy as np


def format_percentage(
    value: Union[int, float],
    decimals: int = 2,
    include_sign: bool = False
) -> str:
    """
    Format a value as a percentage.

    Args:
        value: The value to format (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        include_sign: Whether to include '+' for positive values

    Returns:
        Formatted percentage string
    """
    if np.isnan(value):
        return "N/A"

    percentage = value * 100 if abs(value) < 1.5 else value

    if include_sign and percentage > 0:
        return f"+{percentage:.{decimals}f}%"
    return f"{percentage:.{decimals}f}%"


def format_scientific(
    value: Union[int, float],
    decimals: int = 3,
    threshold: float = 1000.0
) -> str:
    """
    Format a value in scientific notation if it exceeds threshold.

    Args:
        value: The value to format
        decimals: Number of decimal places
        threshold: Threshold for switching to scientific notation

    Returns:
        Formatted string
    """
    if np.isnan(value):
        return "N/A"

    if abs(value) >= threshold or (value != 0 and abs(value) < 0.01):
        return f"{value:.{decimals}e}"
    return f"{value:.{decimals}f}"


def format_measurement(
    value: Union[int, float],
    unit: str,
    decimals: int = 3,
    uncertainty: Optional[float] = None
) -> str:
    """
    Format a measurement with units and optional uncertainty.

    Args:
        value: The measurement value
        unit: The unit of measurement
        decimals: Number of decimal places
        uncertainty: Optional uncertainty value

    Returns:
        Formatted measurement string
    """
    if np.isnan(value):
        return f"N/A {unit}"

    if uncertainty is not None and not np.isnan(uncertainty):
        return f"{value:.{decimals}f} ± {uncertainty:.{decimals}f} {unit}"

    return f"{value:.{decimals}f} {unit}"


def format_duration(hours: float) -> str:
    """
    Format a duration in hours to a human-readable string.

    Args:
        hours: Duration in hours

    Returns:
        Formatted duration string
    """
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} min"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = hours / 24
        return f"{days:.1f} days"
