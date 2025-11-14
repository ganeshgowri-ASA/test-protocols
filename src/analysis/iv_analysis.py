"""
IV Curve Analysis for Photovoltaic Cells

Provides analysis tools for current-voltage (IV) characteristics of PV cells.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class IVAnalyzer:
    """
    Analyzer for PV cell IV curves.

    Extracts key parameters from IV measurements and tracks degradation.
    """

    def __init__(self):
        """Initialize IV analyzer."""
        pass

    def analyze_iv_curve(self, voltage: np.ndarray,
                        current: np.ndarray,
                        irradiance: float = 1000.0,
                        temperature: float = 25.0,
                        cell_area: float = 243.36) -> Dict[str, float]:
        """
        Analyze IV curve and extract parameters.

        Args:
            voltage: Voltage values (V)
            current: Current values (A)
            irradiance: Irradiance level (W/m²)
            temperature: Cell temperature (°C)
            cell_area: Cell area (cm²)

        Returns:
            Dictionary of IV parameters
        """
        # Calculate power
        power = voltage * current

        # Find maximum power point
        max_power_idx = np.argmax(power)
        pmax = power[max_power_idx]
        vmp = voltage[max_power_idx]
        imp = current[max_power_idx]

        # Find Voc (open circuit voltage) - where current crosses zero
        voc = self._find_voc(voltage, current)

        # Find Isc (short circuit current) - where voltage crosses zero
        isc = self._find_isc(voltage, current)

        # Calculate fill factor
        if voc > 0 and isc > 0:
            ff = pmax / (voc * isc)
        else:
            ff = 0.0

        # Calculate series and shunt resistance
        rs, rsh = self._calculate_resistances(voltage, current, vmp, imp)

        # Calculate efficiency
        if irradiance > 0 and cell_area > 0:
            efficiency = (pmax / (irradiance * cell_area / 10000)) * 100  # Convert cm² to m²
        else:
            efficiency = 0.0

        results = {
            'pmax': float(pmax),
            'vmp': float(vmp),
            'imp': float(imp),
            'voc': float(voc),
            'isc': float(isc),
            'ff': float(ff),
            'efficiency': float(efficiency),
            'rs': float(rs),
            'rsh': float(rsh),
            'irradiance': float(irradiance),
            'temperature': float(temperature)
        }

        return results

    def _find_voc(self, voltage: np.ndarray, current: np.ndarray) -> float:
        """Find open circuit voltage (Voc)."""
        # Find where current is closest to zero
        zero_crossing_idx = np.argmin(np.abs(current))
        return float(voltage[zero_crossing_idx])

    def _find_isc(self, voltage: np.ndarray, current: np.ndarray) -> float:
        """Find short circuit current (Isc)."""
        # Find where voltage is closest to zero
        zero_crossing_idx = np.argmin(np.abs(voltage))
        return float(current[zero_crossing_idx])

    def _calculate_resistances(self, voltage: np.ndarray, current: np.ndarray,
                               vmp: float, imp: float) -> Tuple[float, float]:
        """
        Calculate series and shunt resistances.

        Args:
            voltage: Voltage array
            current: Current array
            vmp: Voltage at maximum power
            imp: Current at maximum power

        Returns:
            Tuple of (Rs, Rsh) in Ohms
        """
        # Series resistance from slope near Voc
        voc_region = voltage > 0.9 * np.max(voltage)
        if np.any(voc_region):
            v_voc = voltage[voc_region]
            i_voc = current[voc_region]
            if len(v_voc) > 1:
                rs = -np.polyfit(i_voc, v_voc, 1)[0]
            else:
                rs = 0.0
        else:
            rs = 0.0

        # Shunt resistance from slope near Isc
        isc_region = voltage < 0.1 * np.max(voltage)
        if np.any(isc_region):
            v_isc = voltage[isc_region]
            i_isc = current[isc_region]
            if len(v_isc) > 1:
                rsh = np.polyfit(v_isc, i_isc, 1)[0]
                rsh = 1.0 / rsh if rsh != 0 else np.inf
            else:
                rsh = np.inf
        else:
            rsh = np.inf

        return max(0.0, rs), max(0.0, rsh)

    def compare_iv_curves(self, initial: Dict[str, float],
                         final: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Compare two IV curve measurements.

        Args:
            initial: Initial IV parameters
            final: Final IV parameters

        Returns:
            Dictionary of parameter changes
        """
        comparison = {}

        for param in ['pmax', 'voc', 'isc', 'ff', 'efficiency', 'rs', 'rsh']:
            if param in initial and param in final:
                initial_val = initial[param]
                final_val = final[param]

                absolute_change = final_val - initial_val

                if initial_val != 0:
                    relative_change = (absolute_change / initial_val) * 100
                else:
                    relative_change = 0.0

                comparison[param] = {
                    'initial': initial_val,
                    'final': final_val,
                    'absolute_change': absolute_change,
                    'relative_change': relative_change
                }

        return comparison

    def calculate_degradation_rate(self, measurements: List[Tuple[int, Dict[str, float]]],
                                  parameter: str = 'pmax') -> Dict[str, float]:
        """
        Calculate degradation rate from series of measurements.

        Args:
            measurements: List of (cycle, iv_parameters) tuples
            parameter: Parameter to analyze ('pmax', 'ff', etc.)

        Returns:
            Dictionary with degradation rate information
        """
        if len(measurements) < 2:
            return {
                'rate_per_cycle': 0.0,
                'rate_per_cycle_percent': 0.0,
                'total_degradation': 0.0,
                'total_degradation_percent': 0.0
            }

        # Sort by cycle number
        measurements = sorted(measurements, key=lambda x: x[0])

        cycles = np.array([m[0] for m in measurements])
        values = np.array([m[1].get(parameter, 0) for m in measurements])

        # Linear fit
        if len(cycles) > 1:
            coeffs = np.polyfit(cycles, values, 1)
            rate = coeffs[0]  # Change per cycle
        else:
            rate = 0.0

        initial_value = values[0]
        final_value = values[-1]
        total_degradation = final_value - initial_value

        if initial_value != 0:
            rate_percent = (rate / initial_value) * 100
            total_degradation_percent = (total_degradation / initial_value) * 100
        else:
            rate_percent = 0.0
            total_degradation_percent = 0.0

        return {
            'rate_per_cycle': float(rate),
            'rate_per_cycle_percent': float(rate_percent),
            'total_degradation': float(total_degradation),
            'total_degradation_percent': float(total_degradation_percent),
            'initial_value': float(initial_value),
            'final_value': float(final_value),
            'cycles': int(cycles[-1])
        }

    def temperature_correct(self, iv_params: Dict[str, float],
                          measured_temp: float,
                          target_temp: float = 25.0,
                          alpha_isc: float = 0.0005,
                          beta_voc: float = -0.0023) -> Dict[str, float]:
        """
        Temperature-correct IV parameters to standard conditions.

        Args:
            iv_params: Measured IV parameters
            measured_temp: Temperature during measurement (°C)
            target_temp: Target temperature for correction (°C)
            alpha_isc: Temperature coefficient for Isc (1/°C)
            beta_voc: Temperature coefficient for Voc (1/°C)

        Returns:
            Temperature-corrected IV parameters
        """
        temp_diff = target_temp - measured_temp

        corrected = iv_params.copy()

        # Correct Isc
        if 'isc' in corrected:
            corrected['isc'] = iv_params['isc'] * (1 + alpha_isc * temp_diff)

        # Correct Voc
        if 'voc' in corrected:
            corrected['voc'] = iv_params['voc'] * (1 + beta_voc * temp_diff)

        # Recalculate dependent parameters
        if 'pmax' in corrected and 'ff' in corrected:
            corrected['pmax'] = corrected['voc'] * corrected['isc'] * corrected['ff']

        return corrected


class IVCurveSimulator:
    """Simulate IV curves for testing purposes."""

    @staticmethod
    def generate_ideal_curve(voc: float, isc: float, points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ideal IV curve.

        Args:
            voc: Open circuit voltage (V)
            isc: Short circuit current (A)
            points: Number of points in curve

        Returns:
            Tuple of (voltage, current) arrays
        """
        voltage = np.linspace(0, voc, points)
        # Simple exponential model
        current = isc * (1 - np.exp((voltage - voc) / (voc / 10)))
        current = np.maximum(current, 0)  # Ensure non-negative

        return voltage, current

    @staticmethod
    def add_degradation(voltage: np.ndarray, current: np.ndarray,
                       pmax_loss: float = 0.05,
                       ff_loss: float = 0.02) -> Tuple[np.ndarray, np.ndarray]:
        """
        Add degradation effects to IV curve.

        Args:
            voltage: Voltage array
            current: Current array
            pmax_loss: Fraction of power loss (0-1)
            ff_loss: Fraction of fill factor loss (0-1)

        Returns:
            Degraded (voltage, current) arrays
        """
        # Reduce current (simulates series resistance increase)
        degraded_current = current * (1 - pmax_loss)

        # Modify curve shape (simulates fill factor degradation)
        if ff_loss > 0:
            degraded_current = degraded_current * (1 - ff_loss * (voltage / np.max(voltage)))

        return voltage, degraded_current
