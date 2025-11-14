"""Quality control module for ENER-001 Energy Rating Test."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class QualityChecker:
    """Performs quality checks on energy rating test data."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize quality checker.

        Args:
            config: Protocol configuration dictionary
        """
        self.config = config
        self.quality_checks = config.get("quality_checks", [])

    def run_checks(
        self, data: pd.DataFrame, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run all quality checks.

        Args:
            data: Measurement data
            analysis: Analysis results

        Returns:
            List of quality check results
        """
        results = []

        for qc in self.quality_checks:
            check_id = qc["id"]
            check_type = qc["type"]

            if check_type == "threshold":
                result = self._check_threshold(qc, data)
            elif check_type == "range":
                result = self._check_range(qc, data)
            elif check_type == "derivative":
                result = self._check_derivative(qc, data)
            elif check_type == "completeness":
                result = self._check_completeness(qc, data)
            elif check_type == "uncertainty":
                result = self._check_uncertainty(qc, data)
            else:
                result = {
                    "id": check_id,
                    "name": qc["name"],
                    "type": check_type,
                    "severity": qc.get("severity", "warning"),
                    "passed": None,
                    "message": f"Unknown check type: {check_type}",
                }

            results.append(result)

        # Additional checks based on analysis results
        if analysis:
            results.extend(self._check_analysis_results(analysis))

        return results

    def _check_threshold(self, qc: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Check if parameter variation is within threshold."""
        param = qc.get("parameter")
        condition = qc.get("condition", "")

        result = {
            "id": qc["id"],
            "name": qc["name"],
            "type": "threshold",
            "severity": qc.get("severity", "warning"),
            "passed": True,
            "message": "",
        }

        if param not in data.columns:
            result["passed"] = None
            result["message"] = f"Parameter '{param}' not found in data"
            return result

        try:
            # Calculate stability metric
            param_data = data[param].dropna()

            if len(param_data) < 2:
                result["passed"] = None
                result["message"] = "Insufficient data for stability check"
                return result

            mean_val = param_data.mean()
            std_val = param_data.std()
            relative_std = (std_val / mean_val * 100) if mean_val != 0 else 0

            # Parse condition (e.g., "std_dev < 2%")
            if "%" in condition:
                threshold = float(condition.split("<")[1].replace("%", "").strip())
                result["passed"] = relative_std < threshold
                result["message"] = (
                    f"{param}: CV = {relative_std:.2f}% (threshold: {threshold}%)"
                )
            else:
                result["passed"] = None
                result["message"] = f"Could not parse condition: {condition}"

        except Exception as e:
            result["passed"] = False
            result["message"] = f"Check failed: {str(e)}"

        return result

    def _check_range(self, qc: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Check if all values are within specified range."""
        param = qc.get("parameter")
        min_val = qc.get("min", -np.inf)
        max_val = qc.get("max", np.inf)

        result = {
            "id": qc["id"],
            "name": qc["name"],
            "type": "range",
            "severity": qc.get("severity", "warning"),
            "passed": True,
            "message": "",
        }

        if param not in data.columns:
            result["passed"] = None
            result["message"] = f"Parameter '{param}' not found in data"
            return result

        try:
            param_data = data[param].dropna()
            out_of_range = (param_data < min_val) | (param_data > max_val)

            result["passed"] = not out_of_range.any()

            if result["passed"]:
                result["message"] = (
                    f"{param}: All {len(param_data)} values in range "
                    f"[{min_val}, {max_val}]"
                )
            else:
                count = out_of_range.sum()
                result["message"] = (
                    f"{param}: {count}/{len(param_data)} values "
                    f"out of range [{min_val}, {max_val}]"
                )

        except Exception as e:
            result["passed"] = False
            result["message"] = f"Check failed: {str(e)}"

        return result

    def _check_derivative(self, qc: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Check derivative properties (e.g., monotonic)."""
        param = qc.get("parameter")
        condition = qc.get("condition", "")

        result = {
            "id": qc["id"],
            "name": qc["name"],
            "type": "derivative",
            "severity": qc.get("severity", "warning"),
            "passed": True,
            "message": "",
        }

        if param not in data.columns:
            result["passed"] = None
            result["message"] = f"Parameter '{param}' not found in data"
            return result

        try:
            # For IV curve smoothness, check current vs voltage
            # Group by test conditions and check each curve
            if "voltage" in data.columns and param == "current":
                # Check for monotonic decrease in current with increasing voltage
                # Group by irradiance and temperature
                group_cols = []
                if "irradiance" in data.columns:
                    group_cols.append("irradiance")
                if "module_temp" in data.columns:
                    group_cols.append("module_temp")

                if group_cols:
                    non_monotonic_count = 0
                    total_curves = 0

                    for name, group in data.groupby(group_cols):
                        total_curves += 1
                        sorted_group = group.sort_values("voltage")
                        current_diff = sorted_group["current"].diff()

                        # Allow small positive variations (noise)
                        significant_increases = (current_diff > 0.01).sum()

                        if significant_increases > len(sorted_group) * 0.1:  # More than 10%
                            non_monotonic_count += 1

                    result["passed"] = non_monotonic_count == 0
                    result["message"] = (
                        f"IV curve smoothness: {total_curves - non_monotonic_count}/"
                        f"{total_curves} curves are smooth"
                    )
                else:
                    result["passed"] = None
                    result["message"] = "Cannot group data for curve analysis"
            else:
                result["passed"] = None
                result["message"] = f"Derivative check not implemented for '{param}'"

        except Exception as e:
            result["passed"] = False
            result["message"] = f"Check failed: {str(e)}"

        return result

    def _check_completeness(
        self, qc: Dict[str, Any], data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Check data completeness."""
        result = {
            "id": qc["id"],
            "name": qc["name"],
            "type": "completeness",
            "severity": qc.get("severity", "error"),
            "passed": True,
            "message": "",
        }

        try:
            # Check for missing values
            total_cells = data.size
            missing_cells = data.isna().sum().sum()
            missing_percent = (missing_cells / total_cells * 100) if total_cells > 0 else 0

            # Check for required test points
            required_conditions = []

            # Extract expected irradiance and temperature levels from config
            if "irradiance_levels" in self.config.get("test_conditions", {}):
                irr_levels = self.config["test_conditions"]["irradiance_levels"].get(
                    "values", []
                )
            else:
                irr_levels = []

            if "temperature_matrix" in self.config.get("test_conditions", {}):
                temp_levels = self.config["test_conditions"]["temperature_matrix"].get(
                    "values", []
                )
            else:
                temp_levels = []

            # Count unique test conditions present in data
            unique_conditions = 0
            if "irradiance" in data.columns and "module_temp" in data.columns:
                unique_conditions = len(
                    data.groupby(["irradiance", "module_temp"])
                )

            expected_conditions = len(irr_levels) * len(temp_levels) if irr_levels and temp_levels else 0

            result["passed"] = missing_cells == 0 and (
                expected_conditions == 0 or unique_conditions >= expected_conditions
            )

            result["message"] = (
                f"Missing data: {missing_cells}/{total_cells} cells ({missing_percent:.1f}%). "
                f"Test conditions: {unique_conditions}"
                + (f"/{expected_conditions}" if expected_conditions > 0 else "")
            )

        except Exception as e:
            result["passed"] = False
            result["message"] = f"Check failed: {str(e)}"

        return result

    def _check_uncertainty(
        self, qc: Dict[str, Any], data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Check measurement uncertainty."""
        result = {
            "id": qc["id"],
            "name": qc["name"],
            "type": "uncertainty",
            "severity": qc.get("severity", "warning"),
            "passed": True,
            "message": "",
        }

        try:
            # Simplified uncertainty check
            # In practice, this would combine instrument uncertainties
            condition = qc.get("condition", "")

            # Parse threshold from condition
            if "<" in condition and "%" in condition:
                threshold = float(condition.split("<")[1].replace("%", "").strip())

                # Estimate uncertainty from data variability
                # Group by test conditions and calculate CV for each
                if "irradiance" in data.columns and "module_temp" in data.columns:
                    max_cv = 0

                    for name, group in data.groupby(["irradiance", "module_temp"]):
                        if "current" in data.columns and len(group) > 1:
                            cv = (
                                group["current"].std() / group["current"].mean() * 100
                                if group["current"].mean() > 0
                                else 0
                            )
                            max_cv = max(max_cv, cv)

                    result["passed"] = max_cv < threshold
                    result["message"] = (
                        f"Max measurement CV: {max_cv:.2f}% "
                        f"(threshold: {threshold}%)"
                    )
                else:
                    result["passed"] = None
                    result["message"] = "Cannot calculate uncertainty without test conditions"
            else:
                result["passed"] = None
                result["message"] = f"Could not parse condition: {condition}"

        except Exception as e:
            result["passed"] = False
            result["message"] = f"Check failed: {str(e)}"

        return result

    def _check_analysis_results(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform quality checks on analysis results."""
        checks = []

        # Check fill factor range
        if "statistical_summary" in analysis and "fill_factor" in analysis["statistical_summary"]:
            ff_stats = analysis["statistical_summary"]["fill_factor"]
            ff_mean = ff_stats["mean"]

            checks.append(
                {
                    "id": "qc_analysis_ff",
                    "name": "Fill Factor Reasonability",
                    "type": "analysis",
                    "severity": "warning",
                    "passed": 60 <= ff_mean <= 85,
                    "message": f"Mean fill factor: {ff_mean:.1f}% (typical range: 60-85%)",
                }
            )

        # Check efficiency range
        if "statistical_summary" in analysis and "efficiency" in analysis["statistical_summary"]:
            eff_stats = analysis["statistical_summary"]["efficiency"]
            eff_mean = eff_stats["mean"]

            checks.append(
                {
                    "id": "qc_analysis_eff",
                    "name": "Efficiency Reasonability",
                    "type": "analysis",
                    "severity": "warning",
                    "passed": 5 <= eff_mean <= 25,
                    "message": f"Mean efficiency: {eff_mean:.1f}% (typical range: 5-25%)",
                }
            )

        # Check temperature coefficients
        if "temperature_coefficients" in analysis:
            tc = analysis["temperature_coefficients"]

            # Gamma (Pmax) should be negative and typically -0.3 to -0.5 %/°C
            if "gamma_pmax" in tc:
                gamma = tc["gamma_pmax"]
                gamma_ok = -0.6 <= gamma <= -0.2

                checks.append(
                    {
                        "id": "qc_analysis_tc_pmax",
                        "name": "Temperature Coefficient Pmax Reasonability",
                        "type": "analysis",
                        "severity": "warning",
                        "passed": gamma_ok,
                        "message": (
                            f"Temp coeff Pmax: {gamma:.3f} %/°C "
                            f"(typical range: -0.6 to -0.2 %/°C)"
                        ),
                    }
                )

            # Beta (Voc) should be negative and typically -0.25 to -0.35 %/°C
            if "beta_voc" in tc:
                beta = tc["beta_voc"]
                beta_ok = -0.5 <= beta <= -0.1

                checks.append(
                    {
                        "id": "qc_analysis_tc_voc",
                        "name": "Temperature Coefficient Voc Reasonability",
                        "type": "analysis",
                        "severity": "info",
                        "passed": beta_ok,
                        "message": (
                            f"Temp coeff Voc: {beta:.3f} %/°C "
                            f"(typical range: -0.5 to -0.1 %/°C)"
                        ),
                    }
                )

        return checks
