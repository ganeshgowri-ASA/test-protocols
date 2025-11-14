"""
Protocol Tests
Unit tests for protocol classes and functionality
"""

import pytest
from pathlib import Path
from protocols.base import BaseProtocol, TestParameter, ProtocolMetadata
from protocols.environmental.environmental import DesertClimateProtocol
from protocols.schema import ProtocolValidator


class TestProtocolMetadata:
    """Test ProtocolMetadata class"""

    def test_metadata_from_dict(self, desert_protocol_data):
        """Test creating metadata from dictionary"""
        metadata = ProtocolMetadata.from_dict(desert_protocol_data['metadata'])

        assert metadata.id == "DESERT-001"
        assert metadata.name == "Desert Climate Test"
        assert metadata.category == "Environmental"
        assert metadata.version == "1.0.0"

    def test_metadata_attributes(self, desert_protocol_data):
        """Test metadata attributes"""
        metadata = ProtocolMetadata.from_dict(desert_protocol_data['metadata'])

        assert hasattr(metadata, 'id')
        assert hasattr(metadata, 'name')
        assert hasattr(metadata, 'category')
        assert hasattr(metadata, 'version')
        assert hasattr(metadata, 'description')


class TestTestParameter:
    """Test TestParameter class"""

    def test_parameter_from_dict(self):
        """Test creating parameter from dictionary"""
        param_data = {
            "type": "number",
            "description": "Test temperature",
            "default": 25.0,
            "min": -40,
            "max": 85,
            "unit": "°C",
            "validation": "required",
            "tolerance": 2.0
        }

        param = TestParameter.from_dict("temperature", param_data)

        assert param.name == "temperature"
        assert param.type == "number"
        assert param.default == 25.0
        assert param.min_value == -40
        assert param.max_value == 85
        assert param.unit == "°C"

    def test_parameter_validation_required(self):
        """Test required parameter validation"""
        param = TestParameter(
            name="temp",
            type="number",
            description="Test",
            default=25,
            unit="°C",
            validation="required"
        )

        is_valid, error = param.validate(None)
        assert not is_valid
        assert "required" in error.lower()

    def test_parameter_validation_range(self):
        """Test parameter range validation"""
        param = TestParameter(
            name="temp",
            type="number",
            description="Test",
            default=25,
            unit="°C",
            min_value=0,
            max_value=100
        )

        is_valid, error = param.validate(50)
        assert is_valid

        is_valid, error = param.validate(150)
        assert not is_valid

        is_valid, error = param.validate(-10)
        assert not is_valid

    def test_parameter_validation_type(self):
        """Test parameter type validation"""
        param = TestParameter(
            name="count",
            type="integer",
            description="Test",
            default=10,
            unit=""
        )

        is_valid, error = param.validate(5)
        assert is_valid

        is_valid, error = param.validate("not a number")
        assert not is_valid


class TestDesertClimateProtocol:
    """Test DesertClimateProtocol class"""

    def test_protocol_initialization(self):
        """Test protocol initialization"""
        protocol = DesertClimateProtocol()

        assert protocol is not None
        assert protocol.metadata is not None
        assert protocol.metadata.id == "DESERT-001"

    def test_protocol_metadata(self):
        """Test protocol metadata"""
        protocol = DesertClimateProtocol()

        assert protocol.metadata.name == "Desert Climate Test"
        assert protocol.metadata.category == "Environmental"
        assert protocol.metadata.protocol_number == "P39/54"

    def test_protocol_parameters(self):
        """Test protocol parameters"""
        protocol = DesertClimateProtocol()

        assert "daytime_temperature" in protocol.parameters
        assert "nighttime_temperature" in protocol.parameters
        assert "daytime_humidity" in protocol.parameters
        assert "nighttime_humidity" in protocol.parameters
        assert "total_cycles" in protocol.parameters

    def test_parameter_defaults(self):
        """Test parameter default values"""
        protocol = DesertClimateProtocol()
        defaults = protocol.get_parameter_defaults()

        assert defaults["daytime_temperature"] == 65
        assert defaults["nighttime_temperature"] == 5
        assert defaults["daytime_humidity"] == 15
        assert defaults["nighttime_humidity"] == 40
        assert defaults["total_cycles"] == 200

    def test_parameter_validation(self, sample_parameters):
        """Test parameter validation"""
        protocol = DesertClimateProtocol()

        is_valid, errors = protocol.validate_parameters(sample_parameters)
        assert is_valid
        assert len(errors) == 0

    def test_parameter_validation_invalid(self):
        """Test parameter validation with invalid values"""
        protocol = DesertClimateProtocol()

        invalid_params = {
            "daytime_temperature": 100,  # Above max
            "nighttime_temperature": 5,
            "total_cycles": 10  # Below min
        }

        is_valid, errors = protocol.validate_parameters(invalid_params)
        assert not is_valid
        assert len(errors) > 0

    def test_test_procedure_structure(self):
        """Test test procedure structure"""
        protocol = DesertClimateProtocol()
        procedure = protocol.get_test_procedure()

        assert "preparation" in procedure
        assert "test_cycles" in procedure
        assert "interim_testing" in procedure
        assert "post_test" in procedure

    def test_qc_checks(self):
        """Test QC checks"""
        protocol = DesertClimateProtocol()
        qc_checks = protocol.get_qc_checks()

        assert len(qc_checks) > 0
        assert any(c['name'] == 'temperature_stability' for c in qc_checks)
        assert any(c['name'] == 'humidity_stability' for c in qc_checks)

    def test_data_collection(self):
        """Test data collection"""
        protocol = DesertClimateProtocol()

        data_point = {
            'chamber_temperature': 65.0,
            'chamber_humidity': 15.0,
            'module_temperature': 75.0
        }

        protocol.collect_data(data_point)

        assert len(protocol.data_storage) == 1
        assert protocol.data_storage[0]['chamber_temperature'] == 65.0


class TestProtocolValidator:
    """Test ProtocolValidator class"""

    def test_validate_protocol(self, desert_protocol_data):
        """Test protocol validation"""
        is_valid, errors = ProtocolValidator.validate(desert_protocol_data)

        assert is_valid
        assert errors is None

    def test_validate_invalid_protocol(self):
        """Test invalid protocol validation"""
        invalid_protocol = {
            "metadata": {
                "id": "TEST-001"
                # Missing required fields
            }
        }

        is_valid, errors = ProtocolValidator.validate(invalid_protocol)

        assert not is_valid
        assert errors is not None
        assert len(errors) > 0

    def test_validate_parameter_values(self, sample_parameters, desert_protocol_data):
        """Test parameter value validation"""
        is_valid, errors = ProtocolValidator.validate_parameter_values(
            sample_parameters,
            desert_protocol_data['test_parameters']
        )

        assert is_valid
        assert len(errors) == 0

    def test_validate_parameter_values_out_of_range(self, desert_protocol_data):
        """Test parameter validation with out-of-range values"""
        invalid_params = {
            "daytime_temperature": 100  # Above max
        }

        is_valid, errors = ProtocolValidator.validate_parameter_values(
            invalid_params,
            desert_protocol_data['test_parameters']
        )

        assert not is_valid
        assert len(errors) > 0


@pytest.mark.desert
class TestDesertProtocolExecution:
    """Test desert protocol execution"""

    def test_protocol_start(self):
        """Test protocol start"""
        protocol = DesertClimateProtocol()
        protocol.start()

        assert protocol.start_time is not None
        assert protocol.status.value == "running"

    def test_protocol_complete(self):
        """Test protocol completion"""
        protocol = DesertClimateProtocol()
        protocol.start()
        protocol.complete()

        assert protocol.end_time is not None
        assert protocol.status.value == "completed"

    def test_protocol_fail(self):
        """Test protocol failure"""
        protocol = DesertClimateProtocol()
        protocol.start()
        protocol.fail("Test failure")

        assert protocol.status.value == "failed"

    def test_protocol_abort(self):
        """Test protocol abort"""
        protocol = DesertClimateProtocol()
        protocol.start()
        protocol.abort("Test abort")

        assert protocol.status.value == "aborted"
