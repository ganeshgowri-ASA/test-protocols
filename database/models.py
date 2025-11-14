"""Database models for test protocol system."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, JSON, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class TestStatus(enum.Enum):
    """Test execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class PassFailStatus(enum.Enum):
    """Pass/fail status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"


def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4())


class ProtocolDefinition(Base):
    """Protocol definition metadata stored in database."""

    __tablename__ = 'protocol_definitions'

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    json_definition = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<ProtocolDefinition(protocol_id='{self.protocol_id}', version='{self.version}')>"


class Specimen(Base):
    """Test specimen information."""

    __tablename__ = 'specimens'

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    specimen_code = Column(String(100), unique=True, nullable=False, index=True)
    specimen_type = Column(String(100), nullable=False)
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255), index=True)
    date_received = Column(DateTime)
    lims_id = Column(String(100), index=True)  # Integration with LIMS
    metadata = Column(JSON)  # Additional specimen properties
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="specimen")

    def __repr__(self):
        return f"<Specimen(code='{self.specimen_code}', type='{self.specimen_type}')>"


class TestExecution(Base):
    """Test execution record tracking protocol execution on a specimen."""

    __tablename__ = 'test_executions'

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    test_number = Column(String(100), unique=True, nullable=False, index=True)

    # Foreign keys
    protocol_id = Column(String(50), ForeignKey('protocol_definitions.protocol_id'), nullable=False)
    specimen_id = Column(UUID(as_uuid=False), ForeignKey('specimens.id'), nullable=False)

    # Test execution info
    status = Column(SQLEnum(TestStatus), default=TestStatus.PENDING, nullable=False, index=True)
    start_datetime = Column(DateTime, index=True)
    end_datetime = Column(DateTime)
    operator_id = Column(String(100), nullable=False)
    operator_name = Column(String(255))

    # Test parameters (stored as JSON for flexibility)
    test_parameters = Column(JSON, nullable=False)

    # Equipment used
    equipment_ids = Column(JSON)  # List of equipment IDs used

    # Environment conditions
    environmental_conditions = Column(JSON)

    # Notes and observations
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("ProtocolDefinition", back_populates="test_executions")
    specimen = relationship("Specimen", back_populates="test_executions")
    measurements = relationship("Measurement", back_populates="test_execution", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_execution", uselist=False, cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_test_exec_protocol_status', 'protocol_id', 'status'),
        Index('idx_test_exec_dates', 'start_datetime', 'end_datetime'),
    )

    def __repr__(self):
        return f"<TestExecution(test_number='{self.test_number}', status='{self.status.value}')>"


class Measurement(Base):
    """Individual measurement data point."""

    __tablename__ = 'measurements'

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    # Foreign key
    test_execution_id = Column(UUID(as_uuid=False), ForeignKey('test_executions.id'), nullable=False)

    # Measurement identification
    measurement_point_id = Column(String(100), nullable=False, index=True)
    measurement_point_name = Column(String(255))
    sequence_number = Column(Integer)  # Order in the test

    # Parameter being measured
    parameter_name = Column(String(100), nullable=False, index=True)
    parameter_display_name = Column(String(255))

    # Measurement value and metadata
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    uncertainty = Column(Float)  # Measurement uncertainty

    # Measurement conditions
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    temperature = Column(Float)  # Temperature during measurement
    humidity = Column(Float)  # Humidity during measurement

    # Measurement metadata
    recorded_by = Column(String(100))
    instrument_id = Column(String(100))
    measurement_method = Column(String(255))
    raw_data = Column(JSON)  # Store raw I-V curves, etc.

    # Quality flags
    qc_pass = Column(Boolean)
    qc_flags = Column(JSON)  # QC issue flags

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurements")

    # Indexes for queries
    __table_args__ = (
        Index('idx_measurement_test_point', 'test_execution_id', 'measurement_point_id'),
        Index('idx_measurement_param', 'test_execution_id', 'parameter_name'),
    )

    def __repr__(self):
        return f"<Measurement(parameter='{self.parameter_name}', value={self.value} {self.unit})>"


class TestResult(Base):
    """Test result evaluation and pass/fail determination."""

    __tablename__ = 'test_results'

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    # Foreign key
    test_execution_id = Column(UUID(as_uuid=False), ForeignKey('test_executions.id'), nullable=False, unique=True)

    # Overall result
    pass_fail = Column(SQLEnum(PassFailStatus), nullable=False, index=True)
    overall_score = Column(Float)  # Optional numerical score

    # Criteria evaluations (stored as JSON)
    criteria_evaluations = Column(JSON, nullable=False)
    # Structure: {
    #   "criterion_name": {
    #     "pass": bool,
    #     "message": str,
    #     "initial_value": float,
    #     "final_value": float,
    #     "retention_pct": float
    #   }
    # }

    # Summary statistics
    summary_stats = Column(JSON)
    # Structure: {
    #   "parameter_name": {
    #     "initial": float,
    #     "final": float,
    #     "change": float,
    #     "change_pct": float
    #   }
    # }

    # Quality control results
    qc_results = Column(JSON)
    qc_pass = Column(Boolean)
    qc_warnings = Column(JSON)

    # Visual inspection results (for degradation tests)
    visual_inspection_pass = Column(Boolean)
    visual_defects = Column(JSON)

    # Report generation
    report_generated = Column(Boolean, default=False)
    report_path = Column(String(500))
    report_format = Column(String(20))

    # Timestamps
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    evaluated_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="results")

    def __repr__(self):
        return f"<TestResult(pass_fail='{self.pass_fail.value}')>"


# Additional indexes for performance
Index('idx_protocol_category_active', ProtocolDefinition.category, ProtocolDefinition.active)
Index('idx_specimen_lims', Specimen.lims_id)
Index('idx_result_pass_fail', TestResult.pass_fail, TestResult.evaluated_at)
