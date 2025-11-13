"""
SQLAlchemy Models for PV Testing LIMS-QMS
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text,
    ForeignKey, CheckConstraint, DECIMAL, Enum as SQLEnum, JSON, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))

    # Relationships
    service_requests = relationship("ServiceRequest", back_populates="creator", foreign_keys="ServiceRequest.created_by")
    test_executions = relationship("TestExecution", back_populates="technician", foreign_keys="TestExecution.technician_id")

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'manager', 'technician', 'viewer')", name='check_user_role'),
    )

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class Protocol(Base):
    """Protocol model for test procedures"""
    __tablename__ = 'protocols'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    standard_reference = Column(String(255))
    description = Column(Text)
    test_conditions = Column(JSONB)
    input_parameters = Column(JSONB)
    measurement_points = Column(JSONB)
    calculations = Column(JSONB)
    acceptance_criteria = Column(JSONB)
    equipment_required = Column(JSONB)
    estimated_duration = Column(Integer)  # minutes
    safety_precautions = Column(JSONB)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")

    __table_args__ = (
        CheckConstraint("category IN ('performance', 'degradation', 'environmental', 'mechanical', 'safety')",
                       name='check_protocol_category'),
    )

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', name='{self.name}')>"


class ServiceRequest(Base):
    """Service Request model"""
    __tablename__ = 'service_requests'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_company = Column(String(255))
    customer_address = Column(Text)
    request_date = Column(Date, nullable=False, default=datetime.utcnow().date(), index=True)
    required_date = Column(Date)
    status = Column(String(50), nullable=False, default='pending', index=True)
    priority = Column(String(20), default='normal')
    total_quote = Column(DECIMAL(10, 2))
    currency = Column(String(3), default='USD')
    notes = Column(Text)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    creator = relationship("User", back_populates="service_requests", foreign_keys=[created_by])
    samples = relationship("Sample", back_populates="service_request")
    test_executions = relationship("TestExecution", back_populates="service_request")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'quoted', 'approved', 'in_progress', 'completed', 'cancelled')",
                       name='check_service_request_status'),
        CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')",
                       name='check_service_request_priority'),
    )

    def __repr__(self):
        return f"<ServiceRequest(request_number='{self.request_number}', customer='{self.customer_name}')>"


class Sample(Base):
    """Sample model for test specimens"""
    __tablename__ = 'samples'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(String(50), unique=True, nullable=False, index=True)
    service_request_id = Column(UUID(as_uuid=True), ForeignKey('service_requests.id'), index=True)
    manufacturer = Column(String(255), index=True)
    model = Column(String(255), index=True)
    serial_number = Column(String(255))
    technology = Column(String(100))
    rated_power = Column(DECIMAL(10, 2))
    dimensions_length = Column(DECIMAL(10, 2))
    dimensions_width = Column(DECIMAL(10, 2))
    dimensions_height = Column(DECIMAL(10, 2))
    weight = Column(DECIMAL(10, 3))
    manufacturing_date = Column(Date)
    reception_date = Column(Date, nullable=False, default=datetime.utcnow().date())
    condition = Column(String(50))
    storage_location = Column(String(100))
    barcode = Column(String(100))
    qr_code = Column(Text)
    photos = Column(JSONB)
    inspection_notes = Column(Text)
    inspected_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    inspected_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="samples")
    test_executions = relationship("TestExecution", back_populates="sample")

    __table_args__ = (
        CheckConstraint("condition IN ('excellent', 'good', 'fair', 'damaged')",
                       name='check_sample_condition'),
    )

    def __repr__(self):
        return f"<Sample(sample_id='{self.sample_id}', manufacturer='{self.manufacturer}')>"


class Equipment(Base):
    """Equipment model for laboratory instruments"""
    __tablename__ = 'equipment'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    location = Column(String(100))
    status = Column(String(50), default='available', index=True)
    calibration_due_date = Column(Date)
    last_calibration_date = Column(Date)
    calibration_interval = Column(Integer)  # days
    maintenance_schedule = Column(String(50))
    specifications = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("EquipmentBooking", back_populates="equipment")
    raw_data_files = relationship("RawDataFile", back_populates="equipment")

    __table_args__ = (
        CheckConstraint("status IN ('available', 'in_use', 'maintenance', 'calibration', 'out_of_service')",
                       name='check_equipment_status'),
    )

    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', name='{self.name}')>"


class EquipmentBooking(Base):
    """Equipment Booking model"""
    __tablename__ = 'equipment_bookings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id'), index=True)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'))
    booked_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default='scheduled', index=True)
    purpose = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="bookings")
    test_execution = relationship("TestExecution", back_populates="equipment_bookings")

    __table_args__ = (
        CheckConstraint("end_time > start_time", name='check_booking_time'),
        CheckConstraint("status IN ('scheduled', 'in_progress', 'completed', 'cancelled')",
                       name='check_booking_status'),
    )

    def __repr__(self):
        return f"<EquipmentBooking(equipment_id='{self.equipment_id}', start='{self.start_time}')>"


class TestExecution(Base):
    """Test Execution model"""
    __tablename__ = 'test_executions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_number = Column(String(50), unique=True, nullable=False, index=True)
    service_request_id = Column(UUID(as_uuid=True), ForeignKey('service_requests.id'), index=True)
    sample_id = Column(UUID(as_uuid=True), ForeignKey('samples.id'), index=True)
    protocol_id = Column(UUID(as_uuid=True), ForeignKey('protocols.id'), index=True)
    status = Column(String(50), default='pending', index=True)
    scheduled_start = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    test_conditions = Column(JSONB)
    input_parameters = Column(JSONB)
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(255))
    technician_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="test_executions")
    sample = relationship("Sample", back_populates="test_executions")
    protocol = relationship("Protocol", back_populates="test_executions")
    technician = relationship("User", back_populates="test_executions", foreign_keys=[technician_id])
    equipment_bookings = relationship("EquipmentBooking", back_populates="test_execution")
    raw_data_files = relationship("RawDataFile", back_populates="test_execution")
    measurement_data = relationship("MeasurementData", back_populates="test_execution")
    analysis_results = relationship("AnalysisResult", back_populates="test_execution")
    reports = relationship("Report", back_populates="test_execution")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'setup', 'running', 'paused', 'completed', 'failed', 'cancelled')",
                       name='check_test_execution_status'),
    )

    def __repr__(self):
        return f"<TestExecution(execution_number='{self.execution_number}', status='{self.status}')>"


class RawDataFile(Base):
    """Raw Data File model"""
    __tablename__ = 'raw_data_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'), index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(BigInteger)
    checksum = Column(String(64))
    upload_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id'), index=True)
    measurement_timestamp = Column(DateTime(timezone=True))
    metadata = Column(JSONB)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="raw_data_files")
    equipment = relationship("Equipment", back_populates="raw_data_files")
    measurement_data = relationship("MeasurementData", back_populates="raw_data_file")

    def __repr__(self):
        return f"<RawDataFile(filename='{self.filename}', test_execution_id='{self.test_execution_id}')>"


class MeasurementData(Base):
    """Measurement Data model"""
    __tablename__ = 'measurement_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'), index=True)
    raw_data_file_id = Column(UUID(as_uuid=True), ForeignKey('raw_data_files.id'))
    measurement_point = Column(String(100))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    data = Column(JSONB, nullable=False)
    units = Column(JSONB)
    environmental_conditions = Column(JSONB)
    is_valid = Column(Boolean, default=True)
    validation_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurement_data")
    raw_data_file = relationship("RawDataFile", back_populates="measurement_data")

    def __repr__(self):
        return f"<MeasurementData(measurement_point='{self.measurement_point}', timestamp='{self.timestamp}')>"


class AnalysisResult(Base):
    """Analysis Result model"""
    __tablename__ = 'analysis_results'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'), index=True)
    result_type = Column(String(100), index=True)
    calculated_value = Column(DECIMAL(15, 6))
    unit = Column(String(50))
    uncertainty = Column(DECIMAL(15, 6))
    pass_fail = Column(String(20), index=True)
    acceptance_criteria = Column(JSONB)
    calculation_method = Column(Text)
    intermediate_results = Column(JSONB)
    analyzed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    analyzed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="analysis_results")

    __table_args__ = (
        CheckConstraint("pass_fail IN ('pass', 'fail', 'conditional', 'n/a')",
                       name='check_analysis_pass_fail'),
    )

    def __repr__(self):
        return f"<AnalysisResult(result_type='{self.result_type}', value='{self.calculated_value}')>"


class Report(Base):
    """Report model"""
    __tablename__ = 'reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'), index=True)
    report_type = Column(String(50), default='test_report')
    template_version = Column(String(20))
    file_path = Column(Text)
    file_format = Column(String(10), default='pdf')
    status = Column(String(50), default='draft', index=True)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    generated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_at = Column(DateTime(timezone=True))
    issued_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="reports")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'review', 'approved', 'issued')",
                       name='check_report_status'),
    )

    def __repr__(self):
        return f"<Report(report_number='{self.report_number}', status='{self.status}')>"


class AuditTrail(Base):
    """Audit Trail model"""
    __tablename__ = 'audit_trail'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    notes = Column(Text)

    __table_args__ = (
        CheckConstraint("action IN ('create', 'update', 'delete', 'approve', 'reject', 'complete')",
                       name='check_audit_action'),
    )

    def __repr__(self):
        return f"<AuditTrail(table='{self.table_name}', action='{self.action}', timestamp='{self.timestamp}')>"


class Notification(Base):
    """Notification model"""
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    type = Column(String(50), nullable=False)
    category = Column(String(50))
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    priority = Column(String(20), default='normal')
    is_read = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    related_table = Column(String(100))
    related_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        CheckConstraint("priority IN ('low', 'normal', 'high')",
                       name='check_notification_priority'),
    )

    def __repr__(self):
        return f"<Notification(subject='{self.subject}', user_id='{self.user_id}')>"
