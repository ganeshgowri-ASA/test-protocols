"""Snow Load Test Protocol - SNOW-001

Implementation of snow load testing for photovoltaic modules according to
IEC 61215-1:2016 Part 1.
"""

from .protocol import (
    SnowLoadTestProtocol,
    SnowLoadTestConfig,
    ModuleSpecs,
    LoadPhase,
    VisualCondition,
    MeasurementPoint
)
from .analysis import (
    SnowLoadAnalyzer,
    AnalysisResults,
    LoadDeflectionPoint,
    plot_load_deflection_curve,
    generate_report_summary
)
from .validators import (
    validate_snow_load_config,
    validate_module_specs,
    validate_acceptance_criteria,
    validate_measurement
)


__all__ = [
    # Protocol classes
    "SnowLoadTestProtocol",
    "SnowLoadTestConfig",
    "ModuleSpecs",
    "LoadPhase",
    "VisualCondition",
    "MeasurementPoint",
    # Analysis classes
    "SnowLoadAnalyzer",
    "AnalysisResults",
    "LoadDeflectionPoint",
    "plot_load_deflection_curve",
    "generate_report_summary",
    # Validators
    "validate_snow_load_config",
    "validate_module_specs",
    "validate_acceptance_criteria",
    "validate_measurement",
]
