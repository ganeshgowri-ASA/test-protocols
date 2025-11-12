"""
Protocol Versioning
Protocol version control, change management, and backwards compatibility
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
import difflib

logger = logging.getLogger(__name__)


class VersionType(Enum):
    """Version change type"""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backwards compatible
    PATCH = "patch"  # Bug fixes


class ChangeType(Enum):
    """Type of change"""
    ADDITION = "addition"
    MODIFICATION = "modification"
    DELETION = "deletion"
    DEPRECATION = "deprecation"


@dataclass
class ProtocolVersion:
    """Protocol version record"""
    version_id: str
    protocol_id: str
    version_number: str
    version_type: VersionType
    release_date: datetime
    author: str
    approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    changelog: List[Dict] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    deprecations: List[str] = field(default_factory=list)
    migration_guide: str = ""
    compatibility_notes: str = ""
    is_active: bool = True
    is_deprecated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version_id': self.version_id,
            'protocol_id': self.protocol_id,
            'version_number': self.version_number,
            'version_type': self.version_type.value,
            'release_date': self.release_date.isoformat(),
            'author': self.author,
            'approver': self.approver,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'changelog': self.changelog,
            'breaking_changes': self.breaking_changes,
            'deprecations': self.deprecations,
            'migration_guide': self.migration_guide,
            'compatibility_notes': self.compatibility_notes,
            'is_active': self.is_active,
            'is_deprecated': self.is_deprecated,
            'metadata': self.metadata
        }


class ProtocolVersioning:
    """Protocol version control system"""

    def __init__(self, db_path: str = "protocol_versions.db"):
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"ProtocolVersioning initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protocol_versions (
                    version_id TEXT PRIMARY KEY,
                    protocol_id TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    version_type TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    author TEXT NOT NULL,
                    approver TEXT,
                    approval_date TEXT,
                    changelog TEXT,
                    breaking_changes TEXT,
                    deprecations TEXT,
                    migration_guide TEXT,
                    compatibility_notes TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_deprecated INTEGER DEFAULT 0,
                    metadata TEXT,
                    UNIQUE(protocol_id, version_number)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS version_dependencies (
                    dependency_id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    depends_on_protocol TEXT NOT NULL,
                    depends_on_version TEXT NOT NULL,
                    dependency_type TEXT,
                    FOREIGN KEY (version_id) REFERENCES protocol_versions(version_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compatibility_matrix (
                    matrix_id TEXT PRIMARY KEY,
                    protocol_id TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    compatible_with_protocol TEXT NOT NULL,
                    compatible_with_version TEXT NOT NULL,
                    compatibility_level TEXT,
                    notes TEXT
                )
            """)

            logger.info("Protocol versioning database schema initialized")

    def create_version(
        self,
        protocol_id: str,
        version_number: str,
        version_type: VersionType,
        author: str,
        changelog: List[Dict],
        breaking_changes: Optional[List[str]] = None,
        migration_guide: str = "",
        metadata: Optional[Dict] = None
    ) -> ProtocolVersion:
        """Create new protocol version"""
        version = ProtocolVersion(
            version_id=str(uuid.uuid4()),
            protocol_id=protocol_id,
            version_number=version_number,
            version_type=version_type,
            release_date=datetime.now(timezone.utc),
            author=author,
            approver=None,
            approval_date=None,
            changelog=changelog,
            breaking_changes=breaking_changes or [],
            deprecations=[],
            migration_guide=migration_guide,
            compatibility_notes="",
            is_active=True,
            is_deprecated=False,
            metadata=metadata or {}
        )

        self._store_version(version)
        logger.info(f"Created protocol version: {version.version_number}")
        return version

    def _store_version(self, version: ProtocolVersion):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO protocol_versions
                (version_id, protocol_id, version_number, version_type, release_date,
                 author, approver, approval_date, changelog, breaking_changes, deprecations,
                 migration_guide, compatibility_notes, is_active, is_deprecated, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.version_id,
                version.protocol_id,
                version.version_number,
                version.version_type.value,
                version.release_date.isoformat(),
                version.author,
                version.approver,
                version.approval_date.isoformat() if version.approval_date else None,
                json.dumps(version.changelog),
                json.dumps(version.breaking_changes),
                json.dumps(version.deprecations),
                version.migration_guide,
                version.compatibility_notes,
                1 if version.is_active else 0,
                1 if version.is_deprecated else 0,
                json.dumps(version.metadata)
            ))

    def compare_versions(
        self,
        protocol_id: str,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """Compare two protocol versions"""
        v1 = self.get_version(protocol_id, version1)
        v2 = self.get_version(protocol_id, version2)

        if not v1 or not v2:
            return {'error': 'Version not found'}

        comparison = {
            'protocol_id': protocol_id,
            'version1': version1,
            'version2': version2,
            'changes': [],
            'breaking_changes': v2.breaking_changes if v2.breaking_changes else [],
            'new_features': [],
            'bug_fixes': [],
            'deprecations': v2.deprecations if v2.deprecations else []
        }

        # Analyze changelog
        for change in v2.changelog:
            change_type = change.get('type', 'unknown')
            if change_type == 'feature':
                comparison['new_features'].append(change)
            elif change_type == 'bugfix':
                comparison['bug_fixes'].append(change)
            comparison['changes'].append(change)

        return comparison

    def get_version(self, protocol_id: str, version_number: str) -> Optional[ProtocolVersion]:
        """Get specific version"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM protocol_versions
                WHERE protocol_id = ? AND version_number = ?
            """, (protocol_id, version_number))

            row = cursor.fetchone()
            if row:
                return ProtocolVersion(
                    version_id=row['version_id'],
                    protocol_id=row['protocol_id'],
                    version_number=row['version_number'],
                    version_type=VersionType(row['version_type']),
                    release_date=datetime.fromisoformat(row['release_date']),
                    author=row['author'],
                    approver=row['approver'],
                    approval_date=datetime.fromisoformat(row['approval_date']) if row['approval_date'] else None,
                    changelog=json.loads(row['changelog']),
                    breaking_changes=json.loads(row['breaking_changes']),
                    deprecations=json.loads(row['deprecations']),
                    migration_guide=row['migration_guide'],
                    compatibility_notes=row['compatibility_notes'],
                    is_active=bool(row['is_active']),
                    is_deprecated=bool(row['is_deprecated']),
                    metadata=json.loads(row['metadata'])
                )
        return None

    def get_version_history(self, protocol_id: str) -> List[ProtocolVersion]:
        """Get all versions of a protocol"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM protocol_versions
                WHERE protocol_id = ?
                ORDER BY release_date DESC
            """, (protocol_id,))

            versions = []
            for row in cursor.fetchall():
                versions.append(ProtocolVersion(
                    version_id=row['version_id'],
                    protocol_id=row['protocol_id'],
                    version_number=row['version_number'],
                    version_type=VersionType(row['version_type']),
                    release_date=datetime.fromisoformat(row['release_date']),
                    author=row['author'],
                    approver=row['approver'],
                    approval_date=datetime.fromisoformat(row['approval_date']) if row['approval_date'] else None,
                    changelog=json.loads(row['changelog']),
                    breaking_changes=json.loads(row['breaking_changes']),
                    deprecations=json.loads(row['deprecations']),
                    migration_guide=row['migration_guide'],
                    compatibility_notes=row['compatibility_notes'],
                    is_active=bool(row['is_active']),
                    is_deprecated=bool(row['is_deprecated']),
                    metadata=json.loads(row['metadata'])
                ))

            return versions


if __name__ == "__main__":
    versioning = ProtocolVersioning()

    # Create version
    version = versioning.create_version(
        protocol_id="PVTP-048",
        version_number="2.1.0",
        version_type=VersionType.MINOR,
        author="eng001",
        changelog=[
            {'type': 'feature', 'description': 'Added extended temperature range testing'},
            {'type': 'improvement', 'description': 'Improved data validation'},
            {'type': 'bugfix', 'description': 'Fixed timestamp formatting issue'}
        ],
        migration_guide="No migration required for existing tests"
    )

    print(f"Created version: {version.version_number}")

    # Get history
    history = versioning.get_version_history("PVTP-048")
    print(f"Version history: {len(history)} versions")
