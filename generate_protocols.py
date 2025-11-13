"""
Protocol Generator Script
=========================
Automatically generates all 52 PV testing protocol implementations
following the base protocol structure and specifications.

Usage:
    python generate_protocols.py --all
    python generate_protocols.py --category performance
    python generate_protocols.py --protocol STC-001
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProtocolSpec:
    """Specification for a testing protocol"""
    protocol_id: str
    protocol_name: str
    category: str
    standard_reference: str
    description: str
    test_parameters: List[Dict[str, Any]] = field(default_factory=list)
    data_fields: List[Dict[str, Any]] = field(default_factory=list)
    analysis_methods: List[str] = field(default_factory=list)
    validation_criteria: List[Dict[str, Any]] = field(default_factory=list)
    visualization_types: List[str] = field(default_factory=list)


# Complete Protocol Specifications Database
PROTOCOL_SPECIFICATIONS = {
    # ===== PERFORMANCE PROTOCOLS =====
    "STC-001": ProtocolSpec(
        protocol_id="STC-001",
        protocol_name="Standard Test Conditions (STC) Performance Test",
        category="performance",
        standard_reference="IEC 61215-1:2021 MQT 01",
        description="Measurement of electrical performance at Standard Test Conditions (1000 W/m², 25°C cell temp, AM1.5 spectrum)",
        test_parameters=[
            {"name": "irradiance", "type": "float", "unit": "W/m²", "default": 1000, "range": [980, 1020]},
            {"name": "cell_temperature", "type": "float", "unit": "°C", "default": 25, "range": [23, 27]},
            {"name": "air_mass", "type": "float", "unit": "-", "default": 1.5, "range": [1.4, 1.6]},
            {"name": "module_area", "type": "float", "unit": "m²", "required": True}
        ],
        data_fields=[
            {"name": "voltage", "type": "array", "unit": "V"},
            {"name": "current", "type": "array", "unit": "A"},
            {"name": "timestamp", "type": "datetime"}
        ],
        analysis_methods=["iv_curve_analysis", "mpp_extraction", "fill_factor_calculation", "efficiency_calculation"],
        validation_criteria=[
            {"parameter": "pmax", "min": 0, "tolerance": 0.05},
            {"parameter": "efficiency", "min": 0, "max": 100},
            {"parameter": "fill_factor", "min": 0.5, "max": 0.9}
        ],
        visualization_types=["iv_curve", "pv_curve", "parameter_comparison"]
    ),

    "NOCT-001": ProtocolSpec(
        protocol_id="NOCT-001",
        protocol_name="Nominal Operating Cell Temperature (NOCT) Test",
        category="performance",
        standard_reference="IEC 61215-2:2021",
        description="Measurement of module operating temperature under specified conditions (800 W/m², 20°C ambient, 1 m/s wind)",
        test_parameters=[
            {"name": "irradiance", "type": "float", "unit": "W/m²", "default": 800, "range": [780, 820]},
            {"name": "ambient_temperature", "type": "float", "unit": "°C", "default": 20, "range": [18, 22]},
            {"name": "wind_speed", "type": "float", "unit": "m/s", "default": 1.0, "range": [0.9, 1.1]},
            {"name": "tilt_angle", "type": "float", "unit": "degrees", "default": 45}
        ],
        data_fields=[
            {"name": "cell_temperature", "type": "array", "unit": "°C"},
            {"name": "back_temperature", "type": "array", "unit": "°C"},
            {"name": "irradiance", "type": "array", "unit": "W/m²"},
            {"name": "voltage", "type": "array", "unit": "V"},
            {"name": "current", "type": "array", "unit": "A"},
            {"name": "time", "type": "array", "unit": "minutes"}
        ],
        analysis_methods=["temperature_stabilization", "noct_calculation", "power_temperature_coefficient"],
        validation_criteria=[
            {"parameter": "noct", "min": 35, "max": 60},
            {"parameter": "stabilization_time", "max": 120}
        ],
        visualization_types=["temperature_profile", "time_series", "thermal_analysis"]
    ),

    "LIC-001": ProtocolSpec(
        protocol_id="LIC-001",
        protocol_name="Low Irradiance Characterization",
        category="performance",
        standard_reference="IEC 61853-1:2011",
        description="Performance characterization at low irradiance levels (200-800 W/m²)",
        test_parameters=[
            {"name": "irradiance_levels", "type": "list", "unit": "W/m²", "default": [200, 400, 600, 800]},
            {"name": "cell_temperature", "type": "float", "unit": "°C", "default": 25}
        ],
        data_fields=[
            {"name": "voltage", "type": "array", "unit": "V"},
            {"name": "current", "type": "array", "unit": "A"},
            {"name": "irradiance", "type": "array", "unit": "W/m²"}
        ],
        analysis_methods=["multi_irradiance_analysis", "efficiency_vs_irradiance", "linearity_check"],
        validation_criteria=[
            {"parameter": "efficiency_ratio", "min": 0.85, "max": 1.15}
        ],
        visualization_types=["multi_iv_curves", "efficiency_heatmap", "performance_ratio"]
    ),

    "PERF-001": ProtocolSpec(
        protocol_id="PERF-001",
        protocol_name="Performance Rating Test - Matrix Conditions",
        category="performance",
        standard_reference="IEC 61853-1:2011",
        description="Performance measurement at multiple irradiance and temperature conditions",
        test_parameters=[
            {"name": "irradiance_matrix", "type": "list", "default": [200, 400, 600, 800, 1000]},
            {"name": "temperature_matrix", "type": "list", "default": [15, 25, 50, 75]}
        ],
        data_fields=[
            {"name": "condition_id", "type": "string"},
            {"name": "irradiance", "type": "float", "unit": "W/m²"},
            {"name": "temperature", "type": "float", "unit": "°C"},
            {"name": "voltage", "type": "array", "unit": "V"},
            {"name": "current", "type": "array", "unit": "A"}
        ],
        analysis_methods=["matrix_analysis", "interpolation_model", "energy_rating_calculation"],
        validation_criteria=[
            {"parameter": "data_completeness", "min": 0.95}
        ],
        visualization_types=["3d_performance_surface", "contour_plot", "heatmap"]
    ),

    "PERF-002": ProtocolSpec(
        protocol_id="PERF-002",
        protocol_name="Annual Energy Yield Prediction",
        category="performance",
        standard_reference="IEC 61853-3:2018",
        description="Energy yield prediction based on climate data and performance matrix",
        test_parameters=[
            {"name": "location_data", "type": "dict", "required": True},
            {"name": "mounting_config", "type": "string", "default": "rack_mounted"}
        ],
        data_fields=[
            {"name": "climate_data", "type": "dataframe"},
            {"name": "performance_matrix", "type": "dict"}
        ],
        analysis_methods=["energy_yield_modeling", "loss_factor_analysis", "performance_ratio"],
        validation_criteria=[
            {"parameter": "pr", "min": 0.7, "max": 0.95}
        ],
        visualization_types=["annual_profile", "monthly_breakdown", "loss_waterfall"]
    ),

    "IAM-001": ProtocolSpec(
        protocol_id="IAM-001",
        protocol_name="Incidence Angle Modifier (IAM) Test",
        category="performance",
        standard_reference="IEC 61853-2:2016",
        description="Effect of angle of incidence on module performance",
        test_parameters=[
            {"name": "angle_range", "type": "list", "default": [0, 20, 40, 50, 60, 70, 80]},
            {"name": "irradiance", "type": "float", "default": 1000}
        ],
        data_fields=[
            {"name": "angle", "type": "array", "unit": "degrees"},
            {"name": "isc_normalized", "type": "array"},
            {"name": "pmax_normalized", "type": "array"}
        ],
        analysis_methods=["iam_curve_fitting", "angular_losses", "cosine_correction"],
        validation_criteria=[
            {"parameter": "iam_60deg", "min": 0.85, "max": 1.0}
        ],
        visualization_types=["iam_curve", "polar_plot", "loss_analysis"]
    ),

    "SPEC-001": ProtocolSpec(
        protocol_id="SPEC-001",
        protocol_name="Spectral Response Measurement",
        category="performance",
        standard_reference="IEC 60904-8:2014",
        description="Spectral response and quantum efficiency measurement",
        test_parameters=[
            {"name": "wavelength_range", "type": "list", "default": [300, 1200]},
            {"name": "wavelength_step", "type": "float", "default": 10}
        ],
        data_fields=[
            {"name": "wavelength", "type": "array", "unit": "nm"},
            {"name": "spectral_response", "type": "array", "unit": "A/W"},
            {"name": "quantum_efficiency", "type": "array", "unit": "%"}
        ],
        analysis_methods=["spectral_mismatch_calculation", "quantum_efficiency_analysis"],
        validation_criteria=[
            {"parameter": "peak_qe", "min": 0.7, "max": 1.0}
        ],
        visualization_types=["spectral_response_curve", "quantum_efficiency_plot"]
    ),

    "TEMP-001": ProtocolSpec(
        protocol_id="TEMP-001",
        protocol_name="Temperature Coefficient Measurement",
        category="performance",
        standard_reference="IEC 60891:2021",
        description="Measurement of temperature coefficients for Isc, Voc, and Pmax",
        test_parameters=[
            {"name": "temperature_range", "type": "list", "default": [15, 25, 40, 50, 60, 70]},
            {"name": "irradiance", "type": "float", "default": 1000}
        ],
        data_fields=[
            {"name": "temperature", "type": "array", "unit": "°C"},
            {"name": "isc", "type": "array", "unit": "A"},
            {"name": "voc", "type": "array", "unit": "V"},
            {"name": "pmax", "type": "array", "unit": "W"}
        ],
        analysis_methods=["temperature_coefficient_regression", "normalization"],
        validation_criteria=[
            {"parameter": "alpha_isc", "typical": 0.05},
            {"parameter": "beta_voc", "typical": -0.35},
            {"parameter": "gamma_pmax", "typical": -0.45}
        ],
        visualization_types=["coefficient_plots", "regression_lines", "comparison_table"]
    ),

    "ENER-001": ProtocolSpec(
        protocol_id="ENER-001",
        protocol_name="Energy Rating Test",
        category="performance",
        standard_reference="IEC 61853-3:2018",
        description="Energy rating calculation for different climate zones",
        test_parameters=[
            {"name": "climate_zones", "type": "list", "default": ["tropical", "moderate", "desert"]},
            {"name": "orientation", "type": "string", "default": "south_facing"}
        ],
        data_fields=[
            {"name": "climate_type", "type": "string"},
            {"name": "energy_yield", "type": "float", "unit": "kWh/kWp"},
            {"name": "performance_ratio", "type": "float"}
        ],
        analysis_methods=["climate_specific_modeling", "loss_analysis", "pr_calculation"],
        validation_criteria=[
            {"parameter": "energy_yield", "min": 800, "max": 2500}
        ],
        visualization_types=["climate_comparison", "monthly_profiles", "loss_breakdown"]
    ),

    "BIFI-001": ProtocolSpec(
        protocol_id="BIFI-001",
        protocol_name="Bifacial Module Characterization",
        category="performance",
        standard_reference="IEC TS 60904-1-2:2019",
        description="Characterization of bifacial modules under front and rear irradiance",
        test_parameters=[
            {"name": "front_irradiance", "type": "float", "default": 1000},
            {"name": "rear_irradiance_ratio", "type": "list", "default": [0, 0.1, 0.2, 0.3]},
            {"name": "albedo", "type": "float", "default": 0.2}
        ],
        data_fields=[
            {"name": "front_irradiance", "type": "float"},
            {"name": "rear_irradiance", "type": "float"},
            {"name": "voltage", "type": "array"},
            {"name": "current", "type": "array"},
            {"name": "bifacial_gain", "type": "float"}
        ],
        analysis_methods=["bifacial_gain_calculation", "bifaciality_factor", "equivalent_irradiance"],
        validation_criteria=[
            {"parameter": "bifaciality", "min": 0.65, "max": 0.95}
        ],
        visualization_types=["gain_vs_rear_irradiance", "bifacial_boost", "comparison_chart"]
    ),

    "TRACK-001": ProtocolSpec(
        protocol_id="TRACK-001",
        protocol_name="Tracking System Performance Evaluation",
        category="performance",
        standard_reference="IEC 62817:2014",
        description="Performance evaluation of solar tracking systems",
        test_parameters=[
            {"name": "tracking_type", "type": "string", "default": "single_axis"},
            {"name": "tracking_accuracy", "type": "float", "unit": "degrees"}
        ],
        data_fields=[
            {"name": "time", "type": "datetime"},
            {"name": "sun_position", "type": "dict"},
            {"name": "tracker_position", "type": "dict"},
            {"name": "power_output", "type": "float"}
        ],
        analysis_methods=["tracking_gain_calculation", "accuracy_analysis", "energy_comparison"],
        validation_criteria=[
            {"parameter": "tracking_accuracy", "max": 5.0},
            {"parameter": "tracking_gain", "min": 1.2}
        ],
        visualization_types=["sun_path_diagram", "tracking_accuracy_plot", "gain_analysis"]
    ),

    "CONC-001": ProtocolSpec(
        protocol_id="CONC-001",
        protocol_name="Concentrator PV System Test",
        category="performance",
        standard_reference="IEC 62670-1:2013",
        description="Performance testing of concentrator photovoltaic systems",
        test_parameters=[
            {"name": "concentration_ratio", "type": "float", "required": True},
            {"name": "dni_irradiance", "type": "float", "unit": "W/m²"}
        ],
        data_fields=[
            {"name": "dni", "type": "float"},
            {"name": "voltage", "type": "array"},
            {"name": "current", "type": "array"},
            {"name": "cell_temperature", "type": "float"}
        ],
        analysis_methods=["cpv_efficiency_calculation", "concentration_verification"],
        validation_criteria=[
            {"parameter": "dni_min", "min": 700}
        ],
        visualization_types=["cpv_performance_curve", "efficiency_vs_dni"]
    ),

    # ===== DEGRADATION PROTOCOLS =====
    "LID-001": ProtocolSpec(
        protocol_id="LID-001",
        protocol_name="Light-Induced Degradation (LID) Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021 MQT 19",
        description="Evaluation of power degradation due to light exposure",
        test_parameters=[
            {"name": "irradiance", "type": "float", "default": 1000},
            {"name": "exposure_time", "type": "float", "unit": "hours", "default": 60},
            {"name": "temperature", "type": "float", "default": 50}
        ],
        data_fields=[
            {"name": "time", "type": "array", "unit": "hours"},
            {"name": "pmax", "type": "array", "unit": "W"},
            {"name": "pmax_normalized", "type": "array", "unit": "%"}
        ],
        analysis_methods=["degradation_rate_calculation", "stabilization_detection", "lid_classification"],
        validation_criteria=[
            {"parameter": "max_degradation", "max": 3.0}
        ],
        visualization_types=["degradation_curve", "stabilization_plot", "lid_classification_chart"]
    ),

    "LETID-001": ProtocolSpec(
        protocol_id="LETID-001",
        protocol_name="Light and Elevated Temperature Induced Degradation",
        category="degradation",
        standard_reference="IEC TS 63126:2020",
        description="Evaluation of combined light and temperature induced degradation",
        test_parameters=[
            {"name": "temperature", "type": "float", "default": 75},
            {"name": "irradiance", "type": "float", "default": 1000},
            {"name": "test_duration", "type": "float", "unit": "hours", "default": 400}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "power", "type": "array"},
            {"name": "degradation", "type": "array"}
        ],
        analysis_methods=["letid_kinetics", "recovery_analysis", "defect_identification"],
        validation_criteria=[
            {"parameter": "max_degradation", "max": 5.0}
        ],
        visualization_types=["letid_curve", "kinetics_plot", "recovery_analysis"]
    ),

    "PID-001": ProtocolSpec(
        protocol_id="PID-001",
        protocol_name="Potential-Induced Degradation (PID) Test",
        category="degradation",
        standard_reference="IEC 62804-1:2015",
        description="Assessment of degradation due to high voltage stress",
        test_parameters=[
            {"name": "test_voltage", "type": "float", "unit": "V", "default": -1000},
            {"name": "temperature", "type": "float", "default": 85},
            {"name": "humidity", "type": "float", "unit": "%", "default": 85},
            {"name": "test_duration", "type": "float", "unit": "hours", "default": 96}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "leakage_current", "type": "array"},
            {"name": "power_degradation", "type": "array"}
        ],
        analysis_methods=["pid_rate_calculation", "recovery_test", "susceptibility_classification"],
        validation_criteria=[
            {"parameter": "max_degradation", "max": 5.0}
        ],
        visualization_types=["pid_curve", "leakage_current_plot", "recovery_curve"]
    ),

    "PID-002": ProtocolSpec(
        protocol_id="PID-002",
        protocol_name="PID Recovery Test",
        category="degradation",
        standard_reference="IEC 62804-1:2015",
        description="Evaluation of power recovery after PID stress",
        test_parameters=[
            {"name": "recovery_method", "type": "string", "default": "thermal"},
            {"name": "recovery_duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "power_recovery", "type": "array"}
        ],
        analysis_methods=["recovery_rate_analysis", "reversibility_assessment"],
        validation_criteria=[
            {"parameter": "recovery_percentage", "min": 90}
        ],
        visualization_types=["recovery_curve", "comparison_plot"]
    ),

    "UVID-001": ProtocolSpec(
        protocol_id="UVID-001",
        protocol_name="UV-Induced Degradation Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021 MQT 10",
        description="Assessment of UV radiation effects on module performance",
        test_parameters=[
            {"name": "uv_dose", "type": "float", "unit": "kWh/m²", "default": 60},
            {"name": "temperature", "type": "float", "default": 60}
        ],
        data_fields=[
            {"name": "uv_dose", "type": "array"},
            {"name": "power_change", "type": "array"},
            {"name": "visual_inspection", "type": "dict"}
        ],
        analysis_methods=["uv_degradation_analysis", "visual_defect_correlation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["uv_dose_response", "degradation_progression"]
    ),

    "SPONGE-001": ProtocolSpec(
        protocol_id="SPONGE-001",
        protocol_name="Sponge Layer Formation Detection",
        category="degradation",
        standard_reference="Internal Test Method",
        description="Detection and characterization of sponge layer defects",
        test_parameters=[
            {"name": "inspection_method", "type": "string", "default": "el_imaging"}
        ],
        data_fields=[
            {"name": "el_image", "type": "image"},
            {"name": "defect_locations", "type": "list"},
            {"name": "severity_score", "type": "float"}
        ],
        analysis_methods=["image_processing", "defect_quantification"],
        validation_criteria=[
            {"parameter": "affected_area", "max": 5.0}
        ],
        visualization_types=["el_image_overlay", "defect_map", "severity_heatmap"]
    ),

    "SNAIL-001": ProtocolSpec(
        protocol_id="SNAIL-001",
        protocol_name="Snail Trail Defect Analysis",
        category="degradation",
        standard_reference="Internal Test Method",
        description="Detection and analysis of snail trail defects",
        test_parameters=[
            {"name": "inspection_timing", "type": "string", "default": "post_stress"}
        ],
        data_fields=[
            {"name": "visual_image", "type": "image"},
            {"name": "el_image", "type": "image"},
            {"name": "defect_count", "type": "int"},
            {"name": "power_loss", "type": "float"}
        ],
        analysis_methods=["visual_classification", "power_correlation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 3.0}
        ],
        visualization_types=["before_after_comparison", "defect_distribution"]
    ),

    "DELAM-001": ProtocolSpec(
        protocol_id="DELAM-001",
        protocol_name="Delamination Detection and Analysis",
        category="degradation",
        standard_reference="IEC 61215-2:2021",
        description="Detection and quantification of encapsulant delamination",
        test_parameters=[
            {"name": "inspection_method", "type": "string", "default": "visual_and_el"}
        ],
        data_fields=[
            {"name": "delamination_area", "type": "float", "unit": "cm²"},
            {"name": "location", "type": "string"},
            {"name": "power_impact", "type": "float"}
        ],
        analysis_methods=["area_measurement", "power_loss_correlation"],
        validation_criteria=[
            {"parameter": "delamination_area", "max": 10.0}
        ],
        visualization_types=["delamination_map", "progression_timeline"]
    ),

    "CORR-001": ProtocolSpec(
        protocol_id="CORR-001",
        protocol_name="Corrosion Resistance Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021 MQT 12",
        description="Assessment of module resistance to corrosion",
        test_parameters=[
            {"name": "exposure_duration", "type": "float", "unit": "hours", "default": 240},
            {"name": "salt_concentration", "type": "float", "unit": "%", "default": 5}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "visual_rating", "type": "array"},
            {"name": "electrical_performance", "type": "array"}
        ],
        analysis_methods=["corrosion_rating", "performance_degradation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["corrosion_progression", "performance_impact"]
    ),

    "CHALK-001": ProtocolSpec(
        protocol_id="CHALK-001",
        protocol_name="Chalking and Discoloration Test",
        category="degradation",
        standard_reference="ASTM D4214",
        description="Assessment of backsheet chalking and discoloration",
        test_parameters=[
            {"name": "exposure_duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "chalking_rating", "type": "int"},
            {"name": "color_change", "type": "dict"},
            {"name": "transmittance_change", "type": "float"}
        ],
        analysis_methods=["visual_rating", "spectroscopic_analysis"],
        validation_criteria=[
            {"parameter": "chalking_rating", "min": 8}
        ],
        visualization_types=["color_change_plot", "rating_chart"]
    ),

    "YELLOW-001": ProtocolSpec(
        protocol_id="YELLOW-001",
        protocol_name="Encapsulant Yellowing Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021",
        description="Assessment of encapsulant discoloration",
        test_parameters=[
            {"name": "uv_exposure", "type": "float", "unit": "kWh/m²"},
            {"name": "temperature", "type": "float", "default": 60}
        ],
        data_fields=[
            {"name": "yellowness_index", "type": "array"},
            {"name": "transmittance", "type": "array"},
            {"name": "power_loss", "type": "array"}
        ],
        analysis_methods=["color_measurement", "optical_loss_calculation"],
        validation_criteria=[
            {"parameter": "yellowness_index_change", "max": 10}
        ],
        visualization_types=["color_progression", "transmittance_plot"]
    ),

    "CRACK-001": ProtocolSpec(
        protocol_id="CRACK-001",
        protocol_name="Cell Crack Detection and Analysis",
        category="degradation",
        standard_reference="IEC TS 62782:2016",
        description="Detection and classification of cell cracks using EL imaging",
        test_parameters=[
            {"name": "el_current", "type": "float", "unit": "A"},
            {"name": "imaging_resolution", "type": "string"}
        ],
        data_fields=[
            {"name": "el_image", "type": "image"},
            {"name": "crack_count", "type": "int"},
            {"name": "crack_classification", "type": "dict"},
            {"name": "power_loss", "type": "float"}
        ],
        analysis_methods=["crack_detection_ai", "crack_classification", "power_impact_analysis"],
        validation_criteria=[
            {"parameter": "critical_cracks", "max": 0}
        ],
        visualization_types=["el_image_annotated", "crack_map", "classification_chart"]
    ),

    "SOLDER-001": ProtocolSpec(
        protocol_id="SOLDER-001",
        protocol_name="Solder Bond Integrity Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021 MQT 16",
        description="Assessment of solder bond quality and degradation",
        test_parameters=[
            {"name": "thermal_cycles", "type": "int", "default": 200},
            {"name": "temp_range", "type": "list", "default": [-40, 85]}
        ],
        data_fields=[
            {"name": "cycle_number", "type": "array"},
            {"name": "series_resistance", "type": "array"},
            {"name": "fill_factor", "type": "array"}
        ],
        analysis_methods=["resistance_trend_analysis", "bond_failure_detection"],
        validation_criteria=[
            {"parameter": "resistance_increase", "max": 50}
        ],
        visualization_types=["resistance_progression", "ff_degradation"]
    ),

    "JBOX-001": ProtocolSpec(
        protocol_id="JBOX-001",
        protocol_name="Junction Box Integrity Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021 MQT 08",
        description="Assessment of junction box adhesion and functionality",
        test_parameters=[
            {"name": "peel_test_speed", "type": "float", "unit": "mm/min"}
        ],
        data_fields=[
            {"name": "adhesion_strength", "type": "float", "unit": "N"},
            {"name": "diode_functionality", "type": "bool"},
            {"name": "visual_inspection", "type": "dict"}
        ],
        analysis_methods=["adhesion_analysis", "electrical_continuity"],
        validation_criteria=[
            {"parameter": "adhesion_strength", "min": 40}
        ],
        visualization_types=["adhesion_chart", "failure_mode_analysis"]
    ),

    "SEAL-001": ProtocolSpec(
        protocol_id="SEAL-001",
        protocol_name="Edge Seal Integrity Test",
        category="degradation",
        standard_reference="IEC 61215-2:2021",
        description="Assessment of module edge seal integrity",
        test_parameters=[
            {"name": "test_method", "type": "string", "default": "dye_penetration"}
        ],
        data_fields=[
            {"name": "seal_integrity", "type": "bool"},
            {"name": "penetration_depth", "type": "float", "unit": "mm"},
            {"name": "failure_locations", "type": "list"}
        ],
        analysis_methods=["seal_quality_assessment", "failure_mode_analysis"],
        validation_criteria=[
            {"parameter": "seal_integrity", "value": True}
        ],
        visualization_types=["seal_map", "failure_distribution"]
    ),

    # ===== ENVIRONMENTAL PROTOCOLS =====
    "TC-001": ProtocolSpec(
        protocol_id="TC-001",
        protocol_name="Thermal Cycling Test",
        category="environmental",
        standard_reference="IEC 61215-2:2021 MQT 11",
        description="Assessment of module durability under thermal stress cycles",
        test_parameters=[
            {"name": "number_of_cycles", "type": "int", "default": 200},
            {"name": "temp_min", "type": "float", "default": -40},
            {"name": "temp_max", "type": "float", "default": 85},
            {"name": "dwell_time", "type": "float", "unit": "minutes", "default": 10}
        ],
        data_fields=[
            {"name": "cycle_number", "type": "array"},
            {"name": "power_output", "type": "array"},
            {"name": "visual_inspection", "type": "dict"},
            {"name": "el_imaging", "type": "image"}
        ],
        analysis_methods=["degradation_analysis", "failure_mode_identification"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0},
            {"parameter": "no_major_defects", "value": True}
        ],
        visualization_types=["cycle_degradation_curve", "thermal_profile", "defect_progression"]
    ),

    "DH-001": ProtocolSpec(
        protocol_id="DH-001",
        protocol_name="Damp Heat Test - 1000 hours",
        category="environmental",
        standard_reference="IEC 61215-2:2021 MQT 13",
        description="Accelerated aging test at 85°C/85% RH for 1000 hours",
        test_parameters=[
            {"name": "temperature", "type": "float", "default": 85},
            {"name": "humidity", "type": "float", "default": 85},
            {"name": "duration", "type": "float", "unit": "hours", "default": 1000}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "insulation_resistance", "type": "array"},
            {"name": "power_output", "type": "array"}
        ],
        analysis_methods=["moisture_ingress_analysis", "degradation_kinetics"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0},
            {"parameter": "insulation_resistance", "min": 40e6}
        ],
        visualization_types=["time_series_degradation", "insulation_resistance_plot"]
    ),

    "DH-002": ProtocolSpec(
        protocol_id="DH-002",
        protocol_name="Extended Damp Heat Test - 2000 hours",
        category="environmental",
        standard_reference="IEC 61215-2:2021",
        description="Extended damp heat exposure for harsh climate certification",
        test_parameters=[
            {"name": "temperature", "type": "float", "default": 85},
            {"name": "humidity", "type": "float", "default": 85},
            {"name": "duration", "type": "float", "unit": "hours", "default": 2000}
        ],
        data_fields=[
            {"name": "time", "type": "array"},
            {"name": "power_degradation", "type": "array"},
            {"name": "visual_defects", "type": "dict"}
        ],
        analysis_methods=["long_term_degradation_modeling", "failure_prediction"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 8.0}
        ],
        visualization_types=["degradation_curve", "defect_timeline"]
    ),

    "HF-001": ProtocolSpec(
        protocol_id="HF-001",
        protocol_name="Humidity Freeze Test",
        category="environmental",
        standard_reference="IEC 61215-2:2021 MQT 12",
        description="Combined humidity and freeze cycle test",
        test_parameters=[
            {"name": "number_of_cycles", "type": "int", "default": 10},
            {"name": "humidity_phase_temp", "type": "float", "default": 85},
            {"name": "freeze_temp", "type": "float", "default": -40}
        ],
        data_fields=[
            {"name": "cycle_number", "type": "array"},
            {"name": "power_output", "type": "array"},
            {"name": "visual_inspection", "type": "dict"}
        ],
        analysis_methods=["freeze_thaw_damage_assessment", "moisture_damage_correlation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["cycle_profile", "degradation_curve"]
    ),

    "UV-001": ProtocolSpec(
        protocol_id="UV-001",
        protocol_name="UV Preconditioning Test",
        category="environmental",
        standard_reference="IEC 61215-2:2021 MQT 10",
        description="UV exposure preconditioning test",
        test_parameters=[
            {"name": "uv_dose", "type": "float", "unit": "kWh/m²", "default": 15},
            {"name": "chamber_temperature", "type": "float", "default": 60}
        ],
        data_fields=[
            {"name": "uv_dose_accumulated", "type": "array"},
            {"name": "power_output", "type": "array"}
        ],
        analysis_methods=["uv_degradation_analysis"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["uv_dose_response"]
    ),

    "SALT-001": ProtocolSpec(
        protocol_id="SALT-001",
        protocol_name="Salt Mist Corrosion Test",
        category="environmental",
        standard_reference="IEC 61701:2020",
        description="Salt mist exposure test for coastal environments",
        test_parameters=[
            {"name": "severity_level", "type": "int", "default": 6},
            {"name": "test_duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "exposure_time", "type": "array"},
            {"name": "corrosion_rating", "type": "array"},
            {"name": "power_degradation", "type": "array"}
        ],
        analysis_methods=["corrosion_assessment", "performance_impact"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["corrosion_progression", "performance_degradation"]
    ),

    "SAND-001": ProtocolSpec(
        protocol_id="SAND-001",
        protocol_name="Sand and Dust Resistance Test",
        category="environmental",
        standard_reference="IEC 60068-2-68:2017",
        description="Resistance to sand and dust in desert climates",
        test_parameters=[
            {"name": "dust_concentration", "type": "float", "unit": "g/m³"},
            {"name": "wind_speed", "type": "float", "unit": "m/s"},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "transmittance_loss", "type": "float"},
            {"name": "surface_damage", "type": "dict"},
            {"name": "power_loss", "type": "float"}
        ],
        analysis_methods=["abrasion_analysis", "optical_loss_measurement"],
        validation_criteria=[
            {"parameter": "transmittance_loss", "max": 1.0}
        ],
        visualization_types=["surface_damage_map", "optical_loss_plot"]
    ),

    "AMMON-001": ProtocolSpec(
        protocol_id="AMMON-001",
        protocol_name="Ammonia Exposure Test",
        category="environmental",
        standard_reference="IEC 62716:2013",
        description="Resistance to ammonia corrosion in agricultural environments",
        test_parameters=[
            {"name": "ammonia_concentration", "type": "float", "unit": "ppm", "default": 100},
            {"name": "temperature", "type": "float", "default": 50},
            {"name": "humidity", "type": "float", "default": 85},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "exposure_time", "type": "array"},
            {"name": "power_output", "type": "array"},
            {"name": "corrosion_indicators", "type": "dict"}
        ],
        analysis_methods=["ammonia_corrosion_assessment", "degradation_kinetics"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["degradation_curve", "corrosion_indicators"]
    ),

    "SO2-001": ProtocolSpec(
        protocol_id="SO2-001",
        protocol_name="Sulfur Dioxide Exposure Test",
        category="environmental",
        standard_reference="Internal Test Method",
        description="Resistance to SO2 in industrial environments",
        test_parameters=[
            {"name": "so2_concentration", "type": "float", "unit": "ppm"},
            {"name": "exposure_cycles", "type": "int"}
        ],
        data_fields=[
            {"name": "exposure_time", "type": "array"},
            {"name": "corrosion_damage", "type": "dict"},
            {"name": "electrical_performance", "type": "array"}
        ],
        analysis_methods=["corrosion_analysis", "performance_degradation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["exposure_response", "damage_assessment"]
    ),

    "H2S-001": ProtocolSpec(
        protocol_id="H2S-001",
        protocol_name="Hydrogen Sulfide Exposure Test",
        category="environmental",
        standard_reference="Internal Test Method",
        description="Resistance to H2S in geothermal and industrial areas",
        test_parameters=[
            {"name": "h2s_concentration", "type": "float", "unit": "ppm"},
            {"name": "temperature", "type": "float"},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "exposure_time", "type": "array"},
            {"name": "silver_corrosion", "type": "dict"},
            {"name": "power_degradation", "type": "array"}
        ],
        analysis_methods=["metallization_corrosion_analysis"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["corrosion_timeline", "performance_impact"]
    ),

    "TROP-001": ProtocolSpec(
        protocol_id="TROP-001",
        protocol_name="Tropical Climate Test Sequence",
        category="environmental",
        standard_reference="IEC 61215-2:2021",
        description="Combined stress test for tropical climates",
        test_parameters=[
            {"name": "test_sequence", "type": "list"},
            {"name": "severity_level", "type": "string"}
        ],
        data_fields=[
            {"name": "test_stage", "type": "string"},
            {"name": "power_output", "type": "float"},
            {"name": "defect_assessment", "type": "dict"}
        ],
        analysis_methods=["multi_stress_analysis", "cumulative_degradation"],
        validation_criteria=[
            {"parameter": "final_power_loss", "max": 10.0}
        ],
        visualization_types=["test_sequence_timeline", "cumulative_degradation"]
    ),

    "DESERT-001": ProtocolSpec(
        protocol_id="DESERT-001",
        protocol_name="Desert Climate Test Sequence",
        category="environmental",
        standard_reference="IEC 61215-2:2021",
        description="Combined stress test for desert climates",
        test_parameters=[
            {"name": "test_sequence", "type": "list"},
            {"name": "uv_intensity", "type": "string", "default": "high"}
        ],
        data_fields=[
            {"name": "test_stage", "type": "string"},
            {"name": "power_output", "type": "float"},
            {"name": "thermal_effects", "type": "dict"}
        ],
        analysis_methods=["desert_specific_degradation", "thermal_cycling_effects"],
        validation_criteria=[
            {"parameter": "final_power_loss", "max": 10.0}
        ],
        visualization_types=["test_timeline", "degradation_breakdown"]
    ),

    # ===== MECHANICAL PROTOCOLS =====
    "ML-001": ProtocolSpec(
        protocol_id="ML-001",
        protocol_name="Mechanical Load Test - Static",
        category="mechanical",
        standard_reference="IEC 61215-2:2021 MQT 15",
        description="Static mechanical load test at specified pressures",
        test_parameters=[
            {"name": "front_load", "type": "float", "unit": "Pa", "default": 2400},
            {"name": "back_load", "type": "float", "unit": "Pa", "default": 2400},
            {"name": "cycles", "type": "int", "default": 3}
        ],
        data_fields=[
            {"name": "load_cycle", "type": "int"},
            {"name": "deflection", "type": "float", "unit": "mm"},
            {"name": "power_output", "type": "float"},
            {"name": "visual_inspection", "type": "dict"}
        ],
        analysis_methods=["deflection_analysis", "crack_detection", "power_correlation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0},
            {"parameter": "max_deflection", "max": 30}
        ],
        visualization_types=["load_deflection_curve", "power_vs_load", "crack_map"]
    ),

    "ML-002": ProtocolSpec(
        protocol_id="ML-002",
        protocol_name="Mechanical Load Test - Dynamic",
        category="mechanical",
        standard_reference="IEC 61215-2:2021 MQT 16",
        description="Dynamic mechanical load test with cyclic loading",
        test_parameters=[
            {"name": "load_amplitude", "type": "float", "unit": "Pa", "default": 1000},
            {"name": "number_of_cycles", "type": "int", "default": 1000},
            {"name": "frequency", "type": "float", "unit": "Hz"}
        ],
        data_fields=[
            {"name": "cycle_number", "type": "array"},
            {"name": "power_output", "type": "array"},
            {"name": "fatigue_indicators", "type": "dict"}
        ],
        analysis_methods=["fatigue_analysis", "progressive_degradation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["fatigue_curve", "power_degradation_trend"]
    ),

    "HAIL-001": ProtocolSpec(
        protocol_id="HAIL-001",
        protocol_name="Hail Impact Resistance Test",
        category="mechanical",
        standard_reference="IEC 61215-2:2021 MQT 17",
        description="Impact resistance test simulating hail stones",
        test_parameters=[
            {"name": "ice_ball_diameter", "type": "float", "unit": "mm", "default": 25},
            {"name": "impact_velocity", "type": "float", "unit": "m/s"},
            {"name": "number_of_impacts", "type": "int", "default": 11}
        ],
        data_fields=[
            {"name": "impact_location", "type": "list"},
            {"name": "visual_damage", "type": "dict"},
            {"name": "power_output", "type": "float"},
            {"name": "ir_thermography", "type": "image"}
        ],
        analysis_methods=["impact_damage_assessment", "power_loss_analysis"],
        validation_criteria=[
            {"parameter": "no_cracks", "value": True},
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["impact_location_map", "damage_assessment", "thermal_image"]
    ),

    "WIND-001": ProtocolSpec(
        protocol_id="WIND-001",
        protocol_name="Wind Load Resistance Test",
        category="mechanical",
        standard_reference="IEC 61215-2:2021",
        description="Resistance to wind loads and vibrations",
        test_parameters=[
            {"name": "wind_pressure", "type": "float", "unit": "Pa"},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "pressure", "type": "array"},
            {"name": "deflection", "type": "array"},
            {"name": "structural_integrity", "type": "bool"}
        ],
        analysis_methods=["structural_analysis", "deflection_limits"],
        validation_criteria=[
            {"parameter": "no_structural_damage", "value": True}
        ],
        visualization_types=["pressure_deflection", "stress_map"]
    ),

    "SNOW-001": ProtocolSpec(
        protocol_id="SNOW-001",
        protocol_name="Snow Load Test",
        category="mechanical",
        standard_reference="IEC 61215-2:2021",
        description="Resistance to snow load accumulation",
        test_parameters=[
            {"name": "snow_load", "type": "float", "unit": "Pa", "default": 5400},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "load_applied", "type": "float"},
            {"name": "deflection", "type": "float"},
            {"name": "power_output", "type": "float"}
        ],
        analysis_methods=["snow_load_analysis", "structural_integrity"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["load_deflection", "structural_response"]
    ),

    "VIBR-001": ProtocolSpec(
        protocol_id="VIBR-001",
        protocol_name="Vibration Test - Transportation",
        category="mechanical",
        standard_reference="IEC 61215-2:2021",
        description="Vibration resistance during transportation",
        test_parameters=[
            {"name": "vibration_profile", "type": "string"},
            {"name": "duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "vibration_spectrum", "type": "array"},
            {"name": "power_output", "type": "float"},
            {"name": "visual_inspection", "type": "dict"}
        ],
        analysis_methods=["vibration_damage_assessment"],
        validation_criteria=[
            {"parameter": "no_damage", "value": True}
        ],
        visualization_types=["vibration_spectrum", "damage_assessment"]
    ),

    "TWIST-001": ProtocolSpec(
        protocol_id="TWIST-001",
        protocol_name="Torsion/Twist Test",
        category="mechanical",
        standard_reference="IEC 61215-2:2021 MQT 18",
        description="Resistance to torsional stress",
        test_parameters=[
            {"name": "twist_angle", "type": "float", "unit": "degrees"},
            {"name": "cycles", "type": "int"}
        ],
        data_fields=[
            {"name": "twist_angle", "type": "array"},
            {"name": "power_output", "type": "array"},
            {"name": "crack_detection", "type": "dict"}
        ],
        analysis_methods=["torsion_stress_analysis", "crack_correlation"],
        validation_criteria=[
            {"parameter": "power_loss", "max": 5.0}
        ],
        visualization_types=["twist_response", "crack_progression"]
    ),

    "TERM-001": ProtocolSpec(
        protocol_id="TERM-001",
        protocol_name="Terminal Strength Test",
        category="mechanical",
        standard_reference="IEC 61215-2:2021 MQT 07",
        description="Mechanical strength of cable terminals",
        test_parameters=[
            {"name": "pull_force", "type": "float", "unit": "N"},
            {"name": "torque", "type": "float", "unit": "Nm"}
        ],
        data_fields=[
            {"name": "force_applied", "type": "float"},
            {"name": "displacement", "type": "float"},
            {"name": "failure_mode", "type": "string"}
        ],
        analysis_methods=["pull_test_analysis", "failure_mode_classification"],
        validation_criteria=[
            {"parameter": "min_pull_force", "min": 100}
        ],
        visualization_types=["force_displacement_curve", "failure_analysis"]
    ),

    # ===== SAFETY PROTOCOLS =====
    "INSU-001": ProtocolSpec(
        protocol_id="INSU-001",
        protocol_name="Insulation Resistance Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 01",
        description="Measurement of insulation resistance to ensure electrical safety",
        test_parameters=[
            {"name": "test_voltage", "type": "float", "unit": "V", "default": 1000},
            {"name": "test_duration", "type": "float", "unit": "seconds", "default": 60}
        ],
        data_fields=[
            {"name": "insulation_resistance", "type": "float", "unit": "Ω"},
            {"name": "leakage_current", "type": "float", "unit": "μA"},
            {"name": "test_conditions", "type": "dict"}
        ],
        analysis_methods=["insulation_assessment", "leakage_current_analysis"],
        validation_criteria=[
            {"parameter": "insulation_resistance", "min": 40e6}
        ],
        visualization_types=["resistance_measurement", "leakage_current_plot"]
    ),

    "WET-001": ProtocolSpec(
        protocol_id="WET-001",
        protocol_name="Wet Leakage Current Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 15",
        description="Leakage current measurement under wet conditions",
        test_parameters=[
            {"name": "water_resistivity", "type": "float", "unit": "Ω·cm"},
            {"name": "test_voltage", "type": "float", "unit": "V"}
        ],
        data_fields=[
            {"name": "leakage_current", "type": "float", "unit": "mA"},
            {"name": "water_temperature", "type": "float"},
            {"name": "pass_fail", "type": "bool"}
        ],
        analysis_methods=["wet_leakage_assessment"],
        validation_criteria=[
            {"parameter": "max_leakage_current", "max": 3.5}
        ],
        visualization_types=["leakage_current_measurement"]
    ),

    "DIEL-001": ProtocolSpec(
        protocol_id="DIEL-001",
        protocol_name="Dielectric Withstand Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 01",
        description="High voltage dielectric strength test",
        test_parameters=[
            {"name": "test_voltage", "type": "float", "unit": "V"},
            {"name": "test_duration", "type": "float", "unit": "seconds"}
        ],
        data_fields=[
            {"name": "voltage_applied", "type": "float"},
            {"name": "breakdown_occurred", "type": "bool"},
            {"name": "leakage_current", "type": "float"}
        ],
        analysis_methods=["dielectric_strength_assessment"],
        validation_criteria=[
            {"parameter": "no_breakdown", "value": True}
        ],
        visualization_types=["voltage_ramp", "current_response"]
    ),

    "GROUND-001": ProtocolSpec(
        protocol_id="GROUND-001",
        protocol_name="Ground Continuity Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 01",
        description="Verification of grounding conductor continuity",
        test_parameters=[
            {"name": "test_current", "type": "float", "unit": "A", "default": 10}
        ],
        data_fields=[
            {"name": "resistance", "type": "float", "unit": "Ω"},
            {"name": "pass_fail", "type": "bool"}
        ],
        analysis_methods=["ground_resistance_assessment"],
        validation_criteria=[
            {"parameter": "max_resistance", "max": 0.1}
        ],
        visualization_types=["resistance_measurement"]
    ),

    "HOT-001": ProtocolSpec(
        protocol_id="HOT-001",
        protocol_name="Hot Spot Endurance Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 09",
        description="Ability to withstand hot spot heating effects",
        test_parameters=[
            {"name": "shading_configuration", "type": "string"},
            {"name": "test_duration", "type": "float", "unit": "hours"}
        ],
        data_fields=[
            {"name": "hot_spot_temperature", "type": "float"},
            {"name": "time", "type": "array"},
            {"name": "visual_damage", "type": "dict"},
            {"name": "ir_image", "type": "image"}
        ],
        analysis_methods=["hot_spot_temperature_analysis", "thermal_damage_assessment"],
        validation_criteria=[
            {"parameter": "no_thermal_damage", "value": True}
        ],
        visualization_types=["temperature_profile", "ir_thermography", "damage_assessment"]
    ),

    "BYPASS-001": ProtocolSpec(
        protocol_id="BYPASS-001",
        protocol_name="Bypass Diode Thermal Test",
        category="safety",
        standard_reference="IEC 61215-2:2021 MQT 18",
        description="Thermal performance of bypass diodes under stress",
        test_parameters=[
            {"name": "bypass_current", "type": "float", "unit": "A"},
            {"name": "ambient_temperature", "type": "float", "unit": "°C"}
        ],
        data_fields=[
            {"name": "diode_temperature", "type": "array"},
            {"name": "junction_box_temperature", "type": "array"},
            {"name": "time", "type": "array"}
        ],
        analysis_methods=["thermal_runaway_detection", "diode_functionality_check"],
        validation_criteria=[
            {"parameter": "max_temperature", "max": 130}
        ],
        visualization_types=["temperature_profile", "thermal_image"]
    ),

    "FIRE-001": ProtocolSpec(
        protocol_id="FIRE-001",
        protocol_name="Fire Resistance Test",
        category="safety",
        standard_reference="UL 1703 / IEC 61730-2",
        description="Fire resistance and flame spread characteristics",
        test_parameters=[
            {"name": "fire_class_target", "type": "string"},
            {"name": "test_method", "type": "string"}
        ],
        data_fields=[
            {"name": "flame_spread", "type": "float"},
            {"name": "burning_duration", "type": "float"},
            {"name": "fire_class_achieved", "type": "string"}
        ],
        analysis_methods=["fire_classification", "flame_spread_analysis"],
        validation_criteria=[
            {"parameter": "fire_class", "value": "Class C or better"}
        ],
        visualization_types=["fire_test_results", "classification_chart"]
    ),
}


class ProtocolGenerator:
    """Generate protocol implementation files from specifications"""

    def __init__(self, output_dir: Path = Path(".")):
        self.output_dir = output_dir
        self.template_dir = output_dir / "templates" / "protocols"
        self.protocol_dir = output_dir / "protocols"

    def generate_all(self):
        """Generate all protocols"""
        print("Generating all 52 protocols...")

        for protocol_id, spec in PROTOCOL_SPECIFICATIONS.items():
            print(f"Generating {protocol_id}: {spec.protocol_name}")
            self.generate_protocol(spec)

        print(f"\n✅ Successfully generated all {len(PROTOCOL_SPECIFICATIONS)} protocols!")

    def generate_protocol(self, spec: ProtocolSpec):
        """Generate files for a single protocol"""
        # Generate JSON template
        self._generate_json_template(spec)

        # Generate Python implementation
        self._generate_python_class(spec)

    def _generate_json_template(self, spec: ProtocolSpec):
        """Generate JSON template file"""
        template = {
            "protocol_id": spec.protocol_id,
            "protocol_name": spec.protocol_name,
            "version": "1.0.0",
            "category": spec.category,
            "standard_reference": spec.standard_reference,
            "description": spec.description,
            "test_parameters": spec.test_parameters,
            "data_fields": spec.data_fields,
            "analysis_methods": spec.analysis_methods,
            "validation_criteria": spec.validation_criteria,
            "visualization_types": spec.visualization_types,
            "ui_config": {
                "tabs": [
                    {"id": "setup", "name": "Setup", "icon": "⚙️"},
                    {"id": "data", "name": "Data Acquisition", "icon": "📊"},
                    {"id": "analysis", "name": "Analysis", "icon": "🔬"},
                    {"id": "validation", "name": "Validation", "icon": "✅"},
                    {"id": "report", "name": "Report", "icon": "📄"}
                ]
            }
        }

        template_path = self.template_dir / f"{spec.protocol_id}.json"
        template_path.parent.mkdir(parents=True, exist_ok=True)

        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)

    def _generate_python_class(self, spec: ProtocolSpec):
        """Generate Python protocol class"""
        class_name = spec.protocol_id.replace('-', '') + "Protocol"

        python_code = f'''"""
{spec.protocol_name} Protocol
{'=' * len(spec.protocol_name + ' Protocol')}

Protocol ID: {spec.protocol_id}
Category: {spec.category.upper()}
Standard: {spec.standard_reference}

Description:
{spec.description}

Author: GenSpark PV Testing Framework
Auto-generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from protocols.base_protocol import (
    BaseProtocol,
    ProtocolMetadata,
    ValidationResult,
    ValidationLevel,
    ProtocolFactory
)
from utils.data_validation import DataValidator, FieldValidator
from utils.visualization import PlotlyChartBuilder
from utils.calculations import PVCalculations, StatisticalAnalysis


class {class_name}(BaseProtocol):
    """
    Implementation of {spec.protocol_name}

    This protocol implements {spec.standard_reference} testing procedures
    for PV module {spec.category} characterization.
    """

    def __init__(self):
        metadata = ProtocolMetadata(
            protocol_id="{spec.protocol_id}",
            protocol_name="{spec.protocol_name}",
            version="1.0.0",
            category="{spec.category}",
            standard_reference="{spec.standard_reference}",
            description="{spec.description}"
        )
        super().__init__(metadata)
        self.validator = DataValidator()

    def get_protocol_id(self) -> str:
        return "{spec.protocol_id}"

    def get_protocol_name(self) -> str:
        return "{spec.protocol_name}"

    def get_category(self) -> str:
        return "{spec.category}"

    def get_standard_reference(self) -> str:
        return "{spec.standard_reference}"

    def setup_test_parameters(self) -> Dict[str, Any]:
        """
        Define test setup parameters for {spec.protocol_id}.

        Returns:
            Dictionary of setup parameters with validation rules
        """
        parameters = {{}}

{self._generate_parameter_setup(spec.test_parameters)}

        return parameters

    def acquire_data(self, setup_params: Dict[str, Any]) -> pd.DataFrame:
        """
        Acquire test data for {spec.protocol_id}.

        Args:
            setup_params: Test setup configuration

        Returns:
            DataFrame containing raw test data
        """
        # Data acquisition implementation
        # In production, this would interface with test equipment

{self._generate_data_acquisition(spec.data_fields)}

        return data

    def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze acquired data for {spec.protocol_id}.

        Args:
            data: Raw test data

        Returns:
            Dictionary containing analysis results
        """
        results = {{}}

{self._generate_analysis_methods(spec.analysis_methods)}

        return results

    def validate_results(self, results: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate analysis results against {spec.standard_reference} criteria.

        Args:
            results: Analysis results to validate

        Returns:
            List of validation results
        """
        validation_results = []

{self._generate_validation_checks(spec.validation_criteria)}

        return validation_results

    def generate_visualizations(self, data: pd.DataFrame,
                               results: Dict[str, Any]) -> List[go.Figure]:
        """
        Generate interactive visualizations for {spec.protocol_id}.

        Args:
            data: Test data
            results: Analysis results

        Returns:
            List of Plotly figure objects
        """
        figures = []

{self._generate_visualizations(spec.visualization_types)}

        return figures


# Register protocol with factory
ProtocolFactory.register("{spec.protocol_id}", {class_name})


if __name__ == "__main__":
    # Example usage and testing
    protocol = {class_name}()
    print(f"Protocol: {{protocol.get_protocol_name()}}")
    print(f"ID: {{protocol.get_protocol_id()}}")
    print(f"Category: {{protocol.get_category()}}")
    print(f"Standard: {{protocol.get_standard_reference()}}")
'''

        # Save to appropriate category directory
        protocol_path = self.protocol_dir / spec.category / f"{spec.protocol_id}.py"
        protocol_path.parent.mkdir(parents=True, exist_ok=True)

        with open(protocol_path, 'w') as f:
            f.write(python_code)

    def _generate_parameter_setup(self, parameters: List[Dict]) -> str:
        """Generate parameter setup code"""
        code_lines = []
        for param in parameters:
            param_name = param['name']
            param_type = param.get('type', 'float')
            default = param.get('default', 'None')
            unit = param.get('unit', '')
            required = param.get('required', False)

            code_lines.append(f"        parameters['{param_name}'] = {{")
            code_lines.append(f"            'type': '{param_type}',")
            code_lines.append(f"            'default': {default},")
            if unit:
                code_lines.append(f"            'unit': '{unit}',")
            code_lines.append(f"            'required': {required}")
            code_lines.append("        }")

        return '\n'.join(code_lines)

    def _generate_data_acquisition(self, data_fields: List[Dict]) -> str:
        """Generate data acquisition code"""
        code = """        # Simulated data acquisition
        # In production, replace with actual equipment interface
        data = pd.DataFrame({
"""
        for field in data_fields:
            field_name = field['name']
            field_type = field.get('type', 'float')

            if field_type == 'array':
                code += f"            '{field_name}': np.random.randn(100),\n"
            elif field_type == 'float':
                code += f"            '{field_name}': [np.random.randn()],\n"
            elif field_type == 'datetime':
                code += f"            '{field_name}': [datetime.now()],\n"
            else:
                code += f"            '{field_name}': ['sample_value'],\n"

        code += "        })\n"
        return code

    def _generate_analysis_methods(self, methods: List[str]) -> str:
        """Generate analysis method calls"""
        code = """        # Perform analysis
        try:
            # Implement specific analysis methods
"""
        for method in methods:
            code += f"            # results['{method}'] = self._{method}(data)\n"

        code += """            results['analysis_complete'] = True
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            results['error'] = str(e)
"""
        return code

    def _generate_validation_checks(self, criteria: List[Dict]) -> str:
        """Generate validation check code"""
        code = ""
        for criterion in criteria:
            param = criterion.get('parameter', 'unknown')
            min_val = criterion.get('min')
            max_val = criterion.get('max')
            value = criterion.get('value')

            code += f"""
        # Validate {param}
        if '{param}' in results:
"""
            if min_val is not None:
                code += f"""            if results['{param}'] < {min_val}:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='{param}',
                    message=f'{param} below minimum: {{results[\\"{param}\\"]}}',
                    value=results['{param}'],
                    expected={min_val}
                ))
"""
            if max_val is not None:
                code += f"""            if results['{param}'] > {max_val}:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='{param}',
                    message=f'{param} above maximum: {{results[\\"{param}\\"]}}',
                    value=results['{param}'],
                    expected={max_val}
                ))
"""
            if value is not None:
                code += f"""            if results['{param}'] != {value}:
                validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field='{param}',
                    message=f'{param} does not match expected value',
                    value=results['{param}'],
                    expected={value}
                ))
"""

        return code

    def _generate_visualizations(self, viz_types: List[str]) -> str:
        """Generate visualization code"""
        code = """
        # Generate standard visualizations
        try:
"""
        for viz_type in viz_types:
            code += f"            # fig = PlotlyChartBuilder.create_{viz_type}(...)\n"
            code += f"            # figures.append(fig)\n"

        code += """            pass
        except Exception as e:
            self.logger.error(f"Visualization error: {e}")
"""
        return code


def main():
    """Main entry point for protocol generation"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate PV Testing Protocols")
    parser.add_argument("--all", action="store_true", help="Generate all protocols")
    parser.add_argument("--category", type=str, help="Generate protocols for specific category")
    parser.add_argument("--protocol", type=str, help="Generate specific protocol by ID")

    args = parser.parse_args()

    generator = ProtocolGenerator()

    if args.all:
        generator.generate_all()
    elif args.category:
        for protocol_id, spec in PROTOCOL_SPECIFICATIONS.items():
            if spec.category == args.category:
                generator.generate_protocol(spec)
    elif args.protocol:
        if args.protocol in PROTOCOL_SPECIFICATIONS:
            generator.generate_protocol(PROTOCOL_SPECIFICATIONS[args.protocol])
        else:
            print(f"Error: Protocol {args.protocol} not found")
    else:
        print("Please specify --all, --category, or --protocol")


if __name__ == "__main__":
    main()
