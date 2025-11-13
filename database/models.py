"""
SQLAlchemy Database Models for PV Testing Protocol Framework
============================================================
ORM models for all database tables.

Author: GenSpark PV Testing Framework
Version: 1.0.0
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, LargeBinary, create_engine
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


class Protocol(Base):
    """Protocol registry model"""
    __tablename__ = 'protocols'

    protocol_id = Column(String(20), primary_key=True)
    protocol_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    standard_reference = Column(String(255))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("ProtocolExecution", back_populates="protocol")


class ProtocolExecution(Base):
    """Protocol execution model"""
    __tablename__ = 'protocol_executions'

    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(String(20), ForeignKey('protocols.protocol_id'), nullable=False)
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="executions")
    parameters = relationship("TestParameter", back_populates="execution", cascade="all, delete-orphan")
    test_data = relationship("TestData", back_populates="execution", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="execution", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="execution", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="execution", cascade="all, delete-orphan")
    audit_trail = relationship("AuditTrail", back_populates="execution", cascade="all, delete-orphan")


class TestParameter(Base):
    """Test parameter model"""
    __tablename__ = 'test_parameters'

    id = Column(Integer, primary_key=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    parameter_value = Column(Text)
    parameter_unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="parameters")


class TestData(Base):
    """Test data model"""
    __tablename__ = 'test_data'

    id = Column(Integer, primary_key=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), nullable=False)
    data_type = Column(String(100), nullable=False)
    data_json = Column(JSONB, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="test_data")


class AnalysisResult(Base):
    """Analysis result model"""
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), nullable=False)
    result_name = Column(String(100), nullable=False)
    result_value = Column(Float)
    result_unit = Column(String(50))
    result_json = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="analysis_results")


class ValidationResult(Base):
    """Validation result model"""
    __tablename__ = 'validation_results'

    id = Column(Integer, primary_key=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), nullable=False)
    validation_level = Column(String(20), nullable=False)
    field_name = Column(String(100))
    message = Column(Text)
    expected_value = Column(Text)
    actual_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="validation_results")


class Report(Base):
    """Report model"""
    __tablename__ = 'reports'

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), nullable=False)
    report_format = Column(String(20), nullable=False)
    report_data = Column(LargeBinary)
    file_path = Column(String(512))
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="reports")


class AuditTrail(Base):
    """Audit trail model"""
    __tablename__ = 'audit_trail'

    id = Column(Integer, primary_key=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'))
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB)
    user_id = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("ProtocolExecution", back_populates="audit_trail")


# Category-specific models
class PerformanceTestExecution(Base):
    """Performance test execution model"""
    __tablename__ = 'performance_test_executions'

    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), primary_key=True)
    irradiance = Column(Float)
    cell_temperature = Column(Float)
    ambient_temperature = Column(Float)
    isc = Column(Float)
    voc = Column(Float)
    imp = Column(Float)
    vmp = Column(Float)
    pmax = Column(Float)
    fill_factor = Column(Float)
    efficiency = Column(Float)


class DegradationTestExecution(Base):
    """Degradation test execution model"""
    __tablename__ = 'degradation_test_executions'

    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), primary_key=True)
    initial_power = Column(Float)
    final_power = Column(Float)
    power_loss_pct = Column(Float)
    degradation_rate = Column(Float)
    stress_type = Column(String(100))
    stress_duration = Column(Float)
    recovery_percentage = Column(Float)


class EnvironmentalTestExecution(Base):
    """Environmental test execution model"""
    __tablename__ = 'environmental_test_executions'

    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), primary_key=True)
    test_type = Column(String(100))
    number_of_cycles = Column(Integer)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    humidity = Column(Float)
    exposure_duration = Column(Float)
    visual_defects = Column(JSONB)
    pass_fail = Column(Boolean)


class MechanicalTestExecution(Base):
    """Mechanical test execution model"""
    __tablename__ = 'mechanical_test_executions'

    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), primary_key=True)
    test_type = Column(String(100))
    load_applied = Column(Float)
    load_unit = Column(String(20))
    deflection = Column(Float)
    structural_integrity = Column(Boolean)
    crack_count = Column(Integer)
    visual_damage = Column(JSONB)


class SafetyTestExecution(Base):
    """Safety test execution model"""
    __tablename__ = 'safety_test_executions'

    execution_id = Column(UUID(as_uuid=True), ForeignKey('protocol_executions.execution_id', ondelete='CASCADE'), primary_key=True)
    test_type = Column(String(100))
    insulation_resistance = Column(Float)
    leakage_current = Column(Float)
    test_voltage = Column(Float)
    dielectric_strength = Column(Float)
    ground_continuity = Column(Boolean)
    pass_fail = Column(Boolean)


# Database connection helper
class DatabaseManager:
    """Database connection and session manager"""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_all_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)

    def drop_all_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()


# Example usage
if __name__ == "__main__":
    # Example: Initialize database
    db_manager = DatabaseManager("postgresql://user:password@localhost/pv_testing")
    db_manager.create_all_tables()
    print("Database tables created successfully!")
