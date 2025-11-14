"""Tests for protocol loader."""

import pytest
from pathlib import Path
import json

from src.core.protocol_loader import ProtocolLoader
from src.models.protocol import Protocol, TestCategory


@pytest.fixture
def protocol_loader():
    """Create protocol loader fixture."""
    return ProtocolLoader()


def test_list_protocols(protocol_loader):
    """Test listing available protocols."""
    protocols = protocol_loader.list_protocols()

    assert isinstance(protocols, list)
    assert len(protocols) > 0

    # Check VIBR-001 is in the list
    vibr001 = next((p for p in protocols if p['id'] == 'VIBR-001'), None)
    assert vibr001 is not None
    assert vibr001['name'] == 'Transportation Vibration Test'
    assert vibr001['category'] == 'mechanical'


def test_list_protocols_by_category(protocol_loader):
    """Test listing protocols filtered by category."""
    mechanical_protocols = protocol_loader.list_protocols(category='mechanical')

    assert isinstance(mechanical_protocols, list)
    assert all(p['category'] == 'mechanical' for p in mechanical_protocols)


def test_load_vibr001_protocol(protocol_loader):
    """Test loading VIBR-001 protocol."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    assert isinstance(protocol, Protocol)
    assert protocol.id == 'VIBR-001'
    assert protocol.name == 'Transportation Vibration Test'
    assert protocol.version == '1.0.0'
    assert protocol.standard == 'IEC 62759-1:2022'
    assert protocol.category == TestCategory.MECHANICAL
    assert protocol.test_type == 'vibration'


def test_load_nonexistent_protocol(protocol_loader):
    """Test loading non-existent protocol raises error."""
    with pytest.raises(FileNotFoundError):
        protocol_loader.load_protocol('NONEXIST-999')


def test_protocol_parameters(protocol_loader):
    """Test protocol parameters are loaded correctly."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    assert 'frequency_range' in protocol.parameters
    assert 'vibration_severity' in protocol.parameters
    assert 'test_duration' in protocol.parameters

    # Check parameter values
    freq_range = protocol.parameters['frequency_range']
    assert freq_range.min == 5
    assert freq_range.max == 200
    assert freq_range.unit == 'Hz'

    vibration_severity = protocol.parameters['vibration_severity']
    assert vibration_severity.min == 0.49
    assert vibration_severity.unit == 'g_rms'


def test_protocol_measurements(protocol_loader):
    """Test protocol measurements are loaded correctly."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    assert len(protocol.measurements) > 0

    # Find pre-test visual inspection
    visual_inspection = protocol.get_measurement_by_id('visual_inspection_pre')
    assert visual_inspection is not None
    assert visual_inspection.name == 'Pre-test Visual Inspection'
    assert visual_inspection.required is True


def test_protocol_pass_criteria(protocol_loader):
    """Test protocol pass criteria are loaded correctly."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    assert 'power_degradation' in protocol.pass_criteria
    assert 'visual_defects' in protocol.pass_criteria

    power_criterion = protocol.pass_criteria['power_degradation']
    assert power_criterion.max == 5.0
    assert power_criterion.unit == 'percent'


def test_validate_protocol_parameters(protocol_loader):
    """Test parameter validation."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    # Valid parameters
    valid_params = {
        'vibration_severity': 0.5,
        'test_duration': 180,
        'axis': 'vertical'
    }

    is_valid, errors = protocol.validate_parameters(valid_params)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid parameters - below minimum
    invalid_params = {
        'vibration_severity': 0.3,  # Below minimum of 0.49
        'test_duration': 180
    }

    is_valid, errors = protocol.validate_parameters(invalid_params)
    assert is_valid is False
    assert len(errors) > 0


def test_get_measurements_by_stage(protocol_loader):
    """Test getting measurements by stage."""
    protocol = protocol_loader.load_protocol('VIBR-001')

    from src.models.protocol import TestStage

    pre_test_measurements = protocol.get_measurements_by_stage(TestStage.PRE_TEST)
    assert len(pre_test_measurements) > 0

    during_test_measurements = protocol.get_measurements_by_stage(TestStage.DURING_TEST)
    assert len(during_test_measurements) > 0

    post_test_measurements = protocol.get_measurements_by_stage(TestStage.POST_TEST)
    assert len(post_test_measurements) > 0


def test_get_protocol_info(protocol_loader):
    """Test getting protocol info without full loading."""
    info = protocol_loader.get_protocol_info('VIBR-001')

    assert info is not None
    assert info['id'] == 'VIBR-001'
    assert info['name'] == 'Transportation Vibration Test'
    assert info['version'] == '1.0.0'
    assert 'description' in info


def test_validate_protocol_file(protocol_loader):
    """Test protocol file validation."""
    protocol_file = protocol_loader._find_protocol_file('VIBR-001')
    assert protocol_file is not None

    is_valid, error = protocol_loader.validate_protocol_file(protocol_file)
    assert is_valid is True
    assert error is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
