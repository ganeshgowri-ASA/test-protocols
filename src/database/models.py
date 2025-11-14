"""
Database Models for PV Test Protocol Framework

SQLAlchemy models for storing protocol definitions, test results, and measurements.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text,
    JSON, ForeignKey, Enum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ProtocolStatusEnum(PyEnum):
    """Protocol execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Protocol(Base):
    """Protocol definition table."""
    __tablename__ = 'protocols'

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    definition_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(id={self.protocol_id}, name={self.name}, version={self.version})>"


class Sample(Base):
    """PV sample/cell metadata table."""
    __tablename__ = 'samples'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    manufacturer = Column(String(200))
    cell_type = Column(String(100))
    cell_efficiency = Column(Float)
    cell_area = Column(Float)  # cm²
    manufacturing_date = Column(String(50))
    initial_pmax = Column(Float)  # W
    initial_voc = Column(Float)  # V
    initial_isc = Column(Float)  # A
    initial_ff = Column(Float)  # Fill factor
    batch_number = Column(String(100))
    wafer_type = Column(String(100))
    texture_type = Column(String(100))
    metallization_process = Column(String(100))
    metadata_json = Column(JSON)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship("TestRun", back_populates="sample")

    def __repr__(self):
        return f"<Sample(id={self.sample_id}, type={self.cell_type})>"


class TestRun(Base):
    """Test execution run table."""
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False)
    sample_id = Column(Integer, ForeignKey('samples.id'), nullable=False)
    status = Column(Enum(ProtocolStatusEnum), default=ProtocolStatusEnum.PENDING)
    test_parameters = Column(JSON)  # Test configuration
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    pass_fail = Column(Boolean)
    error_messages = Column(JSON)  # List of errors
    warnings = Column(JSON)  # List of warnings
    metadata = Column(JSON)  # Additional run metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    sample = relationship("Sample", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    crack_data = relationship("CrackData", back_populates="test_run", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_test_runs_protocol_sample', 'protocol_id', 'sample_id'),
        Index('ix_test_runs_status_time', 'status', 'start_time'),
    )

    def __repr__(self):
        return f"<TestRun(id={self.run_id}, status={self.status.value})>"


class Measurement(Base):
    """Measurement data table."""
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    measurement_type = Column(String(50), nullable=False)  # 'initial', 'interim', 'final'
    cycle_number = Column(Integer)  # Null for initial/final, cycle number for interim
    timestamp = Column(DateTime, default=datetime.utcnow)

    # IV Curve Parameters
    pmax = Column(Float)  # Maximum power (W)
    vmp = Column(Float)  # Voltage at maximum power (V)
    imp = Column(Float)  # Current at maximum power (A)
    voc = Column(Float)  # Open circuit voltage (V)
    isc = Column(Float)  # Short circuit current (A)
    ff = Column(Float)  # Fill factor
    efficiency = Column(Float)  # Conversion efficiency (%)
    rs = Column(Float)  # Series resistance (Ω)
    rsh = Column(Float)  # Shunt resistance (Ω)

    # Measurement Conditions
    irradiance = Column(Float)  # W/m²
    temperature = Column(Float)  # °C

    # Raw Data References
    el_image_path = Column(String(500))
    visual_image_path = Column(String(500))
    ir_image_path = Column(String(500))
    iv_data_path = Column(String(500))  # Path to raw IV curve data

    # Additional data
    raw_data = Column(JSON)  # Any additional raw measurement data
    metadata = Column(JSON)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    # Indexes
    __table_args__ = (
        Index('ix_measurements_run_type', 'test_run_id', 'measurement_type'),
        Index('ix_measurements_run_cycle', 'test_run_id', 'cycle_number'),
    )

    def __repr__(self):
        return f"<Measurement(run={self.test_run_id}, type={self.measurement_type}, cycle={self.cycle_number})>"


class CrackData(Base):
    """Crack detection and analysis data table."""
    __tablename__ = 'crack_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    measurement_type = Column(String(50), nullable=False)  # 'initial', 'interim', 'final'
    cycle_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Crack Metrics
    cracks_detected = Column(Boolean, default=False)
    crack_count = Column(Integer, default=0)
    total_crack_area = Column(Float)  # mm²
    total_crack_length = Column(Float)  # mm
    crack_area_percent = Column(Float)  # Percentage of cell area
    isolated_cells = Column(Integer, default=0)
    crack_severity = Column(String(20))  # 'none', 'low', 'medium', 'high', 'critical'

    # Image Analysis
    el_image_path = Column(String(500))
    processed_image_path = Column(String(500))
    crack_locations = Column(JSON)  # List of crack coordinates

    # Analysis Metadata
    detection_sensitivity = Column(String(20))
    processing_version = Column(String(20))
    analysis_metadata = Column(JSON)

    # Relationships
    test_run = relationship("TestRun", back_populates="crack_data")

    # Indexes
    __table_args__ = (
        Index('ix_crack_data_run_type', 'test_run_id', 'measurement_type'),
        Index('ix_crack_data_run_cycle', 'test_run_id', 'cycle_number'),
    )

    def __repr__(self):
        return f"<CrackData(run={self.test_run_id}, cracks={self.crack_count}, severity={self.crack_severity})>"


class DegradationAnalysis(Base):
    """Degradation analysis results table."""
    __tablename__ = 'degradation_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, unique=True)

    # Power Degradation
    initial_pmax = Column(Float)
    final_pmax = Column(Float)
    pmax_degradation_percent = Column(Float)
    pmax_degradation_absolute = Column(Float)

    # Fill Factor Degradation
    initial_ff = Column(Float)
    final_ff = Column(Float)
    ff_degradation_percent = Column(Float)

    # Crack Propagation
    initial_crack_area = Column(Float)
    final_crack_area = Column(Float)
    crack_growth = Column(Float)
    crack_growth_percent = Column(Float)

    # Degradation Rates
    degradation_rate_per_cycle = Column(Float)
    degradation_rate_percent_per_cycle = Column(Float)

    # Pass/Fail Assessment
    pass_fail = Column(Boolean)
    failure_reasons = Column(JSON)  # List of failure criteria violated

    # Analysis Results
    analysis_results = Column(JSON)  # Complete analysis data
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('ix_degradation_analysis_pass_fail', 'pass_fail'),
    )

    def __repr__(self):
        return f"<DegradationAnalysis(run={self.test_run_id}, pass={self.pass_fail})>"


class Equipment(Base):
    """Equipment and calibration tracking table."""
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100))  # 'thermal_chamber', 'el_system', 'solar_simulator', etc.
    manufacturer = Column(String(200))
    model = Column(String(200))
    serial_number = Column(String(200))
    specification = Column(Text)

    # Calibration
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_interval_days = Column(Integer)
    calibration_certificate = Column(String(500))  # Path to certificate

    # Status
    is_operational = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipment(id={self.equipment_id}, name={self.name})>"


class AuditLog(Base):
    """Audit log for protocol executions and changes."""
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user = Column(String(100))
    action = Column(String(100))  # 'protocol_start', 'protocol_complete', 'measurement_taken', etc.
    entity_type = Column(String(50))  # 'test_run', 'sample', 'protocol', etc.
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))

    # Indexes
    __table_args__ = (
        Index('ix_audit_log_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_log_user_time', 'user', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(user={self.user}, action={self.action}, time={self.timestamp})>"
