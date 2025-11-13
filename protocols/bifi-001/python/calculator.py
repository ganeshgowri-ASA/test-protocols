"""
Performance calculations for BIFI-001 Bifacial Performance Protocol
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IVParameters:
    """I-V curve characteristic parameters"""
    isc: float  # Short-circuit current (A)
    voc: float  # Open-circuit voltage (V)
    pmax: float  # Maximum power (W)
    imp: float  # Current at maximum power (A)
    vmp: float  # Voltage at maximum power (V)
    fill_factor: float  # Fill factor
    efficiency: Optional[float] = None  # Conversion efficiency (%)


class BifacialCalculator:
    """Calculate bifacial performance parameters according to IEC 60904-1-2"""

    @staticmethod
    def calculate_iv_parameters(iv_curve: List[Dict], area: float = None,
                                irradiance: float = 1000) -> IVParameters:
        """
        Calculate I-V curve parameters from measurement data

        Args:
            iv_curve: List of voltage-current measurement points
            area: Active area in cm² (for efficiency calculation)
            irradiance: Irradiance in W/m² (for efficiency calculation)

        Returns:
            IVParameters object with calculated values
        """
        if not iv_curve or len(iv_curve) < 2:
            raise ValueError("Insufficient I-V curve data points")

        # Extract voltage and current arrays
        voltages = np.array([point["voltage"] for point in iv_curve])
        currents = np.array([point["current"] for point in iv_curve])

        # Calculate power
        power = voltages * currents

        # Find maximum power point
        pmax_idx = np.argmax(power)
        pmax = power[pmax_idx]
        vmp = voltages[pmax_idx]
        imp = currents[pmax_idx]

        # Find Isc (current at V=0)
        # Interpolate if exact V=0 not present
        if 0 in voltages:
            isc = currents[voltages == 0][0]
        else:
            isc = np.interp(0, voltages, currents)

        # Find Voc (voltage at I=0)
        # Interpolate if exact I=0 not present
        if 0 in currents:
            voc = voltages[currents == 0][0]
        else:
            # For Voc, we need to extrapolate/interpolate near I=0
            # Find the crossing point
            if currents[0] > 0 and currents[-1] < 0:
                voc = np.interp(0, currents[::-1], voltages[::-1])
            else:
                # Use the maximum voltage where current is closest to zero
                voc = voltages[np.argmin(np.abs(currents))]

        # Calculate fill factor
        if isc > 0 and voc > 0:
            fill_factor = pmax / (isc * voc)
        else:
            fill_factor = 0

        # Calculate efficiency if area and irradiance provided
        efficiency = None
        if area is not None and irradiance > 0:
            # Convert area from cm² to m²
            area_m2 = area / 10000
            incident_power = irradiance * area_m2
            if incident_power > 0:
                efficiency = (pmax / incident_power) * 100

        return IVParameters(
            isc=float(isc),
            voc=float(voc),
            pmax=float(pmax),
            imp=float(imp),
            vmp=float(vmp),
            fill_factor=float(fill_factor),
            efficiency=float(efficiency) if efficiency is not None else None
        )

    @staticmethod
    def calculate_bifaciality(front_pmax: float, rear_pmax: float) -> float:
        """
        Calculate bifaciality factor

        Args:
            front_pmax: Maximum power from front side (W)
            rear_pmax: Maximum power from rear side (W)

        Returns:
            Bifaciality factor (0-1)
        """
        if front_pmax <= 0:
            return 0
        return rear_pmax / front_pmax

    @staticmethod
    def calculate_bifacial_gain(front_pmax: float, rear_pmax: float,
                                front_irradiance: float, rear_irradiance: float) -> float:
        """
        Calculate bifacial gain percentage

        Args:
            front_pmax: Maximum power from front side (W)
            rear_pmax: Maximum power from rear side (W)
            front_irradiance: Front side irradiance (W/m²)
            rear_irradiance: Rear side irradiance (W/m²)

        Returns:
            Bifacial gain as percentage
        """
        if front_irradiance <= 0:
            return 0

        # Normalize rear contribution to equivalent front irradiance
        rear_contribution = rear_pmax * (front_irradiance / rear_irradiance) if rear_irradiance > 0 else 0

        if front_pmax > 0:
            gain = (rear_contribution / front_pmax) * 100
            return gain
        return 0

    @staticmethod
    def calculate_equivalent_efficiency(front_params: IVParameters, rear_params: IVParameters,
                                       front_irradiance: float, rear_irradiance: float,
                                       area: float) -> float:
        """
        Calculate equivalent front-side efficiency accounting for bifacial contribution

        Args:
            front_params: Front side I-V parameters
            rear_params: Rear side I-V parameters
            front_irradiance: Front side irradiance (W/m²)
            rear_irradiance: Rear side irradiance (W/m²)
            area: Active area in cm²

        Returns:
            Equivalent efficiency in %
        """
        total_power = front_params.pmax + rear_params.pmax
        total_irradiance = front_irradiance + rear_irradiance

        area_m2 = area / 10000
        incident_power = total_irradiance * area_m2

        if incident_power > 0:
            return (total_power / incident_power) * 100
        return 0

    @staticmethod
    def calculate_temperature_coefficients(measurements: List[Tuple[float, IVParameters]]) -> Dict[str, float]:
        """
        Calculate temperature coefficients from multiple measurements

        Args:
            measurements: List of (temperature, IVParameters) tuples

        Returns:
            Dictionary with temperature coefficients (%/°C)
        """
        if len(measurements) < 2:
            raise ValueError("Need at least 2 measurements at different temperatures")

        temps = np.array([m[0] for m in measurements])
        voc_values = np.array([m[1].voc for m in measurements])
        isc_values = np.array([m[1].isc for m in measurements])
        pmax_values = np.array([m[1].pmax for m in measurements])

        # Linear regression to find coefficients
        voc_coeff = np.polyfit(temps, voc_values, 1)[0]
        isc_coeff = np.polyfit(temps, isc_values, 1)[0]
        pmax_coeff = np.polyfit(temps, pmax_values, 1)[0]

        # Normalize to percentage per degree
        voc_ref = voc_values[0]
        isc_ref = isc_values[0]
        pmax_ref = pmax_values[0]

        return {
            "voc_temp_coeff": (voc_coeff / voc_ref * 100) if voc_ref > 0 else 0,
            "isc_temp_coeff": (isc_coeff / isc_ref * 100) if isc_ref > 0 else 0,
            "pmax_temp_coeff": (pmax_coeff / pmax_ref * 100) if pmax_ref > 0 else 0
        }

    @staticmethod
    def calculate_uncertainty(measurements: Dict, reference_uncertainty: float = 2.0) -> Dict[str, float]:
        """
        Calculate measurement uncertainty according to IEC standards

        Args:
            measurements: Measurement data dictionary
            reference_uncertainty: Reference cell calibration uncertainty (%)

        Returns:
            Dictionary with uncertainty values
        """
        # Type A uncertainty (statistical)
        # For single measurement, use typical instrument uncertainty
        instrument_uncertainty = 1.0  # %

        # Type B uncertainty (systematic)
        # Includes reference cell, temperature, spectral mismatch, etc.
        spectral_mismatch = 1.0  # %
        temperature_uncertainty = 0.5  # %
        non_uniformity = 1.0  # %

        # Combined uncertainty (root sum of squares)
        front_uncertainty = np.sqrt(
            reference_uncertainty**2 +
            instrument_uncertainty**2 +
            spectral_mismatch**2 +
            temperature_uncertainty**2 +
            non_uniformity**2
        )

        # Rear side typically has higher uncertainty due to measurement complexity
        rear_uncertainty = front_uncertainty * 1.2

        # Bifacial measurements combine both uncertainties
        combined_uncertainty = np.sqrt(front_uncertainty**2 + rear_uncertainty**2)

        return {
            "front_pmax_uncertainty": round(front_uncertainty, 2),
            "rear_pmax_uncertainty": round(rear_uncertainty, 2),
            "combined_uncertainty": round(combined_uncertainty, 2)
        }

    @staticmethod
    def smooth_iv_curve(iv_curve: List[Dict], window_size: int = 5) -> List[Dict]:
        """
        Apply moving average smoothing to I-V curve data

        Args:
            iv_curve: Raw I-V curve data
            window_size: Size of moving average window

        Returns:
            Smoothed I-V curve data
        """
        if len(iv_curve) < window_size:
            return iv_curve

        voltages = np.array([point["voltage"] for point in iv_curve])
        currents = np.array([point["current"] for point in iv_curve])

        # Apply moving average to current values (voltage is independent variable)
        smoothed_currents = np.convolve(currents, np.ones(window_size)/window_size, mode='valid')

        # Adjust voltage array to match smoothed data length
        offset = (len(currents) - len(smoothed_currents)) // 2
        smoothed_voltages = voltages[offset:offset+len(smoothed_currents)]

        smoothed_curve = []
        for v, i in zip(smoothed_voltages, smoothed_currents):
            point = {"voltage": float(v), "current": float(i)}
            # Preserve timestamp if present
            if "timestamp" in iv_curve[0]:
                point["timestamp"] = iv_curve[0]["timestamp"]
            smoothed_curve.append(point)

        return smoothed_curve

    @staticmethod
    def interpolate_to_stc(params: IVParameters, measured_irradiance: float,
                          measured_temp: float, temp_coeffs: Dict[str, float] = None) -> IVParameters:
        """
        Interpolate measurements to Standard Test Conditions (STC)

        Args:
            params: Measured I-V parameters
            measured_irradiance: Measured irradiance (W/m²)
            measured_temp: Measured temperature (°C)
            temp_coeffs: Temperature coefficients dictionary

        Returns:
            I-V parameters corrected to STC (1000 W/m², 25°C)
        """
        # Default temperature coefficients if not provided
        if temp_coeffs is None:
            temp_coeffs = {
                "voc_temp_coeff": -0.35,  # %/°C (typical for Si)
                "isc_temp_coeff": 0.05,   # %/°C (typical for Si)
                "pmax_temp_coeff": -0.45  # %/°C (typical for Si)
            }

        # Temperature correction
        delta_t = 25 - measured_temp

        voc_stc = params.voc * (1 + temp_coeffs["voc_temp_coeff"] * delta_t / 100)
        isc_stc = params.isc * (1 + temp_coeffs["isc_temp_coeff"] * delta_t / 100)

        # Irradiance correction
        irr_factor = 1000 / measured_irradiance if measured_irradiance > 0 else 1
        isc_stc *= irr_factor

        # Adjust power and current at MPP
        temp_factor = 1 + temp_coeffs["pmax_temp_coeff"] * delta_t / 100
        pmax_stc = params.pmax * temp_factor * irr_factor

        # Recalculate MPP current and voltage
        # Assume FF remains relatively constant
        ff_stc = params.fill_factor
        imp_stc = pmax_stc / params.vmp if params.vmp > 0 else 0
        vmp_stc = pmax_stc / params.imp if params.imp > 0 else 0

        return IVParameters(
            isc=isc_stc,
            voc=voc_stc,
            pmax=pmax_stc,
            imp=imp_stc,
            vmp=vmp_stc,
            fill_factor=ff_stc,
            efficiency=params.efficiency
        )
