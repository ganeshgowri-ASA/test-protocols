"""
Utility functions for PV testing protocols
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List
import uuid


def generate_run_id(protocol_id: str, sample_id: str) -> str:
    """
    Generate a unique run ID for a test

    Format: {PROTOCOL}_{SAMPLE}_{TIMESTAMP}_{SHORT_UUID}
    Example: LIC-001_SAMPLE123_20231115T143022_a3f9
    """
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{protocol_id}_{sample_id}_{timestamp}_{short_uuid}"


def calculate_hash(data: Dict[str, Any]) -> str:
    """
    Calculate SHA256 hash of data for traceability

    Args:
        data: Dictionary to hash

    Returns:
        Hexadecimal hash string
    """
    # Convert to JSON string with sorted keys for consistency
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()


def format_scientific(value: float, precision: int = 3) -> str:
    """Format a number in scientific notation"""
    return f"{value:.{precision}e}"


def format_percentage(value: float, precision: int = 2) -> str:
    """Format a number as percentage"""
    return f"{value:.{precision}f}%"


def calculate_fill_factor(voc: float, isc: float, pmax: float) -> float:
    """
    Calculate Fill Factor (FF) of a solar cell

    FF = Pmax / (Voc * Isc)

    Args:
        voc: Open circuit voltage (V)
        isc: Short circuit current (A)
        pmax: Maximum power (W)

    Returns:
        Fill factor (0-1)
    """
    if voc <= 0 or isc <= 0:
        return 0.0

    return pmax / (voc * isc)


def calculate_efficiency(
    pmax: float,
    irradiance: float,
    area: float
) -> float:
    """
    Calculate solar cell efficiency

    η = Pmax / (Irradiance * Area)

    Args:
        pmax: Maximum power (W)
        irradiance: Irradiance (W/m²)
        area: Cell area (m²)

    Returns:
        Efficiency (0-1)
    """
    if irradiance <= 0 or area <= 0:
        return 0.0

    return pmax / (irradiance * area)


def find_max_power_point(voltage: List[float], current: List[float]) -> Dict[str, float]:
    """
    Find the maximum power point from I-V curve data

    Args:
        voltage: List of voltage values (V)
        current: List of current values (A)

    Returns:
        Dictionary with Vmp, Imp, and Pmax
    """
    if len(voltage) != len(current) or len(voltage) == 0:
        return {"vmp": 0.0, "imp": 0.0, "pmax": 0.0}

    # Calculate power at each point
    power = [v * i for v, i in zip(voltage, current)]

    # Find maximum power point
    max_idx = power.index(max(power))

    return {
        "vmp": voltage[max_idx],
        "imp": current[max_idx],
        "pmax": power[max_idx]
    }


def interpolate_value(
    x: float,
    x_data: List[float],
    y_data: List[float]
) -> float:
    """
    Linear interpolation

    Args:
        x: Value to interpolate at
        x_data: Known x values (must be sorted)
        y_data: Known y values

    Returns:
        Interpolated y value
    """
    if len(x_data) != len(y_data) or len(x_data) == 0:
        return 0.0

    # Handle edge cases
    if x <= x_data[0]:
        return y_data[0]
    if x >= x_data[-1]:
        return y_data[-1]

    # Find surrounding points
    for i in range(len(x_data) - 1):
        if x_data[i] <= x <= x_data[i + 1]:
            # Linear interpolation
            slope = (y_data[i + 1] - y_data[i]) / (x_data[i + 1] - x_data[i])
            return y_data[i] + slope * (x - x_data[i])

    return 0.0


def temperature_correction(
    value: float,
    measured_temp: float,
    target_temp: float,
    temp_coefficient: float
) -> float:
    """
    Apply temperature correction to a measurement

    Corrected_Value = Measured_Value * (1 + α * ΔT)

    Args:
        value: Measured value
        measured_temp: Temperature at measurement (°C)
        target_temp: Target temperature (°C)
        temp_coefficient: Temperature coefficient (%/°C)

    Returns:
        Temperature-corrected value
    """
    delta_t = target_temp - measured_temp
    correction_factor = 1 + (temp_coefficient / 100) * delta_t
    return value * correction_factor


def irradiance_correction(
    value: float,
    measured_irradiance: float,
    target_irradiance: float
) -> float:
    """
    Apply irradiance correction to a measurement (linear scaling)

    Corrected_Value = Measured_Value * (Target_Irr / Measured_Irr)

    Args:
        value: Measured value
        measured_irradiance: Irradiance at measurement (W/m²)
        target_irradiance: Target irradiance (W/m²)

    Returns:
        Irradiance-corrected value
    """
    if measured_irradiance <= 0:
        return 0.0

    return value * (target_irradiance / measured_irradiance)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate statistical measures for a list of values

    Returns:
        Dictionary with mean, std, min, max, median
    """
    if not values:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0
        }

    import statistics

    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "median": statistics.median(values)
    }


def check_data_quality(
    measured_value: float,
    expected_value: float,
    tolerance: float
) -> tuple[bool, str]:
    """
    Check if a measurement is within acceptable tolerance

    Args:
        measured_value: Measured value
        expected_value: Expected value
        tolerance: Acceptable deviation (as fraction, e.g., 0.05 for 5%)

    Returns:
        (is_acceptable, message)
    """
    if expected_value == 0:
        return True, "Expected value is zero, skipping check"

    deviation = abs(measured_value - expected_value) / abs(expected_value)

    if deviation <= tolerance:
        return True, f"Within tolerance ({deviation:.1%} deviation)"
    else:
        return False, f"Outside tolerance ({deviation:.1%} deviation, limit is {tolerance:.1%})"


def format_test_conditions(conditions: Dict[str, Any]) -> str:
    """
    Format test conditions as a readable string

    Args:
        conditions: Dictionary of test conditions

    Returns:
        Formatted string
    """
    lines = []
    for key, value in conditions.items():
        if isinstance(value, float):
            lines.append(f"{key}: {value:.2f}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)
