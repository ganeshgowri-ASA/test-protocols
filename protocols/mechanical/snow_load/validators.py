"""Snow Load Test Protocol Validators

Protocol-specific validation functions for snow load testing.
"""

from typing import Dict, Any
from protocols.base.validators import (
    validate_range,
    validate_positive,
    validate_non_negative,
    validate_required,
    validate_enum,
    ValidationError
)


def validate_snow_load_config(config: Dict[str, Any]) -> None:
    """
    Validate snow load test configuration.

    Args:
        config: Configuration dictionary

    Raises:
        ValidationError: If configuration is invalid
    """
    # Required fields
    validate_required("snow_load_pa", config.get("snow_load_pa"))
    validate_required("hold_duration_hours", config.get("hold_duration_hours"))
    validate_required("cycles", config.get("cycles"))

    # Snow load validation
    snow_load_pa = config["snow_load_pa"]
    validate_range("snow_load_pa", snow_load_pa, 0, 10000)

    # Duration validation
    hold_duration = config["hold_duration_hours"]
    validate_range("hold_duration_hours", hold_duration, 0.5, 48)

    # Cycles validation
    cycles = config["cycles"]
    validate_range("cycles", cycles, 1, 10)

    # Temperature validation (if provided)
    if "test_temperature_c" in config:
        validate_range("test_temperature_c", config["test_temperature_c"], -70, 60)

    # Humidity validation (if provided)
    if "test_humidity_pct" in config:
        validate_range("test_humidity_pct", config["test_humidity_pct"], 0, 100)

    # Load application rate (if provided)
    if "load_application_rate" in config:
        validate_positive("load_application_rate", config["load_application_rate"])

    # Support configuration (if provided)
    if "support_configuration" in config:
        validate_enum(
            "support_configuration",
            config["support_configuration"],
            ["4-point", "frame", "distributed"]
        )


def validate_module_specs(module_specs: Dict[str, Any]) -> None:
    """
    Validate PV module specifications.

    Args:
        module_specs: Module specifications dictionary

    Raises:
        ValidationError: If specifications are invalid
    """
    # Required fields
    validate_required("module_id", module_specs.get("module_id"))
    validate_required("dimensions", module_specs.get("dimensions"))
    validate_required("mass_kg", module_specs.get("mass_kg"))

    # Dimensions validation
    dimensions = module_specs["dimensions"]
    validate_required("length_mm", dimensions.get("length_mm"))
    validate_required("width_mm", dimensions.get("width_mm"))
    validate_required("thickness_mm", dimensions.get("thickness_mm"))

    validate_positive("length_mm", dimensions["length_mm"])
    validate_positive("width_mm", dimensions["width_mm"])
    validate_positive("thickness_mm", dimensions["thickness_mm"])

    # Mass validation
    validate_positive("mass_kg", module_specs["mass_kg"])

    # Frame type validation (if provided)
    if "frame_type" in module_specs:
        validate_enum(
            "frame_type",
            module_specs["frame_type"],
            ["aluminum", "stainless_steel", "plastic", "frameless"]
        )

    # Rated power validation (if provided)
    if "rated_power_w" in module_specs:
        validate_positive("rated_power_w", module_specs["rated_power_w"])


def validate_acceptance_criteria(criteria: Dict[str, Any]) -> None:
    """
    Validate test acceptance criteria.

    Args:
        criteria: Acceptance criteria dictionary

    Raises:
        ValidationError: If criteria are invalid
    """
    # Required fields
    validate_required("max_deflection_mm", criteria.get("max_deflection_mm"))
    validate_required("max_cracking", criteria.get("max_cracking"))

    # Deflection limits
    validate_non_negative("max_deflection_mm", criteria["max_deflection_mm"])

    if "max_permanent_deflection_mm" in criteria:
        validate_non_negative("max_permanent_deflection_mm", criteria["max_permanent_deflection_mm"])

        # Permanent deflection should be less than max deflection
        if criteria["max_permanent_deflection_mm"] > criteria["max_deflection_mm"]:
            raise ValidationError(
                "max_permanent_deflection_mm cannot exceed max_deflection_mm"
            )

    # Cracking level validation
    validate_enum(
        "max_cracking",
        criteria["max_cracking"],
        ["none", "micro", "hairline", "visible"]
    )

    # Performance retention validation (if provided)
    if "min_performance_retention_pct" in criteria:
        validate_range(
            "min_performance_retention_pct",
            criteria["min_performance_retention_pct"],
            0,
            100
        )


def validate_measurement(measurement: Dict[str, Any]) -> None:
    """
    Validate a single measurement point.

    Args:
        measurement: Measurement dictionary

    Raises:
        ValidationError: If measurement is invalid
    """
    # Required fields
    validate_required("timestamp", measurement.get("timestamp"))
    validate_required("phase", measurement.get("phase"))
    validate_required("load_applied_pa", measurement.get("load_applied_pa"))
    validate_required("deflection_mm", measurement.get("deflection_mm"))

    # Phase validation
    validate_enum(
        "phase",
        measurement["phase"],
        ["baseline", "loading", "hold", "unloading", "recovery"]
    )

    # Load validation
    validate_non_negative("load_applied_pa", measurement["load_applied_pa"])
    validate_range("load_applied_pa", measurement["load_applied_pa"], 0, 10000)

    # Deflection validation
    validate_non_negative("deflection_mm", measurement["deflection_mm"])

    # Visual condition validation (if provided)
    if "visual_condition" in measurement:
        validate_enum(
            "visual_condition",
            measurement["visual_condition"],
            [
                "normal",
                "micro_crack",
                "hairline_crack",
                "visible_crack",
                "delamination",
                "frame_damage",
                "glass_breakage"
            ]
        )

    # Temperature validation (if provided)
    if "temperature_c" in measurement and measurement["temperature_c"] is not None:
        validate_range("temperature_c", measurement["temperature_c"], -70, 60)

    # Humidity validation (if provided)
    if "humidity_pct" in measurement and measurement["humidity_pct"] is not None:
        validate_range("humidity_pct", measurement["humidity_pct"], 0, 100)


def validate_load_consistency(load_pa: float, module_area_m2: float) -> None:
    """
    Validate that the applied load is appropriate for the module size.

    Args:
        load_pa: Applied load in Pascals
        module_area_m2: Module area in square meters

    Raises:
        ValidationError: If load is inappropriate for module size
    """
    validate_positive("module_area_m2", module_area_m2)
    validate_non_negative("load_pa", load_pa)

    # Calculate total force
    total_force_n = load_pa * module_area_m2

    # Typical PV modules: 1.6 to 2.5 m²
    # Typical snow load: 2400 Pa (244 kg/m²)
    # Max expected force: ~6000 N
    max_reasonable_force = 10000  # N

    if total_force_n > max_reasonable_force:
        raise ValidationError(
            f"Total force ({total_force_n:.0f} N) exceeds reasonable limit for PV module testing. "
            f"Check load value ({load_pa} Pa) and module area ({module_area_m2:.2f} m²)."
        )


def validate_deflection_consistency(
    deflection_mm: float,
    load_pa: float,
    module_length_mm: float,
    expected_max_deflection_mm: float
) -> None:
    """
    Validate that deflection is reasonable for the applied load.

    Args:
        deflection_mm: Measured deflection in millimeters
        load_pa: Applied load in Pascals
        module_length_mm: Module length in millimeters
        expected_max_deflection_mm: Expected maximum deflection

    Raises:
        ValidationError: If deflection seems unreasonable
    """
    validate_non_negative("deflection_mm", deflection_mm)
    validate_non_negative("load_pa", load_pa)
    validate_positive("module_length_mm", module_length_mm)

    # Check if deflection is excessive (> L/50 is typically concerning)
    max_allowable_deflection = module_length_mm / 50

    if deflection_mm > max_allowable_deflection:
        raise ValidationError(
            f"Deflection ({deflection_mm:.1f} mm) exceeds span/50 limit "
            f"({max_allowable_deflection:.1f} mm) for module length {module_length_mm:.0f} mm. "
            f"This may indicate structural failure."
        )

    # For zero load, deflection should be minimal
    if load_pa == 0 and deflection_mm > 5:
        raise ValidationError(
            f"Deflection ({deflection_mm:.1f} mm) is excessive for zero load. "
            f"Check measurement system or module condition."
        )
