"""Unit tests for database models"""

import pytest
from datetime import datetime

from database.models import (
    Protocol, TestRun, Measurement, VisualInspection,
    CycleLog, CycleDataPoint, Equipment
)


class TestProtocolModel:
    """Test Protocol database model"""

    def test_create_protocol(self, db_session):
        """Test creating a protocol record"""
        protocol = Protocol(
            protocol_id="HF-001",
            name="Humidity Freeze Test Protocol",
            version="1.0.0",
            standard="IEC 61215 MQT 12",
            category="Environmental Testing",
            description="Test description",
            template_json={"test": "data"}
        )

        db_session.add(protocol)
        db_session.commit()

        assert protocol.id is not None
        assert protocol.protocol_id == "HF-001"
        assert protocol.created_at is not None


class TestTestRunModel:
    """Test TestRun database model"""

    def test_create_test_run(self, db_session):
        """Test creating a test run record"""
        # Create protocol first
        protocol = Protocol(
            protocol_id="HF-001",
            name="Test Protocol",
            version="1.0.0",
            template_json={}
        )
        db_session.add(protocol)
        db_session.commit()

        # Create test run
        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial="MODULE-001",
            operator_id="OP001",
            start_time=datetime.now(),
            status="running"
        )

        db_session.add(test_run)
        db_session.commit()

        assert test_run.id is not None
        assert test_run.test_id == "TEST-001"
        assert test_run.status == "running"

    def test_test_run_relationships(self, db_session):
        """Test TestRun relationships"""
        protocol = Protocol(
            protocol_id="HF-001",
            name="Test",
            version="1.0",
            template_json={}
        )
        db_session.add(protocol)
        db_session.flush()

        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial="MOD-001",
            operator_id="OP001",
            start_time=datetime.now(),
            status="running"
        )
        db_session.add(test_run)
        db_session.commit()

        # Access relationship
        assert test_run.protocol.protocol_id == "HF-001"


class TestMeasurementModel:
    """Test Measurement database model"""

    def test_create_measurement(self, db_session):
        """Test creating a measurement record"""
        protocol = Protocol(
            protocol_id="HF-001",
            name="Test",
            version="1.0",
            template_json={}
        )
        db_session.add(protocol)
        db_session.flush()

        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial="MOD-001",
            operator_id="OP001",
            start_time=datetime.now(),
            status="running"
        )
        db_session.add(test_run)
        db_session.flush()

        measurement = Measurement(
            test_run_id=test_run.id,
            timestamp=datetime.now(),
            parameter="temperature",
            value=85.0,
            unit="°C",
            phase="cycle_1"
        )

        db_session.add(measurement)
        db_session.commit()

        assert measurement.id is not None
        assert measurement.parameter == "temperature"
        assert measurement.value == 85.0


class TestVisualInspectionModel:
    """Test VisualInspection database model"""

    def test_create_visual_inspection(self, db_session):
        """Test creating a visual inspection record"""
        protocol = Protocol(
            protocol_id="HF-001",
            name="Test",
            version="1.0",
            template_json={}
        )
        db_session.add(protocol)
        db_session.flush()

        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial="MOD-001",
            operator_id="OP001",
            start_time=datetime.now(),
            status="running"
        )
        db_session.add(test_run)
        db_session.flush()

        inspection = VisualInspection(
            test_run_id=test_run.id,
            inspection_time=datetime.now(),
            inspection_type="initial",
            broken_cells=0,
            delamination=False,
            junction_box_intact=True,
            discoloration=False,
            bubbles_count=0,
            inspection_passed=True,
            inspector_id="INS001"
        )

        db_session.add(inspection)
        db_session.commit()

        assert inspection.id is not None
        assert inspection.inspection_type == "initial"
        assert inspection.inspection_passed is True


class TestCycleLogModel:
    """Test CycleLog database model"""

    def test_create_cycle_log(self, db_session):
        """Test creating a cycle log record"""
        protocol = Protocol(
            protocol_id="HF-001",
            name="Test",
            version="1.0",
            template_json={}
        )
        db_session.add(protocol)
        db_session.flush()

        test_run = TestRun(
            test_id="TEST-001",
            protocol_id=protocol.id,
            module_serial="MOD-001",
            operator_id="OP001",
            start_time=datetime.now(),
            status="running"
        )
        db_session.add(test_run)
        db_session.flush()

        cycle_log = CycleLog(
            test_run_id=test_run.id,
            cycle_number=1,
            start_time=datetime.now(),
            status="running",
            temp_min=-40.0,
            temp_max=85.0,
            temp_avg=22.5
        )

        db_session.add(cycle_log)
        db_session.commit()

        assert cycle_log.id is not None
        assert cycle_log.cycle_number == 1
        assert cycle_log.temp_min == -40.0


class TestEquipmentModel:
    """Test Equipment database model"""

    def test_create_equipment(self, db_session):
        """Test creating equipment record"""
        equipment = Equipment(
            equipment_id="CHAMBER-01",
            equipment_type="Environmental Chamber",
            manufacturer="TestCo",
            model="TC-1000",
            serial_number="SN12345",
            calibration_required=True,
            calibration_interval_days=365,
            last_calibration_date=datetime.now(),
            status="active"
        )

        db_session.add(equipment)
        db_session.commit()

        assert equipment.id is not None
        assert equipment.equipment_id == "CHAMBER-01"
        assert equipment.status == "active"
