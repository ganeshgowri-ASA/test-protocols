"""Backsheet Chalking Protocol Implementation (CHALK-001)"""

import logging
import statistics
from typing import Dict, List, Any
import numpy as np
from ..core.protocol_base import ProtocolBase

logger = logging.getLogger(__name__)


class BacksheetChalkingProtocol(ProtocolBase):
    """
    Implementation of CHALK-001 Backsheet Chalking Protocol.

    This protocol evaluates chalking degradation in PV module backsheets
    using adhesive tape testing and visual rating per ASTM D4214.
    """

    def __init__(self, protocol_definition: Dict[str, Any]):
        """
        Initialize Backsheet Chalking Protocol.

        Args:
            protocol_definition: Protocol definition from JSON
        """
        super().__init__(protocol_definition)
        self.criteria = self.definition.get("pass_fail_criteria", {})

    def calculate_results(self) -> Dict[str, Any]:
        """
        Calculate statistical metrics from chalking measurements.

        Returns:
            Dictionary containing calculated results
        """
        if not self.measurements:
            logger.warning("No measurements available for calculation")
            return {}

        # Extract chalking ratings from measurements
        ratings = [m.get("chalking_rating", 0) for m in self.measurements]

        if not ratings:
            logger.warning("No chalking ratings found in measurements")
            return {}

        # Calculate basic statistics
        avg_rating = statistics.mean(ratings)
        std_dev = statistics.stdev(ratings) if len(ratings) > 1 else 0
        max_rating = max(ratings)
        min_rating = min(ratings)

        # Calculate coefficient of variation (CV)
        cv = (std_dev / avg_rating * 100) if avg_rating > 0 else 0

        # Calculate uniformity index
        # Uniformity = (1 - CV/100) * 100, capped at 0-100%
        uniformity_index = max(0, min(100, (1 - std_dev / avg_rating) * 100 if avg_rating > 0 else 0))

        results = {
            "average_chalking_rating": round(avg_rating, 2),
            "chalking_std_dev": round(std_dev, 2),
            "max_chalking_rating": round(max_rating, 2),
            "min_chalking_rating": round(min_rating, 2),
            "coefficient_of_variation": round(cv, 2),
            "chalking_uniformity_index": round(uniformity_index, 2),
            "number_of_measurements": len(ratings),
        }

        # Calculate quartiles if enough data points
        if len(ratings) >= 4:
            q1 = np.percentile(ratings, 25)
            q2 = np.percentile(ratings, 50)  # median
            q3 = np.percentile(ratings, 75)
            results.update({
                "quartile_1": round(q1, 2),
                "median": round(q2, 2),
                "quartile_3": round(q3, 2),
            })

        logger.info(f"Calculated results: avg={avg_rating:.2f}, max={max_rating:.2f}")
        return results

    def evaluate_pass_fail(self) -> Dict[str, Any]:
        """
        Evaluate pass/fail criteria based on calculated results.

        Returns:
            Dictionary containing pass/fail assessment
        """
        if not self.calculated_results:
            logger.warning("No calculated results available for evaluation")
            return {
                "overall_result": "FAIL",
                "criteria_evaluations": [],
                "notes": "No calculated results available",
            }

        criteria_evaluations = []

        # Get acceptance thresholds from protocol definition
        thresholds = self.criteria.get("acceptance_thresholds", {})

        # Evaluate average chalking rating
        avg_rating = self.calculated_results.get("average_chalking_rating", float("inf"))
        avg_result = self._evaluate_threshold(
            avg_rating, thresholds.get("average_chalking_rating", {})
        )
        criteria_evaluations.append({
            "criterion": "Average Chalking Rating",
            "actual_value": avg_rating,
            "threshold": self._format_threshold(thresholds.get("average_chalking_rating", {})),
            "result": avg_result,
        })

        # Evaluate maximum chalking rating
        max_rating = self.calculated_results.get("max_chalking_rating", float("inf"))
        max_result = self._evaluate_threshold(
            max_rating, thresholds.get("max_chalking_rating", {})
        )
        criteria_evaluations.append({
            "criterion": "Maximum Chalking Rating",
            "actual_value": max_rating,
            "threshold": self._format_threshold(thresholds.get("max_chalking_rating", {})),
            "result": max_result,
        })

        # Determine overall result
        # FAIL if any criterion fails, WARNING if any warning, otherwise PASS
        if any(c["result"] == "FAIL" for c in criteria_evaluations):
            overall_result = "FAIL"
        elif any(c["result"] == "WARNING" for c in criteria_evaluations):
            overall_result = "WARNING"
        else:
            overall_result = "PASS"

        assessment = {
            "overall_result": overall_result,
            "criteria_evaluations": criteria_evaluations,
            "notes": self._generate_assessment_notes(overall_result, criteria_evaluations),
        }

        logger.info(f"Pass/Fail evaluation: {overall_result}")
        return assessment

    def _evaluate_threshold(
        self, value: float, threshold_spec: Dict[str, str]
    ) -> str:
        """
        Evaluate a value against threshold specification.

        Args:
            value: Measured value
            threshold_spec: Threshold specification with pass/warning/fail criteria

        Returns:
            Result string: 'PASS', 'WARNING', or 'FAIL'
        """
        pass_criteria = threshold_spec.get("pass", "")
        warning_criteria = threshold_spec.get("warning", "")
        fail_criteria = threshold_spec.get("fail", "")

        # Parse criteria (simple implementation for < > patterns)
        if self._meets_criteria(value, fail_criteria):
            return "FAIL"
        elif self._meets_criteria(value, warning_criteria):
            return "WARNING"
        elif self._meets_criteria(value, pass_criteria):
            return "PASS"
        else:
            return "FAIL"  # Default to fail if criteria unclear

    def _meets_criteria(self, value: float, criteria: str) -> bool:
        """
        Check if value meets criteria expression.

        Args:
            value: Measured value
            criteria: Criteria expression (e.g., "< 3.0", "> 5.0", "3.0 - 5.0")

        Returns:
            True if criteria met
        """
        if not criteria:
            return False

        criteria = criteria.strip()

        # Handle range (e.g., "3.0 - 5.0")
        if "-" in criteria and not criteria.startswith("-"):
            parts = criteria.split("-")
            if len(parts) == 2:
                try:
                    lower = float(parts[0].strip())
                    upper = float(parts[1].strip())
                    return lower <= value <= upper
                except ValueError:
                    return False

        # Handle comparison operators
        if criteria.startswith("<="):
            threshold = float(criteria[2:].strip())
            return value <= threshold
        elif criteria.startswith(">="):
            threshold = float(criteria[2:].strip())
            return value >= threshold
        elif criteria.startswith("<"):
            threshold = float(criteria[1:].strip())
            return value < threshold
        elif criteria.startswith(">"):
            threshold = float(criteria[1:].strip())
            return value > threshold
        elif criteria.startswith("=="):
            threshold = float(criteria[2:].strip())
            return abs(value - threshold) < 0.01

        return False

    def _format_threshold(self, threshold_spec: Dict[str, str]) -> str:
        """
        Format threshold specification as readable string.

        Args:
            threshold_spec: Threshold specification dictionary

        Returns:
            Formatted string
        """
        pass_criteria = threshold_spec.get("pass", "N/A")
        return f"Pass: {pass_criteria}"

    def _generate_assessment_notes(
        self, overall_result: str, criteria_evaluations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate explanatory notes for the assessment.

        Args:
            overall_result: Overall result (PASS/WARNING/FAIL)
            criteria_evaluations: List of individual criterion evaluations

        Returns:
            Notes string
        """
        notes = []

        if overall_result == "FAIL":
            failed_criteria = [c for c in criteria_evaluations if c["result"] == "FAIL"]
            notes.append(
                f"Test FAILED: {len(failed_criteria)} criterion/criteria not met."
            )
            for criterion in failed_criteria:
                notes.append(
                    f"  - {criterion['criterion']}: {criterion['actual_value']} "
                    f"(threshold: {criterion['threshold']})"
                )

        elif overall_result == "WARNING":
            warning_criteria = [c for c in criteria_evaluations if c["result"] == "WARNING"]
            notes.append(
                f"Test WARNING: {len(warning_criteria)} criterion/criteria in warning zone."
            )
            for criterion in warning_criteria:
                notes.append(
                    f"  - {criterion['criterion']}: {criterion['actual_value']} "
                    f"(threshold: {criterion['threshold']})"
                )
            notes.append("  Further investigation or monitoring recommended.")

        else:
            notes.append("Test PASSED: All criteria met.")

        return " ".join(notes)

    def generate_spatial_analysis(self) -> Dict[str, Any]:
        """
        Generate spatial analysis of chalking distribution.

        Returns:
            Dictionary with spatial analysis data
        """
        if not self.measurements:
            return {}

        # Extract coordinates and ratings
        spatial_data = []
        for m in self.measurements:
            if "location_x" in m and "location_y" in m:
                spatial_data.append({
                    "x": m["location_x"],
                    "y": m["location_y"],
                    "rating": m.get("chalking_rating", 0),
                    "location_id": m.get("location_id", ""),
                })

        if not spatial_data:
            return {"has_spatial_data": False}

        # Find hotspots (locations with high chalking)
        hotspots = [d for d in spatial_data if d["rating"] > 5.0]

        return {
            "has_spatial_data": True,
            "spatial_points": spatial_data,
            "hotspot_count": len(hotspots),
            "hotspot_locations": [h["location_id"] for h in hotspots],
        }

    def get_recommendations(self) -> List[str]:
        """
        Generate recommendations based on test results.

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if not self.calculated_results or not self.pass_fail_assessment:
            return ["Complete test execution to generate recommendations"]

        avg_rating = self.calculated_results.get("average_chalking_rating", 0)
        max_rating = self.calculated_results.get("max_chalking_rating", 0)
        std_dev = self.calculated_results.get("chalking_std_dev", 0)
        overall_result = self.pass_fail_assessment.get("overall_result", "UNKNOWN")

        if overall_result == "FAIL":
            recommendations.append(
                "CRITICAL: Backsheet shows excessive chalking. "
                "Module may have reduced weatherability."
            )
            recommendations.append(
                "Recommend: Material analysis, warranty review, or module replacement."
            )

        elif overall_result == "WARNING":
            recommendations.append(
                "CAUTION: Backsheet chalking is in warning zone. Monitor for progression."
            )
            recommendations.append(
                "Recommend: Periodic re-inspection (e.g., every 6-12 months)."
            )

        else:
            recommendations.append(
                "Backsheet condition is acceptable. Continue routine monitoring."
            )

        # Non-uniformity recommendations
        if std_dev > 2.0:
            recommendations.append(
                f"High variability detected (σ={std_dev:.2f}). "
                "Investigate non-uniform exposure or manufacturing issues."
            )

        # Hotspot recommendations
        spatial_analysis = self.generate_spatial_analysis()
        if spatial_analysis.get("hotspot_count", 0) > 0:
            recommendations.append(
                f"Chalking hotspots detected at {spatial_analysis['hotspot_count']} location(s): "
                f"{', '.join(spatial_analysis.get('hotspot_locations', []))}"
            )

        return recommendations
