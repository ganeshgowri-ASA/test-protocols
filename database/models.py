"""
Database Models
SQLAlchemy ORM models for test protocols
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, JSON, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ProtocolStatus(enum.Enum):
    """Protocol status enumeration"""
    ACTIVE = "active"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class TestRunStatus(enum.Enum):
    """Test run status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class Protocol(Base):
    """Protocol definition table"""
    __tablename__ = "protocols"

    id = Column(String(50), primary_key=True)
    protocol_number = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    version = Column(String(20), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProtocolStatus), default=ProtocolStatus.ACTIVE)

    # JSON fields
    definition = Column(JSON, nullable=False)  # Complete protocol JSON
    test_parameters = Column(JSON)
    test_procedure = Column(JSON)
    qc_checks = Column(JSON)
    pass_fail_criteria = Column(JSON)

    # Metadata
    author = Column(String(100))
    standard_references = Column(JSON)  # Array of standard references
    created_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Protocol(id='{self.id}', name='{self.name}', version='{self.version}')>"


class TestRun(Base):
    """Test run execution table"""
    __tablename__ = "test_runs"

    id = Column(String(50), primary_key=True)
    protocol_id = Column(String(50), ForeignKey("protocols.id"), nullable=False, index=True)

    # Test identification
    module_serial_number = Column(String(100), index=True)
    batch_id = Column(String(100), index=True)
    operator = Column(String(100))

    # Execution details
    status = Column(SQLEnum(TestRunStatus), default=TestRunStatus.PENDING, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)

    # Test parameters (as executed)
    parameters = Column(JSON)

    # Progress tracking
    current_cycle = Column(Integer, default=0)
    total_cycles = Column(Integer)
    current_phase = Column(String(50))

    # Results summary
    results_summary = Column(JSON)
    pass_fail_status = Column(Boolean)
    failure_reason = Column(Text)

    # Environmental conditions
    ambient_temperature = Column(Float)
    ambient_humidity = Column(Float)
    ambient_pressure = Column(Float)

    # Equipment information
    chamber_id = Column(String(100))
    equipment_info = Column(JSON)

    # Integration
    lims_reference = Column(String(100))
    qms_reference = Column(String(100))
    project_reference = Column(String(100))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    data_points = relationship("DataPoint", back_populates="test_run", cascade="all, delete-orphan")
    qc_results = relationship("QCResult", back_populates="test_run", cascade="all, delete-orphan")
    interim_tests = relationship("InterimTest", back_populates="test_run", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_test_run_protocol_status', 'protocol_id', 'status'),
        Index('idx_test_run_time', 'start_time', 'end_time'),
    )

    def __repr__(self):
        return f"<TestRun(id='{self.id}', protocol='{self.protocol_id}', status='{self.status.value}')>"


class DataPoint(Base):
    """Data point measurements table"""
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False, index=True)

    # Timing
    timestamp = Column(DateTime, nullable=False, index=True)
    cycle_number = Column(Integer, index=True)
    phase = Column(String(50), index=True)

    # Environmental parameters
    chamber_temperature = Column(Float)
    chamber_humidity = Column(Float)
    chamber_pressure = Column(Float)
    uv_irradiance = Column(Float)

    # Module parameters
    module_temperature = Column(Float)
    voc = Column(Float)
    isc = Column(Float)
    vmp = Column(Float)
    imp = Column(Float)
    pmax = Column(Float)
    fill_factor = Column(Float)
    efficiency = Column(Float)

    # Additional measurements (flexible JSON)
    additional_data = Column(JSON)

    # Data quality
    data_quality_flag = Column(String(20))  # good, questionable, bad
    notes = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="data_points")

    # Indexes
    __table_args__ = (
        Index('idx_data_point_test_time', 'test_run_id', 'timestamp'),
        Index('idx_data_point_cycle_phase', 'test_run_id', 'cycle_number', 'phase'),
    )

    def __repr__(self):
        return f"<DataPoint(test_run='{self.test_run_id}', timestamp='{self.timestamp}', cycle={self.cycle_number})>"


class QCResult(Base):
    """QC check results table"""
    __tablename__ = "qc_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False, index=True)

    # Check identification
    check_name = Column(String(100), nullable=False, index=True)
    check_type = Column(String(50))  # continuous, periodic
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    cycle_number = Column(Integer)

    # Results
    passed = Column(Boolean, nullable=False, index=True)
    severity = Column(String(20))  # critical, major, minor
    action_taken = Column(String(50))  # alert, flag, abort

    # Details
    measured_value = Column(Float)
    threshold_value = Column(Float)
    deviation = Column(Float)
    details = Column(JSON)
    notes = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="qc_results")

    # Indexes
    __table_args__ = (
        Index('idx_qc_result_test_check', 'test_run_id', 'check_name'),
        Index('idx_qc_result_passed', 'test_run_id', 'passed'),
    )

    def __repr__(self):
        return f"<QCResult(test_run='{self.test_run_id}', check='{self.check_name}', passed={self.passed})>"


class InterimTest(Base):
    """Interim test results table"""
    __tablename__ = "interim_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(50), ForeignKey("test_runs.id"), nullable=False, index=True)

    # Test identification
    cycle_number = Column(Integer, nullable=False, index=True)
    test_type = Column(String(50), nullable=False)  # iv_curve, insulation_resistance, visual_inspection
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # I-V Curve measurements
    voc = Column(Float)
    isc = Column(Float)
    vmp = Column(Float)
    imp = Column(Float)
    pmax = Column(Float)
    fill_factor = Column(Float)
    efficiency = Column(Float)

    # Degradation tracking
    power_retention_percent = Column(Float)
    degradation_percent = Column(Float)

    # Insulation resistance
    insulation_resistance = Column(Float)  # MΩ

    # Visual inspection
    visual_defects = Column(JSON)  # Array of defect descriptions
    visual_inspection_passed = Column(Boolean)

    # Additional measurements
    additional_measurements = Column(JSON)

    # Pass/Fail
    passed = Column(Boolean)
    failure_modes = Column(JSON)
    notes = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="interim_tests")

    # Indexes
    __table_args__ = (
        Index('idx_interim_test_cycle', 'test_run_id', 'cycle_number'),
        Index('idx_interim_test_type', 'test_run_id', 'test_type'),
    )

    def __repr__(self):
        return f"<InterimTest(test_run='{self.test_run_id}', cycle={self.cycle_number}, type='{self.test_type}')>"
