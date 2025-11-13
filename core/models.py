"""
Database models for PV testing protocols
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TestRun(Base):
    """
    Represents a complete test run for a protocol
    """
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(String(50), nullable=False, index=True)
    protocol_version = Column(String(20), nullable=False)

    # Sample Information
    sample_id = Column(String(100), nullable=False, index=True)
    sample_type = Column(String(50))
    batch_id = Column(String(100), index=True)

    # Test Metadata
    operator = Column(String(100))
    equipment_id = Column(String(100))
    lab_location = Column(String(100))

    # Status and Timestamps
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Test Conditions (JSON field for flexibility)
    test_conditions = Column(JSON)

    # Results Summary
    passed = Column(Boolean, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Notes and Traceability
    notes = Column(Text)
    revision_number = Column(Integer, default=1)

    # Relationships
    measurements = relationship("TestMeasurement", back_populates="test_run", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_run", cascade="all, delete-orphan")

    # Integration IDs
    lims_id = Column(String(100), index=True)
    qms_id = Column(String(100), index=True)
    project_id = Column(String(100), index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TestRun(run_id='{self.run_id}', protocol='{self.protocol_id}', status='{self.status}')>"


class TestMeasurement(Base):
    """
    Represents individual measurements taken during a test
    """
    __tablename__ = 'test_measurements'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)

    # Measurement Details
    measurement_type = Column(String(50), nullable=False)  # iv_curve, temperature, irradiance, etc.
    measurement_point = Column(String(50))  # e.g., "200W/m2", "400W/m2"
    sequence_number = Column(Integer)

    # Measurement Data (JSON for flexibility with different data structures)
    data = Column(JSON, nullable=False)

    # Measurement Conditions
    irradiance = Column(Float)  # W/m²
    temperature = Column(Float)  # °C
    spectrum = Column(String(20))  # AM1.5, etc.

    # Timestamp
    measured_at = Column(DateTime, default=datetime.utcnow)

    # Quality Indicators
    quality_flag = Column(String(20))  # good, warning, bad
    quality_notes = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")

    def __repr__(self):
        return f"<TestMeasurement(type='{self.measurement_type}', point='{self.measurement_point}')>"


class TestResult(Base):
    """
    Represents calculated results from a test run
    """
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)

    # Result Identification
    result_type = Column(String(50), nullable=False)  # pmax, ff, efficiency, etc.
    measurement_point = Column(String(50))  # e.g., "200W/m2" for low irradiance tests

    # Result Values
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    uncertainty = Column(Float)  # Measurement uncertainty

    # Statistical Data
    mean_value = Column(Float)
    std_deviation = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)

    # Pass/Fail Criteria
    specification_min = Column(Float)
    specification_max = Column(Float)
    passed = Column(Boolean)

    # Calculated At
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Additional Data
    metadata = Column(JSON)

    # Relationships
    test_run = relationship("TestRun", back_populates="results")

    def __repr__(self):
        return f"<TestResult(type='{self.result_type}', value={self.value} {self.unit})>"


class ValidationRule(Base):
    """
    Validation rules for test protocols
    """
    __tablename__ = 'validation_rules'

    id = Column(Integer, primary_key=True)
    protocol_id = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    rule_type = Column(String(50))  # range, comparison, calculation, etc.

    # Rule Parameters (JSON for flexibility)
    parameters = Column(JSON)

    # Severity
    severity = Column(String(20), default='error')  # error, warning, info

    # Error Message
    error_message = Column(Text)

    # Active Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ValidationRule(protocol='{self.protocol_id}', rule='{self.rule_name}')>"
