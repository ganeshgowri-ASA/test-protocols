"""
Database ORM Models for Fire Resistance Testing Protocol
SQLAlchemy models for LIMS-QMS integration
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text,
    ForeignKey, JSON, DECIMAL, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Protocol(Base):
    """Protocol definition model"""
    __tablename__ = 'protocols'

    protocol_id = Column(String(50), primary_key=True)
    protocol_name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(100))
    standard_name = Column(String(100))
    standard_section = Column(String(50))
    status = Column(String(50), default='active')
    created_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    protocol_json = Column(JSON)

    # Relationships
    test_sessions = relationship("TestSession", back_populates="protocol")
    training_records = relationship("TrainingRecord", back_populates="protocol")

    __table_args__ = (
        Index('idx_protocol_status', 'status'),
        Index('idx_protocol_category', 'category'),
    )


class Sample(Base):
    """Sample/module model"""
    __tablename__ = 'samples'

    sample_id = Column(String(100), primary_key=True)
    manufacturer = Column(String(255), nullable=False)
    model_number = Column(String(255), nullable=False)
    serial_number = Column(String(255), nullable=False, unique=True)
    date_of_manufacture = Column(Date)
    batch_number = Column(String(100))
    receipt_date = Column(DateTime, default=datetime.utcnow)
    visual_condition = Column(Text)
    dimensions = Column(JSON)
    weight_kg = Column(DECIMAL(10, 3))
    status = Column(String(50), default='Received')
    project_id = Column(String(100))
    customer_id = Column(String(100))
    test_due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_sessions = relationship("TestSession", back_populates="sample")

    __table_args__ = (
        Index('idx_sample_status', 'status'),
        Index('idx_sample_manufacturer', 'manufacturer'),
        Index('idx_sample_receipt_date', 'receipt_date'),
        Index('idx_sample_project', 'project_id'),
    )


class Equipment(Base):
    """Equipment model"""
    __tablename__ = 'equipment'

    equipment_id = Column(String(50), primary_key=True)
    equipment_name = Column(String(255), nullable=False)
    equipment_type = Column(String(100))
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    calibration_required = Column(Boolean, default=False)
    calibration_interval_days = Column(Integer)
    location = Column(String(255))
    status = Column(String(50), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    calibrations = relationship("EquipmentCalibration", back_populates="equipment")
    test_usage = relationship("TestEquipmentUsage", back_populates="equipment")

    __table_args__ = (
        Index('idx_equipment_status', 'status'),
        Index('idx_equipment_type', 'equipment_type'),
    )


class EquipmentCalibration(Base):
    """Equipment calibration record"""
    __tablename__ = 'equipment_calibrations'

    calibration_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(50), ForeignKey('equipment.equipment_id'), nullable=False)
    calibration_date = Column(Date, nullable=False)
    calibration_due_date = Column(Date, nullable=False)
    calibration_certificate = Column(String(255))
    calibrated_by = Column(String(255))
    calibration_results = Column(JSON)
    is_valid = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="calibrations")

    __table_args__ = (
        Index('idx_cal_equipment', 'equipment_id'),
        Index('idx_cal_due_date', 'calibration_due_date'),
        Index('idx_cal_validity', 'is_valid'),
    )


class Personnel(Base):
    """Personnel model"""
    __tablename__ = 'personnel'

    personnel_id = Column(String(50), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    role = Column(String(100))
    department = Column(String(100))
    certifications = Column(JSON)
    training_records_data = Column('training_records', JSON)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_personnel = relationship("TestPersonnel", back_populates="personnel")
    training_records = relationship("TrainingRecord", back_populates="personnel")

    __table_args__ = (
        Index('idx_personnel_role', 'role'),
        Index('idx_personnel_active', 'active'),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TestSession(Base):
    """Test session model"""
    __tablename__ = 'test_sessions'

    test_id = Column(String(100), primary_key=True)
    protocol_id = Column(String(50), ForeignKey('protocols.protocol_id'), nullable=False)
    sample_id = Column(String(100), ForeignKey('samples.sample_id'), nullable=False)
    test_date = Column(DateTime, nullable=False)
    test_status = Column(String(50), default='Pending')
    overall_result = Column(String(50))
    test_duration_minutes = Column(DECIMAL(10, 2))
    environmental_conditions = Column(JSON)
    test_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_sessions")
    sample = relationship("Sample", back_populates="test_sessions")
    personnel = relationship("TestPersonnel", back_populates="test_session")
    equipment_usage = relationship("TestEquipmentUsage", back_populates="test_session")
    measurements = relationship("Measurement", back_populates="test_session")
    observations = relationship("TestObservation", back_populates="test_session", uselist=False)
    acceptance_results = relationship("AcceptanceCriteriaResult", back_populates="test_session")
    reports = relationship("TestReport", back_populates="test_session")
    nonconformances = relationship("NonconformanceReport", back_populates="test_session")

    __table_args__ = (
        Index('idx_test_protocol', 'protocol_id'),
        Index('idx_test_sample', 'sample_id'),
        Index('idx_test_date', 'test_date'),
        Index('idx_test_status', 'test_status'),
        Index('idx_test_result', 'overall_result'),
        Index('idx_test_protocol_date', 'protocol_id', 'test_date'),
    )


class TestPersonnel(Base):
    """Test personnel association"""
    __tablename__ = 'test_personnel'

    test_id = Column(String(100), ForeignKey('test_sessions.test_id', ondelete='CASCADE'), primary_key=True)
    personnel_id = Column(String(50), ForeignKey('personnel.personnel_id'), primary_key=True)
    role_in_test = Column(String(100))

    # Relationships
    test_session = relationship("TestSession", back_populates="personnel")
    personnel = relationship("Personnel", back_populates="test_personnel")

    __table_args__ = (
        Index('idx_tp_test', 'test_id'),
        Index('idx_tp_personnel', 'personnel_id'),
    )


class TestEquipmentUsage(Base):
    """Test equipment usage"""
    __tablename__ = 'test_equipment_usage'

    usage_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id', ondelete='CASCADE'), nullable=False)
    equipment_id = Column(String(50), ForeignKey('equipment.equipment_id'), nullable=False)
    calibration_id = Column(Integer, ForeignKey('equipment_calibrations.calibration_id'))
    usage_notes = Column(Text)

    # Relationships
    test_session = relationship("TestSession", back_populates="equipment_usage")
    equipment = relationship("Equipment", back_populates="test_usage")

    __table_args__ = (
        Index('idx_usage_test', 'test_id'),
        Index('idx_usage_equipment', 'equipment_id'),
    )


class Measurement(Base):
    """Real-time measurement data"""
    __tablename__ = 'measurements'

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    elapsed_time_seconds = Column(DECIMAL(10, 3), nullable=False)
    surface_temperature_c = Column(DECIMAL(6, 2))
    flame_spread_mm = Column(DECIMAL(8, 2))
    observations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_session = relationship("TestSession", back_populates="measurements")

    __table_args__ = (
        Index('idx_meas_test', 'test_id'),
        Index('idx_meas_time', 'elapsed_time_seconds'),
        Index('idx_measurements_test_time', 'test_id', 'elapsed_time_seconds'),
    )


class TestObservation(Base):
    """Test observations"""
    __tablename__ = 'test_observations'

    observation_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id', ondelete='CASCADE'), nullable=False, unique=True)
    ignition_occurred = Column(Boolean, default=False)
    time_to_ignition_seconds = Column(DECIMAL(10, 2))
    self_extinguishing = Column(Boolean, default=False)
    self_extinguishing_time_seconds = Column(DECIMAL(10, 2))
    dripping_materials = Column(Boolean, default=False)
    flaming_drips = Column(Boolean, default=False)
    smoke_generation = Column(String(50))
    material_integrity = Column(String(50))
    max_flame_spread_mm = Column(DECIMAL(8, 2), default=0)
    burning_duration_seconds = Column(DECIMAL(10, 2), default=0)
    continued_smoldering = Column(Boolean, default=False)
    notes = Column(Text)

    # Relationships
    test_session = relationship("TestSession", back_populates="observations")

    __table_args__ = (
        Index('idx_obs_test', 'test_id'),
    )


class AcceptanceCriteriaResult(Base):
    """Acceptance criteria evaluation results"""
    __tablename__ = 'acceptance_criteria_results'

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id', ondelete='CASCADE'), nullable=False)
    criterion_name = Column(String(255), nullable=False)
    requirement = Column(Text)
    measured_value = Column(String(255))
    pass_condition = Column(String(255))
    result = Column(String(50))
    severity = Column(String(50))
    notes = Column(Text)

    # Relationships
    test_session = relationship("TestSession", back_populates="acceptance_results")

    __table_args__ = (
        Index('idx_acr_test', 'test_id'),
        Index('idx_acr_result', 'result'),
    )


class TestReport(Base):
    """Test report model"""
    __tablename__ = 'test_reports'

    report_id = Column(String(100), primary_key=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id'), nullable=False)
    protocol_id = Column(String(50), ForeignKey('protocols.protocol_id'), nullable=False)
    protocol_version = Column(String(20))
    report_date = Column(DateTime, default=datetime.utcnow)
    executive_summary = Column(Text)
    analysis = Column(Text)
    conclusion = Column(Text)
    recommendations = Column(JSON)
    prepared_by = Column(String(100))
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    report_status = Column(String(50), default='Draft')
    report_file_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_session = relationship("TestSession", back_populates="reports")
    signatures = relationship("ReportSignature", back_populates="report")

    __table_args__ = (
        Index('idx_report_test', 'test_id'),
        Index('idx_report_status', 'report_status'),
        Index('idx_report_date', 'report_date'),
    )


class ReportSignature(Base):
    """Report signature model"""
    __tablename__ = 'report_signatures'

    signature_id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), ForeignKey('test_reports.report_id', ondelete='CASCADE'), nullable=False)
    personnel_id = Column(String(50), ForeignKey('personnel.personnel_id'), nullable=False)
    signature_role = Column(String(100))
    signature_date = Column(DateTime, default=datetime.utcnow)
    signature_data = Column(Text)

    # Relationships
    report = relationship("TestReport", back_populates="signatures")

    __table_args__ = (
        Index('idx_sig_report', 'report_id'),
    )


class Attachment(Base):
    """File attachment model"""
    __tablename__ = 'attachments'

    attachment_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(100))
    file_size_bytes = Column(Integer)
    description = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100))

    __table_args__ = (
        Index('idx_attach_entity', 'entity_type', 'entity_id'),
        Index('idx_attach_type', 'file_type'),
    )


class NonconformanceReport(Base):
    """Nonconformance report model"""
    __tablename__ = 'nonconformance_reports'

    ncr_id = Column(String(100), primary_key=True)
    test_id = Column(String(100), ForeignKey('test_sessions.test_id'))
    report_date = Column(DateTime, default=datetime.utcnow)
    reported_by = Column(String(100))
    ncr_type = Column(String(100))
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    status = Column(String(50), default='Open')
    closed_date = Column(DateTime)
    closed_by = Column(String(100))

    # Relationships
    test_session = relationship("TestSession", back_populates="nonconformances")

    __table_args__ = (
        Index('idx_ncr_test', 'test_id'),
        Index('idx_ncr_status', 'status'),
        Index('idx_ncr_date', 'report_date'),
    )


class ChangeControl(Base):
    """Change control record"""
    __tablename__ = 'change_control'

    change_id = Column(String(100), primary_key=True)
    change_type = Column(String(100))
    affected_document = Column(String(255))
    change_description = Column(Text, nullable=False)
    change_reason = Column(Text)
    requested_by = Column(String(100))
    request_date = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String(100))
    review_date = Column(DateTime)
    approved_by = Column(String(100))
    approval_date = Column(DateTime)
    implementation_date = Column(DateTime)
    status = Column(String(50), default='Pending')

    __table_args__ = (
        Index('idx_change_document', 'affected_document'),
        Index('idx_change_status', 'status'),
        Index('idx_change_date', 'request_date'),
    )


class TrainingRecord(Base):
    """Training record model"""
    __tablename__ = 'training_records'

    training_id = Column(Integer, primary_key=True, autoincrement=True)
    personnel_id = Column(String(50), ForeignKey('personnel.personnel_id'), nullable=False)
    protocol_id = Column(String(50), ForeignKey('protocols.protocol_id'))
    training_type = Column(String(100))
    training_date = Column(Date, nullable=False)
    trainer = Column(String(100))
    competency_assessed = Column(Boolean, default=False)
    assessment_result = Column(String(50))
    expiration_date = Column(Date)
    notes = Column(Text)

    # Relationships
    personnel = relationship("Personnel", back_populates="training_records")
    protocol = relationship("Protocol", back_populates="training_records")

    __table_args__ = (
        Index('idx_train_personnel', 'personnel_id'),
        Index('idx_train_protocol', 'protocol_id'),
        Index('idx_train_expiry', 'expiration_date'),
    )


class AuditTrail(Base):
    """Audit trail model"""
    __tablename__ = 'audit_trail'

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(String(100))
    change_timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    user_agent = Column(Text)

    __table_args__ = (
        Index('idx_audit_table', 'table_name'),
        Index('idx_audit_record', 'record_id'),
        Index('idx_audit_timestamp', 'change_timestamp'),
        Index('idx_audit_user', 'changed_by'),
    )


class Notification(Base):
    """Notification model"""
    __tablename__ = 'notifications'

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    notification_type = Column(String(100))
    priority = Column(String(50))
    subject = Column(String(255))
    message = Column(Text)
    recipient_id = Column(String(100))
    sent_date = Column(DateTime, default=datetime.utcnow)
    read_date = Column(DateTime)
    related_entity_type = Column(String(50))
    related_entity_id = Column(String(100))

    __table_args__ = (
        Index('idx_notif_recipient', 'recipient_id'),
        Index('idx_notif_read', 'read_date'),
        Index('idx_notif_type', 'notification_type'),
    )


# Database connection and session management
class DatabaseManager:
    """Database manager for LIMS-QMS system"""

    def __init__(self, connection_string: str = "sqlite:///fire_resistance_lims.db"):
        """Initialize database manager"""
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_all_tables(self):
        """Create all tables in database"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
