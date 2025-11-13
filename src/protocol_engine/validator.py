"""Protocol validator for validating protocol data against schemas."""

from typing import Any, Dict, List, Optional, Tuple
import jsonschema
from jsonschema import Draft7Validator, validators


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class ProtocolValidator:
    """Validate protocol data against JSON schemas."""

    def __init__(self, schema: Dict[str, Any]) -> None:
        """Initialize the validator with a schema.

        Args:
            schema: JSON schema dictionary
        """
        self.schema = schema
        self.validator = Draft7Validator(schema)

    def validate(self, protocol_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate protocol data against the schema.

        Args:
            protocol_data: Protocol data to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        for error in self.validator.iter_errors(protocol_data):
            error_path = ".".join(str(p) for p in error.path) if error.path else "root"
            error_msg = f"{error_path}: {error.message}"
            errors.append(error_msg)

        return len(errors) == 0, errors

    def validate_strict(self, protocol_data: Dict[str, Any]) -> None:
        """Validate protocol data and raise exception if invalid.

        Args:
            protocol_data: Protocol data to validate

        Raises:
            ValidationError: If validation fails
        """
        is_valid, errors = self.validate(protocol_data)

        if not is_valid:
            raise ValidationError(
                f"Protocol validation failed with {len(errors)} error(s)",
                errors
            )

    def validate_measurements(
        self,
        measurements: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate measurement data against configuration requirements.

        Args:
            measurements: List of measurement dictionaries
            config: Protocol configuration dictionary

        Returns:
            Tuple of (is_valid, list of error/warning messages)
        """
        errors = []

        if not measurements:
            errors.append("No measurements provided")
            return False, errors

        # Check minimum data points
        min_points = config.get("validation_rules", {}).get("min_data_points", 5)
        if len(measurements) < min_points:
            errors.append(
                f"Insufficient data points: {len(measurements)} < {min_points} required"
            )

        # Check angle range
        angles = [m.get("angle", 0) for m in measurements]
        min_angle = config.get("validation_rules", {}).get("min_angle", 0)
        max_angle = config.get("validation_rules", {}).get("max_angle", 90)

        if min(angles) < min_angle:
            errors.append(f"Angle below minimum: {min(angles)} < {min_angle}")

        if max(angles) > max_angle:
            errors.append(f"Angle above maximum: {max(angles)} > {max_angle}")

        # Check for duplicate angles
        if len(angles) != len(set(angles)):
            errors.append("Duplicate angles found in measurements")

        # Check measurement values are positive
        for i, meas in enumerate(measurements):
            angle = meas.get("angle", 0)

            if meas.get("isc", 0) < 0:
                errors.append(f"Negative Isc at angle {angle}°: {meas['isc']}")

            if meas.get("voc", 0) < 0:
                errors.append(f"Negative Voc at angle {angle}°: {meas['voc']}")

            if meas.get("pmax", 0) < 0:
                errors.append(f"Negative Pmax at angle {angle}°: {meas['pmax']}")

        # Check monotonic decrease (IAM should generally decrease with angle)
        powers = [m.get("pmax", 0) for m in sorted(measurements, key=lambda x: x.get("angle", 0))]
        if len(powers) > 1:
            # Allow some tolerance for measurement noise
            non_monotonic_count = sum(1 for i in range(1, len(powers)) if powers[i] > powers[i-1] * 1.05)
            if non_monotonic_count > len(powers) * 0.2:  # More than 20% violations
                errors.append(
                    f"Power does not decrease monotonically with angle "
                    f"({non_monotonic_count} violations)"
                )

        return len(errors) == 0, errors

    def validate_irradiance_stability(
        self,
        measurements: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate irradiance stability during test.

        Args:
            measurements: List of measurement dictionaries
            config: Protocol configuration dictionary

        Returns:
            Tuple of (is_stable, list of warning messages)
        """
        warnings = []

        irradiances = [m.get("irradiance_actual", 0) for m in measurements if "irradiance_actual" in m]

        if not irradiances:
            warnings.append("No actual irradiance data available for stability check")
            return True, warnings

        target_irradiance = config.get("default_settings", {}).get("irradiance", 1000)
        tolerance = config.get("validation_rules", {}).get("irradiance_tolerance", 50)

        for i, irr in enumerate(irradiances):
            deviation = abs(irr - target_irradiance)
            if deviation > tolerance:
                angle = measurements[i].get("angle", "unknown")
                warnings.append(
                    f"Irradiance deviation at angle {angle}°: "
                    f"{irr} W/m² (±{deviation:.1f} W/m² from target)"
                )

        # Check overall stability (coefficient of variation)
        if len(irradiances) > 1:
            mean_irr = sum(irradiances) / len(irradiances)
            std_irr = (sum((x - mean_irr)**2 for x in irradiances) / len(irradiances)) ** 0.5
            cv = std_irr / mean_irr if mean_irr > 0 else 0

            stability_threshold = config.get("validation_rules", {}).get("stability_threshold", 0.02)
            if cv > stability_threshold:
                warnings.append(
                    f"High irradiance variation: CV = {cv:.3f} "
                    f"(threshold: {stability_threshold})"
                )

        return len(warnings) == 0, warnings

    def validate_temperature_stability(
        self,
        measurements: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate temperature stability during test.

        Args:
            measurements: List of measurement dictionaries
            config: Protocol configuration dictionary

        Returns:
            Tuple of (is_stable, list of warning messages)
        """
        warnings = []

        temperatures = [m.get("temperature_actual", 0) for m in measurements if "temperature_actual" in m]

        if not temperatures:
            warnings.append("No actual temperature data available for stability check")
            return True, warnings

        target_temp = config.get("default_settings", {}).get("temperature", 25)
        tolerance = config.get("validation_rules", {}).get("temperature_tolerance", 5)

        for i, temp in enumerate(temperatures):
            deviation = abs(temp - target_temp)
            if deviation > tolerance:
                angle = measurements[i].get("angle", "unknown")
                warnings.append(
                    f"Temperature deviation at angle {angle}°: "
                    f"{temp}°C (±{deviation:.1f}°C from target)"
                )

        return len(warnings) == 0, warnings

    def validate_all(
        self,
        protocol_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive validation of protocol data.

        Args:
            protocol_data: Protocol data to validate
            config: Protocol configuration

        Returns:
            Dictionary with validation results
        """
        results = {
            "schema_valid": False,
            "measurements_valid": False,
            "irradiance_stable": False,
            "temperature_stable": False,
            "errors": [],
            "warnings": [],
            "overall_status": "fail"
        }

        # Schema validation
        schema_valid, schema_errors = self.validate(protocol_data)
        results["schema_valid"] = schema_valid
        results["errors"].extend(schema_errors)

        # Measurement validation
        measurements = protocol_data.get("measurements", [])
        meas_valid, meas_errors = self.validate_measurements(measurements, config)
        results["measurements_valid"] = meas_valid
        results["errors"].extend(meas_errors)

        # Irradiance stability
        irr_stable, irr_warnings = self.validate_irradiance_stability(measurements, config)
        results["irradiance_stable"] = irr_stable
        results["warnings"].extend(irr_warnings)

        # Temperature stability
        temp_stable, temp_warnings = self.validate_temperature_stability(measurements, config)
        results["temperature_stable"] = temp_stable
        results["warnings"].extend(temp_warnings)

        # Overall status
        if not results["errors"]:
            if not results["warnings"]:
                results["overall_status"] = "pass"
            else:
                results["overall_status"] = "pass_with_warnings"

        return results
