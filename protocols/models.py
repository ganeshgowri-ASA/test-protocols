"""
Data models for PV testing protocols using Pydantic.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class ProtocolType(str, Enum):
    """Protocol type enumeration."""
    INSPECTION = "inspection"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    THERMAL = "thermal"
    ENVIRONMENTAL = "environmental"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SAFETY = "safety"
    CALIBRATION = "calibration"
    CHARACTERIZATION = "characterization"


class ProtocolStatus(str, Enum):
    """Protocol execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MeasurementStatus(str, Enum):
    """Measurement status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"


class Measurement(BaseModel):
    """Individual measurement data point."""
    measurement_id: str
    parameter: str = Field(description="Name of the measured parameter")
    value: Union[float, str, bool] = Field(description="Measured value")
    unit: str = Field(description="Unit of measurement")
    uncertainty: Optional[float] = Field(None, description="Measurement uncertainty")
    timestamp: Optional[datetime] = None
    status: Optional[MeasurementStatus] = None
    conditions: Optional[Dict[str, Any]] = Field(None, description="Test conditions")

    class Config:
        use_enum_values = True


class Metadata(BaseModel):
    """Protocol metadata."""
    timestamp: Optional[datetime] = None
    operator: Optional[str] = None
    facility: Optional[str] = None
    equipment: Optional[List[str]] = None


class Protocol(BaseModel):
    """Base protocol data model."""
    protocol_id: str = Field(pattern=r"^[A-Z0-9-]+$")
    protocol_name: str = Field(min_length=3, max_length=200)
    protocol_type: ProtocolType
    version: str = Field(pattern=r"^\d+\.\d+(\.\d+)?$")
    standard: Optional[str] = None
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    measurements: List[Measurement] = Field(default_factory=list)
    acceptance_criteria: Optional[Dict[str, Any]] = None
    metadata: Optional[Metadata] = None
    status: ProtocolStatus = ProtocolStatus.PENDING

    class Config:
        use_enum_values = True

    @validator("version")
    def validate_version(cls, v):
        """Validate semantic version format."""
        parts = v.split(".")
        if len(parts) < 2 or len(parts) > 3:
            raise ValueError("Version must be in format X.Y or X.Y.Z")
        if not all(part.isdigit() for part in parts):
            raise ValueError("Version parts must be numeric")
        return v


class ElectricalProtocol(Protocol):
    """Electrical test protocol model."""
    protocol_type: ProtocolType = ProtocolType.ELECTRICAL

    @validator("parameters")
    def validate_electrical_parameters(cls, v):
        """Validate required electrical parameters."""
        required = ["module_id", "test_type"]
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required parameter: {field}")
        return v


class ThermalProtocol(Protocol):
    """Thermal test protocol model."""
    protocol_type: ProtocolType = ProtocolType.THERMAL

    @validator("parameters")
    def validate_thermal_parameters(cls, v):
        """Validate required thermal parameters."""
        required = ["module_id", "test_type"]
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required parameter: {field}")
        return v


class MechanicalProtocol(Protocol):
    """Mechanical test protocol model."""
    protocol_type: ProtocolType = ProtocolType.MECHANICAL

    @validator("parameters")
    def validate_mechanical_parameters(cls, v):
        """Validate required mechanical parameters."""
        required = ["module_id", "test_type"]
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required parameter: {field}")
        return v


class ProtocolResult(BaseModel):
    """Protocol execution result."""
    protocol_id: str
    status: ProtocolStatus
    passed: bool
    measurements: List[Measurement] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    completed_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
