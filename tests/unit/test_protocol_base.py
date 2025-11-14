"""
Unit tests for base protocol classes
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.protocols.base import Protocol, ProtocolExecutor, ProtocolValidator


class TestProtocol:
    """Test Protocol class"""

    @pytest.fixture
    def sample_protocol_data(self):
        """Sample protocol data for testing"""
        return {
            "protocol_id": "TEST-001",
            "protocol_name": "Test Protocol",
            "version": "1.0.0",
            "standard": "TEST-STANDARD",
            "category": "Performance",
            "description": "Test protocol for unit testing",
            "equipment_required": [
                {
                    "id": "test_equipment",
                    "name": "Test Equipment",
                    "type": "measurement",
                    "required": True
                }
            ],
            "test_parameters": {
                "param1": {
                    "type": "number",
                    "label": "Parameter 1",
                    "min": 0,
                    "max": 100,
                    "default": 50,
                    "required": True
                },
                "param2": {
                    "type": "string",
                    "label": "Parameter 2",
                    "required": False
                }
            },
            "procedure": [
                {
                    "step": 1,
                    "action": "initialize",
                    "description": "Initialize test"
                }
            ],
            "data_outputs": {
                "result1": {
                    "type": "number",
                    "unit": "V"
                }
            },
            "qc_criteria": {
                "check1": {
                    "threshold": 10,
                    "unit": "V"
                }
            }
        }

    @pytest.fixture
    def protocol_file(self, sample_protocol_data):
        """Create temporary protocol file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_protocol_data, f)
            return f.name

    def test_protocol_loading(self, protocol_file):
        """Test protocol loading from file"""
        protocol = Protocol(protocol_file)
        assert protocol.protocol_id == "TEST-001"
        assert protocol.protocol_name == "Test Protocol"
        assert protocol.version == "1.0.0"
        assert protocol.standard == "TEST-STANDARD"

    def test_protocol_get_parameter(self, protocol_file):
        """Test getting parameter definition"""
        protocol = Protocol(protocol_file)
        param = protocol.get_parameter("param1")
        assert param is not None
        assert param["type"] == "number"
        assert param["min"] == 0
        assert param["max"] == 100

    def test_protocol_get_equipment(self, protocol_file):
        """Test getting equipment list"""
        protocol = Protocol(protocol_file)
        equipment = protocol.get_equipment()
        assert len(equipment) == 1
        assert equipment[0]["id"] == "test_equipment"

    def test_protocol_get_procedure(self, protocol_file):
        """Test getting procedure steps"""
        protocol = Protocol(protocol_file)
        procedure = protocol.get_procedure()
        assert len(procedure) == 1
        assert procedure[0]["step"] == 1
        assert procedure[0]["action"] == "initialize"

    def test_protocol_validate_parameters_valid(self, protocol_file):
        """Test parameter validation with valid parameters"""
        protocol = Protocol(protocol_file)
        params = {"param1": 50}
        is_valid, errors = protocol.validate_parameters(params)
        assert is_valid
        assert len(errors) == 0

    def test_protocol_validate_parameters_missing_required(self, protocol_file):
        """Test parameter validation with missing required parameter"""
        protocol = Protocol(protocol_file)
        params = {}
        is_valid, errors = protocol.validate_parameters(params)
        assert not is_valid
        assert len(errors) > 0
        assert "param1" in errors[0]

    def test_protocol_validate_parameters_out_of_range(self, protocol_file):
        """Test parameter validation with out-of-range value"""
        protocol = Protocol(protocol_file)
        params = {"param1": 150}  # exceeds max of 100
        is_valid, errors = protocol.validate_parameters(params)
        assert not is_valid
        assert any("above maximum" in err for err in errors)

    def test_protocol_invalid_file(self):
        """Test loading invalid protocol file"""
        with pytest.raises(FileNotFoundError):
            Protocol("nonexistent_file.json")


class TestProtocolValidator:
    """Test ProtocolValidator class"""

    @pytest.fixture
    def schema_file(self):
        """Create temporary schema file"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["protocol_id", "protocol_name", "version"],
            "properties": {
                "protocol_id": {"type": "string"},
                "protocol_name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema, f)
            return f.name

    def test_validator_valid_protocol(self, schema_file):
        """Test validation of valid protocol"""
        validator = ProtocolValidator(schema_file)

        valid_protocol = {
            "protocol_id": "TEST-001",
            "protocol_name": "Test",
            "version": "1.0.0"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_protocol, f)
            f.flush()

            is_valid, errors = validator.validate(f.name)
            assert is_valid
            assert len(errors) == 0

    def test_validator_invalid_protocol(self, schema_file):
        """Test validation of invalid protocol"""
        validator = ProtocolValidator(schema_file)

        invalid_protocol = {
            "protocol_id": "TEST-001"
            # missing required fields
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_protocol, f)
            f.flush()

            is_valid, errors = validator.validate(f.name)
            assert not is_valid
            assert len(errors) > 0


class TestProtocolExecutor:
    """Test ProtocolExecutor base class"""

    class MockExecutor(ProtocolExecutor):
        """Mock executor for testing"""

        def run(self):
            return {"mock_result": 42}

        def analyze(self):
            return {"mock_analysis": "complete"}

    @pytest.fixture
    def protocol_file(self):
        """Create minimal protocol file"""
        protocol_data = {
            "protocol_id": "TEST-001",
            "protocol_name": "Test Protocol",
            "version": "1.0.0",
            "standard": "TEST",
            "category": "Test",
            "description": "Test",
            "equipment_required": [],
            "test_parameters": {
                "param1": {
                    "type": "number",
                    "min": 0,
                    "max": 100,
                    "required": True
                }
            },
            "procedure": [],
            "data_outputs": {},
            "qc_criteria": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(protocol_data, f)
            return f.name

    def test_executor_initialization(self, protocol_file):
        """Test executor initialization"""
        protocol = Protocol(protocol_file)
        executor = self.MockExecutor(protocol)

        assert executor.protocol == protocol
        assert executor.status == "initialized"
        assert executor.test_id is None

    def test_executor_initialize_test(self, protocol_file):
        """Test test initialization"""
        protocol = Protocol(protocol_file)
        executor = self.MockExecutor(protocol)

        test_params = {"param1": 50}
        sample_info = {"sample_id": "SAMPLE-001"}

        test_id = executor.initialize(test_params, sample_info)

        assert test_id is not None
        assert "TEST-001" in test_id
        assert "SAMPLE-001" in test_id
        assert executor.status == "initialized"

    def test_executor_invalid_parameters(self, protocol_file):
        """Test initialization with invalid parameters"""
        protocol = Protocol(protocol_file)
        executor = self.MockExecutor(protocol)

        test_params = {}  # missing required param1
        sample_info = {"sample_id": "SAMPLE-001"}

        with pytest.raises(ValueError):
            executor.initialize(test_params, sample_info)

    def test_executor_run(self, protocol_file):
        """Test running executor"""
        protocol = Protocol(protocol_file)
        executor = self.MockExecutor(protocol)

        test_params = {"param1": 50}
        sample_info = {"sample_id": "SAMPLE-001"}
        executor.initialize(test_params, sample_info)

        results = executor.run()
        assert results["mock_result"] == 42

    def test_executor_complete(self, protocol_file):
        """Test completing test"""
        protocol = Protocol(protocol_file)
        executor = self.MockExecutor(protocol)

        test_params = {"param1": 50}
        sample_info = {"sample_id": "SAMPLE-001"}
        executor.initialize(test_params, sample_info)

        executor.complete()
        assert executor.status == "completed"
        assert executor.end_time is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
