"""
Base database models for test protocol framework
"""

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Protocol(Base):
    """Protocol definition model"""
    __tablename__ = 'protocols'

    id = Column(String(50), primary_key=True)
    protocol_id = Column(String(100), unique=True, nullable=False, index=True)
    version = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    protocol_type = Column(String(50), nullable=False)

    definition = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("TestExecution", back_populates="protocol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Protocol {self.protocol_id} v{self.version}>"


class TestExecution(Base):
    """Test execution records"""
    __tablename__ = 'test_executions'

    id = Column(String(50), primary_key=True)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(String(100), nullable=False, index=True)

    status = Column(String(20), nullable=False, default='PENDING')
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    parameters = Column(JSON, nullable=False)
    execution_summary = Column(JSON)

    protocol_ref = relationship("Protocol", back_populates="executions")
    results = relationship("TestResult", back_populates="execution", cascade="all, delete-orphan")
    qc_validations = relationship("QCValidation", back_populates="execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestExecution {self.execution_id} [{self.status}]>"


class TestResult(Base):
    """Test measurement results"""
    __tablename__ = 'test_results'

    id = Column(String(50), primary_key=True)
    execution_id = Column(String(100), nullable=False, index=True)

    channel_id = Column(String(100), nullable=False)
    channel_name = Column(String(255))
    unit = Column(String(50))

    data_points = Column(JSON)
    statistics = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("TestExecution", back_populates="results")

    def __repr__(self):
        return f"<TestResult {self.channel_id} for {self.execution_id}>"


class QCValidation(Base):
    """QC validation results"""
    __tablename__ = 'qc_validations'

    id = Column(String(50), primary_key=True)
    execution_id = Column(String(100), nullable=False, index=True)

    test_id = Column(String(100), nullable=False)
    test_name = Column(String(255))
    status = Column(String(20), nullable=False)
    severity = Column(String(20))

    details = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("TestExecution", back_populates="qc_validations")

    def __repr__(self):
        return f"<QCValidation {self.test_id} [{self.status}]>"
