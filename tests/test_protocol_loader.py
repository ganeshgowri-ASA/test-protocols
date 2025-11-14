"""
Tests for protocol loader module.
"""

import pytest
from pathlib import Path
from test_protocols.core.protocol_loader import ProtocolLoader
from test_protocols.core.protocol import Protocol


class TestProtocolLoader:
    """Test suite for ProtocolLoader class."""

    def test_load_schema(self, schema_path):
        """Test loading JSON schema."""
        loader = ProtocolLoader(schema_path=schema_path)
        schema = loader.load_schema()

        assert schema is not None
        assert "$schema" in schema
        assert schema["title"] == "Test Protocol Schema"

    def test_validate_valid_protocol(self, ml_001_protocol_data, schema_path):
        """Test validation of valid protocol."""
        loader = ProtocolLoader(schema_path=schema_path)
        is_valid, error = loader.validate_json(ml_001_protocol_data)

        assert is_valid is True
        assert error is None

    def test_validate_invalid_protocol(self, schema_path):
        """Test validation of invalid protocol."""
        loader = ProtocolLoader(schema_path=schema_path)

        invalid_data = {
            "protocol_id": "INVALID",
            # Missing required fields
        }

        is_valid, error = loader.validate_json(invalid_data)

        assert is_valid is False
        assert error is not None

    def test_load_protocol_from_file(self, ml_001_protocol_path, schema_path):
        """Test loading protocol from file."""
        loader = ProtocolLoader(schema_path=schema_path)
        protocol = loader.load_protocol(ml_001_protocol_path)

        assert isinstance(protocol, Protocol)
        assert protocol.protocol_id == "ML-001"
        assert protocol.name == "Mechanical Load Static Test (2400Pa)"
        assert protocol.category == "mechanical"
        assert len(protocol.tests) == 9

    def test_load_protocol_from_string(self, ml_001_protocol_data, schema_path):
        """Test loading protocol from JSON string."""
        import json

        loader = ProtocolLoader(schema_path=schema_path)
        json_string = json.dumps(ml_001_protocol_data)
        protocol = loader.load_protocol_from_string(json_string)

        assert isinstance(protocol, Protocol)
        assert protocol.protocol_id == "ML-001"

    def test_load_nonexistent_file(self, schema_path):
        """Test loading nonexistent protocol file."""
        loader = ProtocolLoader(schema_path=schema_path)

        with pytest.raises(FileNotFoundError):
            loader.load_protocol("/nonexistent/protocol.json")

    def test_list_protocols(self, protocols_dir):
        """Test listing protocol files."""
        protocols = ProtocolLoader.list_protocols(protocols_dir)

        assert len(protocols) > 0
        assert any("ml_001_protocol.json" in str(p) for p in protocols)
