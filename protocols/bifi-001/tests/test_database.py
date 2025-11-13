"""
Unit tests for DatabaseManager
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import DatabaseManager
from db.models import BifacialTest, IVMeasurement, BifacialResult, QualityCheck


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class"""

    def setUp(self):
        """Set up test fixtures with temporary database"""
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db_url = f"sqlite:///{self.db_path}"

        self.db = DatabaseManager(self.db_url)
        self.db.create_tables()

        # Test data
        self.test_data = {
            "metadata": {
                "protocol_name": "BIFI-001 Bifacial Performance",
                "standard": "IEC 60904-1-2",
                "version": "1.0.0",
                "test_date": datetime.utcnow().isoformat() + "Z",
                "operator": "Test Engineer",
                "facility": "Test Lab"
            },
            "device_under_test": {
                "device_id": "TEST-001",
                "manufacturer": "Test Solar",
                "model": "BiModule-500",
                "serial_number": "SN-001",
                "technology": "mono-Si",
                "rated_power_front": 500.0,
                "rated_power_rear": 350.0,
                "bifaciality_factor": 0.70,
                "area_front": 25000.0,
                "area_rear": 25000.0
            },
            "test_conditions": {
                "front_irradiance": {"value": 1000.0, "tolerance": 2.0, "spectrum": "AM1.5G"},
                "rear_irradiance": {"value": 150.0, "tolerance": 2.0, "spectrum": "AM1.5G"},
                "temperature": {"value": 25.0, "tolerance": 2.0},
                "stc_conditions": True
            },
            "measurements": {
                "front_side": {
                    "isc": 10.0,
                    "voc": 45.0,
                    "pmax": 350.0,
                    "imp": 9.5,
                    "vmp": 36.8,
                    "fill_factor": 0.78,
                    "efficiency": 14.0,
                    "iv_curve": [{"voltage": i, "current": 10-i} for i in range(10)]
                },
                "rear_side": {
                    "isc": 7.0,
                    "voc": 43.0,
                    "pmax": 245.0,
                    "imp": 6.7,
                    "vmp": 36.6,
                    "fill_factor": 0.81,
                    "efficiency": 9.8,
                    "iv_curve": [{"voltage": i, "current": 7-i*0.7} for i in range(10)]
                }
            }
        }

    def tearDown(self):
        """Clean up temporary database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_tables(self):
        """Test table creation"""
        # Tables should be created in setUp
        # Test by trying to query
        with self.db.get_session() as session:
            count = session.query(BifacialTest).count()
            self.assertEqual(count, 0)

    def test_create_test(self):
        """Test creating a test record"""
        test = self.db.create_test(self.test_data)

        self.assertIsNotNone(test)
        self.assertIsNotNone(test.id)
        self.assertEqual(test.device_id, "TEST-001")
        self.assertEqual(test.manufacturer, "Test Solar")
        self.assertEqual(test.front_irradiance, 1000.0)

    def test_get_test(self):
        """Test retrieving a test by ID"""
        created_test = self.db.create_test(self.test_data)

        retrieved_test = self.db.get_test(created_test.id)

        self.assertIsNotNone(retrieved_test)
        self.assertEqual(retrieved_test.id, created_test.id)
        self.assertEqual(retrieved_test.device_id, "TEST-001")

    def test_get_test_nonexistent(self):
        """Test retrieving non-existent test"""
        test = self.db.get_test(99999)
        self.assertIsNone(test)

    def test_get_tests_by_device(self):
        """Test retrieving tests by device ID"""
        # Create multiple tests for same device
        self.db.create_test(self.test_data)

        test_data_2 = self.test_data.copy()
        test_data_2["device_under_test"] = self.test_data["device_under_test"].copy()
        test_data_2["device_under_test"]["serial_number"] = "SN-002"
        self.db.create_test(test_data_2)

        tests = self.db.get_tests_by_device("TEST-001")

        self.assertEqual(len(tests), 2)
        self.assertTrue(all(t.device_id == "TEST-001" for t in tests))

    def test_get_tests_by_serial(self):
        """Test retrieving tests by serial number"""
        self.db.create_test(self.test_data)

        tests = self.db.get_tests_by_serial("SN-001")

        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0].serial_number, "SN-001")

    def test_update_test_status(self):
        """Test updating test status"""
        test = self.db.create_test(self.test_data)

        self.db.update_test_status(test.id, "completed", "pass")

        updated_test = self.db.get_test(test.id)
        self.assertEqual(updated_test.status, "completed")
        self.assertEqual(updated_test.pass_fail_status, "pass")

    def test_add_iv_measurement(self):
        """Test adding I-V measurement"""
        test = self.db.create_test(self.test_data)

        measurement_data = self.test_data["measurements"]["front_side"]
        measurement_data["irradiance"] = 1000.0
        measurement_data["temperature"] = 25.0

        iv_meas = self.db.add_iv_measurement(test.id, "front", measurement_data)

        self.assertIsNotNone(iv_meas)
        self.assertEqual(iv_meas.test_id, test.id)
        self.assertEqual(iv_meas.side, "front")
        self.assertEqual(iv_meas.pmax, 350.0)

    def test_get_measurements(self):
        """Test retrieving measurements"""
        test = self.db.create_test(self.test_data)

        # Add front measurement
        front_data = self.test_data["measurements"]["front_side"].copy()
        front_data["irradiance"] = 1000.0
        self.db.add_iv_measurement(test.id, "front", front_data)

        # Add rear measurement
        rear_data = self.test_data["measurements"]["rear_side"].copy()
        rear_data["irradiance"] = 150.0
        self.db.add_iv_measurement(test.id, "rear", rear_data)

        # Get all measurements
        all_meas = self.db.get_measurements(test.id)
        self.assertEqual(len(all_meas), 2)

        # Get front only
        front_meas = self.db.get_measurements(test.id, side="front")
        self.assertEqual(len(front_meas), 1)
        self.assertEqual(front_meas[0].side, "front")

    def test_add_bifacial_result(self):
        """Test adding bifacial results"""
        test = self.db.create_test(self.test_data)

        result_data = {
            "measured_bifaciality": 0.70,
            "bifacial_gain": 45.5,
            "equivalent_front_efficiency": 16.2,
            "bifaciality_deviation": 0.0,
            "front_power_deviation": -30.0,
            "rear_power_deviation": -30.0
        }

        result = self.db.add_bifacial_result(test.id, result_data)

        self.assertIsNotNone(result)
        self.assertEqual(result.test_id, test.id)
        self.assertAlmostEqual(result.measured_bifaciality, 0.70)

    def test_get_bifacial_result(self):
        """Test retrieving bifacial results"""
        test = self.db.create_test(self.test_data)

        result_data = {
            "measured_bifaciality": 0.70,
            "bifacial_gain": 45.5,
            "equivalent_front_efficiency": 16.2
        }

        self.db.add_bifacial_result(test.id, result_data)

        result = self.db.get_bifacial_result(test.id)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.measured_bifaciality, 0.70)

    def test_add_quality_check(self):
        """Test adding quality check"""
        test = self.db.create_test(self.test_data)

        check_data = {
            "check_name": "Schema Validation",
            "check_type": "validation",
            "status": "pass",
            "message": "All checks passed"
        }

        check = self.db.add_quality_check(test.id, check_data)

        self.assertIsNotNone(check)
        self.assertEqual(check.check_name, "Schema Validation")
        self.assertEqual(check.status, "pass")

    def test_get_quality_checks(self):
        """Test retrieving quality checks"""
        test = self.db.create_test(self.test_data)

        # Add multiple checks
        for i in range(3):
            check_data = {
                "check_name": f"Check {i}",
                "status": "pass",
                "message": f"Check {i} passed"
            }
            self.db.add_quality_check(test.id, check_data)

        checks = self.db.get_quality_checks(test.id)

        self.assertEqual(len(checks), 3)

    def test_add_calibration_record(self):
        """Test adding calibration record"""
        cal_data = {
            "equipment_id": "REF-CELL-001",
            "equipment_type": "reference_cell_front",
            "equipment_name": "Front Reference Cell",
            "calibration_date": "2025-01-01",
            "next_calibration_due": "2026-01-01",
            "calibration_authority": "NREL",
            "certificate_number": "CERT-2025-001",
            "is_current": True
        }

        record = self.db.add_calibration_record(cal_data)

        self.assertIsNotNone(record)
        self.assertEqual(record.equipment_id, "REF-CELL-001")

    def test_get_current_calibration(self):
        """Test retrieving current calibration"""
        cal_data = {
            "equipment_id": "REF-CELL-001",
            "equipment_type": "reference_cell_front",
            "calibration_date": "2025-01-01",
            "next_calibration_due": "2026-01-01",
            "is_current": True
        }

        self.db.add_calibration_record(cal_data)

        current_cal = self.db.get_current_calibration("REF-CELL-001")

        self.assertIsNotNone(current_cal)
        self.assertTrue(current_cal.is_current)

    def test_check_calibration_status(self):
        """Test checking calibration status"""
        # Future calibration due date
        cal_data = {
            "equipment_id": "REF-CELL-001",
            "equipment_type": "reference_cell_front",
            "calibration_date": "2025-01-01",
            "next_calibration_due": "2026-12-31",
            "is_current": True
        }

        self.db.add_calibration_record(cal_data)

        status = self.db.check_calibration_status("REF-CELL-001")

        self.assertIn("status", status)
        # Should be "valid" since due date is in future
        self.assertIn(status["status"], ["valid", "warning"])

    def test_get_test_summary(self):
        """Test getting comprehensive test summary"""
        test = self.db.create_test(self.test_data)

        # Add measurements
        front_data = self.test_data["measurements"]["front_side"].copy()
        front_data["irradiance"] = 1000.0
        self.db.add_iv_measurement(test.id, "front", front_data)

        rear_data = self.test_data["measurements"]["rear_side"].copy()
        rear_data["irradiance"] = 150.0
        self.db.add_iv_measurement(test.id, "rear", rear_data)

        # Add bifacial results
        result_data = {"measured_bifaciality": 0.70, "bifacial_gain": 45.5}
        self.db.add_bifacial_result(test.id, result_data)

        # Add QC check
        check_data = {"check_name": "Test Check", "status": "pass"}
        self.db.add_quality_check(test.id, check_data)

        # Get summary
        summary = self.db.get_test_summary(test.id)

        self.assertIsNotNone(summary)
        self.assertIn("test", summary)
        self.assertIn("measurements", summary)
        self.assertIn("bifacial", summary)
        self.assertIn("quality_checks", summary)

        self.assertEqual(summary["test"]["device_id"], "TEST-001")
        self.assertEqual(summary["measurements"]["front"]["pmax"], 350.0)
        self.assertAlmostEqual(summary["bifacial"]["bifaciality"], 0.70)

    def test_export_test_data(self):
        """Test exporting test data"""
        test = self.db.create_test(self.test_data)

        exported = self.db.export_test_data(test.id)

        self.assertIsNotNone(exported)
        self.assertEqual(exported["device_under_test"]["device_id"], "TEST-001")


if __name__ == '__main__':
    unittest.main()
