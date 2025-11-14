"""Unit tests for protocol loader."""

import unittest
import json
import tempfile
from pathlib import Path

from src.parsers import ProtocolLoader
from src.models.base import get_engine, init_db, get_session


class TestProtocolLoader(unittest.TestCase):
    """Test cases for ProtocolLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create in-memory database for testing
        self.engine = get_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.session = get_session(self.engine)

        # Create a temporary protocol file
        self.temp_dir = tempfile.mkdtemp()
        self.protocol_path = Path(self.temp_dir) / "test_protocol.json"

        # Sample protocol data
        self.protocol_data = {
            "protocol_id": "TEST-001",
            "protocol_name": "Test Protocol",
            "version": "1.0.0",
            "category": "Mechanical",
            "description": "Test protocol for unit testing",
            "standard_reference": [
                {
                    "standard": "IEC 61215-2",
                    "section": "Test Section"
                }
            ],
            "test_parameters": {
                "specimen_requirements": {
                    "quantity": 1,
                    "description": "Test specimen"
                },
                "environmental_conditions": {
                    "temperature_range": {
                        "min": 15,
                        "max": 35,
                        "unit": "°C"
                    }
                },
                "test_specific_parameters": {}
            },
            "test_steps": [
                {
                    "step_number": 1,
                    "description": "Test step 1",
                    "action": "measurement",
                    "automation_capable": False
                }
            ],
            "acceptance_criteria": [
                {
                    "criterion_id": "AC-001",
                    "description": "Test criterion",
                    "evaluation_method": "measurement",
                    "threshold": {
                        "parameter": "test_param",
                        "operator": "<=",
                        "value": 5.0,
                        "unit": "%"
                    }
                }
            ],
            "data_collection": {
                "measurements": [
                    {
                        "measurement_id": "M-001",
                        "parameter": "Test Parameter",
                        "unit": "W",
                        "instrument": "Test Instrument",
                        "accuracy": "±1%",
                        "data_type": "numeric"
                    }
                ],
                "documentation": []
            }
        }

        # Write protocol to file
        with open(self.protocol_path, 'w') as f:
            json.dump(self.protocol_data, f)

    def tearDown(self):
        """Clean up test fixtures."""
        self.session.close()
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_protocol_file(self):
        """Test loading a protocol JSON file."""
        loader = ProtocolLoader()
        data = loader.load_protocol_file(self.protocol_path)

        self.assertEqual(data["protocol_id"], "TEST-001")
        self.assertEqual(data["protocol_name"], "Test Protocol")
        self.assertEqual(data["version"], "1.0.0")

    def test_validate_protocol(self):
        """Test protocol validation against schema."""
        loader = ProtocolLoader()

        # This should not raise an exception
        is_valid = loader.validate_protocol(self.protocol_data)
        self.assertTrue(is_valid)

    def test_load_and_validate(self):
        """Test loading and validating a protocol file."""
        loader = ProtocolLoader()
        data = loader.load_and_validate(self.protocol_path)

        self.assertEqual(data["protocol_id"], "TEST-001")

    def test_import_to_database(self):
        """Test importing a protocol to the database."""
        loader = ProtocolLoader()
        protocol = loader.import_to_database(self.protocol_data, self.session)

        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.protocol_id, "TEST-001")
        self.assertEqual(protocol.protocol_name, "Test Protocol")
        self.assertEqual(protocol.version, "1.0.0")
        self.assertEqual(protocol.category, "Mechanical")

    def test_get_protocol_by_id(self):
        """Test retrieving a protocol by ID."""
        loader = ProtocolLoader()
        loader.import_to_database(self.protocol_data, self.session)

        protocol = ProtocolLoader.get_protocol_by_id("TEST-001", self.session)

        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.protocol_id, "TEST-001")

    def test_list_protocols(self):
        """Test listing all protocols."""
        loader = ProtocolLoader()
        loader.import_to_database(self.protocol_data, self.session)

        protocols = ProtocolLoader.list_protocols(self.session)

        self.assertEqual(len(protocols), 1)
        self.assertEqual(protocols[0].protocol_id, "TEST-001")

    def test_list_protocols_by_category(self):
        """Test listing protocols filtered by category."""
        loader = ProtocolLoader()
        loader.import_to_database(self.protocol_data, self.session)

        # Add another protocol with different category
        other_data = self.protocol_data.copy()
        other_data["protocol_id"] = "TEST-002"
        other_data["category"] = "Electrical"
        loader.import_to_database(other_data, self.session)

        mechanical = ProtocolLoader.list_protocols(self.session, category="Mechanical")
        electrical = ProtocolLoader.list_protocols(self.session, category="Electrical")

        self.assertEqual(len(mechanical), 1)
        self.assertEqual(len(electrical), 1)
        self.assertEqual(mechanical[0].protocol_id, "TEST-001")
        self.assertEqual(electrical[0].protocol_id, "TEST-002")


if __name__ == '__main__':
    unittest.main()
