"""Data models for test protocols."""

from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ParameterType(str, Enum):
    """Parameter type enumeration."""
    NUMERIC = "numeric"
    RANGE = "range"
    SELECT = "select"
    BOOLEAN = "boolean"
    OBJECT = "object"


class TestStage(str, Enum):
    """Test stage enumeration."""
    PRE_TEST = "pre_test"
    DURING_TEST = "during_test"
    POST_TEST = "post_test"


class MeasurementType(str, Enum):
    """Measurement type enumeration."""
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    TIME_SERIES = "time_series"


class TestCategory(str, Enum):
    """Test category enumeration."""
    MECHANICAL = "mechanical"
    ENVIRONMENTAL = "environmental"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    COMBINED = "combined"


class SeverityLevel(str, Enum):
    """Test severity level enumeration."""
    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"
    EXTREME = "extreme"


class ComparisonOperator(str, Enum):
    """Comparison operator for pass criteria."""
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"


class ProtocolMetadata(BaseModel):
    """Protocol metadata."""
    description: str
    applicable_products: List[str]
    severity_level: Optional[SeverityLevel] = None
    estimated_duration_hours: Optional[float] = None
    required_equipment: Optional[List[str]] = None
    safety_notes: Optional[List[str]] = None


class Parameter(BaseModel):
    """Test parameter definition."""
    type: ParameterType
    unit: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Any]] = None


class SampleSize(BaseModel):
    """Sample size requirements."""
    min: int = Field(ge=1)
    recommended: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None


class Conditioning(BaseModel):
    """Sample conditioning requirements."""
    temperature: Optional[Dict[str, Any]] = None
    relative_humidity: Optional[Dict[str, Any]] = None
    duration_hours: Optional[float] = None
    description: Optional[str] = None


class SampleRequirements(BaseModel):
    """Sample requirements."""
    sample_size: SampleSize
    conditioning: Optional[Conditioning] = None
    mounting: Optional[Dict[str, Any]] = None


class TestStep(BaseModel):
    """Test sequence step."""
    step: int = Field(ge=1)
    name: str
    description: str
    duration_minutes: Optional[float] = None
    duration_hours: Optional[float] = None


class MeasurementDefinition(BaseModel):
    """Measurement definition."""
    id: str
    name: str
    type: MeasurementType
    stage: TestStage
    required: bool
    checklist: Optional[List[str]] = None
    measurements: Optional[List[Dict[str, Any]]] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    sampling_rate_hz: Optional[float] = None


class PassCriterion(BaseModel):
    """Pass/fail criterion."""
    min: Optional[float] = None
    max: Optional[float] = None
    unit: Optional[str] = None
    comparison: Optional[ComparisonOperator] = None
    description: Optional[str] = None
    critical_defects: Optional[List[str]] = None
    allowed_critical_defects: Optional[int] = None


class ChartDefinition(BaseModel):
    """Chart definition for reporting."""
    name: str
    type: Literal["line", "bar", "scatter", "heatmap", "time_series", "histogram"]
    description: Optional[str] = None


class ReportingRequirements(BaseModel):
    """Reporting requirements."""
    required_charts: List[ChartDefinition]
    required_sections: List[str]
    templates: Optional[Dict[str, str]] = None


class QualityControl(BaseModel):
    """Quality control check."""
    id: str
    name: str
    stage: TestStage
    description: str
    required: bool


class Reference(BaseModel):
    """Reference standard or document."""
    standard: str
    title: str
    section: Optional[str] = None


class Protocol(BaseModel):
    """Complete test protocol definition."""
    id: str = Field(pattern=r"^[A-Z]+-[0-9]{3}$")
    name: str
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    standard: str
    category: TestCategory
    test_type: str
    metadata: ProtocolMetadata
    parameters: Dict[str, Parameter]
    sample_requirements: SampleRequirements
    test_sequence: Optional[List[TestStep]] = None
    measurements: List[MeasurementDefinition]
    pass_criteria: Dict[str, PassCriterion]
    reporting: ReportingRequirements
    quality_controls: Optional[List[QualityControl]] = None
    references: Optional[List[Reference]] = None

    @validator('id')
    def validate_id_format(cls, v):
        """Validate protocol ID format."""
        if not v or len(v) < 5:
            raise ValueError("Protocol ID must be in format XXX-NNN")
        return v

    def get_measurement_by_id(self, measurement_id: str) -> Optional[MeasurementDefinition]:
        """Get measurement definition by ID."""
        for measurement in self.measurements:
            if measurement.id == measurement_id:
                return measurement
        return None

    def get_measurements_by_stage(self, stage: TestStage) -> List[MeasurementDefinition]:
        """Get all measurements for a specific stage."""
        return [m for m in self.measurements if m.stage == stage]

    def validate_parameters(self, input_params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input parameters against protocol requirements.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for param_name, param_def in self.parameters.items():
            if param_name not in input_params:
                continue

            value = input_params[param_name]

            # Validate numeric parameters
            if param_def.type == ParameterType.NUMERIC:
                if param_def.min is not None and value < param_def.min:
                    errors.append(
                        f"{param_name} ({value}) is below minimum ({param_def.min})"
                    )
                if param_def.max is not None and value > param_def.max:
                    errors.append(
                        f"{param_name} ({value}) exceeds maximum ({param_def.max})"
                    )

            # Validate select parameters
            elif param_def.type == ParameterType.SELECT:
                if param_def.options and value not in param_def.options:
                    errors.append(
                        f"{param_name} ({value}) is not in valid options: {param_def.options}"
                    )

        return len(errors) == 0, errors


class ProtocolWrapper(BaseModel):
    """Wrapper for protocol JSON structure."""
    protocol: Protocol
