"""Common calculation functions for PV test protocols."""

from typing import Optional, Tuple
import numpy as np


def calculate_fill_factor(voc: float, isc: float, pmax: float) -> float:
    """
    Calculate fill factor.

    Args:
        voc: Open-circuit voltage (V)
        isc: Short-circuit current (A)
        pmax: Maximum power (W)

    Returns:
        Fill factor (dimensionless)
    """
    if voc <= 0 or isc <= 0:
        return 0.0

    ff = pmax / (voc * isc)
    return ff


def calculate_efficiency(
    pmax: float,
    area: float,
    irradiance: float = 1000.0
) -> float:
    """
    Calculate module efficiency.

    Args:
        pmax: Maximum power (W)
        area: Module area (m²)
        irradiance: Solar irradiance (W/m²), default 1000

    Returns:
        Efficiency (%)
    """
    if area <= 0 or irradiance <= 0:
        return 0.0

    efficiency = 100 * pmax / (irradiance * area)
    return efficiency


def normalize_to_stc(
    pmax: float,
    irradiance: float,
    temperature: float,
    temp_coefficient: float = -0.4
) -> float:
    """
    Normalize power measurement to Standard Test Conditions (STC).

    STC: 1000 W/m², 25°C, AM1.5G spectrum

    Args:
        pmax: Measured maximum power (W)
        irradiance: Measured irradiance (W/m²)
        temperature: Measured cell temperature (°C)
        temp_coefficient: Temperature coefficient of power (%/°C), default -0.4

    Returns:
        Power normalized to STC (W)
    """
    # Normalize for irradiance
    pmax_normalized_irr = pmax * (1000.0 / irradiance)

    # Normalize for temperature
    temp_diff = temperature - 25.0
    temp_correction = 1 + (temp_coefficient / 100) * temp_diff
    pmax_stc = pmax_normalized_irr / temp_correction

    return pmax_stc


def calculate_series_resistance(
    vmp: float,
    imp: float,
    voc: float,
    isc: float,
    pmax: float,
    temperature: float = 25.0
) -> float:
    """
    Estimate series resistance using the simplified method.

    Args:
        vmp: Voltage at maximum power (V)
        imp: Current at maximum power (A)
        voc: Open-circuit voltage (V)
        isc: Short-circuit current (A)
        pmax: Maximum power (W)
        temperature: Cell temperature (°C)

    Returns:
        Series resistance estimate (Ω)
    """
    # Thermal voltage at temperature
    k = 1.380649e-23  # Boltzmann constant
    q = 1.602176634e-19  # Elementary charge
    vt = k * (temperature + 273.15) / q

    # Simplified Rs calculation
    ff = calculate_fill_factor(voc, isc, pmax)
    ff0 = (voc / vt - np.log(voc / vt + 0.72)) / (voc / vt + 1)

    if ff0 > 0 and isc > 0:
        rs = (ff0 - ff) * voc / isc
        return max(0, rs)  # Ensure non-negative
    return 0.0


def calculate_shunt_resistance(
    voc: float,
    isc: float,
    dv_di_voc: Optional[float] = None
) -> float:
    """
    Estimate shunt resistance.

    Args:
        voc: Open-circuit voltage (V)
        isc: Short-circuit current (A)
        dv_di_voc: Slope dV/dI at Voc from I-V curve (optional)

    Returns:
        Shunt resistance estimate (Ω)
    """
    if dv_di_voc is not None:
        # Use slope from I-V curve if available
        return abs(dv_di_voc)
    else:
        # Simplified estimate
        if isc > 0:
            return voc / (isc * 0.01)  # Assume 1% shunt current
        return float('inf')


def calculate_degradation_rate(
    time_hours: np.ndarray,
    degradation_percent: np.ndarray,
    method: str = "linear"
) -> Tuple[float, float]:
    """
    Calculate degradation rate from time series data.

    Args:
        time_hours: Time points in hours
        degradation_percent: Degradation percentages
        method: Regression method ("linear" or "exponential")

    Returns:
        Tuple of (rate, r_squared)
        - For linear: rate in %/hour
        - For exponential: decay constant
    """
    if len(time_hours) < 2:
        return 0.0, 0.0

    if method == "linear":
        # Linear regression
        coeffs = np.polyfit(time_hours, degradation_percent, 1)
        rate = coeffs[0]  # %/hour

        # Calculate R²
        predicted = np.polyval(coeffs, time_hours)
        ss_res = np.sum((degradation_percent - predicted) ** 2)
        ss_tot = np.sum((degradation_percent - np.mean(degradation_percent)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    elif method == "exponential":
        # Exponential fit: y = a * (1 - exp(-b*t))
        # Linearize: ln(1 - y/a) = -b*t
        # For simplicity, use linear fit on log-transformed data
        try:
            log_deg = np.log(degradation_percent + 1)  # +1 to handle small values
            coeffs = np.polyfit(time_hours, log_deg, 1)
            rate = coeffs[0]
            r_squared = 0.0  # Simplified
        except:
            rate = 0.0
            r_squared = 0.0
    else:
        raise ValueError(f"Unknown method: {method}")

    return rate, r_squared


def detect_outliers(
    data: np.ndarray,
    method: str = "iqr",
    threshold: float = 1.5
) -> np.ndarray:
    """
    Detect outliers in data.

    Args:
        data: Data array
        method: Detection method ("iqr", "zscore", "mad")
        threshold: Threshold for outlier detection

    Returns:
        Boolean array indicating outliers (True = outlier)
    """
    if len(data) == 0:
        return np.array([], dtype=bool)

    if method == "iqr":
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return (data < lower) | (data > upper)

    elif method == "zscore":
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return np.zeros(len(data), dtype=bool)
        z_scores = np.abs((data - mean) / std)
        return z_scores > threshold

    elif method == "mad":
        # Median Absolute Deviation
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        if mad == 0:
            return np.zeros(len(data), dtype=bool)
        modified_z_scores = 0.6745 * (data - median) / mad
        return np.abs(modified_z_scores) > threshold

    else:
        raise ValueError(f"Unknown method: {method}")
