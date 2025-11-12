"""
Data Integrity Checker
Data integrity verification with checksums, hash verification, and tamper detection
"""

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import zlib

logger = logging.getLogger(__name__)


class HashAlgorithm(Enum):
    """Supported hash algorithms"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    CRC32 = "crc32"


class IntegrityStatus(Enum):
    """Integrity check status"""
    VALID = "valid"
    INVALID = "invalid"
    MODIFIED = "modified"
    CORRUPTED = "corrupted"
    MISSING = "missing"
    UNKNOWN = "unknown"


@dataclass
class IntegrityRecord:
    """Integrity verification record"""
    record_id: str
    resource_path: str
    resource_type: str
    original_hash: str
    hash_algorithm: HashAlgorithm
    file_size: int
    created_at: datetime
    last_verified: datetime
    verification_count: int
    status: IntegrityStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    hmac_signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'record_id': self.record_id,
            'resource_path': self.resource_path,
            'resource_type': self.resource_type,
            'original_hash': self.original_hash,
            'hash_algorithm': self.hash_algorithm.value,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'last_verified': self.last_verified.isoformat(),
            'verification_count': self.verification_count,
            'status': self.status.value,
            'metadata': self.metadata,
            'hmac_signature': self.hmac_signature
        }


@dataclass
class VerificationResult:
    """Result of integrity verification"""
    verified_at: datetime
    resource_path: str
    expected_hash: str
    actual_hash: str
    status: IntegrityStatus
    file_size_match: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'verified_at': self.verified_at.isoformat(),
            'resource_path': self.resource_path,
            'expected_hash': self.expected_hash,
            'actual_hash': self.actual_hash,
            'status': self.status.value,
            'file_size_match': self.file_size_match,
            'details': self.details
        }


class IntegrityChecker:
    """
    Comprehensive data integrity verification system
    """

    def __init__(
        self,
        db_path: str = "integrity.db",
        secret_key: Optional[str] = None,
        default_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ):
        """
        Initialize integrity checker

        Args:
            db_path: Path to SQLite database
            secret_key: Secret key for HMAC signatures
            default_algorithm: Default hash algorithm
        """
        self.db_path = db_path
        self.secret_key = secret_key or self._generate_secret_key()
        self.default_algorithm = default_algorithm
        self._initialize_database()
        logger.info(f"IntegrityChecker initialized with database: {db_path}")

    def _generate_secret_key(self) -> str:
        """Generate a secret key for HMAC"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

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

            # Integrity records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS integrity_records (
                    record_id TEXT PRIMARY KEY,
                    resource_path TEXT UNIQUE NOT NULL,
                    resource_type TEXT NOT NULL,
                    original_hash TEXT NOT NULL,
                    hash_algorithm TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_verified TEXT NOT NULL,
                    verification_count INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    hmac_signature TEXT
                )
            """)

            # Verification history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_history (
                    verification_id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL,
                    verified_at TEXT NOT NULL,
                    expected_hash TEXT NOT NULL,
                    actual_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    file_size_match INTEGER,
                    details TEXT,
                    FOREIGN KEY (record_id) REFERENCES integrity_records(record_id)
                )
            """)

            # Tamper alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tamper_alerts (
                    alert_id TEXT PRIMARY KEY,
                    record_id TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    details TEXT,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_at TEXT,
                    acknowledged_by TEXT,
                    FOREIGN KEY (record_id) REFERENCES integrity_records(record_id)
                )
            """)

            # Batch verification results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_verifications (
                    batch_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    total_files INTEGER,
                    verified_valid INTEGER,
                    verified_invalid INTEGER,
                    errors INTEGER,
                    summary TEXT
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resource_path ON integrity_records(resource_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON integrity_records(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_verified ON integrity_records(last_verified)")

            logger.info("Integrity checker database schema initialized")

    def compute_hash(
        self,
        data: Any,
        algorithm: Optional[HashAlgorithm] = None
    ) -> str:
        """
        Compute hash of data

        Args:
            data: Data to hash (string, bytes, dict, or file path)
            algorithm: Hash algorithm to use

        Returns:
            Hexadecimal hash string
        """
        algorithm = algorithm or self.default_algorithm

        # Convert data to bytes
        if isinstance(data, dict):
            data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
        elif isinstance(data, str):
            # Check if it's a file path
            path = Path(data)
            if path.exists() and path.is_file():
                with open(path, 'rb') as f:
                    data_bytes = f.read()
            else:
                data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode('utf-8')

        # Compute hash
        if algorithm == HashAlgorithm.MD5:
            return hashlib.md5(data_bytes).hexdigest()
        elif algorithm == HashAlgorithm.SHA1:
            return hashlib.sha1(data_bytes).hexdigest()
        elif algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data_bytes).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data_bytes).hexdigest()
        elif algorithm == HashAlgorithm.CRC32:
            return format(zlib.crc32(data_bytes) & 0xFFFFFFFF, '08x')
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def compute_hmac(self, data: Any) -> str:
        """
        Compute HMAC signature

        Args:
            data: Data to sign

        Returns:
            HMAC signature
        """
        if isinstance(data, dict):
            data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode('utf-8')

        return hmac.new(
            self.secret_key.encode('utf-8'),
            data_bytes,
            hashlib.sha256
        ).hexdigest()

    def register_resource(
        self,
        resource_path: str,
        resource_type: str = "file",
        data: Optional[Any] = None,
        algorithm: Optional[HashAlgorithm] = None,
        metadata: Optional[Dict] = None
    ) -> IntegrityRecord:
        """
        Register a resource for integrity monitoring

        Args:
            resource_path: Path to resource
            resource_type: Type of resource
            data: Data to hash (if not file path)
            algorithm: Hash algorithm
            metadata: Additional metadata

        Returns:
            IntegrityRecord object
        """
        try:
            algorithm = algorithm or self.default_algorithm

            # Compute hash
            if data is not None:
                resource_hash = self.compute_hash(data, algorithm)
                file_size = len(str(data).encode('utf-8'))
            else:
                resource_hash = self.compute_hash(resource_path, algorithm)
                path = Path(resource_path)
                file_size = path.stat().st_size if path.exists() else 0

            # Compute HMAC signature
            signature_data = {
                'resource_path': resource_path,
                'hash': resource_hash,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            hmac_signature = self.compute_hmac(signature_data)

            # Create record
            record = IntegrityRecord(
                record_id=str(uuid.uuid4()),
                resource_path=resource_path,
                resource_type=resource_type,
                original_hash=resource_hash,
                hash_algorithm=algorithm,
                file_size=file_size,
                created_at=datetime.now(timezone.utc),
                last_verified=datetime.now(timezone.utc),
                verification_count=0,
                status=IntegrityStatus.VALID,
                metadata=metadata or {},
                hmac_signature=hmac_signature
            )

            # Store record
            self._store_record(record)

            logger.info(f"Registered resource: {resource_path}")
            return record

        except Exception as e:
            logger.error(f"Error registering resource: {e}")
            raise

    def _store_record(self, record: IntegrityRecord):
        """Store integrity record in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO integrity_records
                (record_id, resource_path, resource_type, original_hash, hash_algorithm,
                 file_size, created_at, last_verified, verification_count, status,
                 metadata, hmac_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id,
                record.resource_path,
                record.resource_type,
                record.original_hash,
                record.hash_algorithm.value,
                record.file_size,
                record.created_at.isoformat(),
                record.last_verified.isoformat(),
                record.verification_count,
                record.status.value,
                json.dumps(record.metadata),
                record.hmac_signature
            ))

    def verify_resource(
        self,
        resource_path: str,
        data: Optional[Any] = None
    ) -> VerificationResult:
        """
        Verify resource integrity

        Args:
            resource_path: Path to resource
            data: Current data (if not file)

        Returns:
            VerificationResult object
        """
        try:
            # Get stored record
            record = self.get_record(resource_path)
            if not record:
                return VerificationResult(
                    verified_at=datetime.now(timezone.utc),
                    resource_path=resource_path,
                    expected_hash="",
                    actual_hash="",
                    status=IntegrityStatus.MISSING,
                    file_size_match=False,
                    details={'error': 'No integrity record found'}
                )

            # Compute current hash
            if data is not None:
                current_hash = self.compute_hash(data, record.hash_algorithm)
                current_size = len(str(data).encode('utf-8'))
            else:
                current_hash = self.compute_hash(resource_path, record.hash_algorithm)
                path = Path(resource_path)
                current_size = path.stat().st_size if path.exists() else 0

            # Compare hashes
            status = IntegrityStatus.VALID if current_hash == record.original_hash else IntegrityStatus.MODIFIED
            size_match = current_size == record.file_size

            result = VerificationResult(
                verified_at=datetime.now(timezone.utc),
                resource_path=resource_path,
                expected_hash=record.original_hash,
                actual_hash=current_hash,
                status=status,
                file_size_match=size_match,
                details={
                    'algorithm': record.hash_algorithm.value,
                    'expected_size': record.file_size,
                    'actual_size': current_size
                }
            )

            # Update record
            self._update_verification_status(record.record_id, status)

            # Store verification result
            self._store_verification_result(record.record_id, result)

            # Generate alert if tampered
            if status != IntegrityStatus.VALID:
                self._create_tamper_alert(record.record_id, result)

            logger.info(f"Verified resource: {resource_path} - Status: {status.value}")
            return result

        except Exception as e:
            logger.error(f"Error verifying resource: {e}")
            return VerificationResult(
                verified_at=datetime.now(timezone.utc),
                resource_path=resource_path,
                expected_hash="",
                actual_hash="",
                status=IntegrityStatus.UNKNOWN,
                file_size_match=False,
                details={'error': str(e)}
            )

    def _update_verification_status(self, record_id: str, status: IntegrityStatus):
        """Update verification status in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE integrity_records
                SET last_verified = ?,
                    verification_count = verification_count + 1,
                    status = ?
                WHERE record_id = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                status.value,
                record_id
            ))

    def _store_verification_result(self, record_id: str, result: VerificationResult):
        """Store verification result in history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verification_history
                (verification_id, record_id, verified_at, expected_hash, actual_hash,
                 status, file_size_match, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                record_id,
                result.verified_at.isoformat(),
                result.expected_hash,
                result.actual_hash,
                result.status.value,
                1 if result.file_size_match else 0,
                json.dumps(result.details)
            ))

    def _create_tamper_alert(self, record_id: str, result: VerificationResult):
        """Create tamper detection alert"""
        severity = "critical" if result.status == IntegrityStatus.CORRUPTED else "high"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tamper_alerts
                (alert_id, record_id, detected_at, alert_type, severity, description, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                record_id,
                datetime.now(timezone.utc).isoformat(),
                "hash_mismatch",
                severity,
                f"Resource integrity violation detected: {result.resource_path}",
                json.dumps(result.to_dict())
            ))

        logger.warning(f"Tamper alert created for {result.resource_path}")

    def get_record(self, resource_path: str) -> Optional[IntegrityRecord]:
        """Get integrity record by resource path"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM integrity_records WHERE resource_path = ?
            """, (resource_path,))

            row = cursor.fetchone()
            if row:
                return IntegrityRecord(
                    record_id=row['record_id'],
                    resource_path=row['resource_path'],
                    resource_type=row['resource_type'],
                    original_hash=row['original_hash'],
                    hash_algorithm=HashAlgorithm(row['hash_algorithm']),
                    file_size=row['file_size'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_verified=datetime.fromisoformat(row['last_verified']),
                    verification_count=row['verification_count'],
                    status=IntegrityStatus(row['status']),
                    metadata=json.loads(row['metadata']),
                    hmac_signature=row['hmac_signature']
                )
        return None

    def batch_verify(
        self,
        resource_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify multiple resources in batch

        Args:
            resource_paths: List of paths (None = verify all)

        Returns:
            Batch verification results
        """
        batch_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        results = {
            'batch_id': batch_id,
            'started_at': started_at.isoformat(),
            'total_files': 0,
            'verified_valid': 0,
            'verified_invalid': 0,
            'errors': 0,
            'details': []
        }

        try:
            # Get resources to verify
            if resource_paths:
                resources = [self.get_record(path) for path in resource_paths]
                resources = [r for r in resources if r is not None]
            else:
                resources = self.get_all_records()

            results['total_files'] = len(resources)

            # Verify each resource
            for record in resources:
                try:
                    result = self.verify_resource(record.resource_path)

                    if result.status == IntegrityStatus.VALID:
                        results['verified_valid'] += 1
                    else:
                        results['verified_invalid'] += 1

                    results['details'].append({
                        'path': record.resource_path,
                        'status': result.status.value
                    })

                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'path': record.resource_path,
                        'error': str(e)
                    })

            # Store batch results
            completed_at = datetime.now(timezone.utc)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO batch_verifications
                    (batch_id, started_at, completed_at, total_files,
                     verified_valid, verified_invalid, errors, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    batch_id,
                    started_at.isoformat(),
                    completed_at.isoformat(),
                    results['total_files'],
                    results['verified_valid'],
                    results['verified_invalid'],
                    results['errors'],
                    json.dumps(results)
                ))

            results['completed_at'] = completed_at.isoformat()
            logger.info(f"Batch verification completed: {batch_id}")

        except Exception as e:
            logger.error(f"Batch verification error: {e}")
            results['error'] = str(e)

        return results

    def get_all_records(self) -> List[IntegrityRecord]:
        """Get all integrity records"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM integrity_records ORDER BY created_at DESC")

            records = []
            for row in cursor.fetchall():
                records.append(IntegrityRecord(
                    record_id=row['record_id'],
                    resource_path=row['resource_path'],
                    resource_type=row['resource_type'],
                    original_hash=row['original_hash'],
                    hash_algorithm=HashAlgorithm(row['hash_algorithm']),
                    file_size=row['file_size'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_verified=datetime.fromisoformat(row['last_verified']),
                    verification_count=row['verification_count'],
                    status=IntegrityStatus(row['status']),
                    metadata=json.loads(row['metadata']),
                    hmac_signature=row['hmac_signature']
                ))

            return records

    def get_tamper_alerts(
        self,
        acknowledged: bool = False
    ) -> List[Dict[str, Any]]:
        """Get tamper alerts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tamper_alerts
                WHERE acknowledged = ?
                ORDER BY detected_at DESC
            """, (1 if acknowledged else 0,))

            return [dict(row) for row in cursor.fetchall()]

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge tamper alert"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tamper_alerts
                SET acknowledged = 1,
                    acknowledged_at = ?,
                    acknowledged_by = ?
                WHERE alert_id = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                acknowledged_by,
                alert_id
            ))

    def get_statistics(self) -> Dict[str, Any]:
        """Get integrity checker statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total records
            cursor.execute("SELECT COUNT(*) as count FROM integrity_records")
            stats['total_records'] = cursor.fetchone()['count']

            # Records by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM integrity_records
                GROUP BY status
            """)
            stats['by_status'] = {row['status']: row['count']
                                 for row in cursor.fetchall()}

            # Total verifications
            cursor.execute("SELECT SUM(verification_count) as total FROM integrity_records")
            stats['total_verifications'] = cursor.fetchone()['total'] or 0

            # Pending alerts
            cursor.execute("SELECT COUNT(*) as count FROM tamper_alerts WHERE acknowledged = 0")
            stats['pending_alerts'] = cursor.fetchone()['count']

            return stats


if __name__ == "__main__":
    # Example usage
    checker = IntegrityChecker()

    # Register a resource
    record = checker.register_resource(
        resource_path="/data/test_results.json",
        resource_type="test_data",
        data={"temperature": 25.4, "humidity": 45.2},
        metadata={'protocol': 'PVTP-048'}
    )

    print(f"Registered resource: {record.record_id}")

    # Verify resource
    result = checker.verify_resource(
        resource_path="/data/test_results.json",
        data={"temperature": 25.4, "humidity": 45.2}
    )

    print(f"Verification result: {result.status.value}")

    # Get statistics
    stats = checker.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
