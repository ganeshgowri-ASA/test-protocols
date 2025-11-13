"""Integration tests for protocol engine."""

import pytest
from src.core.protocol_engine import ProtocolEngine
from src.models.protocol import Protocol, ProtocolStatus, TestExecutionStatus
from src.models.database import get_db


class TestProtocolEngine:
    """Test ProtocolEngine integration."""

    @pytest.fixture
    def engine(self):
        """Create protocol engine instance."""
        return ProtocolEngine()

    @pytest.fixture
    def sample_protocol(self, db_session, pid001_schema):
        """Create sample protocol in database."""
        protocol = Protocol(
            pid="pid-001",
            name="PID Shunting Test Protocol",
            version="1.0.0",
            standard="IEC 62804",
            description="Test protocol",
            schema=pid001_schema,
            status=ProtocolStatus.ACTIVE
        )
        db_session.add(protocol)
        db_session.commit()
        db_session.refresh(protocol)
        return protocol

    def test_load_protocol_schema(self, engine):
        """Test loading protocol schema from filesystem."""
        schema = engine.load_protocol_schema("pid-001")
        assert isinstance(schema, dict)
        assert "metadata" in schema
        assert schema["metadata"]["pid"] == "pid-001"

    def test_load_protocol_schema_not_found(self, engine):
        """Test loading non-existent protocol."""
        with pytest.raises(FileNotFoundError):
            engine.load_protocol_schema("pid-999")

    def test_load_protocol_implementation(self, engine):
        """Test loading protocol implementation module."""
        module = engine.load_protocol_implementation("pid-001")
        assert hasattr(module, "PID001Protocol")
        assert hasattr(module, "LeakageTracker")

    def test_load_protocol_implementation_not_found(self, engine):
        """Test loading non-existent implementation."""
        with pytest.raises(ImportError):
            engine.load_protocol_implementation("pid-999")

    def test_get_protocol_from_db(self, engine, sample_protocol):
        """Test retrieving protocol from database."""
        protocol = engine.get_protocol_from_db("pid-001")
        assert protocol is not None
        assert protocol.pid == "pid-001"
        assert protocol.name == sample_protocol.name

    def test_get_protocol_from_db_not_found(self, engine):
        """Test retrieving non-existent protocol."""
        protocol = engine.get_protocol_from_db("pid-999")
        assert protocol is None

    def test_create_test_execution(self, engine, sample_protocol, sample_test_parameters):
        """Test creating test execution."""
        test_exec = engine.create_test_execution("pid-001", sample_test_parameters)
        assert test_exec is not None
        assert test_exec.test_name == sample_test_parameters["test_name"]
        assert test_exec.module_id == sample_test_parameters["module_id"]
        assert test_exec.status == TestExecutionStatus.PENDING

    def test_create_test_execution_invalid_parameters(self, engine, sample_protocol):
        """Test creating test execution with invalid parameters."""
        invalid_params = {"test_name": "TEST-001"}  # Missing required fields
        with pytest.raises(ValueError):
            engine.create_test_execution("pid-001", invalid_params)

    def test_update_test_execution_status(self, engine, sample_protocol, sample_test_parameters):
        """Test updating test execution status."""
        # Create test execution
        test_exec = engine.create_test_execution("pid-001", sample_test_parameters)
        test_id = test_exec.id

        # Update status
        from datetime import datetime
        updated = engine.update_test_execution_status(
            test_id,
            TestExecutionStatus.IN_PROGRESS,
            start_time=datetime.utcnow()
        )

        assert updated.status == TestExecutionStatus.IN_PROGRESS
        assert updated.start_time is not None

    def test_get_all_protocols(self, engine, sample_protocol):
        """Test getting all protocols."""
        protocols = engine.get_all_protocols()
        assert len(protocols) >= 1
        assert any(p.pid == "pid-001" for p in protocols)

    def test_get_protocol_metadata(self, engine, sample_protocol):
        """Test getting protocol metadata."""
        metadata = engine.get_protocol_metadata("pid-001")
        assert metadata["pid"] == "pid-001"
        assert metadata["name"] == sample_protocol.name
        assert metadata["version"] == sample_protocol.version
        assert "metadata" in metadata
