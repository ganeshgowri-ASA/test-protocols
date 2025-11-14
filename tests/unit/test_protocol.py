"""Unit tests for protocol base classes."""

import pytest
from pathlib import Path


class TestProtocol:
    """Tests for Protocol class."""

    def test_protocol_loads_successfully(self, uvid_001_protocol):
        """Test that protocol loads from JSON file."""
        assert uvid_001_protocol is not None
        assert uvid_001_protocol.protocol_id == "UVID-001"
        assert uvid_001_protocol.name == "UV-Induced Degradation Protocol"
        assert uvid_001_protocol.version == "1.0.0"
        assert uvid_001_protocol.category == "Degradation"

    def test_protocol_has_parameters(self, uvid_001_protocol):
        """Test that protocol has test parameters defined."""
        assert len(uvid_001_protocol.parameters) > 0
        assert 'uv_irradiance' in uvid_001_protocol.parameters
        assert 'chamber_temperature' in uvid_001_protocol.parameters
        assert 'exposure_duration' in uvid_001_protocol.parameters

    def test_protocol_parameter_validation(self, uvid_001_protocol):
        """Test parameter validation."""
        # Valid parameters
        valid_params = {
            'uv_irradiance': 1.0,
            'chamber_temperature': 60.0,
            'exposure_duration': 1000,
            'relative_humidity': 50.0
        }
        is_valid, errors = uvid_001_protocol.validate_parameters(valid_params)
        assert is_valid
        assert len(errors) == 0

    def test_protocol_parameter_validation_out_of_range(self, uvid_001_protocol):
        """Test parameter validation with out-of-range values."""
        invalid_params = {
            'uv_irradiance': 10.0,  # Max is 1.5
            'chamber_temperature': 60.0,
            'exposure_duration': 1000
        }
        is_valid, errors = uvid_001_protocol.validate_parameters(invalid_params)
        assert not is_valid
        assert len(errors) > 0

    def test_protocol_parameter_validation_missing_required(self, uvid_001_protocol):
        """Test parameter validation with missing required parameters."""
        incomplete_params = {
            'uv_irradiance': 1.0,
            # Missing chamber_temperature
            'exposure_duration': 1000
        }
        is_valid, errors = uvid_001_protocol.validate_parameters(incomplete_params)
        assert not is_valid
        assert any('chamber_temperature' in error for error in errors)

    def test_protocol_has_measurement_points(self, uvid_001_protocol):
        """Test that protocol has measurement points defined."""
        assert len(uvid_001_protocol.measurement_points) > 0

        # Check for required measurement points
        point_ids = [mp.id for mp in uvid_001_protocol.measurement_points]
        assert 'initial' in point_ids
        assert 'final' in point_ids

    def test_protocol_measurement_points_ordered(self, uvid_001_protocol):
        """Test that measurement points are ordered by sequence."""
        sequences = [mp.sequence for mp in uvid_001_protocol.measurement_points]
        assert sequences == sorted(sequences)

    def test_get_required_measurements(self, uvid_001_protocol):
        """Test getting required measurement points."""
        required = uvid_001_protocol.get_required_measurements()
        assert len(required) > 0

        # Initial and final should be required
        required_ids = [mp.id for mp in required]
        assert 'initial' in required_ids
        assert 'final' in required_ids

    def test_get_optional_measurements(self, uvid_001_protocol):
        """Test getting optional measurement points."""
        optional = uvid_001_protocol.get_optional_measurements()

        # Intermediate measurements should be optional
        optional_ids = [mp.id for mp in optional]
        assert any('intermediate' in id for id in optional_ids)

    def test_protocol_has_pass_fail_criteria(self, uvid_001_protocol):
        """Test that protocol has pass/fail criteria defined."""
        assert len(uvid_001_protocol.pass_fail_criteria) > 0
        assert 'pmax_retention' in uvid_001_protocol.pass_fail_criteria
        assert 'efficiency_retention' in uvid_001_protocol.pass_fail_criteria

    def test_evaluate_pass_fail_passing_case(
        self,
        uvid_001_protocol,
        sample_initial_measurements,
        sample_final_measurements_pass
    ):
        """Test pass/fail evaluation with passing measurements."""
        results = uvid_001_protocol.evaluate_pass_fail(
            sample_initial_measurements,
            sample_final_measurements_pass
        )

        assert results['overall_pass'] is True
        assert 'criteria_results' in results

        # Check specific criteria
        pmax_result = results['criteria_results']['pmax_retention']
        assert pmax_result['pass'] is True
        assert pmax_result['retention_pct'] >= 95.0

    def test_evaluate_pass_fail_failing_case(
        self,
        uvid_001_protocol,
        sample_initial_measurements,
        sample_final_measurements_fail
    ):
        """Test pass/fail evaluation with failing measurements."""
        results = uvid_001_protocol.evaluate_pass_fail(
            sample_initial_measurements,
            sample_final_measurements_fail
        )

        assert results['overall_pass'] is False
        assert 'criteria_results' in results

        # Check that critical criteria failed
        pmax_result = results['criteria_results']['pmax_retention']
        assert pmax_result['pass'] is False
        assert pmax_result['retention_pct'] < 95.0


class TestProtocolRegistry:
    """Tests for ProtocolRegistry class."""

    def test_registry_initialization(self, protocol_registry):
        """Test registry initializes empty."""
        assert len(protocol_registry) == 0

    def test_register_protocol(self, protocol_registry, uvid_001_protocol):
        """Test registering a protocol."""
        protocol_registry.register(uvid_001_protocol)
        assert len(protocol_registry) == 1
        assert 'UVID-001' in protocol_registry

    def test_get_protocol(self, protocol_registry, uvid_001_protocol):
        """Test getting a protocol by ID."""
        protocol_registry.register(uvid_001_protocol)
        retrieved = protocol_registry.get('UVID-001')

        assert retrieved is not None
        assert retrieved.protocol_id == 'UVID-001'

    def test_get_nonexistent_protocol(self, protocol_registry):
        """Test getting a nonexistent protocol returns None."""
        retrieved = protocol_registry.get('NONEXISTENT')
        assert retrieved is None

    def test_list_protocols(self, protocol_registry, uvid_001_protocol):
        """Test listing all protocols."""
        protocol_registry.register(uvid_001_protocol)
        protocols = protocol_registry.list_protocols()

        assert len(protocols) == 1
        assert protocols[0]['protocol_id'] == 'UVID-001'
        assert protocols[0]['name'] == 'UV-Induced Degradation Protocol'

    def test_get_by_category(self, protocol_registry, uvid_001_protocol):
        """Test getting protocols by category."""
        protocol_registry.register(uvid_001_protocol)
        degradation_protocols = protocol_registry.get_by_category('Degradation')

        assert len(degradation_protocols) == 1
        assert degradation_protocols[0].protocol_id == 'UVID-001'

    def test_clear_registry(self, protocol_registry, uvid_001_protocol):
        """Test clearing the registry."""
        protocol_registry.register(uvid_001_protocol)
        assert len(protocol_registry) == 1

        protocol_registry.clear()
        assert len(protocol_registry) == 0
