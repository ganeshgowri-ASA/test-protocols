"""
Database Models for PV Testing Protocol Framework
SQLAlchemy ORM models for storing protocols, test runs, and results
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey,
    Table, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ProtocolCategory(str, enum.Enum):
    """Protocol category enumeration"""
    DEGRADATION = "Degradation"
    PERFORMANCE = "Performance"
    MECHANICAL = "Mechanical"
    THERMAL = "Thermal"
    ELECTRICAL = "Electrical"
    SAFETY = "Safety"


class TestStatus(str, enum.Enum):
    """Test run status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, enum.Enum):
    """Severity level for defects and issues"""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


# Association table for many-to-many relationship between protocols and tags
protocol_tags = Table(
    'protocol_tags',
    Base.metadata,
    Column('protocol_id', Integer, ForeignKey('protocols.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Protocol(Base):
    """Protocol definition model"""
    __tablename__ = 'protocols'

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(SQLEnum(ProtocolCategory), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text)
    standard_reference = Column(String(255))

    # JSON fields for flexible configuration
    test_conditions = Column(JSON)
    input_parameters = Column(JSON)
    measurements_schema = Column(JSON)
    qc_checks = Column(JSON)
    pass_fail_criteria = Column(JSON)
    visualization_config = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=protocol_tags, back_populates="protocols")

    def __repr__(self):
        return f"<Protocol(id={self.protocol_id}, name={self.name}, version={self.version})>"


class TestRun(Base):
    """Test run instance model"""
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False)

    # Test information
    module_id = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(255))
    model_number = Column(String(100))
    cell_technology = Column(String(50))

    # Test execution
    status = Column(SQLEnum(TestStatus), default=TestStatus.PENDING, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    operator_id = Column(String(100))
    chamber_id = Column(String(50))

    # Initial electrical parameters
    initial_pmax_w = Column(Float)
    initial_isc_a = Column(Float)
    initial_voc_v = Column(Float)
    initial_ff_percent = Column(Float)

    # Final results (cached from analysis)
    final_pmax_w = Column(Float)
    power_degradation_percent = Column(Float)
    qc_passed = Column(Boolean)
    test_passed = Column(Boolean)

    # JSON fields
    input_data = Column(JSON)
    qc_details = Column(JSON)
    pass_fail_results = Column(JSON)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="test_run", uselist=False, cascade="all, delete-orphan")
    images = relationship("TestImage", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun(run_id={self.run_id}, module={self.module_id}, status={self.status.value})>"


class Measurement(Base):
    """Individual measurement data point"""
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)

    # Timing
    inspection_hour = Column(Integer, nullable=False)
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)

    # Visual inspection
    visual_severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.NONE)
    affected_cells_count = Column(Integer, default=0)
    affected_area_percent = Column(Float, default=0.0)

    # Electrical measurements
    pmax_w = Column(Float)
    isc_a = Column(Float)
    voc_v = Column(Float)
    ff_percent = Column(Float)
    impp_a = Column(Float)
    vmpp_v = Column(Float)

    # Calculated fields
    power_degradation_percent = Column(Float)
    isc_degradation_percent = Column(Float)
    voc_degradation_percent = Column(Float)
    ff_degradation_percent = Column(Float)

    # Additional data
    notes = Column(Text)
    measurement_data = Column(JSON)  # For additional custom measurements

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(run={self.test_run_id}, hour={self.inspection_hour})>"


class AnalysisResult(Base):
    """Analysis results for a test run"""
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, unique=True)

    # Degradation analysis
    total_power_degradation_percent = Column(Float)
    total_isc_degradation_percent = Column(Float)
    total_voc_degradation_percent = Column(Float)
    total_ff_degradation_percent = Column(Float)

    # Snail trail specific metrics
    final_affected_area_percent = Column(Float)
    final_affected_cells = Column(Integer)
    progression_rate_percent_per_hour = Column(Float)
    final_severity = Column(SQLEnum(SeverityLevel))

    # Statistical analysis
    power_degradation_rate = Column(Float)  # %/hour
    snail_trail_progression_slope = Column(Float)
    correlation_snail_trail_power = Column(Float)
    regression_r_squared = Column(Float)

    # Full analysis data (JSON)
    detailed_analysis = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(run={self.test_run_id}, power_deg={self.total_power_degradation_percent}%)>"


class TestImage(Base):
    """Images captured during testing"""
    __tablename__ = 'test_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)

    # Image metadata
    image_type = Column(String(50))  # 'visual', 'el', 'ir', etc.
    inspection_hour = Column(Integer)
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255))

    # Image properties
    width_px = Column(Integer)
    height_px = Column(Integer)
    file_size_bytes = Column(Integer)
    format = Column(String(10))  # 'jpg', 'png', 'tiff'

    # Annotations
    description = Column(Text)
    annotations = Column(JSON)  # For storing bounding boxes, labels, etc.

    captured_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="images")

    def __repr__(self):
        return f"<TestImage(type={self.image_type}, run={self.test_run_id})>"


class Tag(Base):
    """Tags for categorizing protocols"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    protocols = relationship("Protocol", secondary=protocol_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(name={self.name})>"


class User(Base):
    """User/Operator model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    full_name = Column(String(255))
    role = Column(String(50))  # 'operator', 'engineer', 'admin'

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


class AuditLog(Base):
    """Audit trail for all operations"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(String(100), index=True)

    # Action details
    action = Column(String(100), nullable=False)  # 'create', 'update', 'delete', 'run'
    entity_type = Column(String(50), nullable=False)  # 'protocol', 'test_run', etc.
    entity_id = Column(String(100))

    # Change tracking
    changes = Column(JSON)  # Before/after values
    description = Column(Text)

    # Client information
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    def __repr__(self):
        return f"<AuditLog(action={self.action}, entity={self.entity_type}, user={self.user_id})>"
