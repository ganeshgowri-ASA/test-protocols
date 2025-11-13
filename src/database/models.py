"""SQLAlchemy database models for protocol storage and traceability."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


class StatusEnum(enum.Enum):
    """Protocol status enumeration."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"


class Protocol(Base):
    """Protocol test instance model."""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), nullable=False, index=True)  # e.g., 'IAM-001'
    protocol_version = Column(String(20), nullable=False)
    test_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Sample information
    sample_id = Column(String(100), nullable=False, index=True)
    module_type = Column(String(200))
    manufacturer = Column(String(200))
    serial_number = Column(String(100))
    technology = Column(String(50))
    rated_power = Column(Float)
    area = Column(Float)

    # Test configuration
    test_config = Column(JSON)  # Store test_configuration as JSON

    # Operator and facility
    operator = Column(String(200))
    facility = Column(String(200))

    # Status and timestamps
    status = Column(Enum(StatusEnum), default=StatusEnum.CREATED, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Metadata
    metadata_json = Column(JSON)  # Store additional metadata
    notes = Column(Text)

    # File reference
    data_file_path = Column(String(500))  # Path to full JSON file

    # Relationships
    measurements = relationship("Measurement", back_populates="protocol", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="protocol", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Protocol(id={self.id}, protocol_id='{self.protocol_id}', sample_id='{self.sample_id}', status='{self.status.value}')>"


class Measurement(Base):
    """Individual measurement model."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False, index=True)

    # Measurement data
    angle = Column(Float, nullable=False, index=True)
    isc = Column(Float, nullable=False)  # Short-circuit current (A)
    voc = Column(Float, nullable=False)  # Open-circuit voltage (V)
    pmax = Column(Float, nullable=False)  # Maximum power (W)
    imp = Column(Float)  # Current at max power (A)
    vmp = Column(Float)  # Voltage at max power (V)
    ff = Column(Float)  # Fill factor

    # Actual test conditions
    irradiance_actual = Column(Float)  # W/m²
    temperature_actual = Column(Float)  # °C

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="measurements")

    def __repr__(self) -> str:
        return f"<Measurement(id={self.id}, angle={self.angle}°, pmax={self.pmax}W)>"


class AnalysisResult(Base):
    """Analysis results model."""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False, index=True)

    # Analysis type and model
    analysis_type = Column(String(50), default="iam_analysis")
    model_name = Column(String(50))  # 'ashrae', 'physical', 'polynomial'

    # Fitting parameters (stored as JSON)
    parameters = Column(JSON)

    # Quality metrics
    r_squared = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)

    # IAM curve data (stored as JSON array)
    iam_curve = Column(JSON)

    # Quality assessment
    fit_quality = Column(String(20))  # 'excellent', 'good', 'acceptable', 'poor'
    measurement_stability = Column(String(20))  # 'pass', 'warning', 'fail'
    data_completeness = Column(Float)  # Percentage

    # Additional statistics
    statistics = Column(JSON)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    protocol = relationship("Protocol", back_populates="analysis_results")

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, model='{self.model_name}', r²={self.r_squared:.4f})>"


class AuditLog(Base):
    """Audit log for traceability."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=True, index=True)

    # Event information
    event_type = Column(String(50), nullable=False, index=True)
    event_description = Column(Text)

    # User information
    user = Column(String(200))
    user_role = Column(String(50))

    # Changes (stored as JSON)
    changes = Column(JSON)  # Before/after values for modifications

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # IP address and session
    ip_address = Column(String(45))  # IPv6-compatible
    session_id = Column(String(100))

    # Relationships
    protocol = relationship("Protocol", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event='{self.event_type}', timestamp='{self.timestamp}')>"


class Equipment(Base):
    """Test equipment model for calibration tracking."""

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Equipment information
    equipment_type = Column(String(50), nullable=False)  # 'simulator', 'iv_tracer', etc.
    manufacturer = Column(String(200))
    model = Column(String(200), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)

    # Calibration information
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime, index=True)
    calibration_certificate = Column(String(100))
    calibration_status = Column(String(20), default="valid")  # 'valid', 'expired', 'due'

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, type='{self.equipment_type}', model='{self.model}')>"
