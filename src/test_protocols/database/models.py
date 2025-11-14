"""
SQLAlchemy database models for test protocol framework.

Defines the database schema for protocols, test runs, measurements, and results.
"""

from sqlalchemy import (
    Column, String, Float, DateTime, Integer, Boolean, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()


class TestCategory(enum.Enum):
    """Test category enumeration."""
    MECHANICAL = "mechanical"
    ENVIRONMENTAL = "environmental"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    OPTICAL = "optical"


class TestStatus(enum.Enum):
    """Test run status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestResult(enum.Enum):
    """Test result enumeration."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"


class Protocol(Base):
    """
    Protocol database model.

    Stores test protocol definitions and metadata.
    """
    __tablename__ = 'protocols'

    protocol_id = Column(String(20), primary_key=True)
    version = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(Enum(TestCategory), nullable=False)
    standard_name = Column(String(50))
    standard_code = Column(String(100))
    description = Column(Text)
    duration_minutes = Column(Float)
    definition = Column(JSON, nullable=False)  # Full protocol JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol")
    equipment = relationship("Equipment", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(id={self.protocol_id}, name={self.name})>"


class TestRun(Base):
    """
    Test run database model.

    Stores information about individual test executions.
    """
    __tablename__ = 'test_runs'

    test_run_id = Column(String(100), primary_key=True)
    protocol_id = Column(String(20), ForeignKey('protocols.protocol_id'), nullable=False)
    protocol_version = Column(String(20), nullable=False)
    sample_id = Column(String(100), nullable=False, index=True)
    operator_id = Column(String(100), nullable=False)
    status = Column(Enum(TestStatus), nullable=False)
    current_step = Column(String(50))
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    notes = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun(id={self.test_run_id}, protocol={self.protocol_id}, sample={self.sample_id})>"


class Measurement(Base):
    """
    Measurement database model.

    Stores individual measurement data points collected during tests.
    """
    __tablename__ = 'measurements'

    measurement_id = Column(String(36), primary_key=True)
    test_run_id = Column(String(100), ForeignKey('test_runs.test_run_id'), nullable=False, index=True)
    step_id = Column(String(50), nullable=False, index=True)
    measurement_type = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    sensor_id = Column(String(50))
    metadata = Column(JSON)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(id={self.measurement_id}, type={self.measurement_type}, value={self.value} {self.unit})>"


class TestResult(Base):
    """
    Test result database model.

    Stores test results and analysis data.
    """
    __tablename__ = 'test_results'

    result_id = Column(String(36), primary_key=True)
    test_run_id = Column(String(100), ForeignKey('test_runs.test_run_id'), nullable=False, index=True)
    step_id = Column(String(50))
    result = Column(Enum(TestResult), nullable=False)
    passed = Column(Boolean)
    summary = Column(Text)
    details = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="results")

    def __repr__(self):
        return f"<TestResult(id={self.result_id}, result={self.result})>"


class Equipment(Base):
    """
    Equipment database model.

    Tracks test equipment, calibration status, and maintenance.
    """
    __tablename__ = 'equipment'

    equipment_id = Column(String(50), primary_key=True)
    protocol_id = Column(String(20), ForeignKey('protocols.protocol_id'))
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    manufacturer = Column(String(100))
    calibration_required = Column(Boolean, default=True)
    calibration_interval_days = Column(Integer)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_status = Column(String(20))  # current, due, overdue
    location = Column(String(100))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment(id={self.equipment_id}, name={self.name}, model={self.model})>"


class Sample(Base):
    """
    Sample database model.

    Stores information about test samples/modules.
    """
    __tablename__ = 'samples'

    sample_id = Column(String(100), primary_key=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    manufacturing_date = Column(DateTime)
    rated_power_w = Column(Float)
    rated_voltage_v = Column(Float)
    rated_current_a = Column(Float)
    dimensions_mm = Column(JSON)  # {length, width, thickness}
    weight_kg = Column(Float)
    technology_type = Column(String(50))  # mono-Si, poly-Si, thin-film, etc.
    received_date = Column(DateTime)
    notes = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Sample(id={self.sample_id}, manufacturer={self.manufacturer}, model={self.model})>"
