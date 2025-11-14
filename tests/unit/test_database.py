"""
Unit Tests for Database Models
Tests for SQLAlchemy models and database operations
"""

import pytest
from datetime import datetime

from database.models import (
    Protocol, Module, TestExecution, Measurement,
    EnvironmentalLog, CalibrationRecord, QualityEvent,
    ProtocolStatus, TestResult
)


class TestProtocolModel:
    """Tests for Protocol model"""

    def test_create_protocol(self, db_session):
        """Test creating a protocol record"""
        protocol = Protocol(
            protocol_id="P37-54",
            code="H2S-001",
            name="Hydrogen Sulfide Exposure Test",
            category="Environmental",
            subcategory="Chemical Exposure",
            version="1.0.0",
            status="active",
            effective_date=datetime(2025, 11, 14),
            description="H2S exposure test for PV modules"
        )

        db_session.add(protocol)
        db_session.commit()

        assert protocol.id is not None
        assert protocol.code == "H2S-001"

    def test_protocol_unique_constraint(self, db_session):
        """Test protocol_id unique constraint"""
        protocol1 = Protocol(
            protocol_id="P37-54",
            code="H2S-001",
            name="Test",
            category="Environmental",
            version="1.0.0",
            status="active"
        )
        db_session.add(protocol1)
        db_session.commit()

        protocol2 = Protocol(
            protocol_id="P37-54",  # Duplicate
            code="H2S-002",
            name="Test 2",
            category="Environmental",
            version="1.0.0",
            status="active"
        )
        db_session.add(protocol2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestModuleModel:
    """Tests for Module model"""

    def test_create_module(self, db_session):
        """Test creating a module record"""
        module = Module(
            module_id="TEST-001",
            manufacturer="Test Manufacturer",
            model="TEST-MODEL-100",
            technology="mono-Si",
            nameplate_power=400.0,
            serial_number="SN123456",
            dimensions_length=1.7,
            dimensions_width=1.0,
            weight=22.5
        )

        db_session.add(module)
        db_session.commit()

        assert module.id is not None
        assert module.module_id == "TEST-001"

    def test_module_unique_constraint(self, db_session):
        """Test module_id unique constraint"""
        module1 = Module(
            module_id="TEST-001",
            manufacturer="Test",
            model="Model",
            technology="mono-Si",
            nameplate_power=400.0
        )
        db_session.add(module1)
        db_session.commit()

        module2 = Module(
            module_id="TEST-001",  # Duplicate
            manufacturer="Test 2",
            model="Model 2",
            technology="poly-Si",
            nameplate_power=350.0
        )
        db_session.add(module2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestExecutionModel:
    """Tests for TestExecution model"""

    def test_create_execution(self, db_session):
        """Test creating a test execution record"""
        # Create protocol and module first
        protocol = Protocol(
            protocol_id="P37-54",
            code="H2S-001",
            name="H2S Test",
            category="Environmental",
            version="1.0.0",
            status="active"
        )
        module = Module(
            module_id="TEST-001",
            manufacturer="Test",
            model="Model",
            technology="mono-Si",
            nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        # Create execution
        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator",
            status=ProtocolStatus.IN_PROGRESS,
            severity_level=2
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.id is not None
        assert execution.execution_id == "EXEC-001"
        assert execution.status == ProtocolStatus.IN_PROGRESS

    def test_execution_with_measurements(self, db_session):
        """Test execution with electrical measurements"""
        protocol = Protocol(
            protocol_id="P37-54", code="H2S-001", name="Test",
            category="Environmental", version="1.0.0", status="active"
        )
        module = Module(
            module_id="TEST-001", manufacturer="Test", model="Model",
            technology="mono-Si", nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator",
            baseline_voc=47.5,
            baseline_isc=10.8,
            baseline_pmax=400.0,
            post_voc=47.2,
            post_isc=10.6,
            post_pmax=388.0,
            degradation_pmax=-3.0
        )
        db_session.add(execution)
        db_session.commit()

        assert execution.baseline_pmax == 400.0
        assert execution.post_pmax == 388.0
        assert execution.degradation_pmax == -3.0

    def test_execution_relationships(self, db_session):
        """Test execution relationships with protocol and module"""
        protocol = Protocol(
            protocol_id="P37-54", code="H2S-001", name="Test",
            category="Environmental", version="1.0.0", status="active"
        )
        module = Module(
            module_id="TEST-001", manufacturer="Test", model="Model",
            technology="mono-Si", nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator"
        )
        db_session.add(execution)
        db_session.commit()

        # Test relationships
        assert execution.protocol.code == "H2S-001"
        assert execution.module.module_id == "TEST-001"


class TestMeasurementModel:
    """Tests for Measurement model"""

    def test_create_measurement(self, db_session):
        """Test creating a measurement record"""
        # Create dependencies
        protocol = Protocol(
            protocol_id="P37-54", code="H2S-001", name="Test",
            category="Environmental", version="1.0.0", status="active"
        )
        module = Module(
            module_id="TEST-001", manufacturer="Test", model="Model",
            technology="mono-Si", nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator"
        )
        db_session.add(execution)
        db_session.commit()

        # Create measurement
        measurement = Measurement(
            execution_id=execution.id,
            table_name="baseline_electrical",
            field_name="Voc",
            value=47.5,
            unit="V",
            phase="Phase 1",
            step="1.3"
        )
        db_session.add(measurement)
        db_session.commit()

        assert measurement.id is not None
        assert measurement.value == 47.5
        assert measurement.unit == "V"


class TestEnvironmentalLog:
    """Tests for EnvironmentalLog model"""

    def test_create_environmental_log(self, db_session):
        """Test creating environmental log entries"""
        protocol = Protocol(
            protocol_id="P37-54", code="H2S-001", name="Test",
            category="Environmental", version="1.0.0", status="active"
        )
        module = Module(
            module_id="TEST-001", manufacturer="Test", model="Model",
            technology="mono-Si", nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator"
        )
        db_session.add(execution)
        db_session.commit()

        # Create log entry
        log_entry = EnvironmentalLog(
            execution_id=execution.id,
            timestamp=datetime.now(),
            h2s_ppm=10.2,
            temperature_c=40.5,
            humidity_rh=85.2
        )
        db_session.add(log_entry)
        db_session.commit()

        assert log_entry.id is not None
        assert log_entry.h2s_ppm == 10.2


class TestCalibrationRecord:
    """Tests for CalibrationRecord model"""

    def test_create_calibration_record(self, db_session):
        """Test creating a calibration record"""
        calibration = CalibrationRecord(
            equipment_name="H2S Gas Analyzer",
            equipment_id="GA-001",
            calibration_date=datetime(2025, 11, 1),
            next_calibration_date=datetime(2026, 2, 1),
            calibration_authority="Calibration Lab Inc.",
            certificate_number="CERT-12345",
            status="current"
        )
        db_session.add(calibration)
        db_session.commit()

        assert calibration.id is not None
        assert calibration.equipment_name == "H2S Gas Analyzer"


class TestQualityEvent:
    """Tests for QualityEvent model"""

    def test_create_quality_event(self, db_session):
        """Test creating a quality event"""
        quality_event = QualityEvent(
            event_type="Non-conformance",
            severity="Major",
            description="Chamber temperature exceeded tolerance",
            status="Open",
            reported_by="Test Operator",
            reported_date=datetime.now()
        )
        db_session.add(quality_event)
        db_session.commit()

        assert quality_event.id is not None
        assert quality_event.event_type == "Non-conformance"

    def test_quality_event_with_execution(self, db_session):
        """Test quality event linked to execution"""
        protocol = Protocol(
            protocol_id="P37-54", code="H2S-001", name="Test",
            category="Environmental", version="1.0.0", status="active"
        )
        module = Module(
            module_id="TEST-001", manufacturer="Test", model="Model",
            technology="mono-Si", nameplate_power=400.0
        )
        db_session.add_all([protocol, module])
        db_session.commit()

        execution = TestExecution(
            execution_id="EXEC-001",
            protocol_id=protocol.id,
            module_id=module.id,
            test_date=datetime.now(),
            operator="Test Operator"
        )
        db_session.add(execution)
        db_session.commit()

        quality_event = QualityEvent(
            execution_id=execution.id,
            event_type="Equipment Failure",
            severity="Critical",
            description="IV curve tracer malfunction",
            status="Open",
            reported_by="Test Operator",
            reported_date=datetime.now()
        )
        db_session.add(quality_event)
        db_session.commit()

        assert quality_event.execution_id == execution.id
