"""
Unit Tests for Protocol Loader
===============================

Tests for protocol loading and management.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.core.protocol_loader import ProtocolLoader


class TestProtocolLoader:
    """Test suite for ProtocolLoader"""

    @pytest.fixture
    def temp_protocols_dir(self, sample_diel001_protocol):
        """Create temporary protocols directory with sample protocol"""
        with tempfile.TemporaryDirectory() as tmpdir:
            protocols_path = Path(tmpdir)

            # Create DIEL-001 protocol directory
            diel_dir = protocols_path / "DIEL-001"
            diel_dir.mkdir()

            # Write protocol.json
            protocol_file = diel_dir / "protocol.json"
            with open(protocol_file, 'w') as f:
                json.dump(sample_diel001_protocol, f)

            yield str(protocols_path)

    def test_load_protocol_success(self, temp_protocols_dir):
        """Test successful protocol loading"""
        loader = ProtocolLoader(temp_protocols_dir)
        protocol = loader.load_protocol("DIEL-001")

        assert protocol is not None
        assert protocol['protocol_id'] == "DIEL-001"
        assert protocol['protocol_name'] == "Dielectric Withstand Test"

    def test_load_protocol_not_found(self, temp_protocols_dir):
        """Test loading non-existent protocol"""
        loader = ProtocolLoader(temp_protocols_dir)
        protocol = loader.load_protocol("NONEXISTENT-001")

        assert protocol is None

    def test_load_protocol_caching(self, temp_protocols_dir):
        """Test protocol caching functionality"""
        loader = ProtocolLoader(temp_protocols_dir)

        # First load
        protocol1 = loader.load_protocol("DIEL-001")

        # Second load (from cache)
        protocol2 = loader.load_protocol("DIEL-001", use_cache=True)

        # Should be the same object
        assert protocol1 is protocol2

    def test_load_all_protocols(self, temp_protocols_dir):
        """Test loading all protocols"""
        loader = ProtocolLoader(temp_protocols_dir)
        protocols = loader.load_all_protocols()

        assert len(protocols) == 1
        assert "DIEL-001" in protocols

    def test_get_protocol_metadata(self, temp_protocols_dir):
        """Test getting protocol metadata"""
        loader = ProtocolLoader(temp_protocols_dir)
        metadata = loader.get_protocol_metadata("DIEL-001")

        assert metadata is not None
        assert metadata.protocol_id == "DIEL-001"
        assert metadata.version == "1.0.0"
        assert metadata.is_valid is True

    def test_list_available_protocols(self, temp_protocols_dir):
        """Test listing available protocols"""
        loader = ProtocolLoader(temp_protocols_dir)
        protocols = loader.list_available_protocols()

        assert len(protocols) == 1
        assert protocols[0].protocol_id == "DIEL-001"

    def test_get_protocols_by_category(self, temp_protocols_dir):
        """Test filtering protocols by category"""
        loader = ProtocolLoader(temp_protocols_dir)
        safety_protocols = loader.get_protocols_by_category("safety")

        assert len(safety_protocols) == 1
        assert safety_protocols[0]['protocol_id'] == "DIEL-001"

    def test_get_data_points(self, temp_protocols_dir):
        """Test getting data points from protocol"""
        loader = ProtocolLoader(temp_protocols_dir)
        data_points = loader.get_data_points("DIEL-001")

        assert data_points is not None
        assert len(data_points) == 3
        assert data_points[0]['field'] == 'module_id'

    def test_clear_cache(self, temp_protocols_dir):
        """Test cache clearing"""
        loader = ProtocolLoader(temp_protocols_dir)

        # Load protocol
        loader.load_protocol("DIEL-001")
        assert len(loader._protocol_cache) == 1

        # Clear cache
        loader.clear_cache()
        assert len(loader._protocol_cache) == 0
