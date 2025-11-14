"""LID-001 Light-Induced Degradation protocol implementation."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

from .base_protocol import BaseProtocol


class LID001Protocol(BaseProtocol):
    """
    Implementation of the LID-001 Light-Induced Degradation protocol.

    This protocol tests for power degradation in PV modules when first
    exposed to light, primarily due to boron-oxygen defects in p-type silicon.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize LID-001 protocol."""
        super().__init__(protocol_id="LID-001", config_path=config_path)
        self.baseline_power = None
        self.measurements_history = []

    def calculate_baseline_power(self, initial_measurements: List[Dict[str, Any]]) -> float:
        """
        Calculate baseline power from initial measurements.

        Args:
            initial_measurements: List of initial measurement dictionaries

        Returns:
            Baseline power (average of initial measurements)
        """
        if not initial_measurements:
            raise ValueError("No initial measurements provided")

        powers = [m.get("pmax") for m in initial_measurements if m.get("pmax") is not None]

        if not powers:
            raise ValueError("No valid Pmax values in initial measurements")

        self.baseline_power = np.mean(powers)
        return self.baseline_power

    def calculate_degradation(
        self,
        current_power: float,
        baseline_power: Optional[float] = None
    ) -> float:
        """
        Calculate power degradation percentage.

        Args:
            current_power: Current measured power
            baseline_power: Baseline power (uses stored baseline if not provided)

        Returns:
            Degradation percentage (positive values indicate power loss)
        """
        if baseline_power is None:
            baseline_power = self.baseline_power

        if baseline_power is None or baseline_power == 0:
            raise ValueError("Baseline power not set or is zero")

        degradation_pct = 100 * (baseline_power - current_power) / baseline_power
        return degradation_pct

    def check_stabilization(
        self,
        recent_measurements: List[Dict[str, Any]],
        threshold_percent: Optional[float] = None
    ) -> tuple[bool, float]:
        """
        Check if degradation has stabilized.

        Args:
            recent_measurements: List of recent measurements (chronological order)
            threshold_percent: Stabilization threshold (uses QC criteria if not provided)

        Returns:
            Tuple of (is_stabilized, current_rate_of_change)
        """
        qc_criteria = self.get_qc_criteria()

        if threshold_percent is None:
            threshold_percent = qc_criteria.get("stabilization_threshold", 0.5)

        min_points = qc_criteria.get("min_stabilization_points", 3)

        if len(recent_measurements) < min_points:
            return False, float("inf")

        # Get the last N measurements
        last_n = recent_measurements[-min_points:]

        # Calculate degradation for each
        degradations = []
        for m in last_n:
            if m.get("pmax") is not None:
                deg = self.calculate_degradation(m["pmax"])
                degradations.append(deg)

        if len(degradations) < min_points:
            return False, float("inf")

        # Calculate maximum change between consecutive measurements
        max_change = 0.0
        for i in range(1, len(degradations)):
            change = abs(degradations[i] - degradations[i-1])
            max_change = max(max_change, change)

        is_stabilized = max_change < threshold_percent

        return is_stabilized, max_change

    def validate_environmental_conditions(
        self,
        irradiance: float,
        temperature: float
    ) -> tuple[bool, List[str]]:
        """
        Validate environmental test conditions.

        Args:
            irradiance: Measured irradiance (W/m²)
            temperature: Measured temperature (°C)

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        params = self.get_parameters()
        qc_criteria = self.get_qc_criteria()

        # Check irradiance
        expected_irr = params.get("light_exposure", {}).get("irradiance", 1000.0)
        irr_tolerance = qc_criteria.get("irradiance_tolerance_percent", 2.0)
        min_irr = expected_irr * (1 - irr_tolerance / 100)
        max_irr = expected_irr * (1 + irr_tolerance / 100)

        if not (min_irr <= irradiance <= max_irr):
            errors.append(
                f"Irradiance {irradiance} W/m² outside acceptable range "
                f"[{min_irr:.1f}, {max_irr:.1f}] W/m²"
            )

        # Check temperature
        expected_temp = params.get("environmental_conditions", {}).get("temperature", 25.0)
        temp_tolerance = qc_criteria.get("temperature_tolerance_celsius", 2.0)
        min_temp = expected_temp - temp_tolerance
        max_temp = expected_temp + temp_tolerance

        if not (min_temp <= temperature <= max_temp):
            errors.append(
                f"Temperature {temperature}°C outside acceptable range "
                f"[{min_temp:.1f}, {max_temp:.1f}]°C"
            )

        return len(errors) == 0, errors

    def check_qc_criteria(
        self,
        measurement: Dict[str, Any],
        degradation_percent: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Check measurement against QC criteria.

        Args:
            measurement: Measurement data
            degradation_percent: Pre-calculated degradation (optional)

        Returns:
            List of QC check results
        """
        qc_results = []
        qc_criteria = self.get_qc_criteria()

        # Check fill factor
        ff = measurement.get("fill_factor")
        if ff is not None:
            min_ff = qc_criteria.get("min_fill_factor", 0.50)
            max_ff = qc_criteria.get("max_fill_factor", 0.85)

            if not (min_ff <= ff <= max_ff):
                qc_results.append({
                    "check_name": "Fill Factor Range",
                    "passed": False,
                    "severity": "warning",
                    "message": f"Fill factor {ff:.4f} outside normal range [{min_ff}, {max_ff}]",
                    "actual_value": str(ff),
                    "threshold": f"[{min_ff}, {max_ff}]",
                })

        # Check environmental conditions
        irradiance = measurement.get("irradiance")
        temperature = measurement.get("temperature")

        if irradiance is not None and temperature is not None:
            env_valid, env_errors = self.validate_environmental_conditions(
                irradiance, temperature
            )
            if not env_valid:
                for error in env_errors:
                    qc_results.append({
                        "check_name": "Environmental Conditions",
                        "passed": False,
                        "severity": "error",
                        "message": error,
                    })

        # Check degradation limit
        if degradation_percent is not None:
            max_deg = qc_criteria.get("max_degradation_percent", 10.0)
            acceptance_max = qc_criteria.get("acceptance_criteria", {}).get(
                "max_allowable_degradation", {}
            ).get("percent", 5.0)

            if degradation_percent > acceptance_max:
                qc_results.append({
                    "check_name": "Maximum Degradation",
                    "passed": False,
                    "severity": "critical",
                    "message": f"Degradation {degradation_percent:.2f}% exceeds acceptance limit {acceptance_max}%",
                    "actual_value": f"{degradation_percent:.2f}%",
                    "threshold": f"{acceptance_max}%",
                })
            elif degradation_percent > max_deg:
                qc_results.append({
                    "check_name": "Degradation Warning",
                    "passed": False,
                    "severity": "warning",
                    "message": f"Degradation {degradation_percent:.2f}% exceeds typical range",
                    "actual_value": f"{degradation_percent:.2f}%",
                    "threshold": f"{max_deg}%",
                })

        return qc_results

    def get_measurement_schedule(self) -> List[Dict[str, Any]]:
        """
        Get the complete measurement schedule for LID-001.

        Returns:
            List of measurement point definitions
        """
        params = self.get_parameters()
        schedule = params.get("measurement_schedule", {})

        measurement_points = []

        # Initial measurements
        initial = schedule.get("initial", {})
        num_initial = initial.get("num_measurements", 3)
        interval_min = initial.get("interval_minutes", 30)

        for i in range(num_initial):
            measurement_points.append({
                "type": "initial",
                "sequence": i + 1,
                "time_hours": -(num_initial - i) * interval_min / 60,  # Negative = before start
                "label": f"Initial {i+1}",
            })

        # During exposure measurements
        during = schedule.get("during_exposure", [])
        for point in during:
            measurement_points.append({
                "type": "during_exposure",
                "time_hours": point.get("time_hours"),
                "label": point.get("label"),
            })

        # Post-exposure measurements (optional)
        post = schedule.get("post_exposure", {})
        if post.get("num_measurements", 0) > 0:
            recovery_hours = post.get("recovery_period_hours", 24.0)
            num_post = post.get("num_measurements", 2)

            for i in range(num_post):
                measurement_points.append({
                    "type": "post_exposure",
                    "time_hours": recovery_hours + i * 1.0,  # 1 hour apart
                    "label": f"Recovery {i+1}",
                })

        return measurement_points

    def generate_measurement_timestamps(
        self,
        start_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate actual timestamps for all measurement points.

        Args:
            start_time: Test start time

        Returns:
            List of measurement points with timestamps
        """
        schedule = self.get_measurement_schedule()

        for point in schedule:
            time_hours = point.get("time_hours", 0)
            timestamp = start_time + timedelta(hours=time_hours)
            point["timestamp"] = timestamp

        return schedule

    def calculate_degradation_rate(
        self,
        measurements: List[Dict[str, Any]]
    ) -> Optional[float]:
        """
        Calculate average degradation rate.

        Args:
            measurements: List of measurements with timestamps and power

        Returns:
            Degradation rate in %/hour, or None if insufficient data
        """
        if len(measurements) < 2:
            return None

        # Calculate degradation for each measurement
        degradations = []
        times = []

        for m in measurements:
            if m.get("pmax") is not None and m.get("elapsed_hours") is not None:
                deg = self.calculate_degradation(m["pmax"])
                degradations.append(deg)
                times.append(m["elapsed_hours"])

        if len(degradations) < 2:
            return None

        # Linear regression to find rate
        times = np.array(times)
        degradations = np.array(degradations)

        # Calculate slope
        coefficients = np.polyfit(times, degradations, 1)
        rate = coefficients[0]  # %/hour

        return rate

    def __repr__(self):
        return f"<LID001Protocol(baseline_power={self.baseline_power})>"
