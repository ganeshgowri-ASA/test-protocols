"""
Test execution, measurement, and result models
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    ForeignKey, Boolean, JSON, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import Base


class TestStatus(PyEnum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestOutcome(PyEnum):
    """Test result outcome"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    NOT_TESTED = "not_tested"


class TestExecution(Base):
    """
    Individual test execution record
    """
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    test_number = Column(String(50), unique=True, nullable=False, index=True)

    # Protocol reference
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)

    # Sample reference
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)

    # Test timing
    scheduled_start = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    duration_seconds = Column(Float)

    # Status
    status = Column(Enum(TestStatus), default=TestStatus.PENDING, nullable=False)
    outcome = Column(Enum(TestOutcome))

    # Operator and equipment
    operator_id = Column(String(100), nullable=False)
    operator_name = Column(String(255))
    equipment_id = Column(Integer, ForeignKey("equipment.id"))

    # Environmental conditions
    ambient_temperature = Column(Float)
    relative_humidity = Column(Float)
    atmospheric_pressure = Column(Float)

    # Test parameters (stored as JSON)
    parameters = Column(JSON)

    # Notes and observations
    pre_test_notes = Column(Text)
    post_test_notes = Column(Text)
    anomalies = Column(Text)

    # QC flags
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_executions")
    sample = relationship("Sample", back_populates="test_executions")
    equipment = relationship("Equipment", back_populates="test_executions")
    measurements = relationship("TestMeasurement", back_populates="test_execution", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution(test_number='{self.test_number}', status='{self.status.value}')>"


class TestMeasurement(Base):
    """
    Individual measurements taken during a test
    """
    __tablename__ = "test_measurements"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)

    # Measurement identification
    measurement_name = Column(String(100), nullable=False)
    measurement_point = Column(String(100))  # e.g., "Point 1", "Frame to Junction Box"
    sequence_number = Column(Integer)  # Order of measurement in test

    # Measurement value
    value = Column(Float)
    value_text = Column(String(500))  # For non-numeric values
    unit = Column(String(50))

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Quality indicators
    within_limits = Column(Boolean)
    uncertainty = Column(Float)
    instrument_id = Column(String(100))

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurements")

    def __repr__(self):
        return f"<TestMeasurement(name='{self.measurement_name}', value={self.value} {self.unit})>"


class TestResult(Base):
    """
    Test results and pass/fail criteria evaluation
    """
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)

    # Criterion identification
    criterion_name = Column(String(255), nullable=False)
    criterion_condition = Column(String(500), nullable=False)
    severity = Column(String(20))  # critical, major, minor

    # Evaluation
    evaluated_value = Column(Float)
    limit_value = Column(Float)
    passed = Column(Boolean, nullable=False)

    # Details
    description = Column(Text)
    failure_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="results")

    def __repr__(self):
        return f"<TestResult(criterion='{self.criterion_name}', passed={self.passed})>"
