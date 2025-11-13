"""PID-001 Protocol Implementation with Leakage Tracking."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import uuid

from src.models.protocol import (
    TestExecution,
    Measurement,
    QCCheck,
    LeakageEvent,
    TestExecutionStatus,
    QCStatus,
)


class LeakageTracker:
    """Track and analyze leakage current data."""

    def __init__(self, threshold_warning: float = 5.0, threshold_critical: float = 10.0):
        """
        Initialize leakage tracker.

        Args:
            threshold_warning: Warning threshold in mA
            threshold_critical: Critical threshold in mA
        """
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.measurements: List[Dict[str, Any]] = []

    def add_measurement(self, leakage_current: float, timestamp: datetime, elapsed_time: float) -> Optional[Dict]:
        """
        Add measurement and check for anomalies.

        Args:
            leakage_current: Leakage current in mA
            timestamp: Measurement timestamp
            elapsed_time: Elapsed time in hours

        Returns:
            Leakage event if anomaly detected, None otherwise
        """
        measurement = {
            "leakage_current": leakage_current,
            "timestamp": timestamp,
            "elapsed_time": elapsed_time,
        }
        self.measurements.append(measurement)

        # Detect anomalies
        return self._detect_anomaly(measurement)

    def _detect_anomaly(self, measurement: Dict[str, Any]) -> Optional[Dict]:
        """Detect leakage current anomalies."""
        current = measurement["leakage_current"]

        # Critical threshold exceeded
        if current > self.threshold_critical:
            return {
                "event_type": "critical_threshold",
                "severity": "critical",
                "description": f"Leakage current {current:.2f}mA exceeds critical threshold {self.threshold_critical}mA",
                "leakage_current": current,
                "threshold_exceeded": self.threshold_critical,
            }

        # Warning threshold exceeded
        if current > self.threshold_warning:
            return {
                "event_type": "warning_threshold",
                "severity": "warning",
                "description": f"Leakage current {current:.2f}mA exceeds warning threshold {self.threshold_warning}mA",
                "leakage_current": current,
                "threshold_exceeded": self.threshold_warning,
            }

        # Rapid increase detection (if we have enough history)
        if len(self.measurements) >= 5:
            recent = [m["leakage_current"] for m in self.measurements[-5:]]
            if current > recent[0] * 2:  # More than 100% increase
                return {
                    "event_type": "rapid_increase",
                    "severity": "warning",
                    "description": f"Rapid increase in leakage current: {recent[0]:.2f}mA → {current:.2f}mA",
                    "leakage_current": current,
                }

        return None

    def get_statistics(self) -> Dict[str, float]:
        """Calculate leakage current statistics."""
        if not self.measurements:
            return {}

        currents = [m["leakage_current"] for m in self.measurements]
        return {
            "average": sum(currents) / len(currents),
            "max": max(currents),
            "min": min(currents),
            "latest": currents[-1],
            "total_measurements": len(currents),
        }


class PID001Protocol:
    """PID-001 Protocol Implementation for IEC 62804 PID Shunting Test."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize PID-001 protocol.

        Args:
            schema_path: Path to schema.json file
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        self.metadata = self.schema["metadata"]
        self.validation_rules = self.schema["validation_rules"]

    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate test parameters against schema.

        Args:
            parameters: Test parameters dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_fields = self.schema["test_parameters"]["required"]

        # Check required fields
        for field in required_fields:
            if field not in parameters:
                errors.append(f"Missing required field: {field}")

        # Validate ranges
        if "test_voltage" in parameters:
            voltage = parameters["test_voltage"]
            if not (-1500 <= voltage <= 1500):
                errors.append(f"Test voltage {voltage}V out of range [-1500, 1500]")

        if "test_duration" in parameters:
            duration = parameters["test_duration"]
            if not (0 <= duration <= 500):
                errors.append(f"Test duration {duration}h out of range [0, 500]")

        if "temperature" in parameters:
            temp = parameters["temperature"]
            if not (0 <= temp <= 100):
                errors.append(f"Temperature {temp}°C out of range [0, 100]")

        if "relative_humidity" in parameters:
            humidity = parameters["relative_humidity"]
            if not (0 <= humidity <= 100):
                errors.append(f"Relative humidity {humidity}% out of range [0, 100]")

        return len(errors) == 0, errors

    def create_test_execution(
        self, protocol_id: str, parameters: Dict[str, Any]
    ) -> TestExecution:
        """
        Create a new test execution record.

        Args:
            protocol_id: Protocol database ID
            parameters: Test parameters

        Returns:
            TestExecution instance
        """
        test_execution = TestExecution(
            id=str(uuid.uuid4()),
            protocol_id=protocol_id,
            test_name=parameters.get("test_name"),
            module_id=parameters.get("module_id"),
            input_parameters=parameters,
            status=TestExecutionStatus.PENDING,
            operator=parameters.get("operator"),
            notes=parameters.get("notes"),
        )
        return test_execution

    def simulate_measurement(
        self, elapsed_time: float, test_voltage: float, base_leakage: float = 1.0
    ) -> Dict[str, Any]:
        """
        Simulate a measurement (for testing/demo purposes).

        Args:
            elapsed_time: Elapsed time in hours
            test_voltage: Applied voltage
            base_leakage: Base leakage current

        Returns:
            Measurement data dictionary
        """
        import random

        # Simulate leakage current increase over time with some noise
        leakage_current = base_leakage + (elapsed_time * 0.05) + random.uniform(-0.2, 0.2)
        leakage_current = max(0, leakage_current)  # No negative current

        # Simulate power degradation
        power_degradation = (elapsed_time / 100) * 2.5 + random.uniform(-0.1, 0.1)
        power_degradation = max(0, power_degradation)

        return {
            "timestamp": datetime.utcnow(),
            "elapsed_time": elapsed_time,
            "leakage_current": leakage_current,
            "voltage": test_voltage,
            "temperature": 85.0 + random.uniform(-1, 1),
            "humidity": 85.0 + random.uniform(-2, 2),
            "power_degradation": power_degradation,
        }

    def process_measurement(
        self,
        test_execution: TestExecution,
        measurement_data: Dict[str, Any],
        leakage_tracker: LeakageTracker,
    ) -> Tuple[Measurement, Optional[LeakageEvent]]:
        """
        Process a single measurement.

        Args:
            test_execution: Test execution instance
            measurement_data: Measurement data
            leakage_tracker: Leakage tracker instance

        Returns:
            Tuple of (Measurement, LeakageEvent if detected)
        """
        # Create measurement record
        measurement = Measurement(
            test_execution_id=test_execution.id,
            timestamp=measurement_data["timestamp"],
            elapsed_time=measurement_data["elapsed_time"],
            leakage_current=measurement_data["leakage_current"],
            voltage=measurement_data["voltage"],
            temperature=measurement_data.get("temperature"),
            humidity=measurement_data.get("humidity"),
            power_degradation=measurement_data.get("power_degradation"),
        )

        # Track leakage and detect anomalies
        anomaly = leakage_tracker.add_measurement(
            measurement_data["leakage_current"],
            measurement_data["timestamp"],
            measurement_data["elapsed_time"],
        )

        leakage_event = None
        if anomaly:
            leakage_event = LeakageEvent(
                test_execution_id=test_execution.id,
                measurement_id=measurement.id,
                event_type=anomaly["event_type"],
                severity=anomaly["severity"],
                timestamp=measurement_data["timestamp"],
                leakage_current=anomaly["leakage_current"],
                threshold_exceeded=anomaly.get("threshold_exceeded"),
                description=anomaly["description"],
            )

        return measurement, leakage_event

    def perform_qc_checks(
        self, measurements: List[Measurement], parameters: Dict[str, Any]
    ) -> Tuple[QCStatus, List[QCCheck]]:
        """
        Perform quality control checks on measurements.

        Args:
            measurements: List of measurement records
            parameters: Test parameters

        Returns:
            Tuple of (overall_qc_status, list_of_qc_checks)
        """
        qc_checks = []

        if not measurements:
            return QCStatus.FAIL, qc_checks

        # Extract leakage currents
        leakage_currents = [m.leakage_current for m in measurements]
        avg_leakage = sum(leakage_currents) / len(leakage_currents)
        max_leakage = max(leakage_currents)

        # Check 1: Average leakage current
        leakage_limits = self.validation_rules["leakage_current_limits"]
        if avg_leakage > leakage_limits["critical_threshold"]:
            status = QCStatus.FAIL
        elif avg_leakage > leakage_limits["warning_threshold"]:
            status = QCStatus.WARNING
        else:
            status = QCStatus.PASS

        qc_checks.append(
            QCCheck(
                check_name="Average Leakage Current",
                check_type="leakage_current",
                status=status,
                measured_value=avg_leakage,
                threshold_value=leakage_limits["critical_threshold"],
                warning_threshold=leakage_limits["warning_threshold"],
                message=f"Average leakage current: {avg_leakage:.2f}mA",
                passed=1 if status == QCStatus.PASS else 0,
            )
        )

        # Check 2: Maximum leakage current
        if max_leakage > leakage_limits["critical_threshold"]:
            status = QCStatus.FAIL
        elif max_leakage > leakage_limits["warning_threshold"]:
            status = QCStatus.WARNING
        else:
            status = QCStatus.PASS

        qc_checks.append(
            QCCheck(
                check_name="Maximum Leakage Current",
                check_type="leakage_current",
                status=status,
                measured_value=max_leakage,
                threshold_value=leakage_limits["critical_threshold"],
                warning_threshold=leakage_limits["warning_threshold"],
                message=f"Maximum leakage current: {max_leakage:.2f}mA",
                passed=1 if status == QCStatus.PASS else 0,
            )
        )

        # Check 3: Power degradation (if available)
        power_degradations = [
            m.power_degradation for m in measurements if m.power_degradation is not None
        ]
        if power_degradations:
            final_degradation = power_degradations[-1]
            degradation_limits = self.validation_rules["power_degradation_limits"]

            if final_degradation > degradation_limits["critical_threshold"]:
                status = QCStatus.FAIL
            elif final_degradation > degradation_limits["warning_threshold"]:
                status = QCStatus.WARNING
            else:
                status = QCStatus.PASS

            qc_checks.append(
                QCCheck(
                    check_name="Power Degradation",
                    check_type="power_degradation",
                    status=status,
                    measured_value=final_degradation,
                    threshold_value=degradation_limits["critical_threshold"],
                    warning_threshold=degradation_limits["warning_threshold"],
                    message=f"Final power degradation: {final_degradation:.2f}%",
                    passed=1 if status == QCStatus.PASS else 0,
                )
            )

        # Determine overall QC status
        overall_status = QCStatus.PASS
        for check in qc_checks:
            if check.status == QCStatus.FAIL:
                overall_status = QCStatus.FAIL
                break
            elif check.status == QCStatus.WARNING:
                overall_status = QCStatus.WARNING

        return overall_status, qc_checks

    def generate_results_summary(
        self,
        measurements: List[Measurement],
        qc_checks: List[QCCheck],
        qc_status: QCStatus,
    ) -> Dict[str, Any]:
        """
        Generate results summary.

        Args:
            measurements: List of measurements
            qc_checks: List of QC checks
            qc_status: Overall QC status

        Returns:
            Results summary dictionary
        """
        if not measurements:
            return {}

        leakage_currents = [m.leakage_current for m in measurements]
        power_degradations = [
            m.power_degradation for m in measurements if m.power_degradation is not None
        ]

        summary = {
            "total_measurements": len(measurements),
            "average_leakage_current": sum(leakage_currents) / len(leakage_currents),
            "max_leakage_current": max(leakage_currents),
            "min_leakage_current": min(leakage_currents),
            "qc_status": qc_status.value,
            "qc_details": [
                {
                    "check": check.check_name,
                    "status": check.status.value,
                    "message": check.message,
                    "value": check.measured_value,
                    "threshold": check.threshold_value,
                }
                for check in qc_checks
            ],
        }

        if power_degradations:
            summary["final_power_degradation"] = power_degradations[-1]

        # IEC 62804 compliance check
        iec_compliant = qc_status != QCStatus.FAIL
        summary["compliance"] = {
            "iec_62804_compliant": iec_compliant,
            "compliance_notes": "Test meets IEC 62804 requirements"
            if iec_compliant
            else "Test failed IEC 62804 requirements",
        }

        return summary

    def get_chart_data(self, measurements: List[Measurement]) -> Dict[str, Any]:
        """
        Prepare data for charting.

        Args:
            measurements: List of measurements

        Returns:
            Chart data dictionary
        """
        if not measurements:
            return {}

        return {
            "elapsed_time": [m.elapsed_time for m in measurements],
            "leakage_current": [m.leakage_current for m in measurements],
            "power_degradation": [
                m.power_degradation for m in measurements if m.power_degradation is not None
            ],
            "temperature": [m.temperature for m in measurements if m.temperature is not None],
            "humidity": [m.humidity for m in measurements if m.humidity is not None],
        }
