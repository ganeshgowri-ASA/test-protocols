"""
Unit tests for database models and operations
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from db.database import Database
from db.models import (
    WindLoadTest, PreTestMeasurement, PostTestMeasurement,
    CycleMeasurement, TestAttachment, TestStatus, LoadType
)


class TestDatabaseModels(unittest.TestCase):
    """Test database models"""

    def setUp(self):
        """Set up test database"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db = Database(f"sqlite:///{self.temp_db.name}")
        self.db.create_tables()

    def tearDown(self):
        """Clean up test database"""
        self.db.drop_tables()
        Path(self.temp_db.name).unlink()

    def test_create_wind_load_test(self):
        """Test creating a wind load test record"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-001",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-001",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.CYCLIC,
                pressure=2400.0,
                duration=60,
                cycles=3
            )
            session.add(test)

        # Query the test
        with self.db.session_scope() as session:
            retrieved = session.query(WindLoadTest).filter_by(test_id="TEST-001").first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.operator, "Test Operator")
            self.assertEqual(retrieved.load_type, LoadType.CYCLIC)

    def test_create_pre_test_measurement(self):
        """Test creating pre-test measurement"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-002",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-002",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.POSITIVE,
                pressure=2400.0,
                duration=60,
                cycles=3
            )
            session.add(test)
            session.flush()

            pre_test = PreTestMeasurement(
                test_id=test.id,
                visual_inspection="No defects",
                voc=48.5,
                isc=10.2,
                vmp=40.0,
                imp=10.0,
                pmax=400.0,
                insulation_resistance=500.0
            )
            session.add(pre_test)

        # Query the measurement
        with self.db.session_scope() as session:
            test = session.query(WindLoadTest).filter_by(test_id="TEST-002").first()
            self.assertIsNotNone(test.pre_test_measurements)
            self.assertEqual(test.pre_test_measurements.pmax, 400.0)

    def test_create_cycle_measurements(self):
        """Test creating multiple cycle measurements"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-003",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-003",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.CYCLIC,
                pressure=2400.0,
                duration=60,
                cycles=3
            )
            session.add(test)
            session.flush()

            for i in range(1, 4):
                cycle = CycleMeasurement(
                    test_id=test.id,
                    cycle_number=i,
                    actual_pressure=2400.0,
                    deflection_center=15.5,
                    deflection_edges=[10.2, 11.5, 10.8, 11.0]
                )
                session.add(cycle)

        # Query the measurements
        with self.db.session_scope() as session:
            test = session.query(WindLoadTest).filter_by(test_id="TEST-003").first()
            self.assertEqual(len(test.cycle_measurements), 3)
            self.assertEqual(test.cycle_measurements[0].cycle_number, 1)

    def test_cascade_delete(self):
        """Test cascade delete of related records"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-004",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-004",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.CYCLIC,
                pressure=2400.0,
                duration=60,
                cycles=3
            )
            session.add(test)
            session.flush()

            pre_test = PreTestMeasurement(
                test_id=test.id,
                visual_inspection="No defects",
                voc=48.5,
                isc=10.2,
                vmp=40.0,
                imp=10.0,
                pmax=400.0,
                insulation_resistance=500.0
            )
            session.add(pre_test)

            cycle = CycleMeasurement(
                test_id=test.id,
                cycle_number=1,
                actual_pressure=2400.0,
                deflection_center=15.5,
                deflection_edges=[10.2, 11.5, 10.8, 11.0]
            )
            session.add(cycle)

        # Delete test and verify cascade
        with self.db.session_scope() as session:
            test = session.query(WindLoadTest).filter_by(test_id="TEST-004").first()
            session.delete(test)

        with self.db.session_scope() as session:
            pre_test_count = session.query(PreTestMeasurement).count()
            cycle_count = session.query(CycleMeasurement).count()
            self.assertEqual(pre_test_count, 0)
            self.assertEqual(cycle_count, 0)

    def test_unique_constraints(self):
        """Test unique constraints"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-005",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-005",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.CYCLIC,
                pressure=2400.0,
                duration=60,
                cycles=3
            )
            session.add(test)

        # Try to create duplicate test_id
        with self.assertRaises(Exception):
            with self.db.session_scope() as session:
                duplicate = WindLoadTest(
                    test_id="TEST-005",  # Duplicate
                    operator="Another Operator",
                    standard="IEC 61215-2:2021",
                    sample_id="SAMPLE-006",
                    manufacturer="Test Manufacturer",
                    model="TEST-400",
                    load_type=LoadType.POSITIVE,
                    pressure=2400.0,
                    duration=60,
                    cycles=3
                )
                session.add(duplicate)

    def test_test_status_enum(self):
        """Test TestStatus enum"""
        with self.db.session_scope() as session:
            test = WindLoadTest(
                test_id="TEST-006",
                operator="Test Operator",
                standard="IEC 61215-2:2021",
                sample_id="SAMPLE-006",
                manufacturer="Test Manufacturer",
                model="TEST-400",
                load_type=LoadType.CYCLIC,
                pressure=2400.0,
                duration=60,
                cycles=3,
                test_status=TestStatus.PASS
            )
            session.add(test)

        with self.db.session_scope() as session:
            test = session.query(WindLoadTest).filter_by(test_id="TEST-006").first()
            self.assertEqual(test.test_status, TestStatus.PASS)


if __name__ == '__main__':
    unittest.main()
