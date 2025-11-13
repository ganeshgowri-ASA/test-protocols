"""Database models for test protocol management."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

Base = declarative_base()


class Protocol(Base):
    """Protocol definition model."""

    __tablename__ = 'protocols'

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    config = Column(JSON, nullable=False)  # Full JSON protocol definition
    standard_references = Column(JSON)  # IEC standards, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Protocol(id={self.protocol_id}, name={self.name}, version={self.version})>"


class TestRun(Base):
    """Individual test execution."""

    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False)
    run_number = Column(String(100), unique=True, nullable=False, index=True)

    # Test metadata
    operator = Column(String(100), nullable=False)
    module_serial = Column(String(100))
    batch_number = Column(String(100))
    project_code = Column(String(100))

    # Timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    # Status: pending, in_progress, completed, failed, cancelled
    status = Column(String(20), nullable=False, default='pending', index=True)

    # Environmental conditions
    ambient_temperature = Column(Float)
    ambient_humidity = Column(Float)

    # Equipment info
    equipment_ids = Column(JSON)  # List of equipment used

    # Traceability
    notes = Column(Text)
    metadata = Column(JSON)  # Additional flexible data

    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="test_run", cascade="all, delete-orphan")
    qc_checks = relationship("QCCheck", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TestRun(run_number={self.run_number}, status={self.status})>"


class Measurement(Base):
    """Individual measurement data points."""

    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    measurement_type = Column(String(50), nullable=False)  # irradiance, voltage, current, etc.

    # Measurement value
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)

    # Spatial position (for grid measurements)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    position_z = Column(Float, nullable=True)

    # Target irradiance level for PERF-002
    target_irradiance = Column(Float, nullable=True)  # 100, 200, 400, 600, 800, 1000, 1100

    # Additional context
    temperature = Column(Float, nullable=True)  # Cell/module temperature
    metadata = Column(JSON)

    test_run = relationship("TestRun", back_populates="measurements")

    def __repr__(self) -> str:
        return f"<Measurement(type={self.measurement_type}, value={self.value} {self.unit})>"


class AnalysisResult(Base):
    """Analysis and calculation results."""

    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    calculation_name = Column(String(100), nullable=False)  # average_irradiance, uniformity, etc.
    result_value = Column(Float, nullable=False)
    unit = Column(String(20))

    # For irradiance level specific results
    irradiance_level = Column(Float, nullable=True)  # Which irradiance level this result is for

    qc_status = Column(String(20))  # pass, fail, warning, na
    calculated_at = Column(DateTime, default=datetime.utcnow)

    metadata = Column(JSON)  # Additional calculation details

    test_run = relationship("TestRun", back_populates="analysis_results")

    def __repr__(self) -> str:
        return f"<AnalysisResult(name={self.calculation_name}, value={self.result_value})>"


class QCCheck(Base):
    """Quality control check results."""

    __tablename__ = 'qc_checks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    check_name = Column(String(100), nullable=False)
    check_type = Column(String(50), nullable=False)  # range, threshold, uniformity, etc.

    # Expected vs actual
    expected_value = Column(Float)
    actual_value = Column(Float)
    tolerance = Column(Float)

    # Result
    status = Column(String(20), nullable=False)  # pass, fail, warning
    severity = Column(String(20), default='normal')  # critical, high, normal, low

    message = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)

    metadata = Column(JSON)

    test_run = relationship("TestRun", back_populates="qc_checks")

    def __repr__(self) -> str:
        return f"<QCCheck(name={self.check_name}, status={self.status})>"


class Equipment(Base):
    """Equipment and instruments used in testing."""

    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(50), nullable=False)  # reference_cell, pyranometer, etc.

    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Calibration
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_certificate = Column(String(200))

    # Status
    status = Column(String(20), default='active')  # active, maintenance, retired

    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Equipment(id={self.equipment_id}, name={self.name})>"


# Pydantic schemas for API/validation

class MeasurementCreate(BaseModel):
    """Schema for creating a measurement."""

    measurement_type: str
    value: float
    unit: str
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None
    target_irradiance: Optional[float] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measurement_type": "irradiance",
                "value": 1000.5,
                "unit": "W/m²",
                "position_x": 0.0,
                "position_y": 0.0,
                "target_irradiance": 1000.0,
                "temperature": 25.0
            }
        }


class TestRunCreate(BaseModel):
    """Schema for creating a test run."""

    protocol_id: str
    operator: str
    module_serial: Optional[str] = None
    batch_number: Optional[str] = None
    project_code: Optional[str] = None
    ambient_temperature: Optional[float] = None
    ambient_humidity: Optional[float] = None
    equipment_ids: Optional[list[str]] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "protocol_id": "PERF-002",
                "operator": "John Doe",
                "module_serial": "MOD-12345",
                "batch_number": "BATCH-001",
                "ambient_temperature": 25.0,
                "ambient_humidity": 45.0
            }
        }


class AnalysisResultCreate(BaseModel):
    """Schema for creating an analysis result."""

    calculation_name: str
    result_value: float
    unit: Optional[str] = None
    irradiance_level: Optional[float] = None
    qc_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
