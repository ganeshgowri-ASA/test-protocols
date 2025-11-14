"""ENER-001: Energy Rating Test Protocol Implementation.

This module implements the Energy Rating Test protocol according to IEC 61853 standards.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from scipy import interpolate
from datetime import datetime

from ..base_protocol import BaseProtocol
from .analysis import EnergyRatingAnalyzer
from .charts import ChartGenerator
from .qc import QualityChecker


class ENER001Protocol(BaseProtocol):
    """Energy Rating Test Protocol (ENER-001) implementation."""

    PROTOCOL_ID = "ENER-001"
    VERSION = "1.0.0"

    def __init__(self, config_path: str = None):
        """Initialize ENER-001 protocol."""
        super().__init__(config_path)

        # Initialize components
        self.analyzer = EnergyRatingAnalyzer(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.qc_checker = QualityChecker(self.config)

        # Extract configuration
        self.irradiance_levels = self.test_conditions.get("irradiance_levels", {}).get(
            "values", []
        )
        self.temperature_matrix = self.test_conditions.get("temperature_matrix", {}).get(
            "values", []
        )

    def validate_inputs(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate input data for ENER-001 protocol.

        Args:
            data: Input data dictionary or DataFrame data

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Convert to DataFrame if dictionary
        if isinstance(data, dict):
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                errors.append(f"Failed to convert data to DataFrame: {e}")
                return False, errors
        else:
            df = data

        # Validate using base class method
        is_valid, param_errors = self._validate_parameters(df)
        errors.extend(param_errors)

        # Additional ENER-001 specific validations
        required_cols = ["irradiance", "module_temp", "voltage", "current"]
        missing = set(required_cols) - set(df.columns)
        if missing:
            errors.append(f"Missing required columns: {missing}")

        # Check for sufficient data points
        if len(df) < 10:
            errors.append(
                f"Insufficient data points: {len(df)} (minimum 10 required for valid IV curve)"
            )

        return len(errors) == 0, errors

    def run_test(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the energy rating test.

        Args:
            data: Test measurement data with columns:
                - irradiance (W/m²)
                - module_temp (°C)
                - voltage (V)
                - current (A)
                - module_area (m²) - optional, can be set as attribute
                - rated_power (W) - optional, can be set as attribute

        Returns:
            Dictionary containing:
                - measurements: Processed measurement data
                - iv_curves: Extracted IV curves for each test condition
                - analysis: Performance parameters and energy rating
                - qc_results: Quality check results
                - charts: Generated charts
        """
        # Store data
        self.test_data = data.copy()

        # Process measurements
        processed_data = self._process_measurements(data)

        # Extract IV curves for each test condition
        iv_curves = self._extract_iv_curves(processed_data)

        # Analyze data
        analysis_results = self.analyzer.analyze(iv_curves, processed_data)

        # Run quality checks
        qc_results = self.qc_checker.run_checks(processed_data, analysis_results)

        # Generate charts
        charts = self.chart_generator.generate_charts(
            processed_data, iv_curves, analysis_results
        )

        # Compile results
        results = {
            "measurements": processed_data.to_dict(orient="records"),
            "iv_curves": iv_curves,
            "analysis": analysis_results,
            "qc_results": qc_results,
            "charts": charts,
            "test_conditions": {
                "irradiance_levels": self.irradiance_levels,
                "temperature_matrix": self.temperature_matrix,
            },
        }

        # Store results
        self.results = results

        return results

    def _extract_iv_curves(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract IV curves for each test condition.

        Args:
            data: Processed measurement data

        Returns:
            Dictionary of IV curves organized by irradiance and temperature
        """
        iv_curves = {}

        # Group by irradiance and temperature
        grouped = data.groupby(["irradiance", "module_temp"])

        for (irr, temp), group_data in grouped:
            # Sort by voltage
            curve_data = group_data.sort_values("voltage")

            # Calculate power
            curve_data = curve_data.copy()
            curve_data["power"] = curve_data["voltage"] * curve_data["current"]

            # Find maximum power point
            mpp_idx = curve_data["power"].idxmax()
            mpp_data = curve_data.loc[mpp_idx]

            # Extract key points
            iv_curve = {
                "irradiance": float(irr),
                "temperature": float(temp),
                "voltage": curve_data["voltage"].tolist(),
                "current": curve_data["current"].tolist(),
                "power": curve_data["power"].tolist(),
                "voc": float(curve_data["voltage"].max()),
                "isc": float(curve_data["current"].max()),
                "vmpp": float(mpp_data["voltage"]),
                "impp": float(mpp_data["current"]),
                "pmpp": float(mpp_data["power"]),
                "fill_factor": self._calculate_fill_factor(
                    mpp_data["power"],
                    curve_data["voltage"].max(),
                    curve_data["current"].max(),
                ),
                "num_points": len(curve_data),
            }

            # Calculate efficiency if module area is available
            if "module_area" in data.columns:
                module_area = curve_data["module_area"].iloc[0]
                iv_curve["efficiency"] = (
                    (mpp_data["power"] / (irr * module_area) * 100)
                    if irr > 0 and module_area > 0
                    else 0
                )

            key = f"G{int(irr)}_T{int(temp)}"
            iv_curves[key] = iv_curve

        return iv_curves

    def _calculate_fill_factor(self, pmpp: float, voc: float, isc: float) -> float:
        """
        Calculate fill factor.

        Args:
            pmpp: Maximum power point power
            voc: Open circuit voltage
            isc: Short circuit current

        Returns:
            Fill factor as percentage
        """
        if voc > 0 and isc > 0:
            return (pmpp / (voc * isc)) * 100
        return 0.0

    def calculate_temperature_coefficients(
        self, iv_curves: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate temperature coefficients from IV curves.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Dictionary with temperature coefficients
        """
        return self.analyzer.calculate_temperature_coefficients(iv_curves)

    def calculate_energy_rating(
        self, iv_curves: Dict[str, Any], climate: str = "moderate"
    ) -> Dict[str, float]:
        """
        Calculate energy rating according to IEC 61853-3.

        Args:
            iv_curves: Dictionary of IV curves
            climate: Climate zone ('hot', 'moderate', 'cold')

        Returns:
            Dictionary with energy rating results
        """
        return self.analyzer.calculate_energy_rating(iv_curves, climate)

    def interpolate_performance(
        self, iv_curves: Dict[str, Any], target_irr: float, target_temp: float
    ) -> Dict[str, float]:
        """
        Interpolate performance parameters for arbitrary irradiance and temperature.

        Args:
            iv_curves: Dictionary of IV curves
            target_irr: Target irradiance (W/m²)
            target_temp: Target temperature (°C)

        Returns:
            Interpolated performance parameters
        """
        # Extract data points
        irradiances = []
        temperatures = []
        pmpps = []
        vocs = []
        iscs = []

        for key, curve in iv_curves.items():
            irradiances.append(curve["irradiance"])
            temperatures.append(curve["temperature"])
            pmpps.append(curve["pmpp"])
            vocs.append(curve["voc"])
            iscs.append(curve["isc"])

        # Create interpolation functions (2D)
        points = list(zip(irradiances, temperatures))

        try:
            pmpp_interp = interpolate.LinearNDInterpolator(points, pmpps)
            voc_interp = interpolate.LinearNDInterpolator(points, vocs)
            isc_interp = interpolate.LinearNDInterpolator(points, iscs)

            # Interpolate at target point
            pmpp = float(pmpp_interp(target_irr, target_temp))
            voc = float(voc_interp(target_irr, target_temp))
            isc = float(isc_interp(target_irr, target_temp))

            return {
                "irradiance": target_irr,
                "temperature": target_temp,
                "pmpp": pmpp,
                "voc": voc,
                "isc": isc,
                "vmpp": pmpp / (isc * 0.8) if isc > 0 else 0,  # Approximate
                "impp": pmpp / (voc * 0.8) if voc > 0 else 0,  # Approximate
                "fill_factor": self._calculate_fill_factor(pmpp, voc, isc),
            }

        except Exception as e:
            raise ValueError(f"Interpolation failed: {e}")
