"""
Database Models and Integration

SQLAlchemy models for storing test protocol data

Author: ganeshgowri-ASA
Date: 2025-11-14
Version: 1.0.0
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class TestRun(Base):
    """Test execution record"""
    __tablename__ = "test_runs"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_id = Column(String(20), index=True, nullable=False)  # e.g., "ML-002"
    protocol_version = Column(String(20))

    # Sample information
    sample_id = Column(String(100), index=True, nullable=False)
    module_type = Column(String(100))
    serial_number = Column(String(100))
    manufacturer = Column(String(200))

    # Test execution
    start_time = Column(DateTime, index=True, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20))  # 'initialized', 'running', 'completed', 'failed', 'aborted'
    passed = Column(Boolean)

    # Test parameters (stored as JSON)
    test_parameters = Column(JSON)

    # Environmental data summary
    environmental_data = Column(JSON)

    # Results summary
    total_cycles = Column(Integer)
    completed_cycles = Column(Integer)
    max_deflection_mm = Column(Float)
    mean_deflection_mm = Column(Float)
    r_squared = Column(Float)

    # Failure information
    failure_reason = Column(Text)

    # Metadata
    operator = Column(String(100))
    facility = Column(String(200))
    equipment_id = Column(String(100))
    notes = Column(Text)

    # Relationships
    sensor_data = relationship("SensorData", back_populates="test_run", cascade="all, delete-orphan")
    cycle_data = relationship("CycleData", back_populates="test_run", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResults", back_populates="test_run", uselist=False, cascade="all, delete-orphan")
    quality_control = relationship("QualityControl", back_populates="test_run", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestRun(id='{self.id}', protocol='{self.protocol_id}', sample='{self.sample_id}', status='{self.status}')>"


class SensorData(Base):
    """Raw sensor readings"""
    __tablename__ = "sensor_data"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id = Column(String(50), ForeignKey('test_runs.id'), index=True, nullable=False)

    sensor_id = Column(String(50), index=True, nullable=False)
    sensor_type = Column(String(50))
    parameter = Column(String(50))

    timestamp = Column(Float, index=True, nullable=False)
    cycle_number = Column(Integer, index=True)

    value = Column(Float, nullable=False)
    unit = Column(String(20))

    # Quality flags
    quality_flag = Column(String(20))  # 'good', 'questionable', 'bad'

    # Relationship
    test_run = relationship("TestRun", back_populates="sensor_data")

    def __repr__(self):
        return f"<SensorData(sensor='{self.sensor_id}', value={self.value}, unit='{self.unit}')>"


class CycleData(Base):
    """Data for each load cycle"""
    __tablename__ = "cycle_data"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id = Column(String(50), ForeignKey('test_runs.id'), index=True, nullable=False)

    cycle_number = Column(Integer, index=True, nullable=False)

    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration_seconds = Column(Float)

    # Load data
    target_load_pa = Column(Float)
    max_load_pa = Column(Float)
    min_load_pa = Column(Float)
    mean_load_pa = Column(Float)

    # Deflection data
    max_deflection_mm = Column(Float)
    min_deflection_mm = Column(Float)
    peak_to_peak_deflection_mm = Column(Float)

    # Deflection at different points
    center_deflection_mm = Column(Float)
    corner1_deflection_mm = Column(Float)
    corner2_deflection_mm = Column(Float)

    # Quality flags
    quality_flags = Column(JSON)
    outlier = Column(Boolean, default=False)

    # Relationship
    test_run = relationship("TestRun", back_populates="cycle_data")

    def __repr__(self):
        return f"<CycleData(cycle={self.cycle_number}, max_deflection={self.max_deflection_mm}mm)>"


class AnalysisResults(Base):
    """Processed analysis results"""
    __tablename__ = "analysis_results"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id = Column(String(50), ForeignKey('test_runs.id'), index=True, nullable=False, unique=True)

    # Deflection statistics
    deflection_mean = Column(Float)
    deflection_std_dev = Column(Float)
    deflection_min = Column(Float)
    deflection_max = Column(Float)
    deflection_coefficient_of_variation = Column(Float)

    # Linearity analysis
    linearity_r_squared = Column(Float)
    linearity_slope = Column(Float)
    linearity_intercept = Column(Float)
    linearity_std_error = Column(Float)

    # Cyclic behavior
    cycle_to_cycle_variation = Column(Float)
    trend_slope = Column(Float)
    trend_p_value = Column(Float)
    fatigue_indicator = Column(Float)

    # Permanent deformation
    permanent_deflection_mm = Column(Float)
    permanent_change_mm = Column(Float)
    permanent_deformation_acceptable = Column(Boolean)

    # Load control quality
    load_control_mean_error_percent = Column(Float)
    load_control_std_error_percent = Column(Float)

    # Environmental stability
    environmental_stable = Column(Boolean)
    temperature_mean = Column(Float)
    temperature_std_dev = Column(Float)
    humidity_mean = Column(Float)
    humidity_std_dev = Column(Float)

    # Full analysis data (JSON)
    full_analysis = Column(JSON)

    # Relationship
    test_run = relationship("TestRun", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResults(test_run='{self.test_run_id}', r_squared={self.linearity_r_squared})>"


class QualityControl(Base):
    """Quality control assessment results"""
    __tablename__ = "quality_control"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id = Column(String(50), ForeignKey('test_runs.id'), index=True, nullable=False, unique=True)

    # Overall assessment
    overall_pass = Column(Boolean, nullable=False)
    total_criteria = Column(Integer)
    passed_criteria = Column(Integer)

    # Individual criteria (Boolean fields for quick queries)
    no_visible_defects = Column(Boolean)
    deflection_linearity_pass = Column(Boolean)
    max_deflection_limit_pass = Column(Boolean)
    deflection_consistency_pass = Column(Boolean)
    load_accuracy_pass = Column(Boolean)
    environmental_stability_pass = Column(Boolean)
    no_permanent_deformation_pass = Column(Boolean)

    # Detailed criteria results (JSON)
    criteria_details = Column(JSON)

    # Failure information
    failed_criteria = Column(JSON)  # List of failed criterion IDs
    critical_failures = Column(JSON)  # List of critical failures

    # Timestamps
    evaluation_time = Column(DateTime, default=datetime.utcnow)

    # Relationship
    test_run = relationship("TestRun", back_populates="quality_control")

    def __repr__(self):
        return f"<QualityControl(test_run='{self.test_run_id}', passed={self.overall_pass})>"


class TestReport(Base):
    """Generated test report"""
    __tablename__ = "test_reports"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id = Column(String(50), ForeignKey('test_runs.id'), index=True, nullable=False)

    report_type = Column(String(20))  # 'summary', 'full', 'qc_only'
    report_format = Column(String(20))  # 'pdf', 'html', 'json'

    report_content = Column(Text)  # HTML, JSON, or base64 encoded PDF
    file_path = Column(String(500))  # If stored as file

    generated_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_by = Column(String(100))

    # Metadata
    report_metadata = Column(JSON)

    def __repr__(self):
        return f"<TestReport(id='{self.id}', type='{self.report_type}', format='{self.report_format}')>"


class CalibrationRecord(Base):
    """Equipment calibration records"""
    __tablename__ = "calibration_records"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))

    equipment_id = Column(String(100), index=True, nullable=False)
    equipment_type = Column(String(50))
    sensor_id = Column(String(50))

    calibration_date = Column(DateTime, index=True, nullable=False)
    calibration_due_date = Column(DateTime, index=True)
    calibrated_by = Column(String(100))

    calibration_certificate = Column(String(100))
    calibration_standard = Column(String(200))

    # Calibration results
    calibration_passed = Column(Boolean)
    calibration_factor = Column(Float)
    accuracy = Column(Float)
    uncertainty = Column(Float)

    # Calibration data
    calibration_data = Column(JSON)

    notes = Column(Text)

    def __repr__(self):
        return f"<CalibrationRecord(equipment='{self.equipment_id}', date='{self.calibration_date}')>"


# Database utility functions

def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """Drop all tables from the database"""
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    from sqlalchemy import create_engine

    # Example: Create SQLite database
    engine = create_engine('sqlite:///ml002_test_data.db', echo=True)
    create_tables(engine)
    print("Database tables created successfully!")
