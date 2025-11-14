"""Unit tests for protocol validator."""

import pytest
from src.core.validator import ProtocolValidator


def test_validator_initialization():
    """Test validator initialization."""
    validator = ProtocolValidator()

    assert 'protocol' in validator.schemas
    assert len(validator.errors) == 0


def test_validate_valid_protocol():
    """Test validation of valid protocol."""
    validator = ProtocolValidator()

    protocol_data = {
        'protocol_id': 'TEST-001',
        'name': 'Test Protocol',
        'version': '1.0.0',
        'category': 'Performance',
        'test_parameters': {
            'duration': {'value': 1, 'unit': 'hours'}
        }
    }

    is_valid = validator.validate_protocol(protocol_data)
    assert is_valid is True
    assert len(validator.errors) == 0


def test_validate_invalid_protocol_id():
    """Test validation fails for invalid protocol ID format."""
    validator = ProtocolValidator()

    protocol_data = {
        'protocol_id': 'INVALID',  # Should be XXX-NNN format
        'name': 'Test Protocol',
        'version': '1.0.0',
        'category': 'Performance',
        'test_parameters': {}
    }

    is_valid = validator.validate_protocol(protocol_data)
    assert is_valid is False
    assert len(validator.errors) > 0


def test_validate_missing_required_field():
    """Test validation fails for missing required fields."""
    validator = ProtocolValidator()

    protocol_data = {
        'protocol_id': 'TEST-001',
        'name': 'Test Protocol',
        # Missing 'version' and other required fields
    }

    is_valid = validator.validate_protocol(protocol_data)
    assert is_valid is False
    assert len(validator.errors) > 0


def test_validate_invalid_category():
    """Test validation fails for invalid category."""
    validator = ProtocolValidator()

    protocol_data = {
        'protocol_id': 'TEST-001',
        'name': 'Test Protocol',
        'version': '1.0.0',
        'category': 'InvalidCategory',  # Not in enum
        'test_parameters': {}
    }

    is_valid = validator.validate_protocol(protocol_data)
    assert is_valid is False


def test_validate_test_data():
    """Test validation of test data against protocol."""
    validator = ProtocolValidator()

    protocol_config = {
        'test_parameters': {
            'metrics': [
                {'name': 'metric1', 'type': 'angle', 'unit': 'degrees'},
                {'name': 'metric2', 'type': 'power', 'unit': 'W'}
            ]
        }
    }

    test_data = {
        'metric1': 45.0,
        'metric2': 100.0
    }

    is_valid = validator.validate_test_data(test_data, protocol_config)
    assert is_valid is True


def test_validate_test_data_missing_metric():
    """Test validation fails when required metric is missing."""
    validator = ProtocolValidator()

    protocol_config = {
        'test_parameters': {
            'metrics': [
                {'name': 'metric1', 'type': 'angle', 'unit': 'degrees'},
                {'name': 'metric2', 'type': 'power', 'unit': 'W'}
            ]
        }
    }

    test_data = {
        'metric1': 45.0
        # Missing metric2
    }

    is_valid = validator.validate_test_data(test_data, protocol_config)
    assert is_valid is False
    assert len(validator.errors) > 0


def test_get_errors():
    """Test getting validation errors."""
    validator = ProtocolValidator()

    # Trigger validation error
    protocol_data = {'protocol_id': 'INVALID'}
    validator.validate_protocol(protocol_data)

    errors = validator.get_errors()
    assert isinstance(errors, list)
    assert len(errors) > 0
