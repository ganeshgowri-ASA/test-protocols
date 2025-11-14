"""Quality control checking module."""

from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
import numpy as np


class QCChecker:
    """Quality control checker for test protocols."""

    def __init__(self, protocol_id: str, config_path: Optional[str] = None):
        """
        Initialize QC checker.

        Args:
            protocol_id: Protocol identifier
            config_path: Path to QC rules configuration
        """
        self.protocol_id = protocol_id
        self.rules = self._load_qc_rules(config_path)

    def _load_qc_rules(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load QC rules from configuration file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "qc_rules.yaml"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                all_rules = yaml.safe_load(f)
        else:
            all_rules = {}

        # Get protocol-specific rules
        protocol_rules = all_rules.get(self.protocol_id, {})
        global_rules = all_rules.get("global", {})

        # Merge rules (protocol-specific overrides global)
        rules = {**global_rules, **protocol_rules}

        return rules

    def check_measurement_range(
        self,
        measurement: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check if measurement values are within acceptable ranges.

        Args:
            measurement: Measurement data dictionary

        Returns:
            List of QC check results
        """
        results = []
        range_rules = self.rules.get("initial_measurements", {})

        for field, value in measurement.items():
            if value is None:
                continue

            # Check if there's a range rule for this field
            range_rule = range_rules.get(f"{field}_range")
            if range_rule:
                min_val = range_rule.get("min")
                max_val = range_rule.get("max")

                if min_val is not None and value < min_val:
                    results.append({
                        "check_name": f"{field.upper()} Range Check",
                        "check_category": "measurement_validation",
                        "passed": False,
                        "severity": "error",
                        "expected_value": f">= {min_val}",
                        "actual_value": str(value),
                        "message": f"{field.upper()} value {value} below minimum {min_val}",
                    })

                if max_val is not None and value > max_val:
                    results.append({
                        "check_name": f"{field.upper()} Range Check",
                        "check_category": "measurement_validation",
                        "passed": False,
                        "severity": "error",
                        "expected_value": f"<= {max_val}",
                        "actual_value": str(value),
                        "message": f"{field.upper()} value {value} exceeds maximum {max_val}",
                    })

        return results

    def check_environmental_conditions(
        self,
        irradiance: float,
        temperature: float
    ) -> List[Dict[str, Any]]:
        """
        Check environmental conditions.

        Args:
            irradiance: Measured irradiance (W/m²)
            temperature: Measured temperature (°C)

        Returns:
            List of QC check results
        """
        results = []
        env_rules = self.rules.get("environmental_conditions", {})

        # Check irradiance
        if "irradiance" in env_rules:
            irr_rules = env_rules["irradiance"]
            nominal = irr_rules.get("nominal", 1000.0)
            tolerance = irr_rules.get("tolerance", 2.0)
            min_irr = nominal * (1 - tolerance / 100)
            max_irr = nominal * (1 + tolerance / 100)

            if not (min_irr <= irradiance <= max_irr):
                results.append({
                    "check_name": "Irradiance Tolerance",
                    "check_category": "environmental",
                    "passed": False,
                    "severity": "warning",
                    "expected_value": f"{nominal} ± {tolerance}% W/m²",
                    "actual_value": f"{irradiance} W/m²",
                    "message": f"Irradiance {irradiance} W/m² outside tolerance range",
                })

        # Check temperature
        if "temperature" in env_rules:
            temp_rules = env_rules["temperature"]
            nominal = temp_rules.get("nominal", 25.0)
            tolerance = temp_rules.get("tolerance", 2.0)
            min_temp = nominal - tolerance
            max_temp = nominal + tolerance

            if not (min_temp <= temperature <= max_temp):
                results.append({
                    "check_name": "Temperature Tolerance",
                    "check_category": "environmental",
                    "passed": False,
                    "severity": "warning",
                    "expected_value": f"{nominal} ± {tolerance}°C",
                    "actual_value": f"{temperature}°C",
                    "message": f"Temperature {temperature}°C outside tolerance range",
                })

        return results

    def check_data_completeness(
        self,
        measurements: List[Dict[str, Any]],
        expected_count: int
    ) -> Dict[str, Any]:
        """
        Check data completeness.

        Args:
            measurements: List of measurements
            expected_count: Expected number of measurements

        Returns:
            QC check result
        """
        actual_count = len(measurements)
        completeness_rules = self.rules.get("data_completeness", {})
        min_rate = completeness_rules.get("min_completion_rate", 95.0)

        completion_rate = 100 * actual_count / expected_count if expected_count > 0 else 0

        passed = completion_rate >= min_rate

        return {
            "check_name": "Data Completeness",
            "check_category": "data_quality",
            "passed": passed,
            "severity": "error" if not passed else "info",
            "expected_value": f">= {min_rate}%",
            "actual_value": f"{completion_rate:.1f}%",
            "message": f"Data completeness: {actual_count}/{expected_count} measurements ({completion_rate:.1f}%)",
        }

    def check_measurement_repeatability(
        self,
        measurements: List[float]
    ) -> Dict[str, Any]:
        """
        Check measurement repeatability.

        Args:
            measurements: List of repeated measurements

        Returns:
            QC check result
        """
        if len(measurements) < 2:
            return {
                "check_name": "Measurement Repeatability",
                "check_category": "data_quality",
                "passed": False,
                "severity": "error",
                "message": "Insufficient measurements for repeatability check",
            }

        repeat_rules = self.rules.get("measurement_repeatability", {})
        max_cv = repeat_rules.get("max_coefficient_of_variation", 2.0)

        mean_val = np.mean(measurements)
        std_val = np.std(measurements, ddof=1)
        cv = 100 * std_val / mean_val if mean_val != 0 else 0

        passed = cv <= max_cv

        return {
            "check_name": "Measurement Repeatability",
            "check_category": "data_quality",
            "passed": passed,
            "severity": "warning" if not passed else "info",
            "expected_value": f"CV <= {max_cv}%",
            "actual_value": f"CV = {cv:.2f}%",
            "threshold": f"{max_cv}%",
            "message": f"Coefficient of variation: {cv:.2f}% (threshold: {max_cv}%)",
            "details": {
                "mean": mean_val,
                "std": std_val,
                "cv_percent": cv,
                "n_measurements": len(measurements),
            }
        }

    def check_chronological_order(
        self,
        measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if measurements are in chronological order.

        Args:
            measurements: List of measurements with timestamps

        Returns:
            QC check result
        """
        timestamp_rules = self.rules.get("timestamp_validation", {})
        check_order = timestamp_rules.get("check_chronological_order", True)

        if not check_order:
            return {
                "check_name": "Chronological Order",
                "check_category": "data_quality",
                "passed": True,
                "severity": "info",
                "message": "Chronological order check disabled",
            }

        # Extract timestamps
        timestamps = []
        for m in measurements:
            ts = m.get("timestamp")
            if ts:
                timestamps.append(ts)

        if len(timestamps) < 2:
            return {
                "check_name": "Chronological Order",
                "check_category": "data_quality",
                "passed": True,
                "severity": "info",
                "message": "Insufficient timestamps for order check",
            }

        # Check if sorted
        is_sorted = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))

        return {
            "check_name": "Chronological Order",
            "check_category": "data_quality",
            "passed": is_sorted,
            "severity": "warning" if not is_sorted else "info",
            "message": "Measurements are in chronological order" if is_sorted else "Measurements are NOT in chronological order",
        }
