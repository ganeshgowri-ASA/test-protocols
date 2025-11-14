"""Test execution database model"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TestExecution(Base):
    """Test execution (test run) model"""

    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_execution_id = Column(String(100), unique=True, nullable=False, index=True)

    # Protocol reference
    protocol_id = Column(String(50), ForeignKey("protocols.protocol_id"), nullable=False)
    protocol_version = Column(String(20), nullable=False)

    # Sample information
    sample_id = Column(String(100), nullable=False, index=True)
    sample_info_json = Column(JSON, nullable=False)

    # Test conditions
    test_conditions_json = Column(JSON, nullable=False)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Operator information
    operator_id = Column(String(100), nullable=False)
    operator_name = Column(String(255))

    # Test status
    status = Column(
        String(20), default="in_progress"
    )  # in_progress, completed, failed, cancelled

    # Relationships
    measurements = relationship("Measurement", back_populates="test_execution", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test_execution", cascade="all, delete-orphan")
    qc_reviews = relationship("QCReview", back_populates="test_execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution(id='{self.test_execution_id}', protocol='{self.protocol_id}', sample='{self.sample_id}')>"
