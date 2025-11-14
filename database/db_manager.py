"""
Database Manager
Handles database connections and operations
"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class DatabaseManager:
    """Manage database connections and operations"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Default to database directory in project root
            project_root = Path(__file__).parent.parent
            db_path = project_root / "database" / "test_protocols.db"

        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection

        Returns:
            SQLite connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries

        return self.connection

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        conn = self.connect()

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        conn.commit()

    def create_test_session(
        self,
        test_id: str,
        protocol_id: str,
        protocol_version: str,
        operator: str,
        **kwargs
    ) -> int:
        """
        Create a new test session

        Args:
            test_id: Unique test identifier
            protocol_id: Protocol identifier
            protocol_version: Protocol version
            operator: Operator name
            **kwargs: Additional optional fields

        Returns:
            Test session ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        INSERT INTO test_sessions (
            test_id, protocol_id, protocol_version, operator,
            start_time, chamber_id, solar_simulator_id, data_logger_id,
            chamber_calibration_date, simulator_calibration_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            test_id,
            protocol_id,
            protocol_version,
            operator,
            kwargs.get('start_time', datetime.now()),
            kwargs.get('chamber_id'),
            kwargs.get('solar_simulator_id'),
            kwargs.get('data_logger_id'),
            kwargs.get('chamber_calibration_date'),
            kwargs.get('simulator_calibration_date')
        ))

        conn.commit()
        return cursor.lastrowid

    def add_module(
        self,
        serial_number: str,
        manufacturer: str,
        model: str,
        module_type: str,
        rated_power: float,
        **kwargs
    ) -> int:
        """
        Add a module to the database

        Args:
            serial_number: Module serial number
            manufacturer: Manufacturer name
            model: Model name
            module_type: Type of module
            rated_power: Rated power in watts
            **kwargs: Additional optional fields

        Returns:
            Module ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Check if module already exists
        cursor.execute(
            "SELECT id FROM modules WHERE serial_number = ?",
            (serial_number,)
        )
        existing = cursor.fetchone()

        if existing:
            return existing[0]

        query = """
        INSERT INTO modules (
            serial_number, manufacturer, model, module_type,
            rated_power, technology, manufacture_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            serial_number,
            manufacturer,
            model,
            module_type,
            rated_power,
            kwargs.get('technology'),
            kwargs.get('manufacture_date'),
            kwargs.get('notes')
        ))

        conn.commit()
        return cursor.lastrowid

    def link_module_to_test(
        self,
        test_session_id: int,
        module_id: int,
        position: Optional[int] = None
    ):
        """
        Link a module to a test session

        Args:
            test_session_id: Test session ID
            module_id: Module ID
            position: Optional position in test chamber
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        INSERT OR IGNORE INTO test_session_modules (
            test_session_id, module_id, position
        ) VALUES (?, ?, ?)
        """

        cursor.execute(query, (test_session_id, module_id, position))
        conn.commit()

    def record_electrical_measurement(
        self,
        test_session_id: int,
        module_id: int,
        phase: str,
        pmax: float,
        voc: float,
        isc: float,
        vmpp: float,
        impp: float,
        fill_factor: float,
        **kwargs
    ) -> int:
        """
        Record an electrical measurement

        Args:
            test_session_id: Test session ID
            module_id: Module ID
            phase: Test phase (pre_test, in_test, post_test)
            pmax: Maximum power (W)
            voc: Open circuit voltage (V)
            isc: Short circuit current (A)
            vmpp: Voltage at MPP (V)
            impp: Current at MPP (A)
            fill_factor: Fill factor (%)
            **kwargs: Additional optional fields

        Returns:
            Measurement ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        INSERT INTO electrical_measurements (
            test_session_id, module_id, timestamp, phase,
            pmax, voc, isc, vmpp, impp, fill_factor,
            irradiance, temperature, spectrum, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            test_session_id,
            module_id,
            kwargs.get('timestamp', datetime.now()),
            phase,
            pmax, voc, isc, vmpp, impp, fill_factor,
            kwargs.get('irradiance', 1000.0),
            kwargs.get('temperature', 25.0),
            kwargs.get('spectrum', 'AM 1.5'),
            kwargs.get('notes')
        ))

        conn.commit()
        return cursor.lastrowid

    def record_environmental_measurement(
        self,
        test_session_id: int,
        step: int,
        cycle: int,
        temperature: float,
        relative_humidity: float,
        sensor_id: str,
        **kwargs
    ) -> int:
        """
        Record an environmental measurement

        Args:
            test_session_id: Test session ID
            step: Test step number
            cycle: Cycle number
            temperature: Temperature (°C)
            relative_humidity: Relative humidity (%)
            sensor_id: Sensor identifier
            **kwargs: Additional optional fields

        Returns:
            Measurement ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        INSERT INTO environmental_measurements (
            test_session_id, timestamp, step, cycle,
            temperature, relative_humidity, sensor_id,
            target_temperature, target_humidity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            test_session_id,
            kwargs.get('timestamp', datetime.now()),
            step, cycle,
            temperature, relative_humidity, sensor_id,
            kwargs.get('target_temperature'),
            kwargs.get('target_humidity')
        ))

        conn.commit()
        return cursor.lastrowid

    def record_alert(
        self,
        test_session_id: int,
        severity: str,
        message: str,
        **kwargs
    ) -> int:
        """
        Record an alert

        Args:
            test_session_id: Test session ID
            severity: Alert severity
            message: Alert message
            **kwargs: Additional optional fields

        Returns:
            Alert ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        INSERT INTO alerts (
            test_session_id, timestamp, severity, message,
            parameter, value, step, cycle
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (
            test_session_id,
            kwargs.get('timestamp', datetime.now()),
            severity,
            message,
            kwargs.get('parameter'),
            kwargs.get('value'),
            kwargs.get('step'),
            kwargs.get('cycle')
        ))

        conn.commit()
        return cursor.lastrowid

    def get_test_session(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test session by test ID

        Args:
            test_id: Test identifier

        Returns:
            Test session data or None
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM test_sessions WHERE test_id = ?",
            (test_id,)
        )

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_test_measurements(
        self,
        test_session_id: int,
        measurement_type: str = 'electrical'
    ) -> List[Dict[str, Any]]:
        """
        Get measurements for a test session

        Args:
            test_session_id: Test session ID
            measurement_type: Type of measurement (electrical, environmental)

        Returns:
            List of measurements
        """
        conn = self.connect()
        cursor = conn.cursor()

        if measurement_type == 'electrical':
            query = """
            SELECT * FROM electrical_measurements
            WHERE test_session_id = ?
            ORDER BY timestamp
            """
        elif measurement_type == 'environmental':
            query = """
            SELECT * FROM environmental_measurements
            WHERE test_session_id = ?
            ORDER BY timestamp
            """
        else:
            return []

        cursor.execute(query, (test_session_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_test_status(
        self,
        test_session_id: int,
        status: str,
        **kwargs
    ):
        """
        Update test session status

        Args:
            test_session_id: Test session ID
            status: New status
            **kwargs: Additional fields to update
        """
        conn = self.connect()
        cursor = conn.cursor()

        updates = ['status = ?']
        params = [status]

        if 'end_time' in kwargs:
            updates.append('end_time = ?')
            params.append(kwargs['end_time'])

        if 'pass_fail' in kwargs:
            updates.append('pass_fail = ?')
            params.append(kwargs['pass_fail'])

        params.append(test_session_id)

        query = f"""
        UPDATE test_sessions
        SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """

        cursor.execute(query, params)
        conn.commit()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
