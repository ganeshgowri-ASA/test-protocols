"""Database utilities for test protocols framework."""

from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from datetime import datetime
import json
import os

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.utils.config import get_config


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize database manager.

        Args:
            config: Optional configuration dictionary. If None, uses default config.
        """
        self.config = config or get_config()
        self.db_config = self.config.get('database', {})
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with appropriate configuration."""
        db_url = self.db_config.get('url', 'sqlite:///./data/db/test_protocols.db')

        # Ensure directory exists for SQLite databases
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        engine_kwargs: Dict[str, Any] = {
            'echo': self.db_config.get('echo', False),
        }

        # SQLite-specific configuration
        if 'sqlite' in db_url:
            engine_kwargs['connect_args'] = {'check_same_thread': False}
            if db_url == 'sqlite:///:memory:':
                engine_kwargs['poolclass'] = StaticPool
        else:
            # PostgreSQL/other database configuration
            engine_kwargs['pool_size'] = self.db_config.get('pool_size', 5)
            engine_kwargs['max_overflow'] = self.db_config.get('max_overflow', 10)

        engine = create_engine(db_url, **engine_kwargs)

        # Enable JSON support for SQLite
        if 'sqlite' in db_url:
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        return engine

    @contextmanager
    def get_session(self) -> Any:
        """Context manager for database sessions.

        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_database(self, schema_file: str = 'data/db/schema.sql') -> None:
        """Initialize database schema from SQL file.

        Args:
            schema_file: Path to SQL schema file
        """
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        # Split by semicolons and execute each statement
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

        with self.engine.begin() as conn:
            for statement in statements:
                if statement:
                    conn.execute(text(statement))

    def insert_protocol(self, protocol_data: Dict[str, Any]) -> int:
        """Insert a new protocol.

        Args:
            protocol_data: Protocol configuration dictionary

        Returns:
            Inserted protocol ID
        """
        with self.get_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO protocols
                    (protocol_id, name, version, category, description, config, created_by)
                    VALUES (:protocol_id, :name, :version, :category, :description, :config, :created_by)
                    RETURNING id
                """),
                {
                    'protocol_id': protocol_data['protocol_id'],
                    'name': protocol_data['name'],
                    'version': protocol_data['version'],
                    'category': protocol_data['category'],
                    'description': protocol_data.get('description', ''),
                    'config': json.dumps(protocol_data),
                    'created_by': protocol_data.get('metadata', {}).get('author', 'system')
                }
            )
            return result.fetchone()[0]

    def create_test_run(self, run_data: Dict[str, Any]) -> str:
        """Create a new test run.

        Args:
            run_data: Test run configuration

        Returns:
            Run ID
        """
        with self.get_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO test_runs
                    (run_id, protocol_id, protocol_version, status, start_time,
                     operator, sample_id, device_id, location, environmental_conditions)
                    VALUES (:run_id, :protocol_id, :protocol_version, :status, :start_time,
                            :operator, :sample_id, :device_id, :location, :environmental_conditions)
                    RETURNING run_id
                """),
                {
                    'run_id': run_data['run_id'],
                    'protocol_id': run_data['protocol_id'],
                    'protocol_version': run_data.get('protocol_version'),
                    'status': run_data.get('status', 'running'),
                    'start_time': run_data.get('start_time', datetime.now()),
                    'operator': run_data.get('operator'),
                    'sample_id': run_data.get('sample_id'),
                    'device_id': run_data.get('device_id'),
                    'location': run_data.get('location'),
                    'environmental_conditions': json.dumps(run_data.get('environmental_conditions', {}))
                }
            )
            return result.fetchone()[0]

    def insert_measurement(self, measurement: Dict[str, Any]) -> int:
        """Insert a measurement record.

        Args:
            measurement: Measurement data

        Returns:
            Measurement ID
        """
        with self.get_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO measurements
                    (run_id, timestamp, metric_name, metric_value, metric_unit,
                     quality_flag, sensor_id, metadata)
                    VALUES (:run_id, :timestamp, :metric_name, :metric_value, :metric_unit,
                            :quality_flag, :sensor_id, :metadata)
                    RETURNING id
                """),
                {
                    'run_id': measurement['run_id'],
                    'timestamp': measurement['timestamp'],
                    'metric_name': measurement['metric_name'],
                    'metric_value': measurement['metric_value'],
                    'metric_unit': measurement.get('metric_unit'),
                    'quality_flag': measurement.get('quality_flag', 'good'),
                    'sensor_id': measurement.get('sensor_id'),
                    'metadata': json.dumps(measurement.get('metadata', {}))
                }
            )
            return result.fetchone()[0]

    def insert_result(self, result_data: Dict[str, Any]) -> int:
        """Insert an analysis result.

        Args:
            result_data: Result data

        Returns:
            Result ID
        """
        with self.get_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO results
                    (run_id, result_type, metric_name, calculated_value, unit,
                     pass_fail, threshold, deviation, calculation_method, result_data)
                    VALUES (:run_id, :result_type, :metric_name, :calculated_value, :unit,
                            :pass_fail, :threshold, :deviation, :calculation_method, :result_data)
                    RETURNING id
                """),
                {
                    'run_id': result_data['run_id'],
                    'result_type': result_data['result_type'],
                    'metric_name': result_data.get('metric_name'),
                    'calculated_value': result_data.get('calculated_value'),
                    'unit': result_data.get('unit'),
                    'pass_fail': result_data.get('pass_fail'),
                    'threshold': result_data.get('threshold'),
                    'deviation': result_data.get('deviation'),
                    'calculation_method': result_data.get('calculation_method'),
                    'result_data': json.dumps(result_data.get('result_data', {}))
                }
            )
            return result.fetchone()[0]

    def get_test_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get test run details.

        Args:
            run_id: Test run ID

        Returns:
            Test run data or None if not found
        """
        with self.get_session() as session:
            result = session.execute(
                text("SELECT * FROM v_test_run_summary WHERE run_id = :run_id"),
                {'run_id': run_id}
            )
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    def get_measurements(self, run_id: str, metric_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get measurements for a test run.

        Args:
            run_id: Test run ID
            metric_name: Optional metric name filter

        Returns:
            List of measurements
        """
        with self.get_session() as session:
            if metric_name:
                query = text("""
                    SELECT * FROM measurements
                    WHERE run_id = :run_id AND metric_name = :metric_name
                    ORDER BY timestamp
                """)
                result = session.execute(query, {'run_id': run_id, 'metric_name': metric_name})
            else:
                query = text("""
                    SELECT * FROM measurements
                    WHERE run_id = :run_id
                    ORDER BY timestamp
                """)
                result = session.execute(query, {'run_id': run_id})

            return [dict(row._mapping) for row in result.fetchall()]


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create global database manager instance.

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
