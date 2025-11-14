"""
Base Pydantic models for data validation
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


class TechnologyType(str, Enum):
    """PV cell technology types"""
    MONO_SI = "mono-Si"
    MULTI_SI = "multi-Si"
    PERC = "PERC"
    HJT = "HJT"
    TOPCON = "TOPCon"
    IBC = "IBC"
    CDTE = "CdTe"
    CIGS = "CIGS"
    A_SI = "a-Si"
    PEROVSKITE = "Perovskite"
    MULTI_JUNCTION = "Multi-junction"
    III_V = "III-V"
    OTHER = "Other"


class TestStatusEnum(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"


class QCStatusEnum(str, Enum):
    """QC check status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_CHECKED = "not_checked"


class SampleInfoBase(BaseModel):
    """Base sample information"""
    sample_id: str = Field(..., min_length=5, max_length=50, description="Unique sample identifier")
    manufacturer: str = Field(..., min_length=1, max_length=200)
    model: str = Field(..., min_length=1, max_length=200)
    serial_number: str = Field(..., min_length=1, max_length=200)
    technology: TechnologyType
    test_date: date = Field(default_factory=date.today)
    operator: str = Field(..., min_length=1, max_length=100)

    project_id: Optional[str] = Field(None, max_length=100)
    customer: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    class Config:
        use_enum_values = True


class MeasurementBase(BaseModel):
    """Base measurement data"""
    value: float
    unit: str
    uncertainty: Optional[float] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('value')
    def value_must_be_finite(cls, v):
        if not (-1e308 < v < 1e308):  # Check for inf/nan
            raise ValueError('Value must be finite')
        return v


class IVDataPoint(BaseModel):
    """Single I-V curve data point"""
    voltage: float = Field(..., description="Voltage in V")
    current: float = Field(..., description="Current in A")
    power: Optional[float] = Field(None, description="Power in W (calculated)")

    @validator('power', always=True)
    def calculate_power(cls, v, values):
        if v is None and 'voltage' in values and 'current' in values:
            return values['voltage'] * values['current']
        return v


class IVCurveData(BaseModel):
    """Complete I-V curve data"""
    data_points: List[IVDataPoint] = Field(..., min_items=50, max_items=5000)
    sweep_direction: Optional[str] = Field("Reverse (Voc→0)")
    sweep_rate: Optional[float] = Field(None, description="V/s")

    @validator('data_points')
    def check_monotonic_voltage(cls, v):
        """Ensure voltage is monotonic"""
        voltages = [p.voltage for p in v]
        # Check if strictly increasing or decreasing
        is_increasing = all(voltages[i] < voltages[i+1] for i in range(len(voltages)-1))
        is_decreasing = all(voltages[i] > voltages[i+1] for i in range(len(voltages)-1))
        if not (is_increasing or is_decreasing):
            raise ValueError('Voltage values must be monotonic')
        return v


class ElectricalParameters(BaseModel):
    """Standard electrical parameters"""
    voc: float = Field(..., gt=0, description="Open circuit voltage (V)")
    isc: float = Field(..., gt=0, description="Short circuit current (A)")
    pmax: float = Field(..., gt=0, description="Maximum power (W)")
    vmpp: float = Field(..., gt=0, description="Voltage at MPP (V)")
    impp: float = Field(..., gt=0, description="Current at MPP (A)")
    fill_factor: float = Field(..., ge=0, le=1, description="Fill factor")
    efficiency: Optional[float] = Field(None, ge=0, le=100, description="Efficiency (%)")

    @validator('fill_factor', always=True)
    def calculate_fill_factor(cls, v, values):
        """Calculate fill factor if not provided"""
        if v is None and all(k in values for k in ['voc', 'isc', 'pmax']):
            voc_isc = values['voc'] * values['isc']
            if voc_isc > 0:
                return values['pmax'] / voc_isc
        return v

    @validator('pmax')
    def check_pmax_consistency(cls, v, values):
        """Verify Pmax = Vmpp * Impp"""
        if 'vmpp' in values and 'impp' in values:
            calculated_pmax = values['vmpp'] * values['impp']
            if abs(v - calculated_pmax) / v > 0.01:  # 1% tolerance
                raise ValueError(f'Pmax ({v}W) inconsistent with Vmpp * Impp ({calculated_pmax}W)')
        return v


class TestConditions(BaseModel):
    """Standard test conditions"""
    irradiance: float = Field(..., gt=0, le=2000, description="Irradiance (W/m²)")
    module_temperature: float = Field(..., ge=-40, le=90, description="Module temperature (°C)")
    ambient_temperature: Optional[float] = Field(None, ge=-20, le=50)
    spectrum: Optional[str] = Field("AM1.5G")

    @validator('module_temperature')
    def temperature_reasonable(cls, v):
        """Warn if temperature is far from STC"""
        if not (15 <= v <= 35):
            # This is a warning, not an error - still allow it
            pass
        return v


class QCCheck(BaseModel):
    """QC check result"""
    check_id: str
    parameter: str
    condition: str
    threshold: Optional[float] = None
    measured_value: Optional[float] = None
    status: QCStatusEnum
    severity: str = Field(..., regex="^(critical|major|warning|info)$")
    message: Optional[str] = None
    action_taken: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class UncertaintyBudget(BaseModel):
    """Measurement uncertainty component"""
    source: str
    uncertainty_type: str = Field(..., regex="^(A|B)$")  # Type A or Type B
    relative_uncertainty: float = Field(..., ge=0, le=1)
    sensitivity: Optional[str] = None


class TestExecutionCreate(BaseModel):
    """Create new test execution"""
    protocol_id: str = Field(..., description="Protocol ID (e.g., PVTP-010)")
    sample_id: str = Field(..., min_length=5)
    operator: str = Field(..., min_length=1)
    test_date: date = Field(default_factory=date.today)
    project_id: Optional[str] = None
    customer: Optional[str] = None


class TestExecutionUpdate(BaseModel):
    """Update test execution"""
    status: Optional[TestStatusEnum] = None
    qc_status: Optional[QCStatusEnum] = None
    input_data: Optional[Dict[str, Any]] = None
    measurement_data: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None
    qc_checks: Optional[List[QCCheck]] = None
    notes: Optional[str] = None
    review_comments: Optional[str] = None

    class Config:
        use_enum_values = True


class TestExecutionResponse(BaseModel):
    """Test execution response"""
    id: int
    execution_id: str
    protocol_id: int
    sample_id: str
    operator: str
    test_date: date
    status: TestStatusEnum
    qc_status: QCStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class ReportGenerate(BaseModel):
    """Request to generate a report"""
    test_execution_id: int
    report_type: str = Field(..., regex="^(test_report|certificate|data_export)$")
    format: str = Field(..., regex="^(PDF|Excel|CSV)$")
    include_charts: bool = True
    include_raw_data: bool = False


class NonconformanceCreate(BaseModel):
    """Create nonconformance record"""
    test_execution_id: Optional[int] = None
    category: str
    severity: str = Field(..., regex="^(critical|major|minor)$")
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=20)
    opened_by: str


class NonconformanceUpdate(BaseModel):
    """Update nonconformance record"""
    status: Optional[str] = Field(None, regex="^(open|investigating|resolved|closed)$")
    assigned_to: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    preventive_actions: Optional[str] = None
    verified_by: Optional[str] = None
    verification_notes: Optional[str] = None
