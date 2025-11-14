"""
Database models for test protocol framework using SQLAlchemy
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Protocol(Base):
    """Protocol definition table"""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    protocol_name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    standard = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    protocol_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', name='{self.protocol_name}')>"


class Sample(Base):
    """Sample/Device Under Test (DUT) information"""

    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    sample_type = Column(String(100), nullable=True)
    technology = Column(String(100), nullable=True)
    area = Column(Float, nullable=True)  # cm²
    manufacturer = Column(String(200), nullable=True)
    batch_number = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="sample")

    def __repr__(self):
        return f"<Sample(sample_id='{self.sample_id}', type='{self.sample_type}')>"


class Equipment(Base):
    """Equipment/Instrument information"""

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String(100), unique=True, nullable=False, index=True)
    equipment_name = Column(String(200), nullable=False)
    equipment_type = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    calibration_date = Column(DateTime, nullable=True)
    calibration_due_date = Column(DateTime, nullable=True)
    specifications = Column(JSON, nullable=True)
    status = Column(String(50), default="active")  # active, maintenance, retired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_executions = relationship(
        "TestExecution", secondary="test_equipment", back_populates="equipment_used"
    )

    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', name='{self.equipment_name}')>"


class TestExecution(Base):
    """Test execution instance"""

    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(200), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)

    # Test metadata
    operator = Column(String(100), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(
        String(50), default="initialized"
    )  # initialized, running, completed, failed, aborted

    # Test parameters and conditions
    test_parameters = Column(JSON, nullable=True)
    environmental_conditions = Column(JSON, nullable=True)

    # Results
    results_summary = Column(JSON, nullable=True)
    qc_status = Column(String(50), nullable=True)  # passed, warning, failed
    data_file_path = Column(String(500), nullable=True)
    report_file_path = Column(String(500), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_executions")
    sample = relationship("Sample", back_populates="test_executions")
    test_results = relationship("TestResult", back_populates="test_execution")
    qc_results = relationship("QualityControl", back_populates="test_execution")
    equipment_used = relationship(
        "Equipment", secondary="test_equipment", back_populates="test_executions"
    )

    def __repr__(self):
        return f"<TestExecution(test_id='{self.test_id}', status='{self.status}')>"


# Association table for many-to-many relationship between TestExecution and Equipment
from sqlalchemy import Table

test_equipment = Table(
    "test_equipment",
    Base.metadata,
    Column("test_execution_id", Integer, ForeignKey("test_executions.id")),
    Column("equipment_id", Integer, ForeignKey("equipment.id")),
)


class TestResult(Base):
    """Individual test result data points"""

    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_execution_id = Column(
        Integer, ForeignKey("test_executions.id"), nullable=False, index=True
    )

    # Result data
    measurement_type = Column(String(100), nullable=False)  # e.g., 'spectral_response'
    wavelength = Column(Float, nullable=True)  # nm (for spectral measurements)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    uncertainty = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Additional metadata
    metadata = Column(JSON, nullable=True)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="test_results")

    def __repr__(self):
        return f"<TestResult(type='{self.measurement_type}', value={self.value})>"


class QualityControl(Base):
    """Quality control check results"""

    __tablename__ = "quality_control"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_execution_id = Column(
        Integer, ForeignKey("test_executions.id"), nullable=False, index=True
    )

    # QC check information
    check_name = Column(String(100), nullable=False)
    check_type = Column(String(50), nullable=True)  # e.g., 'threshold', 'range', 'stability'
    passed = Column(Boolean, nullable=False)
    measured_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    action = Column(String(50), nullable=True)  # warning, error, info

    # Details
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="qc_results")

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"<QualityControl(check='{self.check_name}', status='{status}')>"


# Database initialization functions
def create_engine_instance(database_url: str = "sqlite:///test_protocols.db"):
    """
    Create SQLAlchemy engine

    Args:
        database_url: Database connection URL

    Returns:
        SQLAlchemy engine
    """
    return create_engine(database_url, echo=False)


# Global engine instance
engine = create_engine_instance()


def init_db(engine=engine):
    """
    Initialize database by creating all tables

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def get_session(engine=engine):
    """
    Get database session

    Args:
        engine: SQLAlchemy engine

    Returns:
        SQLAlchemy session
    """
    Session = sessionmaker(bind=engine)
    return Session()


# Database utility functions
def add_protocol_to_db(protocol_json: dict, session) -> Protocol:
    """
    Add a protocol definition to the database

    Args:
        protocol_json: Protocol JSON data
        session: Database session

    Returns:
        Protocol database object
    """
    protocol = Protocol(
        protocol_id=protocol_json["protocol_id"],
        protocol_name=protocol_json["protocol_name"],
        version=protocol_json["version"],
        standard=protocol_json.get("standard"),
        category=protocol_json.get("category"),
        description=protocol_json.get("description"),
        protocol_json=protocol_json,
    )
    session.add(protocol)
    session.commit()
    return protocol


def add_sample_to_db(sample_info: dict, session) -> Sample:
    """
    Add a sample to the database

    Args:
        sample_info: Sample information dictionary
        session: Database session

    Returns:
        Sample database object
    """
    sample = Sample(
        sample_id=sample_info["sample_id"],
        sample_type=sample_info.get("sample_type"),
        technology=sample_info.get("technology"),
        area=sample_info.get("area"),
        manufacturer=sample_info.get("manufacturer"),
        batch_number=sample_info.get("batch_number"),
        metadata=sample_info,
    )
    session.add(sample)
    session.commit()
    return sample


def create_test_execution(
    test_id: str,
    protocol_id: int,
    sample_id: int,
    operator: str,
    test_parameters: dict,
    session,
) -> TestExecution:
    """
    Create a new test execution record

    Args:
        test_id: Unique test identifier
        protocol_id: Protocol database ID
        sample_id: Sample database ID
        operator: Test operator name
        test_parameters: Test parameters dictionary
        session: Database session

    Returns:
        TestExecution database object
    """
    test_execution = TestExecution(
        test_id=test_id,
        protocol_id=protocol_id,
        sample_id=sample_id,
        operator=operator,
        start_time=datetime.utcnow(),
        test_parameters=test_parameters,
        status="initialized",
    )
    session.add(test_execution)
    session.commit()
    return test_execution
