"""
Integration tests for Database operations
"""
import unittest
from pathlib import Path
import sys
import tempfile
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_manager import DatabaseManager


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations"""

    def setUp(self):
        """Set up test database"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()

        self.db = DatabaseManager(self.temp_db.name)
        self.db.initialize_database()

    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_database_initialization(self):
        """Test database initialization"""
        conn = self.db.connect()
        cursor = conn.cursor()

        # Verify tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            'alerts',
            'audit_log',
            'deviations',
            'electrical_measurements',
            'environmental_measurements',
            'inspection_photos',
            'insulation_tests',
            'modules',
            'protocols',
            'system_config',
            'test_results',
            'test_session_modules',
            'test_sessions',
            'visual_inspections'
        ]

        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not found")

    def test_create_test_session(self):
        """Test creating a test session"""
        test_id = "TEST-001"
        protocol_id = "TROP-001"
        protocol_version = "1.0.0"
        operator = "John Doe"

        session_id = self.db.create_test_session(
            test_id,
            protocol_id,
            protocol_version,
            operator,
            chamber_id="CHAMBER-01"
        )

        self.assertIsInstance(session_id, int)
        self.assertGreater(session_id, 0)

        # Verify session was created
        session = self.db.get_test_session(test_id)
        self.assertIsNotNone(session)
        self.assertEqual(session['test_id'], test_id)
        self.assertEqual(session['protocol_id'], protocol_id)
        self.assertEqual(session['operator'], operator)

    def test_add_module(self):
        """Test adding a module"""
        module_id = self.db.add_module(
            serial_number="MOD001",
            manufacturer="Test Manufacturer",
            model="TEST-300",
            module_type="Crystalline Silicon",
            rated_power=300.0,
            technology="PERC"
        )

        self.assertIsInstance(module_id, int)
        self.assertGreater(module_id, 0)

    def test_add_duplicate_module(self):
        """Test adding duplicate module returns existing ID"""
        # Add module first time
        module_id_1 = self.db.add_module(
            serial_number="MOD001",
            manufacturer="Test Manufacturer",
            model="TEST-300",
            module_type="Crystalline Silicon",
            rated_power=300.0
        )

        # Add same module again
        module_id_2 = self.db.add_module(
            serial_number="MOD001",
            manufacturer="Test Manufacturer",
            model="TEST-300",
            module_type="Crystalline Silicon",
            rated_power=300.0
        )

        # Should return same ID
        self.assertEqual(module_id_1, module_id_2)

    def test_link_module_to_test(self):
        """Test linking module to test session"""
        # Create test session
        session_id = self.db.create_test_session(
            "TEST-001",
            "TROP-001",
            "1.0.0",
            "John Doe"
        )

        # Add module
        module_id = self.db.add_module(
            serial_number="MOD001",
            manufacturer="Test Manufacturer",
            model="TEST-300",
            module_type="Crystalline Silicon",
            rated_power=300.0
        )

        # Link module to test
        self.db.link_module_to_test(session_id, module_id, position=1)

        # Verify link (no exception means success)
        # Further verification would require querying the junction table

    def test_record_electrical_measurement(self):
        """Test recording electrical measurement"""
        # Create test session and module
        session_id = self.db.create_test_session(
            "TEST-001",
            "TROP-001",
            "1.0.0",
            "John Doe"
        )

        module_id = self.db.add_module(
            serial_number="MOD001",
            manufacturer="Test Manufacturer",
            model="TEST-300",
            module_type="Crystalline Silicon",
            rated_power=300.0
        )

        # Record measurement
        measurement_id = self.db.record_electrical_measurement(
            test_session_id=session_id,
            module_id=module_id,
            phase="pre_test",
            pmax=300.0,
            voc=40.0,
            isc=9.0,
            vmpp=35.0,
            impp=8.57,
            fill_factor=83.3
        )

        self.assertIsInstance(measurement_id, int)
        self.assertGreater(measurement_id, 0)

        # Verify measurement was recorded
        measurements = self.db.get_test_measurements(session_id, 'electrical')
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0]['pmax'], 300.0)

    def test_record_environmental_measurement(self):
        """Test recording environmental measurement"""
        session_id = self.db.create_test_session(
            "TEST-001",
            "TROP-001",
            "1.0.0",
            "John Doe"
        )

        measurement_id = self.db.record_environmental_measurement(
            test_session_id=session_id,
            step=1,
            cycle=1,
            temperature=85.0,
            relative_humidity=85.0,
            sensor_id="SENSOR-01",
            target_temperature=85.0,
            target_humidity=85.0
        )

        self.assertIsInstance(measurement_id, int)
        self.assertGreater(measurement_id, 0)

        # Verify measurement was recorded
        measurements = self.db.get_test_measurements(session_id, 'environmental')
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0]['temperature'], 85.0)

    def test_record_alert(self):
        """Test recording an alert"""
        session_id = self.db.create_test_session(
            "TEST-001",
            "TROP-001",
            "1.0.0",
            "John Doe"
        )

        alert_id = self.db.record_alert(
            test_session_id=session_id,
            severity="WARNING",
            message="Temperature out of tolerance",
            parameter="temperature",
            value=88.0,
            step=1,
            cycle=1
        )

        self.assertIsInstance(alert_id, int)
        self.assertGreater(alert_id, 0)

    def test_update_test_status(self):
        """Test updating test status"""
        session_id = self.db.create_test_session(
            "TEST-001",
            "TROP-001",
            "1.0.0",
            "John Doe"
        )

        # Update status
        self.db.update_test_status(
            session_id,
            "completed",
            end_time=datetime.now(),
            pass_fail="PASS"
        )

        # Verify update
        session = self.db.get_test_session("TEST-001")
        self.assertEqual(session['status'], "completed")
        self.assertEqual(session['pass_fail'], "PASS")
        self.assertIsNotNone(session['end_time'])

    def test_context_manager(self):
        """Test using database manager as context manager"""
        with DatabaseManager(self.temp_db.name) as db:
            session_id = db.create_test_session(
                "TEST-001",
                "TROP-001",
                "1.0.0",
                "John Doe"
            )
            self.assertGreater(session_id, 0)

        # Connection should be closed after context


if __name__ == '__main__':
    unittest.main()
