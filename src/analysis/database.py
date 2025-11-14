"""
Database operations for test protocol data
"""

from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime
from pathlib import Path


class TestDatabase:
    """Database interface for test protocol data"""

    def __init__(self, db_path: str = "test_protocols.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self) -> None:
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_session(self, protocol_id: str, protocol_version: str,
                      test_date: str, test_operator: str, facility: str = "") -> int:
        """
        Create new test session

        Args:
            protocol_id: Protocol identifier
            protocol_version: Protocol version
            test_date: Test date (ISO format)
            test_operator: Operator name
            facility: Facility name

        Returns:
            Session ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO hail_test_sessions
            (protocol_id, protocol_version, test_date, test_operator, facility, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (protocol_id, protocol_version, test_date, test_operator, facility, 'in_progress'))

        self.conn.commit()
        return cursor.lastrowid

    def insert_module_info(self, session_id: int, module_data: Dict[str, Any]) -> int:
        """
        Insert module information

        Args:
            session_id: Test session ID
            module_data: Module information dictionary

        Returns:
            Module ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO test_modules
            (session_id, manufacturer, model, serial_number, nameplate_power,
             length_mm, width_mm, thickness_mm, weight_kg, cell_technology)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            module_data.get('manufacturer', ''),
            module_data.get('model', ''),
            module_data.get('serial_number', ''),
            module_data.get('nameplate_power', 0),
            module_data.get('dimensions', {}).get('length_mm', 0),
            module_data.get('dimensions', {}).get('width_mm', 0),
            module_data.get('dimensions', {}).get('thickness_mm', 0),
            module_data.get('weight_kg', 0),
            module_data.get('cell_technology', '')
        ))

        self.conn.commit()
        return cursor.lastrowid

    def insert_pre_test_measurement(self, session_id: int, pre_test_data: Dict[str, Any]) -> int:
        """
        Insert pre-test measurements

        Args:
            session_id: Test session ID
            pre_test_data: Pre-test measurement data

        Returns:
            Measurement ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO pre_test_measurements
            (session_id, measurement_timestamp, pmax_initial, voc, isc, vmp, imp,
             fill_factor, insulation_resistance_initial)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            pre_test_data.get('Pmax_initial', 0),
            pre_test_data.get('Voc', 0),
            pre_test_data.get('Isc', 0),
            pre_test_data.get('Vmp', 0),
            pre_test_data.get('Imp', 0),
            pre_test_data.get('fill_factor', 0),
            pre_test_data.get('insulation_resistance_initial', 0)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def insert_impact_data(self, session_id: int, impact_data: Dict[str, Any]) -> int:
        """
        Insert impact test data

        Args:
            session_id: Test session ID
            impact_data: Impact test data

        Returns:
            Impact ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO impact_test_data
            (session_id, impact_number, impact_location_id, impact_location_x,
             impact_location_y, impact_location_description, ice_ball_diameter_mm,
             ice_ball_weight_g, ice_ball_temperature_c, time_delta_seconds,
             target_velocity_kmh, actual_velocity_kmh, velocity_deviation_kmh,
             open_circuit_detected, visual_damage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            impact_data.get('impact_number', 0),
            impact_data.get('impact_location', 0),
            impact_data.get('location_x', 0),
            impact_data.get('location_y', 0),
            impact_data.get('location_description', ''),
            impact_data.get('ice_ball_diameter_mm', 25.0),
            impact_data.get('ice_ball_weight_g', 7.53),
            impact_data.get('ice_ball_temperature_c', -4.0),
            impact_data.get('time_delta_seconds', 0),
            impact_data.get('target_velocity_kmh', 80.0),
            impact_data.get('actual_velocity_kmh', 0),
            impact_data.get('velocity_deviation_kmh', 0),
            impact_data.get('open_circuit_detected', False),
            impact_data.get('visual_damage', '')
        ))

        self.conn.commit()
        return cursor.lastrowid

    def insert_post_test_measurement(self, session_id: int, post_test_data: Dict[str, Any]) -> int:
        """
        Insert post-test measurements

        Args:
            session_id: Test session ID
            post_test_data: Post-test measurement data

        Returns:
            Measurement ID
        """
        visual_defects = post_test_data.get('visual_defects', {})

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO post_test_measurements
            (session_id, measurement_timestamp, pmax_final, voc, isc, vmp, imp,
             fill_factor, insulation_resistance_final, front_glass_cracks,
             cell_cracks, backsheet_cracks, delamination, junction_box_damage,
             frame_damage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            post_test_data.get('Pmax_final', 0),
            post_test_data.get('Voc', 0),
            post_test_data.get('Isc', 0),
            post_test_data.get('Vmp', 0),
            post_test_data.get('Imp', 0),
            post_test_data.get('fill_factor', 0),
            post_test_data.get('insulation_resistance_final', 0),
            visual_defects.get('front_glass_cracks', False),
            visual_defects.get('cell_cracks', False),
            visual_defects.get('backsheet_cracks', False),
            visual_defects.get('delamination', False),
            visual_defects.get('junction_box_damage', False),
            visual_defects.get('frame_damage', False)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def insert_test_results(self, session_id: int, results: Dict[str, Any]) -> int:
        """
        Insert test analysis results

        Args:
            session_id: Test session ID
            results: Analysis and pass/fail results

        Returns:
            Result ID
        """
        power = results.get('power_analysis', {})
        impact = results.get('impact_analysis', {})
        insulation = results.get('insulation_analysis', {})
        pf = results.get('pass_fail', {})
        criteria = pf.get('criteria', {})

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO test_results
            (session_id, pmax_initial, pmax_final, power_degradation_percent,
             power_degradation_watts, velocity_mean, velocity_std, velocity_min,
             velocity_max, time_compliance_count, time_compliance_rate,
             open_circuit_count, insulation_initial, insulation_final,
             insulation_degradation_percent, overall_result, power_criterion_pass,
             visual_criterion_pass, insulation_criterion_pass, open_circuit_criterion_pass)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            power.get('Pmax_initial', 0),
            power.get('Pmax_final', 0),
            power.get('degradation_percent', 0),
            power.get('degradation_watts', 0),
            impact.get('velocity_mean', 0),
            impact.get('velocity_std', 0),
            impact.get('velocity_min', 0),
            impact.get('velocity_max', 0),
            impact.get('time_compliance_count', 0),
            impact.get('time_compliance_rate', 0),
            impact.get('open_circuit_count', 0),
            insulation.get('initial_resistance', 0),
            insulation.get('final_resistance', 0),
            insulation.get('degradation_percent', 0),
            pf.get('overall_result', 'FAIL'),
            criteria.get('power_degradation', {}).get('pass', False),
            criteria.get('visual_inspection', {}).get('pass', False),
            criteria.get('insulation_resistance', {}).get('pass', False),
            criteria.get('open_circuit', {}).get('pass', False)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_session_data(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete test session data

        Args:
            session_id: Test session ID

        Returns:
            Dictionary with session data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM vw_hail_test_report WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def list_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List test sessions

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT session_id, protocol_id, test_date, test_operator,
                   facility, status, created_at
            FROM hail_test_sessions
            ORDER BY test_date DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def update_session_status(self, session_id: int, status: str) -> None:
        """
        Update test session status

        Args:
            session_id: Test session ID
            status: New status
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE hail_test_sessions
            SET status = ?, updated_at = ?
            WHERE session_id = ?
        """, (status, datetime.now().isoformat(), session_id))

        self.conn.commit()
