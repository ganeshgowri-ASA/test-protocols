"""
Admin Seed & Database Management Page
======================================
Comprehensive database administration with:
- Protocol seeding
- Schema validation and comparison
- Migration management with rollback
- QA testing and validation
- Error handling and logging

Author: System Administrator
Version: 2.0.0
"""

import streamlit as st
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Admin - Database Management",
    page_icon="🔧",
    layout="wide"
)


# =============================================================================
# DATABASE CONNECTION UTILITIES
# =============================================================================


def get_database_session() -> Tuple[Any, Optional[str]]:
    """
    Get a database session with error handling.

    Returns:
        Tuple of (session, error_message). Session is None if error occurred.
    """
    try:
        from config.database import get_session_local
        SessionLocal = get_session_local()
        db = SessionLocal()
        return db, None
    except Exception as e:
        error_msg = f"Failed to connect to database: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def get_database_engine() -> Tuple[Any, Optional[str]]:
    """
    Get the database engine for raw SQL operations.

    Returns:
        Tuple of (engine, error_message). Engine is None if error occurred.
    """
    try:
        from config.database import get_engine
        engine = get_engine()
        return engine, None
    except Exception as e:
        error_msg = f"Failed to get database engine: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def check_database_connection() -> Dict[str, Any]:
    """
    Check database connectivity and return status.

    Returns:
        Dictionary with connection status information.
    """
    result = {
        "connected": False,
        "database_type": "unknown",
        "error": None,
        "details": {}
    }

    try:
        engine, error = get_database_engine()
        if error:
            result["error"] = error
            return result

        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Determine database type
        db_url = str(engine.url)
        if "postgresql" in db_url:
            result["database_type"] = "PostgreSQL"
        elif "sqlite" in db_url:
            result["database_type"] = "SQLite"
        else:
            result["database_type"] = "Other"

        result["connected"] = True
        result["details"]["url"] = db_url.split("@")[-1] if "@" in db_url else "local"
        logger.info("Database connection successful")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Database connection failed: {e}")

    return result


# =============================================================================
# SCHEMA VALIDATION UTILITIES
# =============================================================================


def get_expected_tables() -> List[str]:
    """
    Get list of all tables defined in models.py.

    Returns:
        List of expected table names.
    """
    return [
        "users",
        "service_requests",
        "incoming_inspections",
        "equipment",
        "equipment_bookings",
        "test_protocols",
        "test_executions",
        "test_data",
        "audit_logs",
        "qr_codes",
        "company_profile",
        "sample_receipts",
        "samples",
        "sample_status_history",
        "route_cards",
        "sample_test_assignments",
        "sample_inventory",
        "staff_training",
        "staff_training_records",
        "documents",
        "document_access_log",
        "bom_items",
        "bom_protocol_requirements",
        "bom_usage_log",
        "qr_scan_log",
        "calibration_records",
    ]


def get_expected_columns() -> Dict[str, List[str]]:
    """
    Get expected columns for each table based on models.py.

    Returns:
        Dictionary mapping table names to list of expected columns.
    """
    return {
        "samples": [
            "id", "sample_id", "project_id", "service_request_id", "receipt_id",
            "inspection_id", "sample_type", "manufacturer", "model_number",
            "serial_number", "batch_number", "length_mm", "width_mm",
            "thickness_mm", "weight_kg", "qr_code", "qr_code_image_path",
            "qr_data", "status", "current_location", "storage_location",
            "allocation_date", "allocated_by_id", "assigned_protocol_ids",
            "current_test_id", "tests_completed", "tests_total",
            "overall_result", "result_summary", "specifications", "notes",
            "photos", "custody_history", "created_at", "updated_at",
            "completed_at", "disposed_at"
        ],
        "service_requests": [
            "id", "request_number", "client_name", "client_email", "client_phone",
            "client_organization", "sample_type", "sample_count", "manufacturer",
            "model_number", "serial_numbers", "requested_protocols", "priority",
            "expected_completion_date", "status", "created_at", "updated_at",
            "submitted_at", "approved_at", "completed_at", "created_by", "notes",
            "attachments", "expected_sample_quantity", "actual_sample_quantity",
            "quantity_verified", "receipt_id"
        ],
        "incoming_inspections": [
            "id", "inspection_number", "service_request_id", "sample_id",
            "qr_code", "physical_damage", "physical_damage_notes",
            "label_readable", "connectors_intact", "frame_condition",
            "glass_condition", "backsheet_condition", "length_mm", "width_mm",
            "thickness_mm", "weight_kg", "photos", "status", "inspection_date",
            "inspector_id", "passed", "remarks", "created_at", "updated_at",
            "receipt_id", "allocation_triggered", "allocated_sample_id"
        ],
        "sample_receipts": [
            "id", "receipt_number", "service_request_id", "received_date",
            "received_by_id", "client_name", "client_reference", "courier_name",
            "tracking_number", "package_count", "package_condition",
            "package_photos", "expected_sample_count", "actual_sample_count",
            "quantity_mismatch", "mismatch_notes", "requires_supervisor_approval",
            "supervisor_approved", "supervisor_id", "approval_date",
            "approval_notes", "status", "remarks", "created_at", "updated_at"
        ],
    }


def get_actual_database_schema() -> Tuple[Dict[str, List[str]], Optional[str]]:
    """
    Query the actual database schema to get existing tables and columns.

    Returns:
        Tuple of (schema_dict, error_message).
        schema_dict maps table names to list of column names.
    """
    schema = {}
    engine, error = get_database_engine()

    if error:
        return schema, error

    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)

        for table_name in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            schema[table_name] = columns

        logger.info(f"Retrieved schema for {len(schema)} tables")
        return schema, None

    except Exception as e:
        error_msg = f"Failed to retrieve database schema: {str(e)}"
        logger.error(error_msg)
        return schema, error_msg


def compare_schemas() -> Dict[str, Any]:
    """
    Compare expected schema (from models.py) with actual database schema.

    Returns:
        Dictionary with comparison results including missing tables and columns.
    """
    result = {
        "missing_tables": [],
        "missing_columns": {},
        "extra_tables": [],
        "extra_columns": {},
        "match_percentage": 0.0,
        "error": None
    }

    actual_schema, error = get_actual_database_schema()
    if error:
        result["error"] = error
        return result

    expected_tables = get_expected_tables()
    expected_columns = get_expected_columns()

    # Find missing tables
    actual_tables = set(actual_schema.keys())
    expected_tables_set = set(expected_tables)

    result["missing_tables"] = list(expected_tables_set - actual_tables)
    result["extra_tables"] = list(actual_tables - expected_tables_set)

    # Find missing columns for key tables
    for table, expected_cols in expected_columns.items():
        if table in actual_schema:
            actual_cols = set(actual_schema[table])
            expected_cols_set = set(expected_cols)

            missing = list(expected_cols_set - actual_cols)
            extra = list(actual_cols - expected_cols_set)

            if missing:
                result["missing_columns"][table] = missing
            if extra:
                result["extra_columns"][table] = extra

    # Calculate match percentage
    total_expected = len(expected_tables)
    matched = total_expected - len(result["missing_tables"])
    result["match_percentage"] = (matched / total_expected * 100) if total_expected > 0 else 0

    return result


def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a specific column exists in a table.

    Args:
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        True if column exists, False otherwise.
    """
    try:
        engine, error = get_database_engine()
        if error:
            return False

        from sqlalchemy import inspect
        inspector = inspect(engine)

        if table_name not in inspector.get_table_names():
            return False

        columns = [col["name"] for col in inspector.get_columns(table_name)]
        return column_name in columns

    except Exception as e:
        logger.error(f"Error checking column existence: {e}")
        return False


def check_table_exists(table_name: str) -> bool:
    """
    Check if a specific table exists in the database.

    Args:
        table_name: Name of the table

    Returns:
        True if table exists, False otherwise.
    """
    try:
        engine, error = get_database_engine()
        if error:
            return False

        from sqlalchemy import inspect
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()

    except Exception as e:
        logger.error(f"Error checking table existence: {e}")
        return False


# =============================================================================
# MIGRATION EXECUTION UTILITIES
# =============================================================================


def execute_migration_sql(
    sql_statements: List[str],
    migration_name: str,
    rollback_on_error: bool = True
) -> Dict[str, Any]:
    """
    Execute a list of SQL statements as a migration.

    Args:
        sql_statements: List of SQL statements to execute
        migration_name: Name of the migration for logging
        rollback_on_error: Whether to rollback on error

    Returns:
        Dictionary with execution results.
    """
    result = {
        "success": False,
        "executed_statements": 0,
        "total_statements": len(sql_statements),
        "error": None,
        "details": []
    }

    engine, error = get_database_engine()
    if error:
        result["error"] = error
        return result

    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            for i, sql in enumerate(sql_statements):
                try:
                    # Skip empty statements
                    sql = sql.strip()
                    if not sql:
                        continue

                    conn.execute(text(sql))
                    result["executed_statements"] += 1
                    result["details"].append(f"OK: Statement {i + 1}")
                    logger.info(f"Migration {migration_name}: Executed statement {i + 1}")

                except Exception as stmt_error:
                    error_msg = f"Statement {i + 1} failed: {str(stmt_error)}"
                    result["details"].append(f"FAIL: {error_msg}")
                    logger.error(f"Migration {migration_name}: {error_msg}")

                    if rollback_on_error:
                        result["error"] = error_msg
                        raise  # Will trigger rollback

        result["success"] = True
        logger.info(f"Migration {migration_name} completed successfully")

    except Exception as e:
        if not result["error"]:
            result["error"] = str(e)
        logger.error(f"Migration {migration_name} failed: {e}")

    return result


def add_column_if_not_exists(
    table_name: str,
    column_name: str,
    column_type: str,
    default_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Safely add a column to a table if it doesn't exist.

    Args:
        table_name: Name of the table
        column_name: Name of the column to add
        column_type: SQL type of the column
        default_value: Optional default value

    Returns:
        Dictionary with operation result.
    """
    result = {"success": False, "message": "", "already_exists": False}

    # Pre-flight check
    if check_column_exists(table_name, column_name):
        result["success"] = True
        result["already_exists"] = True
        result["message"] = f"Column {table_name}.{column_name} already exists"
        logger.info(result["message"])
        return result

    # Build SQL statement
    default_clause = f" DEFAULT {default_value}" if default_value else ""
    sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}{default_clause}"

    try:
        migration_result = execute_migration_sql([sql], f"add_{table_name}_{column_name}")
        result["success"] = migration_result["success"]
        result["message"] = f"Added column {table_name}.{column_name}" if result["success"] else migration_result["error"]

    except Exception as e:
        result["message"] = str(e)
        logger.error(f"Failed to add column: {e}")

    return result


def drop_column_if_exists(table_name: str, column_name: str) -> Dict[str, Any]:
    """
    Safely drop a column from a table if it exists.

    Args:
        table_name: Name of the table
        column_name: Name of the column to drop

    Returns:
        Dictionary with operation result.
    """
    result = {"success": False, "message": "", "not_found": False}

    # Pre-flight check
    if not check_column_exists(table_name, column_name):
        result["success"] = True
        result["not_found"] = True
        result["message"] = f"Column {table_name}.{column_name} does not exist"
        logger.info(result["message"])
        return result

    sql = f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}"

    try:
        migration_result = execute_migration_sql([sql], f"drop_{table_name}_{column_name}")
        result["success"] = migration_result["success"]
        result["message"] = f"Dropped column {table_name}.{column_name}" if result["success"] else migration_result["error"]

    except Exception as e:
        result["message"] = str(e)
        logger.error(f"Failed to drop column: {e}")

    return result


# =============================================================================
# MIGRATION DEFINITIONS
# =============================================================================


def get_migration_definitions() -> List[Dict[str, Any]]:
    """
    Get all migration definitions with their UP and DOWN operations.

    Returns:
        List of migration definition dictionaries.
    """
    return [
        {
            "id": "001",
            "name": "Initial Schema",
            "description": "Create base tables for users, equipment, and protocols",
            "up_sql": [],  # Already created by SQLAlchemy
            "down_sql": [],
            "pre_check": lambda: True,
            "category": "schema"
        },
        {
            "id": "002",
            "name": "Sample Management Tables",
            "description": "Create sample_receipts, samples, route_cards, and related tables",
            "up_file": "database/migrations/002_sample_management_UP.sql",
            "down_file": "database/migrations/002_sample_management_DOWN.sql",
            "pre_check": lambda: not check_table_exists("samples"),
            "category": "schema"
        },
        {
            "id": "003",
            "name": "Service Request Extensions",
            "description": "Add sample quantity fields to service_requests",
            "up_columns": [
                ("service_requests", "expected_sample_quantity", "INTEGER", "1"),
                ("service_requests", "actual_sample_quantity", "INTEGER", None),
                ("service_requests", "quantity_verified", "BOOLEAN", "FALSE"),
            ],
            "down_columns": [
                ("service_requests", "expected_sample_quantity"),
                ("service_requests", "actual_sample_quantity"),
                ("service_requests", "quantity_verified"),
            ],
            "pre_check": lambda: not check_column_exists("service_requests", "expected_sample_quantity"),
            "category": "columns"
        },
        {
            "id": "004",
            "name": "Incoming Inspection Extensions",
            "description": "Add allocation tracking to incoming_inspections",
            "up_columns": [
                ("incoming_inspections", "allocation_triggered", "BOOLEAN", "FALSE"),
                ("incoming_inspections", "allocated_sample_id", "INTEGER", None),
            ],
            "down_columns": [
                ("incoming_inspections", "allocation_triggered"),
                ("incoming_inspections", "allocated_sample_id"),
            ],
            "pre_check": lambda: not check_column_exists("incoming_inspections", "allocation_triggered"),
            "category": "columns"
        },
        {
            "id": "005",
            "name": "Sample Status Column",
            "description": "Ensure samples.status column exists with correct type",
            "up_columns": [
                ("samples", "status", "VARCHAR(20)", "'received'"),
            ],
            "down_columns": [],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "status"),
            "category": "columns"
        },
        {
            "id": "006",
            "name": "Sample Project ID",
            "description": "Add project_id column to samples table",
            "up_columns": [
                ("samples", "project_id", "VARCHAR(50)", None),
            ],
            "down_columns": [
                ("samples", "project_id"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "project_id"),
            "category": "columns"
        },
        {
            "id": "007",
            "name": "Sample Service Request Link",
            "description": "Add service_request_id column to samples table",
            "up_columns": [
                ("samples", "service_request_id", "INTEGER", None),
            ],
            "down_columns": [
                ("samples", "service_request_id"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "service_request_id"),
            "category": "columns"
        },
        {
            "id": "008",
            "name": "Sample Physical Properties",
            "description": "Add length, width, thickness, weight to samples",
            "up_columns": [
                ("samples", "length_mm", "FLOAT", None),
                ("samples", "width_mm", "FLOAT", None),
                ("samples", "thickness_mm", "FLOAT", None),
                ("samples", "weight_kg", "FLOAT", None),
            ],
            "down_columns": [
                ("samples", "length_mm"),
                ("samples", "width_mm"),
                ("samples", "thickness_mm"),
                ("samples", "weight_kg"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "length_mm"),
            "category": "columns"
        },
        {
            "id": "009",
            "name": "Sample QR Code Fields",
            "description": "Add QR code fields to samples",
            "up_columns": [
                ("samples", "qr_code", "VARCHAR(200)", None),
                ("samples", "qr_code_image_path", "VARCHAR(200)", None),
                ("samples", "qr_data", "JSON", None),
            ],
            "down_columns": [
                ("samples", "qr_code"),
                ("samples", "qr_code_image_path"),
                ("samples", "qr_data"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "qr_code"),
            "category": "columns"
        },
        {
            "id": "010",
            "name": "Sample Allocation Fields",
            "description": "Add allocation tracking fields to samples",
            "up_columns": [
                ("samples", "allocation_date", "TIMESTAMP", None),
                ("samples", "allocated_by_id", "INTEGER", None),
                ("samples", "current_location", "VARCHAR(100)", None),
                ("samples", "storage_location", "VARCHAR(100)", None),
            ],
            "down_columns": [
                ("samples", "allocation_date"),
                ("samples", "allocated_by_id"),
                ("samples", "current_location"),
                ("samples", "storage_location"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "allocation_date"),
            "category": "columns"
        },
        {
            "id": "011",
            "name": "Sample Test Tracking",
            "description": "Add test assignment and tracking fields to samples",
            "up_columns": [
                ("samples", "assigned_protocol_ids", "JSON", None),
                ("samples", "current_test_id", "INTEGER", None),
                ("samples", "tests_completed", "INTEGER", "0"),
                ("samples", "tests_total", "INTEGER", "0"),
            ],
            "down_columns": [
                ("samples", "assigned_protocol_ids"),
                ("samples", "current_test_id"),
                ("samples", "tests_completed"),
                ("samples", "tests_total"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "assigned_protocol_ids"),
            "category": "columns"
        },
        {
            "id": "012",
            "name": "Sample Results Fields",
            "description": "Add result summary fields to samples",
            "up_columns": [
                ("samples", "overall_result", "VARCHAR(20)", None),
                ("samples", "result_summary", "TEXT", None),
                ("samples", "completed_at", "TIMESTAMP", None),
                ("samples", "disposed_at", "TIMESTAMP", None),
            ],
            "down_columns": [
                ("samples", "overall_result"),
                ("samples", "result_summary"),
                ("samples", "completed_at"),
                ("samples", "disposed_at"),
            ],
            "pre_check": lambda: check_table_exists("samples") and not check_column_exists("samples", "overall_result"),
            "category": "columns"
        },
    ]


def run_migration_up(migration: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a migration's UP operation.

    Args:
        migration: Migration definition dictionary

    Returns:
        Result dictionary with success status and messages.
    """
    result = {"success": False, "messages": [], "error": None}

    try:
        # Check if migration should run
        if "pre_check" in migration and callable(migration["pre_check"]):
            if not migration["pre_check"]():
                result["success"] = True
                result["messages"].append(f"Migration {migration['id']} already applied or not needed")
                return result

        # Handle SQL file migrations
        if "up_file" in migration:
            file_path = project_root / migration["up_file"]
            if file_path.exists():
                sql_content = file_path.read_text()
                statements = [s.strip() for s in sql_content.split(";") if s.strip()]
                exec_result = execute_migration_sql(statements, migration["id"])
                result["success"] = exec_result["success"]
                result["messages"] = exec_result["details"]
                result["error"] = exec_result["error"]
            else:
                result["error"] = f"Migration file not found: {migration['up_file']}"
                return result

        # Handle column-based migrations
        elif "up_columns" in migration:
            all_success = True
            for col_def in migration["up_columns"]:
                table, column, col_type, default = col_def
                col_result = add_column_if_not_exists(table, column, col_type, default)
                result["messages"].append(col_result["message"])
                if not col_result["success"]:
                    all_success = False
            result["success"] = all_success

        # Handle raw SQL migrations
        elif "up_sql" in migration and migration["up_sql"]:
            exec_result = execute_migration_sql(migration["up_sql"], migration["id"])
            result["success"] = exec_result["success"]
            result["messages"] = exec_result["details"]
            result["error"] = exec_result["error"]

        else:
            result["success"] = True
            result["messages"].append("No migration actions defined")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Migration {migration['id']} failed: {e}")

    return result


def run_migration_down(migration: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a migration's DOWN (rollback) operation.

    Args:
        migration: Migration definition dictionary

    Returns:
        Result dictionary with success status and messages.
    """
    result = {"success": False, "messages": [], "error": None}

    try:
        # Handle SQL file rollbacks
        if "down_file" in migration:
            file_path = project_root / migration["down_file"]
            if file_path.exists():
                sql_content = file_path.read_text()
                statements = [s.strip() for s in sql_content.split(";") if s.strip()]
                exec_result = execute_migration_sql(statements, f"{migration['id']}_rollback")
                result["success"] = exec_result["success"]
                result["messages"] = exec_result["details"]
                result["error"] = exec_result["error"]
            else:
                result["error"] = f"Rollback file not found: {migration['down_file']}"
                return result

        # Handle column-based rollbacks
        elif "down_columns" in migration and migration["down_columns"]:
            all_success = True
            for col_def in migration["down_columns"]:
                if isinstance(col_def, tuple):
                    table, column = col_def[:2]
                else:
                    table, column = col_def.split(".")
                col_result = drop_column_if_exists(table, column)
                result["messages"].append(col_result["message"])
                if not col_result["success"]:
                    all_success = False
            result["success"] = all_success

        # Handle raw SQL rollbacks
        elif "down_sql" in migration and migration["down_sql"]:
            exec_result = execute_migration_sql(migration["down_sql"], f"{migration['id']}_rollback")
            result["success"] = exec_result["success"]
            result["messages"] = exec_result["details"]
            result["error"] = exec_result["error"]

        else:
            result["success"] = True
            result["messages"].append("No rollback actions defined")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Rollback {migration['id']} failed: {e}")

    return result


# =============================================================================
# PROTOCOL SEEDING
# =============================================================================


def seed_test_protocols() -> Dict[str, Any]:
    """
    Seed all 54 test protocols into the database.

    Returns:
        Dictionary with seeding results.
    """
    result = {"success": False, "count": 0, "error": None, "details": []}

    db, error = get_database_session()
    if error:
        result["error"] = error
        return result

    try:
        from database import TestProtocol

        # All 54 protocols
        protocols_data = [
            # PERFORMANCE TESTING (P1-P12)
            {"protocol_id": "P1", "name": "I-V Performance Characterization", "category": "performance",
             "description": "Measure current-voltage characteristics under STC",
             "standard_reference": "IEC 61215-2:2021 MQT 06", "estimated_duration_hours": 2.0},
            {"protocol_id": "P2", "name": "P-V Performance Analysis", "category": "performance",
             "description": "Power-voltage characteristic measurement",
             "standard_reference": "IEC 61215-2:2021 MQT 06", "estimated_duration_hours": 2.0},
            {"protocol_id": "P3", "name": "STC Power Rating", "category": "performance",
             "description": "Power rating at Standard Test Conditions",
             "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 2.0},
            {"protocol_id": "P4", "name": "NOCT Determination", "category": "performance",
             "description": "Nominal Operating Cell Temperature determination",
             "standard_reference": "IEC 61215-2:2021 MQT 05", "estimated_duration_hours": 8.0},
            {"protocol_id": "P5", "name": "Temperature Coefficient Measurement", "category": "performance",
             "description": "Temperature coefficients for Isc, Voc, and Pmax",
             "standard_reference": "IEC 61215-2:2021 MQT 04", "estimated_duration_hours": 6.0},
            {"protocol_id": "P6", "name": "Low Irradiance Performance", "category": "performance",
             "description": "Performance measurement at 200 W/m2",
             "standard_reference": "IEC 61215-2:2021 MQT 07", "estimated_duration_hours": 3.0},
            {"protocol_id": "P7", "name": "Performance Matrix Test", "category": "performance",
             "description": "Multi-condition performance mapping",
             "standard_reference": "IEC 61853-1:2011", "estimated_duration_hours": 24.0},
            {"protocol_id": "P8", "name": "Spectral Response Measurement", "category": "performance",
             "description": "Measure spectral response and quantum efficiency",
             "standard_reference": "IEC 60904-8:2014", "estimated_duration_hours": 4.0},
            {"protocol_id": "P9", "name": "Incidence Angle Modifier", "category": "performance",
             "description": "Power output vs angle of incidence",
             "standard_reference": "IEC 61853-2:2016", "estimated_duration_hours": 6.0},
            {"protocol_id": "P10", "name": "Bifacial Performance Test", "category": "performance",
             "description": "Bifacial module performance characterization",
             "standard_reference": "IEC TS 60904-1-2:2019", "estimated_duration_hours": 8.0},
            {"protocol_id": "P11", "name": "Energy Rating Test", "category": "performance",
             "description": "Energy yield prediction and rating",
             "standard_reference": "IEC 61853-3:2018", "estimated_duration_hours": 4.0},
            {"protocol_id": "P12", "name": "Bypass Diode Functionality", "category": "performance",
             "description": "Verify bypass diode operation",
             "standard_reference": "IEC 61215-2:2021 MQT 18", "estimated_duration_hours": 2.0},

            # DEGRADATION TESTING (P13-P27)
            {"protocol_id": "P13", "name": "Light-Induced Degradation (LID)", "category": "degradation",
             "description": "Power degradation under light exposure",
             "standard_reference": "IEC 61215-2:2021 MQT 19", "estimated_duration_hours": 48.0},
            {"protocol_id": "P14", "name": "LETID Test", "category": "degradation",
             "description": "Light and elevated temperature induced degradation",
             "standard_reference": "IEC TS 63202-1:2021", "estimated_duration_hours": 162.0},
            {"protocol_id": "P15", "name": "Potential-Induced Degradation (PID)", "category": "degradation",
             "description": "Voltage stress induced degradation test",
             "standard_reference": "IEC TS 62804-1:2015", "estimated_duration_hours": 96.0},
            {"protocol_id": "P16", "name": "PID Recovery Test", "category": "degradation",
             "description": "PID reversibility evaluation",
             "standard_reference": "IEC TS 62804-1:2015", "estimated_duration_hours": 48.0},
            {"protocol_id": "P17", "name": "UV Degradation Test", "category": "degradation",
             "description": "Degradation from UV exposure",
             "standard_reference": "IEC 61215-2:2021 MQT 10", "estimated_duration_hours": 120.0},
            {"protocol_id": "P18", "name": "Hot Spot Endurance Test", "category": "degradation",
             "description": "Module resilience to localized heating",
             "standard_reference": "IEC 61215-2:2021 MQT 09", "estimated_duration_hours": 5.0},
            {"protocol_id": "P19", "name": "Snail Trail Assessment", "category": "degradation",
             "description": "Snail trail formation assessment",
             "standard_reference": "IEC 62759-1:2015", "estimated_duration_hours": 2.0},
            {"protocol_id": "P20", "name": "Cell Crack Detection", "category": "degradation",
             "description": "EL imaging for micro-crack detection",
             "standard_reference": "IEC TS 60904-13:2018", "estimated_duration_hours": 1.0},
            {"protocol_id": "P21", "name": "Solder Bond Degradation", "category": "degradation",
             "description": "Solder joint integrity evaluation",
             "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 4.0},
            {"protocol_id": "P22", "name": "Delamination Assessment", "category": "degradation",
             "description": "Identify delamination in module layers",
             "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 2.0},
            {"protocol_id": "P23", "name": "Yellowing/Browning Test", "category": "degradation",
             "description": "Encapsulant discoloration assessment",
             "standard_reference": "IEC 62788-1-6:2017", "estimated_duration_hours": 2.0},
            {"protocol_id": "P24", "name": "Corrosion Assessment", "category": "degradation",
             "description": "Metallic component corrosion evaluation",
             "standard_reference": "IEC 61701:2020", "estimated_duration_hours": 2.0},
            {"protocol_id": "P25", "name": "Backsheet Chalking Test", "category": "degradation",
             "description": "Backsheet surface degradation",
             "standard_reference": "IEC 62788-2-1:2021", "estimated_duration_hours": 1.0},
            {"protocol_id": "P26", "name": "Junction Box Degradation", "category": "degradation",
             "description": "Junction box integrity evaluation",
             "standard_reference": "IEC 62790:2020", "estimated_duration_hours": 2.0},
            {"protocol_id": "P27", "name": "Long-term Outdoor Exposure", "category": "degradation",
             "description": "Natural weathering monitoring",
             "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 8760.0},

            # ENVIRONMENTAL TESTING (P28-P39)
            {"protocol_id": "P28", "name": "Humidity Freeze Test", "category": "environmental",
             "description": "Humidity freeze cycle resistance",
             "standard_reference": "IEC 61215-2:2021 MQT 12", "estimated_duration_hours": 240.0},
            {"protocol_id": "P29", "name": "Damp Heat Test (1000h)", "category": "environmental",
             "description": "85C/85% RH for 1000 hours",
             "standard_reference": "IEC 61215-2:2021 MQT 13", "estimated_duration_hours": 1000.0},
            {"protocol_id": "P30", "name": "Damp Heat Extended (2000h)", "category": "environmental",
             "description": "Extended damp heat test",
             "standard_reference": "IEC 61215-2:2021", "estimated_duration_hours": 2000.0},
            {"protocol_id": "P31", "name": "Thermal Cycling Test", "category": "environmental",
             "description": "Temperature cycling -40C to +85C",
             "standard_reference": "IEC 61215-2:2021 MQT 11", "estimated_duration_hours": 800.0},
            {"protocol_id": "P32", "name": "Salt Mist Corrosion Test", "category": "environmental",
             "description": "Salt spray exposure test",
             "standard_reference": "IEC 61701:2020", "estimated_duration_hours": 500.0},
            {"protocol_id": "P33", "name": "Ammonia Corrosion Test", "category": "environmental",
             "description": "Ammonia exposure test",
             "standard_reference": "IEC 62716:2013", "estimated_duration_hours": 500.0},
            {"protocol_id": "P34", "name": "Sand/Dust Abrasion Test", "category": "environmental",
             "description": "Sand and dust abrasion resistance",
             "standard_reference": "IEC 60068-2-68:1994", "estimated_duration_hours": 4.0},
            {"protocol_id": "P35", "name": "SO2/H2S Corrosion Test", "category": "environmental",
             "description": "Sulfur compound exposure",
             "standard_reference": "IEC 60068-2-42:2003", "estimated_duration_hours": 240.0},
            {"protocol_id": "P36", "name": "Desert Climate Simulation", "category": "environmental",
             "description": "High temp, low humidity, UV stress",
             "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 720.0},
            {"protocol_id": "P37", "name": "Tropical Climate Simulation", "category": "environmental",
             "description": "High humidity tropical environment",
             "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 720.0},
            {"protocol_id": "P38", "name": "Snow Load Test", "category": "environmental",
             "description": "Static load test for snow",
             "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 4.0},
            {"protocol_id": "P39", "name": "UV Exposure Test", "category": "environmental",
             "description": "Accelerated UV exposure",
             "standard_reference": "IEC 61215-2:2021 MQT 10", "estimated_duration_hours": 120.0},

            # MECHANICAL TESTING (P40-P47)
            {"protocol_id": "P40", "name": "Mechanical Load Test", "category": "mechanical",
             "description": "Static and cyclic mechanical load",
             "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 8.0},
            {"protocol_id": "P41", "name": "Dynamic Mechanical Load", "category": "mechanical",
             "description": "Dynamic loading cycles",
             "standard_reference": "IEC TS 62782:2016", "estimated_duration_hours": 24.0},
            {"protocol_id": "P42", "name": "Hail Impact Test", "category": "mechanical",
             "description": "Ice ball impact resistance",
             "standard_reference": "IEC 61215-2:2021 MQT 17", "estimated_duration_hours": 2.0},
            {"protocol_id": "P43", "name": "Wind Load Simulation", "category": "mechanical",
             "description": "Cyclic wind load simulation",
             "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 4.0},
            {"protocol_id": "P44", "name": "Module Twist Test", "category": "mechanical",
             "description": "Torsional stress test",
             "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 2.0},
            {"protocol_id": "P45", "name": "Vibration Test", "category": "mechanical",
             "description": "Transportation vibration simulation",
             "standard_reference": "IEC 60068-2-6:2007", "estimated_duration_hours": 6.0},
            {"protocol_id": "P46", "name": "Frame/Mounting Stress Test", "category": "mechanical",
             "description": "Mounting point load test",
             "standard_reference": "IEC 61215-2:2021", "estimated_duration_hours": 4.0},
            {"protocol_id": "P47", "name": "Robustness of Terminations", "category": "mechanical",
             "description": "Cable and connector stress test",
             "standard_reference": "IEC 61215-2:2021 MQT 14", "estimated_duration_hours": 2.0},

            # SAFETY TESTING (P48-P54)
            {"protocol_id": "P48", "name": "Wet Leakage Current Test", "category": "safety",
             "description": "Leakage current under wet conditions",
             "standard_reference": "IEC 61215-2:2021 MQT 15", "estimated_duration_hours": 4.0},
            {"protocol_id": "P49", "name": "Insulation Resistance Test", "category": "safety",
             "description": "Dry insulation resistance",
             "standard_reference": "IEC 61215-2:2021 MQT 03", "estimated_duration_hours": 1.0},
            {"protocol_id": "P50", "name": "Dielectric Withstand Test", "category": "safety",
             "description": "High voltage insulation test",
             "standard_reference": "IEC 61730-2:2016 MST 16", "estimated_duration_hours": 1.0},
            {"protocol_id": "P51", "name": "Ground Continuity Test", "category": "safety",
             "description": "Frame grounding verification",
             "standard_reference": "IEC 61730-2:2016 MST 13", "estimated_duration_hours": 0.5},
            {"protocol_id": "P52", "name": "Fire Resistance Test", "category": "safety",
             "description": "Spread of flame test",
             "standard_reference": "IEC 61730-2:2016 MST 23-25", "estimated_duration_hours": 4.0},
            {"protocol_id": "P53", "name": "Reverse Current Overload", "category": "safety",
             "description": "Bypass diode thermal test",
             "standard_reference": "IEC 61215-2:2021 MQT 18", "estimated_duration_hours": 2.0},
            {"protocol_id": "P54", "name": "Impulse Voltage Test", "category": "safety",
             "description": "Lightning impulse withstand",
             "standard_reference": "IEC 61730-2:2016 MST 14", "estimated_duration_hours": 2.0},
        ]

        # Idempotent insert - check each protocol
        for protocol_data in protocols_data:
            existing = db.query(TestProtocol).filter_by(
                protocol_id=protocol_data["protocol_id"]
            ).first()

            if not existing:
                protocol = TestProtocol(**protocol_data, is_active=True)
                db.add(protocol)
                result["count"] += 1
                result["details"].append(f"Added: {protocol_data['protocol_id']}")
            else:
                result["details"].append(f"Exists: {protocol_data['protocol_id']}")

        db.commit()
        result["success"] = True
        logger.info(f"Seeded {result['count']} new protocols")

    except Exception as e:
        db.rollback()
        result["error"] = str(e)
        logger.error(f"Protocol seeding failed: {e}")

    finally:
        db.close()

    return result


# =============================================================================
# QA TEST FUNCTIONS
# =============================================================================


def run_qa_tests() -> Dict[str, Any]:
    """
    Run comprehensive QA tests on the system.

    Returns:
        Dictionary with test results.
    """
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    # Test 1: Database Connection
    results["total_tests"] += 1
    conn_status = check_database_connection()
    test_result = {
        "name": "Database Connection",
        "passed": conn_status["connected"],
        "message": f"Database type: {conn_status['database_type']}" if conn_status["connected"] else conn_status["error"]
    }
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 2: Admin_Seed.py Syntax
    results["total_tests"] += 1
    try:
        import ast
        current_file = Path(__file__)
        ast.parse(current_file.read_text())
        test_result = {"name": "Admin_Seed.py Syntax", "passed": True, "message": "No syntax errors"}
    except SyntaxError as e:
        test_result = {"name": "Admin_Seed.py Syntax", "passed": False, "message": f"Syntax error: {e}"}
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: Models Import
    results["total_tests"] += 1
    try:
        from database import models  # noqa: F401
        test_result = {"name": "Models Import", "passed": True, "message": "All models imported successfully"}
    except Exception as e:
        test_result = {"name": "Models Import", "passed": False, "message": f"Import error: {e}"}
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 4: Schema Comparison
    results["total_tests"] += 1
    schema_result = compare_schemas()
    missing_count = len(schema_result["missing_tables"]) + sum(len(v) for v in schema_result["missing_columns"].values())
    test_result = {
        "name": "Schema Validation",
        "passed": missing_count == 0,
        "message": f"Match: {schema_result['match_percentage']:.1f}%, Missing items: {missing_count}"
    }
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 5: Protocol Count
    results["total_tests"] += 1
    try:
        db, error = get_database_session()
        if error:
            raise Exception(error)
        from database import TestProtocol
        count = db.query(TestProtocol).count()
        db.close()
        test_result = {
            "name": "Protocol Count",
            "passed": count == 54,
            "message": f"Protocol count: {count}/54"
        }
    except Exception as e:
        test_result = {"name": "Protocol Count", "passed": False, "message": f"Error: {e}"}
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 6: Critical Tables Exist
    results["total_tests"] += 1
    critical_tables = ["users", "service_requests", "samples", "test_protocols"]
    missing = [t for t in critical_tables if not check_table_exists(t)]
    test_result = {
        "name": "Critical Tables",
        "passed": len(missing) == 0,
        "message": "All critical tables exist" if len(missing) == 0 else f"Missing: {missing}"
    }
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 7: Samples Table Columns
    results["total_tests"] += 1
    required_cols = ["sample_id", "project_id", "status", "service_request_id"]
    if check_table_exists("samples"):
        missing_cols = [c for c in required_cols if not check_column_exists("samples", c)]
        test_result = {
            "name": "Samples Table Columns",
            "passed": len(missing_cols) == 0,
            "message": "All required columns exist" if len(missing_cols) == 0 else f"Missing: {missing_cols}"
        }
    else:
        test_result = {"name": "Samples Table Columns", "passed": False, "message": "Samples table does not exist"}
    results["tests"].append(test_result)
    if test_result["passed"]:
        results["passed"] += 1
    else:
        results["failed"] += 1

    return results


# =============================================================================
# UI RENDERING FUNCTIONS
# =============================================================================


def render_database_status():
    """Render database connection status section."""
    st.markdown("## Database Status")

    status = check_database_connection()

    col1, col2, col3 = st.columns(3)

    with col1:
        if status["connected"]:
            st.success("Connected")
        else:
            st.error("Disconnected")

    with col2:
        st.info(f"Type: {status['database_type']}")

    with col3:
        if status.get("details", {}).get("url"):
            st.caption(f"Host: {status['details']['url']}")

    if status["error"]:
        st.error(f"Error: {status['error']}")


def render_schema_validation():
    """Render schema validation section."""
    st.markdown("## Schema Validation")

    if st.button("Run Schema Comparison", key="schema_compare"):
        with st.spinner("Comparing schemas..."):
            result = compare_schemas()

        if result["error"]:
            st.error(f"Error: {result['error']}")
            return

        # Display match percentage
        st.metric("Schema Match", f"{result['match_percentage']:.1f}%")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Missing Tables")
            if result["missing_tables"]:
                for table in result["missing_tables"]:
                    st.warning(f"Missing: {table}")
            else:
                st.success("All expected tables exist")

        with col2:
            st.markdown("### Missing Columns")
            if result["missing_columns"]:
                for table, columns in result["missing_columns"].items():
                    st.warning(f"**{table}**: {', '.join(columns)}")
            else:
                st.success("All expected columns exist")


def render_migrations():
    """Render migrations management section."""
    st.markdown("## Migrations")

    migrations = get_migration_definitions()

    # Group migrations by category
    schema_migrations = [m for m in migrations if m.get("category") == "schema"]
    column_migrations = [m for m in migrations if m.get("category") == "columns"]

    st.markdown("### Schema Migrations")
    for migration in schema_migrations:
        with st.expander(f"{migration['id']}: {migration['name']}"):
            st.markdown(f"**Description:** {migration['description']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Run UP", key=f"up_{migration['id']}"):
                    with st.spinner("Running migration..."):
                        result = run_migration_up(migration)
                    if result["success"]:
                        st.success("Migration completed!")
                    else:
                        st.error(f"Failed: {result['error']}")
                    for msg in result["messages"]:
                        st.caption(msg)

            with col2:
                if st.button("Rollback", key=f"down_{migration['id']}"):
                    with st.spinner("Rolling back..."):
                        result = run_migration_down(migration)
                    if result["success"]:
                        st.success("Rollback completed!")
                    else:
                        st.error(f"Failed: {result['error']}")
                    for msg in result["messages"]:
                        st.caption(msg)

    st.markdown("### Column Migrations")
    for migration in column_migrations:
        with st.expander(f"{migration['id']}: {migration['name']}"):
            st.markdown(f"**Description:** {migration['description']}")

            if "up_columns" in migration:
                st.caption(f"Adds: {len(migration['up_columns'])} columns")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Run UP", key=f"up_{migration['id']}"):
                    with st.spinner("Running migration..."):
                        result = run_migration_up(migration)
                    if result["success"]:
                        st.success("Migration completed!")
                    else:
                        st.error(f"Failed: {result['error']}")
                    for msg in result["messages"]:
                        st.caption(msg)

            with col2:
                if st.button("Rollback", key=f"down_{migration['id']}"):
                    with st.spinner("Rolling back..."):
                        result = run_migration_down(migration)
                    if result["success"]:
                        st.success("Rollback completed!")
                    else:
                        st.error(f"Failed: {result['error']}")
                    for msg in result["messages"]:
                        st.caption(msg)

    st.markdown("### Batch Operations")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Run ALL Migrations", type="primary"):
            st.warning("Running all migrations...")
            progress = st.progress(0)
            results = []

            for i, migration in enumerate(migrations):
                result = run_migration_up(migration)
                results.append((migration["id"], result["success"]))
                progress.progress((i + 1) / len(migrations))

            success_count = sum(1 for _, success in results if success)
            st.success(f"Completed: {success_count}/{len(migrations)} migrations")

    with col2:
        st.warning("Use rollback with caution!")


def render_protocol_seeding():
    """Render protocol seeding section."""
    st.markdown("## Protocol Seeding")

    # Check current protocol count
    db, error = get_database_session()
    if error:
        st.error(error)
        return

    try:
        from database import TestProtocol
        count = db.query(TestProtocol).count()
        db.close()
    except Exception as e:
        st.error(f"Error checking protocols: {e}")
        count = 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Current Protocol Count", f"{count}/54")

    with col2:
        if count == 54:
            st.success("All protocols seeded")
        elif count == 0:
            st.warning("No protocols - seeding required")
        else:
            st.info(f"Partial: {54 - count} protocols missing")

    st.divider()

    if st.button("Seed All 54 Protocols", type="primary"):
        with st.spinner("Seeding protocols..."):
            result = seed_test_protocols()

        if result["success"]:
            st.success(f"Seeded {result['count']} new protocols!")
            if result["count"] == 0:
                st.info("All protocols already exist")
            st.balloons()
        else:
            st.error(f"Seeding failed: {result['error']}")

        with st.expander("Details"):
            for detail in result["details"]:
                st.caption(detail)

    # Protocol breakdown
    with st.expander("Protocol Breakdown (54 Total)"):
        st.markdown("""
        | Category | Range | Count |
        |----------|-------|-------|
        | Performance | P1-P12 | 12 |
        | Degradation | P13-P27 | 15 |
        | Environmental | P28-P39 | 12 |
        | Mechanical | P40-P47 | 8 |
        | Safety | P48-P54 | 7 |
        | **Total** | | **54** |
        """)


def render_qa_tests():
    """Render QA testing section."""
    st.markdown("## QA Testing")

    if st.button("Run All QA Tests", type="primary"):
        with st.spinner("Running QA tests..."):
            results = run_qa_tests()

        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tests", results["total_tests"])
        with col2:
            st.metric("Passed", results["passed"])
        with col3:
            st.metric("Failed", results["failed"])

        # Detailed results
        st.divider()

        for test in results["tests"]:
            if test["passed"]:
                st.success(f"PASS: {test['name']} - {test['message']}")
            else:
                st.error(f"FAIL: {test['name']} - {test['message']}")

        # Overall status
        if results["failed"] == 0:
            st.balloons()
            st.success("All QA tests passed!")
        else:
            st.warning(f"{results['failed']} test(s) need attention")


def render_danger_zone():
    """Render danger zone with destructive operations."""
    st.markdown("## Danger Zone")
    st.error("These operations can cause data loss. Use with extreme caution!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reset Database", type="secondary"):
            st.warning("This will DROP ALL TABLES and recreate them!")
            st.error("NOT IMPLEMENTED - Use Alembic for database reset")

    with col2:
        if st.button("Clear All Data", type="secondary"):
            st.warning("This will DELETE all data but keep tables!")
            st.error("NOT IMPLEMENTED - Manual SQL required")


# =============================================================================
# MAIN APPLICATION
# =============================================================================


def main():
    """Main application entry point."""
    st.title("Admin - Database Management")
    st.caption("Version 2.0.0 | Last updated: 2024")

    # Warning banner
    st.warning(
        "This is an administrative page. Changes here affect the database directly. "
        "Always backup before running migrations."
    )

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Database Status",
        "Schema Validation",
        "Migrations",
        "Protocol Seeding",
        "QA Tests",
        "Danger Zone"
    ])

    with tab1:
        render_database_status()

    with tab2:
        render_schema_validation()

    with tab3:
        render_migrations()

    with tab4:
        render_protocol_seeding()

    with tab5:
        render_qa_tests()

    with tab6:
        render_danger_zone()


if __name__ == "__main__":
    main()
