"""Test results database models"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Measurement(Base):
    """Individual measurement model"""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Test execution reference
    test_execution_id = Column(
        String(100), ForeignKey("test_executions.test_execution_id"), nullable=False, index=True
    )

    # Measurement identification
    location_id = Column(String(50), nullable=False)
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)

    # Measurement data (protocol-specific)
    measurement_data_json = Column(JSON, nullable=False)

    # Common fields (duplicated for easier querying)
    chalking_rating = Column(Float)  # For CHALK-001
    location_x = Column(Float)
    location_y = Column(Float)
    visual_observations = Column(Text)
    photo_reference = Column(String(255))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(id={self.id}, test='{self.test_execution_id}', location='{self.location_id}')>"


class TestResult(Base):
    """Calculated test results model"""

    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Test execution reference
    test_execution_id = Column(
        String(100),
        ForeignKey("test_executions.test_execution_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Calculated results
    calculated_results_json = Column(JSON, nullable=False)

    # Pass/Fail assessment
    pass_fail_assessment_json = Column(JSON, nullable=False)
    overall_result = Column(String(20), nullable=False, index=True)  # PASS, WARNING, FAIL

    # Common calculated metrics (duplicated for easier querying)
    average_chalking_rating = Column(Float)  # For CHALK-001
    max_chalking_rating = Column(Float)
    chalking_std_dev = Column(Float)
    chalking_uniformity_index = Column(Float)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="results")

    def __repr__(self):
        return f"<TestResult(id={self.id}, test='{self.test_execution_id}', result='{self.overall_result}')>"
