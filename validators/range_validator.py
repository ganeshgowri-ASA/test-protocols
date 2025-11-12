"""
Range validator for measurement values (temperature, irradiance, etc.).
"""
from typing import Dict, Any, Optional
from loguru import logger


class RangeValidator:
    """Validates measurement values against acceptable ranges."""

    # Standard acceptable ranges for common PV test parameters
    STANDARD_RANGES = {
        "temperature": {
            "min": -40,
            "max": 150,
            "unit": "°C",
            "warning_min": -30,
            "warning_max": 100,
        },
        "irradiance": {
            "min": 0,
            "max": 1500,
            "unit": "W/m²",
            "warning_min": 100,
            "warning_max": 1200,
        },
        "voltage": {
            "min": 0,
            "max": 100,
            "unit": "V",
        },
        "current": {
            "min": 0,
            "max": 20,
            "unit": "A",
        },
        "power": {
            "min": 0,
            "max": 500,
            "unit": "W",
        },
        "efficiency": {
            "min": 0,
            "max": 100,
            "unit": "%",
            "warning_min": 5,
            "warning_max": 25,
        },
        "humidity": {
            "min": 0,
            "max": 100,
            "unit": "%RH",
        },
        "pressure": {
            "min": 0,
            "max": 10000,
            "unit": "Pa",
        },
        "fill_factor": {
            "min": 0,
            "max": 1,
            "unit": "",
            "warning_min": 0.65,
            "warning_max": 0.85,
        },
    }

    def __init__(self, custom_ranges: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize range validator.

        Args:
            custom_ranges: Optional custom range definitions
        """
        self.ranges = self.STANDARD_RANGES.copy()
        if custom_ranges:
            self.ranges.update(custom_ranges)

    def validate_value(
        self, parameter: str, value: float, custom_range: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate a measurement value against acceptable range.

        Args:
            parameter: Parameter name (e.g., 'temperature', 'irradiance')
            value: Measured value
            custom_range: Optional custom range for this validation

        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "status": "pass",
        }

        # Get applicable range
        range_spec = custom_range or self.ranges.get(parameter.lower())
        if not range_spec:
            result["warnings"].append(
                f"No range specification found for parameter: {parameter}"
            )
            return result

        # Validate against hard limits
        min_val = range_spec.get("min")
        max_val = range_spec.get("max")

        if min_val is not None and value < min_val:
            result["is_valid"] = False
            result["status"] = "fail"
            result["errors"].append(
                f"Value {value} below minimum {min_val} {range_spec.get('unit', '')}"
            )

        if max_val is not None and value > max_val:
            result["is_valid"] = False
            result["status"] = "fail"
            result["errors"].append(
                f"Value {value} above maximum {max_val} {range_spec.get('unit', '')}"
            )

        # Check warning thresholds
        warning_min = range_spec.get("warning_min")
        warning_max = range_spec.get("warning_max")

        if warning_min is not None and min_val <= value < warning_min:
            result["warnings"].append(
                f"Value {value} near lower limit (warning: {warning_min})"
            )
            result["status"] = "warning" if result["status"] == "pass" else result["status"]

        if warning_max is not None and warning_max < value <= max_val:
            result["warnings"].append(
                f"Value {value} near upper limit (warning: {warning_max})"
            )
            result["status"] = "warning" if result["status"] == "pass" else result["status"]

        return result

    def validate_multiple_values(
        self, measurements: Dict[str, float], custom_ranges: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validate multiple measurement values.

        Args:
            measurements: Dictionary of parameter: value pairs
            custom_ranges: Optional custom ranges for parameters

        Returns:
            Overall validation result
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "results": {},
        }

        custom_ranges = custom_ranges or {}

        for parameter, value in measurements.items():
            custom_range = custom_ranges.get(parameter)
            param_result = self.validate_value(parameter, value, custom_range)
            result["results"][parameter] = param_result

            if not param_result["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(
                    [f"{parameter}: {err}" for err in param_result["errors"]]
                )

            result["warnings"].extend(
                [f"{parameter}: {warn}" for warn in param_result["warnings"]]
            )

        return result

    def add_range(self, parameter: str, range_spec: Dict[str, Any]):
        """
        Add or update a parameter range specification.

        Args:
            parameter: Parameter name
            range_spec: Range specification dictionary
        """
        self.ranges[parameter.lower()] = range_spec
        logger.info(f"Added/updated range for parameter: {parameter}")

    def get_range(self, parameter: str) -> Optional[Dict[str, Any]]:
        """
        Get range specification for a parameter.

        Args:
            parameter: Parameter name

        Returns:
            Range specification or None
        """
        return self.ranges.get(parameter.lower())

    def list_parameters(self) -> list:
        """
        List all available parameter ranges.

        Returns:
            List of parameter names
        """
        return list(self.ranges.keys())
