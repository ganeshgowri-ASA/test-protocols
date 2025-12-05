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


class IndustryType(str, enum.Enum):
    """Industry type enumeration"""
    SOLAR_PV_TESTING = "solar_pv_testing"
    RENEWABLE_ENERGY = "renewable_energy"
    ELECTRICAL_TESTING = "electrical_testing"
    MATERIALS_TESTING = "materials_testing"
    ENVIRONMENTAL_TESTING = "environmental_testing"
    CERTIFICATION_BODY = "certification_body"
    RESEARCH_INSTITUTION = "research_institution"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    OTHER = "other"


class SampleStatus(str, enum.Enum):
    """Sample lifecycle status"""
    RECEIVED = "received"
    INSPECTED = "inspected"
    ALLOCATED = "allocated"
    ASSIGNED = "assigned"
    IN_TEST = "in_test"
    COMPLETED = "completed"
    ANALYZED = "analyzed"
    REPORTED = "reported"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class DocumentCategory(str, enum.Enum):
    """Document category enumeration"""
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    RECORD = "record"
    SPECIFICATION = "specification"
    DRAWING = "drawing"
    CERTIFICATE = "certificate"
    REPORT = "report"
    MANUAL = "manual"
    POLICY = "policy"
    OTHER = "other"


class TrainingStatus(str, enum.Enum):
    """Training status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BOMItemType(str, enum.Enum):
    """BOM item type enumeration"""
    MATERIAL = "material"
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    SERVICE = "service"
    LABOR = "labor"


class ReceiptStatus(str, enum.Enum):
    """Sample receipt status"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    REJECTED = "rejected"


class InventoryStatus(str, enum.Enum):
    """Inventory status"""
    IN_STOCK = "in_stock"
    IN_TEST = "in_test"
    DISPOSED = "disposed"
    RETURNED = "returned"
    SHIPPED = "shipped"


class DocumentStatus(str, enum.Enum):
    """Document status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


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
    test_executions = relationship("TestExecution", foreign_keys="[TestExecution.technician_id]", back_populates="technician_user")
    reviewed_executions = relationship("TestExecution", foreign_keys="[TestExecution.reviewer_id]", back_populates="reviewer_user")
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

    # Sample quantity tracking (added to match migration 002)
    expected_sample_quantity = Column(Integer, default=1)
    actual_sample_quantity = Column(Integer)
    quantity_verified = Column(Boolean, default=False)
    receipt_id = Column(Integer, ForeignKey("sample_receipts.id"))

    __table_args__ = ({'extend_existing': True},
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
    qr_code = Column(Text, unique=True)

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

    # Link to sample receipt (added to match migration 002)
    receipt_id = Column(Integer, ForeignKey("sample_receipts.id"))

    # Allocation tracking (added to match migration 002)
    allocation_triggered = Column(Boolean, default=False)
    allocated_sample_id = Column(Integer)

    __table_args__ = ({'extend_existing': True},)

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

    __table_args__ = ({'extend_existing': True},
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
    qr_code = Column(Text, unique=True)

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

    __table_args__ = ({'extend_existing': True},
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
    extra_metadata = Column(JSON)  # Additional measurement metadata
    __table_args__ = ({'extend_existing': True},
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

    __table_args__ = ({'extend_existing': True},
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

    __table_args__ = ({'extend_existing': True},
        Index('idx_qr_entity', 'entity_type', 'entity_id'),
    )

    def __repr__(self):
        return f"<QRCode(code='{self.qr_code}', type='{self.entity_type}')>"


class CompanyProfile(Base):
    """Company profile model for organization settings"""
    __tablename__ = "company_profile"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(50), unique=True, nullable=False, index=True, default="DEFAULT")
    company_name = Column(String(200), nullable=False, default="Solar PV Testing Laboratory")
    industry_type = Column(Enum(IndustryType), default=IndustryType.SOLAR_PV_TESTING)
    tagline = Column(String(200))
    description = Column(Text)

    # Contact information
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    zip_code = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))

    # Business details
    established_date = Column(DateTime)
    employees_count = Column(Integer)
    tax_id = Column(String(50))
    registration_id = Column(String(50))

    # Accreditation and certification
    accreditation_number = Column(String(100))
    accreditation_body = Column(String(200))
    accreditation_valid_until = Column(DateTime)
    accreditation_details = Column(JSON)  # Detailed accreditation info
    accreditation_notes = Column(Text)
    certifications = Column(JSON)  # List of certifications

    # Branding
    logo_path = Column(String(200))
    logo_filename = Column(String(200))
    company_logo = Column(Text)  # Base64 encoded logo or binary data
    logo_content_type = Column(String(50))  # MIME type of the logo
    primary_color = Column(String(20))
    secondary_color = Column(String(20))

    # Settings
    settings = Column(JSON)  # Additional company-specific settings

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_default(cls, db):
        """Get or create the default company profile"""
        from sqlalchemy import select
        stmt = select(cls).where(cls.company_id == "DEFAULT")
        profile = db.execute(stmt).scalars().first()
        if not profile:
            profile = cls(company_id="DEFAULT")
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    def __repr__(self):
        return f"<CompanyProfile(company_id='{self.company_id}', name='{self.company_name}')>"


# ============================================================================
# SAMPLE MANAGEMENT MODELS
# ============================================================================

class SampleReceipt(Base):
    """Sample receipt model - tracks physical receipt of samples"""
    __tablename__ = "sample_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # Link to service request
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))

    # Receipt details
    received_date = Column(DateTime, default=datetime.utcnow)
    received_by_id = Column(Integer, ForeignKey("users.id"))

    # Client/Source information
    client_name = Column(String(100))
    client_reference = Column(String(100))
    courier_name = Column(String(100))
    tracking_number = Column(String(100))

    # Package details
    package_count = Column(Integer, default=1)
    package_condition = Column(String(50))  # good, damaged, sealed, opened
    package_photos = Column(JSON)

    # Sample counts
    expected_sample_count = Column(Integer)
    actual_sample_count = Column(Integer)
    quantity_mismatch = Column(Boolean, default=False)
    mismatch_notes = Column(Text)

    # Approval workflow
    requires_supervisor_approval = Column(Boolean, default=False)
    supervisor_approved = Column(Boolean)
    supervisor_id = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)

    # Status and notes
    status = Column(String(20), default="pending")
    remarks = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    received_by_user = relationship("User", foreign_keys=[received_by_id])
    supervisor_user = relationship("User", foreign_keys=[supervisor_id])
    samples = relationship("Sample", back_populates="receipt")

    __table_args__ = ({'extend_existing': True},
        Index('idx_sample_receipts_service_request', 'service_request_id'),
        Index('idx_sample_receipts_received_date', 'received_date'),
        Index('idx_sample_receipts_status', 'status'),
    )

    def __repr__(self):
        return f"<SampleReceipt(number='{self.receipt_number}', status='{self.status}')>"


class Sample(Base):
    """Core sample tracking model with auto-generated IDs"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)

    # Auto-generated identifiers
    sample_id = Column(String(50), unique=True, nullable=False, index=True)  # SAMPLE-YYYY-XXXXX
    project_id = Column(String(50), index=True)  # PROJECT-YYYY-XXXXX

    # Links
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))
    receipt_id = Column(Integer, ForeignKey("sample_receipts.id"))
    inspection_id = Column(Integer, ForeignKey("incoming_inspections.id"))

    # Sample details
    sample_type = Column(String(50))
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    serial_number = Column(String(100))
    batch_number = Column(String(100))

    # Physical properties
    length_mm = Column(Float)
    width_mm = Column(Float)
    thickness_mm = Column(Float)
    weight_kg = Column(Float)

    # QR Code
    qr_code = Column(String(200), unique=True)
    qr_code_image_path = Column(String(200))
    qr_data = Column(JSON)

    # Current status and location
    status = Column(Enum(SampleStatus), default=SampleStatus.RECEIVED)
    current_location = Column(String(100))
    storage_location = Column(String(100))

    # Workflow tracking
    allocation_date = Column(DateTime)
    allocated_by_id = Column(Integer, ForeignKey("users.id"))

    # Test assignment tracking
    assigned_protocol_ids = Column(JSON)
    current_test_id = Column(Integer)
    tests_completed = Column(Integer, default=0)
    tests_total = Column(Integer, default=0)

    # Results summary
    overall_result = Column(String(20))
    result_summary = Column(Text)

    # Metadata
    specifications = Column(JSON)
    notes = Column(Text)
    photos = Column(JSON)
    custody_history = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    disposed_at = Column(DateTime)

    # Relationships
    receipt = relationship("SampleReceipt", back_populates="samples")
    allocated_by_user = relationship("User", foreign_keys=[allocated_by_id])
    status_history = relationship("SampleStatusHistory", back_populates="sample")
    route_cards = relationship("RouteCard", back_populates="sample")
    test_assignments = relationship("SampleTestAssignment", back_populates="sample")
    inventory_records = relationship("SampleInventory", back_populates="sample")

    __table_args__ = ({'extend_existing': True},
        Index('idx_samples_sample_id', 'sample_id'),
        Index('idx_samples_project_id', 'project_id'),
        Index('idx_samples_service_request', 'service_request_id'),
        Index('idx_samples_status', 'status'),
        Index('idx_samples_qr_code', 'qr_code'),
    )

    def __repr__(self):
        return f"<Sample(id='{self.sample_id}', status='{self.status}')>"


class SampleStatusHistory(Base):
    """Complete audit trail of sample status changes"""
    __tablename__ = "sample_status_history"

    id = Column(Integer, primary_key=True, index=True)

    # Sample reference
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)

    # Status change details
    previous_status = Column(String(20))
    new_status = Column(String(20), nullable=False)

    # Location change
    previous_location = Column(String(100))
    new_location = Column(String(100))

    # Who made the change
    changed_by_id = Column(Integer, ForeignKey("users.id"))
    changed_by_name = Column(String(100))

    # How it was changed
    change_source = Column(String(50))  # manual, qr_scan, system, workflow
    qr_scan_id = Column(Integer)

    # Additional info
    reason = Column(Text)
    notes = Column(Text)
    metadata = Column(JSON)

    # Timestamp
    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="status_history")
    changed_by_user = relationship("User", foreign_keys=[changed_by_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_sample_status_history_sample', 'sample_id'),
        Index('idx_sample_status_history_changed_at', 'changed_at'),
        Index('idx_sample_status_history_status', 'new_status'),
    )

    def __repr__(self):
        return f"<SampleStatusHistory(sample_id={self.sample_id}, status='{self.new_status}')>"


class RouteCard(Base):
    """Workflow documentation for samples"""
    __tablename__ = "route_cards"

    id = Column(Integer, primary_key=True, index=True)
    route_card_number = Column(String(50), unique=True, nullable=False, index=True)

    # Sample reference
    sample_id = Column(Integer, ForeignKey("samples.id"))
    project_id = Column(String(50))

    # Service request link
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))

    # Route card details
    title = Column(String(200))
    description = Column(Text)

    # Workflow steps
    workflow_steps = Column(JSON)
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer)

    # Assigned protocols
    assigned_protocols = Column(JSON)

    # Timeline
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # PDF generation
    pdf_path = Column(String(200))
    pdf_generated_at = Column(DateTime)

    # Status
    status = Column(String(20), default="draft")

    # Personnel
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="route_cards")
    created_by_user = relationship("User", foreign_keys=[created_by_id])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_route_cards_sample', 'sample_id'),
        Index('idx_route_cards_service_request', 'service_request_id'),
        Index('idx_route_cards_status', 'status'),
    )

    def __repr__(self):
        return f"<RouteCard(number='{self.route_card_number}', status='{self.status}')>"


class SampleTestAssignment(Base):
    """Assignment of samples to specific tests"""
    __tablename__ = "sample_test_assignments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_number = Column(String(50), unique=True, nullable=False, index=True)

    # Links
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"))
    protocol_id = Column(Integer, ForeignKey("test_protocols.id"), nullable=False)
    route_card_id = Column(Integer, ForeignKey("route_cards.id"))

    # Assignment details
    sequence_number = Column(Integer)
    priority = Column(Integer, default=5)

    # Personnel
    assigned_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))

    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)

    # Equipment booking
    equipment_booking_id = Column(Integer, ForeignKey("equipment_bookings.id"))
    required_equipment = Column(JSON)

    # Status
    status = Column(String(20), default="pending")

    # Results
    test_passed = Column(Boolean)
    result_summary = Column(Text)

    # Notes
    instructions = Column(Text)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="test_assignments")
    protocol = relationship("TestProtocol")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by_id])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_sample_test_assignments_sample', 'sample_id'),
        Index('idx_sample_test_assignments_protocol', 'protocol_id'),
        Index('idx_sample_test_assignments_status', 'status'),
    )

    def __repr__(self):
        return f"<SampleTestAssignment(number='{self.assignment_number}', status='{self.status}')>"


class SampleInventory(Base):
    """Inventory tracking and storage management"""
    __tablename__ = "sample_inventory"

    id = Column(Integer, primary_key=True, index=True)

    # Sample reference
    sample_id = Column(Integer, ForeignKey("samples.id"))
    sample_id_code = Column(String(50))

    # Location tracking
    storage_area = Column(String(50))
    storage_zone = Column(String(50))
    storage_rack = Column(String(50))
    storage_shelf = Column(String(50))
    storage_position = Column(String(50))
    full_location_path = Column(String(200))

    # Physical status
    condition = Column(String(50))
    condition_notes = Column(Text)
    photos = Column(JSON)

    # Inventory status
    inventory_status = Column(Enum(InventoryStatus), default=InventoryStatus.IN_STOCK)

    # Check in/out tracking
    checked_out = Column(Boolean, default=False)
    checked_out_by_id = Column(Integer, ForeignKey("users.id"))
    checked_out_at = Column(DateTime)
    checked_out_reason = Column(Text)
    expected_return = Column(DateTime)

    # Return tracking
    checked_in_by_id = Column(Integer, ForeignKey("users.id"))
    checked_in_at = Column(DateTime)

    # Disposal/Return
    disposal_date = Column(DateTime)
    disposal_method = Column(String(50))
    disposal_notes = Column(Text)
    return_date = Column(DateTime)
    return_tracking_number = Column(String(100))

    # Last inventory count
    last_inventory_date = Column(DateTime)
    inventoried_by_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="inventory_records")
    checked_out_by_user = relationship("User", foreign_keys=[checked_out_by_id])
    checked_in_by_user = relationship("User", foreign_keys=[checked_in_by_id])
    inventoried_by_user = relationship("User", foreign_keys=[inventoried_by_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_sample_inventory_sample', 'sample_id'),
        Index('idx_sample_inventory_location', 'storage_area', 'storage_zone', 'storage_rack'),
        Index('idx_sample_inventory_status', 'inventory_status'),
    )

    def __repr__(self):
        return f"<SampleInventory(sample='{self.sample_id_code}', location='{self.full_location_path}')>"


# ============================================================================
# STAFF TRAINING MODELS
# ============================================================================

class StaffTraining(Base):
    """Training management and competency tracking"""
    __tablename__ = "staff_training"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(String(50), unique=True, nullable=False, index=True)

    # Training details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # safety, equipment, protocol, qms, general
    training_type = Column(String(50))  # initial, refresher, advanced, certification

    # Requirements
    required_for_roles = Column(JSON)
    required_for_protocols = Column(JSON)
    prerequisite_trainings = Column(JSON)

    # Content
    materials_path = Column(String(200))
    duration_hours = Column(Float)
    assessment_required = Column(Boolean, default=True)
    passing_score = Column(Float, default=80.0)

    # Validity
    valid_months = Column(Integer, default=12)

    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by_id])
    training_records = relationship("StaffTrainingRecord", back_populates="training")

    __table_args__ = ({'extend_existing': True},
        Index('idx_staff_training_category', 'category'),
        Index('idx_staff_training_active', 'is_active'),
    )

    def __repr__(self):
        return f"<StaffTraining(id='{self.training_id}', title='{self.title}')>"


class StaffTrainingRecord(Base):
    """Individual training completion records"""
    __tablename__ = "staff_training_records"

    id = Column(Integer, primary_key=True, index=True)
    record_number = Column(String(50), unique=True, nullable=False, index=True)

    # Links
    training_id = Column(Integer, ForeignKey("staff_training.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Training session
    scheduled_date = Column(DateTime)
    completion_date = Column(DateTime)
    trainer_id = Column(Integer, ForeignKey("users.id"))
    trainer_name = Column(String(100))

    # Status
    status = Column(Enum(TrainingStatus), default=TrainingStatus.SCHEDULED)

    # Assessment
    assessment_score = Column(Float)
    assessment_passed = Column(Boolean)
    assessment_date = Column(DateTime)
    assessment_notes = Column(Text)

    # Certificate
    certificate_number = Column(String(50))
    certificate_path = Column(String(200))

    # Validity tracking
    expiry_date = Column(DateTime)
    is_current = Column(Boolean, default=False)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    training = relationship("StaffTraining", back_populates="training_records")
    user = relationship("User", foreign_keys=[user_id])
    trainer = relationship("User", foreign_keys=[trainer_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_staff_training_records_training', 'training_id'),
        Index('idx_staff_training_records_user', 'user_id'),
        Index('idx_staff_training_records_status', 'status'),
        Index('idx_staff_training_records_expiry', 'expiry_date'),
    )

    def __repr__(self):
        return f"<StaffTrainingRecord(number='{self.record_number}', status='{self.status}')>"


# ============================================================================
# DOCUMENT MANAGEMENT MODELS
# ============================================================================

class Document(Base):
    """Document control and version management"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(50), unique=True, nullable=False, index=True)

    # Document details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(DocumentCategory), default=DocumentCategory.OTHER)
    document_type = Column(String(50))

    # Classification
    department = Column(String(50))
    process_area = Column(String(100))
    tags = Column(JSON)

    # Version control
    version = Column(String(20), default="1.0")
    revision_number = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    previous_version_id = Column(Integer, ForeignKey("documents.id"))

    # File storage
    file_path = Column(String(200))
    file_name = Column(String(200))
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64))

    # Review and approval
    author_id = Column(Integer, ForeignKey("users.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    review_date = Column(DateTime)
    approval_date = Column(DateTime)

    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)

    # Effective dates
    effective_date = Column(DateTime)
    next_review_date = Column(DateTime)
    obsolete_date = Column(DateTime)

    # Access control
    access_level = Column(String(20), default="internal")
    allowed_roles = Column(JSON)
    distribution_list = Column(JSON)

    # Notes
    change_summary = Column(Text)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approver_id])
    previous_version = relationship("Document", remote_side=[id])
    access_logs = relationship("DocumentAccessLog", back_populates="document")

    __table_args__ = ({'extend_existing': True},
        Index('idx_documents_number', 'document_number'),
        Index('idx_documents_category', 'category'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_current', 'is_current_version'),
    )

    def __repr__(self):
        return f"<Document(number='{self.document_number}', version='{self.version}')>"


class DocumentAccessLog(Base):
    """Track document access and downloads"""
    __tablename__ = "document_access_log"

    id = Column(Integer, primary_key=True, index=True)

    # Document reference
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # User
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String(100))

    # Access details
    access_type = Column(String(20))  # view, download, print, edit
    access_timestamp = Column(DateTime, default=datetime.utcnow)

    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(200))

    # Notes
    notes = Column(Text)

    # Relationships
    document = relationship("Document", back_populates="access_logs")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_document_access_log_document', 'document_id'),
        Index('idx_document_access_log_user', 'user_id'),
        Index('idx_document_access_log_timestamp', 'access_timestamp'),
    )

    def __repr__(self):
        return f"<DocumentAccessLog(doc_id={self.document_id}, type='{self.access_type}')>"


# ============================================================================
# BOM MANAGEMENT MODELS
# ============================================================================

class BOMItem(Base):
    """Bill of Materials item"""
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True)

    # Item details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    item_type = Column(Enum(BOMItemType), default=BOMItemType.MATERIAL)
    category = Column(String(50))

    # Specifications
    specifications = Column(JSON)
    unit = Column(String(20))

    # Inventory
    current_stock = Column(Float, default=0)
    minimum_stock = Column(Float, default=0)
    reorder_point = Column(Float, default=0)
    reorder_quantity = Column(Float)

    # Cost tracking
    unit_cost = Column(Float, default=0)
    currency = Column(String(10), default="USD")
    cost_center = Column(String(50))

    # Supplier info
    supplier_name = Column(String(100))
    supplier_code = Column(String(50))
    supplier_part_number = Column(String(50))
    lead_time_days = Column(Integer)

    # Shelf life
    has_expiry = Column(Boolean, default=False)
    shelf_life_days = Column(Integer)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol_requirements = relationship("BOMProtocolRequirement", back_populates="bom_item")
    usage_logs = relationship("BOMUsageLog", back_populates="bom_item")

    __table_args__ = ({'extend_existing': True},
        Index('idx_bom_items_code', 'item_code'),
        Index('idx_bom_items_type', 'item_type'),
        Index('idx_bom_items_category', 'category'),
    )

    def __repr__(self):
        return f"<BOMItem(code='{self.item_code}', name='{self.name}')>"


class BOMProtocolRequirement(Base):
    """Link BOM items to test protocols"""
    __tablename__ = "bom_protocol_requirements"

    id = Column(Integer, primary_key=True, index=True)

    # Links
    protocol_id = Column(Integer, ForeignKey("test_protocols.id"), nullable=False)
    bom_item_id = Column(Integer, ForeignKey("bom_items.id"), nullable=False)

    # Requirement details
    quantity_per_test = Column(Float, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    protocol = relationship("TestProtocol")
    bom_item = relationship("BOMItem", back_populates="protocol_requirements")

    __table_args__ = ({'extend_existing': True},
        UniqueConstraint('protocol_id', 'bom_item_id', name='uq_protocol_bom_item'),
        Index('idx_bom_protocol_req_protocol', 'protocol_id'),
        Index('idx_bom_protocol_req_item', 'bom_item_id'),
    )

    def __repr__(self):
        return f"<BOMProtocolRequirement(protocol={self.protocol_id}, item={self.bom_item_id})>"


class BOMUsageLog(Base):
    """Track consumption of BOM items"""
    __tablename__ = "bom_usage_log"

    id = Column(Integer, primary_key=True, index=True)

    # Item reference
    bom_item_id = Column(Integer, ForeignKey("bom_items.id"), nullable=False)

    # Usage context
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"))
    sample_id = Column(Integer, ForeignKey("samples.id"))
    service_request_id = Column(Integer, ForeignKey("service_requests.id"))

    # Usage details
    quantity_used = Column(Float, nullable=False)
    usage_type = Column(String(20))  # consumed, returned, wasted

    # User
    used_by_id = Column(Integer, ForeignKey("users.id"))

    # Lot/Batch tracking
    lot_number = Column(String(50))
    expiry_date = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Timestamp
    used_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bom_item = relationship("BOMItem", back_populates="usage_logs")
    used_by_user = relationship("User", foreign_keys=[used_by_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_bom_usage_log_item', 'bom_item_id'),
        Index('idx_bom_usage_log_test', 'test_execution_id'),
        Index('idx_bom_usage_log_date', 'used_at'),
    )

    def __repr__(self):
        return f"<BOMUsageLog(item={self.bom_item_id}, qty={self.quantity_used})>"


# ============================================================================
# QR SCAN LOG MODEL
# ============================================================================

class QRScanLog(Base):
    """Log all QR code scans for tracking"""
    __tablename__ = "qr_scan_log"

    id = Column(Integer, primary_key=True, index=True)

    # QR code data
    qr_code = Column(String(200), nullable=False)
    decoded_data = Column(JSON)

    # Entity reference
    entity_type = Column(String(50))
    entity_id = Column(Integer)

    # Scan details
    scanned_by_id = Column(Integer, ForeignKey("users.id"))
    scanned_by_name = Column(String(100))
    scan_timestamp = Column(DateTime, default=datetime.utcnow)

    # Location at scan
    scan_location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)

    # Device info
    device_type = Column(String(50))
    device_info = Column(String(200))

    # Action taken
    action_type = Column(String(50))
    action_result = Column(String(50))

    # Status update triggered
    status_changed = Column(Boolean, default=False)
    previous_status = Column(String(20))
    new_status = Column(String(20))

    # Notes
    notes = Column(Text)

    # Relationships
    scanned_by_user = relationship("User", foreign_keys=[scanned_by_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_qr_scan_log_qr_code', 'qr_code'),
        Index('idx_qr_scan_log_entity', 'entity_type', 'entity_id'),
        Index('idx_qr_scan_log_timestamp', 'scan_timestamp'),
    )

    def __repr__(self):
        return f"<QRScanLog(qr='{self.qr_code[:20]}...', action='{self.action_type}')>"


# ============================================================================
# CALIBRATION RECORDS MODEL
# ============================================================================

class CalibrationRecord(Base):
    """Calibration records for equipment"""
    __tablename__ = "calibration_records"

    id = Column(Integer, primary_key=True, index=True)
    calibration_number = Column(String(50), unique=True, nullable=False, index=True)

    # Equipment reference
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)

    # Calibration details
    calibration_date = Column(DateTime, nullable=False)
    next_calibration_date = Column(DateTime)
    calibration_type = Column(String(50))

    # Provider
    performed_by = Column(String(100))
    provider_certificate = Column(String(100))
    technician_name = Column(String(100))

    # Results
    calibration_passed = Column(Boolean)
    deviation_found = Column(Boolean, default=False)
    deviation_details = Column(Text)
    adjustment_made = Column(Boolean, default=False)
    adjustment_details = Column(Text)

    # Documentation
    certificate_number = Column(String(100))
    certificate_path = Column(String(200))
    report_path = Column(String(200))

    # Traceability
    reference_standards = Column(JSON)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    equipment = relationship("Equipment")
    created_by_user = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = ({'extend_existing': True},
        Index('idx_calibration_records_equipment', 'equipment_id'),
        Index('idx_calibration_records_date', 'calibration_date'),
        Index('idx_calibration_records_next', 'next_calibration_date'),
    )

    def __repr__(self):
        return f"<CalibrationRecord(number='{self.calibration_number}', equipment={self.equipment_id})>"
