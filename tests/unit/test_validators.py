"""Unit tests for validators."""

import pytest
from src.core.validators import ParameterValidator, MeasurementValidator


def test_validate_required_parameter():
    """Test validation of required parameters."""
    param_def = {
        "param_id": "test_id",
        "name": "Test Parameter",
        "type": "string",
        "required": True,
    }

    # Should fail with None value
    is_valid, error = ParameterValidator.validate(param_def, None)
    assert not is_valid
    assert "required" in error.lower()

    # Should pass with value
    is_valid, error = ParameterValidator.validate(param_def, "test_value")
    assert is_valid
    assert error == ""


def test_validate_float_type():
    """Test validation of float type."""
    param_def = {"param_id": "test", "name": "Test", "type": "float"}

    is_valid, _ = ParameterValidator.validate(param_def, 42.5)
    assert is_valid

    is_valid, _ = ParameterValidator.validate(param_def, 42)  # int accepted for float
    assert is_valid


def test_validate_integer_type():
    """Test validation of integer type."""
    param_def = {"param_id": "test", "name": "Test", "type": "integer"}

    is_valid, _ = ParameterValidator.validate(param_def, 42)
    assert is_valid


def test_validate_range():
    """Test validation of value ranges."""
    param_def = {
        "param_id": "test",
        "name": "Test",
        "type": "float",
        "min_value": 10,
        "max_value": 50,
    }

    # Within range
    is_valid, _ = ParameterValidator.validate(param_def, 25)
    assert is_valid

    # Below minimum
    is_valid, error = ParameterValidator.validate(param_def, 5)
    assert not is_valid
    assert "minimum" in error.lower()

    # Above maximum
    is_valid, error = ParameterValidator.validate(param_def, 100)
    assert not is_valid
    assert "maximum" in error.lower()


def test_validate_string_pattern():
    """Test validation of string patterns."""
    param_def = {
        "param_id": "test",
        "name": "Test",
        "type": "string",
        "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{8}$"},
    }

    # Valid pattern
    is_valid, _ = ParameterValidator.validate(param_def, "ABC12345")
    assert is_valid

    # Invalid pattern
    is_valid, error = ParameterValidator.validate(param_def, "invalid")
    assert not is_valid
    assert "format" in error.lower()


def test_measurement_range_validation():
    """Test measurement range validation."""
    assert MeasurementValidator.validate_range(50, 0, 100) is True
    assert MeasurementValidator.validate_range(150, 0, 100) is False
    assert MeasurementValidator.validate_range(-10, 0, 100) is False


def test_outlier_detection_iqr():
    """Test IQR outlier detection."""
    values = [10, 12, 13, 14, 15, 16, 17, 18, 19, 100]  # 100 is outlier

    outliers = MeasurementValidator.detect_outliers(values, method="iqr", threshold=1.5)
    assert len(outliers) > 0
    assert 9 in outliers  # Index of outlier value


def test_outlier_detection_zscore():
    """Test Z-score outlier detection."""
    values = [10, 12, 13, 14, 15, 16, 17, 18, 19, 100]  # 100 is outlier

    outliers = MeasurementValidator.detect_outliers(
        values, method="zscore", threshold=2.0
    )
    assert len(outliers) > 0


def test_qc_rule_range():
    """Test QC rule validation for range."""
    rule = {
        "rule_id": "test_rule",
        "type": "range",
        "min_value": 10,
        "max_value": 50,
        "action": "flag_error",
        "description": "Value out of range",
    }

    # Within range
    passes, msg = MeasurementValidator.validate_qc_rule(rule, 30)
    assert passes

    # Out of range
    passes, msg = MeasurementValidator.validate_qc_rule(rule, 100)
    assert not passes
    assert "range" in msg.lower()
