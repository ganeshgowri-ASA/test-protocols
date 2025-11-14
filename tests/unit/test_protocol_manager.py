"""Unit tests for ProtocolManager."""

import pytest
from src.core.protocol_manager import ProtocolManager


class TestProtocolManager:
    """Test cases for ProtocolManager class."""

    def test_initialization(self, protocol_manager):
        """Test ProtocolManager initialization."""
        assert protocol_manager is not None
        assert isinstance(protocol_manager.protocols, dict)

    def test_list_protocols(self, protocol_manager):
        """Test listing available protocols."""
        protocols = protocol_manager.list_protocols()
        assert isinstance(protocols, list)

        # Should have conc-001 if protocols directory exists
        if protocols:
            assert 'conc-001' in protocols

    def test_get_protocol(self, protocol_manager):
        """Test retrieving a specific protocol."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            protocol = protocol_manager.get_protocol('conc-001')
            assert protocol is not None
            assert protocol.get('protocol_id') == 'conc-001'
            assert 'version' in protocol
            assert 'schema' in protocol

    def test_get_nonexistent_protocol(self, protocol_manager):
        """Test retrieving a non-existent protocol."""
        protocol = protocol_manager.get_protocol('nonexistent-protocol')
        assert protocol is None

    def test_get_protocol_metadata(self, protocol_manager):
        """Test retrieving protocol metadata."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            metadata = protocol_manager.get_protocol_metadata('conc-001')
            assert metadata is not None
            assert 'protocol_id' in metadata
            assert 'name' in metadata
            assert 'version' in metadata

    def test_get_config(self, protocol_manager):
        """Test retrieving protocol configuration."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            config = protocol_manager.get_config('conc-001')
            # Config might be None if not loaded
            if config is not None:
                assert isinstance(config, dict)

    def test_get_qc_criteria(self, protocol_manager):
        """Test retrieving QC criteria."""
        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            qc_criteria = protocol_manager.get_qc_criteria('conc-001')
            assert qc_criteria is not None
            assert isinstance(qc_criteria, dict)

    def test_generate_test_run_id(self, protocol_manager):
        """Test test run ID generation."""
        test_run_id = protocol_manager.generate_test_run_id('conc-001')

        assert test_run_id is not None
        assert test_run_id.startswith('CONC-001-')
        assert len(test_run_id.split('-')) == 3

    def test_validate_equipment_calibration_valid(self, protocol_manager):
        """Test equipment calibration validation with valid data."""
        from datetime import datetime, timedelta

        equipment_data = {
            "calibration_date": (datetime.now() - timedelta(days=30)).isoformat()
        }

        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = protocol_manager.validate_equipment_calibration(
                'conc-001',
                equipment_data
            )

            assert result is not None
            assert 'valid' in result

    def test_validate_equipment_calibration_expired(self, protocol_manager):
        """Test equipment calibration validation with expired calibration."""
        from datetime import datetime, timedelta

        equipment_data = {
            "calibration_date": (datetime.now() - timedelta(days=500)).isoformat()
        }

        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = protocol_manager.validate_equipment_calibration(
                'conc-001',
                equipment_data
            )

            assert result is not None
            assert 'valid' in result
            # Should be invalid due to expired calibration
            assert result['valid'] is False or len(result.get('errors', [])) > 0

    def test_validate_equipment_calibration_missing_date(self, protocol_manager):
        """Test equipment calibration validation with missing date."""
        equipment_data = {}

        protocols = protocol_manager.list_protocols()

        if 'conc-001' in protocols:
            result = protocol_manager.validate_equipment_calibration(
                'conc-001',
                equipment_data
            )

            assert result is not None
            assert result['valid'] is False
            assert len(result.get('errors', [])) > 0
