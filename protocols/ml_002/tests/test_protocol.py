"""
Unit tests for ML-002 protocol definition

Tests protocol JSON structure, schema validation, and parameters

Author: ganeshgowri-ASA
Date: 2025-11-14
"""

import pytest
import json
from pathlib import Path
import jsonschema


class TestML002Protocol:
    """Test suite for ML-002 protocol definition"""

    @pytest.fixture
    def protocol_file(self):
        """Get protocol file path"""
        return Path(__file__).parent.parent / "protocol.json"

    @pytest.fixture
    def schema_file(self):
        """Get schema file path"""
        return Path(__file__).parent.parent / "schema.json"

    @pytest.fixture
    def protocol_data(self, protocol_file):
        """Load protocol data"""
        with open(protocol_file) as f:
            return json.load(f)

    @pytest.fixture
    def schema_data(self, schema_file):
        """Load schema data"""
        with open(schema_file) as f:
            return json.load(f)

    def test_protocol_file_exists(self, protocol_file):
        """Test that protocol file exists"""
        assert protocol_file.exists(), "Protocol file not found"

    def test_protocol_valid_json(self, protocol_file):
        """Test that protocol is valid JSON"""
        try:
            with open(protocol_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Protocol is not valid JSON: {e}")

    def test_protocol_has_required_sections(self, protocol_data):
        """Test that protocol has all required sections"""
        required_sections = [
            'metadata',
            'parameters',
            'data_collection',
            'quality_control',
            'data_processing',
            'reporting'
        ]

        for section in required_sections:
            assert section in protocol_data, f"Missing required section: {section}"

    def test_metadata_structure(self, protocol_data):
        """Test metadata section structure"""
        metadata = protocol_data['metadata']

        required_fields = ['protocol_id', 'name', 'version', 'test_type']
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"

        assert metadata['protocol_id'] == 'ML-002', "Incorrect protocol ID"
        assert metadata['test_type'] == 'mechanical_load', "Incorrect test type"

    def test_version_format(self, protocol_data):
        """Test that version follows semantic versioning"""
        version = protocol_data['metadata']['version']
        parts = version.split('.')

        assert len(parts) == 3, "Version should be in format X.Y.Z"
        for part in parts:
            assert part.isdigit(), "Version parts should be numbers"

    def test_load_configuration(self, protocol_data):
        """Test load configuration parameters"""
        load_config = protocol_data['parameters']['load_configuration']

        assert 'test_load_pa' in load_config
        assert load_config['test_load_pa']['value'] == 1000, "Test load should be 1000 Pa"
        assert load_config['test_load_pa']['unit'] == 'Pa'

    def test_cycle_parameters(self, protocol_data):
        """Test cycle parameters"""
        cycle_params = protocol_data['parameters']['cycle_parameters']

        assert 'cycle_count' in cycle_params
        assert cycle_params['cycle_count']['value'] >= 100, "Cycle count should be at least 100"

    def test_environmental_conditions(self, protocol_data):
        """Test environmental conditions"""
        env_conditions = protocol_data['parameters']['environmental_conditions']

        temp = env_conditions['temperature_celsius']
        assert temp['min'] >= 15 and temp['max'] <= 35, "Temperature range should be 15-35°C"

        humidity = env_conditions['humidity_percent']
        assert humidity['min'] >= 45 and humidity['max'] <= 75, "Humidity range should be 45-75%"

    def test_sensor_mappings(self, protocol_data):
        """Test sensor mappings"""
        sensors = protocol_data['data_collection']['sensor_mappings']

        assert len(sensors) > 0, "At least one sensor should be defined"

        # Check for required sensors
        sensor_types = [s['sensor_type'] for s in sensors]
        assert 'load_cell' in sensor_types, "Load cell sensor required"
        assert 'lvdt' in sensor_types, "LVDT sensor required"

    def test_acceptance_criteria(self, protocol_data):
        """Test acceptance criteria"""
        criteria = protocol_data['quality_control']['acceptance_criteria']

        assert len(criteria) > 0, "At least one acceptance criterion required"

        # Check for critical criteria
        critical_ids = [c['criteria_id'] for c in criteria if c['is_critical']]
        assert len(critical_ids) > 0, "At least one critical criterion required"

    def test_failure_conditions(self, protocol_data):
        """Test failure conditions"""
        failures = protocol_data['quality_control']['failure_conditions']

        assert len(failures) > 0, "At least one failure condition required"

        # Check for critical failures
        critical_failures = [f for f in failures if f['alert_level'] == 'critical']
        assert len(critical_failures) > 0, "At least one critical failure condition required"

    def test_charts_defined(self, protocol_data):
        """Test that charts are defined for reporting"""
        charts = protocol_data['reporting']['charts']

        assert len(charts) > 0, "At least one chart should be defined"

        # Check for essential charts
        chart_ids = [c['chart_id'] for c in charts]
        assert 'load_vs_deflection' in chart_ids, "Load vs deflection chart required"

    def test_protocol_validates_against_schema(self, protocol_data, schema_data):
        """Test that protocol validates against JSON schema"""
        try:
            jsonschema.validate(instance=protocol_data, schema=schema_data)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Protocol does not validate against schema: {e}")

    def test_integrations_configured(self, protocol_data):
        """Test that integrations are configured"""
        integrations = protocol_data['integrations']

        assert 'lims' in integrations
        assert 'qms' in integrations

    def test_safety_requirements(self, protocol_data):
        """Test that safety requirements are defined"""
        safety = protocol_data['safety']

        assert 'safety_requirements' in safety
        assert len(safety['safety_requirements']) > 0, "Safety requirements should be defined"

        assert 'emergency_procedures' in safety
        assert safety['emergency_procedures']['emergency_stop_available'] is True


class TestML002ProtocolCalculations:
    """Test calculated values in protocol"""

    @pytest.fixture
    def protocol_data(self):
        """Load protocol data"""
        protocol_file = Path(__file__).parent.parent / "protocol.json"
        with open(protocol_file) as f:
            return json.load(f)

    def test_estimated_duration_calculation(self, protocol_data):
        """Test estimated duration calculation"""
        cycle_params = protocol_data['parameters']['cycle_parameters']

        cycle_count = cycle_params['cycle_count']['value']
        cycle_duration = cycle_params['cycle_duration_seconds']['value']
        rest_time = cycle_params['rest_time_between_cycles_seconds']['value']

        expected_duration = cycle_count * (cycle_duration + rest_time)

        assert expected_duration > 0, "Estimated duration should be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
