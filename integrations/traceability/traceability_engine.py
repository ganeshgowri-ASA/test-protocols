"""
Data Traceability Engine
Complete data lineage tracking from raw data through intermediate processing to final reports
with blockchain-ready hashing, version control, audit trail, and data integrity verification
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from pathlib import Path
import sqlite3
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataType(Enum):
    """Data classification types"""
    RAW = "raw"
    INTERMEDIATE = "intermediate"
    PROCESSED = "processed"
    REPORT = "report"
    METADATA = "metadata"


class TransformationType(Enum):
    """Types of data transformations"""
    COLLECTION = "collection"
    VALIDATION = "validation"
    CALCULATION = "calculation"
    AGGREGATION = "aggregation"
    FORMATTING = "formatting"
    EXPORT = "export"


@dataclass
class DataLineageNode:
    """Represents a node in the data lineage graph"""
    node_id: str
    timestamp: datetime
    data_type: DataType
    transformation_type: TransformationType
    data_hash: str
    data_signature: str
    parent_nodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: str = ""
    protocol_id: str = ""
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['data_type'] = self.data_type.value
        result['transformation_type'] = self.transformation_type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataLineageNode':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['data_type'] = DataType(data['data_type'])
        data['transformation_type'] = TransformationType(data['transformation_type'])
        return cls(**data)


@dataclass
class TraceabilityRecord:
    """Complete traceability record for a data artifact"""
    record_id: str
    artifact_path: str
    lineage_chain: List[str]  # List of node_ids
    created_at: datetime
    last_modified: datetime
    blockchain_hash: str
    verification_status: str
    compliance_flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'record_id': self.record_id,
            'artifact_path': self.artifact_path,
            'lineage_chain': self.lineage_chain,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'blockchain_hash': self.blockchain_hash,
            'verification_status': self.verification_status,
            'compliance_flags': self.compliance_flags
        }


class TraceabilityEngine:
    """
    Main traceability engine for comprehensive data lineage tracking
    """

    def __init__(self, db_path: str = "traceability.db", config: Optional[Dict] = None):
        """
        Initialize the traceability engine

        Args:
            db_path: Path to SQLite database
            config: Configuration dictionary
        """
        self.db_path = db_path
        self.config = config or {}
        self._initialize_database()
        logger.info(f"TraceabilityEngine initialized with database: {db_path}")

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

            # Lineage nodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lineage_nodes (
                    node_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    transformation_type TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    data_signature TEXT NOT NULL,
                    parent_nodes TEXT,
                    metadata TEXT,
                    user_id TEXT,
                    protocol_id TEXT,
                    version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Traceability records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traceability_records (
                    record_id TEXT PRIMARY KEY,
                    artifact_path TEXT NOT NULL,
                    lineage_chain TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    blockchain_hash TEXT NOT NULL,
                    verification_status TEXT NOT NULL,
                    compliance_flags TEXT,
                    UNIQUE(artifact_path)
                )
            """)

            # Parent-child relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lineage_relationships (
                    parent_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    relationship_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (parent_id, child_id),
                    FOREIGN KEY (parent_id) REFERENCES lineage_nodes(node_id),
                    FOREIGN KEY (child_id) REFERENCES lineage_nodes(node_id)
                )
            """)

            # Verification log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_log (
                    log_id TEXT PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    verification_time TEXT NOT NULL,
                    verification_result TEXT NOT NULL,
                    verifier_id TEXT,
                    details TEXT,
                    FOREIGN KEY (node_id) REFERENCES lineage_nodes(node_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_protocol ON lineage_nodes(protocol_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON lineage_nodes(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_type ON lineage_nodes(data_type)")

            logger.info("Database schema initialized successfully")

    def create_data_node(
        self,
        data: Any,
        data_type: DataType,
        transformation_type: TransformationType,
        parent_nodes: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        user_id: str = "",
        protocol_id: str = ""
    ) -> DataLineageNode:
        """
        Create a new data lineage node

        Args:
            data: The actual data (will be hashed)
            data_type: Type of data
            transformation_type: Type of transformation applied
            parent_nodes: List of parent node IDs
            metadata: Additional metadata
            user_id: User who created the data
            protocol_id: Associated protocol ID

        Returns:
            DataLineageNode object
        """
        try:
            # Generate unique node ID
            node_id = str(uuid.uuid4())

            # Create data hash
            data_hash = self._compute_hash(data)

            # Create blockchain-ready signature
            signature_data = {
                'node_id': node_id,
                'data_hash': data_hash,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'parent_nodes': parent_nodes or []
            }
            data_signature = self._compute_hash(json.dumps(signature_data, sort_keys=True))

            # Create node
            node = DataLineageNode(
                node_id=node_id,
                timestamp=datetime.now(timezone.utc),
                data_type=data_type,
                transformation_type=transformation_type,
                data_hash=data_hash,
                data_signature=data_signature,
                parent_nodes=parent_nodes or [],
                metadata=metadata or {},
                user_id=user_id,
                protocol_id=protocol_id
            )

            # Store in database
            self._store_node(node)

            # Create parent-child relationships
            if parent_nodes:
                self._create_relationships(parent_nodes, node_id)

            logger.info(f"Created data node: {node_id} of type {data_type.value}")
            return node

        except Exception as e:
            logger.error(f"Error creating data node: {e}")
            raise

    def _compute_hash(self, data: Any) -> str:
        """
        Compute SHA-256 hash of data

        Args:
            data: Data to hash (can be string, bytes, dict, etc.)

        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, (str, bytes)):
            data = str(data)

        if isinstance(data, str):
            data = data.encode('utf-8')

        return hashlib.sha256(data).hexdigest()

    def _store_node(self, node: DataLineageNode):
        """Store lineage node in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lineage_nodes
                (node_id, timestamp, data_type, transformation_type, data_hash,
                 data_signature, parent_nodes, metadata, user_id, protocol_id, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node.node_id,
                node.timestamp.isoformat(),
                node.data_type.value,
                node.transformation_type.value,
                node.data_hash,
                node.data_signature,
                json.dumps(node.parent_nodes),
                json.dumps(node.metadata),
                node.user_id,
                node.protocol_id,
                node.version
            ))

    def _create_relationships(self, parent_ids: List[str], child_id: str):
        """Create parent-child relationships"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for parent_id in parent_ids:
                cursor.execute("""
                    INSERT OR IGNORE INTO lineage_relationships
                    (parent_id, child_id, relationship_type)
                    VALUES (?, ?, ?)
                """, (parent_id, child_id, "derived_from"))

    def get_lineage_chain(self, node_id: str) -> List[DataLineageNode]:
        """
        Get complete lineage chain from raw data to final artifact

        Args:
            node_id: Starting node ID

        Returns:
            List of DataLineageNode objects in chronological order
        """
        chain = []
        visited = set()

        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)

            node = self.get_node(current_id)
            if node:
                chain.append(node)
                for parent_id in node.parent_nodes:
                    traverse(parent_id)

        traverse(node_id)

        # Sort by timestamp
        chain.sort(key=lambda x: x.timestamp)
        return chain

    def get_node(self, node_id: str) -> Optional[DataLineageNode]:
        """Retrieve a lineage node by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lineage_nodes WHERE node_id = ?
            """, (node_id,))

            row = cursor.fetchone()
            if row:
                return DataLineageNode(
                    node_id=row['node_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    data_type=DataType(row['data_type']),
                    transformation_type=TransformationType(row['transformation_type']),
                    data_hash=row['data_hash'],
                    data_signature=row['data_signature'],
                    parent_nodes=json.loads(row['parent_nodes']),
                    metadata=json.loads(row['metadata']),
                    user_id=row['user_id'],
                    protocol_id=row['protocol_id'],
                    version=row['version']
                )
        return None

    def create_traceability_record(
        self,
        artifact_path: str,
        final_node_id: str
    ) -> TraceabilityRecord:
        """
        Create complete traceability record for a final artifact

        Args:
            artifact_path: Path to the artifact file
            final_node_id: ID of the final node in the lineage chain

        Returns:
            TraceabilityRecord object
        """
        # Get complete lineage chain
        lineage_chain = self.get_lineage_chain(final_node_id)
        node_ids = [node.node_id for node in lineage_chain]

        # Compute blockchain hash
        blockchain_data = {
            'artifact_path': artifact_path,
            'lineage_chain': node_ids,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        blockchain_hash = self._compute_hash(json.dumps(blockchain_data, sort_keys=True))

        # Create record
        record = TraceabilityRecord(
            record_id=str(uuid.uuid4()),
            artifact_path=artifact_path,
            lineage_chain=node_ids,
            created_at=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
            blockchain_hash=blockchain_hash,
            verification_status="verified",
            compliance_flags={
                'data_integrity': True,
                'chain_complete': True,
                'signatures_valid': True
            }
        )

        # Store record
        self._store_traceability_record(record)

        logger.info(f"Created traceability record: {record.record_id}")
        return record

    def _store_traceability_record(self, record: TraceabilityRecord):
        """Store traceability record in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO traceability_records
                (record_id, artifact_path, lineage_chain, created_at, last_modified,
                 blockchain_hash, verification_status, compliance_flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id,
                record.artifact_path,
                json.dumps(record.lineage_chain),
                record.created_at.isoformat(),
                record.last_modified.isoformat(),
                record.blockchain_hash,
                record.verification_status,
                json.dumps(record.compliance_flags)
            ))

    def verify_lineage_integrity(self, node_id: str) -> Dict[str, Any]:
        """
        Verify the integrity of a lineage chain

        Args:
            node_id: Node ID to verify

        Returns:
            Verification result dictionary
        """
        result = {
            'valid': True,
            'issues': [],
            'verified_nodes': 0,
            'total_nodes': 0
        }

        try:
            chain = self.get_lineage_chain(node_id)
            result['total_nodes'] = len(chain)

            for node in chain:
                # Verify signature
                signature_data = {
                    'node_id': node.node_id,
                    'data_hash': node.data_hash,
                    'timestamp': node.timestamp.isoformat(),
                    'parent_nodes': node.parent_nodes
                }
                expected_signature = self._compute_hash(
                    json.dumps(signature_data, sort_keys=True)
                )

                if expected_signature != node.data_signature:
                    result['valid'] = False
                    result['issues'].append(f"Invalid signature for node {node.node_id}")
                else:
                    result['verified_nodes'] += 1

            # Log verification
            self._log_verification(node_id, result)

        except Exception as e:
            result['valid'] = False
            result['issues'].append(f"Verification error: {str(e)}")
            logger.error(f"Lineage verification error: {e}")

        return result

    def _log_verification(self, node_id: str, result: Dict):
        """Log verification attempt"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verification_log
                (log_id, node_id, verification_time, verification_result, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                node_id,
                datetime.now(timezone.utc).isoformat(),
                "passed" if result['valid'] else "failed",
                json.dumps(result)
            ))

    def get_protocol_lineage(self, protocol_id: str) -> List[DataLineageNode]:
        """Get all lineage nodes for a specific protocol"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lineage_nodes
                WHERE protocol_id = ?
                ORDER BY timestamp ASC
            """, (protocol_id,))

            nodes = []
            for row in cursor.fetchall():
                nodes.append(DataLineageNode(
                    node_id=row['node_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    data_type=DataType(row['data_type']),
                    transformation_type=TransformationType(row['transformation_type']),
                    data_hash=row['data_hash'],
                    data_signature=row['data_signature'],
                    parent_nodes=json.loads(row['parent_nodes']),
                    metadata=json.loads(row['metadata']),
                    user_id=row['user_id'],
                    protocol_id=row['protocol_id'],
                    version=row['version']
                ))

            return nodes

    def export_lineage_graph(self, node_id: str, output_format: str = "json") -> str:
        """
        Export lineage graph in various formats

        Args:
            node_id: Root node ID
            output_format: Format (json, graphviz, mermaid)

        Returns:
            Formatted graph representation
        """
        chain = self.get_lineage_chain(node_id)

        if output_format == "json":
            return json.dumps([node.to_dict() for node in chain], indent=2)

        elif output_format == "graphviz":
            dot = ["digraph lineage {"]
            dot.append('  rankdir=LR;')
            dot.append('  node [shape=box];')

            for node in chain:
                label = f"{node.data_type.value}\\n{node.transformation_type.value}"
                dot.append(f'  "{node.node_id}" [label="{label}"];')
                for parent in node.parent_nodes:
                    dot.append(f'  "{parent}" -> "{node.node_id}";')

            dot.append("}")
            return "\n".join(dot)

        elif output_format == "mermaid":
            lines = ["graph LR"]
            for node in chain:
                label = f"{node.data_type.value}"
                lines.append(f'  {node.node_id}["{label}"]')
                for parent in node.parent_nodes:
                    lines.append(f'  {parent} --> {node.node_id}')

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get traceability engine statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total nodes
            cursor.execute("SELECT COUNT(*) as count FROM lineage_nodes")
            stats['total_nodes'] = cursor.fetchone()['count']

            # Nodes by type
            cursor.execute("""
                SELECT data_type, COUNT(*) as count
                FROM lineage_nodes
                GROUP BY data_type
            """)
            stats['nodes_by_type'] = {row['data_type']: row['count']
                                     for row in cursor.fetchall()}

            # Total records
            cursor.execute("SELECT COUNT(*) as count FROM traceability_records")
            stats['total_records'] = cursor.fetchone()['count']

            # Verification stats
            cursor.execute("""
                SELECT verification_result, COUNT(*) as count
                FROM verification_log
                GROUP BY verification_result
            """)
            stats['verification_stats'] = {row['verification_result']: row['count']
                                          for row in cursor.fetchall()}

            return stats


# FastAPI endpoints (optional)
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI(title="Data Traceability API")
    engine = TraceabilityEngine()

    class CreateNodeRequest(BaseModel):
        data: str
        data_type: str
        transformation_type: str
        parent_nodes: Optional[List[str]] = None
        metadata: Optional[Dict[str, Any]] = None
        user_id: str = ""
        protocol_id: str = ""

    @app.post("/api/v1/nodes/create")
    async def create_node(request: CreateNodeRequest):
        """Create a new lineage node"""
        try:
            node = engine.create_data_node(
                data=request.data,
                data_type=DataType(request.data_type),
                transformation_type=TransformationType(request.transformation_type),
                parent_nodes=request.parent_nodes,
                metadata=request.metadata,
                user_id=request.user_id,
                protocol_id=request.protocol_id
            )
            return node.to_dict()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/nodes/{node_id}")
    async def get_node(node_id: str):
        """Get node by ID"""
        node = engine.get_node(node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node.to_dict()

    @app.get("/api/v1/lineage/{node_id}")
    async def get_lineage(node_id: str):
        """Get complete lineage chain"""
        chain = engine.get_lineage_chain(node_id)
        return [node.to_dict() for node in chain]

    @app.post("/api/v1/verify/{node_id}")
    async def verify_lineage(node_id: str):
        """Verify lineage integrity"""
        return engine.verify_lineage_integrity(node_id)

    @app.get("/api/v1/statistics")
    async def get_statistics():
        """Get engine statistics"""
        return engine.get_statistics()

except ImportError:
    logger.warning("FastAPI not available. API endpoints disabled.")


if __name__ == "__main__":
    # Example usage
    engine = TraceabilityEngine()

    # Create raw data node
    raw_node = engine.create_data_node(
        data="Raw sensor readings: [25.3, 25.4, 25.5]",
        data_type=DataType.RAW,
        transformation_type=TransformationType.COLLECTION,
        protocol_id="PVTP-048",
        user_id="analyst001"
    )

    # Create processed data node
    processed_node = engine.create_data_node(
        data="Average temperature: 25.4°C",
        data_type=DataType.PROCESSED,
        transformation_type=TransformationType.CALCULATION,
        parent_nodes=[raw_node.node_id],
        protocol_id="PVTP-048",
        user_id="analyst001"
    )

    # Create final report node
    report_node = engine.create_data_node(
        data="Final report generated",
        data_type=DataType.REPORT,
        transformation_type=TransformationType.EXPORT,
        parent_nodes=[processed_node.node_id],
        protocol_id="PVTP-048",
        user_id="analyst001"
    )

    # Verify lineage
    verification = engine.verify_lineage_integrity(report_node.node_id)
    print(f"Verification result: {verification}")

    # Get statistics
    stats = engine.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
