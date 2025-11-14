"""
Unit tests for Protocol Loader
"""
import unittest
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.protocol_loader import ProtocolLoader


class TestProtocolLoader(unittest.TestCase):
    """Test cases for ProtocolLoader class"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = ProtocolLoader()

    def test_load_trop001_protocol(self):
        """Test loading TROP-001 protocol"""
        protocol = self.loader.load_protocol("TROP-001")

        # Verify basic fields
        self.assertEqual(protocol['protocol_id'], "TROP-001")
        self.assertEqual(protocol['name'], "Tropical Climate Test")
        self.assertEqual(protocol['category'], "Environmental")
        self.assertIn('version', protocol)

    def test_protocol_has_required_fields(self):
        """Test that protocol has all required fields"""
        protocol = self.loader.load_protocol("TROP-001")

        required_fields = [
            'protocol_id',
            'version',
            'name',
            'category',
            'test_sequence',
            'acceptance_criteria'
        ]

        for field in required_fields:
            self.assertIn(field, protocol, f"Missing required field: {field}")

    def test_protocol_test_sequence(self):
        """Test protocol test sequence structure"""
        protocol = self.loader.load_protocol("TROP-001")

        test_sequence = protocol['test_sequence']

        # Verify sequence has required fields
        self.assertIn('steps', test_sequence)
        self.assertIn('total_cycles', test_sequence)
        self.assertIn('total_test_duration', test_sequence)

        # Verify steps
        steps = test_sequence['steps']
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0, "Test sequence must have at least one step")

        # Verify first step structure
        first_step = steps[0]
        self.assertIn('step', first_step)
        self.assertIn('name', first_step)
        self.assertIn('duration', first_step)

    def test_protocol_acceptance_criteria(self):
        """Test protocol acceptance criteria"""
        protocol = self.loader.load_protocol("TROP-001")

        criteria = protocol['acceptance_criteria']

        # Verify criteria structure
        self.assertIn('visual', criteria)
        self.assertIn('electrical', criteria)

        # Verify electrical criteria
        electrical = criteria['electrical']
        self.assertIn('power_degradation', electrical)

    def test_list_protocols(self):
        """Test listing all protocols"""
        protocols = self.loader.list_protocols()

        self.assertIsInstance(protocols, list)
        self.assertGreater(len(protocols), 0, "Should find at least one protocol")

        # Verify protocol structure
        trop001 = next((p for p in protocols if p['protocol_id'] == 'TROP-001'), None)
        self.assertIsNotNone(trop001, "TROP-001 should be in the list")
        self.assertEqual(trop001['name'], "Tropical Climate Test")

    def test_list_protocols_by_category(self):
        """Test filtering protocols by category"""
        protocols = self.loader.list_protocols(category="Environmental")

        self.assertIsInstance(protocols, list)
        self.assertGreater(len(protocols), 0)

        # All protocols should be Environmental
        for protocol in protocols:
            self.assertEqual(protocol['category'], "Environmental")

    def test_get_protocol_info(self):
        """Test getting protocol summary info"""
        info = self.loader.get_protocol_info("TROP-001")

        # Verify info structure
        self.assertEqual(info['protocol_id'], "TROP-001")
        self.assertEqual(info['name'], "Tropical Climate Test")
        self.assertIn('version', info)
        self.assertIn('total_duration', info)
        self.assertIn('sample_size', info)

    def test_load_nonexistent_protocol(self):
        """Test loading non-existent protocol raises error"""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_protocol("NONEXISTENT-999")

    def test_protocol_json_valid(self):
        """Test that protocol JSON is valid"""
        protocol_file = Path(__file__).parent.parent.parent / "protocols" / "climate" / "trop-001.json"

        with open(protocol_file, 'r') as f:
            data = json.load(f)

        # Should not raise any exceptions
        self.assertIsInstance(data, dict)


if __name__ == '__main__':
    unittest.main()
