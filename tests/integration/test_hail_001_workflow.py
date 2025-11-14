"""
Integration tests for HAIL-001 complete workflow
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.protocols.loader import ProtocolLoader
from src.protocols.hail_001 import HAIL001Protocol
from src.analysis.database import TestDatabase
from src.analysis.reporting import ReportGenerator


class TestHAIL001Workflow(unittest.TestCase):
    """Test complete HAIL-001 workflow integration"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        # Load protocol
        protocols_dir = Path(__file__).parent.parent.parent / "protocols"
        loader = ProtocolLoader(str(protocols_dir))
        protocol_data = loader.load_protocol("HAIL-001")
        self.protocol = HAIL001Protocol(protocol_data)

        # Initialize database
        self.db = TestDatabase(self.db_path)

        # Create tables (simplified version for testing)
        self._create_test_tables()

    def tearDown(self):
        """Clean up test fixtures"""
        self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _create_test_tables(self):
        """Create simplified test tables"""
        cursor = self.db.conn.cursor()

        # Simplified schema for testing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hail_test_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_id TEXT NOT NULL,
                protocol_version TEXT NOT NULL,
                test_date TEXT NOT NULL,
                test_operator TEXT,
                facility TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_modules (
                module_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                manufacturer TEXT,
                model TEXT,
                serial_number TEXT,
                nameplate_power REAL,
                length_mm REAL,
                width_mm REAL,
                thickness_mm REAL,
                weight_kg REAL,
                cell_technology TEXT,
                FOREIGN KEY (session_id) REFERENCES hail_test_sessions(session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pre_test_measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                measurement_timestamp TEXT,
                pmax_initial REAL,
                voc REAL,
                isc REAL,
                vmp REAL,
                imp REAL,
                fill_factor REAL,
                insulation_resistance_initial REAL,
                FOREIGN KEY (session_id) REFERENCES hail_test_sessions(session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS impact_test_data (
                impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                impact_number INTEGER,
                impact_location_id INTEGER,
                location_x REAL,
                location_y REAL,
                location_description TEXT,
                ice_ball_diameter_mm REAL,
                ice_ball_weight_g REAL,
                ice_ball_temperature_c REAL,
                time_delta_seconds INTEGER,
                target_velocity_kmh REAL,
                actual_velocity_kmh REAL,
                velocity_deviation_kmh REAL,
                open_circuit_detected INTEGER,
                visual_damage TEXT,
                FOREIGN KEY (session_id) REFERENCES hail_test_sessions(session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_test_measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                measurement_timestamp TEXT,
                pmax_final REAL,
                voc REAL,
                isc REAL,
                vmp REAL,
                imp REAL,
                fill_factor REAL,
                insulation_resistance_final REAL,
                front_glass_cracks INTEGER,
                cell_cracks INTEGER,
                backsheet_cracks INTEGER,
                delamination INTEGER,
                junction_box_damage INTEGER,
                frame_damage INTEGER,
                FOREIGN KEY (session_id) REFERENCES hail_test_sessions(session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                pmax_initial REAL,
                pmax_final REAL,
                power_degradation_percent REAL,
                power_degradation_watts REAL,
                velocity_mean REAL,
                velocity_std REAL,
                velocity_min REAL,
                velocity_max REAL,
                time_compliance_count INTEGER,
                time_compliance_rate REAL,
                open_circuit_count INTEGER,
                insulation_initial REAL,
                insulation_final REAL,
                insulation_degradation_percent REAL,
                overall_result TEXT,
                power_criterion_pass INTEGER,
                visual_criterion_pass INTEGER,
                insulation_criterion_pass INTEGER,
                open_circuit_criterion_pass INTEGER,
                FOREIGN KEY (session_id) REFERENCES hail_test_sessions(session_id)
            )
        """)

        self.db.conn.commit()

    def test_complete_workflow_passing_test(self):
        """Test complete workflow with passing test results"""
        # Step 1: Create test session
        session_id = self.db.create_session(
            protocol_id="HAIL-001",
            protocol_version="1.0.0",
            test_date=datetime.now().isoformat(),
            test_operator="Test Engineer",
            facility="Test Lab"
        )

        self.assertIsNotNone(session_id)
        self.assertGreater(session_id, 0)

        # Step 2: Insert module information
        module_data = {
            'manufacturer': 'Test Manufacturer',
            'model': 'TEST-300W',
            'serial_number': 'TEST-2024-001',
            'nameplate_power': 300.0,
            'dimensions': {
                'length_mm': 1650.0,
                'width_mm': 992.0,
                'thickness_mm': 35.0
            },
            'weight_kg': 18.5,
            'cell_technology': 'Monocrystalline'
        }

        module_id = self.db.insert_module_info(session_id, module_data)
        self.assertGreater(module_id, 0)

        # Step 3: Insert pre-test measurements
        pre_test_data = {
            'Pmax_initial': 300.0,
            'Voc': 40.5,
            'Isc': 9.2,
            'Vmp': 33.6,
            'Imp': 8.93,
            'fill_factor': 0.804,
            'insulation_resistance_initial': 500.0
        }

        pre_test_id = self.db.insert_pre_test_measurement(session_id, pre_test_data)
        self.assertGreater(pre_test_id, 0)

        # Step 4: Insert impact test data (11 impacts)
        impact_locations = self.protocol.generate_impact_locations()

        for i, location in enumerate(impact_locations, 1):
            impact_data = {
                'impact_number': i,
                'impact_location': location['id'],
                'location_x': location['x'],
                'location_y': location['y'],
                'location_description': location['description'],
                'ice_ball_diameter_mm': 25.0,
                'ice_ball_weight_g': 7.53,
                'ice_ball_temperature_c': -4.0,
                'time_delta_seconds': 45 + i,
                'target_velocity_kmh': 80.0,
                'actual_velocity_kmh': 80.0 + (i % 3 - 1) * 0.5,
                'velocity_deviation_kmh': (i % 3 - 1) * 0.5,
                'open_circuit_detected': False,
                'visual_damage': ''
            }

            impact_id = self.db.insert_impact_data(session_id, impact_data)
            self.assertGreater(impact_id, 0)

        # Step 5: Insert post-test measurements
        post_test_data = {
            'Pmax_final': 295.0,  # ~1.67% degradation (passing)
            'Voc': 40.3,
            'Isc': 9.1,
            'Vmp': 33.5,
            'Imp': 8.85,
            'fill_factor': 0.802,
            'insulation_resistance_final': 490.0,
            'visual_defects': {
                'front_glass_cracks': False,
                'cell_cracks': False,
                'backsheet_cracks': False,
                'delamination': False,
                'junction_box_damage': False,
                'frame_damage': False
            }
        }

        post_test_id = self.db.insert_post_test_measurement(session_id, post_test_data)
        self.assertGreater(post_test_id, 0)

        # Step 6: Perform analysis
        test_data = {
            'pre_test_data': pre_test_data,
            'test_execution_data': {
                'impacts': [
                    {
                        'impact_number': i,
                        'actual_velocity_kmh': 80.0 + (i % 3 - 1) * 0.5,
                        'time_delta_seconds': 45 + i,
                        'open_circuit_detected': False
                    }
                    for i in range(1, 12)
                ]
            },
            'post_test_data': post_test_data
        }

        # Validate
        is_valid, errors = self.protocol.validate_test_data(test_data)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

        # Analyze
        analysis_results = self.protocol.analyze_results(test_data)
        self.assertIn('power_analysis', analysis_results)

        # Evaluate
        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)
        self.assertEqual(pass_fail_results['overall_result'], 'PASS')

        # Step 7: Save results to database
        combined_results = {
            'power_analysis': analysis_results['power_analysis'],
            'impact_analysis': analysis_results['impact_analysis'],
            'insulation_analysis': analysis_results['insulation_analysis'],
            'pass_fail': pass_fail_results
        }

        result_id = self.db.insert_test_results(session_id, combined_results)
        self.assertGreater(result_id, 0)

        # Step 8: Update session status
        self.db.update_session_status(session_id, 'passed')

        # Step 9: Generate report
        report_gen = ReportGenerator(
            protocol_data=self.protocol.protocol_data,
            test_data={'test_date': datetime.now().isoformat(), 'module_info': module_data},
            analysis_results=analysis_results,
            pass_fail_results=pass_fail_results
        )

        markdown_report = report_gen.generate_markdown_report()
        self.assertIn('PASS', markdown_report)
        self.assertIn('HAIL-001', markdown_report)

    def test_workflow_with_failing_test(self):
        """Test workflow with failing test results"""
        session_id = self.db.create_session(
            protocol_id="HAIL-001",
            protocol_version="1.0.0",
            test_date=datetime.now().isoformat(),
            test_operator="Test Engineer",
            facility="Test Lab"
        )

        # Insert module info
        module_data = {
            'manufacturer': 'Test Manufacturer',
            'model': 'TEST-300W',
            'serial_number': 'TEST-2024-002',
            'nameplate_power': 300.0,
            'dimensions': {'length_mm': 1650.0, 'width_mm': 992.0, 'thickness_mm': 35.0},
            'weight_kg': 18.5,
            'cell_technology': 'Monocrystalline'
        }
        self.db.insert_module_info(session_id, module_data)

        # Pre-test data
        pre_test_data = {
            'Pmax_initial': 300.0,
            'Voc': 40.5,
            'Isc': 9.2,
            'insulation_resistance_initial': 500.0
        }
        self.db.insert_pre_test_measurement(session_id, pre_test_data)

        # Impact data with open circuit detection
        for i in range(1, 12):
            impact_data = {
                'impact_number': i,
                'actual_velocity_kmh': 80.0,
                'time_delta_seconds': 50,
                'open_circuit_detected': i == 5,  # Fail on impact 5
                'visual_damage': 'Crack observed' if i == 5 else ''
            }
            self.db.insert_impact_data(session_id, impact_data)

        # Post-test data with excessive degradation
        post_test_data = {
            'Pmax_final': 270.0,  # 10% degradation (failing)
            'Voc': 39.0,
            'Isc': 8.5,
            'insulation_resistance_final': 480.0,
            'visual_defects': {
                'front_glass_cracks': True,  # Failing criterion
                'cell_cracks': False,
                'backsheet_cracks': False,
                'delamination': False,
                'junction_box_damage': False,
                'frame_damage': False
            }
        }
        self.db.insert_post_test_measurement(session_id, post_test_data)

        # Analyze
        test_data = {
            'pre_test_data': pre_test_data,
            'test_execution_data': {
                'impacts': [
                    {
                        'impact_number': i,
                        'actual_velocity_kmh': 80.0,
                        'time_delta_seconds': 50,
                        'open_circuit_detected': i == 5
                    }
                    for i in range(1, 12)
                ]
            },
            'post_test_data': post_test_data
        }

        analysis_results = self.protocol.analyze_results(test_data)
        pass_fail_results = self.protocol.evaluate_pass_fail(analysis_results)

        # Should fail overall
        self.assertEqual(pass_fail_results['overall_result'], 'FAIL')

        # Check specific failures
        self.assertFalse(pass_fail_results['criteria']['power_degradation']['pass'])
        self.assertFalse(pass_fail_results['criteria']['visual_inspection']['pass'])
        self.assertFalse(pass_fail_results['criteria']['open_circuit']['pass'])


if __name__ == '__main__':
    unittest.main()
