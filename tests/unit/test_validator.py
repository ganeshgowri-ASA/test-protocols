"""Unit tests for protocol validator."""

import pytest
from protocol_engine import ProtocolValidator


def test_validator_initialization(protocol_schema):
    """Test validator initialization."""
    validator = ProtocolValidator(protocol_schema)
    assert validator.schema is not None


def test_validate_valid_protocol(protocol_schema, sample_protocol_data):
    """Test validation of valid protocol."""
    validator = ProtocolValidator(protocol_schema)

    is_valid, errors = validator.validate(sample_protocol_data)

    assert is_valid
    assert len(errors) == 0


def test_validate_invalid_protocol_missing_required(protocol_schema):
    """Test validation of protocol with missing required fields."""
    validator = ProtocolValidator(protocol_schema)

    invalid_data = {
        "protocol_info": {
            "protocol_id": "IAM-001"
            # Missing required fields
        }
    }

    is_valid, errors = validator.validate(invalid_data)

    assert not is_valid
    assert len(errors) > 0


def test_validate_measurements(protocol_config, sample_measurements):
    """Test measurement validation."""
    from protocol_engine.loader import ProtocolLoader

    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")
    validator = ProtocolValidator(schema)

    is_valid, errors = validator.validate_measurements(sample_measurements, protocol_config)

    assert is_valid
    assert len(errors) == 0


def test_validate_insufficient_measurements(protocol_config):
    """Test validation with insufficient measurements."""
    from protocol_engine.loader import ProtocolLoader

    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")
    validator = ProtocolValidator(schema)

    # Only 2 measurements (minimum is 5)
    measurements = [
        {"angle": 0, "isc": 10, "voc": 48, "pmax": 400},
        {"angle": 45, "isc": 7, "voc": 47, "pmax": 280}
    ]

    is_valid, errors = validator.validate_measurements(measurements, protocol_config)

    assert not is_valid
    assert any("Insufficient data points" in error for error in errors)


def test_validate_negative_values(protocol_config):
    """Test validation with negative values."""
    from protocol_engine.loader import ProtocolLoader

    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")
    validator = ProtocolValidator(schema)

    measurements = [
        {"angle": 0, "isc": 10, "voc": 48, "pmax": 400},
        {"angle": 10, "isc": 9, "voc": 47, "pmax": 380},
        {"angle": 20, "isc": -5, "voc": 46, "pmax": 350},  # Negative Isc
        {"angle": 30, "isc": 7, "voc": 45, "pmax": 300},
        {"angle": 40, "isc": 6, "voc": 44, "pmax": 250},
    ]

    is_valid, errors = validator.validate_measurements(measurements, protocol_config)

    assert not is_valid
    assert any("Negative Isc" in error for error in errors)


def test_validate_irradiance_stability(protocol_config, sample_measurements):
    """Test irradiance stability validation."""
    from protocol_engine.loader import ProtocolLoader

    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")
    validator = ProtocolValidator(schema)

    is_stable, warnings = validator.validate_irradiance_stability(sample_measurements, protocol_config)

    assert is_stable
    assert len(warnings) == 0


def test_validate_all(protocol_schema, protocol_config, sample_protocol_data):
    """Test comprehensive validation."""
    validator = ProtocolValidator(protocol_schema)

    results = validator.validate_all(sample_protocol_data, protocol_config)

    assert results["schema_valid"]
    assert results["measurements_valid"]
    assert results["overall_status"] in ["pass", "pass_with_warnings"]


def test_validate_strict_success(protocol_schema, sample_protocol_data):
    """Test strict validation with valid data."""
    validator = ProtocolValidator(protocol_schema)

    # Should not raise exception
    validator.validate_strict(sample_protocol_data)


def test_validate_strict_failure(protocol_schema):
    """Test strict validation with invalid data."""
    validator = ProtocolValidator(protocol_schema)

    invalid_data = {"invalid": "data"}

    with pytest.raises(Exception):  # ValidationError
        validator.validate_strict(invalid_data)


def test_validate_angle_range(protocol_config):
    """Test validation of angle range."""
    from protocol_engine.loader import ProtocolLoader

    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")
    validator = ProtocolValidator(schema)

    # Angle beyond maximum
    measurements = [
        {"angle": 0, "isc": 10, "voc": 48, "pmax": 400},
        {"angle": 30, "isc": 8, "voc": 47, "pmax": 350},
        {"angle": 60, "isc": 6, "voc": 46, "pmax": 280},
        {"angle": 95, "isc": 1, "voc": 45, "pmax": 50},  # Beyond 90°
        {"angle": 90, "isc": 2, "voc": 44, "pmax": 100},
    ]

    is_valid, errors = validator.validate_measurements(measurements, protocol_config)

    assert not is_valid
    assert any("above maximum" in error for error in errors)
