"""
Test execution database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import BaseModel


class TestStatus(enum.Enum):
    """Test execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestExecution(BaseModel):
    """Test execution model"""

    __tablename__ = 'test_executions'

    test_id = Column(String(50), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False, index=True)
    sample_id = Column(Integer, ForeignKey('samples.id'), nullable=False, index=True)
    protocol_version = Column(String(20), nullable=False)

    # Test execution details
    status = Column(Enum(TestStatus), default=TestStatus.PENDING, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_hours = Column(Float)

    # Environmental conditions
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    environmental_data = Column(JSON)  # Additional environmental data

    # Operator and equipment
    operator_id = Column(String(50))
    equipment_ids = Column(JSON)  # List of equipment IDs used
    facility_location = Column(String(100))

    # Test configuration
    test_parameters = Column(JSON)  # Specific test parameters
    notes = Column(Text)
    metadata = Column(JSON)

    # Relationships
    protocol = relationship("Protocol", back_populates="tests")
    sample = relationship("Sample", back_populates="tests")
    measurements = relationship("TestMeasurement", back_populates="test", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")
    analyses = relationship("AnalysisResult", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution(id={self.id}, test_id='{self.test_id}', status='{self.status.value}')>"


class TestMeasurement(BaseModel):
    """Test measurement model"""

    __tablename__ = 'test_measurements'

    test_id = Column(Integer, ForeignKey('test_executions.id'), nullable=False, index=True)
    measurement_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    interval_hours = Column(Float)  # Time since test start
    measurement_type = Column(String(50), nullable=False)  # voltage, current, power, etc.

    # Measurement values
    value = Column(Float)
    unit = Column(String(20))

    # For complex measurements
    values = Column(JSON)  # Array or dict of multiple values

    # Measurement conditions
    temperature = Column(Float)
    humidity = Column(Float)

    # Quality indicators
    quality_flag = Column(String(20))  # good, suspect, bad
    notes = Column(Text)
    metadata = Column(JSON)

    # Relationships
    test = relationship("TestExecution", back_populates="measurements")

    def __repr__(self):
        return f"<TestMeasurement(id={self.id}, type='{self.measurement_type}', value={self.value})>"


class TestResult(BaseModel):
    """Test result model"""

    __tablename__ = 'test_results'

    test_id = Column(Integer, ForeignKey('test_executions.id'), nullable=False, index=True)

    # Result summary
    passed = Column(Boolean, nullable=False)
    pass_fail_criteria = Column(JSON)  # Detailed pass/fail by criteria

    # Performance metrics
    power_degradation_percent = Column(Float)
    efficiency = Column(Float)
    fill_factor = Column(Float)

    # Visual inspection results
    visual_inspection_passed = Column(Boolean)
    visual_defects = Column(JSON)  # List of visual defects found

    # Delamination specific results (for DELAM-001)
    delamination_detected = Column(Boolean)
    delamination_area_percent = Column(Float)
    delamination_severity = Column(String(20))  # none, minor, moderate, severe, critical

    # Compliance
    meets_standard = Column(Boolean)
    standard_deviations = Column(JSON)  # Deviations from standard requirements

    # Additional data
    summary = Column(Text)
    recommendations = Column(Text)
    metadata = Column(JSON)

    # Relationships
    test = relationship("TestExecution", back_populates="results")

    def __repr__(self):
        return f"<TestResult(id={self.id}, passed={self.passed})>"
