"""
Unit tests for protocol definitions and models
"""

import pytest
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from protocols.delam_001.definition import DELAM001Protocol


class TestDELAM001Protocol:
    """Test DELAM-001 protocol definition"""

    def test_protocol_initialization(self):
        """Test protocol initialization with defaults"""
        protocol = DELAM001Protocol()

        assert protocol.protocol_id == "DELAM-001"
        assert protocol.protocol_name == "Delamination Test with EL Imaging"
        assert protocol.version == "1.0.0"

    def test_protocol_properties(self):
        """Test protocol property accessors"""
        protocol = DELAM001Protocol()

        # Environmental conditions
        env_conditions = protocol.environmental_conditions
        assert env_conditions.temperature.value == 85.0
        assert env_conditions.humidity.value == 85.0

        # Test duration
        duration = protocol.test_duration
        assert duration.value == 1000
        assert duration.unit == "hours"

        # Inspection intervals
        intervals = protocol.inspection_intervals
        assert len(intervals) == 4
        assert intervals[0].interval == 0

        # Acceptance criteria
        criteria = protocol.acceptance_criteria
        assert criteria.maximum_delamination_area['value'] == 5.0

    def test_parameter_update(self):
        """Test updating protocol parameters"""
        protocol = DELAM001Protocol()

        original_temp = protocol.config['test_parameters']['environmental_conditions']['temperature']['value']

        protocol.update_parameter(
            'test_parameters.environmental_conditions.temperature.value',
            90.0
        )

        new_temp = protocol.config['test_parameters']['environmental_conditions']['temperature']['value']

        assert new_temp == 90.0
        assert new_temp != original_temp

    def test_protocol_validation(self):
        """Test protocol test data validation"""
        protocol = DELAM001Protocol()

        test_data = {
            'module_id': 'MOD-2025-001',
            'test_start_time': '2025-01-15T10:00:00Z',
            'environmental_data': {
                'temperature': 85.0,
                'humidity': 85.0
            },
            'measurements': []
        }

        is_valid, errors = protocol.validate_test_data(test_data)
        assert is_valid
        assert len(errors) == 0

    def test_acceptance_criteria_check(self):
        """Test checking results against acceptance criteria"""
        protocol = DELAM001Protocol()

        # Passing results
        passing_results = {
            'delamination_area_percent': 3.0,
            'power_degradation_percent': 2.0,
            'visual_inspection': {
                'no_bubbles': True,
                'no_discoloration': True,
                'no_broken_cells': True,
                'no_broken_interconnects': True
            }
        }

        passed, details = protocol.check_acceptance_criteria(passing_results)
        assert passed
        assert details['passed']

        # Failing results
        failing_results = {
            'delamination_area_percent': 10.0,  # Exceeds 5%
            'power_degradation_percent': 8.0,   # Exceeds 5%
        }

        passed, details = protocol.check_acceptance_criteria(failing_results)
        assert not passed
        assert not details['passed']
        assert len(details['failures']) > 0

    def test_protocol_save_load(self, tmp_path):
        """Test saving and loading protocol configuration"""
        protocol = DELAM001Protocol()

        # Modify a parameter
        protocol.update_parameter(
            'test_parameters.environmental_conditions.temperature.value',
            90.0
        )

        # Save to file
        save_path = tmp_path / "test_protocol.json"
        protocol.save(save_path)

        assert save_path.exists()

        # Load from file
        loaded_protocol = DELAM001Protocol.load(save_path)

        assert loaded_protocol.config['test_parameters']['environmental_conditions']['temperature']['value'] == 90.0

    def test_protocol_to_json(self):
        """Test converting protocol to JSON string"""
        protocol = DELAM001Protocol()

        json_str = protocol.to_json()
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data['protocol_id'] == "DELAM-001"

    def test_required_equipment(self):
        """Test getting required equipment list"""
        protocol = DELAM001Protocol()

        equipment = protocol.get_required_equipment()
        assert len(equipment) > 0
        assert any('Environmental Chamber' in eq['name'] for eq in equipment)
        assert any('EL Camera' in eq['name'] for eq in equipment)

    def test_data_collection_requirements(self):
        """Test getting data collection requirements"""
        protocol = DELAM001Protocol()

        requirements = protocol.get_data_collection_requirements()
        assert 'measurements' in requirements
        assert 'images' in requirements
        assert requirements['images']['el_images']['required'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
