"""SQLAlchemy ORM models for test protocol database."""

from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json as json_module

Base = declarative_base()


class Protocol(Base):
    """Protocol definition record."""

    __tablename__ = "protocols"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, index=True)
    version = Column(String(20), nullable=False)
    category = Column(String(50))
    standard = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author = Column(String(100))
    status = Column(String(20), default="active")  # active, deprecated, archived
    definition = Column(JSON)  # Full protocol JSON

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Protocol(id='{self.id}', code='{self.code}', version='{self.version}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "version": self.version,
            "category": self.category,
            "standard": self.standard,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "author": self.author,
            "status": self.status,
        }


class TestRun(Base):
    """Execution record for a protocol."""

    __tablename__ = "test_runs"

    id = Column(String(50), primary_key=True)
    protocol_id = Column(String(100), ForeignKey("protocols.id"), nullable=False)
    sample_id = Column(String(100), nullable=False, index=True)
    operator_id = Column(String(100))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(20), default="initialized")  # initialized, running, completed, failed, aborted
    current_phase = Column(String(100))
    parameters = Column(JSON)  # Test parameters
    notes = Column(Text)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    qc_flags = relationship("QCFlag", back_populates="test_run", cascade="all, delete-orphan")
    reports = relationship("TestReport", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun(id='{self.id}', protocol='{self.protocol_id}', sample='{self.sample_id}', status='{self.status}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "protocol_id": self.protocol_id,
            "sample_id": self.sample_id,
            "operator_id": self.operator_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "current_phase": self.current_phase,
            "parameters": self.parameters,
            "notes": self.notes,
        }


class Measurement(Base):
    """Individual measurement record."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False, index=True)
    phase_id = Column(String(100), nullable=False, index=True)
    measurement_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Float)
    value_str = Column(String(100))  # For categorical values
    unit = Column(String(20))
    metadata = Column(JSON)  # Additional metadata
    diode_number = Column(Integer)  # For per-diode measurements

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")
    qc_flags = relationship("QCFlag", back_populates="measurement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Measurement(id={self.id}, run='{self.test_run_id}', type='{self.measurement_id}', value={self.value})>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "phase_id": self.phase_id,
            "measurement_id": self.measurement_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "value": self.value,
            "value_str": self.value_str,
            "unit": self.unit,
            "metadata": self.metadata,
            "diode_number": self.diode_number,
        }


class QCFlag(Base):
    """Quality control flag record."""

    __tablename__ = "qc_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False, index=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), index=True)
    rule_id = Column(String(100), nullable=False)
    flag_type = Column(String(20), nullable=False)  # warning, error
    description = Column(String(500))
    value = Column(Float)
    threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)

    # Relationships
    test_run = relationship("TestRun", back_populates="qc_flags")
    measurement = relationship("Measurement", back_populates="qc_flags")

    def __repr__(self):
        return f"<QCFlag(id={self.id}, type='{self.flag_type}', rule='{self.rule_id}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "measurement_id": self.measurement_id,
            "rule_id": self.rule_id,
            "flag_type": self.flag_type,
            "description": self.description,
            "value": self.value,
            "threshold": self.threshold,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }


class TestReport(Base):
    """Generated test report."""

    __tablename__ = "test_reports"

    id = Column(String(50), primary_key=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False)
    report_type = Column(String(50), default="final")  # preliminary, final, summary
    generated_at = Column(DateTime, default=datetime.utcnow)
    report_content = Column(JSON)  # Report data
    file_path = Column(String(500))
    file_format = Column(String(10))  # pdf, html, json
    generated_by = Column(String(100))

    # Relationships
    test_run = relationship("TestRun", back_populates="reports")

    def __repr__(self):
        return f"<TestReport(id='{self.id}', run='{self.test_run_id}', type='{self.report_type}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "report_type": self.report_type,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "generated_by": self.generated_by,
        }


class Equipment(Base):
    """Equipment inventory record."""

    __tablename__ = "equipment"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    equipment_type = Column(String(100))
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    specifications = Column(JSON)
    calibration_required = Column(Boolean, default=True)
    calibration_interval_days = Column(Integer)
    status = Column(String(20), default="active")  # active, maintenance, retired
    location = Column(String(200))
    acquired_date = Column(DateTime)
    notes = Column(Text)

    # Relationships
    calibrations = relationship("EquipmentCalibration", back_populates="equipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Equipment(id='{self.id}', name='{self.name}', status='{self.status}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "equipment_type": self.equipment_type,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "specifications": self.specifications,
            "calibration_required": self.calibration_required,
            "calibration_interval_days": self.calibration_interval_days,
            "status": self.status,
            "location": self.location,
            "acquired_date": self.acquired_date.isoformat() if self.acquired_date else None,
            "notes": self.notes,
        }


class EquipmentCalibration(Base):
    """Equipment calibration record."""

    __tablename__ = "equipment_calibrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(50), ForeignKey("equipment.id"), nullable=False, index=True)
    calibration_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    performed_by = Column(String(100))
    certificate_number = Column(String(100))
    result = Column(String(20))  # pass, fail
    notes = Column(Text)
    certificate_file = Column(String(500))

    # Relationships
    equipment = relationship("Equipment", back_populates="calibrations")

    def __repr__(self):
        return f"<EquipmentCalibration(id={self.id}, equipment='{self.equipment_id}', date='{self.calibration_date}')>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "calibration_date": self.calibration_date.isoformat() if self.calibration_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "performed_by": self.performed_by,
            "certificate_number": self.certificate_number,
            "result": self.result,
            "notes": self.notes,
            "certificate_file": self.certificate_file,
        }
