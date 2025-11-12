"""
Safety Validator for Mechanical Load and PID Testing

This module provides safety validation and monitoring for high-voltage PID testing
and mechanical load testing, including voltage safety checks, load limits validation,
and emergency shutdown protocols.

Author: PV Testing Lab
Version: 1.0
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety status levels"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class TestType(Enum):
    """Types of tests requiring safety validation"""
    MECHANICAL_LOAD = "mechanical_load"
    PID_TESTING = "pid_testing"


@dataclass
class SafetyAlert:
    """Safety alert data structure"""
    level: SafetyLevel
    timestamp: datetime
    message: str
    parameter: str
    value: float
    threshold: float
    action_required: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/reporting"""
        return {
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "parameter": self.parameter,
            "value": self.value,
            "threshold": self.threshold,
            "action_required": self.action_required
        }


class PIDSafetyValidator:
    """Safety validator for high-voltage PID testing"""

    # Safety thresholds
    MAX_SAFE_VOLTAGE = 1500  # V
    MAX_WARNING_CURRENT = 10  # mA
    MAX_CRITICAL_CURRENT = 50  # mA
    MAX_EMERGENCY_CURRENT = 100  # mA
    MIN_INSULATION_RESISTANCE = 40  # MΩ
    MAX_SAFE_TEMPERATURE = 85  # °C
    MIN_SAFE_TEMPERATURE = 40  # °C

    def __init__(self, enable_auto_shutdown: bool = True):
        """
        Initialize PID safety validator

        Args:
            enable_auto_shutdown: Enable automatic emergency shutdown
        """
        self.enable_auto_shutdown = enable_auto_shutdown
        self.safety_alerts: List[SafetyAlert] = []
        self.emergency_shutdown_triggered = False
        self.test_running = False

    def pre_test_safety_check(self, module_data: Dict) -> Tuple[bool, List[str]]:
        """
        Perform pre-test safety checks before starting PID test

        Args:
            module_data: Dictionary with module specifications and measurements

        Returns:
            Tuple of (passed, list of issues)
        """
        issues = []

        # Check insulation resistance
        insulation_resistance = module_data.get("insulation_resistance_mohm", 0)
        if insulation_resistance < self.MIN_INSULATION_RESISTANCE:
            issues.append(
                f"FAIL: Insulation resistance {insulation_resistance}MΩ is below "
                f"minimum {self.MIN_INSULATION_RESISTANCE}MΩ"
            )

        # Check for pre-existing damage
        if module_data.get("visual_defects", False):
            issues.append("WARNING: Visual defects detected - document before proceeding")

        # Verify safety equipment
        safety_equipment = module_data.get("safety_equipment", {})
        required_equipment = [
            "high_voltage_warning_signs",
            "emergency_shutdown_accessible",
            "ground_fault_protection",
            "insulated_barriers",
            "ppe_available"
        ]

        for equipment in required_equipment:
            if not safety_equipment.get(equipment, False):
                issues.append(f"FAIL: {equipment.replace('_', ' ').title()} not confirmed")

        # Check personnel qualifications
        if not module_data.get("qualified_personnel", False):
            issues.append("FAIL: High voltage qualified personnel not confirmed")

        # Check chamber condition
        chamber_checks = module_data.get("chamber_checks", {})
        if not chamber_checks.get("door_interlock_functional", False):
            issues.append("FAIL: Chamber door interlock not functional")

        passed = len([i for i in issues if i.startswith("FAIL")]) == 0

        return passed, issues

    def validate_voltage_settings(self, voltage: float, module_voc: float) -> Tuple[bool, str]:
        """
        Validate voltage settings are safe for the module

        Args:
            voltage: Applied test voltage in V (absolute value)
            module_voc: Module open circuit voltage in V

        Returns:
            Tuple of (is_safe, message)
        """
        abs_voltage = abs(voltage)

        # Check against absolute maximum
        if abs_voltage > self.MAX_SAFE_VOLTAGE:
            return False, f"UNSAFE: Test voltage {abs_voltage}V exceeds maximum safe voltage {self.MAX_SAFE_VOLTAGE}V"

        # Typical PID test uses system voltage of -600V to -1500V
        if abs_voltage < 500:
            return False, f"Invalid: Test voltage {abs_voltage}V is too low for PID testing (typical: 600-1500V)"

        # Warning if voltage is very high relative to module Voc
        if abs_voltage > module_voc * 30:
            return True, f"WARNING: Test voltage {abs_voltage}V is >30x module Voc ({module_voc}V) - verify this is intentional"

        return True, f"Voltage {abs_voltage}V is within safe limits"

    def check_real_time_safety(self, voltage: float, leakage_current: float,
                               temperature: float, humidity: float) -> SafetyAlert:
        """
        Check real-time safety parameters during test

        Args:
            voltage: Current voltage in V
            leakage_current: Leakage current in mA
            temperature: Chamber temperature in °C
            humidity: Relative humidity in %RH

        Returns:
            SafetyAlert object with current safety status
        """
        # Check leakage current (most critical)
        if leakage_current >= self.MAX_EMERGENCY_CURRENT:
            alert = SafetyAlert(
                level=SafetyLevel.EMERGENCY,
                timestamp=datetime.now(),
                message="EMERGENCY: Excessive leakage current - IMMEDIATE SHUTDOWN REQUIRED",
                parameter="leakage_current",
                value=leakage_current,
                threshold=self.MAX_EMERGENCY_CURRENT,
                action_required="DISCONNECT VOLTAGE IMMEDIATELY - Potential module breakdown"
            )
            if self.enable_auto_shutdown:
                self.trigger_emergency_shutdown("Excessive leakage current")
            self.safety_alerts.append(alert)
            return alert

        elif leakage_current >= self.MAX_CRITICAL_CURRENT:
            alert = SafetyAlert(
                level=SafetyLevel.CRITICAL,
                timestamp=datetime.now(),
                message=f"CRITICAL: Leakage current {leakage_current}mA exceeds critical threshold",
                parameter="leakage_current",
                value=leakage_current,
                threshold=self.MAX_CRITICAL_CURRENT,
                action_required="Reduce voltage immediately and investigate"
            )
            self.safety_alerts.append(alert)
            return alert

        elif leakage_current >= self.MAX_WARNING_CURRENT:
            alert = SafetyAlert(
                level=SafetyLevel.WARNING,
                timestamp=datetime.now(),
                message=f"WARNING: Elevated leakage current {leakage_current}mA",
                parameter="leakage_current",
                value=leakage_current,
                threshold=self.MAX_WARNING_CURRENT,
                action_required="Monitor closely, consider reducing voltage"
            )
            self.safety_alerts.append(alert)
            return alert

        # Check temperature
        if temperature > self.MAX_SAFE_TEMPERATURE:
            alert = SafetyAlert(
                level=SafetyLevel.CRITICAL,
                timestamp=datetime.now(),
                message=f"CRITICAL: Temperature {temperature}°C exceeds maximum safe limit",
                parameter="temperature",
                value=temperature,
                threshold=self.MAX_SAFE_TEMPERATURE,
                action_required="Stop test and allow module to cool"
            )
            self.safety_alerts.append(alert)
            return alert

        elif temperature < self.MIN_SAFE_TEMPERATURE:
            alert = SafetyAlert(
                level=SafetyLevel.WARNING,
                timestamp=datetime.now(),
                message=f"WARNING: Temperature {temperature}°C below minimum",
                parameter="temperature",
                value=temperature,
                threshold=self.MIN_SAFE_TEMPERATURE,
                action_required="Increase chamber temperature"
            )
            self.safety_alerts.append(alert)
            return alert

        # Check voltage stability
        abs_voltage = abs(voltage)
        expected_voltage = 1000  # Assuming -1000V standard
        voltage_deviation = abs(abs_voltage - expected_voltage)

        if voltage_deviation > 100:
            alert = SafetyAlert(
                level=SafetyLevel.WARNING,
                timestamp=datetime.now(),
                message=f"WARNING: Voltage deviation {voltage_deviation}V from setpoint",
                parameter="voltage",
                value=abs_voltage,
                threshold=expected_voltage,
                action_required="Check power supply and connections"
            )
            self.safety_alerts.append(alert)
            return alert

        # All checks passed
        alert = SafetyAlert(
            level=SafetyLevel.SAFE,
            timestamp=datetime.now(),
            message="All parameters within safe limits",
            parameter="all",
            value=0,
            threshold=0,
            action_required="Continue monitoring"
        )

        return alert

    def trigger_emergency_shutdown(self, reason: str) -> None:
        """
        Trigger emergency shutdown protocol

        Args:
            reason: Reason for emergency shutdown
        """
        self.emergency_shutdown_triggered = True
        self.test_running = False

        logger.critical(f"EMERGENCY SHUTDOWN TRIGGERED: {reason}")
        logger.critical("=" * 60)
        logger.critical("EMERGENCY SHUTDOWN PROTOCOL:")
        logger.critical("1. DISCONNECT HIGH VOLTAGE IMMEDIATELY")
        logger.critical("2. DO NOT TOUCH MODULE - Wait 5 minutes for discharge")
        logger.critical("3. Verify voltage is 0V with voltmeter")
        logger.critical("4. Document module condition with photos")
        logger.critical("5. Notify safety officer and test supervisor")
        logger.critical("6. Do not restart test until investigation complete")
        logger.critical("=" * 60)

    def get_safety_summary(self) -> Dict:
        """
        Get summary of safety status and alerts

        Returns:
            Dictionary with safety summary
        """
        if not self.safety_alerts:
            return {
                "status": "no_alerts",
                "total_alerts": 0,
                "emergency_shutdown": False
            }

        alert_counts = {
            SafetyLevel.SAFE: 0,
            SafetyLevel.WARNING: 0,
            SafetyLevel.CRITICAL: 0,
            SafetyLevel.EMERGENCY: 0
        }

        for alert in self.safety_alerts:
            alert_counts[alert.level] += 1

        recent_alerts = [a.to_dict() for a in self.safety_alerts[-10:]]

        return {
            "status": "alerts_present",
            "total_alerts": len(self.safety_alerts),
            "warnings": alert_counts[SafetyLevel.WARNING],
            "critical": alert_counts[SafetyLevel.CRITICAL],
            "emergency": alert_counts[SafetyLevel.EMERGENCY],
            "emergency_shutdown": self.emergency_shutdown_triggered,
            "recent_alerts": recent_alerts
        }


class MechanicalLoadSafetyValidator:
    """Safety validator for mechanical load testing"""

    # Safety thresholds
    MAX_SAFE_PRESSURE = 5000  # Pa
    MAX_DEFLECTION_WARNING = 20  # mm
    MAX_DEFLECTION_CRITICAL = 30  # mm
    MAX_LOAD_RATE = 200  # Pa/s

    def __init__(self):
        """Initialize mechanical load safety validator"""
        self.safety_alerts: List[SafetyAlert] = []
        self.test_running = False

    def validate_load_parameters(self, load_value: float, load_rate: float,
                                 module_dimensions: Dict) -> Tuple[bool, List[str]]:
        """
        Validate load test parameters are safe

        Args:
            load_value: Applied load in Pa
            load_rate: Rate of load application in Pa/s
            module_dimensions: Dictionary with module dimensions (length, width in mm)

        Returns:
            Tuple of (is_safe, list of issues)
        """
        issues = []

        # Check load magnitude
        abs_load = abs(load_value)
        if abs_load > self.MAX_SAFE_PRESSURE:
            issues.append(
                f"UNSAFE: Load {abs_load}Pa exceeds maximum safe pressure "
                f"{self.MAX_SAFE_PRESSURE}Pa"
            )

        # Standard IEC test is ±2400Pa, warn if exceeding
        if abs_load > 2400:
            issues.append(
                f"WARNING: Load {abs_load}Pa exceeds standard test pressure of "
                f"2400Pa - verify this is intentional"
            )

        # Check load rate
        if load_rate > self.MAX_LOAD_RATE:
            issues.append(
                f"WARNING: Load rate {load_rate}Pa/s exceeds recommended maximum "
                f"{self.MAX_LOAD_RATE}Pa/s - risk of impact damage"
            )

        # Check module dimensions are provided
        if not module_dimensions.get("length") or not module_dimensions.get("width"):
            issues.append("WARNING: Module dimensions not provided - cannot validate deflection limits")

        passed = len([i for i in issues if i.startswith("UNSAFE")]) == 0

        return passed, issues

    def check_deflection_safety(self, deflection: float, location: str,
                               module_span: float) -> SafetyAlert:
        """
        Check if deflection is within safe limits

        Args:
            deflection: Measured deflection in mm
            location: Measurement location
            module_span: Relevant module span dimension in mm

        Returns:
            SafetyAlert object
        """
        abs_deflection = abs(deflection)

        # Check against absolute limits
        if abs_deflection >= self.MAX_DEFLECTION_CRITICAL:
            alert = SafetyAlert(
                level=SafetyLevel.CRITICAL,
                timestamp=datetime.now(),
                message=f"CRITICAL: Excessive deflection {abs_deflection}mm at {location}",
                parameter="deflection",
                value=abs_deflection,
                threshold=self.MAX_DEFLECTION_CRITICAL,
                action_required="STOP TEST IMMEDIATELY - Risk of module breakage"
            )
            self.safety_alerts.append(alert)
            return alert

        elif abs_deflection >= self.MAX_DEFLECTION_WARNING:
            alert = SafetyAlert(
                level=SafetyLevel.WARNING,
                timestamp=datetime.now(),
                message=f"WARNING: High deflection {abs_deflection}mm at {location}",
                parameter="deflection",
                value=abs_deflection,
                threshold=self.MAX_DEFLECTION_WARNING,
                action_required="Monitor closely, consider reducing load"
            )
            self.safety_alerts.append(alert)
            return alert

        # Check as percentage of span
        if module_span > 0:
            deflection_pct = (abs_deflection / module_span) * 100
            if deflection_pct > 1.5:  # >1.5% of span
                alert = SafetyAlert(
                    level=SafetyLevel.WARNING,
                    timestamp=datetime.now(),
                    message=f"WARNING: Deflection is {deflection_pct:.2f}% of span at {location}",
                    parameter="deflection_percentage",
                    value=deflection_pct,
                    threshold=1.5,
                    action_required="Monitor for permanent deformation"
                )
                self.safety_alerts.append(alert)
                return alert

        # Safe
        alert = SafetyAlert(
            level=SafetyLevel.SAFE,
            timestamp=datetime.now(),
            message=f"Deflection {abs_deflection}mm at {location} is within safe limits",
            parameter="deflection",
            value=abs_deflection,
            threshold=self.MAX_DEFLECTION_WARNING,
            action_required="Continue test"
        )

        return alert

    def validate_equipment_safety(self, equipment_status: Dict) -> Tuple[bool, List[str]]:
        """
        Validate load frame equipment safety

        Args:
            equipment_status: Dictionary with equipment status checks

        Returns:
            Tuple of (passed, list of issues)
        """
        issues = []

        required_checks = {
            "frame_structural_integrity": "Load frame structural integrity verified",
            "pressure_sensors_calibrated": "Pressure sensors calibration current",
            "deflection_sensors_functional": "Deflection sensors functional",
            "emergency_release_functional": "Emergency pressure release functional",
            "module_properly_mounted": "Module properly secured in fixture",
            "safety_barriers_in_place": "Safety barriers around test area"
        }

        for check, description in required_checks.items():
            if not equipment_status.get(check, False):
                issues.append(f"FAIL: {description} - NOT confirmed")

        # Check for overdue calibration
        if equipment_status.get("days_since_calibration", 0) > 365:
            issues.append(
                "WARNING: Equipment calibration is overdue (>365 days)"
            )

        passed = len([i for i in issues if i.startswith("FAIL")]) == 0

        return passed, issues

    def check_cyclic_load_safety(self, cycle_number: int, max_cycles: int,
                                 cumulative_damage_indicator: Optional[float] = None) -> SafetyAlert:
        """
        Check safety during cyclic loading

        Args:
            cycle_number: Current cycle number
            max_cycles: Total planned cycles
            cumulative_damage_indicator: Optional cumulative damage metric

        Returns:
            SafetyAlert object
        """
        # Warn when approaching high cycle counts
        if max_cycles >= 1000 and cycle_number % 100 == 0:
            alert = SafetyAlert(
                level=SafetyLevel.WARNING,
                timestamp=datetime.now(),
                message=f"Cyclic load checkpoint: {cycle_number}/{max_cycles} cycles completed",
                parameter="cycle_count",
                value=cycle_number,
                threshold=max_cycles,
                action_required="Perform interim visual inspection and electrical measurement"
            )
            self.safety_alerts.append(alert)
            return alert

        # Check cumulative damage if provided
        if cumulative_damage_indicator is not None:
            if cumulative_damage_indicator > 0.8:  # 80% of failure threshold
                alert = SafetyAlert(
                    level=SafetyLevel.CRITICAL,
                    timestamp=datetime.now(),
                    message=f"CRITICAL: Cumulative damage indicator at {cumulative_damage_indicator:.1%}",
                    parameter="cumulative_damage",
                    value=cumulative_damage_indicator,
                    threshold=0.8,
                    action_required="Consider stopping test - approaching failure threshold"
                )
                self.safety_alerts.append(alert)
                return alert

        # Normal operation
        alert = SafetyAlert(
            level=SafetyLevel.SAFE,
            timestamp=datetime.now(),
            message=f"Cycle {cycle_number}/{max_cycles} completed successfully",
            parameter="cycle_count",
            value=cycle_number,
            threshold=max_cycles,
            action_required="Continue test"
        )

        return alert


def generate_safety_checklist(test_type: TestType) -> Dict:
    """
    Generate pre-test safety checklist

    Args:
        test_type: Type of test to generate checklist for

    Returns:
        Dictionary with safety checklist items
    """
    if test_type == TestType.PID_TESTING:
        return {
            "test_type": "PID Testing (High Voltage)",
            "checklist": [
                {"item": "HIGH VOLTAGE warning signs posted", "critical": True},
                {"item": "Access restricted to qualified personnel only", "critical": True},
                {"item": "Lockout/tagout procedures reviewed", "critical": True},
                {"item": "Emergency shutdown accessible and tested", "critical": True},
                {"item": "Ground fault protection verified", "critical": True},
                {"item": "Module insulation resistance >40 MΩ", "critical": True},
                {"item": "Chamber door interlock functional", "critical": True},
                {"item": "PPE available (insulated gloves, safety glasses)", "critical": True},
                {"item": "Second person available for voltage work", "critical": True},
                {"item": "Voltage supply calibration current", "critical": False},
                {"item": "Data logging system functional", "critical": False},
                {"item": "Fire extinguisher accessible", "critical": True},
                {"item": "First aid kit available", "critical": True},
                {"item": "Emergency contact numbers posted", "critical": True}
            ]
        }

    elif test_type == TestType.MECHANICAL_LOAD:
        return {
            "test_type": "Mechanical Load Testing",
            "checklist": [
                {"item": "Load frame structural integrity verified", "critical": True},
                {"item": "Module properly secured in fixture", "critical": True},
                {"item": "Pressure sensors calibrated", "critical": True},
                {"item": "Deflection sensors functional and zeroed", "critical": True},
                {"item": "Emergency pressure release functional", "critical": True},
                {"item": "Safety barriers around test area", "critical": True},
                {"item": "Load application rate programmed correctly", "critical": False},
                {"item": "Data acquisition system operational", "critical": False},
                {"item": "Module baseline measurements recorded", "critical": False},
                {"item": "Visual inspection documented", "critical": False},
                {"item": "Test procedure reviewed by operator", "critical": False},
                {"item": "Maximum load limit verified", "critical": True}
            ]
        }


if __name__ == "__main__":
    print("Safety Validator for PV Testing")
    print("=" * 60)

    # Example: PID Safety Validation
    print("\n1. PID Testing Safety Validation:")
    pid_validator = PIDSafetyValidator(enable_auto_shutdown=True)

    # Pre-test check
    module_data = {
        "insulation_resistance_mohm": 45,
        "visual_defects": False,
        "qualified_personnel": True,
        "safety_equipment": {
            "high_voltage_warning_signs": True,
            "emergency_shutdown_accessible": True,
            "ground_fault_protection": True,
            "insulated_barriers": True,
            "ppe_available": True
        },
        "chamber_checks": {
            "door_interlock_functional": True
        }
    }

    passed, issues = pid_validator.pre_test_safety_check(module_data)
    print(f"Pre-test safety check: {'PASSED' if passed else 'FAILED'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")

    # Validate voltage
    is_safe, msg = pid_validator.validate_voltage_settings(-1000, 40.0)
    print(f"Voltage validation: {msg}")

    # Real-time safety check
    alert = pid_validator.check_real_time_safety(-1000, 3.5, 60.0, 85.0)
    print(f"Real-time safety: {alert.level.value} - {alert.message}")

    # Simulate high current
    alert = pid_validator.check_real_time_safety(-1000, 55.0, 60.0, 85.0)
    print(f"High current alert: {alert.level.value} - {alert.message}")

    # Example: Mechanical Load Safety Validation
    print("\n2. Mechanical Load Testing Safety Validation:")
    ml_validator = MechanicalLoadSafetyValidator()

    # Validate load parameters
    passed, issues = ml_validator.validate_load_parameters(
        2400, 100, {"length": 1650, "width": 992}
    )
    print(f"Load parameters: {'SAFE' if passed else 'UNSAFE'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")

    # Check deflection
    alert = ml_validator.check_deflection_safety(8.5, "center", 1650)
    print(f"Deflection check: {alert.level.value} - {alert.message}")

    # Generate safety checklist
    print("\n3. Safety Checklists:")
    for test_type in [TestType.PID_TESTING, TestType.MECHANICAL_LOAD]:
        checklist = generate_safety_checklist(test_type)
        print(f"\n{checklist['test_type']}:")
        critical_items = [item for item in checklist['checklist'] if item['critical']]
        print(f"  Total items: {len(checklist['checklist'])}")
        print(f"  Critical items: {len(critical_items)}")
