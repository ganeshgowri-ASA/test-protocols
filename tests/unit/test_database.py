"""Tests for database models."""

import pytest
from datetime import datetime

from src.test_protocols.models import (
    init_database,
    get_session,
    Protocol,
    TestSession,
    Measurement,
    Report,
)


class TestDatabaseModels:
    """Test suite for database models."""

    @pytest.fixture(autouse=True)
    def setup_database(self, temp_database):
        """Setup test database before each test."""
        init_database(temp_database)

    def test_protocol_creation(self, protocol_config):
        """Test creating a protocol record."""
        with get_session() as session:
            protocol = Protocol.from_config(protocol_config)

            session.add(protocol)
            session.commit()

            assert protocol.id is not None
            assert protocol.protocol_id == "TEST-001"
            assert protocol.version == "1.0.0"
            assert protocol.name == "Test Protocol"
            assert protocol.category == "performance"

    def test_protocol_to_dict(self, protocol_config):
        """Test converting protocol to dictionary."""
        protocol = Protocol.from_config(protocol_config)

        protocol_dict = protocol.to_dict()

        assert isinstance(protocol_dict, dict)
        assert protocol_dict["protocol_id"] == "TEST-001"
        assert protocol_dict["version"] == "1.0.0"
        assert protocol_dict["name"] == "Test Protocol"

    def test_test_session_creation(self, protocol_config):
        """Test creating a test session record."""
        with get_session() as session:
            # Create protocol first
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            # Create test session
            test_session = TestSession(
                session_id="TEST_SESSION_001",
                protocol_id=protocol.id,
                test_name="Test Session",
                operator="Test Operator",
                status="pending",
            )

            session.add(test_session)
            session.commit()

            assert test_session.id is not None
            assert test_session.session_id == "TEST_SESSION_001"
            assert test_session.protocol_id == protocol.id
            assert test_session.status == "pending"

    def test_test_session_status_update(self, protocol_config):
        """Test updating test session status."""
        with get_session() as session:
            # Create protocol
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            # Create test session
            test_session = TestSession(
                session_id="TEST_SESSION_002",
                protocol_id=protocol.id,
                status="pending",
            )

            session.add(test_session)
            session.commit()

            # Update status to running
            test_session.update_status("running")
            session.commit()

            assert test_session.status == "running"
            assert test_session.started_at is not None

            # Update status to completed
            test_session.update_status("completed")
            session.commit()

            assert test_session.status == "completed"
            assert test_session.completed_at is not None
            assert test_session.duration_seconds is not None
            assert test_session.duration_seconds >= 0

    def test_test_session_relationship(self, protocol_config):
        """Test relationship between protocol and test sessions."""
        with get_session() as session:
            # Create protocol
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            # Create multiple test sessions
            for i in range(3):
                test_session = TestSession(
                    session_id=f"TEST_SESSION_{i}",
                    protocol_id=protocol.id,
                    status="completed",
                )
                session.add(test_session)

            session.commit()

            # Query protocol and check sessions
            queried_protocol = session.query(Protocol).filter_by(protocol_id="TEST-001").first()

            assert queried_protocol is not None
            assert len(queried_protocol.test_sessions) == 3

    def test_measurement_creation(self, protocol_config):
        """Test creating measurement records."""
        with get_session() as session:
            # Create protocol and test session
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            test_session = TestSession(
                session_id="TEST_SESSION_003",
                protocol_id=protocol.id,
                status="running",
            )
            session.add(test_session)
            session.commit()

            # Create measurements
            measurement = Measurement(
                session_id=test_session.id,
                timestamp=datetime.utcnow(),
                irradiance=1000,
                module_temp=25,
                voltage=35.5,
                current=8.5,
                power=301.75,
            )

            session.add(measurement)
            session.commit()

            assert measurement.id is not None
            assert measurement.session_id == test_session.id
            assert measurement.irradiance == 1000
            assert measurement.power == 301.75

    def test_measurement_from_dict(self, protocol_config):
        """Test creating measurement from dictionary."""
        with get_session() as session:
            # Create protocol and test session
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            test_session = TestSession(
                session_id="TEST_SESSION_004",
                protocol_id=protocol.id,
                status="running",
            )
            session.add(test_session)
            session.commit()

            # Create measurement from dict
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "irradiance": 800,
                "module_temp": 50,
                "voltage": 32.0,
                "current": 7.0,
            }

            measurement = Measurement.from_dict(data, test_session.id)
            session.add(measurement)
            session.commit()

            assert measurement.id is not None
            assert measurement.power is not None  # Should be calculated
            assert measurement.power == 32.0 * 7.0

    def test_report_creation(self, protocol_config):
        """Test creating report records."""
        with get_session() as session:
            # Create protocol and test session
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            test_session = TestSession(
                session_id="TEST_SESSION_005",
                protocol_id=protocol.id,
                status="completed",
            )
            session.add(test_session)
            session.commit()

            # Create report
            report = Report.from_session(
                session_id=test_session.id,
                report_type="html",
                content="<html><body>Test Report</body></html>",
                title="Test Report",
            )

            session.add(report)
            session.commit()

            assert report.id is not None
            assert report.session_id == test_session.id
            assert report.report_type == "html"
            assert report.content is not None

    def test_cascade_delete(self, protocol_config):
        """Test that deleting protocol cascades to sessions."""
        with get_session() as session:
            # Create protocol with sessions
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            test_session = TestSession(
                session_id="TEST_SESSION_006",
                protocol_id=protocol.id,
                status="completed",
            )
            session.add(test_session)
            session.commit()

            protocol_id = protocol.id
            session_id = test_session.id

            # Delete protocol
            session.delete(protocol)
            session.commit()

            # Check that session was also deleted
            deleted_session = session.query(TestSession).filter_by(id=session_id).first()
            assert deleted_session is None

    def test_query_sessions_by_status(self, protocol_config):
        """Test querying sessions by status."""
        with get_session() as session:
            # Create protocol
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            # Create sessions with different statuses
            statuses = ["pending", "running", "completed", "failed"]

            for status in statuses:
                test_session = TestSession(
                    session_id=f"TEST_{status.upper()}",
                    protocol_id=protocol.id,
                    status=status,
                )
                session.add(test_session)

            session.commit()

            # Query completed sessions
            completed_sessions = (
                session.query(TestSession).filter_by(status="completed").all()
            )

            assert len(completed_sessions) == 1
            assert completed_sessions[0].status == "completed"

    def test_test_session_summary(self, protocol_config):
        """Test getting test session summary."""
        with get_session() as session:
            # Create protocol
            protocol = Protocol.from_config(protocol_config)
            session.add(protocol)
            session.commit()

            # Create test session with results
            test_session = TestSession(
                session_id="TEST_SESSION_SUMMARY",
                protocol_id=protocol.id,
                status="completed",
                results={
                    "analysis": {"energy_rating": {"value": 1500}},
                    "qc_results": [
                        {"passed": True},
                        {"passed": True},
                        {"passed": False, "severity": "warning"},
                    ],
                },
            )
            session.add(test_session)
            session.commit()

            # Get summary
            summary = test_session.get_summary()

            assert summary is not None
            assert "session_id" in summary
            assert "protocol" in summary
            assert "status" in summary
            assert "qc_summary" in summary

            qc_summary = summary["qc_summary"]
            assert qc_summary["total_checks"] == 3
            assert qc_summary["passed"] == 2
