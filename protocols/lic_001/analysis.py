"""
Analysis module for LIC-001 protocol
"""

from typing import Dict, List, Any
import numpy as np
from core.utils import (
    find_max_power_point,
    calculate_fill_factor,
    calculate_efficiency,
    calculate_statistics
)


class LIC001Analyzer:
    """
    Analyzer for Low Irradiance Conditions test data
    """

    def analyze_iv_curve(
        self,
        voltage: List[float],
        current: List[float],
        irradiance: float,
        temperature: float,
        module_area: float
    ) -> Dict[str, Any]:
        """
        Analyze I-V curve and calculate key parameters

        Args:
            voltage: Voltage values (V)
            current: Current values (A)
            irradiance: Actual irradiance (W/m²)
            temperature: Actual temperature (°C)
            module_area: Module area (m²)

        Returns:
            Dictionary with calculated parameters
        """
        if not voltage or not current or len(voltage) != len(current):
            return self._empty_results()

        # Find Voc (last voltage value where current is near zero)
        voc = self._find_voc(voltage, current)

        # Find Isc (first current value where voltage is near zero)
        isc = self._find_isc(voltage, current)

        # Find maximum power point
        mpp = find_max_power_point(voltage, current)

        # Calculate fill factor
        ff = calculate_fill_factor(voc, isc, mpp["pmax"])

        # Calculate efficiency
        efficiency = calculate_efficiency(mpp["pmax"], irradiance, module_area) * 100  # Convert to %

        return {
            "pmax": mpp["pmax"],
            "vmp": mpp["vmp"],
            "imp": mpp["imp"],
            "voc": voc,
            "isc": isc,
            "fill_factor": ff,
            "efficiency": efficiency,
            "actual_irradiance": irradiance,
            "actual_temperature": temperature
        }

    def _find_voc(self, voltage: List[float], current: List[float]) -> float:
        """
        Find open circuit voltage (Voc)

        Voc is where current crosses zero (or is very close to zero)
        """
        if not voltage or not current:
            return 0.0

        # Find where current is closest to zero (in the positive voltage region)
        min_current_idx = 0
        min_current = abs(current[0])

        for i, curr in enumerate(current):
            if abs(curr) < min_current:
                min_current = abs(curr)
                min_current_idx = i

        # Use the voltage at that point, or interpolate
        if min_current < 0.001:  # Close enough to zero
            return voltage[min_current_idx]

        # Linear interpolation between points around zero crossing
        for i in range(len(current) - 1):
            if current[i] > 0 and current[i + 1] <= 0:
                # Interpolate
                slope = (current[i + 1] - current[i]) / (voltage[i + 1] - voltage[i])
                voc = voltage[i] - current[i] / slope
                return voc

        # Fallback: return maximum voltage
        return max(voltage)

    def _find_isc(self, voltage: List[float], current: List[float]) -> float:
        """
        Find short circuit current (Isc)

        Isc is the current when voltage is zero (or very close to zero)
        """
        if not voltage or not current:
            return 0.0

        # Find where voltage is closest to zero
        min_voltage_idx = 0
        min_voltage = abs(voltage[0])

        for i, volt in enumerate(voltage):
            if abs(volt) < min_voltage:
                min_voltage = abs(volt)
                min_voltage_idx = i

        # Use the current at that point, or interpolate
        if min_voltage < 0.01:  # Close enough to zero
            return current[min_voltage_idx]

        # Linear interpolation
        for i in range(len(voltage) - 1):
            if voltage[i] <= 0 and voltage[i + 1] > 0:
                # Interpolate
                slope = (current[i + 1] - current[i]) / (voltage[i + 1] - voltage[i])
                isc = current[i] - slope * voltage[i]
                return isc

        # Fallback: return first current value (usually close to Isc)
        return current[0]

    def _empty_results(self) -> Dict[str, Any]:
        """Return empty results structure"""
        return {
            "pmax": 0.0,
            "vmp": 0.0,
            "imp": 0.0,
            "voc": 0.0,
            "isc": 0.0,
            "fill_factor": 0.0,
            "efficiency": 0.0,
            "actual_irradiance": 0.0,
            "actual_temperature": 0.0
        }

    def assess_curve_quality(
        self,
        voltage: List[float],
        current: List[float]
    ) -> Dict[str, Any]:
        """
        Assess the quality of an I-V curve

        Checks:
        - Number of points
        - Monotonic voltage increase
        - Current behavior
        - Noise level
        - Coverage of full curve

        Returns:
            Quality assessment dictionary
        """
        quality = {
            "curve_quality": "good",
            "data_quality_score": 100.0,
            "issues": []
        }

        if not voltage or not current or len(voltage) != len(current):
            quality["curve_quality"] = "poor"
            quality["data_quality_score"] = 0.0
            quality["issues"].append("Invalid or missing data")
            return quality

        score = 100.0

        # Check number of points
        num_points = len(voltage)
        if num_points < 10:
            score -= 30
            quality["issues"].append(f"Too few points: {num_points} (minimum 10)")
        elif num_points < 20:
            score -= 10
            quality["issues"].append(f"Low number of points: {num_points} (recommended 50+)")

        # Check voltage monotonicity
        non_monotonic = sum(1 for i in range(len(voltage) - 1) if voltage[i] > voltage[i + 1])
        if non_monotonic > 0:
            score -= min(20, non_monotonic * 2)
            quality["issues"].append(f"Non-monotonic voltage ({non_monotonic} reversals)")

        # Check for NaN or Inf
        if any(not np.isfinite(v) for v in voltage) or any(not np.isfinite(i) for i in current):
            score -= 40
            quality["issues"].append("Contains NaN or Inf values")

        # Check current behavior (should be positive at low voltage, decrease to negative)
        if current[0] <= 0:
            score -= 15
            quality["issues"].append("Short circuit current should be positive")

        # Check noise level (standard deviation of power derivative)
        if num_points > 5:
            power = [v * i for v, i in zip(voltage, current)]
            power_diff = [power[i + 1] - power[i] for i in range(len(power) - 1)]
            noise = np.std(power_diff) if len(power_diff) > 1 else 0

            # Normalize by mean power
            mean_power = np.mean([abs(p) for p in power])
            if mean_power > 0:
                relative_noise = noise / mean_power
                if relative_noise > 0.1:
                    score -= min(20, relative_noise * 100)
                    quality["issues"].append(f"High noise level: {relative_noise:.2%}")

        # Determine quality rating
        score = max(0, min(100, score))
        quality["data_quality_score"] = score

        if score >= 90:
            quality["curve_quality"] = "excellent"
        elif score >= 75:
            quality["curve_quality"] = "good"
        elif score >= 60:
            quality["curve_quality"] = "acceptable"
        else:
            quality["curve_quality"] = "poor"

        return quality

    def compare_performance(
        self,
        results_by_irradiance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare performance across different irradiance levels

        Args:
            results_by_irradiance: Results dictionary by irradiance level

        Returns:
            Comparison analysis
        """
        comparison = {
            "linearity": {},
            "efficiency_variation": {},
            "fill_factor_variation": {}
        }

        if len(results_by_irradiance) < 2:
            return comparison

        irradiances = sorted([int(k) for k in results_by_irradiance.keys()])

        # Extract values
        pmaxs = [results_by_irradiance[str(irr)]["pmax"] for irr in irradiances]
        efficiencies = [results_by_irradiance[str(irr)]["efficiency"] for irr in irradiances]
        fill_factors = [results_by_irradiance[str(irr)]["fill_factor"] for irr in irradiances]

        # Analyze Pmax linearity with irradiance
        comparison["linearity"] = self._analyze_linearity(irradiances, pmaxs)

        # Efficiency variation
        comparison["efficiency_variation"] = calculate_statistics(efficiencies)

        # Fill factor variation
        comparison["fill_factor_variation"] = calculate_statistics(fill_factors)

        return comparison

    def _analyze_linearity(
        self,
        irradiances: List[float],
        powers: List[float]
    ) -> Dict[str, float]:
        """
        Analyze linearity between irradiance and power

        Returns:
            R² value and linearity assessment
        """
        if len(irradiances) < 2:
            return {"r_squared": 0.0, "linearity": "insufficient_data"}

        # Calculate R² for linear fit
        x = np.array(irradiances)
        y = np.array(powers)

        # Linear fit
        coeffs = np.polyfit(x, y, 1)
        y_fit = np.polyval(coeffs, x)

        # R² calculation
        ss_res = np.sum((y - y_fit) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Assess linearity
        if r_squared >= 0.99:
            linearity = "excellent"
        elif r_squared >= 0.95:
            linearity = "good"
        elif r_squared >= 0.90:
            linearity = "acceptable"
        else:
            linearity = "poor"

        return {
            "r_squared": float(r_squared),
            "linearity": linearity,
            "slope": float(coeffs[0]),
            "intercept": float(coeffs[1])
        }
