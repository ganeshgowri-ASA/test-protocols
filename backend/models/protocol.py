"""
Database models for PV Testing Protocol Framework
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class TestStatus(str, enum.Enum):
    """Test execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"


class QCStatus(str, enum.Enum):
    """QC check status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_CHECKED = "not_checked"


class Protocol(Base):
    """Protocol template definition"""
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., PVTP-010
    protocol_name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    template_json = Column(JSON, nullable=False)  # Complete JSON template
    effective_date = Column(DateTime)
    author = Column(String(100))
    approver = Column(String(100))
    approval_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")


class TestExecution(Base):
    """Test execution instance"""
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(50), unique=True, index=True, nullable=False)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)

    # Sample information
    sample_id = Column(String(100), index=True, nullable=False)
    manufacturer = Column(String(200))
    model = Column(String(200))
    serial_number = Column(String(200))
    technology = Column(String(100))

    # Test execution details
    operator = Column(String(100), nullable=False)
    test_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)

    # Status
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    qc_status = Column(Enum(QCStatus), default=QCStatus.NOT_CHECKED)

    # Project management
    project_id = Column(String(100), index=True)
    customer = Column(String(200))

    # Data storage
    input_data = Column(JSON)  # All input parameters
    measurement_data = Column(JSON)  # All measurements
    analysis_results = Column(JSON)  # Analysis outputs
    qc_checks = Column(JSON)  # QC check results

    # Comments and notes
    notes = Column(Text)
    review_comments = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_executions")
    measurements = relationship("Measurement", back_populates="test_execution", cascade="all, delete-orphan")
    qc_results = relationship("QCResult", back_populates="test_execution", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="test_execution")
    nonconformances = relationship("Nonconformance", back_populates="test_execution")


class Measurement(Base):
    """Individual measurement data point"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)

    measurement_type = Column(String(100), nullable=False)  # e.g., "flash_measurement", "iv_curve_data"
    parameter_name = Column(String(100), nullable=False)
    value = Column(Float)
    value_text = Column(Text)  # For non-numeric values
    unit = Column(String(50))
    uncertainty = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Metadata
    raw_data = Column(JSON)  # Original raw measurement

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurements")


class QCResult(Base):
    """QC check result"""
    __tablename__ = "qc_results"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)

    check_id = Column(String(50), nullable=False)
    check_type = Column(String(50))  # automatic, manual
    parameter = Column(String(100))
    condition = Column(String(100))
    threshold = Column(Float)
    measured_value = Column(Float)

    status = Column(Enum(QCStatus), nullable=False)
    severity = Column(String(50))  # critical, major, warning, info
    message = Column(Text)
    action_taken = Column(Text)

    checked_by = Column(String(100))
    checked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="qc_results")


class Report(Base):
    """Generated report"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)

    report_type = Column(String(50), nullable=False)  # test_report, certificate, data_export
    format = Column(String(20), nullable=False)  # PDF, Excel, CSV
    file_path = Column(String(500))
    file_size = Column(Integer)  # bytes

    generated_by = Column(String(100))
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Metadata
    report_data = Column(JSON)  # Report configuration and parameters

    # Relationships
    test_execution = relationship("TestExecution", back_populates="reports")


class Nonconformance(Base):
    """Nonconformance/Issue tracking"""
    __tablename__ = "nonconformances"

    id = Column(Integer, primary_key=True, index=True)
    nc_id = Column(String(50), unique=True, index=True, nullable=False)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"))

    category = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Investigation
    root_cause = Column(Text)
    corrective_actions = Column(Text)
    preventive_actions = Column(Text)

    # Status tracking
    status = Column(String(50), default="open")  # open, investigating, resolved, closed
    opened_by = Column(String(100), nullable=False)
    opened_at = Column(DateTime, default=datetime.utcnow)
    assigned_to = Column(String(100))
    closed_by = Column(String(100))
    closed_at = Column(DateTime)

    # Verification
    verification_required = Column(Boolean, default=True)
    verified_by = Column(String(100))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="nonconformances")


class Equipment(Base):
    """Equipment/instrument tracking"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100))
    manufacturer = Column(String(200))
    model = Column(String(200))
    serial_number = Column(String(200))

    # Calibration
    calibration_required = Column(Boolean, default=True)
    calibration_interval_days = Column(Integer)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_lab = Column(String(200))

    # Status
    is_active = Column(Boolean, default=True)
    location = Column(String(200))

    # Maintenance
    maintenance_schedule = Column(JSON)
    maintenance_history = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """User/Operator management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True)
    full_name = Column(String(200))

    role = Column(String(50))  # operator, reviewer, manager, admin
    skills = Column(JSON)  # List of qualified skills
    certifications = Column(JSON)  # List of certifications

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
