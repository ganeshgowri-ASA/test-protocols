"""Unit tests for protocol loading and management."""

import pytest
from src.core.protocol_loader import ProtocolLoader


class TestProtocolLoader:
    """Tests for ProtocolLoader class."""

    def test_load_perf002_protocol(self, protocol_loader):
        """Test loading PERF-002 protocol."""
        protocol = protocol_loader.load("PERF-002")

        assert protocol is not None
        assert protocol['protocol_id'] == "PERF-002"
        assert protocol['version'] == "1.0.0"
        assert protocol['category'] == "Performance"

    def test_get_irradiance_levels(self, protocol_loader):
        """Test getting irradiance levels from protocol."""
        levels = protocol_loader.get_irradiance_levels("PERF-002")

        expected_levels = [100, 200, 400, 600, 800, 1000, 1100]
        assert levels == expected_levels

    def test_get_required_equipment(self, protocol_loader):
        """Test getting required equipment."""
        equipment = protocol_loader.get_required_equipment("PERF-002")

        assert len(equipment) > 0
        assert any(eq['type'] == 'solar_simulator' for eq in equipment)
        assert any(eq['type'] == 'reference_cell' for eq in equipment)

    def test_get_data_fields(self, protocol_loader):
        """Test getting data collection fields."""
        fields = protocol_loader.get_data_fields("PERF-002")

        field_names = [f['name'] for f in fields]
        assert 'irradiance' in field_names
        assert 'voltage' in field_names
        assert 'current' in field_names
        assert 'module_temperature' in field_names

    def test_get_qc_checks(self, protocol_loader):
        """Test getting QC checks."""
        qc_checks = protocol_loader.get_qc_checks("PERF-002")

        assert len(qc_checks) > 0
        check_names = [c['name'] for c in qc_checks]
        assert 'irradiance_tolerance' in check_names
        assert 'uniformity_threshold' in check_names

    def test_get_calculations(self, protocol_loader):
        """Test getting analysis calculations."""
        calculations = protocol_loader.get_calculations("PERF-002")

        calc_names = [c['name'] for c in calculations]
        assert 'pmax' in calc_names
        assert 'efficiency' in calc_names
        assert 'fill_factor' in calc_names

    def test_list_protocols(self, protocol_loader):
        """Test listing available protocols."""
        protocols = protocol_loader.list_protocols()

        assert len(protocols) > 0
        assert any(p['protocol_id'] == 'PERF-002' for p in protocols)

    def test_list_protocols_by_category(self, protocol_loader):
        """Test listing protocols by category."""
        protocols = protocol_loader.list_protocols(category='PERF')

        assert len(protocols) > 0
        assert all(p['category'] == 'Performance' for p in protocols)

    def test_cache_functionality(self, protocol_loader):
        """Test protocol caching."""
        # Load protocol first time
        protocol1 = protocol_loader.load("PERF-002")

        # Load again (should come from cache)
        protocol2 = protocol_loader.load("PERF-002")

        assert protocol1 is protocol2  # Same object reference

    def test_reload_clears_cache(self, protocol_loader):
        """Test reload functionality."""
        protocol1 = protocol_loader.load("PERF-002")
        protocol2 = protocol_loader.reload("PERF-002")

        # Should be different objects after reload
        assert protocol1 is not protocol2

    def test_invalid_protocol_raises_error(self, protocol_loader):
        """Test loading non-existent protocol raises error."""
        with pytest.raises(FileNotFoundError):
            protocol_loader.load("INVALID-999")
