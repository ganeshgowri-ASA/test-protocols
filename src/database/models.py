"""
SQLAlchemy Database Models for Test Protocols
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    JSON, ForeignKey, Text, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ProtocolStatus(enum.Enum):
    """Protocol status enumeration."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


class TestRunStatus(enum.Enum):
    """Test run status enumeration."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QCStatus(enum.Enum):
    """QC result status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class Protocol(Base):
    """Protocol definition table."""

    __tablename__ = "protocols"

    id = Column(String(50), primary_key=True)  # e.g., 'conc-001'
    name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # e.g., 'Performance', 'Reliability'
    status = Column(Enum(ProtocolStatus), default=ProtocolStatus.ACTIVE)

    schema_json = Column(JSON, nullable=False)
    config_json = Column(JSON)
    qc_criteria_json = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(id='{self.id}', name='{self.name}', version='{self.version}')>"


class Equipment(Base):
    """Equipment and calibration tracking table."""

    __tablename__ = "equipment"

    id = Column(String(100), primary_key=True)  # e.g., 'SIM-001-ClassAAA'
    name = Column(String(255), nullable=False)
    equipment_type = Column(String(100), nullable=False)  # e.g., 'solar_simulator'
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    calibration_date = Column(DateTime)
    calibration_due_date = Column(DateTime)
    calibration_certificate = Column(String(255))  # File reference
    calibration_status = Column(String(50))  # 'valid', 'expired', 'due_soon'

    specifications = Column(JSON)  # Technical specifications
    location = Column(String(255))
    status = Column(String(50), default='active')  # 'active', 'maintenance', 'retired'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship("TestRun", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment(id='{self.id}', type='{self.equipment_type}')>"


class TestRun(Base):
    """Test run execution table."""

    __tablename__ = "test_runs"

    id = Column(String(100), primary_key=True)  # e.g., 'CONC-001-20251114-0001'
    protocol_id = Column(String(50), ForeignKey("protocols.id"), nullable=False)
    equipment_id = Column(String(100), ForeignKey("equipment.id"))

    sample_id = Column(String(100), nullable=False)
    operator = Column(String(100), nullable=False)
    status = Column(Enum(TestRunStatus), default=TestRunStatus.PLANNED)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_minutes = Column(Float)

    # Test data
    raw_data_json = Column(JSON)  # Complete raw data
    processed_data_json = Column(JSON)  # Processed/calculated data
    metadata_json = Column(JSON)  # Additional metadata

    # Environmental conditions
    ambient_temperature_c = Column(Float)
    humidity_percent = Column(Float)
    atmospheric_pressure_kpa = Column(Float)

    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    equipment = relationship("Equipment", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    qc_results = relationship("QCResult", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun(id='{self.id}', sample='{self.sample_id}', status='{self.status.value}')>"


class Measurement(Base):
    """Individual measurement data points."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(100), ForeignKey("test_runs.id"), nullable=False)

    # Measurement sequence
    sequence_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Common measurement fields
    concentration_suns = Column(Float)
    temperature_c = Column(Float)

    # Electrical parameters
    voc = Column(Float)  # Open circuit voltage
    isc = Column(Float)  # Short circuit current
    vmp = Column(Float)  # Maximum power voltage
    imp = Column(Float)  # Maximum power current
    power_w = Column(Float)  # Power output
    fill_factor = Column(Float)
    efficiency = Column(Float)

    # Additional parameters
    spectral_mismatch = Column(Float)
    series_resistance = Column(Float)
    shunt_resistance = Column(Float)

    # IV curve data (if applicable)
    iv_curve_data = Column(JSON)

    # Quality indicators
    measurement_quality = Column(String(50))  # 'good', 'acceptable', 'poor'
    flags = Column(JSON)  # List of any flags or warnings

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(id={self.id}, test_run='{self.test_run_id}', seq={self.sequence_number})>"


class QCResult(Base):
    """Quality control results table."""

    __tablename__ = "qc_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(100), ForeignKey("test_runs.id"), nullable=False)

    criterion_name = Column(String(100), nullable=False)
    criterion_description = Column(Text)

    status = Column(Enum(QCStatus), nullable=False)
    measured_value = Column(Float)
    expected_value = Column(Float)
    tolerance = Column(Float)
    pass_fail_threshold = Column(Float)

    message = Column(Text)
    severity = Column(String(50))  # 'critical', 'major', 'minor'

    checked_at = Column(DateTime, default=datetime.utcnow)
    checked_by = Column(String(100))

    details_json = Column(JSON)  # Additional QC details

    # Relationships
    test_run = relationship("TestRun", back_populates="qc_results")

    def __repr__(self):
        return f"<QCResult(id={self.id}, criterion='{self.criterion_name}', status='{self.status.value}')>"


class CalibrationHistory(Base):
    """Calibration history tracking."""

    __tablename__ = "calibration_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), ForeignKey("equipment.id"), nullable=False)

    calibration_date = Column(DateTime, nullable=False)
    performed_by = Column(String(100))
    calibration_lab = Column(String(255))

    certificate_number = Column(String(100))
    certificate_file = Column(String(255))

    traceable_to = Column(String(100))  # e.g., 'NIST'
    calibration_standard = Column(String(255))

    results_json = Column(JSON)  # Calibration results and uncertainties
    passed = Column(Boolean)

    next_calibration_due = Column(DateTime)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalibrationHistory(id={self.id}, equipment='{self.equipment_id}', date='{self.calibration_date}')>"


class AuditLog(Base):
    """Audit trail for compliance and traceability."""

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)  # 'create', 'update', 'delete', 'execute'
    entity_type = Column(String(50))  # 'protocol', 'test_run', 'equipment'
    entity_id = Column(String(100))

    changes_json = Column(JSON)  # Before/after values
    ip_address = Column(String(50))
    user_agent = Column(String(255))

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user='{self.user}', action='{self.action}')>"
