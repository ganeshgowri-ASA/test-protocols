"""Quality control checking module."""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class QCChecker:
    """Perform quality control checks on measurement data."""

    def __init__(self, protocol: Dict[str, Any]):
        """
        Initialize QC Checker.

        Args:
            protocol: Protocol definition dictionary
        """
        self.protocol = protocol
        self.qc_rules = protocol["protocol"].get("qc_rules", [])
        logger.info(f"QCChecker initialized with {len(self.qc_rules)} rules")

    def check_measurement(
        self, measurement: Dict[str, Any], all_values: List[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Check a measurement against all applicable QC rules.

        Args:
            measurement: Measurement dictionary containing:
                - measurement_id: str
                - phase_id: str
                - value: float
            all_values: List of all values for outlier detection

        Returns:
            List of QC flag dictionaries
        """
        flags = []

        measurement_id = measurement.get("measurement_id")
        phase_id = measurement.get("phase_id")
        value = measurement.get("value")

        if value is None:
            return flags

        # Find applicable rules
        for rule in self.qc_rules:
            # Check if rule applies to this measurement
            if rule.get("measurement_id") and rule["measurement_id"] != measurement_id:
                continue

            if rule.get("phase_id") and rule["phase_id"] != phase_id:
                continue

            # Apply the rule
            flag = self._apply_rule(rule, value, all_values)
            if flag:
                flags.append(flag)

        if flags:
            logger.warning(
                f"QC check found {len(flags)} flags for {measurement_id} = {value}"
            )

        return flags

    def _apply_rule(
        self, rule: Dict[str, Any], value: float, all_values: List[float] = None
    ) -> Dict[str, Any] | None:
        """
        Apply a single QC rule.

        Args:
            rule: QC rule definition
            value: Measurement value
            all_values: All values for outlier detection

        Returns:
            QC flag dictionary or None if rule passes
        """
        rule_type = rule.get("type")
        rule_id = rule.get("rule_id")

        if rule_type == "range":
            return self._check_range(rule, value)

        elif rule_type == "outlier":
            return self._check_outlier(rule, value, all_values)

        elif rule_type == "trend":
            return self._check_trend(rule, all_values)

        else:
            logger.warning(f"Unknown rule type: {rule_type}")
            return None

    def _check_range(self, rule: Dict[str, Any], value: float) -> Dict[str, Any] | None:
        """
        Check if value is within acceptable range.

        Args:
            rule: Range rule definition
            value: Measurement value

        Returns:
            QC flag or None
        """
        min_value = rule.get("min_value", float("-inf"))
        max_value = rule.get("max_value", float("inf"))

        if value < min_value or value > max_value:
            return {
                "rule_id": rule["rule_id"],
                "flag_type": "error" if rule["action"] == "flag_error" else "warning",
                "description": rule.get("description", "Value out of range"),
                "value": value,
                "threshold": f"[{min_value}, {max_value}]",
            }

        return None

    def _check_outlier(
        self, rule: Dict[str, Any], value: float, all_values: List[float] = None
    ) -> Dict[str, Any] | None:
        """
        Check if value is a statistical outlier.

        Args:
            rule: Outlier rule definition
            value: Measurement value
            all_values: All values for comparison

        Returns:
            QC flag or None
        """
        if not all_values or len(all_values) < 4:
            return None

        method = rule.get("method", "iqr")
        threshold = rule.get("threshold", 1.5)

        is_outlier = False

        if method == "iqr":
            q1 = np.percentile(all_values, 25)
            q3 = np.percentile(all_values, 75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            is_outlier = value < lower_bound or value > upper_bound

        elif method == "zscore":
            mean = np.mean(all_values)
            std = np.std(all_values)

            if std > 0:
                z_score = abs((value - mean) / std)
                is_outlier = z_score > threshold

        if is_outlier:
            return {
                "rule_id": rule["rule_id"],
                "flag_type": "error" if rule["action"] == "flag_error" else "warning",
                "description": rule.get("description", "Value is statistical outlier"),
                "value": value,
                "threshold": f"{method}:{threshold}",
            }

        return None

    def _check_trend(
        self, rule: Dict[str, Any], all_values: List[float] = None
    ) -> Dict[str, Any] | None:
        """
        Check for trends in data.

        Args:
            rule: Trend rule definition
            all_values: All values for trend analysis

        Returns:
            QC flag or None
        """
        if not all_values or len(all_values) < 5:
            return None

        # Simple linear regression to detect trends
        x = np.arange(len(all_values))
        y = np.array(all_values)

        # Calculate slope
        slope, _ = np.polyfit(x, y, 1)

        threshold = rule.get("threshold", 0.1)

        if abs(slope) > threshold:
            return {
                "rule_id": rule["rule_id"],
                "flag_type": "warning",
                "description": f"Significant trend detected (slope={slope:.4f})",
                "value": slope,
                "threshold": threshold,
            }

        return None

    def check_all_measurements(
        self, measurements: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Check all measurements in a DataFrame.

        Args:
            measurements: DataFrame with measurements

        Returns:
            List of all QC flags
        """
        all_flags = []

        # Group by measurement_id for outlier detection
        for measurement_id in measurements["measurement_id"].unique():
            subset = measurements[
                measurements["measurement_id"] == measurement_id
            ]
            values = subset["value"].dropna().tolist()

            for _, row in subset.iterrows():
                measurement_dict = {
                    "measurement_id": row["measurement_id"],
                    "phase_id": row.get("phase_id"),
                    "value": row.get("value"),
                }

                flags = self.check_measurement(measurement_dict, values)
                all_flags.extend(flags)

        logger.info(f"QC check completed: {len(all_flags)} total flags")
        return all_flags

    def get_qc_summary(self, flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics of QC flags.

        Args:
            flags: List of QC flag dictionaries

        Returns:
            Summary dictionary
        """
        summary = {
            "total_flags": len(flags),
            "errors": len([f for f in flags if f["flag_type"] == "error"]),
            "warnings": len([f for f in flags if f["flag_type"] == "warning"]),
            "by_rule": {},
        }

        for flag in flags:
            rule_id = flag["rule_id"]
            if rule_id not in summary["by_rule"]:
                summary["by_rule"][rule_id] = 0
            summary["by_rule"][rule_id] += 1

        return summary
