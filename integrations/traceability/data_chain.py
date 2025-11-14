"""
Data Chain Management
Manages parent-child relationships, transformation tracking, and data provenance
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
import networkx as nx

logger = logging.getLogger(__name__)


class ChainType(Enum):
    """Types of data chains"""
    LINEAR = "linear"  # Single parent -> child
    BRANCHING = "branching"  # One parent -> multiple children
    MERGING = "merging"  # Multiple parents -> one child
    COMPLEX = "complex"  # Complex dependency graph


class TransformationStatus(Enum):
    """Status of transformations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Transformation:
    """Represents a data transformation"""
    transform_id: str
    name: str
    input_nodes: List[str]
    output_node: str
    transformation_function: str
    parameters: Dict[str, Any]
    status: TransformationStatus
    executed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'transform_id': self.transform_id,
            'name': self.name,
            'input_nodes': self.input_nodes,
            'output_node': self.output_node,
            'transformation_function': self.transformation_function,
            'parameters': self.parameters,
            'status': self.status.value,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


@dataclass
class DataChain:
    """Represents a complete data chain"""
    chain_id: str
    name: str
    chain_type: ChainType
    root_nodes: List[str]  # Starting points
    leaf_nodes: List[str]  # End points
    all_nodes: Set[str]
    created_at: datetime
    last_modified: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chain_id': self.chain_id,
            'name': self.name,
            'chain_type': self.chain_type.value,
            'root_nodes': self.root_nodes,
            'leaf_nodes': self.leaf_nodes,
            'all_nodes': list(self.all_nodes),
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'metadata': self.metadata
        }


class DataChainManager:
    """
    Manages data chains with parent-child relationships and transformation tracking
    """

    def __init__(self, db_path: str = "data_chains.db"):
        """
        Initialize the data chain manager

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.graph = nx.DiGraph()
        self._initialize_database()
        self._load_graph()
        logger.info(f"DataChainManager initialized with database: {db_path}")

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

            # Data chains table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_chains (
                    chain_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    chain_type TEXT NOT NULL,
                    root_nodes TEXT NOT NULL,
                    leaf_nodes TEXT NOT NULL,
                    all_nodes TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Transformations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transformations (
                    transform_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    input_nodes TEXT NOT NULL,
                    output_node TEXT NOT NULL,
                    transformation_function TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    executed_at TEXT,
                    duration_ms REAL,
                    error_message TEXT,
                    metadata TEXT,
                    chain_id TEXT,
                    FOREIGN KEY (chain_id) REFERENCES data_chains(chain_id)
                )
            """)

            # Node relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS node_relationships (
                    parent_node TEXT NOT NULL,
                    child_node TEXT NOT NULL,
                    relationship_type TEXT,
                    weight REAL DEFAULT 1.0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (parent_node, child_node)
                )
            """)

            # Provenance records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provenance_records (
                    record_id TEXT PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    provenance_type TEXT NOT NULL,
                    source_system TEXT,
                    source_timestamp TEXT,
                    transformations_applied TEXT,
                    quality_metrics TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chain_type ON data_chains(chain_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transform_status ON transformations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_parent ON node_relationships(parent_node)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_child ON node_relationships(child_node)")

            logger.info("Data chain database schema initialized")

    def _load_graph(self):
        """Load graph from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT parent_node, child_node, weight FROM node_relationships")

            for row in cursor.fetchall():
                self.graph.add_edge(
                    row['parent_node'],
                    row['child_node'],
                    weight=row['weight']
                )

        logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def create_chain(
        self,
        name: str,
        root_nodes: List[str],
        metadata: Optional[Dict] = None
    ) -> DataChain:
        """
        Create a new data chain

        Args:
            name: Chain name
            root_nodes: Starting node IDs
            metadata: Additional metadata

        Returns:
            DataChain object
        """
        chain_id = str(uuid.uuid4())

        chain = DataChain(
            chain_id=chain_id,
            name=name,
            chain_type=ChainType.LINEAR,  # Will be updated as nodes are added
            root_nodes=root_nodes,
            leaf_nodes=[],
            all_nodes=set(root_nodes),
            created_at=datetime.now(timezone.utc),
            last_modified=datetime.now(timezone.utc),
            metadata=metadata or {}
        )

        self._store_chain(chain)
        logger.info(f"Created data chain: {chain_id}")
        return chain

    def _store_chain(self, chain: DataChain):
        """Store chain in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO data_chains
                (chain_id, name, chain_type, root_nodes, leaf_nodes, all_nodes,
                 created_at, last_modified, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chain.chain_id,
                chain.name,
                chain.chain_type.value,
                json.dumps(chain.root_nodes),
                json.dumps(chain.leaf_nodes),
                json.dumps(list(chain.all_nodes)),
                chain.created_at.isoformat(),
                chain.last_modified.isoformat(),
                json.dumps(chain.metadata)
            ))

    def add_relationship(
        self,
        parent_node: str,
        child_node: str,
        relationship_type: str = "derived_from",
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        """
        Add parent-child relationship

        Args:
            parent_node: Parent node ID
            child_node: Child node ID
            relationship_type: Type of relationship
            weight: Relationship weight
            metadata: Additional metadata
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO node_relationships
                (parent_node, child_node, relationship_type, weight, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                parent_node,
                child_node,
                relationship_type,
                weight,
                json.dumps(metadata or {})
            ))

        # Update graph
        self.graph.add_edge(parent_node, child_node, weight=weight)
        logger.info(f"Added relationship: {parent_node} -> {child_node}")

    def create_transformation(
        self,
        name: str,
        input_nodes: List[str],
        transformation_function: str,
        parameters: Dict[str, Any],
        chain_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Transformation:
        """
        Create a transformation record

        Args:
            name: Transformation name
            input_nodes: Input node IDs
            transformation_function: Function identifier
            parameters: Transformation parameters
            chain_id: Associated chain ID
            metadata: Additional metadata

        Returns:
            Transformation object
        """
        transform = Transformation(
            transform_id=str(uuid.uuid4()),
            name=name,
            input_nodes=input_nodes,
            output_node="",  # Will be set after execution
            transformation_function=transformation_function,
            parameters=parameters,
            status=TransformationStatus.PENDING,
            metadata=metadata or {}
        )

        self._store_transformation(transform, chain_id)
        logger.info(f"Created transformation: {transform.transform_id}")
        return transform

    def _store_transformation(self, transform: Transformation, chain_id: Optional[str] = None):
        """Store transformation in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO transformations
                (transform_id, name, input_nodes, output_node, transformation_function,
                 parameters, status, executed_at, duration_ms, error_message, metadata, chain_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transform.transform_id,
                transform.name,
                json.dumps(transform.input_nodes),
                transform.output_node,
                transform.transformation_function,
                json.dumps(transform.parameters),
                transform.status.value,
                transform.executed_at.isoformat() if transform.executed_at else None,
                transform.duration_ms,
                transform.error_message,
                json.dumps(transform.metadata),
                chain_id
            ))

    def execute_transformation(
        self,
        transform_id: str,
        output_node: str
    ) -> bool:
        """
        Mark transformation as executed

        Args:
            transform_id: Transformation ID
            output_node: Output node ID

        Returns:
            Success status
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transformations
                    SET status = ?, output_node = ?, executed_at = ?
                    WHERE transform_id = ?
                """, (
                    TransformationStatus.COMPLETED.value,
                    output_node,
                    datetime.now(timezone.utc).isoformat(),
                    transform_id
                ))

            logger.info(f"Transformation {transform_id} executed successfully")
            return True

        except Exception as e:
            logger.error(f"Error executing transformation: {e}")
            return False

    def get_ancestors(self, node_id: str, max_depth: Optional[int] = None) -> List[str]:
        """
        Get all ancestor nodes

        Args:
            node_id: Node ID
            max_depth: Maximum traversal depth

        Returns:
            List of ancestor node IDs
        """
        try:
            if node_id not in self.graph:
                return []

            ancestors = set()
            current_level = {node_id}
            depth = 0

            while current_level and (max_depth is None or depth < max_depth):
                next_level = set()
                for node in current_level:
                    parents = list(self.graph.predecessors(node))
                    ancestors.update(parents)
                    next_level.update(parents)

                current_level = next_level
                depth += 1

            return list(ancestors)

        except Exception as e:
            logger.error(f"Error getting ancestors: {e}")
            return []

    def get_descendants(self, node_id: str, max_depth: Optional[int] = None) -> List[str]:
        """
        Get all descendant nodes

        Args:
            node_id: Node ID
            max_depth: Maximum traversal depth

        Returns:
            List of descendant node IDs
        """
        try:
            if node_id not in self.graph:
                return []

            descendants = set()
            current_level = {node_id}
            depth = 0

            while current_level and (max_depth is None or depth < max_depth):
                next_level = set()
                for node in current_level:
                    children = list(self.graph.successors(node))
                    descendants.update(children)
                    next_level.update(children)

                current_level = next_level
                depth += 1

            return list(descendants)

        except Exception as e:
            logger.error(f"Error getting descendants: {e}")
            return []

    def find_common_ancestors(self, node_ids: List[str]) -> List[str]:
        """
        Find common ancestors of multiple nodes

        Args:
            node_ids: List of node IDs

        Returns:
            List of common ancestor IDs
        """
        if not node_ids:
            return []

        # Get ancestors for each node
        ancestor_sets = [set(self.get_ancestors(node_id)) for node_id in node_ids]

        # Find intersection
        common = set.intersection(*ancestor_sets) if ancestor_sets else set()
        return list(common)

    def get_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Get path from source to target node

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        try:
            if nx.has_path(self.graph, source, target):
                return nx.shortest_path(self.graph, source, target)
            return None
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return None

    def analyze_chain_structure(self, chain_id: str) -> Dict[str, Any]:
        """
        Analyze chain structure and characteristics

        Args:
            chain_id: Chain ID

        Returns:
            Analysis results
        """
        chain = self.get_chain(chain_id)
        if not chain:
            return {}

        # Create subgraph for this chain
        subgraph = self.graph.subgraph(chain.all_nodes)

        analysis = {
            'chain_id': chain_id,
            'total_nodes': len(chain.all_nodes),
            'root_nodes': len(chain.root_nodes),
            'leaf_nodes': len(chain.leaf_nodes),
            'max_depth': 0,
            'branching_factor': 0,
            'is_dag': nx.is_directed_acyclic_graph(subgraph),
            'connected_components': nx.number_weakly_connected_components(subgraph),
            'density': nx.density(subgraph)
        }

        # Calculate max depth
        try:
            for root in chain.root_nodes:
                for leaf in chain.leaf_nodes:
                    if nx.has_path(subgraph, root, leaf):
                        path = nx.shortest_path(subgraph, root, leaf)
                        analysis['max_depth'] = max(analysis['max_depth'], len(path) - 1)
        except:
            pass

        # Calculate average branching factor
        out_degrees = [subgraph.out_degree(node) for node in subgraph.nodes()]
        analysis['branching_factor'] = sum(out_degrees) / len(out_degrees) if out_degrees else 0

        return analysis

    def get_chain(self, chain_id: str) -> Optional[DataChain]:
        """Get chain by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_chains WHERE chain_id = ?", (chain_id,))
            row = cursor.fetchone()

            if row:
                return DataChain(
                    chain_id=row['chain_id'],
                    name=row['name'],
                    chain_type=ChainType(row['chain_type']),
                    root_nodes=json.loads(row['root_nodes']),
                    leaf_nodes=json.loads(row['leaf_nodes']),
                    all_nodes=set(json.loads(row['all_nodes'])),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_modified=datetime.fromisoformat(row['last_modified']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def record_provenance(
        self,
        node_id: str,
        provenance_type: str,
        source_system: str,
        transformations_applied: List[str],
        quality_metrics: Optional[Dict] = None
    ) -> str:
        """
        Record provenance information for a node

        Args:
            node_id: Node ID
            provenance_type: Type of provenance record
            source_system: Source system identifier
            transformations_applied: List of transformation IDs
            quality_metrics: Quality metrics

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO provenance_records
                (record_id, node_id, provenance_type, source_system, source_timestamp,
                 transformations_applied, quality_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                node_id,
                provenance_type,
                source_system,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(transformations_applied),
                json.dumps(quality_metrics or {})
            ))

        logger.info(f"Recorded provenance for node {node_id}")
        return record_id

    def get_provenance(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all provenance records for a node"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM provenance_records WHERE node_id = ? ORDER BY created_at DESC
            """, (node_id,))

            records = []
            for row in cursor.fetchall():
                records.append({
                    'record_id': row['record_id'],
                    'node_id': row['node_id'],
                    'provenance_type': row['provenance_type'],
                    'source_system': row['source_system'],
                    'source_timestamp': row['source_timestamp'],
                    'transformations_applied': json.loads(row['transformations_applied']),
                    'quality_metrics': json.loads(row['quality_metrics']),
                    'created_at': row['created_at']
                })

            return records

    def export_chain_visualization(self, chain_id: str) -> str:
        """
        Export chain as DOT graph for visualization

        Args:
            chain_id: Chain ID

        Returns:
            DOT format string
        """
        chain = self.get_chain(chain_id)
        if not chain:
            return ""

        dot_lines = [
            f'digraph "{chain.name}" {{',
            '  rankdir=TB;',
            '  node [shape=box, style=rounded];'
        ]

        # Add nodes
        for node in chain.all_nodes:
            label = node[:12] + "..." if len(node) > 12 else node
            color = "lightgreen" if node in chain.root_nodes else \
                    "lightblue" if node in chain.leaf_nodes else "white"
            dot_lines.append(f'  "{node}" [label="{label}", fillcolor="{color}", style="filled,rounded"];')

        # Add edges
        subgraph = self.graph.subgraph(chain.all_nodes)
        for source, target in subgraph.edges():
            dot_lines.append(f'  "{source}" -> "{target}";')

        dot_lines.append('}')
        return '\n'.join(dot_lines)


if __name__ == "__main__":
    # Example usage
    manager = DataChainManager()

    # Create a chain
    chain = manager.create_chain(
        name="PVTP-048 Test Data Chain",
        root_nodes=["raw_data_001"]
    )

    # Add relationships
    manager.add_relationship("raw_data_001", "validated_data_001")
    manager.add_relationship("validated_data_001", "processed_data_001")
    manager.add_relationship("processed_data_001", "report_001")

    # Create transformation
    transform = manager.create_transformation(
        name="Data Validation",
        input_nodes=["raw_data_001"],
        transformation_function="validate_sensor_data",
        parameters={"threshold": 0.01, "method": "statistical"},
        chain_id=chain.chain_id
    )

    # Get ancestors
    ancestors = manager.get_ancestors("report_001")
    print(f"Ancestors of report_001: {ancestors}")

    # Analyze chain
    analysis = manager.analyze_chain_structure(chain.chain_id)
    print(f"Chain analysis: {json.dumps(analysis, indent=2)}")
