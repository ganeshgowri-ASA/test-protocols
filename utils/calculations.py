"""PV Calculations and Statistical Analysis Utilities"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional, List
from scipy import stats, optimize, interpolate
from dataclasses import dataclass


@dataclass
class IVCurveParameters:
    """Container for I-V curve parameters"""
    isc: float  # Short-circuit current (A)
    voc: float  # Open-circuit voltage (V)
    imp: float  # Current at maximum power (A)
    vmp: float  # Voltage at maximum power (V)
    pmax: float  # Maximum power (W)
    ff: float  # Fill factor
    efficiency: Optional[float] = None  # Efficiency (%)
    rs: Optional[float] = None  # Series resistance (Ω)
    rsh: Optional[float] = None  # Shunt resistance (Ω)


class PVCalculations:
    """Photovoltaic calculations and analysis"""

    # Physical constants
    K_BOLTZMANN = 1.380649e-23  # Boltzmann constant (J/K)
    Q_ELECTRON = 1.602176634e-19  # Elementary charge (C)

    @staticmethod
    def calculate_fill_factor(isc: float, voc: float, pmax: float) -> float:
        """
        Calculate fill factor.

        Args:
            isc: Short-circuit current (A)
            voc: Open-circuit voltage (V)
            pmax: Maximum power (W)

        Returns:
            Fill factor (0-1)
        """
        if isc == 0 or voc == 0:
            return 0.0
        return pmax / (isc * voc)

    @staticmethod
    def calculate_efficiency(pmax: float, irradiance: float, area: float) -> float:
        """
        Calculate module efficiency.

        Args:
            pmax: Maximum power (W)
            irradiance: Incident irradiance (W/m²)
            area: Module area (m²)

        Returns:
            Efficiency (%)
        """
        if irradiance == 0 or area == 0:
            return 0.0
        return (pmax / (irradiance * area)) * 100

    @staticmethod
    def analyze_iv_curve(voltage: np.ndarray, current: np.ndarray,
                        area: Optional[float] = None,
                        irradiance: Optional[float] = None) -> IVCurveParameters:
        """
        Analyze I-V curve and extract key parameters.

        Args:
            voltage: Voltage array (V)
            current: Current array (A)
            area: Module area (m²), optional
            irradiance: Irradiance (W/m²), optional

        Returns:
            IVCurveParameters object with extracted parameters
        """
        # Short-circuit current (at V=0)
        isc = np.interp(0, voltage, current)

        # Open-circuit voltage (at I=0)
        voc = np.interp(0, current[::-1], voltage[::-1])

        # Calculate power
        power = voltage * current

        # Maximum power point
        idx_max = np.argmax(power)
        pmax = power[idx_max]
        vmp = voltage[idx_max]
        imp = current[idx_max]

        # Fill factor
        ff = PVCalculations.calculate_fill_factor(isc, voc, pmax)

        # Efficiency (if area and irradiance provided)
        efficiency = None
        if area and irradiance:
            efficiency = PVCalculations.calculate_efficiency(pmax, irradiance, area)

        # Series and shunt resistance estimation
        rs = PVCalculations.estimate_series_resistance(voltage, current, vmp, imp)
        rsh = PVCalculations.estimate_shunt_resistance(voltage, current)

        return IVCurveParameters(
            isc=isc,
            voc=voc,
            imp=imp,
            vmp=vmp,
            pmax=pmax,
            ff=ff,
            efficiency=efficiency,
            rs=rs,
            rsh=rsh
        )

    @staticmethod
    def estimate_series_resistance(voltage: np.ndarray, current: np.ndarray,
                                   vmp: float, imp: float) -> float:
        """
        Estimate series resistance from I-V curve.

        Args:
            voltage: Voltage array (V)
            current: Current array (A)
            vmp: Voltage at maximum power (V)
            imp: Current at maximum power (A)

        Returns:
            Estimated series resistance (Ω)
        """
        # Use slope near Voc
        mask = voltage > (vmp + 0.3 * (np.max(voltage) - vmp))
        if np.sum(mask) < 2:
            return 0.0

        slope = np.polyfit(voltage[mask], current[mask], 1)[0]
        rs = -1 / slope if slope != 0 else 0.0
        return max(0, rs)

    @staticmethod
    def estimate_shunt_resistance(voltage: np.ndarray, current: np.ndarray) -> float:
        """
        Estimate shunt resistance from I-V curve.

        Args:
            voltage: Voltage array (V)
            current: Current array (A)

        Returns:
            Estimated shunt resistance (Ω)
        """
        # Use slope near Isc
        mask = voltage < (0.1 * np.max(voltage))
        if np.sum(mask) < 2:
            return np.inf

        slope = np.polyfit(voltage[mask], current[mask], 1)[0]
        rsh = 1 / slope if slope != 0 else np.inf
        return max(0, rsh)

    @staticmethod
    def correct_to_stc(pmax: float, temp_cell: float, irradiance: float,
                      temp_coeff: float = -0.0045,
                      temp_ref: float = 25.0,
                      irr_ref: float = 1000.0) -> float:
        """
        Correct measured power to STC conditions.

        Args:
            pmax: Measured maximum power (W)
            temp_cell: Cell temperature (°C)
            irradiance: Measured irradiance (W/m²)
            temp_coeff: Temperature coefficient of power (%/°C)
            temp_ref: Reference temperature (°C)
            irr_ref: Reference irradiance (W/m²)

        Returns:
            Power corrected to STC (W)
        """
        if irradiance == 0:
            return 0.0

        # Irradiance correction
        p_corrected = pmax * (irr_ref / irradiance)

        # Temperature correction
        temp_diff = temp_cell - temp_ref
        temp_factor = 1 + (temp_coeff * temp_diff)
        p_stc = p_corrected / temp_factor

        return p_stc

    @staticmethod
    def calculate_temperature_coefficients(temp: np.ndarray,
                                          isc: np.ndarray,
                                          voc: np.ndarray,
                                          pmax: np.ndarray) -> Dict[str, float]:
        """
        Calculate temperature coefficients from measurements at different temperatures.

        Args:
            temp: Temperature array (°C)
            isc: Short-circuit current array (A)
            voc: Open-circuit voltage array (V)
            pmax: Maximum power array (W)

        Returns:
            Dict with temperature coefficients
        """
        # Linear fit for each parameter
        isc_coeff = np.polyfit(temp, isc, 1)[0]
        voc_coeff = np.polyfit(temp, voc, 1)[0]
        pmax_coeff = np.polyfit(temp, pmax, 1)[0]

        # Normalize to percentage per degree
        isc_ref = np.mean(isc)
        voc_ref = np.mean(voc)
        pmax_ref = np.mean(pmax)

        return {
            "alpha_isc": (isc_coeff / isc_ref) * 100 if isc_ref != 0 else 0,  # %/°C
            "beta_voc": (voc_coeff / voc_ref) * 100 if voc_ref != 0 else 0,  # %/°C
            "gamma_pmax": (pmax_coeff / pmax_ref) * 100 if pmax_ref != 0 else 0,  # %/°C
        }

    @staticmethod
    def calculate_degradation_rate(time: np.ndarray, power: np.ndarray,
                                   method: str = "linear") -> Dict[str, float]:
        """
        Calculate degradation rate from time-series power measurements.

        Args:
            time: Time array (hours or years)
            power: Normalized power array (%)
            method: Method to use ("linear", "exponential")

        Returns:
            Dict with degradation parameters
        """
        if method == "linear":
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(time, power)

            return {
                "degradation_rate": -slope,  # %/time unit
                "initial_power": intercept,
                "r_squared": r_value**2,
                "p_value": p_value,
                "std_error": std_err
            }

        elif method == "exponential":
            # Exponential fit: P(t) = P0 * exp(-k*t)
            def exp_func(t, p0, k):
                return p0 * np.exp(-k * t)

            try:
                params, _ = optimize.curve_fit(exp_func, time, power, p0=[100, 0.001])
                p0, k = params

                return {
                    "degradation_rate": k * 100,  # Convert to %
                    "initial_power": p0,
                    "decay_constant": k
                }
            except:
                return PVCalculations.calculate_degradation_rate(time, power, "linear")

        else:
            raise ValueError(f"Unknown method: {method}")


class StatisticalAnalysis:
    """Statistical analysis utilities for test data"""

    @staticmethod
    def calculate_uncertainty(data: np.ndarray,
                            confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate measurement uncertainty.

        Args:
            data: Data array
            confidence_level: Confidence level (default 95%)

        Returns:
            Dict with uncertainty metrics
        """
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        se = std / np.sqrt(n)

        # t-distribution for confidence interval
        df = n - 1
        t_critical = stats.t.ppf((1 + confidence_level) / 2, df)
        margin_error = t_critical * se

        return {
            "mean": mean,
            "std": std,
            "standard_error": se,
            "confidence_level": confidence_level,
            "confidence_interval_lower": mean - margin_error,
            "confidence_interval_upper": mean + margin_error,
            "margin_of_error": margin_error,
            "relative_uncertainty_pct": (margin_error / mean * 100) if mean != 0 else 0
        }

    @staticmethod
    def detect_outliers(data: np.ndarray, method: str = "zscore",
                       threshold: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect outliers in data.

        Args:
            data: Data array
            method: Method to use ("zscore", "iqr", "modified_zscore")
            threshold: Threshold for outlier detection

        Returns:
            Tuple of (outlier_indices, outlier_values)
        """
        if method == "zscore":
            z_scores = np.abs(stats.zscore(data))
            outlier_mask = z_scores > threshold

        elif method == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - (threshold * iqr)
            upper_bound = q3 + (threshold * iqr)
            outlier_mask = (data < lower_bound) | (data > upper_bound)

        elif method == "modified_zscore":
            median = np.median(data)
            mad = np.median(np.abs(data - median))
            modified_z = 0.6745 * (data - median) / mad if mad != 0 else np.zeros_like(data)
            outlier_mask = np.abs(modified_z) > threshold

        else:
            raise ValueError(f"Unknown method: {method}")

        outlier_indices = np.where(outlier_mask)[0]
        outlier_values = data[outlier_mask]

        return outlier_indices, outlier_values

    @staticmethod
    def calculate_process_capability(data: np.ndarray,
                                    lower_spec: float,
                                    upper_spec: float) -> Dict[str, float]:
        """
        Calculate process capability indices.

        Args:
            data: Process data array
            lower_spec: Lower specification limit
            upper_spec: Upper specification limit

        Returns:
            Dict with Cp, Cpk, Pp, Ppk indices
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)

        # Process capability indices
        cp = (upper_spec - lower_spec) / (6 * std) if std != 0 else 0
        cpu = (upper_spec - mean) / (3 * std) if std != 0 else 0
        cpl = (mean - lower_spec) / (3 * std) if std != 0 else 0
        cpk = min(cpu, cpl)

        # Performance indices (using population std)
        std_pop = np.std(data)
        pp = (upper_spec - lower_spec) / (6 * std_pop) if std_pop != 0 else 0
        ppu = (upper_spec - mean) / (3 * std_pop) if std_pop != 0 else 0
        ppl = (mean - lower_spec) / (3 * std_pop) if std_pop != 0 else 0
        ppk = min(ppu, ppl)

        return {
            "cp": cp,
            "cpk": cpk,
            "pp": pp,
            "ppk": ppk,
            "cpu": cpu,
            "cpl": cpl
        }

    @staticmethod
    def perform_normality_test(data: np.ndarray) -> Dict[str, Any]:
        """
        Perform normality test on data.

        Args:
            data: Data array

        Returns:
            Dict with test results
        """
        # Shapiro-Wilk test
        shapiro_stat, shapiro_p = stats.shapiro(data)

        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.kstest(data, 'norm',
                                     args=(np.mean(data), np.std(data)))

        # Anderson-Darling test
        anderson_result = stats.anderson(data)

        return {
            "shapiro_wilk": {
                "statistic": shapiro_stat,
                "p_value": shapiro_p,
                "is_normal": shapiro_p > 0.05
            },
            "kolmogorov_smirnov": {
                "statistic": ks_stat,
                "p_value": ks_p,
                "is_normal": ks_p > 0.05
            },
            "anderson_darling": {
                "statistic": anderson_result.statistic,
                "critical_values": anderson_result.critical_values.tolist(),
                "significance_levels": anderson_result.significance_level.tolist()
            }
        }

    @staticmethod
    def calculate_correlation_matrix(df: pd.DataFrame,
                                    method: str = "pearson") -> pd.DataFrame:
        """
        Calculate correlation matrix for DataFrame.

        Args:
            df: DataFrame with numeric columns
            method: Correlation method ("pearson", "spearman", "kendall")

        Returns:
            Correlation matrix DataFrame
        """
        return df.corr(method=method)
