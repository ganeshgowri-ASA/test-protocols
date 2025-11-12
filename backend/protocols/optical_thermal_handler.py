"""
Optical and Thermal Test Protocol Handler

This module provides calculation algorithms and analysis functions for:
- UV Exposure Tests (PVTP-007-UV): UV dose calculation and tracking
- Hot Spot Tests (PVTP-008-HS): Hot spot detection and thermal analysis
- Bypass Diode Tests (PVTP-009-BD): Diode characteristic curves and analysis

Standards: IEC 61215-2:2016 MQT 09, MQT 10, MQT 18
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from scipy import integrate, optimize, ndimage, stats
from scipy.signal import savgol_filter
import warnings


# ============================================================================
# UV EXPOSURE TEST CALCULATIONS
# ============================================================================

@dataclass
class UVExposureData:
    """Data structure for UV exposure measurements"""
    timestamp: List[datetime]
    irradiance: List[float]  # W/m² at 340 nm
    temperature: List[float]  # °C
    cumulative_dose: Optional[List[float]] = None  # kWh/m²


class UVDoseCalculator:
    """Calculate and track UV dose exposure"""

    def __init__(self, target_dose: float = 15.0, irradiance_target: float = 0.6):
        """
        Initialize UV dose calculator

        Args:
            target_dose: Target cumulative dose in kWh/m² (default: 15 per IEC 61215-2)
            irradiance_target: Target spectral irradiance at 340 nm in W/m²/nm (default: 0.6)
        """
        self.target_dose = target_dose
        self.irradiance_target = irradiance_target
        self.wavelength_range = (280, 400)  # nm, UVA and UVB range

    def calculate_cumulative_dose(
        self,
        irradiance: np.ndarray,
        timestamps: np.ndarray
    ) -> np.ndarray:
        """
        Calculate cumulative UV dose from time-series irradiance data

        Args:
            irradiance: Array of irradiance measurements in W/m²
            timestamps: Array of datetime objects or Unix timestamps

        Returns:
            Array of cumulative dose in kWh/m²
        """
        # Convert timestamps to hours elapsed
        if isinstance(timestamps[0], datetime):
            time_hours = np.array([(t - timestamps[0]).total_seconds() / 3600
                                   for t in timestamps])
        else:
            time_hours = (timestamps - timestamps[0]) / 3600

        # Integrate irradiance over time using trapezoidal rule
        # Dose (Wh/m²) = ∫ irradiance(t) dt
        dose_wh_m2 = integrate.cumtrapz(irradiance, time_hours, initial=0)

        # Convert to kWh/m²
        dose_kwh_m2 = dose_wh_m2 / 1000

        return dose_kwh_m2

    def estimate_remaining_time(
        self,
        current_dose: float,
        avg_irradiance: float
    ) -> Tuple[float, str]:
        """
        Estimate remaining exposure time to reach target dose

        Args:
            current_dose: Current cumulative dose in kWh/m²
            avg_irradiance: Average irradiance in W/m²

        Returns:
            Tuple of (hours_remaining, formatted_time_string)
        """
        remaining_dose = self.target_dose - current_dose

        if remaining_dose <= 0:
            return 0.0, "Target dose achieved"

        if avg_irradiance <= 0:
            return float('inf'), "Invalid irradiance"

        # Time = Energy / Power
        hours_remaining = (remaining_dose * 1000) / avg_irradiance

        # Format as days:hours:minutes
        days = int(hours_remaining // 24)
        hours = int(hours_remaining % 24)
        minutes = int((hours_remaining * 60) % 60)

        time_str = f"{days}d {hours}h {minutes}m"

        return hours_remaining, time_str

    def calculate_dose_uniformity(
        self,
        doses: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate spatial uniformity of UV dose across multiple sensors

        Args:
            doses: Array of dose measurements from different positions

        Returns:
            Dictionary with uniformity metrics
        """
        mean_dose = np.mean(doses)
        std_dose = np.std(doses)
        min_dose = np.min(doses)
        max_dose = np.max(doses)

        # Non-uniformity as percentage
        non_uniformity = (max_dose - min_dose) / mean_dose * 100

        # Coefficient of variation
        cv = (std_dose / mean_dose) * 100 if mean_dose > 0 else 0

        return {
            'mean_dose_kwh_m2': mean_dose,
            'std_dose_kwh_m2': std_dose,
            'min_dose_kwh_m2': min_dose,
            'max_dose_kwh_m2': max_dose,
            'non_uniformity_percent': non_uniformity,
            'coefficient_of_variation_percent': cv,
            'passes_uniformity': non_uniformity <= 10.0  # ±10% per IEC 61215-2
        }

    def verify_spectrum(
        self,
        wavelengths: np.ndarray,
        irradiances: np.ndarray,
        reference_spectrum: Optional[np.ndarray] = None
    ) -> Dict[str, Union[float, bool]]:
        """
        Verify UV spectrum against reference

        Args:
            wavelengths: Array of wavelengths in nm
            irradiances: Array of spectral irradiances in W/m²/nm
            reference_spectrum: Optional reference spectrum for comparison

        Returns:
            Dictionary with spectrum verification results
        """
        # Find peak wavelength
        peak_idx = np.argmax(irradiances)
        peak_wavelength = wavelengths[peak_idx]
        peak_irradiance = irradiances[peak_idx]

        # Calculate UVA (315-400 nm) and UVB (280-315 nm) content
        uva_mask = (wavelengths >= 315) & (wavelengths <= 400)
        uvb_mask = (wavelengths >= 280) & (wavelengths < 315)

        uva_integral = integrate.trapz(irradiances[uva_mask], wavelengths[uva_mask])
        uvb_integral = integrate.trapz(irradiances[uvb_mask], wavelengths[uvb_mask])
        total_integral = uva_integral + uvb_integral

        uva_fraction = (uva_integral / total_integral * 100) if total_integral > 0 else 0
        uvb_fraction = (uvb_integral / total_integral * 100) if total_integral > 0 else 0

        results = {
            'peak_wavelength_nm': peak_wavelength,
            'peak_irradiance_W_m2_nm': peak_irradiance,
            'uva_fraction_percent': uva_fraction,
            'uvb_fraction_percent': uvb_fraction,
            'total_uv_irradiance_W_m2': total_integral,
            'peak_within_spec': 335 <= peak_wavelength <= 345,  # 340 ± 5 nm
            'uva_uvb_ratio_within_spec': 93 <= uva_fraction <= 97  # 95:5 ± 2%
        }

        # Compare to reference spectrum if provided
        if reference_spectrum is not None:
            # Ensure same wavelength grid
            if len(reference_spectrum) == len(irradiances):
                deviation = np.abs((irradiances - reference_spectrum) / reference_spectrum) * 100
                max_deviation = np.max(deviation)
                results['max_deviation_from_reference_percent'] = max_deviation
                results['spectrum_within_tolerance'] = max_deviation <= 15  # ±15% per spec

        return results


# ============================================================================
# HOT SPOT DETECTION AND THERMAL ANALYSIS
# ============================================================================

@dataclass
class ThermalImage:
    """Thermal image data structure"""
    temperature_matrix: np.ndarray  # 2D array of temperatures in °C
    timestamp: datetime
    emissivity: float
    distance_m: float
    ambient_temp_c: float
    reflected_temp_c: float
    resolution: Tuple[int, int]


class HotSpotDetector:
    """Detect and analyze hot spots in thermal images"""

    def __init__(
        self,
        threshold_method: str = 'adaptive',
        min_hotspot_area_cm2: float = 10.0
    ):
        """
        Initialize hot spot detector

        Args:
            threshold_method: Method for hot spot detection ('absolute', 'adaptive', 'statistical')
            min_hotspot_area_cm2: Minimum contiguous area to be considered a hot spot
        """
        self.threshold_method = threshold_method
        self.min_hotspot_area_cm2 = min_hotspot_area_cm2

    def detect_hotspots(
        self,
        thermal_image: np.ndarray,
        pixel_size_cm: float = 1.0,
        absolute_threshold_c: float = 85.0,
        adaptive_offset_c: float = 20.0
    ) -> Dict[str, Union[np.ndarray, List, float]]:
        """
        Detect hot spots in thermal image

        Args:
            thermal_image: 2D array of temperatures in °C
            pixel_size_cm: Size of each pixel in cm (for area calculation)
            absolute_threshold_c: Absolute temperature threshold in °C
            adaptive_offset_c: Temperature offset above mean for adaptive threshold

        Returns:
            Dictionary with hot spot detection results
        """
        # Calculate threshold based on method
        if self.threshold_method == 'absolute':
            threshold = absolute_threshold_c
        elif self.threshold_method == 'adaptive':
            mean_temp = np.mean(thermal_image)
            threshold = mean_temp + adaptive_offset_c
        elif self.threshold_method == 'statistical':
            mean_temp = np.mean(thermal_image)
            std_temp = np.std(thermal_image)
            threshold = mean_temp + 2 * std_temp  # 2-sigma threshold
        else:
            raise ValueError(f"Unknown threshold method: {self.threshold_method}")

        # Create binary mask of hot pixels
        hotspot_mask = thermal_image > threshold

        # Label connected regions
        labeled_regions, num_regions = ndimage.label(hotspot_mask)

        # Analyze each hot spot region
        hotspots = []
        pixel_area_cm2 = pixel_size_cm ** 2
        min_pixels = int(self.min_hotspot_area_cm2 / pixel_area_cm2)

        for region_id in range(1, num_regions + 1):
            region_mask = labeled_regions == region_id
            region_size = np.sum(region_mask)

            # Skip small regions
            if region_size < min_pixels:
                continue

            # Extract region properties
            region_temps = thermal_image[region_mask]
            max_temp = np.max(region_temps)
            mean_temp_region = np.mean(region_temps)

            # Find location of maximum temperature
            max_indices = np.where((thermal_image == max_temp) & region_mask)
            max_location = (int(max_indices[0][0]), int(max_indices[1][0]))

            # Calculate area
            area_cm2 = region_size * pixel_area_cm2

            hotspots.append({
                'region_id': region_id,
                'max_temperature_c': max_temp,
                'mean_temperature_c': mean_temp_region,
                'area_cm2': area_cm2,
                'location_row_col': max_location,
                'num_pixels': region_size
            })

        # Overall statistics
        max_temp_overall = np.max(thermal_image)
        mean_temp_overall = np.mean(thermal_image)
        gradient = max_temp_overall - mean_temp_overall

        return {
            'threshold_used_c': threshold,
            'num_hotspots_detected': len(hotspots),
            'hotspots': hotspots,
            'hotspot_mask': hotspot_mask,
            'labeled_regions': labeled_regions,
            'max_temperature_c': max_temp_overall,
            'mean_temperature_c': mean_temp_overall,
            'temperature_gradient_c': gradient
        }

    def track_temperature_transient(
        self,
        temperatures: np.ndarray,
        times_minutes: np.ndarray
    ) -> Dict[str, float]:
        """
        Analyze temperature transient and fit exponential model

        Model: T(t) = T_final × (1 - exp(-t/τ)) + T_initial

        Args:
            temperatures: Array of hot spot temperatures over time (°C)
            times_minutes: Array of time points in minutes

        Returns:
            Dictionary with transient analysis results
        """
        # Define exponential model
        def exp_rise(t, T_final, tau, T_initial):
            return T_final * (1 - np.exp(-t / tau)) + T_initial

        try:
            # Initial parameter guesses
            T_initial_guess = temperatures[0]
            T_final_guess = temperatures[-1]
            tau_guess = times_minutes[-1] / 3  # Rough estimate

            # Fit model
            params, covariance = optimize.curve_fit(
                exp_rise,
                times_minutes,
                temperatures,
                p0=[T_final_guess, tau_guess, T_initial_guess],
                maxfev=10000
            )

            T_final_fit, tau_fit, T_initial_fit = params

            # Calculate R² goodness of fit
            residuals = temperatures - exp_rise(times_minutes, *params)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((temperatures - np.mean(temperatures))**2)
            r_squared = 1 - (ss_res / ss_tot)

            # Calculate time to 95% of final temperature
            time_to_95_percent = -tau_fit * np.log(0.05)

            # Check if steady state reached
            recent_temps = temperatures[-5:]  # Last 5 measurements
            temp_std = np.std(recent_temps)
            is_steady = temp_std < 2.0  # < 2°C variation

            # Calculate rate of change in last 10 minutes
            if len(temperatures) >= 2:
                dt_dt = (temperatures[-1] - temperatures[-2]) / (times_minutes[-1] - times_minutes[-2])
            else:
                dt_dt = 0.0

            return {
                'T_initial_c': T_initial_fit,
                'T_final_c': T_final_fit,
                'time_constant_tau_min': tau_fit,
                'time_to_95_percent_min': time_to_95_percent,
                'r_squared': r_squared,
                'is_steady_state': is_steady,
                'current_rate_of_change_c_per_min': dt_dt,
                'fit_successful': True
            }

        except Exception as e:
            warnings.warn(f"Temperature transient fit failed: {e}")
            return {
                'fit_successful': False,
                'error': str(e)
            }

    def calculate_thermal_distribution(
        self,
        thermal_image: np.ndarray
    ) -> Dict[str, Union[float, np.ndarray]]:
        """
        Calculate statistical distribution of temperatures

        Args:
            thermal_image: 2D array of temperatures in °C

        Returns:
            Dictionary with thermal distribution metrics
        """
        temps_flat = thermal_image.flatten()

        # Statistical moments
        mean_temp = np.mean(temps_flat)
        median_temp = np.median(temps_flat)
        std_temp = np.std(temps_flat)
        min_temp = np.min(temps_flat)
        max_temp = np.max(temps_flat)

        # Percentiles
        p5 = np.percentile(temps_flat, 5)
        p95 = np.percentile(temps_flat, 95)

        # Skewness and kurtosis
        skewness = stats.skew(temps_flat)
        kurtosis = stats.kurtosis(temps_flat)

        # Temperature histogram
        hist, bin_edges = np.histogram(temps_flat, bins=50)

        return {
            'mean_temperature_c': mean_temp,
            'median_temperature_c': median_temp,
            'std_temperature_c': std_temp,
            'min_temperature_c': min_temp,
            'max_temperature_c': max_temp,
            'percentile_5_c': p5,
            'percentile_95_c': p95,
            'range_c': max_temp - min_temp,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'histogram_counts': hist,
            'histogram_bin_edges': bin_edges
        }


# ============================================================================
# BYPASS DIODE I-V CURVE ANALYSIS
# ============================================================================

@dataclass
class DiodeIVData:
    """Diode I-V characteristic data"""
    voltage: np.ndarray  # Volts
    current: np.ndarray  # Amps
    temperature: float  # °C
    diode_id: str
    timestamp: datetime


class DiodeCharacteristicAnalyzer:
    """Analyze bypass diode I-V characteristics"""

    def __init__(self):
        """Initialize diode analyzer"""
        self.k_boltzmann = 1.380649e-23  # J/K
        self.q_electron = 1.602176634e-19  # C

    def analyze_forward_characteristics(
        self,
        voltage: np.ndarray,
        current: np.ndarray,
        test_current: float,
        temperature_c: float = 25.0
    ) -> Dict[str, float]:
        """
        Analyze forward I-V characteristics

        Args:
            voltage: Array of voltage measurements (V)
            current: Array of current measurements (A)
            test_current: Test current level (typically 1.25 × Isc)
            temperature_c: Measurement temperature in °C

        Returns:
            Dictionary with forward characteristic parameters
        """
        # Sort by voltage
        sort_idx = np.argsort(voltage)
        v_sorted = voltage[sort_idx]
        i_sorted = current[sort_idx]

        # Find forward voltage at test current
        if np.max(i_sorted) >= test_current:
            vf_at_test = np.interp(test_current, i_sorted, v_sorted)
        else:
            vf_at_test = None

        # Calculate dynamic resistance dV/dI in forward region
        # Use region around test current
        if vf_at_test is not None:
            current_window = 0.2 * test_current
            mask = np.abs(i_sorted - test_current) < current_window
            if np.sum(mask) > 2:
                v_region = v_sorted[mask]
                i_region = i_sorted[mask]

                # Linear fit to get dV/dI
                coeffs = np.polyfit(i_region, v_region, 1)
                dynamic_resistance = coeffs[0]  # dV/dI in ohms
            else:
                dynamic_resistance = None
        else:
            dynamic_resistance = None

        # Estimate ideality factor from exponential region
        # Shockley equation: I = I0 * (exp(qV/nkT) - 1)
        # ln(I) vs V should be linear with slope = q/(nkT)

        # Select exponential region (typically 0.3 to 0.6 V)
        exp_mask = (v_sorted > 0.3) & (v_sorted < 0.6) & (i_sorted > 0)

        if np.sum(exp_mask) > 5:
            v_exp = v_sorted[exp_mask]
            i_exp = i_sorted[exp_mask]

            # Avoid log(0)
            i_exp = i_exp[i_exp > 1e-6]
            v_exp = v_exp[:len(i_exp)]

            if len(i_exp) > 5:
                log_i = np.log(i_exp)

                # Linear fit: ln(I) = ln(I0) + (q/nkT) * V
                coeffs = np.polyfit(v_exp, log_i, 1)
                slope = coeffs[0]

                # Extract ideality factor
                T_kelvin = temperature_c + 273.15
                kT_q = (self.k_boltzmann * T_kelvin) / self.q_electron
                ideality_factor = 1 / (slope * kT_q)
            else:
                ideality_factor = None
        else:
            ideality_factor = None

        # Power dissipation at test current
        if vf_at_test is not None:
            power_dissipation = vf_at_test * test_current
        else:
            power_dissipation = None

        return {
            'vf_at_test_current_v': vf_at_test,
            'test_current_a': test_current,
            'dynamic_resistance_ohm': dynamic_resistance,
            'ideality_factor': ideality_factor,
            'power_dissipation_w': power_dissipation,
            'max_current_measured_a': np.max(i_sorted),
            'max_voltage_measured_v': np.max(v_sorted)
        }

    def analyze_reverse_characteristics(
        self,
        voltage: np.ndarray,
        current: np.ndarray,
        voc_module: float
    ) -> Dict[str, float]:
        """
        Analyze reverse I-V characteristics

        Args:
            voltage: Array of voltage measurements (V, negative for reverse bias)
            current: Array of current measurements (A)
            voc_module: Module open-circuit voltage (V)

        Returns:
            Dictionary with reverse characteristic parameters
        """
        # Sort by voltage
        sort_idx = np.argsort(voltage)
        v_sorted = voltage[sort_idx]
        i_sorted = current[sort_idx]

        # Find reverse leakage at -Voc
        v_target = -abs(voc_module)

        # Find closest voltage to target
        if np.min(v_sorted) <= v_target <= np.max(v_sorted):
            leakage_current = np.interp(v_target, v_sorted, i_sorted)
        else:
            leakage_current = None

        # Find maximum reverse voltage applied
        max_reverse_voltage = np.min(v_sorted)  # Most negative

        # Detect breakdown (if applicable)
        # Breakdown indicated by rapid current increase
        di_dv = np.gradient(i_sorted, v_sorted)
        breakdown_threshold = 0.1  # A/V

        breakdown_idx = np.where(np.abs(di_dv) > breakdown_threshold)[0]
        if len(breakdown_idx) > 0:
            breakdown_voltage = v_sorted[breakdown_idx[0]]
        else:
            breakdown_voltage = None

        return {
            'leakage_at_minus_voc_a': leakage_current,
            'test_voltage_v': v_target,
            'max_reverse_voltage_v': max_reverse_voltage,
            'breakdown_voltage_v': breakdown_voltage,
            'max_leakage_current_a': np.max(np.abs(i_sorted))
        }

    def calculate_thermal_resistance(
        self,
        vf: float,
        current: float,
        junction_box_temp_c: float,
        ambient_temp_c: float
    ) -> Dict[str, float]:
        """
        Calculate thermal resistance of junction box

        Args:
            vf: Forward voltage drop (V)
            current: Forward current (A)
            junction_box_temp_c: Junction box temperature (°C)
            ambient_temp_c: Ambient temperature (°C)

        Returns:
            Dictionary with thermal resistance calculation
        """
        # Power dissipation
        power_dissipation = vf * current

        # Temperature rise
        temp_rise = junction_box_temp_c - ambient_temp_c

        # Thermal resistance
        if power_dissipation > 0:
            thermal_resistance = temp_rise / power_dissipation
        else:
            thermal_resistance = None

        # Check if junction box temperature is acceptable
        temp_acceptable = junction_box_temp_c < 85.0  # °C per IEC standards

        return {
            'power_dissipation_w': power_dissipation,
            'temperature_rise_c': temp_rise,
            'thermal_resistance_c_per_w': thermal_resistance,
            'junction_box_temperature_c': junction_box_temp_c,
            'ambient_temperature_c': ambient_temp_c,
            'temperature_acceptable': temp_acceptable
        }

    def compare_iv_curves(
        self,
        baseline_v: np.ndarray,
        baseline_i: np.ndarray,
        test_v: np.ndarray,
        test_i: np.ndarray
    ) -> Dict[str, Union[float, bool]]:
        """
        Compare baseline and post-test I-V curves

        Args:
            baseline_v, baseline_i: Baseline I-V curve
            test_v, test_i: Post-test I-V curve

        Returns:
            Dictionary with comparison metrics
        """
        # Interpolate both curves to common voltage grid
        v_common = np.linspace(
            max(np.min(baseline_v), np.min(test_v)),
            min(np.max(baseline_v), np.max(test_v)),
            100
        )

        i_baseline_interp = np.interp(v_common, baseline_v, baseline_i)
        i_test_interp = np.interp(v_common, test_v, test_i)

        # Calculate RMS difference
        current_diff = i_test_interp - i_baseline_interp
        rms_diff = np.sqrt(np.mean(current_diff**2))

        # Maximum absolute difference
        max_abs_diff = np.max(np.abs(current_diff))

        # Average percent difference
        # Avoid division by zero
        i_baseline_safe = np.where(np.abs(i_baseline_interp) > 1e-6,
                                    i_baseline_interp, 1e-6)
        percent_diff = (current_diff / i_baseline_safe) * 100
        avg_percent_diff = np.mean(np.abs(percent_diff))

        # Check if degradation is acceptable (< 10% change)
        acceptable_degradation = avg_percent_diff < 10.0

        return {
            'rms_current_difference_a': rms_diff,
            'max_abs_current_difference_a': max_abs_diff,
            'avg_percent_difference': avg_percent_diff,
            'degradation_acceptable': acceptable_degradation,
            'num_comparison_points': len(v_common)
        }

    def estimate_temperature_coefficient(
        self,
        vf_measurements: List[Tuple[float, float]]
    ) -> Dict[str, float]:
        """
        Estimate temperature coefficient of forward voltage

        Args:
            vf_measurements: List of (temperature_c, vf_volts) tuples

        Returns:
            Dictionary with temperature coefficient
        """
        if len(vf_measurements) < 2:
            return {'error': 'Need at least 2 measurements at different temperatures'}

        temps = np.array([t for t, v in vf_measurements])
        vfs = np.array([v for t, v in vf_measurements])

        # Linear fit: Vf = Vf0 + α * T
        coeffs = np.polyfit(temps, vfs, 1)
        temp_coeff = coeffs[0]  # V/°C
        vf_at_25c = coeffs[1] + 25 * temp_coeff

        # R² goodness of fit
        vf_fit = np.polyval(coeffs, temps)
        residuals = vfs - vf_fit
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vfs - np.mean(vfs))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Typical value is -2 mV/°C for Schottky diodes
        typical_coeff_mv_c = -2.0
        is_typical = abs(temp_coeff * 1000 - typical_coeff_mv_c) < 1.0

        return {
            'temperature_coefficient_v_per_c': temp_coeff,
            'temperature_coefficient_mv_per_c': temp_coeff * 1000,
            'vf_at_25c_v': vf_at_25c,
            'r_squared': r_squared,
            'is_within_typical_range': is_typical
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_test_report(
    protocol_id: str,
    test_data: Dict,
    acceptance_criteria: Dict,
    template_path: str
) -> Dict[str, Union[str, bool, Dict]]:
    """
    Generate comprehensive test report with pass/fail determination

    Args:
        protocol_id: Protocol identifier (PVTP-007-UV, PVTP-008-HS, PVTP-009-BD)
        test_data: Dictionary of test results
        acceptance_criteria: Dictionary of pass/fail criteria
        template_path: Path to protocol template JSON

    Returns:
        Dictionary with report data and pass/fail status
    """
    report = {
        'protocol_id': protocol_id,
        'test_date': datetime.now().isoformat(),
        'results': test_data,
        'criteria': acceptance_criteria,
        'evaluations': {}
    }

    # Protocol-specific pass/fail evaluation
    if protocol_id == 'PVTP-007-UV':
        # UV exposure evaluation
        evaluations = {}

        # Check dose achievement
        if 'cumulative_dose_kwh_m2' in test_data:
            target_dose = acceptance_criteria.get('target_dose_kwh_m2', 15.0)
            actual_dose = test_data['cumulative_dose_kwh_m2']
            dose_tolerance = 0.05  # ±5%

            evaluations['dose_achieved'] = (
                target_dose * (1 - dose_tolerance) <= actual_dose <=
                target_dose * (1 + dose_tolerance)
            )

        # Check performance retention
        if 'power_degradation_percent' in test_data:
            max_degradation = acceptance_criteria.get('max_power_degradation_percent', 5.0)
            evaluations['performance_acceptable'] = (
                test_data['power_degradation_percent'] <= max_degradation
            )

        report['evaluations'] = evaluations
        report['overall_pass'] = all(evaluations.values())

    elif protocol_id == 'PVTP-008-HS':
        # Hot spot evaluation
        evaluations = {}

        # Check maximum temperature
        if 'max_temperature_c' in test_data:
            max_temp_limit = acceptance_criteria.get('max_temperature_c', 105.0)
            evaluations['temperature_acceptable'] = (
                test_data['max_temperature_c'] <= max_temp_limit
            )

        # Check temperature stability
        if 'is_steady_state' in test_data:
            evaluations['steady_state_achieved'] = test_data['is_steady_state']

        # Check performance retention
        if 'power_degradation_percent' in test_data:
            max_degradation = acceptance_criteria.get('max_power_degradation_percent', 5.0)
            evaluations['performance_acceptable'] = (
                test_data['power_degradation_percent'] <= max_degradation
            )

        report['evaluations'] = evaluations
        report['overall_pass'] = all(evaluations.values())

    elif protocol_id == 'PVTP-009-BD':
        # Bypass diode evaluation
        evaluations = {}

        # Check forward voltage
        if 'vf_at_test_current_v' in test_data:
            max_vf = acceptance_criteria.get('max_vf_v', 0.9)
            evaluations['vf_acceptable'] = (
                test_data['vf_at_test_current_v'] <= max_vf
            )

        # Check reverse leakage
        if 'leakage_at_minus_voc_a' in test_data:
            max_leakage = acceptance_criteria.get('max_leakage_25c_a', 0.001)
            evaluations['leakage_acceptable'] = (
                test_data['leakage_at_minus_voc_a'] <= max_leakage
            )

        # Check thermal performance
        if 'temperature_acceptable' in test_data:
            evaluations['thermal_acceptable'] = test_data['temperature_acceptable']

        report['evaluations'] = evaluations
        report['overall_pass'] = all(evaluations.values())

    return report


def export_results_to_csv(
    results: Dict,
    output_path: str
) -> None:
    """
    Export test results to CSV format

    Args:
        results: Dictionary of test results
        output_path: Path for output CSV file
    """
    # Flatten nested dictionary
    flat_results = {}

    def flatten_dict(d, parent_key=''):
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                flatten_dict(v, new_key)
            elif isinstance(v, (list, np.ndarray)):
                # Skip arrays in CSV export
                continue
            else:
                flat_results[new_key] = v

    flatten_dict(results)

    # Create DataFrame and export
    df = pd.DataFrame([flat_results])
    df.to_csv(output_path, index=False)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Optical and Thermal Test Protocol Handler")
    print("=" * 60)

    # Example 1: UV Dose Calculation
    print("\n1. UV Dose Calculation Example:")
    print("-" * 60)

    uv_calc = UVDoseCalculator(target_dose=15.0)

    # Simulate 100 hours of exposure at 60 W/m²
    time_hours = np.linspace(0, 100, 1000)
    irradiance = np.ones_like(time_hours) * 60  # W/m²

    # Add some variation
    irradiance += np.random.normal(0, 3, len(time_hours))

    dose = uv_calc.calculate_cumulative_dose(irradiance, time_hours)

    print(f"   After 100 hours at 60 W/m²:")
    print(f"   Cumulative dose: {dose[-1]:.2f} kWh/m²")

    hours_remaining, time_str = uv_calc.estimate_remaining_time(dose[-1], 60)
    print(f"   Remaining time to 15 kWh/m²: {time_str}")

    # Example 2: Hot Spot Detection
    print("\n2. Hot Spot Detection Example:")
    print("-" * 60)

    detector = HotSpotDetector(threshold_method='adaptive')

    # Create synthetic thermal image with hot spot
    thermal_img = np.random.normal(50, 5, (480, 640))  # Background at 50°C
    thermal_img[200:250, 300:350] = 95  # Hot spot at 95°C

    hotspot_results = detector.detect_hotspots(
        thermal_img,
        pixel_size_cm=0.5,
        adaptive_offset_c=20
    )

    print(f"   Detected {hotspot_results['num_hotspots_detected']} hot spot(s)")
    print(f"   Maximum temperature: {hotspot_results['max_temperature_c']:.1f}°C")
    print(f"   Temperature gradient: {hotspot_results['temperature_gradient_c']:.1f}°C")

    # Example 3: Diode I-V Analysis
    print("\n3. Bypass Diode I-V Analysis Example:")
    print("-" * 60)

    analyzer = DiodeCharacteristicAnalyzer()

    # Create synthetic I-V curve for Schottky diode
    voltage = np.linspace(0, 1.0, 100)
    Is = 1e-6  # Saturation current
    n = 1.2  # Ideality factor
    T = 298.15  # 25°C in Kelvin
    Vt = (analyzer.k_boltzmann * T) / analyzer.q_electron
    current = Is * (np.exp(voltage / (n * Vt)) - 1)

    forward_results = analyzer.analyze_forward_characteristics(
        voltage,
        current,
        test_current=12.0
    )

    print(f"   Forward voltage at 12 A: {forward_results['vf_at_test_current_v']:.3f} V")
    print(f"   Ideality factor: {forward_results['ideality_factor']:.2f}")
    print(f"   Power dissipation: {forward_results['power_dissipation_w']:.2f} W")

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
