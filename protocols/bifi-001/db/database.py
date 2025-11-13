"""
Database manager for BIFI-001 Bifacial Performance Protocol
Handles CRUD operations and LIMS/QMS integration
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, List, Optional
from datetime import datetime
import json

from .models import (
    Base,
    BifacialTest,
    IVMeasurement,
    BifacialResult,
    QualityCheck,
    CalibrationRecord,
    UncertaintyAnalysis
)


class DatabaseManager:
    """Manages database operations for bifacial testing protocol"""

    def __init__(self, database_url: str = "sqlite:///bifacial_tests.db"):
        """
        Initialize database manager

        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    # ========== BifacialTest Operations ==========

    def create_test(self, test_data: Dict) -> BifacialTest:
        """
        Create a new bifacial test record

        Args:
            test_data: Dictionary containing test data

        Returns:
            Created BifacialTest object
        """
        with self.get_session() as session:
            # Extract metadata
            metadata = test_data.get("metadata", {})
            device = test_data.get("device_under_test", {})
            conditions = test_data.get("test_conditions", {})

            test = BifacialTest(
                protocol_name=metadata.get("protocol_name", "BIFI-001 Bifacial Performance"),
                standard=metadata.get("standard", "IEC 60904-1-2"),
                version=metadata.get("version", "1.0.0"),
                test_date=datetime.fromisoformat(metadata.get("test_date", datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                operator=metadata.get("operator", "Unknown"),
                facility=metadata.get("facility"),
                device_id=device.get("device_id"),
                manufacturer=device.get("manufacturer"),
                model=device.get("model"),
                serial_number=device.get("serial_number"),
                technology=device.get("technology"),
                rated_power_front=device.get("rated_power_front"),
                rated_power_rear=device.get("rated_power_rear"),
                bifaciality_factor_spec=device.get("bifaciality_factor"),
                area_front=device.get("area_front"),
                area_rear=device.get("area_rear"),
                front_irradiance=conditions.get("front_irradiance", {}).get("value"),
                front_irradiance_tolerance=conditions.get("front_irradiance", {}).get("tolerance"),
                front_spectrum=conditions.get("front_irradiance", {}).get("spectrum"),
                rear_irradiance=conditions.get("rear_irradiance", {}).get("value"),
                rear_irradiance_tolerance=conditions.get("rear_irradiance", {}).get("tolerance"),
                rear_spectrum=conditions.get("rear_irradiance", {}).get("spectrum"),
                temperature=conditions.get("temperature", {}).get("value"),
                temperature_tolerance=conditions.get("temperature", {}).get("tolerance"),
                stc_conditions=conditions.get("stc_conditions", False),
                raw_data=test_data,
                status="in_progress"
            )

            session.add(test)
            session.commit()
            session.refresh(test)
            return test

    def get_test(self, test_id: int) -> Optional[BifacialTest]:
        """Get test by ID"""
        with self.get_session() as session:
            return session.query(BifacialTest).filter(BifacialTest.id == test_id).first()

    def get_tests_by_device(self, device_id: str) -> List[BifacialTest]:
        """Get all tests for a specific device"""
        with self.get_session() as session:
            return session.query(BifacialTest).filter(BifacialTest.device_id == device_id).all()

    def get_tests_by_serial(self, serial_number: str) -> List[BifacialTest]:
        """Get all tests for a device serial number"""
        with self.get_session() as session:
            return session.query(BifacialTest).filter(BifacialTest.serial_number == serial_number).all()

    def update_test_status(self, test_id: int, status: str, pass_fail: str = None):
        """Update test status"""
        with self.get_session() as session:
            test = session.query(BifacialTest).filter(BifacialTest.id == test_id).first()
            if test:
                test.status = status
                if pass_fail:
                    test.pass_fail_status = pass_fail
                session.commit()

    # ========== IVMeasurement Operations ==========

    def add_iv_measurement(self, test_id: int, side: str, measurement_data: Dict) -> IVMeasurement:
        """
        Add I-V measurement for a test

        Args:
            test_id: Test ID
            side: 'front' or 'rear'
            measurement_data: Dictionary with measurement data

        Returns:
            Created IVMeasurement object
        """
        with self.get_session() as session:
            measurement = IVMeasurement(
                test_id=test_id,
                side=side,
                isc=measurement_data.get("isc"),
                voc=measurement_data.get("voc"),
                pmax=measurement_data.get("pmax"),
                imp=measurement_data.get("imp"),
                vmp=measurement_data.get("vmp"),
                fill_factor=measurement_data.get("fill_factor"),
                efficiency=measurement_data.get("efficiency"),
                iv_curve_data=measurement_data.get("iv_curve"),
                irradiance=measurement_data.get("irradiance"),
                temperature=measurement_data.get("temperature")
            )

            session.add(measurement)
            session.commit()
            session.refresh(measurement)
            return measurement

    def get_measurements(self, test_id: int, side: str = None) -> List[IVMeasurement]:
        """Get I-V measurements for a test"""
        with self.get_session() as session:
            query = session.query(IVMeasurement).filter(IVMeasurement.test_id == test_id)
            if side:
                query = query.filter(IVMeasurement.side == side)
            return query.all()

    # ========== BifacialResult Operations ==========

    def add_bifacial_result(self, test_id: int, result_data: Dict) -> BifacialResult:
        """Add bifacial calculation results"""
        with self.get_session() as session:
            result = BifacialResult(
                test_id=test_id,
                measured_bifaciality=result_data.get("measured_bifaciality"),
                bifacial_gain=result_data.get("bifacial_gain"),
                equivalent_front_efficiency=result_data.get("equivalent_front_efficiency"),
                combined_iv_curve=result_data.get("combined_iv_curve"),
                bifaciality_deviation=result_data.get("bifaciality_deviation"),
                front_power_deviation=result_data.get("front_power_deviation"),
                rear_power_deviation=result_data.get("rear_power_deviation")
            )

            session.add(result)
            session.commit()
            session.refresh(result)
            return result

    def get_bifacial_result(self, test_id: int) -> Optional[BifacialResult]:
        """Get bifacial results for a test"""
        with self.get_session() as session:
            return session.query(BifacialResult).filter(BifacialResult.test_id == test_id).first()

    # ========== QualityCheck Operations ==========

    def add_quality_check(self, test_id: int, check_data: Dict) -> QualityCheck:
        """Add a quality control check"""
        with self.get_session() as session:
            check = QualityCheck(
                test_id=test_id,
                check_name=check_data.get("check_name"),
                check_type=check_data.get("check_type", "validation"),
                status=check_data.get("status"),
                message=check_data.get("message"),
                details=check_data.get("details")
            )

            session.add(check)
            session.commit()
            session.refresh(check)
            return check

    def get_quality_checks(self, test_id: int) -> List[QualityCheck]:
        """Get all quality checks for a test"""
        with self.get_session() as session:
            return session.query(QualityCheck).filter(QualityCheck.test_id == test_id).all()

    # ========== CalibrationRecord Operations ==========

    def add_calibration_record(self, calibration_data: Dict) -> CalibrationRecord:
        """Add a calibration record"""
        with self.get_session() as session:
            record = CalibrationRecord(
                equipment_id=calibration_data.get("equipment_id"),
                equipment_type=calibration_data.get("equipment_type"),
                equipment_name=calibration_data.get("equipment_name"),
                calibration_date=datetime.fromisoformat(calibration_data.get("calibration_date")),
                next_calibration_due=datetime.fromisoformat(calibration_data.get("next_calibration_due")),
                calibration_authority=calibration_data.get("calibration_authority"),
                certificate_number=calibration_data.get("certificate_number"),
                calibration_values=calibration_data.get("calibration_values"),
                is_current=calibration_data.get("is_current", True),
                notes=calibration_data.get("notes")
            )

            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_current_calibration(self, equipment_id: str) -> Optional[CalibrationRecord]:
        """Get current calibration record for equipment"""
        with self.get_session() as session:
            return session.query(CalibrationRecord).filter(
                and_(
                    CalibrationRecord.equipment_id == equipment_id,
                    CalibrationRecord.is_current == True
                )
            ).first()

    def check_calibration_status(self, equipment_id: str) -> Dict:
        """Check if equipment calibration is current"""
        record = self.get_current_calibration(equipment_id)
        if not record:
            return {"status": "unknown", "message": "No calibration record found"}

        now = datetime.utcnow()
        if now > record.next_calibration_due:
            return {"status": "overdue", "message": "Calibration is overdue", "due_date": record.next_calibration_due}
        elif (record.next_calibration_due - now).days < 30:
            return {"status": "warning", "message": "Calibration due soon", "due_date": record.next_calibration_due}
        else:
            return {"status": "valid", "message": "Calibration is current", "due_date": record.next_calibration_due}

    # ========== UncertaintyAnalysis Operations ==========

    def add_uncertainty_analysis(self, test_id: int, uncertainty_data: Dict) -> UncertaintyAnalysis:
        """Add uncertainty analysis results"""
        with self.get_session() as session:
            analysis = UncertaintyAnalysis(
                test_id=test_id,
                type_a_front=uncertainty_data.get("type_a_front"),
                type_a_rear=uncertainty_data.get("type_a_rear"),
                type_b_reference=uncertainty_data.get("type_b_reference"),
                type_b_spectral=uncertainty_data.get("type_b_spectral"),
                type_b_temperature=uncertainty_data.get("type_b_temperature"),
                type_b_non_uniformity=uncertainty_data.get("type_b_non_uniformity"),
                front_pmax_uncertainty=uncertainty_data.get("front_pmax_uncertainty"),
                rear_pmax_uncertainty=uncertainty_data.get("rear_pmax_uncertainty"),
                combined_uncertainty=uncertainty_data.get("combined_uncertainty"),
                expanded_uncertainty=uncertainty_data.get("expanded_uncertainty")
            )

            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            return analysis

    def get_uncertainty_analysis(self, test_id: int) -> Optional[UncertaintyAnalysis]:
        """Get uncertainty analysis for a test"""
        with self.get_session() as session:
            return session.query(UncertaintyAnalysis).filter(UncertaintyAnalysis.test_id == test_id).first()

    # ========== Reporting and Analytics ==========

    def get_test_summary(self, test_id: int) -> Dict:
        """Get comprehensive test summary"""
        with self.get_session() as session:
            test = session.query(BifacialTest).filter(BifacialTest.id == test_id).first()
            if not test:
                return None

            front_meas = session.query(IVMeasurement).filter(
                and_(IVMeasurement.test_id == test_id, IVMeasurement.side == 'front')
            ).first()

            rear_meas = session.query(IVMeasurement).filter(
                and_(IVMeasurement.test_id == test_id, IVMeasurement.side == 'rear')
            ).first()

            bifacial = session.query(BifacialResult).filter(BifacialResult.test_id == test_id).first()
            qc_checks = session.query(QualityCheck).filter(QualityCheck.test_id == test_id).all()
            uncertainty = session.query(UncertaintyAnalysis).filter(UncertaintyAnalysis.test_id == test_id).first()

            return {
                "test": {
                    "id": test.id,
                    "device_id": test.device_id,
                    "serial_number": test.serial_number,
                    "test_date": test.test_date.isoformat(),
                    "operator": test.operator,
                    "status": test.status,
                    "pass_fail": test.pass_fail_status
                },
                "measurements": {
                    "front": {
                        "pmax": front_meas.pmax if front_meas else None,
                        "efficiency": front_meas.efficiency if front_meas else None
                    } if front_meas else None,
                    "rear": {
                        "pmax": rear_meas.pmax if rear_meas else None,
                        "efficiency": rear_meas.efficiency if rear_meas else None
                    } if rear_meas else None
                },
                "bifacial": {
                    "bifaciality": bifacial.measured_bifaciality if bifacial else None,
                    "gain": bifacial.bifacial_gain if bifacial else None
                } if bifacial else None,
                "quality_checks": [
                    {"name": check.check_name, "status": check.status}
                    for check in qc_checks
                ],
                "uncertainty": {
                    "combined": uncertainty.combined_uncertainty if uncertainty else None
                } if uncertainty else None
            }

    def export_test_data(self, test_id: int) -> Dict:
        """Export complete test data for external systems"""
        test = self.get_test(test_id)
        if not test:
            return None

        # Return the raw_data JSON which contains all protocol information
        return test.raw_data
