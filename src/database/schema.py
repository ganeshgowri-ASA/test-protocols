"""Database schema initialization and migration utilities."""

from sqlalchemy import inspect
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manage database schema operations."""

    def __init__(self, db_manager):
        """
        Initialize SchemaManager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.engine = db_manager.engine

    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database.

        Returns:
            List of table names
        """
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        logger.info(f"Found {len(tables)} tables in database")
        return tables

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary containing column information
        """
        inspector = inspect(self.engine)

        if not self.table_exists(table_name):
            logger.warning(f"Table {table_name} does not exist")
            return {}

        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)

        schema = {
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "indexes": indexes,
        }

        logger.info(f"Retrieved schema for table: {table_name}")
        return schema

    def verify_schema(self) -> Dict[str, bool]:
        """
        Verify that all required tables exist.

        Returns:
            Dictionary mapping table names to existence status
        """
        required_tables = [
            "protocols",
            "test_runs",
            "measurements",
            "qc_flags",
            "test_reports",
            "equipment",
            "equipment_calibrations",
        ]

        status = {}
        for table in required_tables:
            exists = self.table_exists(table)
            status[table] = exists
            if not exists:
                logger.warning(f"Required table missing: {table}")

        all_exist = all(status.values())
        if all_exist:
            logger.info("All required tables exist")
        else:
            logger.warning(f"Missing tables: {[t for t, exists in status.items() if not exists]}")

        return status

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary containing database statistics
        """
        from .models import (
            Protocol,
            TestRun,
            Measurement,
            QCFlag,
            TestReport,
            Equipment,
        )

        stats = {}

        with self.db_manager.get_session() as session:
            stats["protocols_count"] = session.query(Protocol).count()
            stats["test_runs_count"] = session.query(TestRun).count()
            stats["measurements_count"] = session.query(Measurement).count()
            stats["qc_flags_count"] = session.query(QCFlag).count()
            stats["test_reports_count"] = session.query(TestReport).count()
            stats["equipment_count"] = session.query(Equipment).count()

        logger.info(f"Database stats: {stats}")
        return stats
