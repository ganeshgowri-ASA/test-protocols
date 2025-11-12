"""
Environmental Test Protocol Handler
Unified handler for Humidity-Freeze (PVTP-003-HF) and Damp Heat (PVTP-004-DH) protocols
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from dataclasses import dataclass, asdict


@dataclass
class EnvironmentalConditions:
    """Environmental chamber conditions"""
    temperature: float
    humidity: float
    timestamp: datetime
    chamber_status: str
    alarms: List[str]


@dataclass
class PhaseTransition:
    """Phase transition event for humidity-freeze cycling"""
    from_phase: str
    to_phase: str
    start_time: datetime
    end_time: Optional[datetime]
    target_rate: float
    actual_max_rate: float
    is_valid: bool
    validation_notes: str


@dataclass
class PerformanceMeasurement:
    """Module performance measurement at checkpoint"""
    timestamp: datetime
    interval: float  # hours from start
    Pmax: float
    Voc: float
    Isc: float
    FF: float
    insulation_resistance: float
    visual_defects: List[str]
    power_loss_percentage: float


class EnvironmentalProtocolHandler:
    """Unified handler for environmental stress test protocols"""

    def __init__(self, protocol_type: str, protocol_path: str):
        """
        Initialize handler for environmental protocols

        Args:
            protocol_type: Either "humidity_freeze" or "damp_heat"
            protocol_path: Path to the protocol JSON template
        """
        self.protocol_type = protocol_type
        self.protocol_path = Path(protocol_path)
        self.protocol_data = self._load_protocol()
        self.test_start_time = None
        self.current_cycle = 0
        self.current_phase = "not_started"
        self.phase_history = []
        self.measurements = []
        self.continuous_data = []
        self.nonconformances = []

    def _load_protocol(self) -> Dict:
        """Load protocol template from JSON file"""
        with open(self.protocol_path, 'r') as f:
            return json.load(f)

    def start_test(self, module_serial_numbers: List[str]) -> Dict:
        """
        Initialize and start the environmental test

        Args:
            module_serial_numbers: List of module serial numbers under test

        Returns:
            Test session information
        """
        self.test_start_time = datetime.now()
        self.current_phase = "stabilization"

        # Update protocol inputs with module info
        if self.protocol_type == "humidity_freeze":
            self.protocol_data['protocol_inputs']['module_configuration']['serial_numbers'] = module_serial_numbers
        else:  # damp_heat
            self.protocol_data['protocol_inputs']['module_configuration']['serial_numbers'] = module_serial_numbers

        session_info = {
            "protocol_id": self.protocol_data['protocol_metadata']['id'],
            "protocol_name": self.protocol_data['protocol_metadata']['name'],
            "protocol_type": self.protocol_type,
            "start_time": self.test_start_time.isoformat(),
            "modules": module_serial_numbers,
            "status": "running"
        }

        return session_info

    def log_environmental_data(self, temperature: float, humidity: float,
                               chamber_status: str, alarms: List[str] = None) -> Dict:
        """
        Log environmental chamber data

        Args:
            temperature: Chamber temperature in °C
            humidity: Relative humidity in %
            chamber_status: Current chamber status
            alarms: List of active alarms

        Returns:
            Validation results for current conditions
        """
        if alarms is None:
            alarms = []

        timestamp = datetime.now()
        conditions = EnvironmentalConditions(
            temperature=temperature,
            humidity=humidity,
            timestamp=timestamp,
            chamber_status=chamber_status,
            alarms=alarms
        )

        self.continuous_data.append(conditions)

        # Validate conditions against protocol requirements
        validation = self._validate_conditions(conditions)

        return {
            "timestamp": timestamp.isoformat(),
            "elapsed_hours": self._get_elapsed_hours(),
            "conditions": asdict(conditions),
            "validation": validation
        }

    def _validate_conditions(self, conditions: EnvironmentalConditions) -> Dict:
        """Validate current conditions against protocol requirements"""
        validation = {
            "temperature_in_spec": False,
            "humidity_in_spec": False,
            "overall_valid": False,
            "deviations": []
        }

        if self.protocol_type == "humidity_freeze":
            validation = self._validate_hf_conditions(conditions)
        else:  # damp_heat
            validation = self._validate_dh_conditions(conditions)

        # Check for alarms
        if conditions.alarms:
            validation["deviations"].append(f"Active alarms: {', '.join(conditions.alarms)}")
            validation["overall_valid"] = False

        return validation

    def _validate_hf_conditions(self, conditions: EnvironmentalConditions) -> Dict:
        """Validate humidity-freeze specific conditions"""
        validation = {
            "temperature_in_spec": False,
            "humidity_in_spec": False,
            "overall_valid": False,
            "deviations": []
        }

        if self.current_phase == "humidity":
            target_temp = self.protocol_data['protocol_inputs']['humidity_phase']['temperature']['value']
            target_rh = self.protocol_data['protocol_inputs']['humidity_phase']['relative_humidity']['value']
            temp_tol = 2.0
            rh_tol = 5.0
        elif self.current_phase == "freeze":
            target_temp = self.protocol_data['protocol_inputs']['freeze_phase']['temperature']['value']
            temp_tol = 3.0
            target_rh = None  # No humidity control during freeze
            rh_tol = None
        else:
            # Transition or stabilization phase
            return validation

        # Check temperature
        temp_dev = abs(conditions.temperature - target_temp)
        if temp_dev <= temp_tol:
            validation["temperature_in_spec"] = True
        else:
            validation["deviations"].append(
                f"Temperature deviation: {temp_dev:.1f}°C (tolerance: ±{temp_tol}°C)"
            )

        # Check humidity (only during humidity phase)
        if target_rh is not None:
            rh_dev = abs(conditions.humidity - target_rh)
            if rh_dev <= rh_tol:
                validation["humidity_in_spec"] = True
            else:
                validation["deviations"].append(
                    f"Humidity deviation: {rh_dev:.1f}% (tolerance: ±{rh_tol}%)"
                )
        else:
            validation["humidity_in_spec"] = True  # Not controlled

        validation["overall_valid"] = (
            validation["temperature_in_spec"] and
            validation["humidity_in_spec"]
        )

        return validation

    def _validate_dh_conditions(self, conditions: EnvironmentalConditions) -> Dict:
        """Validate damp heat specific conditions"""
        validation = {
            "temperature_in_spec": False,
            "humidity_in_spec": False,
            "overall_valid": False,
            "deviations": []
        }

        target_temp = self.protocol_data['protocol_inputs']['conditions']['temperature']['value']
        target_rh = self.protocol_data['protocol_inputs']['conditions']['relative_humidity']['value']
        temp_tol = 2.0
        rh_tol = 5.0

        # Check temperature
        temp_dev = abs(conditions.temperature - target_temp)
        if temp_dev <= temp_tol:
            validation["temperature_in_spec"] = True
        else:
            validation["deviations"].append(
                f"Temperature deviation: {temp_dev:.1f}°C (tolerance: ±{temp_tol}°C)"
            )

        # Check humidity
        rh_dev = abs(conditions.humidity - target_rh)
        if rh_dev <= rh_tol:
            validation["humidity_in_spec"] = True
        else:
            validation["deviations"].append(
                f"Humidity deviation: {rh_dev:.1f}% (tolerance: ±{rh_tol}%)"
            )

        validation["overall_valid"] = (
            validation["temperature_in_spec"] and
            validation["humidity_in_spec"]
        )

        return validation

    def transition_phase(self, new_phase: str) -> Dict:
        """
        Transition to a new test phase (humidity-freeze only)

        Args:
            new_phase: Name of the new phase

        Returns:
            Transition validation results
        """
        if self.protocol_type != "humidity_freeze":
            return {"error": "Phase transitions only applicable to humidity-freeze protocol"}

        transition = PhaseTransition(
            from_phase=self.current_phase,
            to_phase=new_phase,
            start_time=datetime.now(),
            end_time=None,
            target_rate=self.protocol_data['protocol_inputs']['transition_requirements']['max_rate']['value'],
            actual_max_rate=0.0,
            is_valid=True,
            validation_notes=""
        )

        self.current_phase = new_phase
        self.phase_history.append(transition)

        return {
            "transition": asdict(transition),
            "current_phase": self.current_phase,
            "cycle": self.current_cycle
        }

    def validate_transition_rate(self, temperature_data: List[Tuple[datetime, float]]) -> Dict:
        """
        Validate temperature transition rate

        Args:
            temperature_data: List of (timestamp, temperature) tuples

        Returns:
            Validation results including max rate and compliance
        """
        if len(temperature_data) < 2:
            return {"error": "Insufficient data for rate calculation"}

        # Calculate rates between consecutive points
        rates = []
        for i in range(1, len(temperature_data)):
            t1, temp1 = temperature_data[i-1]
            t2, temp2 = temperature_data[i]
            dt_minutes = (t2 - t1).total_seconds() / 60.0
            if dt_minutes > 0:
                rate = abs(temp2 - temp1) / dt_minutes
                rates.append(rate)

        if not rates:
            return {"error": "Could not calculate transition rates"}

        max_rate = max(rates)
        avg_rate = np.mean(rates)
        target_rate = self.protocol_data['protocol_inputs']['transition_requirements']['max_rate']['value']

        is_valid = max_rate <= target_rate

        # Update last transition record
        if self.phase_history:
            last_transition = self.phase_history[-1]
            last_transition.actual_max_rate = max_rate
            last_transition.is_valid = is_valid
            last_transition.end_time = datetime.now()
            if not is_valid:
                last_transition.validation_notes = f"Exceeded max rate: {max_rate:.2f}°C/min > {target_rate}°C/min"

        return {
            "max_rate": max_rate,
            "avg_rate": avg_rate,
            "target_rate": target_rate,
            "is_valid": is_valid,
            "compliance": "PASS" if is_valid else "FAIL"
        }

    def increment_cycle(self) -> Dict:
        """Increment cycle counter for humidity-freeze protocol"""
        if self.protocol_type != "humidity_freeze":
            return {"error": "Cycles only applicable to humidity-freeze protocol"}

        self.current_cycle += 1
        max_cycles = self.protocol_data['protocol_inputs']['cycles']['value']

        return {
            "current_cycle": self.current_cycle,
            "max_cycles": max_cycles,
            "progress_percentage": (self.current_cycle / max_cycles) * 100,
            "remaining_cycles": max_cycles - self.current_cycle
        }

    def log_performance_measurement(self, Pmax: float, Voc: float, Isc: float,
                                   FF: float, insulation_resistance: float,
                                   visual_defects: List[str] = None) -> Dict:
        """
        Log module performance measurement

        Args:
            Pmax: Maximum power in W
            Voc: Open circuit voltage in V
            Isc: Short circuit current in A
            FF: Fill factor
            insulation_resistance: Insulation resistance in MΩ
            visual_defects: List of observed visual defects

        Returns:
            Measurement record with degradation analysis
        """
        if visual_defects is None:
            visual_defects = []

        timestamp = datetime.now()
        interval = self._get_elapsed_hours()

        # Calculate power loss percentage
        if self.measurements:
            initial_power = self.measurements[0].Pmax
            power_loss_percentage = ((initial_power - Pmax) / initial_power) * 100
        else:
            initial_power = Pmax
            power_loss_percentage = 0.0

        measurement = PerformanceMeasurement(
            timestamp=timestamp,
            interval=interval,
            Pmax=Pmax,
            Voc=Voc,
            Isc=Isc,
            FF=FF,
            insulation_resistance=insulation_resistance,
            visual_defects=visual_defects,
            power_loss_percentage=power_loss_percentage
        )

        self.measurements.append(measurement)

        # Check against acceptance criteria
        acceptance = self._check_acceptance_criteria(measurement)

        return {
            "measurement": asdict(measurement),
            "acceptance_check": acceptance,
            "measurement_count": len(self.measurements)
        }

    def _check_acceptance_criteria(self, measurement: PerformanceMeasurement) -> Dict:
        """Check measurement against acceptance criteria"""
        acceptance = {
            "power_loss": "UNKNOWN",
            "insulation_resistance": "UNKNOWN",
            "visual": "UNKNOWN",
            "overall": "UNKNOWN",
            "failures": []
        }

        if not self.measurements or len(self.measurements) < 2:
            return acceptance

        # Check power loss
        if self.protocol_type == "damp_heat":
            # Damp heat: ≤5% after 1000h
            if measurement.interval >= 1000:
                if measurement.power_loss_percentage <= 5.0:
                    acceptance["power_loss"] = "PASS"
                else:
                    acceptance["power_loss"] = "FAIL"
                    acceptance["failures"].append(
                        f"Power loss {measurement.power_loss_percentage:.1f}% exceeds 5% limit"
                    )
        else:  # humidity_freeze
            # Humidity-freeze: depends on cycle count
            if self.current_cycle <= 5:
                if measurement.power_loss_percentage <= 2.0:
                    acceptance["power_loss"] = "PASS"
                else:
                    acceptance["power_loss"] = "FAIL"
                    acceptance["failures"].append(
                        f"Power loss {measurement.power_loss_percentage:.1f}% exceeds 2% limit (cycles 0-5)"
                    )
            else:
                if measurement.power_loss_percentage <= 5.0:
                    acceptance["power_loss"] = "PASS"
                else:
                    acceptance["power_loss"] = "FAIL"
                    acceptance["failures"].append(
                        f"Power loss {measurement.power_loss_percentage:.1f}% exceeds 5% limit (cycles 5-10)"
                    )

        # Check insulation resistance
        if measurement.insulation_resistance >= 40.0:
            acceptance["insulation_resistance"] = "PASS"
        else:
            acceptance["insulation_resistance"] = "FAIL"
            acceptance["failures"].append(
                f"Insulation resistance {measurement.insulation_resistance:.1f} MΩ below 40 MΩ limit"
            )

        # Check visual defects
        critical_defects = ["broken_cells", "delamination", "open_circuits", "broken_interconnects"]
        has_critical = any(defect in measurement.visual_defects for defect in critical_defects)
        if has_critical:
            acceptance["visual"] = "FAIL"
            acceptance["failures"].append(f"Critical visual defects: {', '.join(measurement.visual_defects)}")
        else:
            acceptance["visual"] = "PASS"

        # Overall assessment
        all_pass = (
            acceptance["power_loss"] == "PASS" and
            acceptance["insulation_resistance"] == "PASS" and
            acceptance["visual"] == "PASS"
        )
        acceptance["overall"] = "PASS" if all_pass else "FAIL"

        return acceptance

    def log_nonconformance(self, nc_type: str, description: str,
                          duration: float, impact: str,
                          corrective_action: str, disposition: str,
                          approved_by: str) -> Dict:
        """
        Log a nonconformance event

        Args:
            nc_type: Type of nonconformance
            description: Detailed description
            duration: Duration in hours
            impact: Impact assessment
            corrective_action: Action taken
            disposition: Decision on how to proceed
            approved_by: Approver name

        Returns:
            Nonconformance record
        """
        nc_id = f"NC-{self.protocol_data['protocol_metadata']['id']}-{len(self.nonconformances)+1:03d}"

        nc_record = {
            "nc_id": nc_id,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time": self._get_elapsed_hours(),
            "type": nc_type,
            "description": description,
            "duration": duration,
            "impact_assessment": impact,
            "corrective_action": corrective_action,
            "disposition": disposition,
            "approved_by": approved_by
        }

        if self.protocol_type == "humidity_freeze":
            nc_record["cycle_number"] = self.current_cycle

        self.nonconformances.append(nc_record)

        return nc_record

    def get_test_progress(self) -> Dict:
        """Get current test progress and status"""
        elapsed_hours = self._get_elapsed_hours()

        progress = {
            "elapsed_hours": elapsed_hours,
            "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
            "current_phase": self.current_phase,
            "measurements_count": len(self.measurements),
            "nonconformances_count": len(self.nonconformances)
        }

        if self.protocol_type == "humidity_freeze":
            max_cycles = self.protocol_data['protocol_inputs']['cycles']['value']
            progress["current_cycle"] = self.current_cycle
            progress["max_cycles"] = max_cycles
            progress["progress_percentage"] = (self.current_cycle / max_cycles) * 100

            # Estimate remaining time
            hours_per_cycle = (
                self.protocol_data['protocol_inputs']['humidity_phase']['duration']['value'] +
                self.protocol_data['protocol_inputs']['freeze_phase']['duration']['value']
            )
            remaining_cycles = max_cycles - self.current_cycle
            progress["estimated_remaining_hours"] = remaining_cycles * hours_per_cycle
        else:  # damp_heat
            total_duration = self.protocol_data['protocol_inputs']['test_duration']['value']
            progress["total_duration_hours"] = total_duration
            progress["progress_percentage"] = (elapsed_hours / total_duration) * 100
            progress["estimated_remaining_hours"] = total_duration - elapsed_hours

        return progress

    def calculate_insulation_resistance_trend(self) -> Dict:
        """Calculate insulation resistance trend over time"""
        if len(self.measurements) < 2:
            return {"error": "Insufficient measurements for trend analysis"}

        times = [m.interval for m in self.measurements]
        ir_values = [m.insulation_resistance for m in self.measurements]

        # Linear regression
        coeffs = np.polyfit(times, ir_values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # Calculate R-squared
        mean_ir = np.mean(ir_values)
        ss_tot = sum((y - mean_ir) ** 2 for y in ir_values)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(times, ir_values))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Predict when IR might fall below 40 MΩ threshold
        threshold = 40.0
        if slope < 0:  # Decreasing trend
            hours_to_threshold = (threshold - intercept) / slope
        else:
            hours_to_threshold = None

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "trend": "decreasing" if slope < 0 else "stable" if abs(slope) < 0.01 else "increasing",
            "current_value": ir_values[-1],
            "initial_value": ir_values[0],
            "change": ir_values[-1] - ir_values[0],
            "hours_to_threshold": hours_to_threshold,
            "measurement_count": len(self.measurements)
        }

    def _get_elapsed_hours(self) -> float:
        """Get elapsed time since test start in hours"""
        if self.test_start_time is None:
            return 0.0
        return (datetime.now() - self.test_start_time).total_seconds() / 3600.0

    def export_test_data(self) -> Dict:
        """Export complete test data for reporting"""
        return {
            "protocol_metadata": self.protocol_data['protocol_metadata'],
            "protocol_inputs": self.protocol_data['protocol_inputs'],
            "test_session": {
                "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                "elapsed_hours": self._get_elapsed_hours(),
                "current_phase": self.current_phase,
                "current_cycle": self.current_cycle if self.protocol_type == "humidity_freeze" else None
            },
            "measurements": [asdict(m) for m in self.measurements],
            "continuous_data_count": len(self.continuous_data),
            "phase_transitions": [asdict(t) for t in self.phase_history],
            "nonconformances": self.nonconformances,
            "progress": self.get_test_progress()
        }
