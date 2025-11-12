"""
Database Manager
Handles database connections, queries, and transactions
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: str = "data/pv_testing.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._init_database()

    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent.parent.parent / "database" / "schema.sql"

        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()

            try:
                conn = self.get_connection()
                conn.executescript(schema)
                conn.commit()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
            finally:
                conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute SELECT query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            # Convert rows to dictionaries
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            conn.close()
            return results
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT, UPDATE, DELETE query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected
        except Exception as e:
            logger.error(f"Update execution error: {e}")
            raise

    # ============================================
    # SERVICE REQUEST METHODS
    # ============================================

    def create_service_request(self, data: Dict) -> str:
        """Create new service request"""
        query = """
        INSERT INTO service_requests
        (request_id, customer_name, customer_email, customer_phone, project_name,
         sample_description, requested_protocols, priority, requested_by, due_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        request_id = data.get('request_id', f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        params = (
            request_id,
            data['customer_name'],
            data.get('customer_email'),
            data.get('customer_phone'),
            data.get('project_name'),
            data.get('sample_description'),
            json.dumps(data.get('requested_protocols', [])),
            data.get('priority', 'medium'),
            data.get('requested_by', 1),
            data.get('due_date'),
            data.get('notes')
        )

        self.execute_update(query, params)
        self.log_audit('service_requests', request_id, 'create', data.get('requested_by', 1))
        return request_id

    def get_service_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Get service requests with optional status filter"""
        if status:
            query = "SELECT * FROM service_requests WHERE status = ? ORDER BY requested_date DESC"
            return self.execute_query(query, (status,))
        else:
            query = "SELECT * FROM service_requests ORDER BY requested_date DESC"
            return self.execute_query(query)

    def update_service_request_status(self, request_id: str, status: str, user_id: int = 1):
        """Update service request status"""
        query = """
        UPDATE service_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE request_id = ?
        """
        self.execute_update(query, (status, request_id))
        self.log_audit('service_requests', request_id, 'update', user_id, {'status': status})

    # ============================================
    # INSPECTION METHODS
    # ============================================

    def create_inspection(self, data: Dict) -> str:
        """Create incoming inspection record"""
        query = """
        INSERT INTO incoming_inspections
        (inspection_id, request_id, sample_id, sample_type, manufacturer, model_number,
         serial_number, quantity, condition, visual_inspection_notes, dimensions,
         weight_kg, photos, inspected_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        inspection_id = data.get('inspection_id', f"INS-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        params = (
            inspection_id,
            data.get('request_id'),
            data['sample_id'],
            data.get('sample_type'),
            data.get('manufacturer'),
            data.get('model_number'),
            data.get('serial_number'),
            data.get('quantity', 1),
            data.get('condition'),
            data.get('visual_inspection_notes'),
            json.dumps(data.get('dimensions', {})),
            data.get('weight_kg'),
            json.dumps(data.get('photos', [])),
            data.get('inspected_by', 1)
        )

        self.execute_update(query, params)
        self.log_audit('incoming_inspections', inspection_id, 'create', data.get('inspected_by', 1))
        return inspection_id

    def get_inspections(self, request_id: Optional[str] = None) -> List[Dict]:
        """Get inspection records"""
        if request_id:
            query = "SELECT * FROM incoming_inspections WHERE request_id = ?"
            return self.execute_query(query, (request_id,))
        else:
            query = "SELECT * FROM incoming_inspections ORDER BY inspection_date DESC"
            return self.execute_query(query)

    # ============================================
    # PROTOCOL EXECUTION METHODS
    # ============================================

    def create_protocol_execution(self, data: Dict) -> str:
        """Create protocol execution record"""
        query = """
        INSERT INTO protocol_executions
        (execution_id, protocol_id, protocol_name, protocol_version, request_id,
         inspection_id, equipment_id, sample_id, operator_id, general_data, protocol_inputs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        execution_id = data.get('execution_id', f"EXE-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        params = (
            execution_id,
            data['protocol_id'],
            data['protocol_name'],
            data.get('protocol_version', '1.0'),
            data.get('request_id'),
            data.get('inspection_id'),
            data.get('equipment_id'),
            data.get('sample_id'),
            data.get('operator_id', 1),
            json.dumps(data.get('general_data', {})),
            json.dumps(data.get('protocol_inputs', {}))
        )

        self.execute_update(query, params)
        self.log_audit('protocol_executions', execution_id, 'create', data.get('operator_id', 1))
        return execution_id

    def get_protocol_executions(self, protocol_id: Optional[str] = None) -> List[Dict]:
        """Get protocol execution records"""
        if protocol_id:
            query = "SELECT * FROM protocol_executions WHERE protocol_id = ? ORDER BY created_at DESC"
            return self.execute_query(query, (protocol_id,))
        else:
            query = "SELECT * FROM protocol_executions ORDER BY created_at DESC"
            return self.execute_query(query)

    def update_protocol_status(self, execution_id: str, status: str, user_id: int = 1):
        """Update protocol execution status"""
        query = """
        UPDATE protocol_executions
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE execution_id = ?
        """
        self.execute_update(query, (status, execution_id))
        self.log_audit('protocol_executions', execution_id, 'update', user_id, {'status': status})

    # ============================================
    # MEASUREMENT METHODS
    # ============================================

    def add_measurement(self, data: Dict) -> int:
        """Add measurement record"""
        query = """
        INSERT INTO measurements
        (execution_id, measurement_type, sequence_number, data, unit,
         equipment_used, conditions, operator_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            data['execution_id'],
            data['measurement_type'],
            data.get('sequence_number'),
            json.dumps(data['data']),
            data.get('unit'),
            data.get('equipment_used'),
            json.dumps(data.get('conditions', {})),
            data.get('operator_id', 1)
        )

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        measurement_id = cursor.lastrowid
        conn.close()

        return measurement_id

    def get_measurements(self, execution_id: str) -> List[Dict]:
        """Get measurements for execution"""
        query = """
        SELECT * FROM measurements
        WHERE execution_id = ?
        ORDER BY timestamp, sequence_number
        """
        return self.execute_query(query, (execution_id,))

    # ============================================
    # TRACEABILITY METHODS
    # ============================================

    def get_complete_traceability(self, entity_type: str, entity_id: str) -> Dict:
        """
        Get complete traceability chain for an entity

        Args:
            entity_type: Type of entity ('request', 'inspection', 'execution', 'report')
            entity_id: Entity ID

        Returns:
            Complete traceability information
        """
        traceability = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'chain': []
        }

        if entity_type == 'execution':
            # Get execution details
            exec_query = "SELECT * FROM protocol_executions WHERE execution_id = ?"
            execution = self.execute_query(exec_query, (entity_id,))
            if execution:
                traceability['execution'] = execution[0]

                # Get linked inspection
                if execution[0].get('inspection_id'):
                    insp_query = "SELECT * FROM incoming_inspections WHERE inspection_id = ?"
                    inspection = self.execute_query(insp_query, (execution[0]['inspection_id'],))
                    if inspection:
                        traceability['inspection'] = inspection[0]

                        # Get linked request
                        if inspection[0].get('request_id'):
                            req_query = "SELECT * FROM service_requests WHERE request_id = ?"
                            request = self.execute_query(req_query, (inspection[0]['request_id'],))
                            if request:
                                traceability['request'] = request[0]

                # Get measurements
                traceability['measurements'] = self.get_measurements(entity_id)

                # Get reports
                report_query = "SELECT * FROM reports WHERE execution_id = ?"
                traceability['reports'] = self.execute_query(report_query, (entity_id,))

        return traceability

    # ============================================
    # AUDIT METHODS
    # ============================================

    def log_audit(self, table_name: str, record_id: str, action: str,
                  user_id: int, new_values: Optional[Dict] = None):
        """Log audit trail entry"""
        query = """
        INSERT INTO audit_trail
        (table_name, record_id, action, user_id, new_values)
        VALUES (?, ?, ?, ?, ?)
        """

        params = (
            table_name,
            record_id,
            action,
            user_id,
            json.dumps(new_values) if new_values else None
        )

        try:
            self.execute_update(query, params)
        except Exception as e:
            logger.error(f"Audit logging error: {e}")

    def get_audit_trail(self, table_name: Optional[str] = None,
                        record_id: Optional[str] = None) -> List[Dict]:
        """Get audit trail records"""
        if table_name and record_id:
            query = """
            SELECT * FROM audit_trail
            WHERE table_name = ? AND record_id = ?
            ORDER BY timestamp DESC
            """
            return self.execute_query(query, (table_name, record_id))
        elif table_name:
            query = "SELECT * FROM audit_trail WHERE table_name = ? ORDER BY timestamp DESC"
            return self.execute_query(query, (table_name,))
        else:
            query = "SELECT * FROM audit_trail ORDER BY timestamp DESC LIMIT 1000"
            return self.execute_query(query)

    # ============================================
    # DASHBOARD & ANALYTICS METHODS
    # ============================================

    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        stats = {}

        # Service requests by status
        sr_query = """
        SELECT status, COUNT(*) as count
        FROM service_requests
        GROUP BY status
        """
        stats['service_requests'] = self.execute_query(sr_query)

        # Protocol executions by status
        pe_query = """
        SELECT status, COUNT(*) as count
        FROM protocol_executions
        GROUP BY status
        """
        stats['protocol_executions'] = self.execute_query(pe_query)

        # Recent activity
        activity_query = """
        SELECT protocol_name, status, created_at
        FROM protocol_executions
        ORDER BY created_at DESC
        LIMIT 10
        """
        stats['recent_activity'] = self.execute_query(activity_query)

        # NC register summary
        nc_query = """
        SELECT status, severity, COUNT(*) as count
        FROM nc_register
        GROUP BY status, severity
        """
        stats['nc_summary'] = self.execute_query(nc_query)

        return stats
