"""Tests for database models and operations."""

import pytest
from datetime import datetime, timedelta

from src.database.models import (
    Protocol,
    TestExecution,
    TestStep,
    Measurement,
    QCCheck,
    Equipment,
)
from src.database.connection import get_session, init_db


class TestDatabaseModels:
    """Tests for database models."""

    def test_create_protocol(self, test_db):
        """Test creating a protocol record."""
        with get_session() as session:
            protocol = Protocol(
                protocol_id="TEST-001",
                version="1.0",
                title="Test Protocol",
                category="Test",
                description="A test protocol",
                test_steps=[],
            )
            session.add(protocol)
            session.commit()

            # Query back
            saved = session.query(Protocol).filter_by(protocol_id="TEST-001").first()
            assert saved is not None
            assert saved.title == "Test Protocol"
            assert saved.is_active

    def test_create_test_execution(self, test_db):
        """Test creating a test execution record."""
        with get_session() as session:
            # Create protocol first
            protocol = Protocol(
                protocol_id="TEST-001",
                version="1.0",
                title="Test Protocol",
                category="Test",
            )
            session.add(protocol)
            session.flush()

            # Create test execution
            test_exec = TestExecution(
                test_id="EXEC-001",
                protocol_id=protocol.id,
                module_serial_number="MOD-001",
                operator="Test Operator",
                start_time=datetime.now(),
                status="In Progress",
            )
            session.add(test_exec)
            session.commit()

            # Query back
            saved = session.query(TestExecution).filter_by(test_id="EXEC-001").first()
            assert saved is not None
            assert saved.module_serial_number == "MOD-001"
            assert saved.protocol.protocol_id == "TEST-001"

    def test_create_test_step(self, test_db):
        """Test creating test step records."""
        with get_session() as session:
            # Create protocol and test execution
            protocol = Protocol(
                protocol_id="TEST-001",
                version="1.0",
                title="Test Protocol",
                category="Test",
            )
            session.add(protocol)
            session.flush()

            test_exec = TestExecution(
                test_id="EXEC-001",
                protocol_id=protocol.id,
                module_serial_number="MOD-001",
                operator="Test Operator",
                start_time=datetime.now(),
            )
            session.add(test_exec)
            session.flush()

            # Create test step
            step = TestStep(
                test_execution_id=test_exec.id,
                step_number=1,
                name="Step 1",
                description="First step",
                completed=True,
                passed=True,
                results={"value1": 50},
            )
            session.add(step)
            session.commit()

            # Query back
            saved = session.query(TestStep).first()
            assert saved is not None
            assert saved.step_number == 1
            assert saved.passed
            assert saved.results["value1"] == 50

    def test_create_measurement(self, test_db):
        """Test creating measurement records."""
        with get_session() as session:
            # Create protocol, test execution, and test step
            protocol = Protocol(
                protocol_id="TEST-001",
                version="1.0",
                title="Test Protocol",
                category="Test",
            )
            session.add(protocol)
            session.flush()

            test_exec = TestExecution(
                test_id="EXEC-001",
                protocol_id=protocol.id,
                module_serial_number="MOD-001",
                operator="Test Operator",
                start_time=datetime.now(),
            )
            session.add(test_exec)
            session.flush()

            step = TestStep(
                test_execution_id=test_exec.id,
                step_number=1,
                name="Step 1",
                description="First step",
            )
            session.add(step)
            session.flush()

            # Create measurements
            measurement1 = Measurement(
                test_step_id=step.id,
                measurement_name="resistance",
                measurement_type="number",
                value_numeric=45.5,
                unit="mΩ",
            )
            session.add(measurement1)

            measurement2 = Measurement(
                test_step_id=step.id,
                measurement_name="condition",
                measurement_type="text",
                value_text="Pass",
            )
            session.add(measurement2)

            measurement3 = Measurement(
                test_step_id=step.id,
                measurement_name="cable_pulled_out",
                measurement_type="boolean",
                value_boolean=False,
            )
            session.add(measurement3)

            session.commit()

            # Query back
            saved_measurements = session.query(Measurement).all()
            assert len(saved_measurements) == 3

            # Test get_value method
            assert saved_measurements[0].get_value() == 45.5
            assert saved_measurements[1].get_value() == "Pass"
            assert saved_measurements[2].get_value() is False

    def test_create_equipment(self, test_db):
        """Test creating equipment records."""
        with get_session() as session:
            equipment = Equipment(
                name="Digital Multimeter",
                equipment_type="Multimeter",
                manufacturer="Fluke",
                model="87V",
                serial_number="12345",
                calibration_required=True,
                calibration_date=datetime.now(),
                calibration_due_date=datetime.now() + timedelta(days=365),
                status="Active",
            )
            session.add(equipment)
            session.commit()

            # Query back
            saved = session.query(Equipment).filter_by(serial_number="12345").first()
            assert saved is not None
            assert saved.name == "Digital Multimeter"
            assert saved.is_calibration_valid

    def test_equipment_calibration_expired(self, test_db):
        """Test equipment with expired calibration."""
        with get_session() as session:
            equipment = Equipment(
                name="Expired Meter",
                serial_number="99999",
                calibration_required=True,
                calibration_date=datetime.now() - timedelta(days=400),
                calibration_due_date=datetime.now() - timedelta(days=30),
                status="Active",
            )
            session.add(equipment)
            session.commit()

            # Query back
            saved = session.query(Equipment).filter_by(serial_number="99999").first()
            assert saved is not None
            assert not saved.is_calibration_valid

    def test_relationship_cascade(self, test_db):
        """Test that relationships cascade correctly."""
        with get_session() as session:
            # Create protocol, test execution, and related records
            protocol = Protocol(
                protocol_id="TEST-001",
                version="1.0",
                title="Test Protocol",
                category="Test",
            )
            session.add(protocol)
            session.flush()

            test_exec = TestExecution(
                test_id="EXEC-001",
                protocol_id=protocol.id,
                module_serial_number="MOD-001",
                operator="Test Operator",
                start_time=datetime.now(),
            )
            session.add(test_exec)
            session.flush()

            step = TestStep(
                test_execution_id=test_exec.id,
                step_number=1,
                name="Step 1",
            )
            session.add(step)
            session.commit()

            # Verify relationships
            assert len(test_exec.test_steps) == 1
            assert test_exec.test_steps[0].step_number == 1
            assert test_exec.protocol.protocol_id == "TEST-001"

            # Delete test execution should cascade to steps
            session.delete(test_exec)
            session.commit()

            remaining_steps = session.query(TestStep).all()
            assert len(remaining_steps) == 0
