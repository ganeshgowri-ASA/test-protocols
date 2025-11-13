"""
Unit tests for DELAM-001 validation module
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from protocols.delam_001.validation import DELAM001Validator


class TestModuleIDValidation:
    """Test module ID validation"""

    def test_valid_module_id(self):
        """Test valid module ID formats"""
        validator = DELAM001Validator()

        valid_ids = [
            "MOD-2025-001",
            "MODULE_001",
            "TEST-MOD-123",
            "ABC123XYZ"
        ]

        for module_id in valid_ids:
            is_valid, errors = validator.validate_module_id(module_id)
            assert is_valid, f"Expected {module_id} to be valid, got errors: {errors}"
            assert len(errors) == 0

    def test_invalid_module_id(self):
        """Test invalid module ID formats"""
        validator = DELAM001Validator()

        invalid_ids = [
            "",  # Empty
            "abc",  # Too short
            "mod-001",  # Lowercase
            "MODULE_001_VERY_LONG_ID_NAME",  # Too long
            "MOD 001",  # Space
            "MOD@001"  # Invalid character
        ]

        for module_id in invalid_ids:
            is_valid, errors = validator.validate_module_id(module_id)
            assert not is_valid, f"Expected {module_id} to be invalid"
            assert len(errors) > 0


class TestEnvironmentalDataValidation:
    """Test environmental data validation"""

    def test_valid_environmental_data(self):
        """Test valid environmental data"""
        validator = DELAM001Validator()

        data = {
            'temperature': 85.0,
            'humidity': 85.0
        }

        is_valid, errors = validator.validate_environmental_data(data)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test missing required fields"""
        validator = DELAM001Validator()

        # Missing humidity
        data = {'temperature': 85.0}
        is_valid, errors = validator.validate_environmental_data(data)
        assert not is_valid
        assert any('humidity' in err.lower() for err in errors)

        # Missing temperature
        data = {'humidity': 85.0}
        is_valid, errors = validator.validate_environmental_data(data)
        assert not is_valid
        assert any('temperature' in err.lower() for err in errors)

    def test_out_of_range_values(self):
        """Test out of range values"""
        validator = DELAM001Validator()

        # Temperature out of range
        data = {'temperature': 200.0, 'humidity': 85.0}
        is_valid, errors = validator.validate_environmental_data(data)
        assert not is_valid
        assert any('temperature' in err.lower() for err in errors)

        # Humidity out of range
        data = {'temperature': 85.0, 'humidity': 150.0}
        is_valid, errors = validator.validate_environmental_data(data)
        assert not is_valid
        assert any('humidity' in err.lower() for err in errors)

    def test_tolerance_validation(self):
        """Test validation with expected conditions and tolerance"""
        validator = DELAM001Validator()

        expected_conditions = {
            'temperature': {'value': 85.0, 'tolerance': 2.0},
            'humidity': {'value': 85.0, 'tolerance': 5.0}
        }

        # Within tolerance
        data = {'temperature': 86.0, 'humidity': 87.0}
        is_valid, errors = validator.validate_environmental_data(data, expected_conditions)
        assert is_valid
        assert len(errors) == 0

        # Outside tolerance
        data = {'temperature': 90.0, 'humidity': 95.0}
        is_valid, errors = validator.validate_environmental_data(data, expected_conditions)
        assert not is_valid
        assert len(errors) > 0


class TestELImageValidation:
    """Test EL image metadata validation"""

    def test_valid_el_image_metadata(self):
        """Test valid EL image metadata"""
        validator = DELAM001Validator()

        metadata = {
            'filename': 'test_image.tiff',
            'timestamp': '2025-01-15T10:30:00Z',
            'resolution': {'width': 2048, 'height': 2048},
            'bit_depth': 16
        }

        is_valid, errors = validator.validate_el_image_metadata(metadata)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_image_format(self):
        """Test invalid image format"""
        validator = DELAM001Validator()

        metadata = {
            'filename': 'test_image.bmp',  # Invalid format
            'timestamp': '2025-01-15T10:30:00Z',
            'resolution': {'width': 2048, 'height': 2048},
            'bit_depth': 16
        }

        is_valid, errors = validator.validate_el_image_metadata(metadata)
        assert not is_valid
        assert any('format' in err.lower() for err in errors)

    def test_low_resolution(self):
        """Test resolution below minimum"""
        validator = DELAM001Validator()

        metadata = {
            'filename': 'test_image.tiff',
            'timestamp': '2025-01-15T10:30:00Z',
            'resolution': {'width': 320, 'height': 240},  # Below minimum
            'bit_depth': 16
        }

        is_valid, errors = validator.validate_el_image_metadata(metadata)
        assert not is_valid
        assert any('resolution' in err.lower() for err in errors)


class TestMeasurementDataValidation:
    """Test measurement data validation"""

    def test_valid_measurement(self):
        """Test valid measurement data"""
        validator = DELAM001Validator()

        data = {
            'voltage': 50.0,
            'current': 10.0,
            'power': 500.0
        }

        is_valid, errors = validator.validate_measurement_data(data)
        assert is_valid
        assert len(errors) == 0

    def test_negative_values(self):
        """Test negative measurement values"""
        validator = DELAM001Validator()

        data = {
            'voltage': -50.0,
            'current': 10.0
        }

        is_valid, errors = validator.validate_measurement_data(data)
        assert not is_valid
        assert any('voltage' in err.lower() for err in errors)

    def test_power_calculation_validation(self):
        """Test power calculation cross-validation"""
        validator = DELAM001Validator()

        # Mismatched power
        data = {
            'voltage': 50.0,
            'current': 10.0,
            'power': 100.0  # Should be ~500W
        }

        is_valid, errors = validator.validate_measurement_data(data)
        assert not is_valid
        assert any('power' in err.lower() for err in errors)


class TestAnalysisResultsValidation:
    """Test analysis results validation"""

    def test_valid_analysis_results(self):
        """Test valid analysis results"""
        validator = DELAM001Validator()

        results = {
            'delamination_detected': True,
            'delamination_area_percent': 2.5,
            'defect_count': 3
        }

        is_valid, errors = validator.validate_analysis_results(results)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_percentage(self):
        """Test invalid percentage values"""
        validator = DELAM001Validator()

        results = {
            'delamination_detected': True,
            'delamination_area_percent': 150.0,  # >100%
            'defect_count': 3
        }

        is_valid, errors = validator.validate_analysis_results(results)
        assert not is_valid
        assert any('percent' in err.lower() for err in errors)

    def test_severity_level_validation(self):
        """Test severity level validation"""
        validator = DELAM001Validator()

        # Valid severity
        results = {
            'delamination_detected': True,
            'delamination_area_percent': 2.5,
            'defect_count': 3,
            'severity_level': 'moderate'
        }

        is_valid, errors = validator.validate_analysis_results(results)
        assert is_valid

        # Invalid severity
        results['severity_level'] = 'extreme'
        is_valid, errors = validator.validate_analysis_results(results)
        assert not is_valid
        assert any('severity' in err.lower() for err in errors)


class TestBatchValidation:
    """Test batch validation"""

    def test_batch_validation(self):
        """Test validation of multiple test records"""
        validator = DELAM001Validator()

        batch_data = [
            {
                'test_id': 'TEST-001',
                'module_id': 'MOD-2025-001',
                'start_time': '2025-01-15T10:00:00Z',
                'protocol_version': '1.0.0'
            },
            {
                'test_id': 'TEST-002',
                'module_id': 'INVALID',  # Invalid module ID
                'start_time': '2025-01-15T11:00:00Z',
                'protocol_version': '1.0.0'
            }
        ]

        all_valid, error_map = validator.validate_batch_test_data(batch_data)
        assert not all_valid
        assert 'TEST-002' in error_map
        assert len(error_map['TEST-002']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
