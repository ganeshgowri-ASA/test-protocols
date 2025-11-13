"""
Validation module for LIC-001 protocol
"""

from typing import Dict, List, Any, Tuple
from core.validators import (
    ProtocolValidator,
    RequiredFieldValidator,
    RangeValidator,
    ValidationSeverity,
    IVCurveValidator
)


class LIC001Validator:
    """
    Validator for LIC-001 Low Irradiance Conditions test data
    """

    # Test parameters
    TARGET_TEMPERATURE = 25.0  # °C
    TEMPERATURE_TOLERANCE = 2.0  # °C
    REQUIRED_IRRADIANCE_LEVELS = [200, 400, 600, 800]  # W/m²
    IRRADIANCE_TOLERANCE = 10.0  # W/m²
    MIN_IV_POINTS = 10

    def __init__(self):
        self.validator = ProtocolValidator()
        self._setup_validation_rules()

    def _setup_validation_rules(self):
        """Setup validation rules for LIC-001"""

        # Protocol info validations
        self.validator.add_rule(
            "protocol_info.protocol_id",
            RequiredFieldValidator(
                "protocol_id_required",
                severity=ValidationSeverity.ERROR,
                message="Protocol ID is required"
            )
        )

        # Sample info validations
        self.validator.add_rule(
            "sample_info.sample_id",
            RequiredFieldValidator(
                "sample_id_required",
                severity=ValidationSeverity.ERROR,
                message="Sample ID is required"
            )
        )

        self.validator.add_rule(
            "sample_info.module_area",
            RangeValidator(
                "module_area_range",
                min_value=0.1,
                max_value=10.0,
                severity=ValidationSeverity.ERROR,
                message="Module area must be between 0.1 and 10.0 m²"
            )
        )

        # Temperature validation
        self.validator.add_rule(
            "test_conditions.temperature",
            RangeValidator(
                "temperature_range",
                min_value=self.TARGET_TEMPERATURE - self.TEMPERATURE_TOLERANCE,
                max_value=self.TARGET_TEMPERATURE + self.TEMPERATURE_TOLERANCE,
                severity=ValidationSeverity.ERROR,
                message=f"Temperature must be {self.TARGET_TEMPERATURE}°C ± {self.TEMPERATURE_TOLERANCE}°C"
            )
        )

    def validate_all(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all test data

        Args:
            data: Complete test data dictionary

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Validate protocol info
        protocol_errors = self._validate_protocol_info(data.get("protocol_info", {}))
        errors.extend(protocol_errors)

        # Validate sample info
        sample_errors = self._validate_sample_info(data.get("sample_info", {}))
        errors.extend(sample_errors)

        # Validate test conditions
        conditions_errors = self._validate_test_conditions(data.get("test_conditions", {}))
        errors.extend(conditions_errors)

        # Validate measurements
        measurement_errors = self._validate_measurements(data.get("measurements", {}))
        errors.extend(measurement_errors)

        return len(errors) == 0, errors

    def _validate_protocol_info(self, protocol_info: Dict[str, Any]) -> List[str]:
        """Validate protocol information"""
        errors = []

        if not protocol_info:
            errors.append("Protocol info is missing")
            return errors

        # Check protocol ID
        if protocol_info.get("protocol_id") != "LIC-001":
            errors.append(f"Invalid protocol ID: {protocol_info.get('protocol_id')} (expected LIC-001)")

        # Check standard
        if protocol_info.get("standard") != "IEC 61215-1:2021":
            errors.append(f"Invalid standard: {protocol_info.get('standard')} (expected IEC 61215-1:2021)")

        return errors

    def _validate_sample_info(self, sample_info: Dict[str, Any]) -> List[str]:
        """Validate sample information"""
        errors = []

        if not sample_info:
            errors.append("Sample info is missing")
            return errors

        # Required fields
        required = ["sample_id", "module_type"]
        for field in required:
            if not sample_info.get(field):
                errors.append(f"Sample info: {field} is required")

        # Module area validation
        module_area = sample_info.get("module_area")
        if module_area is not None:
            if module_area <= 0:
                errors.append(f"Module area must be positive, got {module_area}")
            elif module_area > 10:
                errors.append(f"Module area seems unreasonably large: {module_area} m²")

        return errors

    def _validate_test_conditions(self, test_conditions: Dict[str, Any]) -> List[str]:
        """Validate test conditions"""
        errors = []

        if not test_conditions:
            errors.append("Test conditions are missing")
            return errors

        # Temperature validation
        temperature = test_conditions.get("temperature")
        if temperature is None:
            errors.append("Temperature is required")
        else:
            temp_min = self.TARGET_TEMPERATURE - self.TEMPERATURE_TOLERANCE
            temp_max = self.TARGET_TEMPERATURE + self.TEMPERATURE_TOLERANCE
            if not (temp_min <= temperature <= temp_max):
                errors.append(
                    f"Temperature {temperature}°C is outside tolerance "
                    f"({temp_min}°C to {temp_max}°C)"
                )

        # Irradiance levels validation
        irradiance_levels = test_conditions.get("irradiance_levels", [])
        if not irradiance_levels:
            errors.append("Irradiance levels are required")
        else:
            # Check all required levels are present
            missing_levels = set(self.REQUIRED_IRRADIANCE_LEVELS) - set(irradiance_levels)
            if missing_levels:
                errors.append(f"Missing irradiance levels: {sorted(missing_levels)}")

            # Check for extra levels
            extra_levels = set(irradiance_levels) - set(self.REQUIRED_IRRADIANCE_LEVELS)
            if extra_levels:
                errors.append(f"Unexpected irradiance levels: {sorted(extra_levels)}")

        # Spectrum validation
        spectrum = test_conditions.get("spectrum")
        if spectrum and spectrum not in ["AM1.5G", "AM1.5D"]:
            errors.append(f"Invalid spectrum: {spectrum} (expected AM1.5G or AM1.5D)")

        return errors

    def _validate_measurements(self, measurements: Dict[str, Any]) -> List[str]:
        """Validate measurement data"""
        errors = []

        if not measurements:
            errors.append("Measurements are missing")
            return errors

        # Check all required irradiance levels have measurements
        for irradiance in self.REQUIRED_IRRADIANCE_LEVELS:
            key = str(irradiance)
            if key not in measurements:
                errors.append(f"Missing measurements for {irradiance} W/m²")
                continue

            # Validate individual measurement
            measurement_errors = self._validate_single_measurement(
                measurements[key],
                irradiance
            )
            errors.extend([f"{irradiance} W/m²: {err}" for err in measurement_errors])

        return errors

    def _validate_single_measurement(
        self,
        measurement: Dict[str, Any],
        target_irradiance: int
    ) -> List[str]:
        """Validate a single measurement at one irradiance level"""
        errors = []

        if not measurement:
            return ["Measurement data is empty"]

        # Actual irradiance validation
        actual_irradiance = measurement.get("actual_irradiance")
        if actual_irradiance is None:
            errors.append("Actual irradiance is missing")
        else:
            irr_min = target_irradiance - self.IRRADIANCE_TOLERANCE
            irr_max = target_irradiance + self.IRRADIANCE_TOLERANCE
            if not (irr_min <= actual_irradiance <= irr_max):
                errors.append(
                    f"Actual irradiance {actual_irradiance} W/m² is outside tolerance "
                    f"({irr_min} to {irr_max} W/m²)"
                )

        # Actual temperature validation
        actual_temp = measurement.get("actual_temperature")
        if actual_temp is None:
            errors.append("Actual temperature is missing")
        else:
            temp_min = self.TARGET_TEMPERATURE - self.TEMPERATURE_TOLERANCE
            temp_max = self.TARGET_TEMPERATURE + self.TEMPERATURE_TOLERANCE
            if not (temp_min <= actual_temp <= temp_max):
                errors.append(
                    f"Actual temperature {actual_temp}°C is outside tolerance "
                    f"({temp_min} to {temp_max}°C)"
                )

        # I-V curve validation
        iv_curve = measurement.get("iv_curve", {})
        if not iv_curve:
            errors.append("I-V curve data is missing")
        else:
            curve_errors = self._validate_iv_curve(
                iv_curve,
                actual_irradiance or target_irradiance,
                actual_temp or self.TARGET_TEMPERATURE
            )
            errors.extend(curve_errors)

        return errors

    def _validate_iv_curve(
        self,
        iv_curve: Dict[str, Any],
        irradiance: float,
        temperature: float
    ) -> List[str]:
        """Validate I-V curve data"""
        errors = []

        voltage = iv_curve.get("voltage", [])
        current = iv_curve.get("current", [])

        # Check arrays exist and have data
        if not voltage:
            errors.append("Voltage array is empty")
        if not current:
            errors.append("Current array is empty")

        if not voltage or not current:
            return errors

        # Check minimum number of points
        if len(voltage) < self.MIN_IV_POINTS:
            errors.append(
                f"I-V curve has only {len(voltage)} points "
                f"(minimum {self.MIN_IV_POINTS} required)"
            )

        # Check arrays have same length
        if len(voltage) != len(current):
            errors.append(
                f"Voltage and current arrays have different lengths "
                f"({len(voltage)} vs {len(current)})"
            )
            return errors

        # Use IVCurveValidator for detailed validation
        validation_results = IVCurveValidator.validate_curve(
            voltage, current, irradiance, temperature
        )

        for result in validation_results:
            if not result.is_valid and result.severity == ValidationSeverity.ERROR:
                errors.append(result.message)

        return errors

    def validate_results(self, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate calculated results

        Args:
            results: Calculated results dictionary

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        if not results:
            errors.append("Results are empty")
            return False, errors

        by_irradiance = results.get("by_irradiance", {})

        # Check results exist for all irradiance levels
        for irradiance in self.REQUIRED_IRRADIANCE_LEVELS:
            key = str(irradiance)
            if key not in by_irradiance:
                errors.append(f"Missing results for {irradiance} W/m²")
                continue

            level_results = by_irradiance[key]

            # Validate key parameters
            result_errors = self._validate_level_results(level_results, irradiance)
            errors.extend([f"{irradiance} W/m²: {err}" for err in result_errors])

        return len(errors) == 0, errors

    def _validate_level_results(
        self,
        results: Dict[str, Any],
        irradiance: int
    ) -> List[str]:
        """Validate results for a single irradiance level"""
        errors = []

        required_fields = ["pmax", "vmp", "imp", "voc", "isc", "fill_factor", "efficiency"]

        for field in required_fields:
            if field not in results:
                errors.append(f"Missing required result: {field}")
                continue

            value = results[field]

            # Check for reasonable values
            if value is None or (isinstance(value, float) and not (0 <= value < float('inf'))):
                errors.append(f"Invalid value for {field}: {value}")

        # Specific validations
        if "fill_factor" in results:
            ff = results["fill_factor"]
            if not (0 <= ff <= 1):
                errors.append(f"Fill factor {ff} is out of range (0-1)")

        if "efficiency" in results:
            eff = results["efficiency"]
            if not (0 <= eff <= 100):
                errors.append(f"Efficiency {eff}% is out of range (0-100)")
            elif eff > 30:
                errors.append(f"Efficiency {eff}% seems unreasonably high")

        return errors
