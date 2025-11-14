"""Database models for test protocols framework."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class TestProtocol(Base):
    """Test protocol definition."""

    __tablename__ = 'test_protocols'

    id = Column(String, primary_key=True, default=generate_uuid)
    protocol_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    standard = Column(String, nullable=False)
    category = Column(String)  # e.g., Safety, Performance, Environmental
    version = Column(String, nullable=False)
    schema = Column(JSON)  # Store protocol schema as JSON
    description = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)

    # Relationships
    test_runs = relationship('TestRun', back_populates='protocol', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<TestProtocol(protocol_id='{self.protocol_id}', name='{self.name}')>"


class SampleInformation(Base):
    """Sample/module information."""

    __tablename__ = 'sample_information'

    id = Column(String, primary_key=True, default=generate_uuid)
    sample_id = Column(String, unique=True, nullable=False, index=True)
    module_type = Column(String)
    manufacturer = Column(String)
    manufacturing_date = Column(DateTime)
    serial_number = Column(String)
    rated_power = Column(Float)  # Watts
    additional_info = Column(JSON)  # Flexible storage for extra fields
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_runs = relationship('TestRun', back_populates='sample')

    def __repr__(self) -> str:
        return f"<SampleInformation(sample_id='{self.sample_id}', module_type='{self.module_type}')>"


class TestRun(Base):
    """Test run instance."""

    __tablename__ = 'test_runs'

    id = Column(String, primary_key=True, default=generate_uuid)
    protocol_id = Column(String, ForeignKey('test_protocols.id'), nullable=False, index=True)
    sample_id = Column(String, ForeignKey('sample_information.id'), nullable=False, index=True)
    run_number = Column(Integer)  # Sequential run number for this sample/protocol
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    operator = Column(String)
    test_facility = Column(String)
    equipment_id = Column(String)

    # Test parameters and conditions (stored as JSON for flexibility)
    test_parameters = Column(JSON, nullable=False)
    environmental_conditions = Column(JSON)
    acceptance_criteria = Column(JSON)

    # Status tracking
    status = Column(String, default='in_progress')  # in_progress, completed, failed, aborted
    pass_fail = Column(Boolean)

    # Results
    result_summary = Column(Text)
    report_id = Column(String)
    report_path = Column(String)

    created_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship('TestProtocol', back_populates='test_runs')
    sample = relationship('SampleInformation', back_populates='test_runs')
    measurements = relationship('Measurement', back_populates='test_run', cascade='all, delete-orphan')
    results = relationship('TestResult', back_populates='test_run', uselist=False, cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<TestRun(id='{self.id}', protocol='{self.protocol_id}', sample='{self.sample_id}')>"


class Measurement(Base):
    """Individual measurement point."""

    __tablename__ = 'measurements'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_run_id = Column(String, ForeignKey('test_runs.id'), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    sequence_number = Column(Integer)  # Order of measurement in the test

    # Common measurements (protocol-specific values in JSON)
    leakage_current = Column(Float)  # mA
    voltage = Column(Float)  # V
    current = Column(Float)  # A
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %
    pressure = Column(Float)  # kPa
    insulation_resistance = Column(Float)  # MΩ

    # Flexible storage for protocol-specific measurements
    additional_values = Column(JSON)

    # Observations
    notes = Column(Text)
    anomaly_detected = Column(Boolean, default=False)
    anomaly_description = Column(Text)

    # Relationships
    test_run = relationship('TestRun', back_populates='measurements')

    def __repr__(self) -> str:
        return f"<Measurement(test_run_id='{self.test_run_id}', timestamp='{self.timestamp}')>"


class TestResult(Base):
    """Test result with analysis."""

    __tablename__ = 'test_results'

    id = Column(String, primary_key=True, default=generate_uuid)
    test_run_id = Column(String, ForeignKey('test_runs.id'), nullable=False, unique=True, index=True)

    # Overall result
    passed = Column(Boolean, nullable=False)
    summary = Column(Text, nullable=False)

    # Statistical analysis
    max_leakage_current = Column(Float)
    min_leakage_current = Column(Float)
    avg_leakage_current = Column(Float)
    std_dev_leakage_current = Column(Float)

    max_insulation_resistance = Column(Float)
    min_insulation_resistance = Column(Float)
    avg_insulation_resistance = Column(Float)
    std_dev_insulation_resistance = Column(Float)

    max_voltage_deviation = Column(Float)

    # Pass/Fail details
    failure_reasons = Column(JSON)  # List of failure reasons
    surface_tracking_observed = Column(Boolean)
    visible_damage_observed = Column(Boolean)

    # Trending and anomalies
    trending_analysis = Column(JSON)
    anomalies = Column(JSON)  # List of detected anomalies

    # Additional analysis results (protocol-specific)
    detailed_analysis = Column(JSON)

    # Report information
    report_generated = Column(Boolean, default=False)
    report_path = Column(String)
    report_format = Column(String)

    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship('TestRun', back_populates='results')

    def __repr__(self) -> str:
        return f"<TestResult(test_run_id='{self.test_run_id}', passed={self.passed})>"
