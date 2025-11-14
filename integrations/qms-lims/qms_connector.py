"""
QMS Connector
Quality Management System integration with NC register, CAPA tracking, and document control
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
import hashlib

logger = logging.getLogger(__name__)


class NCStatus(Enum):
    """Non-Conformance status"""
    OPEN = "open"
    INVESTIGATION = "investigation"
    ACTION_PLAN = "action_plan"
    VERIFICATION = "verification"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CAPAStatus(Enum):
    """CAPA (Corrective/Preventive Action) status"""
    IDENTIFIED = "identified"
    ANALYSIS = "analysis"
    ACTION_PLANNED = "action_planned"
    IMPLEMENTING = "implementing"
    VERIFICATION = "verification"
    EFFECTIVENESS_CHECK = "effectiveness_check"
    COMPLETED = "completed"
    CLOSED = "closed"


class DocumentStatus(Enum):
    """Document status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    OBSOLETE = "obsolete"
    SUPERSEDED = "superseded"


class Severity(Enum):
    """Issue severity"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class NonConformance:
    """Non-Conformance record"""
    nc_id: str
    nc_number: str
    title: str
    description: str
    detected_date: datetime
    detected_by: str
    area: str  # Lab area, process, etc.
    severity: Severity
    status: NCStatus
    root_cause: Optional[str] = None
    containment_actions: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    target_closure_date: Optional[datetime] = None
    actual_closure_date: Optional[datetime] = None
    related_documents: List[str] = field(default_factory=list)
    related_capas: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'nc_id': self.nc_id,
            'nc_number': self.nc_number,
            'title': self.title,
            'description': self.description,
            'detected_date': self.detected_date.isoformat(),
            'detected_by': self.detected_by,
            'area': self.area,
            'severity': self.severity.value,
            'status': self.status.value,
            'root_cause': self.root_cause,
            'containment_actions': self.containment_actions,
            'assigned_to': self.assigned_to,
            'target_closure_date': self.target_closure_date.isoformat() if self.target_closure_date else None,
            'actual_closure_date': self.actual_closure_date.isoformat() if self.actual_closure_date else None,
            'related_documents': self.related_documents,
            'related_capas': self.related_capas,
            'metadata': self.metadata
        }


@dataclass
class CAPA:
    """Corrective/Preventive Action record"""
    capa_id: str
    capa_number: str
    title: str
    description: str
    capa_type: str  # corrective, preventive
    initiated_date: datetime
    initiated_by: str
    source_nc_id: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    proposed_action: str = ""
    action_owner: Optional[str] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    status: CAPAStatus = CAPAStatus.IDENTIFIED
    effectiveness_verified: bool = False
    verification_date: Optional[datetime] = None
    verification_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'capa_id': self.capa_id,
            'capa_number': self.capa_number,
            'title': self.title,
            'description': self.description,
            'capa_type': self.capa_type,
            'initiated_date': self.initiated_date.isoformat(),
            'initiated_by': self.initiated_by,
            'source_nc_id': self.source_nc_id,
            'root_cause_analysis': self.root_cause_analysis,
            'proposed_action': self.proposed_action,
            'action_owner': self.action_owner,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'status': self.status.value,
            'effectiveness_verified': self.effectiveness_verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_notes': self.verification_notes,
            'metadata': self.metadata
        }


@dataclass
class ControlledDocument:
    """Controlled document record"""
    document_id: str
    document_number: str
    title: str
    document_type: str  # SOP, protocol, work instruction, etc.
    version: str
    revision_history: List[Dict] = field(default_factory=list)
    status: DocumentStatus = DocumentStatus.DRAFT
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    owner: str = ""
    approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    file_path: str = ""
    file_hash: str = ""
    access_level: str = "internal"
    training_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'document_id': self.document_id,
            'document_number': self.document_number,
            'title': self.title,
            'document_type': self.document_type,
            'version': self.version,
            'revision_history': self.revision_history,
            'status': self.status.value,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'owner': self.owner,
            'approver': self.approver,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'access_level': self.access_level,
            'training_required': self.training_required,
            'metadata': self.metadata
        }


class QMSConnector:
    """
    Quality Management System connector
    """

    def __init__(self, db_path: str = "qms.db"):
        """
        Initialize QMS connector

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"QMSConnector initialized with database: {db_path}")

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

            # Non-conformances table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS non_conformances (
                    nc_id TEXT PRIMARY KEY,
                    nc_number TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    detected_date TEXT NOT NULL,
                    detected_by TEXT NOT NULL,
                    area TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    root_cause TEXT,
                    containment_actions TEXT,
                    assigned_to TEXT,
                    target_closure_date TEXT,
                    actual_closure_date TEXT,
                    related_documents TEXT,
                    related_capas TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # CAPAs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS capas (
                    capa_id TEXT PRIMARY KEY,
                    capa_number TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    capa_type TEXT NOT NULL,
                    initiated_date TEXT NOT NULL,
                    initiated_by TEXT NOT NULL,
                    source_nc_id TEXT,
                    root_cause_analysis TEXT,
                    proposed_action TEXT,
                    action_owner TEXT,
                    target_completion_date TEXT,
                    actual_completion_date TEXT,
                    status TEXT NOT NULL,
                    effectiveness_verified INTEGER DEFAULT 0,
                    verification_date TEXT,
                    verification_notes TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_nc_id) REFERENCES non_conformances(nc_id)
                )
            """)

            # Controlled documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS controlled_documents (
                    document_id TEXT PRIMARY KEY,
                    document_number TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    revision_history TEXT,
                    status TEXT NOT NULL,
                    effective_date TEXT,
                    review_date TEXT,
                    next_review_date TEXT,
                    owner TEXT,
                    approver TEXT,
                    approval_date TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    access_level TEXT DEFAULT 'internal',
                    training_required INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Document access log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_access_log (
                    log_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (document_id) REFERENCES controlled_documents(document_id)
                )
            """)

            # Quality metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    metric_id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    target_value REAL,
                    measurement_date TEXT NOT NULL,
                    unit TEXT,
                    category TEXT,
                    notes TEXT
                )
            """)

            # Audit trail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qms_audit_trail (
                    audit_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    changes TEXT,
                    notes TEXT
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nc_status ON non_conformances(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nc_severity ON non_conformances(severity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_capa_status ON capas(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_status ON controlled_documents(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_number ON controlled_documents(document_number)")

            logger.info("QMS database schema initialized")

    def create_non_conformance(
        self,
        title: str,
        description: str,
        detected_by: str,
        area: str,
        severity: Severity,
        containment_actions: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> NonConformance:
        """
        Create a non-conformance record

        Args:
            title: NC title
            description: NC description
            detected_by: User who detected the NC
            area: Area where NC was detected
            severity: Severity level
            containment_actions: Immediate containment actions
            metadata: Additional metadata

        Returns:
            NonConformance object
        """
        # Generate NC number
        nc_number = self._generate_nc_number()

        nc = NonConformance(
            nc_id=str(uuid.uuid4()),
            nc_number=nc_number,
            title=title,
            description=description,
            detected_date=datetime.now(timezone.utc),
            detected_by=detected_by,
            area=area,
            severity=severity,
            status=NCStatus.OPEN,
            root_cause=None,
            containment_actions=containment_actions or [],
            assigned_to=None,
            target_closure_date=None,
            actual_closure_date=None,
            related_documents=[],
            related_capas=[],
            metadata=metadata or {}
        )

        self._store_nc(nc)
        self._log_audit('non_conformance', nc.nc_id, 'created', detected_by)

        logger.info(f"Created non-conformance: {nc.nc_number}")
        return nc

    def _generate_nc_number(self) -> str:
        """Generate unique NC number"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM non_conformances")
            count = cursor.fetchone()['count']

        year = datetime.now().year
        return f"NC-{year}-{count + 1:04d}"

    def _store_nc(self, nc: NonConformance):
        """Store non-conformance in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO non_conformances
                (nc_id, nc_number, title, description, detected_date, detected_by, area,
                 severity, status, root_cause, containment_actions, assigned_to,
                 target_closure_date, actual_closure_date, related_documents,
                 related_capas, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nc.nc_id,
                nc.nc_number,
                nc.title,
                nc.description,
                nc.detected_date.isoformat(),
                nc.detected_by,
                nc.area,
                nc.severity.value,
                nc.status.value,
                nc.root_cause,
                json.dumps(nc.containment_actions),
                nc.assigned_to,
                nc.target_closure_date.isoformat() if nc.target_closure_date else None,
                nc.actual_closure_date.isoformat() if nc.actual_closure_date else None,
                json.dumps(nc.related_documents),
                json.dumps(nc.related_capas),
                json.dumps(nc.metadata),
                datetime.now(timezone.utc).isoformat()
            ))

    def create_capa(
        self,
        title: str,
        description: str,
        capa_type: str,
        initiated_by: str,
        source_nc_id: Optional[str] = None,
        proposed_action: str = "",
        target_completion_date: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> CAPA:
        """
        Create a CAPA record

        Args:
            title: CAPA title
            description: CAPA description
            capa_type: Type (corrective, preventive)
            initiated_by: User who initiated CAPA
            source_nc_id: Source NC ID if applicable
            proposed_action: Proposed action
            target_completion_date: Target completion date
            metadata: Additional metadata

        Returns:
            CAPA object
        """
        capa_number = self._generate_capa_number()

        capa = CAPA(
            capa_id=str(uuid.uuid4()),
            capa_number=capa_number,
            title=title,
            description=description,
            capa_type=capa_type,
            initiated_date=datetime.now(timezone.utc),
            initiated_by=initiated_by,
            source_nc_id=source_nc_id,
            root_cause_analysis=None,
            proposed_action=proposed_action,
            action_owner=None,
            target_completion_date=target_completion_date,
            actual_completion_date=None,
            status=CAPAStatus.IDENTIFIED,
            effectiveness_verified=False,
            verification_date=None,
            verification_notes=None,
            metadata=metadata or {}
        )

        self._store_capa(capa)
        self._log_audit('capa', capa.capa_id, 'created', initiated_by)

        # Link to NC if applicable
        if source_nc_id:
            self._link_capa_to_nc(source_nc_id, capa.capa_id)

        logger.info(f"Created CAPA: {capa.capa_number}")
        return capa

    def _generate_capa_number(self) -> str:
        """Generate unique CAPA number"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM capas")
            count = cursor.fetchone()['count']

        year = datetime.now().year
        return f"CAPA-{year}-{count + 1:04d}"

    def _store_capa(self, capa: CAPA):
        """Store CAPA in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO capas
                (capa_id, capa_number, title, description, capa_type, initiated_date,
                 initiated_by, source_nc_id, root_cause_analysis, proposed_action,
                 action_owner, target_completion_date, actual_completion_date, status,
                 effectiveness_verified, verification_date, verification_notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capa.capa_id,
                capa.capa_number,
                capa.title,
                capa.description,
                capa.capa_type,
                capa.initiated_date.isoformat(),
                capa.initiated_by,
                capa.source_nc_id,
                capa.root_cause_analysis,
                capa.proposed_action,
                capa.action_owner,
                capa.target_completion_date.isoformat() if capa.target_completion_date else None,
                capa.actual_completion_date.isoformat() if capa.actual_completion_date else None,
                capa.status.value,
                1 if capa.effectiveness_verified else 0,
                capa.verification_date.isoformat() if capa.verification_date else None,
                capa.verification_notes,
                json.dumps(capa.metadata)
            ))

    def _link_capa_to_nc(self, nc_id: str, capa_id: str):
        """Link CAPA to NC"""
        nc = self.get_non_conformance(nc_id)
        if nc:
            nc.related_capas.append(capa_id)
            self._store_nc(nc)

    def create_controlled_document(
        self,
        document_number: str,
        title: str,
        document_type: str,
        version: str,
        owner: str,
        file_path: str = "",
        training_required: bool = False,
        metadata: Optional[Dict] = None
    ) -> ControlledDocument:
        """
        Create a controlled document record

        Args:
            document_number: Document number
            title: Document title
            document_type: Document type
            version: Version number
            owner: Document owner
            file_path: Path to document file
            training_required: Whether training is required
            metadata: Additional metadata

        Returns:
            ControlledDocument object
        """
        # Calculate file hash if file exists
        file_hash = ""
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            except:
                pass

        document = ControlledDocument(
            document_id=str(uuid.uuid4()),
            document_number=document_number,
            title=title,
            document_type=document_type,
            version=version,
            revision_history=[{
                'version': version,
                'date': datetime.now(timezone.utc).isoformat(),
                'changes': 'Initial version',
                'author': owner
            }],
            status=DocumentStatus.DRAFT,
            effective_date=None,
            review_date=None,
            next_review_date=None,
            owner=owner,
            approver=None,
            approval_date=None,
            file_path=file_path,
            file_hash=file_hash,
            access_level='internal',
            training_required=training_required,
            metadata=metadata or {}
        )

        self._store_document(document)
        self._log_audit('document', document.document_id, 'created', owner)

        logger.info(f"Created controlled document: {document.document_number}")
        return document

    def _store_document(self, document: ControlledDocument):
        """Store document in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO controlled_documents
                (document_id, document_number, title, document_type, version,
                 revision_history, status, effective_date, review_date, next_review_date,
                 owner, approver, approval_date, file_path, file_hash, access_level,
                 training_required, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document.document_id,
                document.document_number,
                document.title,
                document.document_type,
                document.version,
                json.dumps(document.revision_history),
                document.status.value,
                document.effective_date.isoformat() if document.effective_date else None,
                document.review_date.isoformat() if document.review_date else None,
                document.next_review_date.isoformat() if document.next_review_date else None,
                document.owner,
                document.approver,
                document.approval_date.isoformat() if document.approval_date else None,
                document.file_path,
                document.file_hash,
                document.access_level,
                1 if document.training_required else 0,
                json.dumps(document.metadata)
            ))

    def approve_document(
        self,
        document_id: str,
        approver: str,
        effective_date: Optional[datetime] = None
    ):
        """Approve a document"""
        document = self.get_document(document_id)
        if document:
            document.status = DocumentStatus.APPROVED
            document.approver = approver
            document.approval_date = datetime.now(timezone.utc)
            document.effective_date = effective_date or datetime.now(timezone.utc)
            document.next_review_date = document.effective_date + timedelta(days=365)

            self._store_document(document)
            self._log_audit('document', document_id, 'approved', approver)

    def _log_audit(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        performed_by: str,
        changes: Optional[Dict] = None
    ):
        """Log audit trail"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qms_audit_trail
                (audit_id, entity_type, entity_id, action, performed_by, timestamp, changes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                entity_type,
                entity_id,
                action,
                performed_by,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(changes or {}),
                ""
            ))

    def get_non_conformance(self, nc_id: str) -> Optional[NonConformance]:
        """Get NC by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM non_conformances WHERE nc_id = ?", (nc_id,))
            row = cursor.fetchone()

            if row:
                return NonConformance(
                    nc_id=row['nc_id'],
                    nc_number=row['nc_number'],
                    title=row['title'],
                    description=row['description'],
                    detected_date=datetime.fromisoformat(row['detected_date']),
                    detected_by=row['detected_by'],
                    area=row['area'],
                    severity=Severity(row['severity']),
                    status=NCStatus(row['status']),
                    root_cause=row['root_cause'],
                    containment_actions=json.loads(row['containment_actions']),
                    assigned_to=row['assigned_to'],
                    target_closure_date=datetime.fromisoformat(row['target_closure_date']) if row['target_closure_date'] else None,
                    actual_closure_date=datetime.fromisoformat(row['actual_closure_date']) if row['actual_closure_date'] else None,
                    related_documents=json.loads(row['related_documents']),
                    related_capas=json.loads(row['related_capas']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_document(self, document_id: str) -> Optional[ControlledDocument]:
        """Get document by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM controlled_documents WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()

            if row:
                return ControlledDocument(
                    document_id=row['document_id'],
                    document_number=row['document_number'],
                    title=row['title'],
                    document_type=row['document_type'],
                    version=row['version'],
                    revision_history=json.loads(row['revision_history']),
                    status=DocumentStatus(row['status']),
                    effective_date=datetime.fromisoformat(row['effective_date']) if row['effective_date'] else None,
                    review_date=datetime.fromisoformat(row['review_date']) if row['review_date'] else None,
                    next_review_date=datetime.fromisoformat(row['next_review_date']) if row['next_review_date'] else None,
                    owner=row['owner'],
                    approver=row['approver'],
                    approval_date=datetime.fromisoformat(row['approval_date']) if row['approval_date'] else None,
                    file_path=row['file_path'],
                    file_hash=row['file_hash'],
                    access_level=row['access_level'],
                    training_required=bool(row['training_required']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get QMS statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # NCs by status
            cursor.execute("SELECT status, COUNT(*) as count FROM non_conformances GROUP BY status")
            stats['ncs_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # CAPAs by status
            cursor.execute("SELECT status, COUNT(*) as count FROM capas GROUP BY status")
            stats['capas_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # Documents by status
            cursor.execute("SELECT status, COUNT(*) as count FROM controlled_documents GROUP BY status")
            stats['documents_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            return stats


if __name__ == "__main__":
    # Example usage
    qms = QMSConnector()

    # Create non-conformance
    nc = qms.create_non_conformance(
        title="Temperature out of range",
        description="Chamber temperature exceeded acceptable range during test",
        detected_by="tech001",
        area="Testing Lab A",
        severity=Severity.MAJOR,
        containment_actions=["Test halted", "Equipment inspection scheduled"]
    )

    print(f"Created NC: {nc.nc_number}")

    # Create CAPA
    capa = qms.create_capa(
        title="Improve temperature monitoring",
        description="Implement enhanced monitoring for thermal chambers",
        capa_type="corrective",
        initiated_by="qm001",
        source_nc_id=nc.nc_id,
        target_completion_date=datetime.now(timezone.utc) + timedelta(days=30)
    )

    print(f"Created CAPA: {capa.capa_number}")

    # Create document
    doc = qms.create_controlled_document(
        document_number="SOP-001",
        title="Standard Operating Procedure for Thermal Testing",
        document_type="SOP",
        version="1.0",
        owner="qm001",
        training_required=True
    )

    print(f"Created document: {doc.document_number}")
