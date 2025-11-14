"""
Database Models
SQLAlchemy models for test protocol data storage
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, Boolean, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ProtocolStatus(enum.Enum):
    """Protocol execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestResult(enum.Enum):
    """Test pass/fail result"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    NOT_EVALUATED = "not_evaluated"


class Protocol(Base):
    """Protocol definition metadata"""
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    version = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    effective_date = Column(DateTime)
    json_path = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(id={self.protocol_id}, code={self.code}, name={self.name})>"


class Module(Base):
    """PV Module information"""
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True)
    module_id = Column(String(100), unique=True, nullable=False, index=True)
    manufacturer = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    technology = Column(String(50), nullable=False)
    nameplate_power = Column(Float, nullable=False)
    serial_number = Column(String(100))
    manufacturing_date = Column(DateTime)
    dimensions_length = Column(Float)
    dimensions_width = Column(Float)
    dimensions_thickness = Column(Float)
    weight = Column(Float)
    additional_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("TestExecution", back_populates="module")

    def __repr__(self):
        return f"<Module(id={self.module_id}, manufacturer={self.manufacturer}, model={self.model})>"


class TestExecution(Base):
    """Test execution instance"""
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    test_date = Column(DateTime, nullable=False, index=True)
    operator = Column(String(200), nullable=False)
    status = Column(SQLEnum(ProtocolStatus), nullable=False, default=ProtocolStatus.NOT_STARTED)
    result = Column(SQLEnum(TestResult), default=TestResult.NOT_EVALUATED)
    severity_level = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_hours = Column(Float)

    # Test conditions
    h2s_concentration = Column(Float)
    temperature = Column(Float)
    relative_humidity = Column(Float)
    exposure_duration = Column(Float)

    # Measurements - Baseline
    baseline_voc = Column(Float)
    baseline_isc = Column(Float)
    baseline_vmp = Column(Float)
    baseline_imp = Column(Float)
    baseline_pmax = Column(Float)
    baseline_ff = Column(Float)
    baseline_insulation_mohm = Column(Float)
    baseline_weight_kg = Column(Float)

    # Measurements - Post-test
    post_voc = Column(Float)
    post_isc = Column(Float)
    post_vmp = Column(Float)
    post_imp = Column(Float)
    post_pmax = Column(Float)
    post_ff = Column(Float)
    post_insulation_mohm = Column(Float)
    post_weight_kg = Column(Float)

    # Degradation analysis
    degradation_pmax = Column(Float)
    degradation_voc = Column(Float)
    degradation_isc = Column(Float)
    degradation_ff = Column(Float)
    weight_change_pct = Column(Float)

    # Quality and acceptance
    environmental_stability_pass = Column(Boolean)
    critical_failures = Column(Integer, default=0)
    major_failures = Column(Integer, default=0)
    minor_failures = Column(Integer, default=0)

    # Additional data
    test_data = Column(JSON)
    analysis_results = Column(JSON)
    notes = Column(Text)
    abort_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="executions")
    module = relationship("Module", back_populates="executions")
    measurements = relationship("Measurement", back_populates="execution", cascade="all, delete-orphan")
    environmental_logs = relationship("EnvironmentalLog", back_populates="execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution(id={self.execution_id}, protocol={self.protocol_id}, status={self.status.value})>"


class Measurement(Base):
    """Individual measurement record"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    table_name = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(Float)
    value_text = Column(Text)
    unit = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    phase = Column(String(100))
    step = Column(String(50))
    notes = Column(Text)

    # Relationships
    execution = relationship("TestExecution", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(table={self.table_name}, field={self.field_name}, value={self.value})>"


class EnvironmentalLog(Base):
    """Environmental chamber conditions log"""
    __tablename__ = "environmental_logs"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    h2s_ppm = Column(Float)
    temperature_c = Column(Float)
    humidity_rh = Column(Float)
    chamber_pressure = Column(Float)
    notes = Column(Text)

    # Relationships
    execution = relationship("TestExecution", back_populates="environmental_logs")

    def __repr__(self):
        return f"<EnvironmentalLog(timestamp={self.timestamp}, h2s={self.h2s_ppm}ppm)>"


class CalibrationRecord(Base):
    """Equipment calibration tracking"""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True)
    equipment_name = Column(String(200), nullable=False)
    equipment_id = Column(String(100), nullable=False)
    calibration_date = Column(DateTime, nullable=False, index=True)
    next_calibration_date = Column(DateTime, nullable=False, index=True)
    calibration_authority = Column(String(200))
    certificate_number = Column(String(100))
    status = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalibrationRecord(equipment={self.equipment_name}, date={self.calibration_date})>"


class QualityEvent(Base):
    """Quality management system events"""
    __tablename__ = "quality_events"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"))
    event_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    status = Column(String(50), nullable=False)
    reported_by = Column(String(200), nullable=False)
    reported_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<QualityEvent(type={self.event_type}, severity={self.severity}, status={self.status})>"
