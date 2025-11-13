"""
NOCT and Temperature Coefficient Calculations

Implements IEC 61215-1:2021 calculation methods
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class NOCTCalculator:
    """
    NOCT (Nominal Operating Cell Temperature) Calculations

    Implements calculations per IEC 61215-1:2021 Section 7.3
    """

    @staticmethod
    def calculate_noct(cell_temps: np.ndarray,
                      ambient_temps: np.ndarray,
                      irradiances: np.ndarray,
                      target_irradiance: float = 800.0) -> Dict[str, float]:
        """
        Calculate NOCT from measured data

        NOCT is the cell temperature when:
        - Irradiance = 800 W/m²
        - Ambient temperature = 20°C
        - Wind speed = 1 m/s
        - Open circuit conditions

        Args:
            cell_temps: Array of cell temperatures (°C)
            ambient_temps: Array of ambient temperatures (°C)
            irradiances: Array of irradiance values (W/m²)
            target_irradiance: Target irradiance for normalization (default 800 W/m²)

        Returns:
            Dict with NOCT calculation results
        """
        # Calculate temperature rise above ambient
        temp_rise = cell_temps - ambient_temps

        # Normalize to target irradiance
        # NOCT = T_ambient + (T_cell - T_ambient) * (G_target / G_actual)
        normalized_noct = ambient_temps + (temp_rise * target_irradiance / irradiances)

        # Calculate mean NOCT
        noct_mean = np.mean(normalized_noct)
        noct_std = np.std(normalized_noct)
        noct_min = np.min(normalized_noct)
        noct_max = np.max(normalized_noct)

        # Calculate uncertainty
        uncertainty = 2.0 * noct_std / np.sqrt(len(normalized_noct))  # 95% confidence

        logger.info(f"Calculated NOCT: {noct_mean:.2f}°C ± {uncertainty:.2f}°C")

        return {
            'noct': float(noct_mean),
            'std_deviation': float(noct_std),
            'uncertainty': float(uncertainty),
            'min': float(noct_min),
            'max': float(noct_max),
            'num_points': len(normalized_noct),
            'target_irradiance': target_irradiance
        }

    @staticmethod
    def calculate_power_at_noct(pmax_stc: float,
                               noct: float,
                               temp_coeff_power: float,
                               irradiance_noct: float = 800.0) -> Dict[str, float]:
        """
        Calculate expected power output at NOCT conditions

        Args:
            pmax_stc: Rated power at STC (W)
            noct: Calculated NOCT value (°C)
            temp_coeff_power: Temperature coefficient of power (%/°C)
            irradiance_noct: Irradiance at NOCT conditions (W/m²)

        Returns:
            Dict with power calculation results
        """
        # Temperature correction from 25°C to NOCT
        temp_correction = 1 + (temp_coeff_power / 100) * (noct - 25)

        # Irradiance correction from 1000 W/m² to irradiance_noct
        irradiance_correction = irradiance_noct / 1000.0

        # Calculate Pmax at NOCT
        pmax_noct = pmax_stc * temp_correction * irradiance_correction

        logger.info(f"Power at NOCT: {pmax_noct:.2f}W (from {pmax_stc:.2f}W at STC)")

        return {
            'pmax_noct': float(pmax_noct),
            'pmax_stc': float(pmax_stc),
            'temp_correction_factor': float(temp_correction),
            'irradiance_correction_factor': float(irradiance_correction),
            'power_loss_percent': float((pmax_stc - pmax_noct) / pmax_stc * 100)
        }

    @staticmethod
    def calculate_efficiency_at_noct(pmax_noct: float,
                                    module_area: float,
                                    irradiance_noct: float = 800.0) -> Dict[str, float]:
        """
        Calculate module efficiency at NOCT conditions

        Args:
            pmax_noct: Maximum power at NOCT (W)
            module_area: Module area (m²)
            irradiance_noct: Irradiance at NOCT (W/m²)

        Returns:
            Dict with efficiency calculation results
        """
        # Efficiency = Pmax / (Irradiance * Area) * 100
        efficiency = (pmax_noct / (irradiance_noct * module_area)) * 100

        logger.info(f"Efficiency at NOCT: {efficiency:.2f}%")

        return {
            'efficiency_noct': float(efficiency),
            'pmax_noct': float(pmax_noct),
            'module_area': float(module_area),
            'irradiance': float(irradiance_noct)
        }

    @staticmethod
    def estimate_operating_temperature(ambient_temp: float,
                                      irradiance: float,
                                      noct: float,
                                      ref_ambient: float = 20.0,
                                      ref_irradiance: float = 800.0) -> float:
        """
        Estimate module operating temperature for given conditions

        T_op = T_amb + (NOCT - T_ref) * (G / G_ref)

        Args:
            ambient_temp: Ambient temperature (°C)
            irradiance: Irradiance (W/m²)
            noct: Module NOCT (°C)
            ref_ambient: Reference ambient temperature (°C)
            ref_irradiance: Reference irradiance (W/m²)

        Returns:
            Estimated operating temperature (°C)
        """
        temp_rise = (noct - ref_ambient) * (irradiance / ref_irradiance)
        operating_temp = ambient_temp + temp_rise

        return float(operating_temp)


class TemperatureCoefficients:
    """
    Temperature Coefficient Calculations

    Calculate temperature coefficients of Pmax, Voc, and Isc
    """

    @staticmethod
    def calculate_power_coefficient(temperatures: np.ndarray,
                                   powers: np.ndarray,
                                   pmax_ref: float,
                                   temp_ref: float = 25.0) -> Dict[str, float]:
        """
        Calculate temperature coefficient of power (alpha_P)

        α_P = (1/P_ref) * (dP/dT) * 100  [%/°C]

        Args:
            temperatures: Array of cell temperatures (°C)
            powers: Array of maximum power values (W)
            pmax_ref: Reference power at temp_ref (W)
            temp_ref: Reference temperature (°C)

        Returns:
            Dict with coefficient calculation results
        """
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temperatures, powers)

        # Calculate temperature coefficient (normalize to reference power)
        alpha_p = (slope / pmax_ref) * 100  # Convert to %/°C

        # Calculate R-squared
        r_squared = r_value ** 2

        logger.info(f"Temperature coefficient of power: {alpha_p:.4f}%/°C (R²={r_squared:.4f})")

        return {
            'alpha_p': float(alpha_p),
            'alpha_p_absolute': float(slope),  # W/°C
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'reference_power': float(pmax_ref),
            'reference_temp': float(temp_ref),
            'num_points': len(temperatures)
        }

    @staticmethod
    def calculate_voc_coefficient(temperatures: np.ndarray,
                                 voltages: np.ndarray,
                                 voc_ref: float,
                                 temp_ref: float = 25.0) -> Dict[str, float]:
        """
        Calculate temperature coefficient of Voc (beta_Voc)

        β_Voc = (1/V_ref) * (dV/dT) * 100  [%/°C]

        Args:
            temperatures: Array of cell temperatures (°C)
            voltages: Array of open-circuit voltages (V)
            voc_ref: Reference Voc at temp_ref (V)
            temp_ref: Reference temperature (°C)

        Returns:
            Dict with coefficient calculation results
        """
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temperatures, voltages)

        # Calculate temperature coefficient
        beta_voc = (slope / voc_ref) * 100  # Convert to %/°C

        r_squared = r_value ** 2

        logger.info(f"Temperature coefficient of Voc: {beta_voc:.4f}%/°C (R²={r_squared:.4f})")

        return {
            'beta_voc': float(beta_voc),
            'beta_voc_absolute': float(slope),  # V/°C
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'reference_voc': float(voc_ref),
            'reference_temp': float(temp_ref),
            'num_points': len(temperatures)
        }

    @staticmethod
    def calculate_isc_coefficient(temperatures: np.ndarray,
                                 currents: np.ndarray,
                                 isc_ref: float,
                                 temp_ref: float = 25.0) -> Dict[str, float]:
        """
        Calculate temperature coefficient of Isc (alpha_Isc)

        α_Isc = (1/I_ref) * (dI/dT) * 100  [%/°C]

        Args:
            temperatures: Array of cell temperatures (°C)
            currents: Array of short-circuit currents (A)
            isc_ref: Reference Isc at temp_ref (A)
            temp_ref: Reference temperature (°C)

        Returns:
            Dict with coefficient calculation results
        """
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temperatures, currents)

        # Calculate temperature coefficient
        alpha_isc = (slope / isc_ref) * 100  # Convert to %/°C

        r_squared = r_value ** 2

        logger.info(f"Temperature coefficient of Isc: {alpha_isc:.4f}%/°C (R²={r_squared:.4f})")

        return {
            'alpha_isc': float(alpha_isc),
            'alpha_isc_absolute': float(slope),  # A/°C
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'reference_isc': float(isc_ref),
            'reference_temp': float(temp_ref),
            'num_points': len(temperatures)
        }

    @staticmethod
    def calculate_all_coefficients(temperatures: np.ndarray,
                                  powers: np.ndarray,
                                  voltages: np.ndarray,
                                  currents: np.ndarray,
                                  pmax_ref: float,
                                  voc_ref: float,
                                  isc_ref: float,
                                  temp_ref: float = 25.0) -> Dict[str, Any]:
        """
        Calculate all temperature coefficients

        Args:
            temperatures: Array of cell temperatures (°C)
            powers: Array of maximum power values (W)
            voltages: Array of open-circuit voltages (V)
            currents: Array of short-circuit currents (A)
            pmax_ref: Reference power (W)
            voc_ref: Reference Voc (V)
            isc_ref: Reference Isc (A)
            temp_ref: Reference temperature (°C)

        Returns:
            Dict with all coefficients
        """
        results = {
            'power': TemperatureCoefficients.calculate_power_coefficient(
                temperatures, powers, pmax_ref, temp_ref
            ),
            'voc': TemperatureCoefficients.calculate_voc_coefficient(
                temperatures, voltages, voc_ref, temp_ref
            ),
            'isc': TemperatureCoefficients.calculate_isc_coefficient(
                temperatures, currents, isc_ref, temp_ref
            )
        }

        logger.info("Calculated all temperature coefficients")
        return results
