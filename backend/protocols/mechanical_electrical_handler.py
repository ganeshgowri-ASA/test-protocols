"""
Mechanical Load and PID Testing Protocol Handler

This module provides functionality for managing mechanical load tests and
Potential Induced Degradation (PID) tests, including cycle management,
monitoring, degradation calculations, and recovery tracking.

Author: PV Testing Lab
Version: 1.0
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from enum import Enum


class LoadType(Enum):
    """Types of mechanical loads"""
    STATIC = "static_load"
    DYNAMIC = "dynamic_load"
    CYCLIC = "cyclic_load"


class PIDAffectLevel(Enum):
    """PID susceptibility classification levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class LoadCycle:
    """Data structure for a single load cycle"""
    cycle_number: int
    load_value: float  # Pa
    application_time: datetime
    dwell_duration: int  # seconds
    deflection_measurements: Dict[str, List[float]] = field(default_factory=dict)
    max_deflection: float = 0.0
    max_deflection_location: str = ""

    def add_deflection_measurement(self, location: str, value: float):
        """Add a deflection measurement at a specific location"""
        if location not in self.deflection_measurements:
            self.deflection_measurements[location] = []
        self.deflection_measurements[location].append(value)

        if abs(value) > abs(self.max_deflection):
            self.max_deflection = value
            self.max_deflection_location = location


@dataclass
class ElectricalMeasurement:
    """Electrical performance measurement data"""
    timestamp: datetime
    stage: str
    pmax: float  # W
    voc: float  # V
    isc: float  # A
    fill_factor: float  # %

    def calculate_fill_factor(self) -> float:
        """Calculate fill factor from measurements"""
        if self.voc > 0 and self.isc > 0:
            self.fill_factor = (self.pmax / (self.voc * self.isc)) * 100
        return self.fill_factor


@dataclass
class PIDMonitoringData:
    """Real-time PID monitoring data point"""
    timestamp: datetime
    voltage: float  # V
    leakage_current: float  # mA
    temperature: float  # °C
    humidity: float  # %RH

    def is_within_limits(self,
                        voltage_tolerance: float = 100.0,
                        current_threshold: float = 10.0,
                        temp_tolerance: float = 5.0,
                        humidity_tolerance: float = 10.0) -> Tuple[bool, List[str]]:
        """Check if measurements are within acceptable limits"""
        issues = []

        if abs(self.voltage - (-1000)) > voltage_tolerance:
            issues.append(f"Voltage deviation: {self.voltage}V")

        if self.leakage_current > current_threshold:
            issues.append(f"Excessive leakage current: {self.leakage_current}mA")

        if abs(self.temperature - 60) > temp_tolerance:
            issues.append(f"Temperature deviation: {self.temperature}°C")

        if abs(self.humidity - 85) > humidity_tolerance:
            issues.append(f"Humidity deviation: {self.humidity}%RH")

        return len(issues) == 0, issues


class MechanicalLoadHandler:
    """Handler for mechanical load testing operations"""

    def __init__(self, protocol_data: Dict):
        """
        Initialize mechanical load handler

        Args:
            protocol_data: Dictionary containing protocol configuration
        """
        self.protocol = protocol_data
        self.cycles: List[LoadCycle] = []
        self.electrical_measurements: List[ElectricalMeasurement] = []
        self.baseline_power: Optional[float] = None

    def start_load_cycle(self, cycle_number: int, load_value: float,
                        dwell_duration: int) -> LoadCycle:
        """
        Start a new load cycle

        Args:
            cycle_number: Sequential cycle number
            load_value: Applied load in Pa
            dwell_duration: Duration to maintain load in seconds

        Returns:
            LoadCycle object for this cycle
        """
        cycle = LoadCycle(
            cycle_number=cycle_number,
            load_value=load_value,
            application_time=datetime.now(),
            dwell_duration=dwell_duration
        )
        self.cycles.append(cycle)
        return cycle

    def record_deflection(self, cycle_number: int, location: str,
                         deflection: float) -> None:
        """
        Record deflection measurement for a specific cycle

        Args:
            cycle_number: Cycle number (1-indexed)
            location: Measurement location (e.g., 'center', 'quarter_point_1')
            deflection: Deflection value in mm
        """
        if cycle_number <= len(self.cycles):
            cycle = self.cycles[cycle_number - 1]
            cycle.add_deflection_measurement(location, deflection)

    def record_electrical_measurement(self, stage: str, pmax: float,
                                     voc: float, isc: float) -> ElectricalMeasurement:
        """
        Record electrical performance measurement

        Args:
            stage: Test stage (e.g., 'baseline', 'after_cycle_1')
            pmax: Maximum power in W
            voc: Open circuit voltage in V
            isc: Short circuit current in A

        Returns:
            ElectricalMeasurement object
        """
        measurement = ElectricalMeasurement(
            timestamp=datetime.now(),
            stage=stage,
            pmax=pmax,
            voc=voc,
            isc=isc,
            fill_factor=0.0
        )
        measurement.calculate_fill_factor()
        self.electrical_measurements.append(measurement)

        if stage == "baseline":
            self.baseline_power = pmax

        return measurement

    def calculate_power_degradation(self, final_power: float) -> Dict:
        """
        Calculate power degradation from baseline

        Args:
            final_power: Final measured power in W

        Returns:
            Dictionary with degradation analysis
        """
        if self.baseline_power is None:
            raise ValueError("Baseline power not recorded")

        degradation_pct = ((final_power - self.baseline_power) /
                          self.baseline_power) * 100

        passed = abs(degradation_pct) <= 5.0

        return {
            "baseline_power": self.baseline_power,
            "final_power": final_power,
            "degradation_percent": degradation_pct,
            "degradation_watts": final_power - self.baseline_power,
            "passed": passed,
            "threshold": "±5%",
            "result": "PASS" if passed else "FAIL"
        }

    def analyze_deflection(self, cycle_number: int) -> Dict:
        """
        Analyze deflection measurements for a specific cycle

        Args:
            cycle_number: Cycle number to analyze

        Returns:
            Dictionary with deflection analysis
        """
        if cycle_number > len(self.cycles):
            raise ValueError(f"Cycle {cycle_number} not found")

        cycle = self.cycles[cycle_number - 1]

        # Calculate statistics for each location
        location_stats = {}
        for location, measurements in cycle.deflection_measurements.items():
            location_stats[location] = {
                "mean": np.mean(measurements),
                "max": np.max(np.abs(measurements)),
                "min": np.min(measurements),
                "std_dev": np.std(measurements)
            }

        return {
            "cycle_number": cycle_number,
            "max_deflection": cycle.max_deflection,
            "max_deflection_location": cycle.max_deflection_location,
            "location_statistics": location_stats,
            "load_value": cycle.load_value
        }

    def calculate_permanent_deformation(self, pre_load_deflection: float,
                                       post_recovery_deflection: float,
                                       max_deflection: float) -> Dict:
        """
        Calculate permanent deformation after recovery period

        Args:
            pre_load_deflection: Deflection before load application
            post_recovery_deflection: Deflection 24h after load removal
            max_deflection: Maximum deflection during load

        Returns:
            Dictionary with deformation analysis
        """
        permanent_def = post_recovery_deflection - pre_load_deflection
        permanent_def_pct = (permanent_def / max_deflection) * 100 if max_deflection != 0 else 0

        passed = abs(permanent_def_pct) < 10.0

        return {
            "permanent_deformation": permanent_def,
            "permanent_deformation_percent": permanent_def_pct,
            "max_deflection_during_load": max_deflection,
            "acceptance_criteria": "<10% of max deflection",
            "passed": passed,
            "result": "PASS" if passed else "FAIL"
        }

    def generate_load_profile(self, num_cycles: int,
                             pressure_positive: float = 2400,
                             pressure_negative: float = -2400) -> List[Dict]:
        """
        Generate load profile for cyclic testing

        Args:
            num_cycles: Number of cycles to generate
            pressure_positive: Positive pressure in Pa
            pressure_negative: Negative pressure in Pa

        Returns:
            List of load steps with timing
        """
        profile = []

        for cycle in range(1, num_cycles + 1):
            # Positive pressure phase
            profile.append({
                "cycle": cycle,
                "phase": "positive",
                "pressure": pressure_positive,
                "duration_seconds": 3600,  # 1 hour
                "ramp_rate": 100  # Pa/s
            })

            # Release phase
            profile.append({
                "cycle": cycle,
                "phase": "release",
                "pressure": 0,
                "duration_seconds": 900,  # 15 minutes
                "ramp_rate": 100
            })

            # Negative pressure phase
            profile.append({
                "cycle": cycle,
                "phase": "negative",
                "pressure": pressure_negative,
                "duration_seconds": 3600,  # 1 hour
                "ramp_rate": 100
            })

            # Release phase
            profile.append({
                "cycle": cycle,
                "phase": "release_final",
                "pressure": 0,
                "duration_seconds": 900,  # 15 minutes
                "ramp_rate": 100
            })

        return profile


class PIDTestHandler:
    """Handler for Potential Induced Degradation testing operations"""

    def __init__(self, protocol_data: Dict):
        """
        Initialize PID test handler

        Args:
            protocol_data: Dictionary containing protocol configuration
        """
        self.protocol = protocol_data
        self.monitoring_data: List[PIDMonitoringData] = []
        self.performance_measurements: List[ElectricalMeasurement] = []
        self.baseline_power: Optional[float] = None
        self.test_start_time: Optional[datetime] = None
        self.recovery_start_time: Optional[datetime] = None

    def start_test(self, baseline_power: float) -> None:
        """
        Start PID test and record baseline

        Args:
            baseline_power: Baseline power measurement in W
        """
        self.test_start_time = datetime.now()
        self.baseline_power = baseline_power

    def add_monitoring_data(self, voltage: float, leakage_current: float,
                           temperature: float, humidity: float) -> PIDMonitoringData:
        """
        Add a monitoring data point

        Args:
            voltage: Applied voltage in V
            leakage_current: Leakage current in mA
            temperature: Chamber temperature in °C
            humidity: Relative humidity in %RH

        Returns:
            PIDMonitoringData object
        """
        data_point = PIDMonitoringData(
            timestamp=datetime.now(),
            voltage=voltage,
            leakage_current=leakage_current,
            temperature=temperature,
            humidity=humidity
        )
        self.monitoring_data.append(data_point)
        return data_point

    def check_safety_limits(self, critical_current: float = 50.0) -> Tuple[bool, str]:
        """
        Check if current measurements are within safety limits

        Args:
            critical_current: Critical leakage current threshold in mA

        Returns:
            Tuple of (is_safe, message)
        """
        if not self.monitoring_data:
            return True, "No data to check"

        latest = self.monitoring_data[-1]

        if latest.leakage_current > critical_current:
            return False, f"CRITICAL: Leakage current {latest.leakage_current}mA exceeds {critical_current}mA - EMERGENCY SHUTDOWN REQUIRED"

        is_ok, issues = latest.is_within_limits()
        if not is_ok:
            return True, f"WARNING: {', '.join(issues)}"

        return True, "All parameters within limits"

    def record_performance_measurement(self, interval_hours: int,
                                      pmax: float, voc: float,
                                      isc: float) -> ElectricalMeasurement:
        """
        Record performance measurement at specified interval

        Args:
            interval_hours: Hours since test start
            pmax: Maximum power in W
            voc: Open circuit voltage in V
            isc: Short circuit current in A

        Returns:
            ElectricalMeasurement object
        """
        stage = f"after_{interval_hours}h"
        measurement = ElectricalMeasurement(
            timestamp=datetime.now(),
            stage=stage,
            pmax=pmax,
            voc=voc,
            isc=isc,
            fill_factor=0.0
        )
        measurement.calculate_fill_factor()
        self.performance_measurements.append(measurement)
        return measurement

    def calculate_degradation_rate(self, hours_elapsed: float,
                                   current_power: float) -> Dict:
        """
        Calculate degradation rate

        Args:
            hours_elapsed: Hours since test start
            current_power: Current power measurement in W

        Returns:
            Dictionary with degradation rate analysis
        """
        if self.baseline_power is None:
            raise ValueError("Baseline power not recorded")

        if hours_elapsed == 0:
            return {
                "degradation_rate_pct_per_hour": 0.0,
                "cumulative_degradation_pct": 0.0
            }

        cumulative_deg = ((current_power - self.baseline_power) /
                         self.baseline_power) * 100
        degradation_rate = cumulative_deg / hours_elapsed

        return {
            "hours_elapsed": hours_elapsed,
            "baseline_power": self.baseline_power,
            "current_power": current_power,
            "cumulative_degradation_pct": cumulative_deg,
            "degradation_rate_pct_per_hour": degradation_rate,
            "power_loss_watts": current_power - self.baseline_power
        }

    def classify_pid_susceptibility(self, total_degradation_pct: float) -> Dict:
        """
        Classify PID susceptibility based on total degradation

        Args:
            total_degradation_pct: Total power degradation percentage

        Returns:
            Dictionary with classification results
        """
        # Use absolute value for classification
        abs_deg = abs(total_degradation_pct)

        if abs_deg < 2:
            level = PIDAffectLevel.NONE
            description = "No significant PID observed"
            passed = True
        elif abs_deg < 5:
            level = PIDAffectLevel.LOW
            description = "Minor PID susceptibility"
            passed = True
        elif abs_deg < 10:
            level = PIDAffectLevel.MEDIUM
            description = "Moderate PID susceptibility"
            passed = False
        else:
            level = PIDAffectLevel.HIGH
            description = "Severe PID susceptibility - module fails test"
            passed = False

        return {
            "total_degradation_percent": total_degradation_pct,
            "pid_susceptibility": level.value,
            "description": description,
            "passed": passed,
            "standard_threshold": "5% per IEC 62804-1",
            "result": "PASS" if passed else "FAIL"
        }

    def start_recovery_phase(self) -> None:
        """Start the recovery phase tracking"""
        self.recovery_start_time = datetime.now()

    def calculate_recovery(self, degraded_power: float,
                          recovery_power: float) -> Dict:
        """
        Calculate recovery percentage after recovery phase

        Args:
            degraded_power: Power at end of stress test
            recovery_power: Power after recovery period

        Returns:
            Dictionary with recovery analysis
        """
        if self.baseline_power is None:
            raise ValueError("Baseline power not recorded")

        power_loss = self.baseline_power - degraded_power
        power_recovered = recovery_power - degraded_power

        if power_loss != 0:
            recovery_pct = (power_recovered / power_loss) * 100
        else:
            recovery_pct = 0.0

        permanent_loss = self.baseline_power - recovery_power
        permanent_loss_pct = (permanent_loss / self.baseline_power) * 100

        # Classify recovery
        if recovery_pct > 90:
            recovery_type = "fully_reversible"
        elif recovery_pct >= 50:
            recovery_type = "partially_reversible"
        else:
            recovery_type = "irreversible"

        return {
            "baseline_power": self.baseline_power,
            "degraded_power": degraded_power,
            "recovery_power": recovery_power,
            "power_loss": power_loss,
            "power_recovered": power_recovered,
            "recovery_percentage": recovery_pct,
            "permanent_loss": permanent_loss,
            "permanent_loss_percentage": permanent_loss_pct,
            "recovery_classification": recovery_type
        }

    def analyze_leakage_current_trends(self) -> Dict:
        """
        Analyze leakage current trends over time

        Returns:
            Dictionary with leakage current analysis
        """
        if not self.monitoring_data:
            return {"error": "No monitoring data available"}

        currents = [d.leakage_current for d in self.monitoring_data]
        timestamps = [d.timestamp for d in self.monitoring_data]

        # Calculate statistics
        mean_current = np.mean(currents)
        max_current = np.max(currents)
        min_current = np.min(currents)
        std_current = np.std(currents)

        # Find time of max current
        max_idx = np.argmax(currents)
        max_current_time = timestamps[max_idx]

        # Check for increasing trend
        if len(currents) > 10:
            recent_mean = np.mean(currents[-10:])
            early_mean = np.mean(currents[:10])
            trend = "increasing" if recent_mean > early_mean else "stable/decreasing"
        else:
            trend = "insufficient_data"

        return {
            "mean_leakage_current": mean_current,
            "max_leakage_current": max_current,
            "min_leakage_current": min_current,
            "std_deviation": std_current,
            "max_occurred_at": max_current_time.isoformat(),
            "trend": trend,
            "data_points": len(currents)
        }


def load_protocol_template(protocol_id: str) -> Dict:
    """
    Load protocol template from JSON file

    Args:
        protocol_id: Protocol ID (e.g., 'PVTP-005-ML' or 'PVTP-006-PID')

    Returns:
        Dictionary containing protocol data
    """
    filename_map = {
        "PVTP-005-ML": "templates/mechanical_load.json",
        "PVTP-006-PID": "templates/pid_testing.json"
    }

    if protocol_id not in filename_map:
        raise ValueError(f"Unknown protocol ID: {protocol_id}")

    with open(filename_map[protocol_id], 'r') as f:
        return json.load(f)


def export_test_data(handler, output_file: str, format: str = "json") -> None:
    """
    Export test data to file

    Args:
        handler: MechanicalLoadHandler or PIDTestHandler instance
        output_file: Output file path
        format: Export format ('json' or 'csv')
    """
    if format == "json":
        data = {
            "protocol_id": handler.protocol.get("protocol_metadata", {}).get("id", "unknown"),
            "export_timestamp": datetime.now().isoformat(),
        }

        if isinstance(handler, MechanicalLoadHandler):
            data["test_type"] = "mechanical_load"
            data["cycles"] = [
                {
                    "cycle_number": c.cycle_number,
                    "load_value": c.load_value,
                    "application_time": c.application_time.isoformat(),
                    "max_deflection": c.max_deflection,
                    "max_deflection_location": c.max_deflection_location,
                    "deflection_measurements": c.deflection_measurements
                }
                for c in handler.cycles
            ]
            data["electrical_measurements"] = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "stage": m.stage,
                    "pmax": m.pmax,
                    "voc": m.voc,
                    "isc": m.isc,
                    "fill_factor": m.fill_factor
                }
                for m in handler.electrical_measurements
            ]

        elif isinstance(handler, PIDTestHandler):
            data["test_type"] = "pid_testing"
            data["monitoring_data"] = [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "voltage": d.voltage,
                    "leakage_current": d.leakage_current,
                    "temperature": d.temperature,
                    "humidity": d.humidity
                }
                for d in handler.monitoring_data
            ]
            data["performance_measurements"] = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "stage": m.stage,
                    "pmax": m.pmax,
                    "voc": m.voc,
                    "isc": m.isc,
                    "fill_factor": m.fill_factor
                }
                for m in handler.performance_measurements
            ]

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    elif format == "csv":
        import csv
        # CSV export implementation would go here
        raise NotImplementedError("CSV export not yet implemented")


if __name__ == "__main__":
    # Example usage
    print("Mechanical Load and PID Testing Protocol Handler")
    print("=" * 50)

    # Example: Mechanical Load Test
    print("\n1. Mechanical Load Test Example:")
    ml_protocol = load_protocol_template("PVTP-005-ML")
    ml_handler = MechanicalLoadHandler(ml_protocol)

    # Start a cycle
    cycle = ml_handler.start_load_cycle(1, 2400, 3600)
    print(f"Started cycle {cycle.cycle_number} with {cycle.load_value} Pa load")

    # Record some deflections
    ml_handler.record_deflection(1, "center", 5.2)
    ml_handler.record_deflection(1, "quarter_point_1", 3.1)
    print("Recorded deflection measurements")

    # Record electrical measurements
    ml_handler.record_electrical_measurement("baseline", 300.0, 40.0, 9.0)
    ml_handler.record_electrical_measurement("after_cycle_1", 297.5, 39.8, 8.98)

    # Calculate degradation
    degradation = ml_handler.calculate_power_degradation(297.5)
    print(f"Power degradation: {degradation['degradation_percent']:.2f}% - {degradation['result']}")

    # Example: PID Test
    print("\n2. PID Test Example:")
    pid_protocol = load_protocol_template("PVTP-006-PID")
    pid_handler = PIDTestHandler(pid_protocol)

    # Start test
    pid_handler.start_test(baseline_power=300.0)
    print("Started PID test with 300W baseline")

    # Add monitoring data
    pid_handler.add_monitoring_data(-1000, 2.5, 60.0, 85.0)
    is_safe, msg = pid_handler.check_safety_limits()
    print(f"Safety check: {msg}")

    # Record performance at 24h
    pid_handler.record_performance_measurement(24, 285.0, 39.5, 8.7)

    # Calculate degradation
    deg_rate = pid_handler.calculate_degradation_rate(24, 285.0)
    print(f"Degradation after 24h: {deg_rate['cumulative_degradation_pct']:.2f}%")

    # Classify susceptibility
    classification = pid_handler.classify_pid_susceptibility(deg_rate['cumulative_degradation_pct'])
    print(f"PID Susceptibility: {classification['pid_susceptibility']} - {classification['result']}")
