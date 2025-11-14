"""
Database Models

SQLAlchemy models for storing protocol test data.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TestRunStatus(enum.Enum):
    """Test run status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class StepStatus(enum.Enum):
    """Step status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class QCSeverity(enum.Enum):
    """QC severity enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Protocol(Base):
    """Protocol definition table."""

    __tablename__ = 'protocols'

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    standard_reference = Column(String(100))
    description = Column(Text)
    definition_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    test_runs = relationship('TestRun', back_populates='protocol')

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', version='{self.version}')>"


class TestRun(Base):
    """Test run table."""

    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False)
    protocol_version = Column(String(20), nullable=False)
    status = Column(SQLEnum(TestRunStatus), nullable=False, default=TestRunStatus.PENDING)

    # Test metadata
    sample_id = Column(String(100), index=True)
    batch_id = Column(String(100), index=True)
    operator_id = Column(String(100))
    facility = Column(String(100))

    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_hours = Column(Float)

    # Results
    pass_fail_status = Column(String(20))
    grade = Column(String(10))
    metadata_json = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship('Protocol', back_populates='test_runs')
    steps = relationship('TestStep', back_populates='test_run', cascade='all, delete-orphan')
    measurements = relationship('Measurement', back_populates='test_run', cascade='all, delete-orphan')
    qc_flags = relationship('QCFlag', back_populates='test_run', cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        Index('idx_test_run_status_date', 'status', 'created_at'),
        Index('idx_test_run_sample', 'sample_id', 'protocol_id'),
    )

    def __repr__(self):
        return f"<TestRun(test_run_id='{self.test_run_id}', status='{self.status.value}')>"


class TestStep(Base):
    """Test step execution table."""

    __tablename__ = 'test_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    step_id = Column(Integer, nullable=False)
    substep_id = Column(Float, nullable=False)
    step_name = Column(String(200), nullable=False)
    step_type = Column(String(50), nullable=False)
    status = Column(SQLEnum(StepStatus), nullable=False, default=StepStatus.PENDING)

    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)

    # Data
    data_json = Column(JSON)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_run = relationship('TestRun', back_populates='steps')

    # Indexes
    __table_args__ = (
        Index('idx_step_run_id', 'test_run_id', 'step_id', 'substep_id'),
    )

    def __repr__(self):
        return f"<TestStep(step={self.step_id}.{self.substep_id}, status='{self.status.value}')>"


class Measurement(Base):
    """Measurement data table."""

    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    step_id = Column(Integer, nullable=False)
    substep_id = Column(Float, nullable=False)
    field_id = Column(String(100), nullable=False, index=True)
    field_label = Column(String(200))

    # Value (stored as appropriate type)
    value_numeric = Column(Float)
    value_text = Column(Text)
    value_boolean = Column(Boolean)
    value_datetime = Column(DateTime)
    value_json = Column(JSON)

    # Metadata
    unit = Column(String(50))
    measurement_time = Column(DateTime, default=datetime.utcnow)
    instrument_id = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship('TestRun', back_populates='measurements')

    # Indexes
    __table_args__ = (
        Index('idx_measurement_run_field', 'test_run_id', 'field_id'),
        Index('idx_measurement_step', 'test_run_id', 'step_id', 'substep_id'),
    )

    def __repr__(self):
        return f"<Measurement(field_id='{self.field_id}', step={self.step_id}.{self.substep_id})>"


class QCFlag(Base):
    """QC flag table."""

    __tablename__ = 'qc_flags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    rule_id = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(200))
    severity = Column(SQLEnum(QCSeverity), nullable=False)
    message = Column(Text, nullable=False)
    action = Column(String(100))

    # Context
    step_id = Column(Integer)
    substep_id = Column(Float)
    triggered_by_field = Column(String(100))
    field_value = Column(Float)

    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolution_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship('TestRun', back_populates='qc_flags')

    # Indexes
    __table_args__ = (
        Index('idx_qc_flag_run_severity', 'test_run_id', 'severity'),
    )

    def __repr__(self):
        return f"<QCFlag(rule_id='{self.rule_id}', severity='{self.severity.value}')>"


class Equipment(Base):
    """Equipment registry table."""

    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100), nullable=False)
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Calibration
    calibration_required = Column(Boolean, default=True)
    calibration_interval_months = Column(Integer)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_status = Column(String(50))

    # Specifications
    specifications_json = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True)
    location = Column(String(200))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', name='{self.name}')>"


class CalibrationRecord(Base):
    """Calibration record table."""

    __tablename__ = 'calibration_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    calibration_date = Column(DateTime, nullable=False)
    calibration_type = Column(String(100))
    performed_by = Column(String(100))
    certificate_number = Column(String(100))
    certificate_file_path = Column(String(500))

    # Results
    status = Column(String(50))  # passed, failed, conditional
    results_json = Column(JSON)
    notes = Column(Text)

    # Next calibration
    next_calibration_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalibrationRecord(equipment_id={self.equipment_id}, date='{self.calibration_date}')>"


class Sample(Base):
    """Sample/module registry table."""

    __tablename__ = 'samples'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    sample_type = Column(String(100), nullable=False)
    batch_id = Column(String(100), index=True)
    production_date = Column(DateTime)

    # Module specifics (for PV modules)
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))
    nameplate_power = Column(Float)  # Watts
    technology = Column(String(100))  # Mono-Si, Poly-Si, CdTe, etc.

    # Physical properties
    dimensions_json = Column(JSON)
    weight_kg = Column(Float)

    # Status
    is_active = Column(Boolean, default=True)
    current_location = Column(String(200))

    # Metadata
    metadata_json = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Sample(sample_id='{self.sample_id}', type='{self.sample_type}')>"
