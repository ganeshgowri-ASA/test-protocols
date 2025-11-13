"""Database models for protocols, test executions, and measurements."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from .database import Base


class ProtocolStatus(str, Enum):
    """Protocol status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class TestExecutionStatus(str, Enum):
    """Test execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class QCStatus(str, Enum):
    """Quality control status enumeration."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class Protocol(Base):
    """Protocol definition model."""

    __tablename__ = "protocols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pid = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    standard = Column(String(100))  # e.g., "IEC 62804"
    description = Column(Text)
    schema = Column(JSON, nullable=False)
    status = Column(SQLEnum(ProtocolStatus), default=ProtocolStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Protocol(pid='{self.pid}', name='{self.name}', version='{self.version}')>"


class TestExecution(Base):
    """Test execution model."""

    __tablename__ = "test_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_id = Column(String(36), ForeignKey("protocols.id"), nullable=False)
    test_name = Column(String(255), nullable=False, index=True)
    module_id = Column(String(255), index=True)

    # Test parameters
    input_parameters = Column(JSON, nullable=False)

    # Test status and timing
    status = Column(SQLEnum(TestExecutionStatus), default=TestExecutionStatus.PENDING)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_hours = Column(Float)

    # Results summary
    results_summary = Column(JSON)
    qc_status = Column(SQLEnum(QCStatus))

    # Metadata
    operator = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_executions")
    measurements = relationship("Measurement", back_populates="test_execution", cascade="all, delete-orphan")
    qc_checks = relationship("QCCheck", back_populates="test_execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution(id='{self.id}', test_name='{self.test_name}', status='{self.status}')>"


class Measurement(Base):
    """Measurement data point model for leakage tracking."""

    __tablename__ = "measurements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_execution_id = Column(String(36), ForeignKey("test_executions.id"), nullable=False, index=True)

    # Timing
    timestamp = Column(DateTime, nullable=False)
    elapsed_time = Column(Float, nullable=False)  # hours

    # Primary measurements
    leakage_current = Column(Float, nullable=False)  # mA
    voltage = Column(Float, nullable=False)  # V

    # Environmental conditions
    temperature = Column(Float)  # Celsius
    humidity = Column(Float)  # percent

    # Derived metrics
    power_degradation = Column(Float)  # percent

    # Additional data
    raw_data = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(elapsed_time={self.elapsed_time}h, leakage_current={self.leakage_current}mA)>"


class QCCheck(Base):
    """Quality control check result model."""

    __tablename__ = "qc_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_execution_id = Column(String(36), ForeignKey("test_executions.id"), nullable=False, index=True)

    # Check details
    check_name = Column(String(255), nullable=False)
    check_type = Column(String(100))  # e.g., "leakage_current", "power_degradation"
    status = Column(SQLEnum(QCStatus), nullable=False)

    # Values
    measured_value = Column(Float)
    threshold_value = Column(Float)
    warning_threshold = Column(Float)

    # Results
    message = Column(Text)
    passed = Column(Integer)  # Boolean as integer

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="qc_checks")

    def __repr__(self):
        return f"<QCCheck(check_name='{self.check_name}', status='{self.status}')>"


class LeakageEvent(Base):
    """Leakage event tracking for anomaly detection."""

    __tablename__ = "leakage_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_execution_id = Column(String(36), ForeignKey("test_executions.id"), nullable=False, index=True)
    measurement_id = Column(String(36), ForeignKey("measurements.id"))

    # Event details
    event_type = Column(String(100))  # e.g., "spike", "sustained_high", "rapid_increase"
    severity = Column(String(50))  # e.g., "warning", "critical"

    # Event data
    timestamp = Column(DateTime, nullable=False)
    leakage_current = Column(Float, nullable=False)
    threshold_exceeded = Column(Float)

    # Event description
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LeakageEvent(type='{self.event_type}', severity='{self.severity}')>"
