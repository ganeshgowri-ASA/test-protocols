"""
Audit Logger
Comprehensive audit logging with user actions, data modifications, and compliance tracking
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    DATA_CREATE = "data_create"
    DATA_READ = "data_read"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    PROTOCOL_EXECUTE = "protocol_execute"
    REPORT_GENERATE = "report_generate"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_EVENT = "compliance_event"


class SeverityLevel(Enum):
    """Severity levels for audit events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents an audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: SeverityLevel
    user_id: str
    session_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str = ""
    user_agent: str = ""
    before_state: Optional[Dict] = None
    after_state: Optional[Dict] = None
    success: bool = True
    error_message: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    compliance_flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'success': self.success,
            'error_message': self.error_message,
            'tags': self.tags,
            'compliance_flags': self.compliance_flags
        }

    def compute_hash(self) -> str:
        """Compute tamper-proof hash of event"""
        event_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()


@dataclass
class ComplianceReport:
    """Compliance audit report"""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_events: int
    events_by_type: Dict[str, int]
    compliance_violations: List[Dict[str, Any]]
    risk_score: float
    recommendations: List[str]


class AuditLogger:
    """
    Comprehensive audit logging system with compliance tracking
    """

    def __init__(self, db_path: str = "audit_log.db", config: Optional[Dict] = None):
        """
        Initialize audit logger

        Args:
            db_path: Path to SQLite database
            config: Configuration dictionary
        """
        self.db_path = db_path
        self.config = config or {}
        self._initialize_database()
        self.retention_days = self.config.get('retention_days', 2555)  # 7 years default
        logger.info(f"AuditLogger initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Audit events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    before_state TEXT,
                    after_state TEXT,
                    success INTEGER,
                    error_message TEXT,
                    tags TEXT,
                    compliance_flags TEXT,
                    event_hash TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    login_time TEXT NOT NULL,
                    logout_time TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_duration_seconds INTEGER,
                    events_count INTEGER DEFAULT 0
                )
            """)

            # Compliance violations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_violations (
                    violation_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    detected_at TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0,
                    resolved_at TEXT,
                    resolved_by TEXT,
                    resolution_notes TEXT,
                    FOREIGN KEY (event_id) REFERENCES audit_events(event_id)
                )
            """)

            # Data modifications table (detailed change tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_modifications (
                    modification_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES audit_events(event_id)
                )
            """)

            # Audit trail integrity checks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS integrity_checks (
                    check_id TEXT PRIMARY KEY,
                    check_time TEXT NOT NULL,
                    events_checked INTEGER,
                    integrity_valid INTEGER,
                    anomalies_detected TEXT,
                    check_hash TEXT
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON audit_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resource ON audit_events(resource_type, resource_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)")

            logger.info("Audit database schema initialized")

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        session_id: str = "",
        details: Optional[Dict] = None,
        severity: SeverityLevel = SeverityLevel.INFO,
        before_state: Optional[Dict] = None,
        after_state: Optional[Dict] = None,
        ip_address: str = "",
        user_agent: str = "",
        success: bool = True,
        error_message: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Log an audit event

        Args:
            event_type: Type of event
            action: Action description
            resource_type: Type of resource affected
            resource_id: ID of resource
            user_id: User who performed action
            session_id: User session ID
            details: Additional details
            severity: Severity level
            before_state: State before action
            after_state: State after action
            ip_address: IP address
            user_agent: User agent string
            success: Whether action succeeded
            error_message: Error message if failed
            tags: Event tags

        Returns:
            Event ID
        """
        try:
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                session_id=session_id or str(uuid.uuid4()),
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                before_state=before_state,
                after_state=after_state,
                success=success,
                error_message=error_message,
                tags=tags or [],
                compliance_flags=self._check_compliance(event_type, action, details or {})
            )

            # Compute event hash
            event_hash = event.compute_hash()

            # Store event
            self._store_event(event, event_hash)

            # Check for compliance violations
            self._check_violations(event)

            # Update session
            if session_id:
                self._update_session(session_id)

            logger.info(f"Logged audit event: {event.event_id}")
            return event.event_id

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            raise

    def _store_event(self, event: AuditEvent, event_hash: str):
        """Store audit event in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_events
                (event_id, timestamp, event_type, severity, user_id, session_id,
                 action, resource_type, resource_id, details, ip_address, user_agent,
                 before_state, after_state, success, error_message, tags,
                 compliance_flags, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.severity.value,
                event.user_id,
                event.session_id,
                event.action,
                event.resource_type,
                event.resource_id,
                json.dumps(event.details),
                event.ip_address,
                event.user_agent,
                json.dumps(event.before_state) if event.before_state else None,
                json.dumps(event.after_state) if event.after_state else None,
                1 if event.success else 0,
                event.error_message,
                json.dumps(event.tags),
                json.dumps(event.compliance_flags),
                event_hash
            ))

    def _check_compliance(
        self,
        event_type: AuditEventType,
        action: str,
        details: Dict
    ) -> Dict[str, bool]:
        """Check compliance requirements for event"""
        flags = {
            '21_cfr_part_11': False,
            'gdpr_compliant': False,
            'iso_17025': False,
            'gxp_compliant': False
        }

        # Simple compliance checks (can be extended)
        if event_type in [AuditEventType.DATA_CREATE, AuditEventType.DATA_UPDATE, AuditEventType.DATA_DELETE]:
            flags['21_cfr_part_11'] = True
            flags['iso_17025'] = True

        if event_type == AuditEventType.USER_LOGIN:
            flags['gdpr_compliant'] = True

        return flags

    def _check_violations(self, event: AuditEvent):
        """Check for compliance violations"""
        violations = []

        # Check for unauthorized access patterns
        if event.event_type == AuditEventType.SECURITY_EVENT and not event.success:
            violations.append({
                'type': 'unauthorized_access',
                'severity': 'high',
                'description': 'Failed security event detected'
            })

        # Check for data deletion without proper authorization
        if event.event_type == AuditEventType.DATA_DELETE:
            if 'authorization' not in event.details:
                violations.append({
                    'type': 'unauthorized_deletion',
                    'severity': 'critical',
                    'description': 'Data deletion without authorization record'
                })

        # Store violations
        for violation in violations:
            self._store_violation(event.event_id, violation)

    def _store_violation(self, event_id: str, violation: Dict):
        """Store compliance violation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO compliance_violations
                (violation_id, event_id, violation_type, severity, description, detected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                event_id,
                violation['type'],
                violation['severity'],
                violation['description'],
                datetime.now(timezone.utc).isoformat()
            ))

    def _update_session(self, session_id: str):
        """Update session event count"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions
                SET events_count = events_count + 1
                WHERE session_id = ?
            """, (session_id,))

    def start_session(
        self,
        user_id: str,
        ip_address: str = "",
        user_agent: str = ""
    ) -> str:
        """
        Start user session

        Args:
            user_id: User ID
            ip_address: IP address
            user_agent: User agent string

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions
                (session_id, user_id, login_time, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                datetime.now(timezone.utc).isoformat(),
                ip_address,
                user_agent
            ))

        # Log login event
        self.log_event(
            event_type=AuditEventType.USER_LOGIN,
            action="User login",
            resource_type="session",
            resource_id=session_id,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        logger.info(f"Started session {session_id} for user {user_id}")
        return session_id

    def end_session(self, session_id: str):
        """End user session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get session info
            cursor.execute("""
                SELECT user_id, login_time FROM user_sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()

            if row:
                login_time = datetime.fromisoformat(row['login_time'])
                logout_time = datetime.now(timezone.utc)
                duration = (logout_time - login_time).total_seconds()

                # Update session
                cursor.execute("""
                    UPDATE user_sessions
                    SET logout_time = ?, session_duration_seconds = ?
                    WHERE session_id = ?
                """, (logout_time.isoformat(), duration, session_id))

                # Log logout event
                self.log_event(
                    event_type=AuditEventType.USER_LOGOUT,
                    action="User logout",
                    resource_type="session",
                    resource_id=session_id,
                    user_id=row['user_id'],
                    session_id=session_id,
                    details={'session_duration': duration}
                )

    def log_data_modification(
        self,
        event_id: str,
        table_name: str,
        record_id: str,
        changes: List[Dict[str, Any]]
    ):
        """
        Log detailed data modifications

        Args:
            event_id: Associated event ID
            table_name: Database table name
            record_id: Record ID
            changes: List of field changes
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for change in changes:
                cursor.execute("""
                    INSERT INTO data_modifications
                    (modification_id, event_id, table_name, record_id, field_name,
                     old_value, new_value, change_type, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    event_id,
                    table_name,
                    record_id,
                    change['field'],
                    change.get('old_value'),
                    change.get('new_value'),
                    change.get('type', 'update'),
                    datetime.now(timezone.utc).isoformat()
                ))

    def query_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        resource_type: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit events

        Args:
            start_time: Start of time range
            end_time: End of time range
            user_id: Filter by user
            event_type: Filter by event type
            resource_type: Filter by resource type
            severity: Filter by severity
            limit: Maximum results

        Returns:
            List of events
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)

            if resource_type:
                query += " AND resource_type = ?"
                params.append(resource_type)

            if severity:
                query += " AND severity = ?"
                params.append(severity.value)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            events = []
            for row in cursor.fetchall():
                events.append(dict(row))

            return events

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> ComplianceReport:
        """
        Generate compliance audit report

        Args:
            start_date: Report period start
            end_date: Report period end

        Returns:
            ComplianceReport object
        """
        events = self.query_events(
            start_time=start_date,
            end_time=end_date,
            limit=100000
        )

        # Count events by type
        events_by_type = {}
        for event in events:
            event_type = event['event_type']
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

        # Get violations
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM compliance_violations
                WHERE detected_at >= ? AND detected_at <= ?
                AND resolved = 0
            """, (start_date.isoformat(), end_date.isoformat()))

            violations = [dict(row) for row in cursor.fetchall()]

        # Calculate risk score
        risk_score = len(violations) * 10  # Simple calculation

        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(timezone.utc),
            period_start=start_date,
            period_end=end_date,
            total_events=len(events),
            events_by_type=events_by_type,
            compliance_violations=violations,
            risk_score=min(risk_score, 100),
            recommendations=self._generate_recommendations(violations)
        )

        return report

    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        if violations:
            recommendations.append("Review and resolve pending compliance violations")

        violation_types = set(v['violation_type'] for v in violations)

        if 'unauthorized_access' in violation_types:
            recommendations.append("Strengthen access controls and authentication")

        if 'unauthorized_deletion' in violation_types:
            recommendations.append("Implement mandatory authorization for data deletion")

        return recommendations

    def verify_integrity(self, event_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Verify audit log integrity

        Args:
            event_ids: Specific events to check (None = check all)

        Returns:
            Verification results
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if event_ids:
                placeholders = ','.join('?' * len(event_ids))
                cursor.execute(f"""
                    SELECT * FROM audit_events WHERE event_id IN ({placeholders})
                """, event_ids)
            else:
                cursor.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT 1000")

            results = {
                'total_checked': 0,
                'valid': 0,
                'invalid': 0,
                'anomalies': []
            }

            for row in cursor.fetchall():
                results['total_checked'] += 1

                # Reconstruct event and verify hash
                event = AuditEvent(
                    event_id=row['event_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    event_type=AuditEventType(row['event_type']),
                    severity=SeverityLevel(row['severity']),
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    action=row['action'],
                    resource_type=row['resource_type'],
                    resource_id=row['resource_id'],
                    details=json.loads(row['details']),
                    ip_address=row['ip_address'] or "",
                    user_agent=row['user_agent'] or "",
                    before_state=json.loads(row['before_state']) if row['before_state'] else None,
                    after_state=json.loads(row['after_state']) if row['after_state'] else None,
                    success=bool(row['success']),
                    error_message=row['error_message'],
                    tags=json.loads(row['tags']),
                    compliance_flags=json.loads(row['compliance_flags'])
                )

                computed_hash = event.compute_hash()

                if computed_hash == row['event_hash']:
                    results['valid'] += 1
                else:
                    results['invalid'] += 1
                    results['anomalies'].append({
                        'event_id': row['event_id'],
                        'reason': 'Hash mismatch',
                        'expected': row['event_hash'],
                        'computed': computed_hash
                    })

            # Store integrity check result
            check_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO integrity_checks
                (check_id, check_time, events_checked, integrity_valid, anomalies_detected, check_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                check_id,
                datetime.now(timezone.utc).isoformat(),
                results['total_checked'],
                1 if results['invalid'] == 0 else 0,
                json.dumps(results['anomalies']),
                hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest()
            ))

            conn.commit()

            return results


if __name__ == "__main__":
    # Example usage
    audit = AuditLogger()

    # Start session
    session_id = audit.start_session(
        user_id="analyst001",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )

    # Log data creation
    event_id = audit.log_event(
        event_type=AuditEventType.DATA_CREATE,
        action="Create test record",
        resource_type="test_result",
        resource_id="TR-2025-001",
        user_id="analyst001",
        session_id=session_id,
        details={
            'protocol_id': 'PVTP-048',
            'test_type': 'thermal_cycling'
        },
        after_state={'status': 'created', 'value': 25.4}
    )

    # Log data modification
    audit.log_event(
        event_type=AuditEventType.DATA_UPDATE,
        action="Update test result",
        resource_type="test_result",
        resource_id="TR-2025-001",
        user_id="analyst001",
        session_id=session_id,
        before_state={'status': 'created', 'value': 25.4},
        after_state={'status': 'validated', 'value': 25.4}
    )

    # Verify integrity
    verification = audit.verify_integrity()
    print(f"Integrity check: {json.dumps(verification, indent=2)}")

    # End session
    audit.end_session(session_id)
