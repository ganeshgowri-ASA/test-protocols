"""Unit tests for SchemaValidator."""

import pytest
from src.core.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test cases for SchemaValidator class."""

    def test_initialization(self, schema_validator):
        """Test SchemaValidator initialization."""
        assert schema_validator is not None
        assert schema_validator.protocol_manager is not None

    def test_validate_valid_data(self, schema_validator, sample_conc001_data, protocol_manager):
        """Test validation with valid data."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = schema_validator.validate_data('conc-001', sample_conc001_data)

            assert result is not None
            assert 'valid' in result
            assert 'errors' in result
            assert 'warnings' in result

    def test_validate_invalid_data(self, schema_validator, invalid_conc001_data, protocol_manager):
        """Test validation with invalid data."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = schema_validator.validate_data('conc-001', invalid_conc001_data)

            assert result is not None
            assert result['valid'] is False
            assert len(result.get('errors', [])) > 0

    def test_validate_nonexistent_protocol(self, schema_validator):
        """Test validation with non-existent protocol."""
        result = schema_validator.validate_data('nonexistent-protocol', {})

        assert result is not None
        assert result['valid'] is False
        assert len(result.get('errors', [])) > 0

    def test_validate_qc_criteria(self, schema_validator, sample_conc001_data, protocol_manager):
        """Test QC criteria validation."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = schema_validator.validate_qc_criteria('conc-001', sample_conc001_data)

            assert result is not None
            assert 'passed' in result
            assert 'overall_status' in result
            assert 'criteria_results' in result

    def test_custom_conc001_validations(self, schema_validator, protocol_manager):
        """Test CONC-001 specific validations."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            # Data with fill factor mismatch
            data_with_mismatch = {
                "test_run_id": "CONC-001-20251114-0001",
                "sample_id": "TEST-001",
                "timestamp": "2025-11-14T10:00:00",
                "operator": "Test",
                "measurements": [
                    {
                        "concentration_suns": 1.0,
                        "temperature_c": 25.0,
                        "voc": 0.650,
                        "isc": 8.5,
                        "vmp": 0.550,
                        "imp": 8.0,
                        "fill_factor": 0.500,  # Incorrect - should be ~0.846
                        "efficiency": 22.5
                    }
                ]
            }

            result = schema_validator.validate_data('conc-001', data_with_mismatch)

            assert result is not None
            # Should have warnings about fill factor
            assert len(result.get('warnings', [])) > 0

    def test_temperature_out_of_range(self, schema_validator, protocol_manager):
        """Test validation with temperature out of valid range."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            data_invalid_temp = {
                "test_run_id": "CONC-001-20251114-0001",
                "sample_id": "TEST-001",
                "timestamp": "2025-11-14T10:00:00",
                "operator": "Test",
                "measurements": [
                    {
                        "concentration_suns": 1.0,
                        "temperature_c": 300.0,  # Out of range
                        "voc": 0.650,
                        "isc": 8.5,
                        "vmp": 0.550,
                        "imp": 8.0,
                        "fill_factor": 0.846,
                        "efficiency": 22.5
                    }
                ]
            }

            result = schema_validator.validate_data('conc-001', data_invalid_temp)

            assert result is not None
            # Should have errors about temperature
            assert len(result.get('errors', [])) > 0
