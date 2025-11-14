"""
H2S-001 Hydrogen Sulfide Exposure Test Protocol
Implementation of P37-54 protocol for H2S exposure testing
"""

import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseProtocol, Criticality
from ..loader import ProtocolLoader


class H2S001Protocol(BaseProtocol):
    """
    Hydrogen Sulfide (H2S) Exposure Test Protocol

    Tests PV module resistance to hydrogen sulfide gas exposure,
    simulating conditions in geothermal, volcanic, or industrial areas.
    """

    def __init__(self, protocol_path: Path):
        """Initialize H2S-001 protocol"""
        super().__init__(protocol_path)
        self.baseline_measurements: Dict[str, float] = {}
        self.post_test_measurements: Dict[str, float] = {}
        self.environmental_log: List[Dict[str, Any]] = []
        self.degradation_results: Dict[str, float] = {}

    def record_baseline_electrical(
        self,
        voc: float,
        isc: float,
        vmp: float,
        imp: float,
        pmax: float,
        ff: float
    ):
        """
        Record baseline electrical measurements

        Args:
            voc: Open circuit voltage (V)
            isc: Short circuit current (A)
            vmp: Maximum power voltage (V)
            imp: Maximum power current (A)
            pmax: Maximum power (W)
            ff: Fill factor (dimensionless)
        """
        self.baseline_measurements = {
            "Voc": voc,
            "Isc": isc,
            "Vmp": vmp,
            "Imp": imp,
            "Pmax": pmax,
            "FF": ff
        }

        for param, value in self.baseline_measurements.items():
            self.record_measurement("baseline_electrical", param, value,
                                  self._get_unit(param))

    def record_post_test_electrical(
        self,
        voc: float,
        isc: float,
        vmp: float,
        imp: float,
        pmax: float,
        ff: float
    ):
        """
        Record post-test electrical measurements

        Args:
            voc: Open circuit voltage (V)
            isc: Short circuit current (A)
            vmp: Maximum power voltage (V)
            imp: Maximum power current (A)
            pmax: Maximum power (W)
            ff: Fill factor (dimensionless)
        """
        self.post_test_measurements = {
            "Voc": voc,
            "Isc": isc,
            "Vmp": vmp,
            "Imp": imp,
            "Pmax": pmax,
            "FF": ff
        }

        for param, value in self.post_test_measurements.items():
            self.record_measurement("post_test_electrical", param, value,
                                  self._get_unit(param))

    def record_environmental_data(
        self,
        timestamp: datetime,
        h2s_ppm: float,
        temperature_c: float,
        humidity_rh: float
    ):
        """
        Record environmental chamber conditions

        Args:
            timestamp: Measurement timestamp
            h2s_ppm: H2S concentration in ppm
            temperature_c: Temperature in Celsius
            humidity_rh: Relative humidity in %
        """
        entry = {
            "timestamp": timestamp.isoformat(),
            "h2s_ppm": h2s_ppm,
            "temperature_c": temperature_c,
            "humidity_rh": humidity_rh
        }
        self.environmental_log.append(entry)

    def record_insulation_resistance(
        self,
        baseline_mohm: float,
        post_test_mohm: float
    ):
        """
        Record insulation resistance measurements

        Args:
            baseline_mohm: Baseline insulation resistance (MΩ)
            post_test_mohm: Post-test insulation resistance (MΩ)
        """
        self.record_measurement("insulation_resistance", "baseline_MOhm",
                              baseline_mohm, "MΩ")
        self.record_measurement("insulation_resistance", "post_test_MOhm",
                              post_test_mohm, "MΩ")

    def record_weight_measurements(
        self,
        baseline_kg: float,
        post_test_kg: float
    ):
        """
        Record module weight measurements

        Args:
            baseline_kg: Baseline weight (kg)
            post_test_kg: Post-test weight (kg)
        """
        weight_change_pct = ((post_test_kg - baseline_kg) / baseline_kg) * 100

        self.record_measurement("physical_measurements", "baseline_weight_kg",
                              baseline_kg, "kg")
        self.record_measurement("physical_measurements", "post_test_weight_kg",
                              post_test_kg, "kg")
        self.record_measurement("physical_measurements", "weight_change_pct",
                              weight_change_pct, "%")

    def calculate_degradation(self) -> Dict[str, float]:
        """
        Calculate performance degradation from baseline to post-test

        Returns:
            Dictionary of degradation percentages for each parameter
        """
        if not self.baseline_measurements or not self.post_test_measurements:
            raise ValueError("Both baseline and post-test measurements required")

        degradation = {}
        for param in self.baseline_measurements.keys():
            baseline = self.baseline_measurements[param]
            post_test = self.post_test_measurements[param]

            # Calculate percentage change
            deg_pct = ((post_test - baseline) / baseline) * 100
            degradation[f"Δ{param}"] = deg_pct

        self.degradation_results = degradation
        return degradation

    def analyze_environmental_stability(self) -> Dict[str, Any]:
        """
        Analyze environmental conditions stability during exposure

        Returns:
            Statistics on environmental parameter stability
        """
        if not self.environmental_log:
            return {"error": "No environmental data recorded"}

        h2s_values = [entry["h2s_ppm"] for entry in self.environmental_log]
        temp_values = [entry["temperature_c"] for entry in self.environmental_log]
        humidity_values = [entry["humidity_rh"] for entry in self.environmental_log]

        # Get target conditions
        conditions = self.get_test_conditions()["environmental"]

        def calculate_stats(values: List[float], target: float, tolerance: float):
            """Calculate stability statistics"""
            values_array = np.array(values)
            within_tolerance = np.sum(
                np.abs(values_array - target) <= tolerance
            )
            pct_within = (within_tolerance / len(values)) * 100

            return {
                "mean": float(np.mean(values_array)),
                "std": float(np.std(values_array)),
                "min": float(np.min(values_array)),
                "max": float(np.max(values_array)),
                "target": target,
                "tolerance": tolerance,
                "percent_within_tolerance": pct_within,
                "meets_requirement": pct_within >= 95.0
            }

        analysis = {
            "h2s_concentration": calculate_stats(
                h2s_values,
                conditions["h2s_concentration"]["value"],
                float(conditions["h2s_concentration"]["tolerance"])
            ),
            "temperature": calculate_stats(
                temp_values,
                conditions["temperature"]["value"],
                float(conditions["temperature"]["tolerance"])
            ),
            "relative_humidity": calculate_stats(
                humidity_values,
                conditions["relative_humidity"]["value"],
                float(conditions["relative_humidity"]["tolerance"])
            ),
            "total_measurements": len(self.environmental_log),
            "duration_hours": (
                (datetime.fromisoformat(self.environmental_log[-1]["timestamp"]) -
                 datetime.fromisoformat(self.environmental_log[0]["timestamp"])).total_seconds() / 3600
                if len(self.environmental_log) > 1 else 0
            )
        }

        return analysis

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze test results and evaluate performance

        Returns:
            Comprehensive analysis results
        """
        analysis = {
            "degradation": {},
            "environmental_stability": {},
            "acceptance_evaluation": {},
            "recommendations": []
        }

        # Calculate degradation if not already done
        if not self.degradation_results:
            try:
                self.calculate_degradation()
            except ValueError as e:
                analysis["error"] = str(e)
                return analysis

        analysis["degradation"] = self.degradation_results

        # Analyze environmental stability
        analysis["environmental_stability"] = self.analyze_environmental_stability()

        # Evaluate acceptance criteria
        self._evaluate_criteria()
        analysis["acceptance_evaluation"] = self.evaluate_acceptance()

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations()

        return analysis

    def _evaluate_criteria(self):
        """Evaluate all acceptance criteria against measured data"""
        # Evaluate power degradation (critical)
        if "ΔPmax" in self.degradation_results:
            pmax_deg = abs(self.degradation_results["ΔPmax"])
            for criterion in self.acceptance_criteria:
                if criterion.parameter == "Maximum Power Degradation":
                    criterion.actual_value = pmax_deg
                    # Extract numeric requirement (e.g., "≤ 5%" -> 5.0)
                    req_value = float(criterion.requirement.replace("≤", "").replace("%", "").strip())
                    criterion.passed = pmax_deg <= req_value
                    if not criterion.passed:
                        criterion.notes = f"Degradation {pmax_deg:.2f}% exceeds limit {req_value}%"

        # Evaluate insulation resistance (critical)
        if "insulation_resistance" in self.test_data:
            post_test_ir = self.test_data["insulation_resistance"].get("post_test_MOhm", {}).get("value")
            if post_test_ir:
                for criterion in self.acceptance_criteria:
                    if criterion.parameter == "Insulation Resistance":
                        criterion.actual_value = post_test_ir
                        # Requirement: ≥ 400 MΩ or 40 MΩ·m²
                        criterion.passed = post_test_ir >= 400
                        if not criterion.passed:
                            criterion.notes = f"Insulation resistance {post_test_ir:.1f} MΩ below 400 MΩ minimum"

        # Evaluate Voc degradation
        if "ΔVoc" in self.degradation_results:
            voc_deg = abs(self.degradation_results["ΔVoc"])
            for criterion in self.acceptance_criteria:
                if criterion.parameter == "Open Circuit Voltage Degradation":
                    criterion.actual_value = voc_deg
                    req_value = 3.0  # ≤ 3%
                    criterion.passed = voc_deg <= req_value

        # Evaluate Isc degradation
        if "ΔIsc" in self.degradation_results:
            isc_deg = abs(self.degradation_results["ΔIsc"])
            for criterion in self.acceptance_criteria:
                if criterion.parameter == "Short Circuit Current Degradation":
                    criterion.actual_value = isc_deg
                    req_value = 3.0  # ≤ 3%
                    criterion.passed = isc_deg <= req_value

        # Evaluate FF degradation
        if "ΔFF" in self.degradation_results:
            ff_deg = abs(self.degradation_results["ΔFF"])
            for criterion in self.acceptance_criteria:
                if criterion.parameter == "Fill Factor Degradation":
                    criterion.actual_value = ff_deg
                    req_value = 5.0  # ≤ 5%
                    criterion.passed = ff_deg <= req_value

        # Evaluate weight change
        if "physical_measurements" in self.test_data:
            weight_change = self.test_data["physical_measurements"].get("weight_change_pct", {}).get("value")
            if weight_change is not None:
                for criterion in self.acceptance_criteria:
                    if criterion.parameter == "Weight Change":
                        criterion.actual_value = abs(weight_change)
                        req_value = 1.0  # < 1%
                        criterion.passed = abs(weight_change) < req_value

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for critical failures
        acceptance_eval = self.evaluate_acceptance()
        if acceptance_eval["critical_failures"]:
            recommendations.append(
                "CRITICAL: Module failed critical acceptance criteria. "
                "Not recommended for deployment in H2S environments."
            )

        # Check degradation patterns
        if self.degradation_results:
            pmax_deg = abs(self.degradation_results.get("ΔPmax", 0))
            if pmax_deg > 3 and pmax_deg <= 5:
                recommendations.append(
                    "Moderate power degradation observed. Consider additional "
                    "testing or enhanced encapsulation for H2S applications."
                )

            # Check if Isc dropped more than Voc (potential corrosion indicator)
            isc_deg = abs(self.degradation_results.get("ΔIsc", 0))
            voc_deg = abs(self.degradation_results.get("ΔVoc", 0))
            if isc_deg > voc_deg + 1.0:
                recommendations.append(
                    "Higher Isc degradation vs Voc suggests possible corrosion "
                    "of cell metallization. Inspect contact quality."
                )

        # Check environmental stability
        env_stability = self.analyze_environmental_stability()
        if not env_stability.get("h2s_concentration", {}).get("meets_requirement", True):
            recommendations.append(
                "WARNING: H2S concentration was outside tolerance for >5% of "
                "exposure time. Results may not be representative."
            )

        if not recommendations:
            recommendations.append(
                "Module passed all acceptance criteria for H2S exposure. "
                "Suitable for deployment in specified H2S environment."
            )

        return recommendations

    @staticmethod
    def _get_unit(parameter: str) -> str:
        """Get unit for electrical parameter"""
        units = {
            "Voc": "V",
            "Isc": "A",
            "Vmp": "V",
            "Imp": "A",
            "Pmax": "W",
            "FF": "dimensionless"
        }
        return units.get(parameter, "")

    def validate_test_execution(self) -> Tuple[bool, List[str]]:
        """
        Validate that test was executed properly

        Returns:
            Tuple of (is_valid, list of validation issues)
        """
        issues = []

        # Check that all phases were completed
        for phase in self.phases:
            if phase.status.value != "completed":
                issues.append(f"Phase {phase.phase_id} ({phase.name}) not completed")

        # Check environmental stability
        env_stability = self.analyze_environmental_stability()
        for param in ["h2s_concentration", "temperature", "relative_humidity"]:
            if not env_stability.get(param, {}).get("meets_requirement", False):
                issues.append(
                    f"{param.replace('_', ' ').title()} outside tolerance "
                    f"for >5% of exposure time"
                )

        # Check data completeness
        if not self.baseline_measurements:
            issues.append("Baseline electrical measurements not recorded")
        if not self.post_test_measurements:
            issues.append("Post-test electrical measurements not recorded")
        if not self.environmental_log:
            issues.append("Environmental data log is empty")

        is_valid = len(issues) == 0
        return is_valid, issues


# Register protocol
ProtocolLoader.register_protocol("H2S-001", H2S001Protocol)
