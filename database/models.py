"""
Database Models for Solar PV Testing LIMS-QMS System
====================================================
Comprehensive SQLAlchemy models for all system entities.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from config.database import Base
import enum


# Enumerations
class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class RequestStatus(str, enum.Enum):
    """Service request status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestStatus(str, enum.Enum):
    """Test execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EquipmentStatus(str, enum.Enum):
    """Equipment status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    CALIBRATION_DUE = "calibration_due"
    OUT_OF_SERVICE = "out_of_service"


class InspectionStatus(str, enum.Enum):
    """Incoming inspection status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"


# Models
class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.TECHNICIAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    phone = Column(String(20))
    department = Column(String(50))

    # Relationships
    service_requests = relationship("ServiceRequest", back_populates="created_by_user")
    test_executions = relationship("TestExecution", back_populates="technician_user")
    reviewed_executions = relationship("TestExecution", back_populates="reviewer_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class ServiceRequest(Base):
    """Service request model - entry point for testing workflow"""
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    client_name = Column(String(100), nullable=False)
    client_email = Column(String(100))
    client_phone = Column(String(20))
    client_organization = Column(String(100))

    # Request details
    sample_type = Column(String(50))  # module, cell, array, etc.
    sample_count = Column(Integer, default=1)
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    serial_numbers = Column(JSON)  # List of serial numbers

    # Protocol selection
    requested_protocols = Column(JSON)  # List of protocol IDs
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    expected_completion_date = Column(DateTime)

    # Status tracking
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"))
    created_by_user = relationship("User", back_populates="service_requests")

    inspections = relationship("IncomingInspection", back_populates="service_request")
    test_executions = relationship("TestExecution", back_populates="service_request")

    # Additional fields
    notes = Column(Text)
    attachments = Column(JSON)  # List of file paths

    __table_args__ = (
        Index('idx_service_request_status', 'status'),
        Index('idx_service_request_created', 'created_at'),
    )

    def __repr__(self):
        return f"<ServiceRequest(number='{self.request_number}', status='{self.status}')>"


class IncomingInspection(Base):
    """Incoming inspection model - pre-test visual inspection"""
    __tablename__ = "incoming_inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_number = Column(String(50), unique=True, nullable=False, index=True)

    # Link to service request
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    service_request = relationship("ServiceRequest", back_populates="inspections")

    # Sample identification
    sample_id = Column(String(100), nullable=False)
    qr_code = Column(String(100), unique=True)

    # Visual inspection checklist
    physical_damage = Column(Boolean, default=False)
    physical_damage_notes = Column(Text)
    label_readable = Column(Boolean, default=True)
    connectors_intact = Column(Boolean, default=True)
    frame_condition = Column(String(50))  # excellent, good, fair, poor
    glass_condition = Column(String(50))
    backsheet_condition = Column(String(50))

    # Measurements
    length_mm = Column(Float)
    width_mm = Column(Float)
    thickness_mm = Column(Float)
    weight_kg = Column(Float)

    # Photos
    photos = Column(JSON)  # List of photo file paths

    # Status
    status = Column(Enum(InspectionStatus), default=InspectionStatus.PENDING)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    inspector_id = Column(Integer, ForeignKey("users.id"))

    # Results
    passed = Column(Boolean)
    remarks = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<IncomingInspection(number='{self.inspection_number}', status='{self.status}')>"


class Equipment(Base):
    """Equipment/instrument model"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # simulator, chamber, tester, etc.
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Status and availability
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.AVAILABLE)
    location = Column(String(100))

    # Calibration tracking
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    calibration_certificate = Column(String(200))

    # Maintenance tracking
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)
    maintenance_notes = Column(Text)

    # Technical specifications
    specifications = Column(JSON)  # Equipment-specific specs
    protocols_supported = Column(JSON)  # List of protocol IDs

    # Relationships
    bookings = relationship("EquipmentBooking", back_populates="equipment")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipment(code='{self.equipment_code}', name='{self.name}')>"


class EquipmentBooking(Base):
    """Equipment booking/reservation model"""
    __tablename__ = "equipment_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)

    # Equipment and user
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    equipment = relationship("Equipment", back_populates="bookings")

    booked_by_id = Column(Integer, ForeignKey("users.id"))
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"))

    # Booking period
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(Text)

    purpose = Column(Text)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_booking_period', 'start_time', 'end_time'),
        Index('idx_booking_equipment', 'equipment_id'),
    )

    def __repr__(self):
        return f"<EquipmentBooking(number='{self.booking_number}', equipment_id={self.equipment_id})>"


class TestProtocol(Base):
    """Test protocol definition model"""
    __tablename__ = "test_protocols"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String(20), unique=True, nullable=False, index=True)  # P1, P2, etc.
    name = Column(String(200), nullable=False)
    category = Column(String(50))  # performance, degradation, etc.
    description = Column(Text)

    # Protocol metadata
    standard_reference = Column(String(200))  # IEC standard reference
    version = Column(String(20))
    is_active = Column(Boolean, default=True)

    # Test configuration
    json_template_path = Column(String(200))  # Path to JSON template
    estimated_duration_hours = Column(Float)
    required_equipment = Column(JSON)  # List of equipment codes
    prerequisites = Column(JSON)  # List of prerequisite protocol IDs

    # Parameters and calculations
    input_parameters = Column(JSON)  # Parameter definitions
    calculation_formulas = Column(JSON)  # Calculation definitions
    acceptance_criteria = Column(JSON)  # Pass/fail criteria

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TestProtocol(id='{self.protocol_id}', name='{self.name}')>"


class TestExecution(Base):
    """Test execution instance model - tracks actual test runs"""
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_number = Column(String(50), unique=True, nullable=False, index=True)

    # Links
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    service_request = relationship("ServiceRequest", back_populates="test_executions")

    protocol_id = Column(Integer, ForeignKey("test_protocols.id"))
    protocol = relationship("TestProtocol", back_populates="test_executions")

    # Sample information
    sample_id = Column(String(100))
    qr_code = Column(String(100))

    # Execution tracking
    status = Column(Enum(TestStatus), default=TestStatus.NOT_STARTED)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_hours = Column(Float)

    # Personnel
    technician_id = Column(Integer, ForeignKey("users.id"))
    technician_user = relationship("User", foreign_keys=[technician_id], back_populates="test_executions")
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewer_user = relationship("User", foreign_keys=[reviewer_id], back_populates="reviewed_executions")

    # Test data
    input_data = Column(JSON)  # Input parameters
    raw_data = Column(JSON)  # Raw measurements
    processed_data = Column(JSON)  # Processed/calculated data
    results = Column(JSON)  # Final results

    # Quality control
    qa_passed = Column(Boolean)
    qa_notes = Column(Text)
    validation_errors = Column(JSON)

    # Results summary
    test_passed = Column(Boolean)
    failure_mode = Column(String(100))
    remarks = Column(Text)

    # Attachments and reports
    data_files = Column(JSON)  # Uploaded data files
    photos = Column(JSON)  # Test photos
    report_path = Column(String(200))  # Generated report PDF

    # Relationships
    test_data_points = relationship("TestData", back_populates="test_execution")
    equipment_bookings = relationship("EquipmentBooking", foreign_keys=[EquipmentBooking.test_execution_id])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_test_execution_status', 'status'),
        Index('idx_test_execution_protocol', 'protocol_id'),
    )

    def __repr__(self):
        return f"<TestExecution(number='{self.execution_number}', status='{self.status}')>"


class TestData(Base):
    """Detailed test data points model - stores time-series or measurement data"""
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True, index=True)

    # Link to test execution
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    test_execution = relationship("TestExecution", back_populates="test_data_points")

    # Data identification
    measurement_type = Column(String(100))  # voltage, current, temperature, etc.
    sequence_number = Column(Integer)  # For ordered data points
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Data values
    value = Column(Float)
    unit = Column(String(20))
    setpoint = Column(Float)  # Expected/target value
    tolerance = Column(Float)  # Acceptable deviation

    # Quality flags
    is_valid = Column(Boolean, default=True)
    quality_flag = Column(String(50))  # good, questionable, bad
    notes = Column(Text)

    # Metadata
    metadata = Column(JSON)  # Additional measurement metadata

    __table_args__ = (
        Index('idx_test_data_execution', 'test_execution_id'),
        Index('idx_test_data_type', 'measurement_type'),
    )

    def __repr__(self):
        return f"<TestData(type='{self.measurement_type}', value={self.value})>"


class AuditLog(Base):
    """Audit trail model - tracks all system changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who did what
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="audit_logs")
    action = Column(String(100), nullable=False)  # create, update, delete, etc.

    # What was affected
    table_name = Column(String(50))
    record_id = Column(Integer)

    # Change details
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    changes_summary = Column(Text)

    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    session_id = Column(String(100))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_table', 'table_name', 'record_id'),
        Index('idx_audit_log_created', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', table='{self.table_name}')>"


class QRCode(Base):
    """QR code mapping model - links QR codes to samples/equipment"""
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    qr_code = Column(String(100), unique=True, nullable=False, index=True)

    # What does this QR code point to?
    entity_type = Column(String(50))  # sample, equipment, service_request, etc.
    entity_id = Column(Integer)

    # QR code data
    data = Column(JSON)  # Additional data encoded in QR
    qr_image_path = Column(String(200))  # Path to QR code image

    # Status
    is_active = Column(Boolean, default=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by_id = Column(Integer, ForeignKey("users.id"))

    # Usage tracking
    first_scanned_at = Column(DateTime)
    last_scanned_at = Column(DateTime)
    scan_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_qr_entity', 'entity_type', 'entity_id'),
    )

    def __repr__(self):
        return f"<QRCode(code='{self.qr_code}', type='{self.entity_type}')>"
