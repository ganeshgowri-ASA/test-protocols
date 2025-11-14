"""
Data Processor - Process and analyze test data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and analyze test protocol data."""

    def __init__(self, protocol_manager=None):
        """
        Initialize the data processor.

        Args:
            protocol_manager: ProtocolManager instance for accessing protocol info
        """
        self.protocol_manager = protocol_manager

    def process_raw_data(
        self,
        protocol_id: str,
        raw_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Process raw test data into structured DataFrame.

        Args:
            protocol_id: Protocol identifier
            raw_data: Raw test data dictionary

        Returns:
            Processed data as DataFrame
        """
        if protocol_id == "conc-001":
            return self._process_conc001_data(raw_data)
        else:
            # Generic processing
            measurements = raw_data.get("measurements", [])
            return pd.DataFrame(measurements)

    def _process_conc001_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process CONC-001 concentration testing data.

        Args:
            raw_data: Raw test data

        Returns:
            Processed DataFrame with calculated fields
        """
        measurements = raw_data.get("measurements", [])
        df = pd.DataFrame(measurements)

        if df.empty:
            return df

        # Calculate derived parameters
        if all(col in df.columns for col in ['vmp', 'imp']):
            df['power_w'] = df['vmp'] * df['imp']

        if all(col in df.columns for col in ['voc', 'isc', 'vmp', 'imp']):
            df['fill_factor_calc'] = (df['vmp'] * df['imp']) / (df['voc'] * df['isc'])

        # Calculate normalized efficiency (relative to 1 sun)
        if 'efficiency' in df.columns and 'concentration_suns' in df.columns:
            one_sun_eff = df[df['concentration_suns'] == 1]['efficiency'].values
            if len(one_sun_eff) > 0:
                df['efficiency_normalized'] = df['efficiency'] / one_sun_eff[0]

        # Add metadata columns
        df['test_run_id'] = raw_data.get('test_run_id', '')
        df['sample_id'] = raw_data.get('sample_id', '')
        df['operator'] = raw_data.get('operator', '')
        df['timestamp'] = raw_data.get('timestamp', datetime.now().isoformat())

        # Sort by concentration
        if 'concentration_suns' in df.columns:
            df = df.sort_values('concentration_suns')

        return df

    def calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistical summary of test data.

        Args:
            df: Test data DataFrame

        Returns:
            Dictionary of statistical measures
        """
        stats = {}

        # Numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            stats[col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median())
            }

        return stats

    def calculate_temperature_coefficient(
        self,
        df: pd.DataFrame,
        parameter: str = 'efficiency'
    ) -> Optional[float]:
        """
        Calculate temperature coefficient for a parameter.

        Args:
            df: Test data DataFrame
            parameter: Parameter to analyze (e.g., 'efficiency', 'voc')

        Returns:
            Temperature coefficient (%/°C) or None if insufficient data
        """
        if parameter not in df.columns or 'temperature_c' not in df.columns:
            return None

        if len(df) < 3:
            return None

        # Linear regression: parameter vs temperature
        temps = df['temperature_c'].values
        values = df[parameter].values

        # Remove NaN values
        valid_idx = ~(np.isnan(temps) | np.isnan(values))
        temps = temps[valid_idx]
        values = values[valid_idx]

        if len(temps) < 3:
            return None

        # Calculate slope using numpy polyfit
        slope, intercept = np.polyfit(temps, values, 1)

        # Normalize to reference value at 25°C
        ref_value = intercept + slope * 25

        if ref_value != 0:
            # Temperature coefficient as %/°C
            temp_coeff = (slope / ref_value) * 100
            return float(temp_coeff)

        return None

    def calculate_concentration_coefficient(
        self,
        df: pd.DataFrame,
        parameter: str = 'efficiency'
    ) -> Optional[float]:
        """
        Calculate concentration coefficient for a parameter.

        Args:
            df: Test data DataFrame
            parameter: Parameter to analyze

        Returns:
            Concentration coefficient or None if insufficient data
        """
        if parameter not in df.columns or 'concentration_suns' not in df.columns:
            return None

        if len(df) < 3:
            return None

        # Filter to same temperature
        # Group by temperature and find most common
        if 'temperature_c' in df.columns:
            temp_counts = df['temperature_c'].value_counts()
            if len(temp_counts) > 0:
                most_common_temp = temp_counts.index[0]
                df_filtered = df[df['temperature_c'] == most_common_temp]
            else:
                df_filtered = df
        else:
            df_filtered = df

        if len(df_filtered) < 3:
            return None

        concentrations = df_filtered['concentration_suns'].values
        values = df_filtered[parameter].values

        # Remove NaN values
        valid_idx = ~(np.isnan(concentrations) | np.isnan(values))
        concentrations = concentrations[valid_idx]
        values = values[valid_idx]

        if len(concentrations) < 3:
            return None

        # Calculate slope
        slope, intercept = np.polyfit(concentrations, values, 1)

        return float(slope)

    def identify_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = 'iqr'
    ) -> List[int]:
        """
        Identify outliers in a data column.

        Args:
            df: Test data DataFrame
            column: Column to analyze
            method: Outlier detection method ('iqr' or 'zscore')

        Returns:
            List of row indices containing outliers
        """
        if column not in df.columns:
            return []

        values = df[column].values
        outlier_indices = []

        if method == 'iqr':
            # Interquartile range method
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_indices = df[
                (df[column] < lower_bound) | (df[column] > upper_bound)
            ].index.tolist()

        elif method == 'zscore':
            # Z-score method
            mean = np.mean(values)
            std = np.std(values)

            if std > 0:
                z_scores = np.abs((values - mean) / std)
                outlier_indices = df[z_scores > 3].index.tolist()

        return outlier_indices

    def generate_summary_report(
        self,
        protocol_id: str,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary report.

        Args:
            protocol_id: Protocol identifier
            raw_data: Raw test data

        Returns:
            Summary report dictionary
        """
        df = self.process_raw_data(protocol_id, raw_data)

        report = {
            "protocol_id": protocol_id,
            "test_run_id": raw_data.get("test_run_id", ""),
            "sample_id": raw_data.get("sample_id", ""),
            "timestamp": raw_data.get("timestamp", ""),
            "operator": raw_data.get("operator", ""),
            "data_summary": {
                "total_measurements": len(df),
                "concentration_range": {
                    "min": float(df['concentration_suns'].min()) if 'concentration_suns' in df.columns else None,
                    "max": float(df['concentration_suns'].max()) if 'concentration_suns' in df.columns else None
                },
                "temperature_range": {
                    "min": float(df['temperature_c'].min()) if 'temperature_c' in df.columns else None,
                    "max": float(df['temperature_c'].max()) if 'temperature_c' in df.columns else None
                }
            },
            "statistics": self.calculate_statistics(df),
            "analysis": {
                "temperature_coefficient_efficiency": self.calculate_temperature_coefficient(df, 'efficiency'),
                "temperature_coefficient_voc": self.calculate_temperature_coefficient(df, 'voc'),
                "concentration_coefficient_efficiency": self.calculate_concentration_coefficient(df, 'efficiency')
            },
            "quality_indicators": {
                "outliers_efficiency": self.identify_outliers(df, 'efficiency') if 'efficiency' in df.columns else [],
                "outliers_fill_factor": self.identify_outliers(df, 'fill_factor') if 'fill_factor' in df.columns else []
            }
        }

        return report

    def export_to_csv(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Export DataFrame to CSV file.

        Args:
            df: DataFrame to export
            filepath: Output file path
        """
        df.to_csv(filepath, index=False)
        logger.info(f"Data exported to CSV: {filepath}")

    def export_to_excel(
        self,
        data: Dict[str, pd.DataFrame],
        filepath: str
    ) -> None:
        """
        Export multiple DataFrames to Excel file with sheets.

        Args:
            data: Dictionary of {sheet_name: DataFrame}
            filepath: Output file path
        """
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Data exported to Excel: {filepath}")
