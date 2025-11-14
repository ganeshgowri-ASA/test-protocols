"""LID-001 specific analysis module."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime

from .calculations import calculate_degradation_rate, detect_outliers
from .qc_checks import QCChecker


class LID001Analyzer:
    """Analyzer for LID-001 test data."""

    def __init__(self):
        """Initialize LID-001 analyzer."""
        self.protocol_id = "LID-001"
        self.qc_checker = QCChecker(self.protocol_id)

    def analyze_test_run(
        self,
        measurements: List[Dict[str, Any]],
        baseline_power: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform complete analysis of LID-001 test run.

        Args:
            measurements: List of measurements
            baseline_power: Baseline power (calculated from initial measurements if not provided)

        Returns:
            Analysis results dictionary
        """
        if not measurements:
            return {"error": "No measurements provided"}

        # Calculate baseline power if not provided
        if baseline_power is None:
            initial_measurements = [m for m in measurements if m.get("measurement_type") == "initial"]
            if initial_measurements:
                initial_powers = [m.get("pmax") for m in initial_measurements if m.get("pmax")]
                baseline_power = np.mean(initial_powers) if initial_powers else None

        if baseline_power is None or baseline_power == 0:
            return {"error": "Could not determine baseline power"}

        # Calculate degradation for all measurements
        degradation_data = []
        for m in measurements:
            pmax = m.get("pmax")
            if pmax is not None:
                degradation_pct = 100 * (baseline_power - pmax) / baseline_power
                degradation_data.append({
                    "timestamp": m.get("timestamp"),
                    "elapsed_hours": m.get("elapsed_hours"),
                    "pmax": pmax,
                    "degradation_percent": degradation_pct,
                    "measurement_type": m.get("measurement_type")
                })

        # Find maximum degradation
        if degradation_data:
            max_deg_point = max(degradation_data, key=lambda x: x["degradation_percent"])
            max_degradation = max_deg_point["degradation_percent"]
            max_deg_time = max_deg_point["elapsed_hours"]
        else:
            max_degradation = 0.0
            max_deg_time = 0.0

        # Find final degradation
        final_measurements = [d for d in degradation_data if d["measurement_type"] != "initial"]
        if final_measurements:
            final_degradation = final_measurements[-1]["degradation_percent"]
        else:
            final_degradation = 0.0

        # Check for stabilization
        stabilization_result = self._check_stabilization(degradation_data)

        # Calculate degradation rate
        times = np.array([d["elapsed_hours"] for d in degradation_data if d["elapsed_hours"] is not None])
        degradations = np.array([d["degradation_percent"] for d in degradation_data if d["elapsed_hours"] is not None])

        if len(times) >= 2:
            rate, r_squared = calculate_degradation_rate(times, degradations, method="linear")
        else:
            rate, r_squared = 0.0, 0.0

        # Detect outliers in power measurements
        powers = np.array([d["pmax"] for d in degradation_data])
        outlier_mask = detect_outliers(powers, method="iqr", threshold=1.5)
        num_outliers = np.sum(outlier_mask)

        # Calculate recovery (if post-exposure measurements exist)
        recovery_result = self._calculate_recovery(degradation_data)

        # Perform QC checks
        qc_results = self._perform_qc_checks(measurements, baseline_power, max_degradation)

        # Compile results
        results = {
            "baseline_power": baseline_power,
            "max_degradation_percent": max_degradation,
            "max_degradation_time_hours": max_deg_time,
            "final_degradation_percent": final_degradation,
            "degradation_rate_percent_per_hour": rate,
            "degradation_rate_r_squared": r_squared,
            "is_stabilized": stabilization_result["is_stabilized"],
            "stabilization_time_hours": stabilization_result.get("stabilization_time"),
            "stabilization_degradation_percent": stabilization_result.get("stabilization_degradation"),
            "recovery_percent": recovery_result.get("recovery_percent"),
            "recovery_power": recovery_result.get("recovery_power"),
            "num_measurements": len(measurements),
            "num_outliers": int(num_outliers),
            "qc_passed": all(qc["passed"] for qc in qc_results),
            "qc_results": qc_results,
            "degradation_data": degradation_data,
        }

        return results

    def _check_stabilization(
        self,
        degradation_data: List[Dict[str, Any]],
        threshold: float = 0.5,
        num_points: int = 3
    ) -> Dict[str, Any]:
        """
        Check if degradation has stabilized.

        Args:
            degradation_data: List of degradation data points
            threshold: Stabilization threshold (% change)
            num_points: Number of consecutive points required

        Returns:
            Stabilization analysis results
        """
        if len(degradation_data) < num_points:
            return {
                "is_stabilized": False,
                "message": "Insufficient data points"
            }

        # Check last N points
        recent_data = degradation_data[-num_points:]
        degradations = [d["degradation_percent"] for d in recent_data]

        # Calculate maximum change between consecutive points
        max_change = 0.0
        for i in range(1, len(degradations)):
            change = abs(degradations[i] - degradations[i-1])
            max_change = max(max_change, change)

        is_stabilized = max_change < threshold

        # Find stabilization point if stabilized
        stabilization_time = None
        stabilization_degradation = None

        if is_stabilized:
            # Work backwards to find when stabilization began
            for i in range(len(degradation_data) - num_points, -1, -1):
                window = degradation_data[i:i+num_points]
                window_degs = [d["degradation_percent"] for d in window]

                window_max_change = 0.0
                for j in range(1, len(window_degs)):
                    change = abs(window_degs[j] - window_degs[j-1])
                    window_max_change = max(window_max_change, change)

                if window_max_change >= threshold:
                    # Stabilization started after this window
                    stabilization_time = degradation_data[i+num_points]["elapsed_hours"]
                    stabilization_degradation = degradation_data[i+num_points]["degradation_percent"]
                    break

        return {
            "is_stabilized": is_stabilized,
            "max_recent_change": max_change,
            "threshold": threshold,
            "stabilization_time": stabilization_time,
            "stabilization_degradation": stabilization_degradation,
        }

    def _calculate_recovery(
        self,
        degradation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate power recovery after dark storage.

        Args:
            degradation_data: List of degradation data points

        Returns:
            Recovery analysis results
        """
        # Find post-exposure (recovery) measurements
        post_exposure = [d for d in degradation_data if d.get("measurement_type") == "post_exposure"]

        if not post_exposure:
            return {
                "recovery_measured": False,
                "message": "No post-exposure measurements"
            }

        # Get final degraded power (last during_exposure measurement)
        during_exposure = [d for d in degradation_data if d.get("measurement_type") == "during_exposure"]

        if not during_exposure:
            return {
                "recovery_measured": False,
                "message": "No during-exposure measurements for comparison"
            }

        degraded_power = during_exposure[-1]["pmax"]
        recovery_power = post_exposure[-1]["pmax"]

        # Get baseline
        baseline_power = degradation_data[0]["pmax"] if degradation_data else 0

        if baseline_power == 0:
            return {
                "recovery_measured": False,
                "message": "Invalid baseline power"
            }

        # Calculate recovery percentage
        power_loss = baseline_power - degraded_power
        power_recovered = recovery_power - degraded_power

        if power_loss > 0:
            recovery_percent = 100 * power_recovered / power_loss
        else:
            recovery_percent = 0.0

        return {
            "recovery_measured": True,
            "degraded_power": degraded_power,
            "recovery_power": recovery_power,
            "power_recovered": power_recovered,
            "recovery_percent": recovery_percent,
        }

    def _perform_qc_checks(
        self,
        measurements: List[Dict[str, Any]],
        baseline_power: float,
        max_degradation: float
    ) -> List[Dict[str, Any]]:
        """
        Perform QC checks on test data.

        Args:
            measurements: List of measurements
            baseline_power: Baseline power
            max_degradation: Maximum degradation percentage

        Returns:
            List of QC check results
        """
        qc_results = []

        # Check data completeness
        expected_count = 15  # Approximate for LID-001 (3 initial + 12 during exposure)
        completeness_check = self.qc_checker.check_data_completeness(
            measurements, expected_count
        )
        qc_results.append(completeness_check)

        # Check repeatability of initial measurements
        initial_measurements = [m for m in measurements if m.get("measurement_type") == "initial"]
        if len(initial_measurements) >= 2:
            initial_powers = [m.get("pmax") for m in initial_measurements if m.get("pmax")]
            if initial_powers:
                repeatability_check = self.qc_checker.check_measurement_repeatability(
                    initial_powers
                )
                qc_results.append(repeatability_check)

        # Check chronological order
        chronological_check = self.qc_checker.check_chronological_order(measurements)
        qc_results.append(chronological_check)

        # Check maximum degradation against criteria
        max_allowable_degradation = 5.0  # From QC criteria
        if max_degradation > max_allowable_degradation:
            qc_results.append({
                "check_name": "Maximum Degradation Limit",
                "check_category": "degradation",
                "passed": False,
                "severity": "critical",
                "expected_value": f"<= {max_allowable_degradation}%",
                "actual_value": f"{max_degradation:.2f}%",
                "message": f"Maximum degradation {max_degradation:.2f}% exceeds limit {max_allowable_degradation}%",
            })

        # Check environmental conditions for each measurement
        for m in measurements:
            irr = m.get("irradiance")
            temp = m.get("temperature")
            if irr is not None and temp is not None:
                env_checks = self.qc_checker.check_environmental_conditions(irr, temp)
                qc_results.extend(env_checks)

        return qc_results

    def generate_summary_report(
        self,
        analysis_results: Dict[str, Any],
        sample_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text summary report.

        Args:
            analysis_results: Analysis results from analyze_test_run
            sample_info: Optional sample information

        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append("LID-001 LIGHT-INDUCED DEGRADATION TEST REPORT")
        report.append("=" * 80)
        report.append("")

        # Sample information
        if sample_info:
            report.append("SAMPLE INFORMATION")
            report.append("-" * 80)
            report.append(f"Sample ID: {sample_info.get('sample_id', 'N/A')}")
            report.append(f"Manufacturer: {sample_info.get('manufacturer', 'N/A')}")
            report.append(f"Model: {sample_info.get('model', 'N/A')}")
            report.append(f"Technology: {sample_info.get('technology', 'N/A')}")
            report.append("")

        # Test results
        report.append("TEST RESULTS")
        report.append("-" * 80)
        report.append(f"Baseline Power: {analysis_results.get('baseline_power', 0):.2f} W")
        report.append(f"Maximum Degradation: {analysis_results.get('max_degradation_percent', 0):.2f}%")
        report.append(f"  at {analysis_results.get('max_degradation_time_hours', 0):.1f} hours")
        report.append(f"Final Degradation: {analysis_results.get('final_degradation_percent', 0):.2f}%")
        report.append(f"Degradation Rate: {analysis_results.get('degradation_rate_percent_per_hour', 0):.4f} %/hour")
        report.append("")

        # Stabilization
        report.append("STABILIZATION ANALYSIS")
        report.append("-" * 80)
        if analysis_results.get('is_stabilized'):
            report.append("Status: STABILIZED")
            stab_time = analysis_results.get('stabilization_time_hours')
            stab_deg = analysis_results.get('stabilization_degradation_percent')
            if stab_time and stab_deg:
                report.append(f"Stabilization Time: {stab_time:.1f} hours")
                report.append(f"Stabilization Degradation: {stab_deg:.2f}%")
        else:
            report.append("Status: NOT STABILIZED")
        report.append("")

        # Recovery
        if analysis_results.get('recovery_percent') is not None:
            report.append("RECOVERY ANALYSIS")
            report.append("-" * 80)
            report.append(f"Recovery: {analysis_results.get('recovery_percent', 0):.1f}%")
            report.append(f"Recovery Power: {analysis_results.get('recovery_power', 0):.2f} W")
            report.append("")

        # QC Status
        report.append("QUALITY CONTROL")
        report.append("-" * 80)
        qc_passed = analysis_results.get('qc_passed', False)
        report.append(f"Overall QC Status: {'PASS' if qc_passed else 'FAIL'}")
        report.append(f"Number of Measurements: {analysis_results.get('num_measurements', 0)}")
        report.append(f"Outliers Detected: {analysis_results.get('num_outliers', 0)}")
        report.append("")

        # QC Issues
        qc_results = analysis_results.get('qc_results', [])
        failed_qc = [qc for qc in qc_results if not qc.get('passed', True)]

        if failed_qc:
            report.append("QC ISSUES")
            report.append("-" * 80)
            for qc in failed_qc:
                report.append(f"[{qc.get('severity', 'unknown').upper()}] {qc.get('check_name', 'Unknown')}")
                report.append(f"  {qc.get('message', 'No message')}")
            report.append("")

        report.append("=" * 80)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        return "\n".join(report)
