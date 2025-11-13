"""
LETID-001 Test Protocol Data Processing Module

This module provides data processing and analysis functions for LeTID test data.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class LETID001Processor:
    """Processor for LETID-001 test protocol data analysis."""

    def __init__(self, protocol_schema_path: str = None):
        """
        Initialize processor with protocol schema.

        Args:
            protocol_schema_path: Path to protocol.json schema file
        """
        if protocol_schema_path is None:
            protocol_schema_path = Path(__file__).parent.parent / "schemas" / "protocol.json"

        with open(protocol_schema_path, 'r') as f:
            self.schema = json.load(f)

    def calculate_degradation(self, initial_pmax: float, final_pmax: float) -> float:
        """
        Calculate power degradation percentage.

        Args:
            initial_pmax: Initial maximum power (W)
            final_pmax: Final maximum power (W)

        Returns:
            Degradation percentage (negative indicates loss)
        """
        return ((final_pmax - initial_pmax) / initial_pmax) * 100

    def calculate_degradation_rate(self, degradation_percent: float,
                                   exposure_hours: float) -> float:
        """
        Calculate degradation rate per hour.

        Args:
            degradation_percent: Total degradation (%)
            exposure_hours: Total exposure time (hours)

        Returns:
            Degradation rate (%/hour)
        """
        if exposure_hours <= 0:
            return 0.0
        return degradation_percent / exposure_hours

    def normalize_power(self, pmax: float, initial_pmax: float) -> float:
        """
        Calculate normalized power relative to initial.

        Args:
            pmax: Current maximum power (W)
            initial_pmax: Initial maximum power (W)

        Returns:
            Normalized power (%)
        """
        return (pmax / initial_pmax) * 100

    def process_time_series(self, time_series_data: List[Dict[str, Any]],
                           initial_pmax: float) -> pd.DataFrame:
        """
        Process time series data into pandas DataFrame with calculated fields.

        Args:
            time_series_data: List of periodic measurements
            initial_pmax: Initial maximum power for normalization

        Returns:
            DataFrame with processed time series data
        """
        df = pd.DataFrame(time_series_data)

        # Convert timestamp if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calculate normalized power
        if 'pmax' in df.columns:
            df['normalized_power'] = df['pmax'].apply(
                lambda x: self.normalize_power(x, initial_pmax)
            )
            df['degradation_percent'] = df['pmax'].apply(
                lambda x: self.calculate_degradation(initial_pmax, x)
            )

        # Calculate instantaneous degradation rate
        if 'elapsed_hours' in df.columns and 'degradation_percent' in df.columns:
            df['degradation_rate'] = df['degradation_percent'] / df['elapsed_hours']
            df['degradation_rate'] = df['degradation_rate'].replace([np.inf, -np.inf], 0)

        return df

    def detect_stabilization(self, df: pd.DataFrame,
                           window_hours: int = 48,
                           threshold_percent: float = 0.5) -> Optional[float]:
        """
        Detect when degradation has stabilized.

        Args:
            df: DataFrame with time series data
            window_hours: Time window to check for stability (hours)
            threshold_percent: Maximum allowed variation for stability (%)

        Returns:
            Elapsed hours when stabilization occurred, or None if not stabilized
        """
        if 'normalized_power' not in df.columns or 'elapsed_hours' not in df.columns:
            return None

        if len(df) < 2:
            return None

        for i in range(len(df) - 1):
            # Get measurements within window after this point
            current_time = df.iloc[i]['elapsed_hours']
            window_end = current_time + window_hours

            window_data = df[
                (df['elapsed_hours'] >= current_time) &
                (df['elapsed_hours'] <= window_end)
            ]

            if len(window_data) < 2:
                continue

            # Check variation in normalized power
            power_variation = window_data['normalized_power'].max() - \
                            window_data['normalized_power'].min()

            if power_variation <= threshold_percent:
                return current_time

        return None

    def calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistical summary of test data.

        Args:
            df: DataFrame with time series data

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_measurements': len(df),
            'duration_hours': 0,
            'power_stats': {},
            'environmental_stats': {}
        }

        if 'elapsed_hours' in df.columns:
            stats['duration_hours'] = df['elapsed_hours'].max()

        # Power statistics
        if 'normalized_power' in df.columns:
            stats['power_stats'] = {
                'min_normalized_power': float(df['normalized_power'].min()),
                'max_normalized_power': float(df['normalized_power'].max()),
                'final_normalized_power': float(df['normalized_power'].iloc[-1]),
                'mean_normalized_power': float(df['normalized_power'].mean()),
                'std_normalized_power': float(df['normalized_power'].std())
            }

        if 'degradation_percent' in df.columns:
            stats['power_stats']['max_degradation'] = float(df['degradation_percent'].min())
            stats['power_stats']['final_degradation'] = float(df['degradation_percent'].iloc[-1])

        # Environmental statistics
        if 'module_temp' in df.columns:
            stats['environmental_stats']['temperature'] = {
                'mean': float(df['module_temp'].mean()),
                'std': float(df['module_temp'].std()),
                'min': float(df['module_temp'].min()),
                'max': float(df['module_temp'].max())
            }

        if 'irradiance' in df.columns:
            stats['environmental_stats']['irradiance'] = {
                'mean': float(df['irradiance'].mean()),
                'std': float(df['irradiance'].std()),
                'min': float(df['irradiance'].min()),
                'max': float(df['irradiance'].max())
            }

        return stats

    def fit_degradation_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Fit exponential degradation model to data.

        Args:
            df: DataFrame with time series data

        Returns:
            Dictionary with model parameters and fit quality
        """
        if 'elapsed_hours' not in df.columns or 'normalized_power' not in df.columns:
            return {'error': 'Required columns not found'}

        if len(df) < 3:
            return {'error': 'Insufficient data points for fitting'}

        x = df['elapsed_hours'].values
        y = df['normalized_power'].values

        try:
            # Fit linear degradation (simple model)
            coeffs = np.polyfit(x, y, 1)
            y_fit = np.polyval(coeffs, x)
            r_squared = 1 - (np.sum((y - y_fit) ** 2) / np.sum((y - np.mean(y)) ** 2))

            model = {
                'model_type': 'linear',
                'slope': float(coeffs[0]),
                'intercept': float(coeffs[1]),
                'r_squared': float(r_squared),
                'predicted_300h_power': float(coeffs[0] * 300 + coeffs[1])
            }

            # Try exponential fit if degradation is non-linear
            if len(df) >= 5:
                try:
                    # Log transform for exponential fit
                    log_y = np.log(y / 100)  # Normalize to 1.0
                    exp_coeffs = np.polyfit(x, log_y, 1)
                    exp_y_fit = 100 * np.exp(np.polyval(exp_coeffs, x))
                    exp_r_squared = 1 - (np.sum((y - exp_y_fit) ** 2) /
                                        np.sum((y - np.mean(y)) ** 2))

                    if exp_r_squared > r_squared:
                        model = {
                            'model_type': 'exponential',
                            'decay_rate': float(exp_coeffs[0]),
                            'initial_value': float(np.exp(exp_coeffs[1]) * 100),
                            'r_squared': float(exp_r_squared),
                            'predicted_300h_power': float(100 * np.exp(
                                exp_coeffs[0] * 300 + exp_coeffs[1]
                            ))
                        }
                except (RuntimeError, ValueError):
                    pass  # Keep linear model

            return model

        except Exception as e:
            return {'error': f'Model fitting failed: {str(e)}'}

    def generate_analysis_report(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report.

        Args:
            test_data: Complete test data dictionary

        Returns:
            Analysis report dictionary
        """
        report = {
            'protocol_id': self.schema['id'],
            'protocol_version': self.schema['version'],
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'sample_info': test_data.get('sample_info', {}),
            'results': {}
        }

        # Extract initial and final measurements
        initial = test_data.get('initial_characterization', {})
        final = test_data.get('final_characterization', {})

        if initial and final:
            initial_pmax = initial.get('pmax')
            final_pmax = final.get('pmax')

            if initial_pmax and final_pmax:
                report['results']['initial_pmax'] = initial_pmax
                report['results']['final_pmax'] = final_pmax
                report['results']['degradation_percent'] = self.calculate_degradation(
                    initial_pmax, final_pmax
                )

                # Process time series
                if 'time_series' in test_data:
                    df = self.process_time_series(
                        test_data['time_series'],
                        initial_pmax
                    )

                    report['results']['statistics'] = self.calculate_statistics(df)
                    report['results']['degradation_model'] = self.fit_degradation_model(df)

                    stabilization_point = self.detect_stabilization(df)
                    if stabilization_point:
                        report['results']['stabilization_hours'] = stabilization_point

                    # Export processed data
                    report['processed_time_series'] = df.to_dict(orient='records')

        return report

    def export_to_csv(self, df: pd.DataFrame, output_path: str):
        """
        Export processed data to CSV.

        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        df.to_csv(output_path, index=False)

    def export_to_json(self, data: Dict[str, Any], output_path: str):
        """
        Export data to JSON.

        Args:
            data: Dictionary to export
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
