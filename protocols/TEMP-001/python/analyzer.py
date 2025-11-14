"""
Temperature Coefficient Analyzer for TEMP-001 Protocol

Implements IEC 60891:2021 procedures for determining temperature coefficients
of photovoltaic modules.

Author: ASA PV Testing
Date: 2025-11-14
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from dataclasses import dataclass, asdict
import warnings


@dataclass
class TemperatureCoefficients:
    """Temperature coefficient results according to IEC 60891"""

    # Power coefficients
    alpha_pmp_relative: float  # %/°C
    alpha_pmp_absolute: float  # W/°C
    r_squared_pmp: float

    # Voltage coefficients
    beta_voc_relative: float  # %/°C
    beta_voc_absolute: float  # V/°C
    r_squared_voc: float

    # Current coefficients
    alpha_isc_relative: float  # %/°C
    alpha_isc_absolute: float  # A/°C
    r_squared_isc: float

    # STC-corrected values
    pmp_at_stc: float  # W
    voc_at_stc: float  # V
    isc_at_stc: float  # A

    # Temperature reference
    reference_temperature: float = 25.0  # °C
    reference_irradiance: float = 1000.0  # W/m²

    # Regression details
    pmp_slope: float = 0.0
    pmp_intercept: float = 0.0
    voc_slope: float = 0.0
    voc_intercept: float = 0.0
    isc_slope: float = 0.0
    isc_intercept: float = 0.0

    # Data quality metrics
    num_points: int = 0
    temperature_range: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class TemperatureCoefficientAnalyzer:
    """
    Analyzer for determining temperature coefficients of PV modules
    according to IEC 60891:2021
    """

    def __init__(self, protocol_config_path: Optional[str] = None):
        """
        Initialize analyzer

        Args:
            protocol_config_path: Path to protocol.json configuration file
        """
        self.config = self._load_config(protocol_config_path)
        self.data = None
        self.results = None
        self._reference_temp = 25.0  # °C (STC)
        self._reference_irradiance = 1000.0  # W/m² (STC)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load protocol configuration"""
        if config_path is None:
            # Default to protocol.json in same directory structure
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "protocol.json"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            warnings.warn(f"Configuration file not found: {config_path}")
            return {}

    def load_data(
        self,
        data: Union[pd.DataFrame, Dict, str, Path]
    ) -> pd.DataFrame:
        """
        Load measurement data

        Args:
            data: DataFrame, dictionary, or path to CSV/JSON file

        Returns:
            Loaded DataFrame
        """
        if isinstance(data, pd.DataFrame):
            self.data = data.copy()
        elif isinstance(data, dict):
            self.data = pd.DataFrame(data)
        elif isinstance(data, (str, Path)):
            file_path = Path(data)
            if file_path.suffix == '.csv':
                self.data = pd.read_csv(file_path)
            elif file_path.suffix == '.json':
                self.data = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        # Ensure required columns exist
        required_columns = ['module_temperature', 'pmax', 'voc', 'isc']
        missing = [col for col in required_columns if col not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        return self.data

    def normalize_to_irradiance(
        self,
        target_irradiance: float = 1000.0
    ) -> pd.DataFrame:
        """
        Normalize measurements to target irradiance

        Args:
            target_irradiance: Target irradiance in W/m² (default: 1000)

        Returns:
            DataFrame with normalized values
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        if 'irradiance' not in self.data.columns:
            warnings.warn("Irradiance column not found. Assuming 1000 W/m²")
            return self.data

        # Normalize current and power to target irradiance
        # Per IEC 60891, Isc scales linearly with irradiance
        irrad_ratio = target_irradiance / self.data['irradiance']

        self.data['isc_normalized'] = self.data['isc'] * irrad_ratio
        self.data['pmax_normalized'] = self.data['pmax'] * irrad_ratio

        # Voltage is less affected by irradiance, but apply logarithmic correction
        # ΔV ≈ n·k·T/q · ln(G2/G1) where n is ideality factor (~1.3 for Si)
        # For small irradiance variations, this is often negligible
        self.data['voc_normalized'] = self.data['voc']  # Simplified

        return self.data

    def calculate_linear_regression(
        self,
        x: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, float, float, float, float]:
        """
        Perform linear regression and calculate statistics

        Args:
            x: Independent variable (temperature)
            y: Dependent variable (Pmp, Voc, or Isc)

        Returns:
            Tuple of (slope, intercept, r_squared, std_err, p_value)
        """
        # Remove any NaN values
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]

        if len(x_clean) < 2:
            raise ValueError("Insufficient data points for regression")

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x_clean, y_clean
        )

        r_squared = r_value ** 2

        return slope, intercept, r_squared, std_err, p_value

    def calculate_temperature_coefficients(self) -> TemperatureCoefficients:
        """
        Calculate temperature coefficients according to IEC 60891

        Returns:
            TemperatureCoefficients object with all results
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Normalize to reference irradiance if needed
        if 'irradiance' in self.data.columns:
            self.normalize_to_irradiance(self._reference_irradiance)
            use_normalized = True
        else:
            use_normalized = False

        # Extract temperature and parameters
        temp = self.data['module_temperature'].values
        pmax = (self.data['pmax_normalized'].values if use_normalized
                else self.data['pmax'].values)
        voc = (self.data['voc_normalized'].values if use_normalized
               else self.data['voc'].values)
        isc = (self.data['isc_normalized'].values if use_normalized
               else self.data['isc'].values)

        # Calculate data quality metrics
        num_points = len(temp)
        temp_range = temp.max() - temp.min()

        # 1. Power temperature coefficient (α_Pmp or γ)
        pmp_slope, pmp_intercept, r2_pmp, _, _ = self.calculate_linear_regression(
            temp, pmax
        )

        # Calculate value at reference temperature
        pmp_at_ref = pmp_slope * self._reference_temp + pmp_intercept

        # Relative coefficient: %/°C
        alpha_pmp_relative = (pmp_slope / pmp_at_ref) * 100.0
        # Absolute coefficient: W/°C
        alpha_pmp_absolute = pmp_slope

        # 2. Voltage temperature coefficient (β_Voc)
        voc_slope, voc_intercept, r2_voc, _, _ = self.calculate_linear_regression(
            temp, voc
        )

        voc_at_ref = voc_slope * self._reference_temp + voc_intercept

        # Relative coefficient: %/°C
        beta_voc_relative = (voc_slope / voc_at_ref) * 100.0
        # Absolute coefficient: V/°C
        beta_voc_absolute = voc_slope

        # 3. Current temperature coefficient (α_Isc)
        isc_slope, isc_intercept, r2_isc, _, _ = self.calculate_linear_regression(
            temp, isc
        )

        isc_at_ref = isc_slope * self._reference_temp + isc_intercept

        # Relative coefficient: %/°C
        alpha_isc_relative = (isc_slope / isc_at_ref) * 100.0
        # Absolute coefficient: A/°C
        alpha_isc_absolute = isc_slope

        # Create results object
        self.results = TemperatureCoefficients(
            alpha_pmp_relative=alpha_pmp_relative,
            alpha_pmp_absolute=alpha_pmp_absolute,
            r_squared_pmp=r2_pmp,
            beta_voc_relative=beta_voc_relative,
            beta_voc_absolute=beta_voc_absolute,
            r_squared_voc=r2_voc,
            alpha_isc_relative=alpha_isc_relative,
            alpha_isc_absolute=alpha_isc_absolute,
            r_squared_isc=r2_isc,
            pmp_at_stc=pmp_at_ref,
            voc_at_stc=voc_at_ref,
            isc_at_stc=isc_at_ref,
            reference_temperature=self._reference_temp,
            reference_irradiance=self._reference_irradiance,
            pmp_slope=pmp_slope,
            pmp_intercept=pmp_intercept,
            voc_slope=voc_slope,
            voc_intercept=voc_intercept,
            isc_slope=isc_slope,
            isc_intercept=isc_intercept,
            num_points=num_points,
            temperature_range=temp_range
        )

        return self.results

    def correct_to_stc(
        self,
        temperature: float,
        pmax: float,
        voc: float,
        isc: float,
        irradiance: float = 1000.0
    ) -> Dict[str, float]:
        """
        Correct a single measurement to STC using calculated coefficients

        Args:
            temperature: Module temperature in °C
            pmax: Maximum power in W
            voc: Open circuit voltage in V
            isc: Short circuit current in A
            irradiance: Irradiance in W/m² (default: 1000)

        Returns:
            Dictionary with STC-corrected values
        """
        if self.results is None:
            raise ValueError("No results available. Run calculate_temperature_coefficients() first.")

        # Temperature difference from STC
        delta_t = self._reference_temp - temperature

        # Irradiance ratio
        g_ratio = self._reference_irradiance / irradiance

        # Apply IEC 60891 corrections
        pmax_stc = pmax * g_ratio * (
            1 + (self.results.alpha_pmp_relative / 100.0) * delta_t
        )

        voc_stc = voc + self.results.beta_voc_absolute * delta_t

        isc_stc = isc * g_ratio * (
            1 + (self.results.alpha_isc_relative / 100.0) * delta_t
        )

        return {
            'pmax_stc': pmax_stc,
            'voc_stc': voc_stc,
            'isc_stc': isc_stc,
            'temperature': temperature,
            'irradiance': irradiance
        }

    def calculate_residuals(self) -> pd.DataFrame:
        """
        Calculate regression residuals for quality assessment

        Returns:
            DataFrame with residual values
        """
        if self.data is None or self.results is None:
            raise ValueError("Data and results required. Run analysis first.")

        temp = self.data['module_temperature'].values

        # Calculate predicted values
        pmax_pred = self.results.pmp_slope * temp + self.results.pmp_intercept
        voc_pred = self.results.voc_slope * temp + self.results.voc_intercept
        isc_pred = self.results.isc_slope * temp + self.results.isc_intercept

        # Use normalized values if available
        pmax_actual = (self.data['pmax_normalized'].values
                      if 'pmax_normalized' in self.data.columns
                      else self.data['pmax'].values)
        voc_actual = (self.data['voc_normalized'].values
                     if 'voc_normalized' in self.data.columns
                     else self.data['voc'].values)
        isc_actual = (self.data['isc_normalized'].values
                     if 'isc_normalized' in self.data.columns
                     else self.data['isc'].values)

        # Calculate residuals
        residuals = pd.DataFrame({
            'temperature': temp,
            'pmax_residual': pmax_actual - pmax_pred,
            'voc_residual': voc_actual - voc_pred,
            'isc_residual': isc_actual - isc_pred,
            'pmax_predicted': pmax_pred,
            'voc_predicted': voc_pred,
            'isc_predicted': isc_pred
        })

        return residuals

    def get_summary(self) -> Dict:
        """
        Get a summary of analysis results

        Returns:
            Dictionary with formatted summary
        """
        if self.results is None:
            raise ValueError("No results available. Run analysis first.")

        summary = {
            'test_info': {
                'protocol': 'TEMP-001',
                'standard': 'IEC 60891:2021',
                'num_measurements': self.results.num_points,
                'temperature_range': f"{self.results.temperature_range:.1f} °C"
            },
            'temperature_coefficients': {
                'power': {
                    'relative': f"{self.results.alpha_pmp_relative:.4f} %/°C",
                    'absolute': f"{self.results.alpha_pmp_absolute:.4f} W/°C",
                    'r_squared': f"{self.results.r_squared_pmp:.4f}"
                },
                'voltage': {
                    'relative': f"{self.results.beta_voc_relative:.4f} %/°C",
                    'absolute': f"{self.results.beta_voc_absolute:.5f} V/°C",
                    'r_squared': f"{self.results.r_squared_voc:.4f}"
                },
                'current': {
                    'relative': f"{self.results.alpha_isc_relative:.4f} %/°C",
                    'absolute': f"{self.results.alpha_isc_absolute:.5f} A/°C",
                    'r_squared': f"{self.results.r_squared_isc:.4f}"
                }
            },
            'stc_performance': {
                'pmax': f"{self.results.pmp_at_stc:.2f} W",
                'voc': f"{self.results.voc_at_stc:.3f} V",
                'isc': f"{self.results.isc_at_stc:.3f} A"
            }
        }

        return summary

    def export_results(
        self,
        output_path: Union[str, Path],
        format: str = 'json'
    ) -> None:
        """
        Export results to file

        Args:
            output_path: Output file path
            format: Export format ('json', 'csv', or 'excel')
        """
        if self.results is None:
            raise ValueError("No results to export. Run analysis first.")

        output_path = Path(output_path)

        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results.to_dict(), f, indent=2)

        elif format == 'csv':
            df = pd.DataFrame([self.results.to_dict()])
            df.to_csv(output_path, index=False)

        elif format == 'excel':
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Results sheet
                df_results = pd.DataFrame([self.results.to_dict()])
                df_results.to_excel(writer, sheet_name='Results', index=False)

                # Raw data sheet
                if self.data is not None:
                    self.data.to_excel(writer, sheet_name='Raw Data', index=False)

                # Residuals sheet
                residuals = self.calculate_residuals()
                residuals.to_excel(writer, sheet_name='Residuals', index=False)

        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Example usage"""
    # Sample data
    sample_data = {
        'module_temperature': [20, 30, 40, 50, 60, 70],
        'pmax': [260, 252, 244, 236, 228, 220],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'irradiance': [1000, 1000, 1000, 1000, 1000, 1000]
    }

    # Initialize analyzer
    analyzer = TemperatureCoefficientAnalyzer()

    # Load data
    analyzer.load_data(sample_data)

    # Calculate coefficients
    results = analyzer.calculate_temperature_coefficients()

    # Print summary
    print("Temperature Coefficient Analysis Results")
    print("=" * 50)
    summary = analyzer.get_summary()
    print(json.dumps(summary, indent=2))

    # Calculate residuals
    residuals = analyzer.calculate_residuals()
    print("\nResiduals:")
    print(residuals)


if __name__ == "__main__":
    main()
