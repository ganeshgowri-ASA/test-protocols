"""
Unit tests for protocol handler.
"""
import pytest
from pathlib import Path
from protocols.handler import ProtocolHandler
from protocols.models import Protocol, ProtocolStatus


@pytest.mark.unit
class TestProtocolHandler:
    """Test ProtocolHandler."""

    def test_load_protocol(self, sample_protocol_data):
        """Test loading protocol from dictionary."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol(sample_protocol_data)

        assert isinstance(protocol, Protocol)
        assert protocol.protocol_id == sample_protocol_data["protocol_id"]
        assert handler.current_protocol == protocol

    def test_load_invalid_protocol(self):
        """Test loading invalid protocol data."""
        handler = ProtocolHandler()
        invalid_data = {"invalid": "data"}

        with pytest.raises(ValueError):
            handler.load_protocol(invalid_data)

    def test_load_protocol_from_file(self, temp_protocol_file):
        """Test loading protocol from JSON file."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol_from_file(temp_protocol_file)

        assert isinstance(protocol, Protocol)
        assert protocol.protocol_id == "TEST-001"

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        handler = ProtocolHandler()

        with pytest.raises(FileNotFoundError):
            handler.load_protocol_from_file(Path("/nonexistent/file.json"))

    def test_execute_protocol(self, sample_protocol_data):
        """Test protocol execution."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol(sample_protocol_data)
        result = handler.execute_protocol(protocol)

        assert result.protocol_id == protocol.protocol_id
        assert result.status in ["completed", "failed"]
        assert result.execution_time is not None

    def test_execute_protocol_without_loading(self):
        """Test execution without loading protocol."""
        handler = ProtocolHandler()

        with pytest.raises(ValueError, match="No protocol loaded"):
            handler.execute_protocol()

    def test_execute_protocol_validation_failure(self):
        """Test execution with validation failure."""
        handler = ProtocolHandler()
        invalid_protocol = handler.load_protocol({
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "protocol_type": "electrical",
            "version": "1.0",
            "parameters": {"module_id": ""},  # Empty module_id
        })

        result = handler.execute_protocol(invalid_protocol)

        assert result.passed is False
        assert len(result.errors) > 0

    def test_get_result_history(self, sample_protocol_data):
        """Test getting result history."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol(sample_protocol_data)

        # Execute multiple times
        handler.execute_protocol(protocol)
        handler.execute_protocol(protocol)

        history = handler.get_result_history()

        assert len(history) == 2

    def test_save_result(self, sample_protocol_data, tmp_path):
        """Test saving protocol result."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol(sample_protocol_data)
        result = handler.execute_protocol(protocol)

        output_dir = tmp_path / "results"
        handler.save_result(result, output_dir)

        # Check that file was created
        files = list(output_dir.glob("*.json"))
        assert len(files) == 1
        assert result.protocol_id in files[0].name


@pytest.mark.unit
class TestProtocolValidation:
    """Test protocol validation logic."""

    def test_validate_protocol_with_empty_parameters(self):
        """Test validation rejects empty parameters."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol({
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "protocol_type": "electrical",
            "version": "1.0",
            "parameters": {},
        })

        errors = handler._validate_protocol(protocol)

        assert len(errors) > 0
        assert any("empty" in error.lower() for error in errors)

    def test_validate_protocol_missing_module_id(self):
        """Test validation catches missing module_id."""
        handler = ProtocolHandler()
        protocol = handler.load_protocol({
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "protocol_type": "electrical",
            "version": "1.0",
            "parameters": {"module_id": ""},
        })

        errors = handler._validate_protocol(protocol)

        assert len(errors) > 0
