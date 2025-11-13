"""Integration tests for database models."""

import pytest
from datetime import datetime
from src.models.protocol import (
    Protocol,
    TestExecution,
    Measurement,
    QCCheck,
    LeakageEvent,
    ProtocolStatus,
    TestExecutionStatus,
    QCStatus
)


class TestDatabaseModels:
    """Test database model operations."""

    def test_create_protocol(self, db_session, pid001_schema):
        """Test creating protocol in database."""
        protocol = Protocol(
            pid="pid-test-001",
            name="Test Protocol",
            version="1.0.0",
            standard="IEC 12345",
            description="Test description",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )

        db_session.add(protocol)
        db_session.commit()
        db_session.refresh(protocol)

        assert protocol.id is not None
        assert protocol.pid == "pid-test-001"
        assert protocol.created_at is not None

    def test_create_test_execution(self, db_session, pid001_schema):
        """Test creating test execution."""
        # Create protocol first
        protocol = Protocol(
            pid="pid-test-002",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        # Create test execution
        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-001",
            module_id="MOD-001",
            input_parameters={"test_voltage": -1000},
            status=TestExecutionStatus.PENDING,
            operator="Test User"
        )

        db_session.add(test_exec)
        db_session.commit()
        db_session.refresh(test_exec)

        assert test_exec.id is not None
        assert test_exec.protocol_id == protocol.id
        assert test_exec.status == TestExecutionStatus.PENDING

    def test_create_measurement(self, db_session, pid001_schema):
        """Test creating measurement."""
        # Create protocol and test execution
        protocol = Protocol(
            pid="pid-test-003",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-002",
            module_id="MOD-002",
            input_parameters={},
            status=TestExecutionStatus.IN_PROGRESS
        )
        db_session.add(test_exec)
        db_session.commit()

        # Create measurement
        measurement = Measurement(
            test_execution_id=test_exec.id,
            timestamp=datetime.utcnow(),
            elapsed_time=5.0,
            leakage_current=2.5,
            voltage=-1000,
            temperature=85.0,
            humidity=85.0,
            power_degradation=0.5
        )

        db_session.add(measurement)
        db_session.commit()
        db_session.refresh(measurement)

        assert measurement.id is not None
        assert measurement.leakage_current == 2.5

    def test_relationship_protocol_test_execution(self, db_session, pid001_schema):
        """Test relationship between protocol and test execution."""
        protocol = Protocol(
            pid="pid-test-004",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec1 = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-003",
            module_id="MOD-003",
            input_parameters={},
            status=TestExecutionStatus.PENDING
        )
        test_exec2 = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-004",
            module_id="MOD-004",
            input_parameters={},
            status=TestExecutionStatus.PENDING
        )

        db_session.add_all([test_exec1, test_exec2])
        db_session.commit()

        # Query protocol and check executions
        db_protocol = db_session.query(Protocol).filter_by(pid="pid-test-004").first()
        assert len(db_protocol.test_executions) == 2

    def test_relationship_test_execution_measurements(self, db_session, pid001_schema):
        """Test relationship between test execution and measurements."""
        protocol = Protocol(
            pid="pid-test-005",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-005",
            module_id="MOD-005",
            input_parameters={},
            status=TestExecutionStatus.IN_PROGRESS
        )
        db_session.add(test_exec)
        db_session.commit()

        # Add multiple measurements
        for i in range(5):
            measurement = Measurement(
                test_execution_id=test_exec.id,
                timestamp=datetime.utcnow(),
                elapsed_time=float(i),
                leakage_current=2.0 + i * 0.1,
                voltage=-1000
            )
            db_session.add(measurement)

        db_session.commit()

        # Query and check
        db_test_exec = db_session.query(TestExecution).filter_by(test_name="TEST-005").first()
        assert len(db_test_exec.measurements) == 5

    def test_create_qc_check(self, db_session, pid001_schema):
        """Test creating QC check."""
        protocol = Protocol(
            pid="pid-test-006",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-006",
            module_id="MOD-006",
            input_parameters={},
            status=TestExecutionStatus.COMPLETED
        )
        db_session.add(test_exec)
        db_session.commit()

        qc_check = QCCheck(
            test_execution_id=test_exec.id,
            check_name="Leakage Current Check",
            check_type="leakage_current",
            status=QCStatus.PASS,
            measured_value=2.5,
            threshold_value=10.0,
            message="Check passed"
        )

        db_session.add(qc_check)
        db_session.commit()
        db_session.refresh(qc_check)

        assert qc_check.id is not None
        assert qc_check.status == QCStatus.PASS

    def test_create_leakage_event(self, db_session, pid001_schema):
        """Test creating leakage event."""
        protocol = Protocol(
            pid="pid-test-007",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-007",
            module_id="MOD-007",
            input_parameters={},
            status=TestExecutionStatus.IN_PROGRESS
        )
        db_session.add(test_exec)
        db_session.commit()

        event = LeakageEvent(
            test_execution_id=test_exec.id,
            event_type="critical_threshold",
            severity="critical",
            timestamp=datetime.utcnow(),
            leakage_current=15.0,
            threshold_exceeded=10.0,
            description="Critical threshold exceeded"
        )

        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)

        assert event.id is not None
        assert event.severity == "critical"

    def test_cascade_delete(self, db_session, pid001_schema):
        """Test cascade delete from protocol to test executions."""
        protocol = Protocol(
            pid="pid-test-008",
            name="Test Protocol",
            version="1.0.0",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()

        test_exec = TestExecution(
            protocol_id=protocol.id,
            test_name="TEST-008",
            module_id="MOD-008",
            input_parameters={},
            status=TestExecutionStatus.PENDING
        )
        db_session.add(test_exec)
        db_session.commit()

        protocol_id = protocol.id
        test_exec_id = test_exec.id

        # Delete protocol
        db_session.delete(protocol)
        db_session.commit()

        # Check that test execution is also deleted
        deleted_test_exec = db_session.query(TestExecution).filter_by(id=test_exec_id).first()
        assert deleted_test_exec is None
