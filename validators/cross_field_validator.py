"""
Cross-field validator for dependent fields and logical consistency.
"""
from typing import Dict, Any, List, Callable
from loguru import logger


class CrossFieldValidator:
    """Validates logical consistency across multiple fields."""

    def __init__(self):
        """Initialize cross-field validator."""
        self.validation_rules = []
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default cross-field validation rules."""
        # Rule: Temperature must be within range for irradiance measurement
        self.add_rule(
            "irradiance_temp_check",
            lambda data: self._check_irradiance_temperature(data),
            "Temperature must be appropriate for irradiance measurement"
        )

        # Rule: Power must not exceed theoretical maximum
        self.add_rule(
            "power_limit_check",
            lambda data: self._check_power_limits(data),
            "Power output must not exceed theoretical maximum"
        )

        # Rule: Fill factor must be consistent with voltage and current
        self.add_rule(
            "fill_factor_check",
            lambda data: self._check_fill_factor_consistency(data),
            "Fill factor must be consistent with I-V curve data"
        )

        # Rule: Test conditions must match protocol type
        self.add_rule(
            "protocol_conditions_check",
            lambda data: self._check_protocol_conditions(data),
            "Test conditions must match protocol requirements"
        )

    def add_rule(
        self, rule_name: str, validation_func: Callable, description: str
    ):
        """
        Add a custom validation rule.

        Args:
            rule_name: Unique name for the rule
            validation_func: Function that takes protocol data and returns (bool, str)
            description: Description of what the rule checks
        """
        self.validation_rules.append({
            "name": rule_name,
            "func": validation_func,
            "description": description,
        })
        logger.debug(f"Added validation rule: {rule_name}")

    def validate(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate protocol data against all cross-field rules.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "rule_results": {},
        }

        for rule in self.validation_rules:
            rule_name = rule["name"]
            validation_func = rule["func"]

            try:
                is_valid, message = validation_func(protocol_data)
                result["rule_results"][rule_name] = {
                    "passed": is_valid,
                    "message": message,
                }

                if not is_valid:
                    result["is_valid"] = False
                    result["errors"].append(f"{rule_name}: {message}")

            except Exception as e:
                logger.error(f"Error in validation rule {rule_name}: {e}")
                result["warnings"].append(
                    f"{rule_name}: Validation error - {str(e)}"
                )

        return result

    def _check_irradiance_temperature(
        self, protocol_data: Dict[str, Any]
    ) -> tuple:
        """Check if temperature is appropriate for irradiance measurement."""
        parameters = protocol_data.get("parameters", {})
        irradiance = parameters.get("irradiance")
        temperature = parameters.get("temperature")

        if irradiance is None or temperature is None:
            return True, "N/A - parameters not present"

        # STC conditions: 1000 W/m² at 25°C
        if irradiance >= 900 and irradiance <= 1100:
            if abs(temperature - 25) > 5:
                return False, f"STC requires ~25°C, got {temperature}°C"

        # Low irradiance testing typically at 25°C
        if irradiance < 300:
            if abs(temperature - 25) > 10:
                return False, f"Low irradiance testing typically at ~25°C, got {temperature}°C"

        return True, "Temperature appropriate for irradiance"

    def _check_power_limits(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check if power output is within theoretical limits."""
        measurements = protocol_data.get("measurements", [])

        power_measurements = [
            m for m in measurements
            if isinstance(m, dict) and m.get("parameter") == "power"
        ]

        if not power_measurements:
            return True, "N/A - no power measurements"

        for measurement in power_measurements:
            power = measurement.get("value")
            if power and power < 0:
                return False, "Power cannot be negative"

            # Check for unreasonably high power (> 500W for typical modules)
            if power and power > 500:
                return False, f"Power {power}W exceeds typical module limits"

        return True, "Power within acceptable limits"

    def _check_fill_factor_consistency(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check if fill factor is consistent with I-V data."""
        acceptance = protocol_data.get("acceptance_criteria", {})
        fill_factor = acceptance.get("fill_factor_min")

        if fill_factor is None:
            return True, "N/A - no fill factor specified"

        # Fill factor must be between 0 and 1 (or 0-100%)
        if fill_factor < 0 or fill_factor > 1:
            if fill_factor > 100:
                return False, "Fill factor cannot exceed 100%"
            if fill_factor < 0:
                return False, "Fill factor cannot be negative"

        # Typical fill factors are 0.65-0.85 for good modules
        if fill_factor < 0.50:
            return False, f"Fill factor {fill_factor} is unusually low"

        return True, "Fill factor within reasonable range"

    def _check_protocol_conditions(self, protocol_data: Dict[str, Any]) -> tuple:
        """Check if test conditions match protocol requirements."""
        protocol_type = protocol_data.get("protocol_type")
        parameters = protocol_data.get("parameters", {})

        if protocol_type == "electrical":
            # Electrical tests need voltage and current ranges
            if "voltage_range" not in parameters and "current_range" not in parameters:
                return False, "Electrical protocols require voltage/current ranges"

        elif protocol_type == "thermal":
            # Thermal tests need temperature profile
            if "temperature_profile" not in parameters and "temperature" not in parameters:
                return False, "Thermal protocols require temperature parameters"

        elif protocol_type == "mechanical":
            # Mechanical tests need load profile
            if "load_profile" not in parameters:
                return False, "Mechanical protocols require load profile"

        return True, "Protocol conditions match requirements"

    def validate_measurement_consistency(
        self, measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate consistency across multiple measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Validation result
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        if not measurements:
            return result

        # Check timestamp ordering
        timestamps = [
            m.get("timestamp") for m in measurements
            if m.get("timestamp")
        ]

        if len(timestamps) > 1:
            for i in range(len(timestamps) - 1):
                if timestamps[i] > timestamps[i + 1]:
                    result["warnings"].append(
                        "Measurements not in chronological order"
                    )
                    break

        # Check for duplicate measurement IDs
        measurement_ids = [m.get("measurement_id") for m in measurements]
        if len(measurement_ids) != len(set(measurement_ids)):
            result["is_valid"] = False
            result["errors"].append("Duplicate measurement IDs found")

        # Check unit consistency for same parameters
        param_units = {}
        for m in measurements:
            param = m.get("parameter")
            unit = m.get("unit")
            if param and unit:
                if param in param_units and param_units[param] != unit:
                    result["is_valid"] = False
                    result["errors"].append(
                        f"Inconsistent units for {param}: {param_units[param]} vs {unit}"
                    )
                param_units[param] = unit

        return result
