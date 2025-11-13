"""
Data Processing Utilities for PV Test Data

Provides functionality for:
- IV curve analysis
- Power calculations
- Temperature coefficient calculations
- Statistical analysis
- Data quality checks
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from scipy.optimize import curve_fit
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processor for PV test data"""

    @staticmethod
    def analyze_iv_curve(voltage: List[float], current: List[float],
                        irradiance: float, temperature: float) -> Dict[str, Any]:
        """
        Analyze IV curve and extract key parameters

        Args:
            voltage: Voltage measurements (V)
            current: Current measurements (A)
            irradiance: Irradiance during measurement (W/m²)
            temperature: Temperature during measurement (°C)

        Returns:
            Dict with analysis results (Isc, Voc, Pmax, Imax, Vmax, FF, Eff)
        """
        try:
            v = np.array(voltage)
            i = np.array(current)
            power = v * i

            # Short circuit current (approximately)
            isc = np.max(i)

            # Open circuit voltage (approximately)
            voc = np.max(v)

            # Maximum power point
            pmax_idx = np.argmax(power)
            pmax = power[pmax_idx]
            vmax = v[pmax_idx]
            imax = i[pmax_idx]

            # Fill factor
            fill_factor = pmax / (voc * isc) if (voc * isc) > 0 else 0

            # Efficiency (assuming 1m² area, can be parameterized)
            area = 1.0  # m²
            efficiency = (pmax / (irradiance * area)) * 100 if irradiance > 0 else 0

            # Series resistance (approximate from slope near Voc)
            rs = DataProcessor._estimate_series_resistance(v, i)

            # Shunt resistance (approximate from slope near Isc)
            rsh = DataProcessor._estimate_shunt_resistance(v, i)

            results = {
                'isc': float(isc),
                'voc': float(voc),
                'pmax': float(pmax),
                'vmax': float(vmax),
                'imax': float(imax),
                'fill_factor': float(fill_factor),
                'efficiency': float(efficiency),
                'series_resistance': float(rs),
                'shunt_resistance': float(rsh),
                'irradiance': irradiance,
                'temperature': temperature,
                'data_points': len(v)
            }

            logger.info(f"IV curve analyzed: Pmax={pmax:.2f}W, FF={fill_factor:.3f}, Eff={efficiency:.2f}%")
            return results

        except Exception as e:
            logger.error(f"IV curve analysis failed: {e}")
            return {}

    @staticmethod
    def _estimate_series_resistance(v: np.ndarray, i: np.ndarray) -> float:
        """Estimate series resistance from IV curve"""
        try:
            # Use points near Voc (top 10% of voltage range)
            threshold = np.max(v) * 0.9
            mask = v > threshold
            if np.sum(mask) > 2:
                slope, _ = np.polyfit(v[mask], i[mask], 1)
                rs = -1 / slope if slope != 0 else 0
                return max(0, rs)  # Ensure positive
        except:
            pass
        return 0.0

    @staticmethod
    def _estimate_shunt_resistance(v: np.ndarray, i: np.ndarray) -> float:
        """Estimate shunt resistance from IV curve"""
        try:
            # Use points near Isc (bottom 10% of voltage range)
            threshold = np.max(v) * 0.1
            mask = v < threshold
            if np.sum(mask) > 2:
                slope, _ = np.polyfit(v[mask], i[mask], 1)
                rsh = 1 / slope if slope != 0 else np.inf
                return max(0, rsh)  # Ensure positive
        except:
            pass
        return np.inf

    @staticmethod
    def calculate_temperature_coefficients(
        data: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Calculate temperature coefficients from multi-temperature measurements

        Args:
            data: List of measurements, each with temp, voc, isc, pmax

        Returns:
            Dict with alpha (Isc/T), beta (Voc/T), gamma (Pmax/T)
        """
        try:
            df = pd.DataFrame(data)

            # Calculate coefficients using linear regression
            temp = df['temperature'].values
            voc = df['voc'].values
            isc = df['isc'].values
            pmax = df['pmax'].values

            # Beta: Voc temperature coefficient (%/°C)
            beta_slope, _, _, _, _ = stats.linregress(temp, voc)
            voc_ref = np.mean(voc)
            beta = (beta_slope / voc_ref) * 100 if voc_ref > 0 else 0

            # Alpha: Isc temperature coefficient (%/°C)
            alpha_slope, _, _, _, _ = stats.linregress(temp, isc)
            isc_ref = np.mean(isc)
            alpha = (alpha_slope / isc_ref) * 100 if isc_ref > 0 else 0

            # Gamma: Pmax temperature coefficient (%/°C)
            gamma_slope, _, _, _, _ = stats.linregress(temp, pmax)
            pmax_ref = np.mean(pmax)
            gamma = (gamma_slope / pmax_ref) * 100 if pmax_ref > 0 else 0

            results = {
                'alpha_isc': float(alpha),  # %/°C
                'beta_voc': float(beta),    # %/°C
                'gamma_pmax': float(gamma),  # %/°C
                'reference_temperature': float(np.mean(temp)),
                'measurements_count': len(data)
            }

            logger.info(f"Temperature coefficients: α={alpha:.3f}, β={beta:.3f}, γ={gamma:.3f} %/°C")
            return results

        except Exception as e:
            logger.error(f"Temperature coefficient calculation failed: {e}")
            return {}

    @staticmethod
    def calculate_degradation_rate(
        initial_power: float,
        final_power: float,
        duration_hours: float
    ) -> Dict[str, float]:
        """
        Calculate degradation rate

        Args:
            initial_power: Initial power (W)
            final_power: Final power (W)
            duration_hours: Test duration (hours)

        Returns:
            Dict with degradation results
        """
        try:
            power_loss = initial_power - final_power
            power_loss_percent = (power_loss / initial_power) * 100 if initial_power > 0 else 0

            # Convert to per year (assuming 8760 hours/year)
            degradation_rate_per_year = (power_loss_percent / duration_hours) * 8760

            results = {
                'initial_power': float(initial_power),
                'final_power': float(final_power),
                'power_loss': float(power_loss),
                'power_loss_percent': float(power_loss_percent),
                'duration_hours': float(duration_hours),
                'degradation_rate_per_year': float(degradation_rate_per_year),
                'retention_percent': float((final_power / initial_power) * 100) if initial_power > 0 else 0
            }

            logger.info(f"Degradation: {power_loss_percent:.2f}% loss, {degradation_rate_per_year:.2f}%/year")
            return results

        except Exception as e:
            logger.error(f"Degradation calculation failed: {e}")
            return {}

    @staticmethod
    def normalize_to_stc(
        power: float,
        irradiance: float,
        temperature: float,
        gamma: float = -0.4,
        irradiance_stc: float = 1000.0,
        temperature_stc: float = 25.0
    ) -> float:
        """
        Normalize power to Standard Test Conditions (STC)

        Args:
            power: Measured power (W)
            irradiance: Measured irradiance (W/m²)
            temperature: Measured temperature (°C)
            gamma: Temperature coefficient of power (%/°C)
            irradiance_stc: STC irradiance (W/m²)
            temperature_stc: STC temperature (°C)

        Returns:
            Power normalized to STC
        """
        try:
            # Irradiance correction
            power_corrected = power * (irradiance_stc / irradiance)

            # Temperature correction
            temp_diff = temperature - temperature_stc
            temp_correction_factor = 1 + (gamma / 100) * temp_diff
            power_stc = power_corrected * temp_correction_factor

            logger.debug(f"Normalized {power:.2f}W to {power_stc:.2f}W (STC)")
            return float(power_stc)

        except Exception as e:
            logger.error(f"STC normalization failed: {e}")
            return power

    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """Calculate statistical parameters for a dataset"""
        try:
            arr = np.array(data)

            results = {
                'mean': float(np.mean(arr)),
                'median': float(np.median(arr)),
                'std_dev': float(np.std(arr, ddof=1)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'range': float(np.max(arr) - np.min(arr)),
                'count': len(data),
                'coefficient_of_variation': float((np.std(arr, ddof=1) / np.mean(arr)) * 100) if np.mean(arr) > 0 else 0
            }

            return results

        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {}

    @staticmethod
    def validate_data_quality(
        data: List[float],
        expected_range: Tuple[float, float],
        max_outliers_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        Validate data quality

        Args:
            data: Measurement data
            expected_range: Expected (min, max) range
            max_outliers_percent: Maximum acceptable outliers percentage

        Returns:
            Dict with validation results
        """
        try:
            arr = np.array(data)
            min_val, max_val = expected_range

            # Check range violations
            out_of_range = np.sum((arr < min_val) | (arr > max_val))
            out_of_range_percent = (out_of_range / len(arr)) * 100

            # Detect outliers using IQR method
            q1 = np.percentile(arr, 25)
            q3 = np.percentile(arr, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = np.sum((arr < lower_bound) | (arr > upper_bound))
            outliers_percent = (outliers / len(arr)) * 100

            is_valid = (
                out_of_range_percent < max_outliers_percent and
                outliers_percent < max_outliers_percent
            )

            results = {
                'is_valid': bool(is_valid),
                'data_points': len(data),
                'out_of_range_count': int(out_of_range),
                'out_of_range_percent': float(out_of_range_percent),
                'outliers_count': int(outliers),
                'outliers_percent': float(outliers_percent),
                'expected_range': expected_range,
                'actual_range': (float(np.min(arr)), float(np.max(arr)))
            }

            if not is_valid:
                logger.warning(f"Data quality check failed: {results}")
            else:
                logger.info("Data quality check passed")

            return results

        except Exception as e:
            logger.error(f"Data quality validation failed: {e}")
            return {'is_valid': False, 'error': str(e)}

    @staticmethod
    def calculate_uncertainty(
        measurements: List[float],
        instrument_uncertainty: float = 0.5
    ) -> Dict[str, float]:
        """
        Calculate measurement uncertainty

        Args:
            measurements: Repeated measurements
            instrument_uncertainty: Instrument uncertainty (%)

        Returns:
            Dict with uncertainty analysis
        """
        try:
            arr = np.array(measurements)
            mean_value = np.mean(arr)
            std_dev = np.std(arr, ddof=1)

            # Type A uncertainty (from repeatability)
            type_a_uncertainty = std_dev / np.sqrt(len(arr))

            # Type B uncertainty (from instrument)
            type_b_uncertainty = (instrument_uncertainty / 100) * mean_value / np.sqrt(3)

            # Combined uncertainty
            combined_uncertainty = np.sqrt(type_a_uncertainty**2 + type_b_uncertainty**2)

            # Expanded uncertainty (k=2, 95% confidence)
            expanded_uncertainty = 2 * combined_uncertainty

            # Relative uncertainty
            relative_uncertainty = (expanded_uncertainty / mean_value) * 100 if mean_value > 0 else 0

            results = {
                'mean': float(mean_value),
                'type_a_uncertainty': float(type_a_uncertainty),
                'type_b_uncertainty': float(type_b_uncertainty),
                'combined_uncertainty': float(combined_uncertainty),
                'expanded_uncertainty': float(expanded_uncertainty),
                'relative_uncertainty_percent': float(relative_uncertainty),
                'measurements_count': len(arr)
            }

            logger.info(f"Uncertainty: {mean_value:.2f} ± {expanded_uncertainty:.2f} ({relative_uncertainty:.2f}%)")
            return results

        except Exception as e:
            logger.error(f"Uncertainty calculation failed: {e}")
            return {}
