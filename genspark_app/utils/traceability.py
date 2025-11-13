"""
Traceability Management

Provides complete data traceability from raw data to final reports:
- Audit trail logging
- Data lineage tracking
- Version control
- Change history
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import logging
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class TraceabilityManager:
    """Manage data traceability and audit trails"""

    def __init__(self, db_session=None):
        """
        Initialize traceability manager

        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session
        self.audit_records = []

    def log_action(
        self,
        table_name: str,
        record_id: str,
        action: str,
        user_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Log an action to the audit trail

        Args:
            table_name: Database table name
            record_id: Record identifier
            action: Action type (create, update, delete, approve, etc.)
            user_id: User who performed the action
            old_values: Previous values (for updates)
            new_values: New values
            notes: Additional notes
            ip_address: User's IP address
            user_agent: User's browser/client

        Returns:
            Audit record ID
        """
        try:
            audit_record = {
                'id': str(uuid4()),
                'table_name': table_name,
                'record_id': record_id,
                'action': action,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'old_values': old_values,
                'new_values': new_values,
                'notes': notes,
                'ip_address': ip_address,
                'user_agent': user_agent
            }

            # Store in memory
            self.audit_records.append(audit_record)

            # Persist to database if available
            if self.db_session:
                self._persist_audit_record(audit_record)

            logger.info(f"Audit logged: {table_name}.{record_id} - {action}")
            return audit_record['id']

        except Exception as e:
            logger.error(f"Failed to log audit trail: {e}")
            return ""

    def _persist_audit_record(self, audit_record: Dict[str, Any]):
        """Persist audit record to database"""
        # In production: save to audit_trail table
        pass

    def track_file(
        self,
        file_path: str,
        test_execution_id: str,
        uploaded_by: Optional[str] = None,
        equipment_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a raw data file

        Args:
            file_path: Path to the file
            test_execution_id: Associated test execution
            uploaded_by: User who uploaded the file
            equipment_id: Equipment that generated the data
            metadata: Additional metadata

        Returns:
            File tracking record
        """
        try:
            # Calculate file checksum
            checksum = self._calculate_checksum(file_path)

            file_record = {
                'id': str(uuid4()),
                'file_path': file_path,
                'filename': file_path.split('/')[-1],
                'test_execution_id': test_execution_id,
                'uploaded_by': uploaded_by,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'checksum': checksum,
                'equipment_id': equipment_id,
                'metadata': metadata or {}
            }

            logger.info(f"File tracked: {file_path} (checksum: {checksum[:8]}...)")
            return file_record

        except Exception as e:
            logger.error(f"Failed to track file: {e}")
            return {}

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""

    def verify_file_integrity(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file integrity using checksum"""
        try:
            actual_checksum = self._calculate_checksum(file_path)
            is_valid = actual_checksum == expected_checksum

            if is_valid:
                logger.info(f"File integrity verified: {file_path}")
            else:
                logger.error(f"File integrity check FAILED: {file_path}")

            return is_valid

        except Exception as e:
            logger.error(f"File integrity verification failed: {e}")
            return False

    def create_lineage(
        self,
        test_execution_id: str,
        raw_data_files: List[str],
        processed_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        report_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create data lineage record

        Args:
            test_execution_id: Test execution ID
            raw_data_files: List of raw data file IDs
            processed_data: Processed data identifiers
            analysis_results: Analysis result identifiers
            report_path: Path to generated report

        Returns:
            Data lineage record
        """
        lineage = {
            'id': str(uuid4()),
            'test_execution_id': test_execution_id,
            'created_at': datetime.utcnow().isoformat(),
            'lineage_chain': {
                'raw_data': raw_data_files,
                'processed_data': processed_data,
                'analysis_results': analysis_results,
                'report': report_path
            },
            'traceability_complete': True
        }

        logger.info(f"Data lineage created for test execution: {test_execution_id}")
        return lineage

    def get_audit_trail(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail records with filters

        Args:
            table_name: Filter by table name
            record_id: Filter by record ID
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of audit records
        """
        filtered_records = self.audit_records.copy()

        if table_name:
            filtered_records = [r for r in filtered_records if r['table_name'] == table_name]

        if record_id:
            filtered_records = [r for r in filtered_records if r['record_id'] == record_id]

        if user_id:
            filtered_records = [r for r in filtered_records if r['user_id'] == user_id]

        if start_date:
            filtered_records = [
                r for r in filtered_records
                if datetime.fromisoformat(r['timestamp']) >= start_date
            ]

        if end_date:
            filtered_records = [
                r for r in filtered_records
                if datetime.fromisoformat(r['timestamp']) <= end_date
            ]

        return filtered_records

    def generate_traceability_report(
        self,
        test_execution_id: str
    ) -> Dict[str, Any]:
        """
        Generate complete traceability report for a test execution

        Args:
            test_execution_id: Test execution ID

        Returns:
            Comprehensive traceability report
        """
        try:
            # Get all audit records for this test execution
            audit_records = self.get_audit_trail(
                table_name='test_executions',
                record_id=test_execution_id
            )

            report = {
                'test_execution_id': test_execution_id,
                'report_generated': datetime.utcnow().isoformat(),
                'audit_trail': audit_records,
                'raw_data_files': self._get_associated_files(test_execution_id),
                'measurements': self._get_associated_measurements(test_execution_id),
                'analysis_results': self._get_associated_analysis(test_execution_id),
                'change_history': self._get_change_history(test_execution_id),
                'personnel': self._get_personnel_involved(test_execution_id),
                'equipment_used': self._get_equipment_used(test_execution_id)
            }

            logger.info(f"Traceability report generated for: {test_execution_id}")
            return report

        except Exception as e:
            logger.error(f"Traceability report generation failed: {e}")
            return {}

    def _get_associated_files(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get files associated with test execution"""
        # In production: query raw_data_files table
        return []

    def _get_associated_measurements(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get measurements associated with test execution"""
        # In production: query measurement_data table
        return []

    def _get_associated_analysis(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get analysis results associated with test execution"""
        # In production: query analysis_results table
        return []

    def _get_change_history(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get change history for test execution"""
        return self.get_audit_trail(
            table_name='test_executions',
            record_id=test_execution_id
        )

    def _get_personnel_involved(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get personnel involved in test execution"""
        # In production: query users and test_executions
        return []

    def _get_equipment_used(self, test_execution_id: str) -> List[Dict[str, Any]]:
        """Get equipment used in test execution"""
        # In production: query equipment_bookings
        return []

    def validate_chain_of_custody(self, test_execution_id: str) -> Dict[str, Any]:
        """
        Validate complete chain of custody for a test execution

        Args:
            test_execution_id: Test execution ID

        Returns:
            Validation result with any gaps or issues
        """
        try:
            audit_trail = self.get_audit_trail(
                table_name='test_executions',
                record_id=test_execution_id
            )

            # Check for required actions
            required_actions = ['create', 'setup', 'execute', 'analyze', 'validate', 'complete']
            found_actions = [record['action'] for record in audit_trail]

            missing_actions = [action for action in required_actions if action not in found_actions]

            # Check for data integrity
            has_raw_data = len(self._get_associated_files(test_execution_id)) > 0
            has_measurements = len(self._get_associated_measurements(test_execution_id)) > 0
            has_analysis = len(self._get_associated_analysis(test_execution_id)) > 0

            is_valid = (
                len(missing_actions) == 0 and
                has_raw_data and
                has_measurements and
                has_analysis
            )

            validation_result = {
                'test_execution_id': test_execution_id,
                'is_valid': is_valid,
                'validation_timestamp': datetime.utcnow().isoformat(),
                'missing_actions': missing_actions,
                'has_raw_data': has_raw_data,
                'has_measurements': has_measurements,
                'has_analysis': has_analysis,
                'audit_trail_complete': len(audit_trail) > 0
            }

            if is_valid:
                logger.info(f"Chain of custody validated for: {test_execution_id}")
            else:
                logger.warning(f"Chain of custody validation FAILED for: {test_execution_id}")

            return validation_result

        except Exception as e:
            logger.error(f"Chain of custody validation failed: {e}")
            return {'is_valid': False, 'error': str(e)}
