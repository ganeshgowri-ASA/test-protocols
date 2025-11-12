"""
Protocol execution monitoring system.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from loguru import logger
from .alerts import AlertManager
from .metrics import MetricsCollector


class ProtocolMonitor:
    """Monitors protocol execution and data quality in real-time."""

    def __init__(self):
        """Initialize protocol monitor."""
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector()
        self.validation_rules = []
        self.active_protocols = {}
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default monitoring rules."""
        # Temperature anomaly detection
        self.add_rule(
            "temperature_anomaly",
            lambda data: self._check_temperature_anomaly(data),
            severity="warning",
            description="Detect temperature anomalies"
        )

        # Measurement out of range
        self.add_rule(
            "measurement_range",
            lambda data: self._check_measurement_ranges(data),
            severity="error",
            description="Detect out-of-range measurements"
        )

        # Execution time anomaly
        self.add_rule(
            "execution_time",
            lambda data: self._check_execution_time(data),
            severity="warning",
            description="Detect abnormal execution times"
        )

    def add_rule(
        self,
        rule_name: str,
        check_func: Callable,
        severity: str = "warning",
        description: str = ""
    ):
        """
        Add a monitoring rule.

        Args:
            rule_name: Unique rule identifier
            check_func: Function that takes data and returns (passed, message)
            severity: Alert severity (info, warning, error, critical)
            description: Rule description
        """
        self.validation_rules.append({
            "name": rule_name,
            "func": check_func,
            "severity": severity,
            "description": description,
        })
        logger.debug(f"Added monitoring rule: {rule_name}")

    def monitor_protocol_execution(
        self, protocol_id: str, protocol_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monitor protocol execution in real-time.

        Args:
            protocol_id: Protocol identifier
            protocol_data: Protocol execution data

        Returns:
            Monitoring result with alerts
        """
        logger.info(f"Monitoring protocol execution: {protocol_id}")

        result = {
            "protocol_id": protocol_id,
            "timestamp": datetime.now().isoformat(),
            "alerts": [],
            "metrics": {},
            "status": "ok",
        }

        # Track active protocol
        self.active_protocols[protocol_id] = {
            "start_time": datetime.now(),
            "data": protocol_data,
        }

        # Run monitoring rules
        for rule in self.validation_rules:
            try:
                passed, message = rule["func"](protocol_data)

                if not passed:
                    alert = self.alert_manager.create_alert(
                        alert_type=rule["name"],
                        severity=rule["severity"],
                        message=message,
                        protocol_id=protocol_id,
                    )
                    result["alerts"].append(alert)

                    # Update overall status
                    if rule["severity"] in ["error", "critical"]:
                        result["status"] = "error"
                    elif rule["severity"] == "warning" and result["status"] == "ok":
                        result["status"] = "warning"

            except Exception as e:
                logger.error(f"Error in monitoring rule {rule['name']}: {e}")

        # Collect metrics
        result["metrics"] = self.metrics_collector.collect_protocol_metrics(
            protocol_data
        )

        return result

    def monitor_measurement(
        self, protocol_id: str, measurement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monitor individual measurement in real-time.

        Args:
            protocol_id: Protocol identifier
            measurement: Measurement data

        Returns:
            Monitoring result
        """
        result = {
            "measurement_id": measurement.get("measurement_id"),
            "alerts": [],
            "status": "ok",
        }

        # Check measurement value range
        parameter = measurement.get("parameter")
        value = measurement.get("value")

        if parameter and value is not None:
            in_range, message = self._check_single_measurement_range(
                parameter, value
            )

            if not in_range:
                alert = self.alert_manager.create_alert(
                    alert_type="measurement_out_of_range",
                    severity="error",
                    message=message,
                    protocol_id=protocol_id,
                    measurement_id=measurement.get("measurement_id"),
                )
                result["alerts"].append(alert)
                result["status"] = "error"

        return result

    def _check_temperature_anomaly(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check for temperature anomalies."""
        parameters = protocol_data.get("parameters", {})
        temperature = parameters.get("temperature")

        if temperature is None:
            return True, ""

        # Check for extreme values
        if temperature < -50 or temperature > 100:
            return False, f"Extreme temperature detected: {temperature}°C"

        # Check for suspicious patterns in measurements
        measurements = protocol_data.get("measurements", [])
        temp_measurements = [
            m for m in measurements
            if isinstance(m, dict) and m.get("parameter") == "temperature"
        ]

        if len(temp_measurements) > 2:
            values = [m.get("value") for m in temp_measurements if m.get("value")]
            if values:
                # Check for sudden jumps
                for i in range(len(values) - 1):
                    if abs(values[i+1] - values[i]) > 20:
                        return False, f"Sudden temperature jump detected: {values[i]} to {values[i+1]}"

        return True, ""

    def _check_measurement_ranges(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check if all measurements are within acceptable ranges."""
        from validators import RangeValidator

        measurements = protocol_data.get("measurements", [])
        if not measurements:
            return True, ""

        validator = RangeValidator()
        out_of_range = []

        for measurement in measurements:
            if not isinstance(measurement, dict):
                continue

            parameter = measurement.get("parameter")
            value = measurement.get("value")

            if parameter and isinstance(value, (int, float)):
                result = validator.validate_value(parameter, value)
                if not result["is_valid"]:
                    out_of_range.append(f"{parameter}={value}")

        if out_of_range:
            return False, f"Measurements out of range: {', '.join(out_of_range)}"

        return True, ""

    def _check_execution_time(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check for abnormal execution times."""
        protocol_id = protocol_data.get("protocol_id")

        if protocol_id not in self.active_protocols:
            return True, ""

        start_time = self.active_protocols[protocol_id]["start_time"]
        elapsed = (datetime.now() - start_time).total_seconds()

        # Check if execution is taking too long (> 1 hour)
        if elapsed > 3600:
            return False, f"Protocol execution time excessive: {elapsed:.1f}s"

        return True, ""

    def _check_single_measurement_range(
        self, parameter: str, value: float
    ) -> tuple:
        """Check if a single measurement is in range."""
        from validators import RangeValidator

        validator = RangeValidator()
        result = validator.validate_value(parameter, value)

        if not result["is_valid"]:
            errors = ", ".join(result["errors"])
            return False, f"{parameter}: {errors}"

        return True, ""

    def get_active_protocols(self) -> List[str]:
        """
        Get list of currently active protocols.

        Returns:
            List of protocol IDs
        """
        return list(self.active_protocols.keys())

    def stop_monitoring(self, protocol_id: str):
        """
        Stop monitoring a protocol.

        Args:
            protocol_id: Protocol to stop monitoring
        """
        if protocol_id in self.active_protocols:
            del self.active_protocols[protocol_id]
            logger.info(f"Stopped monitoring protocol: {protocol_id}")

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """
        Get summary of monitoring activity.

        Returns:
            Summary dictionary
        """
        return {
            "active_protocols": len(self.active_protocols),
            "total_alerts": self.alert_manager.get_alert_count(),
            "rules_count": len(self.validation_rules),
        }
