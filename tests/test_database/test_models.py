"""Tests for Database Models

Unit tests for SQLAlchemy database models.
"""

import pytest
from datetime import datetime, timedelta

from database.models import (
    Protocol,
    TestRun,
    Measurement,
    VisualInspectionRecord,
    HotSpotTest,
    Equipment,
    EquipmentCalibration,
    TestStatus,
    DefectSeverity
)


class TestProtocolModel:
    """Test Protocol model"""

    def test_create_protocol(self, db_session):
        """Test creating a protocol record"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09",
            category="Safety Testing",
            description="Test description"
        )

        db_session.add(protocol)
        db_session.commit()

        assert protocol.id is not None
        assert protocol.protocol_id == "HOT-001"

    def test_protocol_relationships(self, db_session):
        """Test protocol relationships with test runs"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )

        db_session.add(protocol)
        db_session.commit()

        # Add test run
        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial_number="MODULE-001",
            operator_name="Test Operator",
            start_time=datetime.now()
        )

        db_session.add(test_run)
        db_session.commit()

        assert len(protocol.test_runs) == 1
        assert protocol.test_runs[0].test_id == "TEST-001"


class TestTestRunModel:
    """Test TestRun model"""

    def test_create_test_run(self, db_session):
        """Test creating a test run record"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial_number="MODULE-001",
            module_manufacturer="Test Solar Inc.",
            module_model="TEST-300W",
            operator_name="Test Operator",
            test_facility="Test Lab",
            start_time=datetime.now(),
            status=TestStatus.RUNNING
        )

        db_session.add(test_run)
        db_session.commit()

        assert test_run.id is not None
        assert test_run.status == TestStatus.RUNNING

    def test_test_run_complete_flow(self, db_session):
        """Test complete test run lifecycle"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        # Create test run
        start_time = datetime.now()
        test_run = TestRun(
            test_id="TEST-002",
            protocol_id=protocol.id,
            module_serial_number="MODULE-002",
            operator_name="Test Operator",
            start_time=start_time,
            status=TestStatus.RUNNING,
            initial_pmax=300.0
        )

        db_session.add(test_run)
        db_session.commit()

        # Complete test run
        test_run.end_time = datetime.now()
        test_run.status = TestStatus.COMPLETED
        test_run.final_pmax = 291.0
        test_run.power_degradation_percent = 3.0
        test_run.pass_fail = True

        db_session.commit()

        retrieved = db_session.query(TestRun).filter_by(test_id="TEST-002").first()
        assert retrieved.status == TestStatus.COMPLETED
        assert retrieved.pass_fail is True
        assert retrieved.power_degradation_percent == 3.0


class TestMeasurementModel:
    """Test Measurement model"""

    def test_create_measurement(self, db_session):
        """Test creating measurement records"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-003",
            protocol_id=protocol.id,
            module_serial_number="MODULE-003",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        # Add measurements
        measurement = Measurement(
            test_run_id=test_run.id,
            timestamp=datetime.now(),
            parameter="temperature",
            value=85.5,
            unit="°C",
            notes="Hot spot test cell A1"
        )

        db_session.add(measurement)
        db_session.commit()

        assert measurement.id is not None
        assert measurement.parameter == "temperature"
        assert measurement.value == 85.5

    def test_measurement_relationships(self, db_session):
        """Test measurement relationships"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-004",
            protocol_id=protocol.id,
            module_serial_number="MODULE-004",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        # Add multiple measurements
        for i in range(5):
            measurement = Measurement(
                test_run_id=test_run.id,
                timestamp=datetime.now(),
                parameter=f"param_{i}",
                value=float(i),
                unit="units"
            )
            db_session.add(measurement)

        db_session.commit()

        assert len(test_run.measurements) == 5


class TestVisualInspectionModel:
    """Test VisualInspectionRecord model"""

    def test_create_visual_inspection(self, db_session):
        """Test creating visual inspection record"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-005",
            protocol_id=protocol.id,
            module_serial_number="MODULE-005",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        inspection = VisualInspectionRecord(
            test_run_id=test_run.id,
            inspection_type="initial",
            timestamp=datetime.now(),
            inspector="Test Inspector",
            defects=[{"type": "crack", "description": "Small crack in cell A5"}],
            severity=DefectSeverity.MINOR,
            notes="Minor defect found"
        )

        db_session.add(inspection)
        db_session.commit()

        assert inspection.id is not None
        assert inspection.severity == DefectSeverity.MINOR
        assert len(inspection.defects) == 1


class TestHotSpotTestModel:
    """Test HotSpotTest model"""

    def test_create_hot_spot_test(self, db_session):
        """Test creating hot spot test record"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-006",
            protocol_id=protocol.id,
            module_serial_number="MODULE-006",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        # Create temperature profile
        start_time = datetime.now()
        temp_profile = [
            [start_time.isoformat(), 25.0],
            [(start_time + timedelta(minutes=30)).isoformat(), 85.0],
            [(start_time + timedelta(hours=1)).isoformat(), 85.5]
        ]

        hot_spot = HotSpotTest(
            test_run_id=test_run.id,
            cell_id="A1",
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            target_temperature=85.0,
            max_temperature_reached=85.5,
            reverse_bias_voltage=50.0,
            current_limit=9.0,
            temperature_profile=temp_profile,
            completed=True
        )

        db_session.add(hot_spot)
        db_session.commit()

        assert hot_spot.id is not None
        assert hot_spot.cell_id == "A1"
        assert hot_spot.completed is True
        assert hot_spot.max_temperature_reached == 85.5

    def test_multiple_hot_spot_tests(self, db_session):
        """Test multiple hot spot tests for one test run"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-007",
            protocol_id=protocol.id,
            module_serial_number="MODULE-007",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        # Add 3 hot spot tests
        for cell_id in ['A1', 'B5', 'C9']:
            hot_spot = HotSpotTest(
                test_run_id=test_run.id,
                cell_id=cell_id,
                start_time=datetime.now(),
                target_temperature=85.0,
                reverse_bias_voltage=50.0,
                current_limit=9.0,
                completed=True
            )
            db_session.add(hot_spot)

        db_session.commit()

        assert len(test_run.hot_spot_tests) == 3


class TestEquipmentModel:
    """Test Equipment model"""

    def test_create_equipment(self, db_session):
        """Test creating equipment record"""
        equipment = Equipment(
            equipment_id="SIM-001",
            name="Solar Simulator A",
            equipment_type="solar_simulator",
            manufacturer="Test Equipment Inc.",
            model="SIM-1000",
            serial_number="SN-12345",
            specifications={
                "irradiance": "1000 W/m²",
                "uniformity": "±2%",
                "spectral_match": "Class A"
            },
            location="Lab Room 1",
            status="active"
        )

        db_session.add(equipment)
        db_session.commit()

        assert equipment.id is not None
        assert equipment.equipment_id == "SIM-001"
        assert equipment.status == "active"


class TestEquipmentCalibrationModel:
    """Test EquipmentCalibration model"""

    def test_create_calibration(self, db_session):
        """Test creating calibration record"""
        equipment = Equipment(
            equipment_id="SIM-002",
            name="Solar Simulator B",
            equipment_type="solar_simulator",
            manufacturer="Test Equipment Inc.",
            model="SIM-2000"
        )
        db_session.add(equipment)
        db_session.commit()

        cal_date = datetime.now()
        due_date = cal_date + timedelta(days=365)

        calibration = EquipmentCalibration(
            equipment_id=equipment.id,
            calibration_date=cal_date,
            calibration_due_date=due_date,
            calibration_certificate="CERT-2025-001",
            performed_by="Calibration Lab",
            calibration_standard="NIST Traceable",
            is_valid=True
        )

        db_session.add(calibration)
        db_session.commit()

        assert calibration.id is not None
        assert calibration.is_valid is True

    def test_calibration_relationships(self, db_session):
        """Test calibration relationships"""
        equipment = Equipment(
            equipment_id="SIM-003",
            name="Solar Simulator C",
            equipment_type="solar_simulator"
        )
        db_session.add(equipment)
        db_session.commit()

        # Add multiple calibrations
        for i in range(3):
            cal = EquipmentCalibration(
                equipment_id=equipment.id,
                calibration_date=datetime.now() - timedelta(days=365*i),
                calibration_due_date=datetime.now() + timedelta(days=365*(1-i)),
                performed_by="Calibration Lab"
            )
            db_session.add(cal)

        db_session.commit()

        assert len(equipment.calibrations) == 3


class TestCascadeDeletes:
    """Test cascade delete behavior"""

    def test_delete_protocol_cascades(self, db_session):
        """Test deleting protocol cascades to test runs"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-008",
            protocol_id=protocol.id,
            module_serial_number="MODULE-008",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        protocol_id = protocol.id
        test_run_id = test_run.id

        # Delete protocol
        db_session.delete(protocol)
        db_session.commit()

        # Test run should be deleted
        deleted_test_run = db_session.query(TestRun).filter_by(id=test_run_id).first()
        assert deleted_test_run is None

    def test_delete_test_run_cascades(self, db_session):
        """Test deleting test run cascades to measurements"""
        protocol = Protocol(
            protocol_id="HOT-001",
            name="Hot Spot Endurance Test",
            version="1.0.0",
            standard="IEC 61215 MQT 09"
        )
        db_session.add(protocol)
        db_session.commit()

        test_run = TestRun(
            test_id="TEST-009",
            protocol_id=protocol.id,
            module_serial_number="MODULE-009",
            operator_name="Test Operator",
            start_time=datetime.now()
        )
        db_session.add(test_run)
        db_session.commit()

        measurement = Measurement(
            test_run_id=test_run.id,
            timestamp=datetime.now(),
            parameter="temperature",
            value=85.0,
            unit="°C"
        )
        db_session.add(measurement)
        db_session.commit()

        measurement_id = measurement.id

        # Delete test run
        db_session.delete(test_run)
        db_session.commit()

        # Measurement should be deleted
        deleted_measurement = db_session.query(Measurement).filter_by(id=measurement_id).first()
        assert deleted_measurement is None
