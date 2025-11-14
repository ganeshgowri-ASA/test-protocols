"""Data models for test results and sessions."""

from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum

from .protocol import TestStage, MeasurementType


class TestStatus(str, Enum):
    """Test session status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PassFailStatus(str, Enum):
    """Pass/fail status for test results."""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    NOT_EVALUATED = "not_evaluated"


class Sample(BaseModel):
    """Sample/specimen information."""
    sample_id: str
    sample_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)


class MeasurementData(BaseModel):
    """Individual measurement data."""
    measurement_id: str
    measurement_name: str
    measurement_type: MeasurementType
    stage: TestStage
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Any
    unit: Optional[str] = None
    operator: Optional[str] = None
    notes: Optional[str] = None


class QCCheckResult(BaseModel):
    """Quality control check result."""
    check_id: str
    check_name: str
    stage: TestStage
    result: PassFailStatus
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    performed_by: Optional[str] = None


class CriterionEvaluation(BaseModel):
    """Evaluation of a single pass criterion."""
    criterion_name: str
    status: PassFailStatus
    measured_value: Optional[float] = None
    limit_value: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class TestSession(BaseModel):
    """Test session information."""
    session_id: UUID = Field(default_factory=uuid4)
    protocol_id: str
    protocol_version: str
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: TestStatus = TestStatus.PENDING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    samples: List[Sample] = Field(default_factory=list)
    measurements: List[MeasurementData] = Field(default_factory=list)
    qc_checks: List[QCCheckResult] = Field(default_factory=list)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def add_measurement(self, measurement: MeasurementData):
        """Add a measurement to the session."""
        self.measurements.append(measurement)

    def add_qc_check(self, qc_check: QCCheckResult):
        """Add a QC check result to the session."""
        self.qc_checks.append(qc_check)

    def get_measurements_by_stage(self, stage: TestStage) -> List[MeasurementData]:
        """Get all measurements for a specific stage."""
        return [m for m in self.measurements if m.stage == stage]

    def get_measurement_by_id(self, measurement_id: str) -> Optional[MeasurementData]:
        """Get a specific measurement by ID."""
        for measurement in self.measurements:
            if measurement.measurement_id == measurement_id:
                return measurement
        return None

    def complete_session(self):
        """Mark session as completed."""
        self.status = TestStatus.COMPLETED
        self.end_time = datetime.now()

    def fail_session(self):
        """Mark session as failed."""
        self.status = TestStatus.FAILED
        self.end_time = datetime.now()


class TestResult(BaseModel):
    """Complete test result including evaluation."""
    session: TestSession
    overall_status: PassFailStatus = PassFailStatus.NOT_EVALUATED
    criterion_evaluations: List[CriterionEvaluation] = Field(default_factory=list)
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    report_paths: Optional[Dict[str, str]] = None
    evaluated_at: Optional[datetime] = None
    evaluated_by: Optional[str] = None

    def add_criterion_evaluation(self, evaluation: CriterionEvaluation):
        """Add a criterion evaluation."""
        self.criterion_evaluations.append(evaluation)

    def evaluate_overall_status(self):
        """Determine overall pass/fail status based on criterion evaluations."""
        if not self.criterion_evaluations:
            self.overall_status = PassFailStatus.NOT_EVALUATED
            return

        # If any criterion fails, overall status is fail
        if any(e.status == PassFailStatus.FAIL for e in self.criterion_evaluations):
            self.overall_status = PassFailStatus.FAIL
        # If any criterion is conditional pass, overall is conditional
        elif any(e.status == PassFailStatus.CONDITIONAL_PASS for e in self.criterion_evaluations):
            self.overall_status = PassFailStatus.CONDITIONAL_PASS
        # All criteria pass
        else:
            self.overall_status = PassFailStatus.PASS

        self.evaluated_at = datetime.now()

    def get_failed_criteria(self) -> List[CriterionEvaluation]:
        """Get all failed criteria."""
        return [e for e in self.criterion_evaluations if e.status == PassFailStatus.FAIL]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for the test result."""
        return {
            "total_criteria": len(self.criterion_evaluations),
            "passed": sum(1 for e in self.criterion_evaluations if e.status == PassFailStatus.PASS),
            "failed": sum(1 for e in self.criterion_evaluations if e.status == PassFailStatus.FAIL),
            "conditional": sum(1 for e in self.criterion_evaluations if e.status == PassFailStatus.CONDITIONAL_PASS),
            "overall_status": self.overall_status.value,
            "test_duration_minutes": (
                (self.session.end_time - self.session.start_time).total_seconds() / 60
                if self.session.end_time
                else None
            )
        }
