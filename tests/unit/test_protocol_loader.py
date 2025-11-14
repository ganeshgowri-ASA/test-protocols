"""
Unit Tests for Protocol Loader

Tests the protocol loading and caching functionality.
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core import ProtocolLoader


class TestProtocolLoader:
    """Test cases for ProtocolLoader class."""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create a ProtocolLoader with temporary protocols directory."""
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir()
        return ProtocolLoader(protocols_dir)

    @pytest.fixture
    def sample_protocol(self, tmp_path):
        """Create a sample protocol file."""
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir(exist_ok=True)

        protocol_data = {
            "protocol_id": "TEST-001",
            "name": "Test Protocol",
            "version": "1.0.0",
            "category": "test",
            "test_sequence": {
                "steps": [
                    {
                        "step_id": 1,
                        "name": "Test Step",
                        "type": "measurement",
                        "substeps": []
                    }
                ]
            }
        }

        protocol_file = protocols_dir / "test-001.json"
        with open(protocol_file, 'w') as f:
            json.dump(protocol_data, f)

        return protocol_file, protocol_data

    def test_initialization(self, tmp_path):
        """Test ProtocolLoader initialization."""
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir()

        loader = ProtocolLoader(protocols_dir)

        assert loader.protocols_dir == protocols_dir
        assert loader._protocol_cache == {}

    def test_load_protocol_success(self, tmp_path, sample_protocol):
        """Test successful protocol loading."""
        protocol_file, expected_data = sample_protocol
        loader = ProtocolLoader(tmp_path / "protocols")

        protocol = loader.load_protocol("TEST-001")

        assert protocol == expected_data
        assert protocol['protocol_id'] == "TEST-001"
        assert protocol['name'] == "Test Protocol"

    def test_load_protocol_not_found(self, loader):
        """Test loading non-existent protocol."""
        with pytest.raises(FileNotFoundError):
            loader.load_protocol("NONEXISTENT-001")

    def test_load_protocol_caching(self, tmp_path, sample_protocol):
        """Test protocol caching."""
        protocol_file, expected_data = sample_protocol
        loader = ProtocolLoader(tmp_path / "protocols")

        # First load
        protocol1 = loader.load_protocol("TEST-001")

        # Second load (should be from cache)
        protocol2 = loader.load_protocol("TEST-001")

        assert protocol1 is protocol2  # Same object from cache
        assert "TEST-001" in loader._protocol_cache

    def test_load_protocol_from_file(self, tmp_path, sample_protocol):
        """Test loading protocol from specific file path."""
        protocol_file, expected_data = sample_protocol
        loader = ProtocolLoader(tmp_path / "protocols")

        protocol = loader.load_protocol_from_file(protocol_file)

        assert protocol == expected_data

    def test_list_protocols(self, tmp_path, sample_protocol):
        """Test listing available protocols."""
        loader = ProtocolLoader(tmp_path / "protocols")

        protocols = loader.list_protocols()

        assert len(protocols) == 1
        assert protocols[0]['protocol_id'] == "TEST-001"
        assert protocols[0]['name'] == "Test Protocol"
        assert protocols[0]['version'] == "1.0.0"

    def test_list_protocols_empty(self, loader):
        """Test listing protocols when none exist."""
        protocols = loader.list_protocols()

        assert protocols == []

    def test_get_protocol_metadata(self, tmp_path, sample_protocol):
        """Test getting protocol metadata."""
        loader = ProtocolLoader(tmp_path / "protocols")

        metadata = loader.get_protocol_metadata("TEST-001")

        assert metadata['protocol_id'] == "TEST-001"
        assert metadata['name'] == "Test Protocol"
        assert metadata['version'] == "1.0.0"
        assert metadata['category'] == "test"

    def test_get_test_steps(self, tmp_path, sample_protocol):
        """Test getting test steps."""
        loader = ProtocolLoader(tmp_path / "protocols")

        steps = loader.get_test_steps("TEST-001")

        assert len(steps) == 1
        assert steps[0]['step_id'] == 1
        assert steps[0]['name'] == "Test Step"

    def test_clear_cache(self, tmp_path, sample_protocol):
        """Test clearing protocol cache."""
        loader = ProtocolLoader(tmp_path / "protocols")

        # Load protocol
        loader.load_protocol("TEST-001")
        assert "TEST-001" in loader._protocol_cache

        # Clear cache
        loader.clear_cache()
        assert loader._protocol_cache == {}

    def test_invalid_json(self, tmp_path):
        """Test loading invalid JSON."""
        protocols_dir = tmp_path / "protocols"
        protocols_dir.mkdir()

        invalid_file = protocols_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")

        loader = ProtocolLoader(protocols_dir)

        # Should not crash when listing protocols
        protocols = loader.list_protocols()
        assert protocols == []
