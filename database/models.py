"""SQLAlchemy ORM Models for test protocols"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class ProtocolType(str, enum.Enum):
    """Enum for protocol types"""
    SNOW_LOAD = "snow_load"
    WIND_LOAD = "wind_load"
    ICE_LOAD = "ice_load"
    HUMIDITY_FREEZE = "humidity_freeze"
    THERMAL_CYCLING = "thermal_cycling"
    UV_EXPOSURE = "uv_exposure"
    IV_CURVE = "iv_curve"
    FLASH_TEST = "flash_test"
    INSULATION_RESISTANCE = "insulation_resistance"


class TestStatus(str, enum.Enum):
    """Enum for test status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestResult(str, enum.Enum):
    """Enum for test results"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    NOT_EVALUATED = "not_evaluated"


class TestRun(Base):
    """Model for a single test run"""
    __tablename__ = "test_runs"

    id = Column(String, primary_key=True)
    protocol_type = Column(Enum(ProtocolType), nullable=False, index=True)
    protocol_version = Column(String, nullable=False)
    module_id = Column(String, nullable=False, index=True)
    specimen_id = Column(String, nullable=True)

    test_start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    test_end_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)

    status = Column(Enum(TestStatus), default=TestStatus.PENDING, nullable=False)
    test_result = Column(Enum(TestResult), default=TestResult.NOT_EVALUATED, nullable=True)
    result_summary = Column(Text, nullable=True)

    # Configuration as JSON
    configuration = Column(JSON, nullable=False)

    # Results as JSON
    results = Column(JSON, nullable=True)
    measurements = Column(JSON, nullable=True)  # Array of measurement objects

    # Metadata
    operator = Column(String, nullable=True)
    facility = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("TestStep", back_populates="test_run", cascade="all, delete-orphan")
    test_measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    attachments = relationship("TestAttachment", back_populates="test_run", cascade="all, delete-orphan")


class TestStep(Base):
    """Model for individual test steps"""
    __tablename__ = "test_steps"

    id = Column(String, primary_key=True)
    test_run_id = Column(String, ForeignKey("test_runs.id"), nullable=False, index=True)

    step_order = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    step_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(String, default="pending")  # pending, in_progress, completed, failed, skipped

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    success = Column(Boolean, default=None, nullable=True)
    error_message = Column(Text, nullable=True)

    # Step-specific data
    parameters = Column(JSON, nullable=True)
    readings = Column(JSON, nullable=True)

    test_run = relationship("TestRun", back_populates="steps")


class Measurement(Base):
    """Model for individual measurements"""
    __tablename__ = "measurements"

    id = Column(String, primary_key=True)
    test_run_id = Column(String, ForeignKey("test_runs.id"), nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    measurement_type = Column(String, nullable=False)  # deflection, load, temperature, etc.

    phase = Column(String, nullable=False)  # baseline, loading, hold, unloading, recovery
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    # Context
    applied_load = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)

    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=True)
    notes = Column(Text, nullable=True)

    test_run = relationship("TestRun", back_populates="test_measurements")
    equipment = relationship("Equipment")


class TestAttachment(Base):
    """Model for files attached to test runs"""
    __tablename__ = "test_attachments"

    id = Column(String, primary_key=True)
    test_run_id = Column(String, ForeignKey("test_runs.id"), nullable=False, index=True)

    filename = Column(String, nullable=False)
    file_type = Column(String)  # image, document, data, report
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="attachments")


class Equipment(Base):
    """Model for testing equipment"""
    __tablename__ = "equipment"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)  # load_frame, sensor, etc.
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, unique=True, nullable=True)

    location = Column(String, nullable=True)
    status = Column(String, default="available")  # available, in_use, maintenance, retired

    last_calibration = Column(DateTime, nullable=True)
    calibration_due = Column(DateTime, nullable=True)

    specifications = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Module(Base):
    """Model for PV modules under test"""
    __tablename__ = "modules"

    id = Column(String, primary_key=True)
    module_id = Column(String, unique=True, nullable=False, index=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)

    # Module specifications
    length_mm = Column(Float, nullable=True)
    width_mm = Column(Float, nullable=True)
    thickness_mm = Column(Float, nullable=True)
    mass_kg = Column(Float, nullable=True)
    rated_power_w = Column(Float, nullable=True)

    # Material properties
    frame_type = Column(String, nullable=True)  # aluminum, stainless_steel, frameless
    glass_type = Column(String, nullable=True)
    cell_technology = Column(String, nullable=True)  # mono, poly, thin-film, etc.

    # Status
    status = Column(String, default="active")  # active, retired, failed
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
