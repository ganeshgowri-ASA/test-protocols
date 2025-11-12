"""
LIMS Connector
LIMS integration for sample tracking, chain of custody, and result management
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
import barcode
from barcode.writer import ImageWriter

logger = logging.getLogger(__name__)


class SampleStatus(Enum):
    """Sample status"""
    REGISTERED = "registered"
    IN_STORAGE = "in_storage"
    IN_TESTING = "in_testing"
    COMPLETED = "completed"
    DISPOSED = "disposed"
    ON_HOLD = "on_hold"


class TestStatus(Enum):
    """Test status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Sample:
    """Sample record"""
    sample_id: str
    sample_number: str
    sample_type: str
    description: str
    collection_date: datetime
    collection_location: str
    collected_by: str
    project_id: str
    protocol_id: str
    status: SampleStatus
    storage_location: str = ""
    storage_conditions: str = ""
    expiry_date: Optional[datetime] = None
    chain_of_custody: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sample_id': self.sample_id,
            'sample_number': self.sample_number,
            'sample_type': self.sample_type,
            'description': self.description,
            'collection_date': self.collection_date.isoformat(),
            'collection_location': self.collection_location,
            'collected_by': self.collected_by,
            'project_id': self.project_id,
            'protocol_id': self.protocol_id,
            'status': self.status.value,
            'storage_location': self.storage_location,
            'storage_conditions': self.storage_conditions,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'chain_of_custody': self.chain_of_custody,
            'metadata': self.metadata
        }


@dataclass
class TestResult:
    """Test result record"""
    result_id: str
    sample_id: str
    test_name: str
    test_method: str
    performed_by: str
    performed_date: datetime
    status: TestStatus
    result_values: Dict[str, Any] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    pass_fail: Optional[bool] = None
    specifications: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'sample_id': self.sample_id,
            'test_name': self.test_name,
            'test_method': self.test_method,
            'performed_by': self.performed_by,
            'performed_date': self.performed_date.isoformat(),
            'status': self.status.value,
            'result_values': self.result_values,
            'units': self.units,
            'pass_fail': self.pass_fail,
            'specifications': self.specifications,
            'notes': self.notes,
            'reviewed_by': self.reviewed_by,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'metadata': self.metadata
        }


class LIMSConnector:
    """
    LIMS connector for sample and result management
    """

    def __init__(self, db_path: str = "lims.db"):
        """Initialize LIMS connector"""
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"LIMSConnector initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection"""
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS samples (
                    sample_id TEXT PRIMARY KEY,
                    sample_number TEXT UNIQUE NOT NULL,
                    sample_type TEXT NOT NULL,
                    description TEXT,
                    collection_date TEXT NOT NULL,
                    collection_location TEXT,
                    collected_by TEXT NOT NULL,
                    project_id TEXT,
                    protocol_id TEXT,
                    status TEXT NOT NULL,
                    storage_location TEXT,
                    storage_conditions TEXT,
                    expiry_date TEXT,
                    chain_of_custody TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    result_id TEXT PRIMARY KEY,
                    sample_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    test_method TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    performed_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_values TEXT,
                    units TEXT,
                    pass_fail INTEGER,
                    specifications TEXT,
                    notes TEXT,
                    reviewed_by TEXT,
                    review_date TEXT,
                    metadata TEXT,
                    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chain_of_custody (
                    custody_id TEXT PRIMARY KEY,
                    sample_id TEXT NOT NULL,
                    transferred_from TEXT NOT NULL,
                    transferred_to TEXT NOT NULL,
                    transfer_date TEXT NOT NULL,
                    purpose TEXT,
                    condition_notes TEXT,
                    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
                )
            """)

            logger.info("LIMS database schema initialized")

    def register_sample(
        self,
        sample_type: str,
        description: str,
        collection_location: str,
        collected_by: str,
        project_id: str,
        protocol_id: str,
        storage_location: str = "",
        metadata: Optional[Dict] = None
    ) -> Sample:
        """Register a new sample"""
        sample_number = self._generate_sample_number()

        sample = Sample(
            sample_id=str(uuid.uuid4()),
            sample_number=sample_number,
            sample_type=sample_type,
            description=description,
            collection_date=datetime.now(timezone.utc),
            collection_location=collection_location,
            collected_by=collected_by,
            project_id=project_id,
            protocol_id=protocol_id,
            status=SampleStatus.REGISTERED,
            storage_location=storage_location,
            storage_conditions="",
            expiry_date=None,
            chain_of_custody=[{
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': 'registered',
                'user': collected_by
            }],
            metadata=metadata or {}
        )

        self._store_sample(sample)
        logger.info(f"Registered sample: {sample.sample_number}")
        return sample

    def _generate_sample_number(self) -> str:
        """Generate unique sample number"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM samples")
            count = cursor.fetchone()['count']

        year = datetime.now().year
        return f"SMP-{year}-{count + 1:06d}"

    def _store_sample(self, sample: Sample):
        """Store sample in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO samples
                (sample_id, sample_number, sample_type, description, collection_date,
                 collection_location, collected_by, project_id, protocol_id, status,
                 storage_location, storage_conditions, expiry_date, chain_of_custody, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample.sample_id,
                sample.sample_number,
                sample.sample_type,
                sample.description,
                sample.collection_date.isoformat(),
                sample.collection_location,
                sample.collected_by,
                sample.project_id,
                sample.protocol_id,
                sample.status.value,
                sample.storage_location,
                sample.storage_conditions,
                sample.expiry_date.isoformat() if sample.expiry_date else None,
                json.dumps(sample.chain_of_custody),
                json.dumps(sample.metadata)
            ))

    def record_test_result(
        self,
        sample_id: str,
        test_name: str,
        test_method: str,
        performed_by: str,
        result_values: Dict[str, Any],
        units: Optional[Dict[str, str]] = None,
        specifications: Optional[Dict] = None,
        notes: str = "",
        metadata: Optional[Dict] = None
    ) -> TestResult:
        """Record test result"""
        # Determine pass/fail
        pass_fail = None
        if specifications and result_values:
            pass_fail = all(
                specifications.get(key, {}).get('min', float('-inf')) <= value <= specifications.get(key, {}).get('max', float('inf'))
                for key, value in result_values.items() if isinstance(value, (int, float))
            )

        result = TestResult(
            result_id=str(uuid.uuid4()),
            sample_id=sample_id,
            test_name=test_name,
            test_method=test_method,
            performed_by=performed_by,
            performed_date=datetime.now(timezone.utc),
            status=TestStatus.COMPLETED,
            result_values=result_values,
            units=units or {},
            pass_fail=pass_fail,
            specifications=specifications or {},
            notes=notes,
            reviewed_by=None,
            review_date=None,
            metadata=metadata or {}
        )

        self._store_result(result)
        logger.info(f"Recorded test result: {result.result_id}")
        return result

    def _store_result(self, result: TestResult):
        """Store test result"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_results
                (result_id, sample_id, test_name, test_method, performed_by, performed_date,
                 status, result_values, units, pass_fail, specifications, notes,
                 reviewed_by, review_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.result_id,
                result.sample_id,
                result.test_name,
                result.test_method,
                result.performed_by,
                result.performed_date.isoformat(),
                result.status.value,
                json.dumps(result.result_values),
                json.dumps(result.units),
                1 if result.pass_fail else 0 if result.pass_fail is not None else None,
                json.dumps(result.specifications),
                result.notes,
                result.reviewed_by,
                result.review_date.isoformat() if result.review_date else None,
                json.dumps(result.metadata)
            ))

    def transfer_custody(
        self,
        sample_id: str,
        transferred_from: str,
        transferred_to: str,
        purpose: str,
        condition_notes: str = ""
    ):
        """Transfer sample custody"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chain_of_custody
                (custody_id, sample_id, transferred_from, transferred_to, transfer_date, purpose, condition_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                sample_id,
                transferred_from,
                transferred_to,
                datetime.now(timezone.utc).isoformat(),
                purpose,
                condition_notes
            ))

        # Update sample chain of custody
        sample = self.get_sample(sample_id)
        if sample:
            sample.chain_of_custody.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'from': transferred_from,
                'to': transferred_to,
                'purpose': purpose
            })
            self._store_sample(sample)

    def get_sample(self, sample_id: str) -> Optional[Sample]:
        """Get sample by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM samples WHERE sample_id = ?", (sample_id,))
            row = cursor.fetchone()

            if row:
                return Sample(
                    sample_id=row['sample_id'],
                    sample_number=row['sample_number'],
                    sample_type=row['sample_type'],
                    description=row['description'],
                    collection_date=datetime.fromisoformat(row['collection_date']),
                    collection_location=row['collection_location'],
                    collected_by=row['collected_by'],
                    project_id=row['project_id'],
                    protocol_id=row['protocol_id'],
                    status=SampleStatus(row['status']),
                    storage_location=row['storage_location'],
                    storage_conditions=row['storage_conditions'],
                    expiry_date=datetime.fromisoformat(row['expiry_date']) if row['expiry_date'] else None,
                    chain_of_custody=json.loads(row['chain_of_custody']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get LIMS statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM samples")
            stats['total_samples'] = cursor.fetchone()['count']

            cursor.execute("SELECT status, COUNT(*) as count FROM samples GROUP BY status")
            stats['samples_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as count FROM test_results")
            stats['total_results'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM test_results WHERE pass_fail = 1")
            stats['passed_tests'] = cursor.fetchone()['count']

            return stats


if __name__ == "__main__":
    lims = LIMSConnector()

    sample = lims.register_sample(
        sample_type="PV Module",
        description="Polycrystalline module for thermal cycling test",
        collection_location="Receiving Dock A",
        collected_by="tech001",
        project_id="PRJ-001",
        protocol_id="PVTP-048"
    )

    print(f"Registered sample: {sample.sample_number}")

    result = lims.record_test_result(
        sample_id=sample.sample_id,
        test_name="Thermal Cycling",
        test_method="IEC 61215",
        performed_by="tech001",
        result_values={'max_temp': 85.0, 'min_temp': -40.0, 'cycles': 200},
        specifications={'max_temp': {'min': 80, 'max': 90}, 'min_temp': {'min': -45, 'max': -35}}
    )

    print(f"Result pass/fail: {result.pass_fail}")
