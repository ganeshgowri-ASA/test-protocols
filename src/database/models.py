"""
SQLAlchemy ORM Models for UV-001 Protocol Database

Provides Python object mapping for database tables with complete
data traceability and integrity constraints.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, BigInteger, DECIMAL, Boolean, Text, DateTime,
    ForeignKey, Index, CheckConstraint, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class TestSession(Base):
    """UV-001 Test Session Model"""
    __tablename__ = 'uv001_test_sessions'

    session_id = Column(String(100), primary_key=True)
    protocol_id = Column(String(20), nullable=False, default='UV-001')
    protocol_version = Column(String(10), nullable=False, default='1.0')

    # Session metadata
    sample_id = Column(String(100), nullable=False, index=True)
    operator = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    status = Column(String(20), nullable=False, index=True)

    # Calculated metrics
    cumulative_uv_dose = Column(DECIMAL(10, 4), default=0.0)
    total_exposure_time = Column(DECIMAL(10, 2), default=0.0)
    average_irradiance = Column(DECIMAL(10, 2), default=0.0)

    # Notes
    notes = Column(Text)
    abort_reason = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    irradiance_measurements = relationship("IrradianceMeasurement", back_populates="session", cascade="all, delete-orphan")
    environmental_measurements = relationship("EnvironmentalMeasurement", back_populates="session", cascade="all, delete-orphan")
    spectral_measurements = relationship("SpectralMeasurement", back_populates="session", cascade="all, delete-orphan")
    electrical_characterizations = relationship("ElectricalCharacterization", back_populates="session", cascade="all, delete-orphan")
    visual_inspections = relationship("VisualInspection", back_populates="session", cascade="all, delete-orphan")
    test_events = relationship("TestEvent", back_populates="session", cascade="all, delete-orphan")
    test_result = relationship("TestResult", back_populates="session", uselist=False, cascade="all, delete-orphan")
    equipment_usage = relationship("EquipmentUsage", back_populates="session", cascade="all, delete-orphan")
    data_quality = relationship("DataQuality", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'paused', 'completed', 'failed', 'aborted')"),
    )

    def __repr__(self):
        return f"<TestSession(session_id='{self.session_id}', sample_id='{self.sample_id}', status='{self.status}')>"


class IrradianceMeasurement(Base):
    """UV Irradiance Measurement Model"""
    __tablename__ = 'uv001_irradiance_measurements'

    measurement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Irradiance data
    uv_irradiance = Column(DECIMAL(10, 2), nullable=False)
    sensor_temperature = Column(DECIMAL(6, 2))

    # Uniformity measurements
    uniformity_point_1 = Column(DECIMAL(10, 2))
    uniformity_point_2 = Column(DECIMAL(10, 2))
    uniformity_point_3 = Column(DECIMAL(10, 2))
    uniformity_point_4 = Column(DECIMAL(10, 2))
    uniformity_deviation = Column(DECIMAL(6, 2))

    # Compliance
    compliance_status = Column(String(20))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="irradiance_measurements")

    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        CheckConstraint("compliance_status IN ('compliant', 'out_of_spec', 'warning')"),
    )

    def __repr__(self):
        return f"<IrradianceMeasurement(id={self.measurement_id}, irradiance={self.uv_irradiance})>"


class EnvironmentalMeasurement(Base):
    """Environmental Conditions Measurement Model"""
    __tablename__ = 'uv001_environmental_measurements'

    measurement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Temperature data
    module_temperature = Column(DECIMAL(6, 2), nullable=False)
    ambient_temperature = Column(DECIMAL(6, 2), nullable=False)

    # Additional environmental parameters
    relative_humidity = Column(DECIMAL(5, 2), nullable=False)
    air_velocity = Column(DECIMAL(6, 2))
    barometric_pressure = Column(DECIMAL(7, 2))

    # Multi-point temperature measurements
    temp_center = Column(DECIMAL(6, 2))
    temp_corner_1 = Column(DECIMAL(6, 2))
    temp_corner_2 = Column(DECIMAL(6, 2))
    temp_corner_3 = Column(DECIMAL(6, 2))
    temp_corner_4 = Column(DECIMAL(6, 2))
    temp_uniformity = Column(DECIMAL(6, 2))

    # Compliance flags
    module_temp_compliant = Column(Boolean)
    ambient_temp_compliant = Column(Boolean)
    humidity_compliant = Column(Boolean)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="environmental_measurements")

    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<EnvironmentalMeasurement(id={self.measurement_id}, module_temp={self.module_temperature})>"


class SpectralMeasurement(Base):
    """Spectral Irradiance Measurement Model"""
    __tablename__ = 'uv001_spectral_measurements'

    measurement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Spectral summary data
    total_uv_irradiance = Column(DECIMAL(10, 2), nullable=False)
    peak_wavelength = Column(DECIMAL(6, 2), nullable=False)
    uv_a_percentage = Column(DECIMAL(5, 2), nullable=False)
    uv_b_percentage = Column(DECIMAL(5, 2), nullable=False)

    # Full spectral data (JSON)
    spectral_data_json = Column(Text)

    # Compliance flags
    peak_wavelength_compliant = Column(Boolean)
    uva_compliant = Column(Boolean)
    uvb_compliant = Column(Boolean)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="spectral_measurements")

    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<SpectralMeasurement(id={self.measurement_id}, peak={self.peak_wavelength}nm)>"


class ElectricalCharacterization(Base):
    """Electrical I-V Characterization Model"""
    __tablename__ = 'uv001_electrical_characterization'

    characterization_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    measurement_type = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # I-V parameters
    open_circuit_voltage = Column(DECIMAL(8, 4), nullable=False)
    short_circuit_current = Column(DECIMAL(8, 4), nullable=False)
    maximum_power = Column(DECIMAL(10, 4), nullable=False)
    voltage_at_max_power = Column(DECIMAL(8, 4))
    current_at_max_power = Column(DECIMAL(8, 4))
    fill_factor = Column(DECIMAL(6, 4), nullable=False)

    # Additional parameters
    efficiency = Column(DECIMAL(6, 3))
    series_resistance = Column(DECIMAL(10, 6))
    shunt_resistance = Column(DECIMAL(12, 4))

    # I-V curve data (JSON)
    iv_curve_json = Column(Text)

    # Test conditions
    irradiance = Column(DECIMAL(8, 2))
    module_temperature = Column(DECIMAL(6, 2))
    spectrum_type = Column(String(20))

    # Insulation resistance
    insulation_resistance = Column(DECIMAL(10, 2))
    insulation_compliant = Column(Boolean)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="electrical_characterizations")

    __table_args__ = (
        Index('idx_session_type', 'session_id', 'measurement_type'),
        CheckConstraint("measurement_type IN ('pre_test', 'post_test', 'intermediate')"),
    )

    def __repr__(self):
        return f"<ElectricalCharacterization(id={self.characterization_id}, type='{self.measurement_type}', Pmax={self.maximum_power})>"


class VisualInspection(Base):
    """Visual Inspection Model"""
    __tablename__ = 'uv001_visual_inspections'

    inspection_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    inspection_type = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    inspector = Column(String(100), nullable=False)

    # Defect observations
    discoloration = Column(Boolean, default=False)
    discoloration_description = Column(Text)
    delamination = Column(Boolean, default=False)
    delamination_description = Column(Text)
    bubbles_blisters = Column(Boolean, default=False)
    bubbles_description = Column(Text)
    edge_seal_degradation = Column(Boolean, default=False)
    edge_seal_description = Column(Text)
    cell_cracks = Column(Boolean, default=False)
    cell_cracks_description = Column(Text)
    junction_box_issues = Column(Boolean, default=False)
    junction_box_description = Column(Text)

    # Overall assessment
    overall_condition = Column(String(20))
    major_defects_found = Column(Boolean, default=False)
    general_notes = Column(Text)

    # Photo documentation
    photo_urls = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="visual_inspections")

    __table_args__ = (
        Index('idx_session_type', 'session_id', 'inspection_type'),
        CheckConstraint("inspection_type IN ('pre_test', 'post_test', 'intermediate')"),
        CheckConstraint("overall_condition IN ('excellent', 'good', 'acceptable', 'poor', 'failed')"),
    )

    def __repr__(self):
        return f"<VisualInspection(id={self.inspection_id}, type='{self.inspection_type}')>"


class TestEvent(Base):
    """Test Events and Incidents Model"""
    __tablename__ = 'uv001_test_events'

    event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), index=True)

    # Event details
    event_description = Column(Text, nullable=False)
    parameter_name = Column(String(100))
    parameter_value = Column(String(100))
    expected_value = Column(String(100))

    # Response
    action_taken = Column(Text)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="test_events")

    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        CheckConstraint("severity IN ('critical', 'high', 'medium', 'low', 'info')"),
    )

    def __repr__(self):
        return f"<TestEvent(id={self.event_id}, type='{self.event_type}', severity='{self.severity}')>"


class TestResult(Base):
    """Test Results and Analysis Model"""
    __tablename__ = 'uv001_test_results'

    result_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False, unique=True)

    # UV dose compliance
    final_uv_dose = Column(DECIMAL(10, 4), nullable=False)
    target_uv_dose = Column(DECIMAL(10, 4), nullable=False)
    dose_tolerance = Column(DECIMAL(6, 4), nullable=False)
    dose_compliant = Column(Boolean, nullable=False)

    # Performance degradation
    power_degradation_percentage = Column(DECIMAL(6, 3))
    voc_degradation_percentage = Column(DECIMAL(6, 3))
    isc_degradation_percentage = Column(DECIMAL(6, 3))
    ff_degradation_percentage = Column(DECIMAL(6, 3))

    # Acceptance criteria
    max_power_degradation_limit = Column(DECIMAL(6, 3), default=5.0)
    power_degradation_pass = Column(Boolean)

    min_insulation_resistance_limit = Column(DECIMAL(10, 2), default=40.0)
    insulation_resistance_pass = Column(Boolean)

    visual_inspection_pass = Column(Boolean)

    # Overall result
    overall_pass = Column(Boolean, nullable=False)
    test_status = Column(String(20))

    # Quality metrics
    data_completeness_percentage = Column(DECIMAL(5, 2))
    measurement_count_irradiance = Column(Integer)
    measurement_count_environmental = Column(Integer)
    measurement_count_spectral = Column(Integer)

    # Analysis notes
    analysis_notes = Column(Text)
    recommendations = Column(Text)

    # Analyst information
    analyzed_by = Column(String(100))
    analyzed_at = Column(DateTime)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="test_result")

    __table_args__ = (
        CheckConstraint("test_status IN ('pass', 'fail', 'conditional_pass', 'inconclusive')"),
    )

    def __repr__(self):
        return f"<TestResult(session_id='{self.session_id}', status='{self.test_status}', pass={self.overall_pass})>"


class EquipmentUsage(Base):
    """Equipment and Calibration Tracking Model"""
    __tablename__ = 'uv001_equipment_usage'

    usage_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)

    # Equipment details
    equipment_type = Column(String(50), nullable=False)
    equipment_id = Column(String(100), nullable=False, index=True)
    equipment_name = Column(String(200))
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Calibration status
    last_calibration_date = Column(DateTime)
    calibration_due_date = Column(DateTime)
    calibration_certificate_number = Column(String(100))
    calibration_valid = Column(Boolean)

    # Usage details
    usage_start = Column(DateTime)
    usage_end = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="equipment_usage")

    __table_args__ = (
        Index('idx_session_equipment', 'session_id', 'equipment_type'),
    )

    def __repr__(self):
        return f"<EquipmentUsage(id={self.usage_id}, equipment='{self.equipment_id}')>"


class DataQuality(Base):
    """Data Quality and Validation Model"""
    __tablename__ = 'uv001_data_quality'

    quality_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('uv001_test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    check_timestamp = Column(DateTime, nullable=False)
    check_type = Column(String(50), nullable=False)

    # Quality metrics
    parameter_name = Column(String(100))
    expected_count = Column(Integer)
    actual_count = Column(Integer)
    missing_count = Column(Integer)
    out_of_range_count = Column(Integer)

    # Quality score
    quality_score = Column(DECIMAL(5, 2))
    quality_status = Column(String(20))

    # Issue details
    issues_found = Column(Text)
    corrective_actions = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TestSession", back_populates="data_quality")

    __table_args__ = (
        Index('idx_session_check', 'session_id', 'check_timestamp'),
        CheckConstraint("quality_status IN ('excellent', 'good', 'acceptable', 'poor', 'failed')"),
    )

    def __repr__(self):
        return f"<DataQuality(id={self.quality_id}, status='{self.quality_status}')>"


# Database utility functions

def create_database_engine(connection_string: str):
    """Create SQLAlchemy engine"""
    return create_engine(connection_string, echo=False)


def create_all_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def get_session_maker(engine):
    """Get SQLAlchemy session maker"""
    return sessionmaker(bind=engine)
