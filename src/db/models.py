"""
Database models for test protocols
SQLAlchemy ORM models for storing test data
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TestStatus(enum.Enum):
    """Test execution status"""
    IN_PROGRESS = "in_progress"
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    INCOMPLETE = "incomplete"


class LoadType(enum.Enum):
    """Wind load type"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CYCLIC = "cyclic"


class WindLoadTest(Base):
    """Main wind load test record"""
    __tablename__ = 'wind_load_tests'

    id = Column(Integer, primary_key=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(String(50), default="WIND-001")
    protocol_version = Column(String(20), default="1.0.0")

    # Test metadata
    test_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    operator = Column(String(200), nullable=False)
    standard = Column(String(100), nullable=False)
    equipment_id = Column(String(100))
    calibration_date = Column(DateTime)

    # Sample information
    sample_id = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    serial_number = Column(String(200))
    technology = Column(String(50))
    rated_power = Column(Float)

    # Module dimensions (stored as JSON)
    dimensions = Column(JSON)

    # Test parameters
    load_type = Column(SQLEnum(LoadType), nullable=False)
    pressure = Column(Float, nullable=False)  # Pa
    duration = Column(Integer, nullable=False)  # seconds
    cycles = Column(Integer, nullable=False)
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %
    mounting_configuration = Column(String(100))

    # Acceptance criteria (stored as JSON)
    acceptance_criteria = Column(JSON)

    # Test results
    test_status = Column(SQLEnum(TestStatus), default=TestStatus.IN_PROGRESS)
    power_degradation = Column(Float)  # %
    max_deflection_measured = Column(Float)  # mm
    failure_modes = Column(JSON)  # List of failure modes
    notes = Column(Text)
    reviewer = Column(String(200))
    review_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    pre_test_measurements = relationship("PreTestMeasurement", back_populates="test", uselist=False, cascade="all, delete-orphan")
    post_test_measurements = relationship("PostTestMeasurement", back_populates="test", uselist=False, cascade="all, delete-orphan")
    cycle_measurements = relationship("CycleMeasurement", back_populates="test", cascade="all, delete-orphan")
    attachments = relationship("TestAttachment", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WindLoadTest(test_id='{self.test_id}', status='{self.test_status}')>"


class PreTestMeasurement(Base):
    """Pre-test baseline measurements"""
    __tablename__ = 'pre_test_measurements'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('wind_load_tests.id'), nullable=False, unique=True)

    # Visual inspection
    visual_inspection = Column(Text, nullable=False)

    # Electrical performance (I-V curve)
    voc = Column(Float, nullable=False)  # Open circuit voltage (V)
    isc = Column(Float, nullable=False)  # Short circuit current (A)
    vmp = Column(Float, nullable=False)  # Voltage at max power (V)
    imp = Column(Float, nullable=False)  # Current at max power (A)
    pmax = Column(Float, nullable=False)  # Maximum power (W)

    # Insulation resistance
    insulation_resistance = Column(Float, nullable=False)  # MΩ

    # Timestamp
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    test = relationship("WindLoadTest", back_populates="pre_test_measurements")

    def __repr__(self):
        return f"<PreTestMeasurement(test_id={self.test_id}, pmax={self.pmax}W)>"


class PostTestMeasurement(Base):
    """Post-test measurements"""
    __tablename__ = 'post_test_measurements'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('wind_load_tests.id'), nullable=False, unique=True)

    # Visual inspection
    visual_inspection = Column(Text, nullable=False)

    # Electrical performance (I-V curve)
    voc = Column(Float, nullable=False)  # Open circuit voltage (V)
    isc = Column(Float, nullable=False)  # Short circuit current (A)
    vmp = Column(Float, nullable=False)  # Voltage at max power (V)
    imp = Column(Float, nullable=False)  # Current at max power (A)
    pmax = Column(Float, nullable=False)  # Maximum power (W)

    # Insulation resistance
    insulation_resistance = Column(Float, nullable=False)  # MΩ

    # Defects observed (stored as JSON array)
    defects_observed = Column(JSON)

    # Timestamp
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    test = relationship("WindLoadTest", back_populates="post_test_measurements")

    def __repr__(self):
        return f"<PostTestMeasurement(test_id={self.test_id}, pmax={self.pmax}W)>"


class CycleMeasurement(Base):
    """Measurement data for each load test cycle"""
    __tablename__ = 'cycle_measurements'
    __table_args__ = (
        UniqueConstraint('test_id', 'cycle_number', name='uq_test_cycle'),
    )

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('wind_load_tests.id'), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False)

    # Measurements
    actual_pressure = Column(Float, nullable=False)  # Pa
    deflection_center = Column(Float, nullable=False)  # mm
    deflection_edges = Column(JSON)  # Array of edge deflection measurements (mm)

    # Observations
    observations = Column(Text)

    # Timestamp
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    test = relationship("WindLoadTest", back_populates="cycle_measurements")

    def __repr__(self):
        return f"<CycleMeasurement(test_id={self.test_id}, cycle={self.cycle_number})>"


class TestAttachment(Base):
    """Supporting documents and files for tests"""
    __tablename__ = 'test_attachments'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('wind_load_tests.id'), nullable=False, index=True)

    # File information
    filename = Column(String(500), nullable=False)
    filepath = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, video, data_file, report, certificate
    description = Column(Text)

    # Metadata
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(100))

    # Timestamp
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    test = relationship("WindLoadTest", back_populates="attachments")

    def __repr__(self):
        return f"<TestAttachment(test_id={self.test_id}, filename='{self.filename}')>"


class ProtocolConfig(Base):
    """Protocol configuration and versioning"""
    __tablename__ = 'protocol_configs'

    id = Column(Integer, primary_key=True)
    protocol_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)

    # Configuration data (stored as JSON)
    config_data = Column(JSON, nullable=False)
    schema_data = Column(JSON, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ProtocolConfig(protocol_id='{self.protocol_id}', version='{self.version}')>"


class TestAuditLog(Base):
    """Audit log for test modifications and actions"""
    __tablename__ = 'test_audit_logs'

    id = Column(Integer, primary_key=True)
    test_id = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # created, updated, approved, rejected, etc.
    user = Column(String(200), nullable=False)
    details = Column(JSON)  # Additional action details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TestAuditLog(test_id='{self.test_id}', action='{self.action}')>"
