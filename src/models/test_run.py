"""Test run models for storing test execution data."""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Integer, String, Text, Float, Boolean, DateTime, JSON,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Any

from .base import Base, TimestampMixin


class TestStatus(str, Enum):
    """Enumeration of possible test statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestResult(str, Enum):
    """Enumeration of possible test results."""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    NOT_EVALUATED = "not_evaluated"


class TestRun(Base, TimestampMixin):
    """Model representing a single execution of a test protocol.

    A test run tracks the execution of a protocol on a specific specimen,
    including all measurements, observations, and final results.
    """

    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Protocol reference
    protocol_id: Mapped[int] = mapped_column(Integer, ForeignKey("protocols.id"), nullable=False)
    protocol: Mapped["Protocol"] = relationship("Protocol", back_populates="test_runs")

    # Specimen information
    specimen_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specimen_description: Mapped[Optional[str]] = mapped_column(Text)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model_number: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Test execution
    status: Mapped[TestStatus] = mapped_column(
        SQLEnum(TestStatus),
        default=TestStatus.PENDING,
        nullable=False
    )
    result: Mapped[TestResult] = mapped_column(
        SQLEnum(TestResult),
        default=TestResult.NOT_EVALUATED,
        nullable=False
    )

    # Operator and facility
    operator_name: Mapped[Optional[str]] = mapped_column(String(100))
    facility: Mapped[Optional[str]] = mapped_column(String(100))
    test_station: Mapped[Optional[str]] = mapped_column(String(50))

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Environmental conditions
    ambient_temperature: Mapped[Optional[float]] = mapped_column(Float)
    ambient_humidity: Mapped[Optional[float]] = mapped_column(Float)

    # Additional metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    attachments: Mapped[Optional[dict]] = mapped_column(JSON)  # Store file references

    # Relationships
    test_steps: Mapped[List["TestStep"]] = relationship(
        "TestStep",
        back_populates="test_run",
        cascade="all, delete-orphan",
        order_by="TestStep.step_number"
    )
    measurements: Mapped[List["Measurement"]] = relationship(
        "Measurement",
        back_populates="test_run",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of TestRun."""
        return f"<TestRun(id={self.id}, run_id='{self.run_id}', status='{self.status.value}')>"

    def to_dict(self) -> dict:
        """Convert test run to dictionary format.

        Returns:
            Dictionary representation of the test run.
        """
        return {
            "id": self.id,
            "run_id": self.run_id,
            "protocol_id": self.protocol_id,
            "specimen_id": self.specimen_id,
            "specimen_description": self.specimen_description,
            "manufacturer": self.manufacturer,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "status": self.status.value,
            "result": self.result.value,
            "operator_name": self.operator_name,
            "facility": self.facility,
            "test_station": self.test_station,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "ambient_temperature": self.ambient_temperature,
            "ambient_humidity": self.ambient_humidity,
            "notes": self.notes,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TestStep(Base, TimestampMixin):
    """Model representing the execution of a single test step."""

    __tablename__ = "test_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Test run reference
    test_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_runs.id"), nullable=False)
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="test_steps")

    # Step information
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    # Execution
    status: Mapped[TestStatus] = mapped_column(
        SQLEnum(TestStatus),
        default=TestStatus.PENDING,
        nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Results
    observations: Mapped[Optional[str]] = mapped_column(Text)
    step_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Store step-specific data
    pass_fail: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        """String representation of TestStep."""
        return f"<TestStep(id={self.id}, step_number={self.step_number}, status='{self.status.value}')>"

    def to_dict(self) -> dict:
        """Convert test step to dictionary format.

        Returns:
            Dictionary representation of the test step.
        """
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "step_number": self.step_number,
            "description": self.description,
            "action": self.action,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "observations": self.observations,
            "step_data": self.step_data,
            "pass_fail": self.pass_fail,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Measurement(Base, TimestampMixin):
    """Model representing a single measurement or data point."""

    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Test run reference
    test_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_runs.id"), nullable=False)
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="measurements")

    # Measurement identification
    measurement_id: Mapped[str] = mapped_column(String(50), nullable=False)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

    # Measurement values
    value_numeric: Mapped[Optional[float]] = mapped_column(Float)
    value_text: Mapped[Optional[str]] = mapped_column(String(500))
    value_boolean: Mapped[Optional[bool]] = mapped_column(Boolean)
    value_json: Mapped[Optional[dict]] = mapped_column(JSON)  # For arrays or complex data

    # Measurement context
    measurement_type: Mapped[str] = mapped_column(String(50))  # pre_test, during_test, post_test
    instrument: Mapped[Optional[str]] = mapped_column(String(100))
    accuracy: Mapped[Optional[str]] = mapped_column(String(50))

    # Timing
    measured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Quality flags
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        """String representation of Measurement."""
        return f"<Measurement(id={self.id}, parameter='{self.parameter}', value={self.value_numeric})>"

    def to_dict(self) -> dict:
        """Convert measurement to dictionary format.

        Returns:
            Dictionary representation of the measurement.
        """
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "measurement_id": self.measurement_id,
            "parameter": self.parameter,
            "unit": self.unit,
            "value_numeric": self.value_numeric,
            "value_text": self.value_text,
            "value_boolean": self.value_boolean,
            "value_json": self.value_json,
            "measurement_type": self.measurement_type,
            "instrument": self.instrument,
            "accuracy": self.accuracy,
            "measured_at": self.measured_at.isoformat(),
            "is_valid": self.is_valid,
            "validation_notes": self.validation_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
