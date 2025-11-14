"""
Validators for electrical performance protocols (PVTP-010 through PVTP-015)
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator, root_validator
from backend.validators.base import (
    SampleInfoBase, IVCurveData, ElectricalParameters,
    TestConditions, IVDataPoint, MeasurementBase
)


# ============================================================================
# PVTP-010: Flash Test / STC Performance
# ============================================================================

class PVTP010_FlashMeasurement(BaseModel):
    """Flash measurement data for PVTP-010"""
    irradiance_measured: float = Field(..., ge=800, le=1200, description="W/m²")
    temperature_measured: float = Field(..., ge=15, le=45, description="°C")
    voc_measured: float = Field(..., gt=0, description="V")
    isc_measured: float = Field(..., gt=0, description="A")
    pmax_measured: float = Field(..., gt=0, description="W")
    vmpp_measured: float = Field(..., gt=0, description="V")
    impp_measured: float = Field(..., gt=0, description="A")
    ff_measured: Optional[float] = Field(None, ge=0, le=1)

    @validator('ff_measured', always=True)
    def calculate_ff(cls, v, values):
        if v is None and all(k in values for k in ['voc_measured', 'isc_measured', 'pmax_measured']):
            voc_isc = values['voc_measured'] * values['isc_measured']
            if voc_isc > 0:
                return values['pmax_measured'] / voc_isc
        return v


class PVTP010_STCResults(BaseModel):
    """STC-corrected results for PVTP-010"""
    voc_stc: float = Field(..., gt=0, description="V @ STC")
    isc_stc: float = Field(..., gt=0, description="A @ STC")
    pmax_stc: float = Field(..., gt=0, description="W @ STC")
    vmpp_stc: float = Field(..., gt=0, description="V @ STC")
    impp_stc: float = Field(..., gt=0, description="A @ STC")
    ff_stc: float = Field(..., ge=0, le=1, description="FF @ STC")
    efficiency_stc: Optional[float] = Field(None, ge=0, le=100, description="% @ STC")

    combined_uncertainty_pmax: float = Field(..., ge=0, le=10, description="% uncertainty")
    expanded_uncertainty_pmax: float = Field(..., ge=0, le=20, description="% expanded (k=2)")


class PVTP010_Input(SampleInfoBase):
    """Input data for PVTP-010"""
    rated_power: float = Field(..., gt=0, description="Nameplate power (W)")


class PVTP010_Measurement(BaseModel):
    """Complete measurement for PVTP-010"""
    pre_test_conditions: Dict[str, float]
    flash_measurement: PVTP010_FlashMeasurement
    spectral_mismatch_factor: Optional[float] = Field(1.0, ge=0.9, le=1.1)


class PVTP010_Analysis(BaseModel):
    """Analysis results for PVTP-010"""
    stc_results: PVTP010_STCResults
    performance_ratio: float = Field(..., ge=0, le=150, description="% of nameplate")
    power_deviation: float = Field(..., description="W from nameplate")


class PVTP010_Complete(BaseModel):
    """Complete PVTP-010 test data"""
    inputs: PVTP010_Input
    measurements: PVTP010_Measurement
    analysis: PVTP010_Analysis


# ============================================================================
# PVTP-011: I-V Curve Characterization
# ============================================================================

class PVTP011_ExtractedParameters(BaseModel):
    """Extracted electrical parameters from I-V curve"""
    # Basic parameters
    voc: float = Field(..., gt=0)
    isc: float = Field(..., gt=0)
    pmax: float = Field(..., gt=0)
    vmpp: float = Field(..., gt=0)
    impp: float = Field(..., gt=0)
    fill_factor: float = Field(..., ge=0, le=1)

    # Advanced parameters
    series_resistance: float = Field(..., ge=0, description="Ohms")
    shunt_resistance: float = Field(..., gt=0, description="Ohms")
    ideality_factor: Optional[float] = Field(None, ge=0.5, le=5)
    reverse_saturation_current: Optional[float] = Field(None, gt=0, description="A")

    @validator('series_resistance')
    def rs_reasonable(cls, v):
        if v > 10:  # Warning threshold
            pass  # Could log warning
        return v

    @validator('shunt_resistance')
    def rsh_reasonable(cls, v):
        if v < 100:  # Warning threshold
            pass  # Could log warning
        return v


class PVTP011_ModelFit(BaseModel):
    """Single diode model fit parameters"""
    I_L: float = Field(..., description="Light current (A)")
    I_0: float = Field(..., gt=0, description="Saturation current (A)")
    Rs: float = Field(..., ge=0, description="Series resistance (Ohm)")
    Rsh: float = Field(..., gt=0, description="Shunt resistance (Ohm)")
    n: float = Field(..., ge=0.5, le=5, description="Ideality factor")
    r_squared: float = Field(..., ge=0, le=1, description="Fit quality")

    @validator('r_squared')
    def rsquared_threshold(cls, v):
        if v < 0.999:
            raise ValueError(f'R² ({v}) below quality threshold (0.999)')
        return v


class PVTP011_Input(SampleInfoBase):
    """Input data for PVTP-011"""
    test_conditions: str = Field("STC (1000 W/m², 25°C, AM1.5G)")
    cell_count: Optional[int] = Field(None, ge=1, le=200)
    module_area: Optional[float] = Field(None, gt=0, description="m²")


class PVTP011_Measurement(BaseModel):
    """Measurement data for PVTP-011"""
    test_conditions: TestConditions
    iv_curve_data: IVCurveData
    reverse_bias_data: Optional[List[IVDataPoint]] = None


class PVTP011_Analysis(BaseModel):
    """Analysis for PVTP-011"""
    extracted_parameters: PVTP011_ExtractedParameters
    model_fit: PVTP011_ModelFit
    efficiency: Optional[float] = Field(None, ge=0, le=100)


class PVTP011_Complete(BaseModel):
    """Complete PVTP-011 test data"""
    inputs: PVTP011_Input
    measurements: PVTP011_Measurement
    analysis: PVTP011_Analysis


# ============================================================================
# PVTP-012: Low Irradiance Performance
# ============================================================================

class PVTP012_IrradianceLevel(BaseModel):
    """Measurement at single irradiance level"""
    level_id: str
    target_irradiance: float = Field(..., gt=0, le=1500)
    irradiance_measured: float = Field(..., gt=0, le=1500)
    module_temperature: float = Field(..., ge=-40, le=90)
    voc: float = Field(..., gt=0)
    isc: float = Field(..., gt=0)
    pmax: float = Field(..., gt=0)
    vmpp: float = Field(..., gt=0)
    impp: float = Field(..., gt=0)
    fill_factor: Optional[float] = Field(None, ge=0, le=1)


class PVTP012_LowLightMetrics(BaseModel):
    """Low light performance metrics"""
    relative_efficiency_at_800: Optional[float] = Field(None, ge=0, le=2)
    relative_efficiency_at_500: Optional[float] = Field(None, ge=0, le=2)
    relative_efficiency_at_200: Optional[float] = Field(None, ge=0, le=2)
    weak_light_response_factor: float = Field(..., ge=0, le=2, description="WLRF")
    current_linearity_r_squared: float = Field(..., ge=0.9, le=1)

    @validator('weak_light_response_factor')
    def wlrf_quality(cls, v):
        if v < 0.9:
            pass  # Warning: poor low light performance
        return v


class PVTP012_Input(SampleInfoBase):
    """Input for PVTP-012"""
    bifacial: bool = False
    bifaciality_factor: Optional[float] = Field(None, ge=0, le=1)
    module_area_front: Optional[float] = Field(None, gt=0)


class PVTP012_Measurement(BaseModel):
    """Measurements for PVTP-012"""
    irradiance_levels: List[PVTP012_IrradianceLevel] = Field(..., min_items=3)

    @validator('irradiance_levels')
    def check_required_levels(cls, v):
        """Ensure standard levels are measured"""
        measured = {level.target_irradiance for level in v}
        required = {1000, 500, 200}
        if not required.issubset({int(m) for m in measured}):
            raise ValueError(f'Must include measurements at 1000, 500, and 200 W/m²')
        return v


class PVTP012_Analysis(BaseModel):
    """Analysis for PVTP-012"""
    low_light_metrics: PVTP012_LowLightMetrics


class PVTP012_Complete(BaseModel):
    """Complete PVTP-012 test data"""
    inputs: PVTP012_Input
    measurements: PVTP012_Measurement
    analysis: PVTP012_Analysis


# ============================================================================
# PVTP-013: Temperature Coefficient
# ============================================================================

class PVTP013_TemperaturePoint(BaseModel):
    """Measurement at single temperature"""
    target_temperature: float = Field(..., ge=-40, le=90)
    module_temperature_measured: float = Field(..., ge=-40, le=90)
    irradiance_measured: float = Field(..., ge=900, le=1100)
    voc: float = Field(..., gt=0)
    isc: float = Field(..., gt=0)
    pmax: float = Field(..., gt=0)
    vmpp: float = Field(..., gt=0)
    impp: float = Field(..., gt=0)
    fill_factor: Optional[float] = None
    temperature_uniformity: Optional[float] = Field(None, description="°C std dev")


class PVTP013_Coefficients(BaseModel):
    """Temperature coefficients"""
    alpha_isc_absolute: float = Field(..., description="A/°C")
    alpha_isc_relative: float = Field(..., description="%/°C")
    beta_voc_absolute: float = Field(..., description="V/°C")
    beta_voc_relative: float = Field(..., description="%/°C")
    gamma_pmax_absolute: float = Field(..., description="W/°C")
    gamma_pmax_relative: float = Field(..., description="%/°C")

    # Fit quality
    alpha_r_squared: float = Field(..., ge=0.95, le=1)
    beta_r_squared: float = Field(..., ge=0.95, le=1)
    gamma_r_squared: float = Field(..., ge=0.95, le=1)

    @validator('gamma_pmax_relative')
    def gamma_typical_range(cls, v):
        """Check if gamma is in typical range for silicon"""
        if not (-0.7 <= v <= -0.2):
            pass  # Warning: outside typical range
        return v


class PVTP013_Input(SampleInfoBase):
    """Input for PVTP-013"""
    test_method: str = Field("Indoor (Climate Chamber)")
    datasheet_alpha: Optional[float] = None
    datasheet_beta: Optional[float] = None
    datasheet_gamma: Optional[float] = None


class PVTP013_Measurement(BaseModel):
    """Measurements for PVTP-013"""
    temperature_points: List[PVTP013_TemperaturePoint] = Field(..., min_items=5)

    @validator('temperature_points')
    def check_temperature_range(cls, v):
        """Ensure adequate temperature range"""
        temps = [p.module_temperature_measured for p in v]
        temp_range = max(temps) - min(temps)
        if temp_range < 30:
            raise ValueError(f'Temperature range ({temp_range}°C) too small, need ≥30°C')
        return v


class PVTP013_Analysis(BaseModel):
    """Analysis for PVTP-013"""
    coefficients: PVTP013_Coefficients


class PVTP013_Complete(BaseModel):
    """Complete PVTP-013 test data"""
    inputs: PVTP013_Input
    measurements: PVTP013_Measurement
    analysis: PVTP013_Analysis


# ============================================================================
# PVTP-014: Spectral Response
# ============================================================================

class PVTP014_SpectralPoint(BaseModel):
    """Single wavelength measurement"""
    wavelength: float = Field(..., ge=250, le=2500, description="nm")
    incident_power: float = Field(..., gt=0, description="W")
    photocurrent: float = Field(..., ge=0, description="A")
    spectral_response: Optional[float] = Field(None, description="A/W")
    eqe: Optional[float] = Field(None, ge=0, le=100, description="%")

    @validator('spectral_response', always=True)
    def calc_sr(cls, v, values):
        if v is None and 'photocurrent' in values and 'incident_power' in values:
            if values['incident_power'] > 0:
                return values['photocurrent'] / values['incident_power']
        return v


class PVTP014_SpectralMetrics(BaseModel):
    """Spectral response metrics"""
    peak_eqe: float = Field(..., ge=0, le=100, description="%")
    peak_eqe_wavelength: float = Field(..., ge=250, le=2500, description="nm")
    integrated_jsc: float = Field(..., gt=0, description="mA/cm²")
    blue_response: float = Field(..., ge=0, le=100, description="avg EQE 400-500nm")
    red_response: float = Field(..., ge=0, le=100, description="avg EQE 700-900nm")
    band_edge_wavelength: Optional[float] = Field(None, description="nm")


class PVTP014_Input(SampleInfoBase):
    """Input for PVTP-014"""
    sample_type: str = Field("Full Module")
    measurement_type: str = Field("EQE + IQE")
    cell_area: Optional[float] = Field(None, gt=0, description="cm²")
    bias_light_required: bool = True


class PVTP014_Measurement(BaseModel):
    """Measurements for PVTP-014"""
    wavelength_range: Dict[str, float]  # min, max, step
    spectral_data: List[PVTP014_SpectralPoint] = Field(..., min_items=30)
    reflectance_data: Optional[List[Dict[str, float]]] = None


class PVTP014_Analysis(BaseModel):
    """Analysis for PVTP-014"""
    spectral_metrics: PVTP014_SpectralMetrics


class PVTP014_Complete(BaseModel):
    """Complete PVTP-014 test data"""
    inputs: PVTP014_Input
    measurements: PVTP014_Measurement
    analysis: PVTP014_Analysis


# ============================================================================
# PVTP-015: Dark I-V Analysis
# ============================================================================

class PVTP015_DiodeParameters(BaseModel):
    """Extracted diode parameters"""
    saturation_current: float = Field(..., gt=0, description="I0 (A)")
    ideality_factor: float = Field(..., ge=0.5, le=5, description="n")
    series_resistance: float = Field(..., ge=0, description="Rs (Ohm)")
    shunt_resistance: float = Field(..., gt=0, description="Rsh (Ohm)")
    r_squared: float = Field(..., ge=0.99, le=1, description="Fit quality")

    @validator('ideality_factor')
    def ideality_interpretation(cls, v):
        """Check ideality factor range"""
        if not (1 <= v <= 2.5):
            pass  # Warning: unusual ideality factor
        return v


class PVTP015_DefectAnalysis(BaseModel):
    """Defect identification"""
    breakdown_detected: bool = False
    breakdown_voltage: Optional[float] = None
    shunt_type: Optional[str] = Field(None, regex="^(ohmic|non_ohmic|junction)$")
    defect_classification: Optional[str] = None


class PVTP015_Input(SampleInfoBase):
    """Input for PVTP-015"""
    sample_type: str = Field("Full Module")
    test_mode: str = Field("Full Range (Forward + Reverse)")
    expected_voc: Optional[float] = Field(None, gt=0)
    defect_analysis: bool = True


class PVTP015_Measurement(BaseModel):
    """Measurements for PVTP-015"""
    test_conditions: TestConditions
    forward_bias_data: List[IVDataPoint] = Field(..., min_items=50)
    reverse_bias_data: Optional[List[IVDataPoint]] = None


class PVTP015_Analysis(BaseModel):
    """Analysis for PVTP-015"""
    diode_parameters: PVTP015_DiodeParameters
    defect_analysis: Optional[PVTP015_DefectAnalysis] = None


class PVTP015_Complete(BaseModel):
    """Complete PVTP-015 test data"""
    inputs: PVTP015_Input
    measurements: PVTP015_Measurement
    analysis: PVTP015_Analysis
