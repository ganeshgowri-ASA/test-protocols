"""Integration tests for database operations."""

import pytest
from datetime import datetime
from src.database.models import Protocol, TestRun, Measurement


def test_create_protocol(db_manager):
    """Test creating a protocol in database."""
    protocol = Protocol(
        id="test-protocol-v1",
        name="Test Protocol",
        code="TEST-001",
        version="1.0.0",
        category="Safety",
        standard="IEC 61215",
        description="Test protocol for testing",
        definition={"protocol": {"id": "test-protocol-v1"}},
    )

    with db_manager.get_session() as session:
        session.add(protocol)
        session.commit()

        # Query back
        retrieved = session.query(Protocol).filter_by(id="test-protocol-v1").first()
        assert retrieved is not None
        assert retrieved.code == "TEST-001"


def test_create_test_run(db_manager):
    """Test creating a test run in database."""
    # First create protocol
    protocol = Protocol(
        id="test-protocol-v1",
        name="Test Protocol",
        code="TEST-001",
        version="1.0.0",
        definition={},
    )

    with db_manager.get_session() as session:
        session.add(protocol)
        session.commit()

    # Create test run
    test_run = TestRun(
        id="RUN-001",
        protocol_id="test-protocol-v1",
        sample_id="SAMPLE-001",
        operator_id="OP-001",
        status="initialized",
        parameters={"test_param": 50},
    )

    with db_manager.get_session() as session:
        session.add(test_run)
        session.commit()

        # Query back
        retrieved = session.query(TestRun).filter_by(id="RUN-001").first()
        assert retrieved is not None
        assert retrieved.sample_id == "SAMPLE-001"
        assert retrieved.parameters["test_param"] == 50


def test_create_measurement(db_manager):
    """Test creating measurements in database."""
    # Setup protocol and test run
    protocol = Protocol(
        id="test-protocol-v1", name="Test", code="TEST-001", version="1.0.0", definition={}
    )

    test_run = TestRun(
        id="RUN-001",
        protocol_id="test-protocol-v1",
        sample_id="SAMPLE-001",
        status="running",
    )

    with db_manager.get_session() as session:
        session.add(protocol)
        session.add(test_run)
        session.commit()

    # Create measurement
    measurement = Measurement(
        test_run_id="RUN-001",
        phase_id="p1_test",
        measurement_id="voltage",
        timestamp=datetime.now(),
        value=50.5,
        unit="V",
    )

    with db_manager.get_session() as session:
        session.add(measurement)
        session.commit()

        # Query back
        count = session.query(Measurement).count()
        assert count == 1


def test_relationship_protocol_test_runs(db_manager):
    """Test relationship between protocol and test runs."""
    protocol = Protocol(
        id="test-protocol-v1", name="Test", code="TEST-001", version="1.0.0", definition={}
    )

    test_run1 = TestRun(
        id="RUN-001", protocol_id="test-protocol-v1", sample_id="SAMPLE-001"
    )

    test_run2 = TestRun(
        id="RUN-002", protocol_id="test-protocol-v1", sample_id="SAMPLE-002"
    )

    with db_manager.get_session() as session:
        session.add(protocol)
        session.add(test_run1)
        session.add(test_run2)
        session.commit()

        # Query protocol and check test runs
        retrieved = session.query(Protocol).filter_by(id="test-protocol-v1").first()
        assert len(retrieved.test_runs) == 2
