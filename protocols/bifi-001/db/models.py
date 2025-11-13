"""
Database models for BIFI-001 Bifacial Performance Protocol
SQLAlchemy models for LIMS/QMS integration
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class BifacialTest(Base):
    """Main test record for bifacial performance testing"""

    __tablename__ = 'bifacial_tests'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Metadata
    protocol_name = Column(String(100), nullable=False, default="BIFI-001 Bifacial Performance")
    standard = Column(String(50), nullable=False, default="IEC 60904-1-2")
    version = Column(String(20), nullable=False, default="1.0.0")
    test_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    operator = Column(String(100), nullable=False)
    facility = Column(String(100))

    # Device information
    device_id = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True, index=True)
    technology = Column(String(50))
    rated_power_front = Column(Float)
    rated_power_rear = Column(Float)
    bifaciality_factor_spec = Column(Float)
    area_front = Column(Float)
    area_rear = Column(Float)

    # Test conditions
    front_irradiance = Column(Float, nullable=False)
    front_irradiance_tolerance = Column(Float)
    front_spectrum = Column(String(20))
    rear_irradiance = Column(Float, nullable=False)
    rear_irradiance_tolerance = Column(Float)
    rear_spectrum = Column(String(20))
    temperature = Column(Float, nullable=False)
    temperature_tolerance = Column(Float)
    stc_conditions = Column(Boolean, default=False)

    # Relationships
    front_measurements = relationship("IVMeasurement", foreign_keys="IVMeasurement.test_id",
                                     primaryjoin="and_(BifacialTest.id==IVMeasurement.test_id, "
                                                "IVMeasurement.side=='front')",
                                     backref="test_front")
    rear_measurements = relationship("IVMeasurement", foreign_keys="IVMeasurement.test_id",
                                    primaryjoin="and_(BifacialTest.id==IVMeasurement.test_id, "
                                               "IVMeasurement.side=='rear')",
                                    backref="test_rear")
    bifacial_results = relationship("BifacialResult", back_populates="test", uselist=False)
    qc_checks = relationship("QualityCheck", back_populates="test")

    # Status and results
    status = Column(String(20), default="pending")  # pending, in_progress, completed, failed
    pass_fail_status = Column(String(20))  # pass, fail, conditional

    # Raw data storage
    raw_data = Column(JSON)  # Complete test data in JSON format

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BifacialTest(id={self.id}, device_id='{self.device_id}', date={self.test_date})>"


class IVMeasurement(Base):
    """I-V curve measurements for front or rear side"""

    __tablename__ = 'iv_measurements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('bifacial_tests.id'), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'front' or 'rear'

    # Calculated parameters
    isc = Column(Float, nullable=False)  # Short-circuit current (A)
    voc = Column(Float, nullable=False)  # Open-circuit voltage (V)
    pmax = Column(Float, nullable=False)  # Maximum power (W)
    imp = Column(Float, nullable=False)  # Current at max power (A)
    vmp = Column(Float, nullable=False)  # Voltage at max power (V)
    fill_factor = Column(Float, nullable=False)  # Fill factor (0-1)
    efficiency = Column(Float)  # Efficiency (%)

    # I-V curve data
    iv_curve_data = Column(JSON)  # Array of {voltage, current, timestamp} points

    # Metadata
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)
    irradiance = Column(Float)  # Irradiance during measurement (W/m²)
    temperature = Column(Float)  # Temperature during measurement (°C)

    def __repr__(self):
        return f"<IVMeasurement(id={self.id}, test_id={self.test_id}, side='{self.side}', pmax={self.pmax}W)>"


class BifacialResult(Base):
    """Bifacial-specific calculation results"""

    __tablename__ = 'bifacial_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('bifacial_tests.id'), nullable=False, unique=True, index=True)
    test = relationship("BifacialTest", back_populates="bifacial_results")

    # Bifacial parameters
    measured_bifaciality = Column(Float, nullable=False)  # Measured bifaciality factor
    bifacial_gain = Column(Float, nullable=False)  # Gain from rear illumination (%)
    equivalent_front_efficiency = Column(Float)  # Equivalent efficiency (%)

    # Combined I-V curve
    combined_iv_curve = Column(JSON)  # Combined front+rear I-V data

    # Deviation analysis
    bifaciality_deviation = Column(Float)  # Deviation from spec (%)
    front_power_deviation = Column(Float)  # Deviation from rated (%)
    rear_power_deviation = Column(Float)  # Deviation from rated (%)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BifacialResult(test_id={self.test_id}, bifaciality={self.measured_bifaciality:.3f})>"


class QualityCheck(Base):
    """Quality control and validation checks"""

    __tablename__ = 'quality_checks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('bifacial_tests.id'), nullable=False, index=True)
    test = relationship("BifacialTest", back_populates="qc_checks")

    check_name = Column(String(100), nullable=False)
    check_type = Column(String(50))  # validation, calibration, uncertainty, etc.
    status = Column(String(20), nullable=False)  # pass, fail, warning
    message = Column(Text)
    details = Column(JSON)  # Additional check-specific data

    checked_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QualityCheck(id={self.id}, name='{self.check_name}', status='{self.status}')>"


class CalibrationRecord(Base):
    """Calibration records for reference cells and equipment"""

    __tablename__ = 'calibration_records'

    id = Column(Integer, primary_key=True, autoincrement=True)

    equipment_id = Column(String(100), nullable=False, index=True)
    equipment_type = Column(String(50), nullable=False)  # reference_cell_front, reference_cell_rear, etc.
    equipment_name = Column(String(100))

    calibration_date = Column(DateTime, nullable=False)
    next_calibration_due = Column(DateTime, nullable=False)
    calibration_authority = Column(String(100))  # Calibration lab/authority
    certificate_number = Column(String(100))

    # Calibration values
    calibration_values = Column(JSON)  # Specific calibration parameters

    # Status
    is_current = Column(Boolean, default=True)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalibrationRecord(id={self.id}, equipment='{self.equipment_id}', date={self.calibration_date})>"


class UncertaintyAnalysis(Base):
    """Measurement uncertainty analysis results"""

    __tablename__ = 'uncertainty_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('bifacial_tests.id'), nullable=False, unique=True, index=True)

    # Type A uncertainties (statistical)
    type_a_front = Column(Float)
    type_a_rear = Column(Float)

    # Type B uncertainties (systematic)
    type_b_reference = Column(Float)
    type_b_spectral = Column(Float)
    type_b_temperature = Column(Float)
    type_b_non_uniformity = Column(Float)

    # Combined uncertainties
    front_pmax_uncertainty = Column(Float, nullable=False)
    rear_pmax_uncertainty = Column(Float, nullable=False)
    combined_uncertainty = Column(Float, nullable=False)

    # Expanded uncertainty (k=2 for 95% confidence)
    expanded_uncertainty = Column(Float)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UncertaintyAnalysis(test_id={self.test_id}, combined_u={self.combined_uncertainty}%)>"
