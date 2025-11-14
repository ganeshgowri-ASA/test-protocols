"""
Database Models for SPONGE-001 Protocol
SQLAlchemy ORM models for test data management
"""

from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4
import json

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, JSON,
    ForeignKey, CheckConstraint, UniqueConstraint, Enum as SQLEnum,
    create_engine
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class SpongeTest(Base):
    """Main test information"""
    __tablename__ = 'sponge_tests'

    test_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    protocol_version = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    operator_id = Column(String(100), nullable=False)
    chamber_id = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    test_parameters = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    samples = relationship("SpongeSample", back_populates="test", cascade="all, delete-orphan")
    analyses = relationship("SpongeAnalysis", back_populates="test", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed', 'aborted')",
            name='valid_status'
        ),
    )

    def __repr__(self):
        return f"<SpongeTest(test_id={self.test_id}, status={self.status})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'test_id': str(self.test_id),
            'protocol_version': self.protocol_version,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'operator_id': self.operator_id,
            'chamber_id': self.chamber_id,
            'notes': self.notes,
            'test_parameters': self.test_parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SpongeSample(Base):
    """Sample information and characterization"""
    __tablename__ = 'sponge_samples'

    sample_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey('sponge_tests.test_id', ondelete='CASCADE'), nullable=False)
    sample_serial = Column(String(100), nullable=False, unique=True)
    manufacturer = Column(String(200), nullable=True)
    model = Column(String(200), nullable=True)
    technology_type = Column(String(100), nullable=True)
    rated_power_w = Column(Float, nullable=True)

    # Initial characterization
    initial_weight_g = Column(Float, nullable=True)
    initial_pmax_w = Column(Float, nullable=True)
    initial_voc_v = Column(Float, nullable=True)
    initial_isc_a = Column(Float, nullable=True)
    initial_ff_percent = Column(Float, nullable=True)

    # Final characterization
    final_weight_g = Column(Float, nullable=True)
    final_pmax_w = Column(Float, nullable=True)
    final_voc_v = Column(Float, nullable=True)
    final_isc_a = Column(Float, nullable=True)
    final_ff_percent = Column(Float, nullable=True)

    # Visual inspection
    initial_inspection = Column(JSONB, nullable=True)
    final_inspection = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    test = relationship("SpongeTest", back_populates="samples")
    measurements = relationship("SpongeMeasurement", back_populates="sample", cascade="all, delete-orphan")
    analysis = relationship("SpongeAnalysis", back_populates="sample", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SpongeSample(sample_serial={self.sample_serial})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'sample_id': str(self.sample_id),
            'test_id': str(self.test_id),
            'sample_serial': self.sample_serial,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'technology_type': self.technology_type,
            'rated_power_w': self.rated_power_w,
            'initial_weight_g': self.initial_weight_g,
            'initial_pmax_w': self.initial_pmax_w,
            'initial_voc_v': self.initial_voc_v,
            'initial_isc_a': self.initial_isc_a,
            'initial_ff_percent': self.initial_ff_percent,
            'final_weight_g': self.final_weight_g,
            'final_pmax_w': self.final_pmax_w,
            'final_voc_v': self.final_voc_v,
            'final_isc_a': self.final_isc_a,
            'final_ff_percent': self.final_ff_percent,
            'initial_inspection': self.initial_inspection,
            'final_inspection': self.final_inspection
        }


class SpongeMeasurement(Base):
    """Individual measurement data points"""
    __tablename__ = 'sponge_measurements'

    measurement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey('sponge_samples.sample_id', ondelete='CASCADE'), nullable=False)
    cycle_number = Column(Integer, nullable=False)
    phase = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Weight measurements
    weight_g = Column(Float, nullable=True)

    # Electrical measurements
    pmax_w = Column(Float, nullable=True)
    voc_v = Column(Float, nullable=True)
    isc_a = Column(Float, nullable=True)
    ff_percent = Column(Float, nullable=True)

    # Environmental conditions
    temperature_c = Column(Float, nullable=True)
    rh_percent = Column(Float, nullable=True)

    # Additional data
    additional_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    sample = relationship("SpongeSample", back_populates="measurements")

    __table_args__ = (
        CheckConstraint("phase IN ('initial', 'humid', 'dry', 'final')", name='valid_phase'),
        CheckConstraint("cycle_number >= 0", name='valid_cycle'),
        CheckConstraint("rh_percent IS NULL OR (rh_percent >= 0 AND rh_percent <= 100)", name='valid_rh'),
    )

    def __repr__(self):
        return f"<SpongeMeasurement(sample_id={self.sample_id}, cycle={self.cycle_number}, phase={self.phase})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'measurement_id': str(self.measurement_id),
            'sample_id': str(self.sample_id),
            'cycle_number': self.cycle_number,
            'phase': self.phase,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'weight_g': self.weight_g,
            'pmax_w': self.pmax_w,
            'voc_v': self.voc_v,
            'isc_a': self.isc_a,
            'ff_percent': self.ff_percent,
            'temperature_c': self.temperature_c,
            'rh_percent': self.rh_percent,
            'additional_data': self.additional_data
        }


class SpongeAnalysis(Base):
    """Analysis results and quality control"""
    __tablename__ = 'sponge_analysis'

    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey('sponge_tests.test_id', ondelete='CASCADE'), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey('sponge_samples.sample_id', ondelete='CASCADE'), nullable=False)

    # Moisture metrics
    moisture_absorption_percent = Column(Float, nullable=True)
    moisture_desorption_percent = Column(Float, nullable=True)
    sponge_coefficient = Column(Float, nullable=True)
    avg_absorption_rate_g_per_cycle = Column(Float, nullable=True)
    avg_desorption_rate_g_per_cycle = Column(Float, nullable=True)

    # Performance degradation
    pmax_degradation_percent = Column(Float, nullable=True)
    voc_degradation_percent = Column(Float, nullable=True)
    isc_degradation_percent = Column(Float, nullable=True)
    ff_degradation_percent = Column(Float, nullable=True)

    # Reversible vs irreversible
    reversible_degradation_percent = Column(Float, nullable=True)
    irreversible_degradation_percent = Column(Float, nullable=True)

    # Quality control
    pass_fail = Column(String(20), nullable=False)
    qc_notes = Column(Text, nullable=True)

    # Analysis metadata
    analysis_date = Column(DateTime, server_default=func.now())
    analyzed_by = Column(String(100), nullable=True)

    # Detailed results
    detailed_results = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    test = relationship("SpongeTest", back_populates="analyses")
    sample = relationship("SpongeSample", back_populates="analysis")

    __table_args__ = (
        CheckConstraint("pass_fail IN ('PASS', 'FAIL', 'WARNING')", name='valid_pass_fail'),
        UniqueConstraint('test_id', 'sample_id', name='unique_test_sample_analysis'),
    )

    def __repr__(self):
        return f"<SpongeAnalysis(sample_id={self.sample_id}, pass_fail={self.pass_fail})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'analysis_id': str(self.analysis_id),
            'test_id': str(self.test_id),
            'sample_id': str(self.sample_id),
            'moisture_absorption_percent': self.moisture_absorption_percent,
            'moisture_desorption_percent': self.moisture_desorption_percent,
            'sponge_coefficient': self.sponge_coefficient,
            'avg_absorption_rate_g_per_cycle': self.avg_absorption_rate_g_per_cycle,
            'avg_desorption_rate_g_per_cycle': self.avg_desorption_rate_g_per_cycle,
            'pmax_degradation_percent': self.pmax_degradation_percent,
            'voc_degradation_percent': self.voc_degradation_percent,
            'isc_degradation_percent': self.isc_degradation_percent,
            'ff_degradation_percent': self.ff_degradation_percent,
            'reversible_degradation_percent': self.reversible_degradation_percent,
            'irreversible_degradation_percent': self.irreversible_degradation_percent,
            'pass_fail': self.pass_fail,
            'qc_notes': self.qc_notes,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'analyzed_by': self.analyzed_by,
            'detailed_results': self.detailed_results
        }


class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, connection_string: str):
        """
        Initialize database manager

        Args:
            connection_string: SQLAlchemy connection string
                              e.g., 'postgresql://user:pass@localhost/dbname'
        """
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()


# Data Access Layer
class SpongeDataAccess:
    """Data access layer for SPONGE-001 protocol"""

    def __init__(self, session: Session):
        """
        Initialize data access

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create_test(self, protocol_version: str, operator_id: str,
                   chamber_id: str, test_parameters: Dict = None,
                   notes: str = None) -> SpongeTest:
        """Create a new test"""
        test = SpongeTest(
            protocol_version=protocol_version,
            start_date=datetime.now(),
            status='pending',
            operator_id=operator_id,
            chamber_id=chamber_id,
            test_parameters=test_parameters,
            notes=notes
        )
        self.session.add(test)
        self.session.commit()
        return test

    def create_sample(self, test_id: str, sample_serial: str,
                     **kwargs) -> SpongeSample:
        """Create a new sample"""
        sample = SpongeSample(
            test_id=test_id,
            sample_serial=sample_serial,
            **kwargs
        )
        self.session.add(sample)
        self.session.commit()
        return sample

    def create_measurement(self, sample_id: str, cycle_number: int,
                          phase: str, **kwargs) -> SpongeMeasurement:
        """Create a new measurement"""
        measurement = SpongeMeasurement(
            sample_id=sample_id,
            cycle_number=cycle_number,
            phase=phase,
            timestamp=datetime.now(),
            **kwargs
        )
        self.session.add(measurement)
        self.session.commit()
        return measurement

    def create_analysis(self, test_id: str, sample_id: str,
                       pass_fail: str, **kwargs) -> SpongeAnalysis:
        """Create analysis results"""
        analysis = SpongeAnalysis(
            test_id=test_id,
            sample_id=sample_id,
            pass_fail=pass_fail,
            **kwargs
        )
        self.session.add(analysis)
        self.session.commit()
        return analysis

    def get_test(self, test_id: str) -> Optional[SpongeTest]:
        """Get test by ID"""
        return self.session.query(SpongeTest).filter_by(test_id=test_id).first()

    def get_test_samples(self, test_id: str) -> List[SpongeSample]:
        """Get all samples for a test"""
        return self.session.query(SpongeSample).filter_by(test_id=test_id).all()

    def get_sample_measurements(self, sample_id: str) -> List[SpongeMeasurement]:
        """Get all measurements for a sample"""
        return self.session.query(SpongeMeasurement).filter_by(
            sample_id=sample_id
        ).order_by(SpongeMeasurement.cycle_number, SpongeMeasurement.timestamp).all()

    def update_test_status(self, test_id: str, status: str):
        """Update test status"""
        test = self.get_test(test_id)
        if test:
            test.status = status
            if status == 'completed':
                test.end_date = datetime.now()
            self.session.commit()

    def get_tests_by_status(self, status: str) -> List[SpongeTest]:
        """Get all tests with given status"""
        return self.session.query(SpongeTest).filter_by(status=status).all()

    def get_analysis_summary(self, test_id: str) -> Dict:
        """Get analysis summary for a test"""
        analyses = self.session.query(SpongeAnalysis).filter_by(test_id=test_id).all()

        summary = {
            'total_samples': len(analyses),
            'passed': sum(1 for a in analyses if a.pass_fail == 'PASS'),
            'failed': sum(1 for a in analyses if a.pass_fail == 'FAIL'),
            'warnings': sum(1 for a in analyses if a.pass_fail == 'WARNING'),
            'avg_pmax_degradation': sum(a.pmax_degradation_percent or 0 for a in analyses) / len(analyses) if analyses else 0,
            'avg_moisture_absorption': sum(a.moisture_absorption_percent or 0 for a in analyses) / len(analyses) if analyses else 0
        }

        return summary


# Example usage
if __name__ == "__main__":
    # Create in-memory SQLite database for testing
    db = DatabaseManager('sqlite:///:memory:')
    db.create_tables()

    # Create a session
    session = db.get_session()
    dao = SpongeDataAccess(session)

    # Create test
    test = dao.create_test(
        protocol_version='1.0.0',
        operator_id='operator@example.com',
        chamber_id='CHAMBER-01',
        test_parameters={'cycles': 10, 'humid_temp': 85}
    )
    print(f"Created test: {test.test_id}")

    # Create samples
    for i in range(3):
        sample = dao.create_sample(
            test_id=test.test_id,
            sample_serial=f'MODULE-{i+1:03d}',
            manufacturer='Test Manufacturer',
            model='Test Model'
        )
        print(f"Created sample: {sample.sample_serial}")

        # Create measurement
        measurement = dao.create_measurement(
            sample_id=sample.sample_id,
            cycle_number=0,
            phase='initial',
            weight_g=18000.0,
            pmax_w=300.0
        )
        print(f"Created measurement for {sample.sample_serial}")

    session.close()
    print("Database operations completed successfully!")
