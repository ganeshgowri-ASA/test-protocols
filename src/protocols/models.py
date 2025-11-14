"""Pydantic models for protocol data validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MeasurementType(str, Enum):
    """Types of measurements that can be recorded."""

    NUMBER = "number"
    TEXT = "text"
    BOOLEAN = "boolean"
    SELECT = "select"


class ConditionType(str, Enum):
    """Types of acceptance criteria conditions."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"


class TestResult(str, Enum):
    """Possible test result statuses."""

    PASS = "Pass"
    FAIL = "Fail"
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"


class TestCondition(BaseModel):
    """Model for test conditions."""

    value: Union[int, float, str]
    unit: str
    tolerance: Optional[Union[int, float]] = None
    required: bool = True


class Equipment(BaseModel):
    """Model for test equipment."""

    name: str
    specification: str
    calibration_required: bool = False
    calibration_date: Optional[datetime] = None
    calibration_due_date: Optional[datetime] = None


class Measurement(BaseModel):
    """Model for a measurement definition."""

    name: str
    type: MeasurementType
    unit: Optional[str] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    options: Optional[List[str]] = None
    required: bool = True
    calculated: bool = False
    formula: Optional[str] = None


class AcceptanceCriterion(BaseModel):
    """Model for acceptance criteria."""

    parameter: str
    condition: ConditionType
    value: Union[int, float, str, bool]


class ProtocolStepData(BaseModel):
    """Model for protocol step data."""

    step_number: int
    name: str
    description: str
    duration: int
    duration_unit: str
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    measurements: List[Measurement]
    acceptance_criteria: List[AcceptanceCriterion]


class QCCheck(BaseModel):
    """Model for QC check."""

    name: str
    description: str
    required: bool = True
    frequency: str
    completed: bool = False
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None


class Protocol(BaseModel):
    """Complete protocol definition model."""

    protocol_id: str
    version: str
    title: str
    category: str
    description: str
    applicable_standards: List[str] = Field(default_factory=list)
    test_conditions: Dict[str, TestCondition] = Field(default_factory=dict)
    test_equipment: List[Equipment] = Field(default_factory=list)
    test_steps: List[ProtocolStepData]
    qc_checks: List[QCCheck] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class TestExecution(BaseModel):
    """Model for a test execution instance."""

    test_id: str
    protocol_id: str
    protocol_version: str
    module_serial_number: str
    operator: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: TestResult = TestResult.NOT_STARTED
    current_step: int = 0
    test_conditions_actual: Dict[str, Any] = Field(default_factory=dict)
    equipment_used: List[Dict[str, Any]] = Field(default_factory=list)
    step_results: List[Dict[str, Any]] = Field(default_factory=list)
    qc_results: List[Dict[str, Any]] = Field(default_factory=list)
    overall_result: Optional[TestResult] = None
    notes: Optional[str] = None

    class Config:
        use_enum_values = True


class QCResult(BaseModel):
    """Model for QC check results."""

    check_name: str
    passed: bool
    performed_by: str
    performed_at: datetime
    notes: Optional[str] = None

    class Config:
        use_enum_values = True
