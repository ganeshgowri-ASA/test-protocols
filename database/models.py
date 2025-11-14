"""
Database Models

SQLAlchemy models for storing test protocols, runs, and results.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()


class TestStatus(enum.Enum):
    """Test run status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QCSeverity(enum.Enum):
    """QC check severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Protocol(Base):
    """
    Protocol definition table.
    Stores metadata about test protocols.
    """
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    definition_json = Column(JSON, nullable=False)  # Full protocol definition
    standards = Column(JSON)  # List of applicable standards
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    author = Column(String(100))
    tags = Column(JSON)  # List of tags

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_protocol_category_active", "category", "is_active"),
        UniqueConstraint("protocol_id", "version", name="uq_protocol_version"),
    )

    def __repr__(self) -> str:
        return f"<Protocol(protocol_id='{self.protocol_id}', name='{self.name}', version='{self.version}')>"


class TestRun(Base):
    """
    Test run instance table.
    Stores information about individual test executions.
    """
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False, index=True)
    sample_id = Column(String(100), nullable=False, index=True)
    serial_number = Column(String(100))
    operator = Column(String(100), nullable=False)
    status = Column(SQLEnum(TestStatus), nullable=False, default=TestStatus.PLANNED, index=True)

    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime)
    planned_completion = Column(DateTime)

    # Test parameters and data
    test_data = Column(JSON)  # All collected data
    metadata = Column(JSON)  # Additional metadata

    # Results summary
    test_result = Column(String(50))  # Pass/Fail/Conditional
    total_cycles = Column(Integer)
    current_cycle = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    qc_results = relationship("QCResult", back_populates="test_run", cascade="all, delete-orphan")
    inspections = relationship("VisualInspection", back_populates="test_run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_testrun_status_date", "status", "start_date"),
        Index("idx_testrun_operator", "operator"),
    )

    def __repr__(self) -> str:
        return f"<TestRun(run_id='{self.run_id}', sample_id='{self.sample_id}', status='{self.status.value}')>"


class Measurement(Base):
    """
    Measurement data table.
    Stores individual measurements taken during test runs.
    """
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False, default=0)
    measurement_type = Column(String(50), nullable=False)  # baseline, interim, final
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Electrical measurements
    voc = Column(Float)  # Open circuit voltage
    isc = Column(Float)  # Short circuit current
    pmax = Column(Float)  # Maximum power
    vmp = Column(Float)  # Voltage at maximum power
    imp = Column(Float)  # Current at maximum power
    ff = Column(Float)  # Fill factor
    rs = Column(Float)  # Series resistance
    rsh = Column(Float)  # Shunt resistance

    # Environmental measurements
    temperature = Column(Float)
    humidity = Column(Float)
    irradiance = Column(Float)

    # Other measurements
    insulation_resistance = Column(Float)
    wet_leakage_current = Column(Float)
    ground_continuity = Column(Boolean)

    # Raw data and notes
    raw_data = Column(JSON)  # IV curve data, etc.
    notes = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    __table_args__ = (
        Index("idx_measurement_testrun_cycle", "test_run_id", "cycle_number"),
        Index("idx_measurement_type", "measurement_type"),
    )

    def __repr__(self) -> str:
        return f"<Measurement(type='{self.measurement_type}', cycle={self.cycle_number}, pmax={self.pmax})>"


class VisualInspection(Base):
    """
    Visual inspection results table.
    Stores observations from visual inspections.
    """
    __tablename__ = "visual_inspections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False, default=0)
    inspection_type = Column(String(50), nullable=False)  # baseline, interim, final
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Corrosion observations
    visual_corrosion = Column(String(50))  # None, Minor, Moderate, Severe
    corrosion_locations = Column(JSON)  # List of locations
    corrosion_area_mm2 = Column(Float)  # Estimated area

    # Other defects
    delamination = Column(Boolean, default=False)
    delamination_locations = Column(JSON)
    discoloration = Column(Boolean, default=False)
    bubbles = Column(Boolean, default=False)
    cracks = Column(Boolean, default=False)
    hot_spots = Column(Boolean, default=False)

    # Documentation
    photos = Column(JSON)  # List of photo file paths
    notes = Column(Text)
    inspector = Column(String(100))

    # Relationships
    test_run = relationship("TestRun", back_populates="inspections")

    __table_args__ = (
        Index("idx_inspection_testrun_cycle", "test_run_id", "cycle_number"),
    )

    def __repr__(self) -> str:
        return f"<VisualInspection(cycle={self.cycle_number}, corrosion='{self.visual_corrosion}')>"


class QCResult(Base):
    """
    Quality control check results table.
    Stores results of QC checks performed on test data.
    """
    __tablename__ = "qc_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    criterion_id = Column(String(100), nullable=False)
    criterion_name = Column(String(200), nullable=False)
    criterion_type = Column(String(50))  # threshold, range, comparison, pattern
    severity = Column(SQLEnum(QCSeverity), nullable=False, default=QCSeverity.WARNING)

    passed = Column(Boolean, nullable=False)
    measured_value = Column(Float)
    expected_value = Column(Float)
    threshold = Column(Float)
    message = Column(Text)

    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    checked_by = Column(String(100))

    # Relationships
    test_run = relationship("TestRun", back_populates="qc_results")

    __table_args__ = (
        Index("idx_qc_testrun_severity", "test_run_id", "severity", "passed"),
    )

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"<QCResult(criterion='{self.criterion_name}', status='{status}')>"


class Equipment(Base):
    """
    Equipment/instrumentation table.
    Tracks equipment used in testing.
    """
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    calibration_required = Column(Boolean, default=False)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_interval_days = Column(Integer)

    location = Column(String(100))
    status = Column(String(50))  # available, in_use, maintenance, retired
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_equipment_type_status", "type", "status"),
    )

    def __repr__(self) -> str:
        return f"<Equipment(id='{self.equipment_id}', name='{self.name}', type='{self.type}')>"


class Sample(Base):
    """
    Sample/specimen table.
    Tracks samples being tested.
    """
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    serial_number = Column(String(100), index=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    technology = Column(String(100))  # mono-Si, poly-Si, CdTe, etc.

    # Physical characteristics
    length_mm = Column(Float)
    width_mm = Column(Float)
    thickness_mm = Column(Float)
    weight_g = Column(Float)
    area_m2 = Column(Float)

    # Electrical ratings
    rated_power_w = Column(Float)
    rated_voc_v = Column(Float)
    rated_isc_a = Column(Float)
    rated_vmp_v = Column(Float)
    rated_imp_a = Column(Float)

    # Tracking
    received_date = Column(DateTime)
    condition_on_receipt = Column(String(50))
    storage_location = Column(String(100))
    status = Column(String(50))  # available, testing, completed, damaged

    metadata = Column(JSON)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Sample(sample_id='{self.sample_id}', model='{self.model}')>"


class User(Base):
    """
    User table for operators and reviewers.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50))  # operator, reviewer, admin
    department = Column(String(100))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role}')>"
