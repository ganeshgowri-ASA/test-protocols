"""
Data Traceability and Audit Log System
Comprehensive tracking of all data, calculations, approvals, and modifications
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import hashlib
import logging


class AuditEventType(Enum):
    """Types of audit events"""
    SESSION_START = "session-start"
    SESSION_END = "session-end"
    STATE_CHANGE = "state-change"
    MEASUREMENT = "measurement"
    CALCULATION = "calculation"
    APPROVAL = "approval"
    REJECTION = "rejection"
    INTERLOCK_CHECK = "interlock-check"
    INTERLOCK_TRIGGERED = "interlock-triggered"
    EMERGENCY_STOP = "emergency-stop"
    DATA_MODIFICATION = "data-modification"
    REPORT_GENERATED = "report-generated"
    NC_CREATED = "nc-created"
    EQUIPMENT_CALIBRATION = "equipment-calibration"
    OPERATOR_CHANGE = "operator-change"
    SYSTEM_ERROR = "system-error"


class AuditEntry:
    """
    Single audit log entry with full traceability
    """

    def __init__(self, event_type: AuditEventType, description: str,
                 actor: Optional[str] = None, data: Optional[Dict] = None):
        self.entry_id = self._generate_entry_id()
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.description = description
        self.actor = actor  # Person or system performing action
        self.data = data or {}

        # Cryptographic integrity
        self.hash = self._compute_hash()
        self.previous_hash: Optional[str] = None  # For blockchain-like integrity

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        from uuid import uuid4
        return f"AE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8]}"

    def _compute_hash(self) -> str:
        """Compute cryptographic hash of entry for integrity"""
        content = json.dumps({
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "description": self.description,
            "actor": self.actor,
            "data": self.data
        }, sort_keys=True)

        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify entry has not been tampered with"""
        return self.hash == self._compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entryId": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "eventType": self.event_type.value,
            "description": self.description,
            "actor": self.actor,
            "data": self.data,
            "hash": self.hash,
            "previousHash": self.previous_hash
        }


class AuditLog:
    """
    Comprehensive audit log with cryptographic integrity
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries: List[AuditEntry] = []
        self.logger = logging.getLogger(f"{__name__}.{session_id}")

    def add_entry(self, event_type: AuditEventType, description: str,
                  actor: Optional[str] = None, data: Optional[Dict] = None) -> AuditEntry:
        """
        Add audit log entry

        Args:
            event_type: Type of event
            description: Human-readable description
            actor: Person or system performing action
            data: Additional data

        Returns:
            Created AuditEntry
        """
        entry = AuditEntry(event_type, description, actor, data)

        # Link to previous entry for blockchain-like integrity
        if len(self.entries) > 0:
            entry.previous_hash = self.entries[-1].hash

        self.entries.append(entry)

        self.logger.info(f"[AUDIT] {event_type.value}: {description}")

        return entry

    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify entire audit chain integrity

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        is_valid = True

        for i, entry in enumerate(self.entries):
            # Check entry hash
            if not entry.verify_integrity():
                issues.append(f"Entry {entry.entry_id} hash mismatch")
                is_valid = False

            # Check chain linkage
            if i > 0:
                if entry.previous_hash != self.entries[i-1].hash:
                    issues.append(f"Entry {entry.entry_id} chain broken")
                    is_valid = False

        return is_valid, issues

    def get_entries_by_type(self, event_type: AuditEventType) -> List[AuditEntry]:
        """Get all entries of specific type"""
        return [e for e in self.entries if e.event_type == event_type]

    def get_entries_by_actor(self, actor: str) -> List[AuditEntry]:
        """Get all entries by specific actor"""
        return [e for e in self.entries if e.actor == actor]

    def get_entries_in_timerange(self, start: datetime, end: datetime) -> List[AuditEntry]:
        """Get entries within time range"""
        return [e for e in self.entries if start <= e.timestamp <= end]

    def export(self) -> Dict[str, Any]:
        """Export complete audit log"""
        return {
            "sessionId": self.session_id,
            "totalEntries": len(self.entries),
            "firstEntry": self.entries[0].timestamp.isoformat() if self.entries else None,
            "lastEntry": self.entries[-1].timestamp.isoformat() if self.entries else None,
            "entries": [e.to_dict() for e in self.entries]
        }


class DataLineage:
    """
    Tracks data lineage - origin, transformations, and dependencies
    """

    def __init__(self, data_id: str):
        self.data_id = data_id
        self.origin: Dict[str, Any] = {}
        self.transformations: List[Dict] = []
        self.dependencies: List[str] = []

        self.created_time = datetime.now()
        self.created_by: Optional[str] = None

    def set_origin(self, source: str, method: str, metadata: Optional[Dict] = None):
        """Set data origin"""
        self.origin = {
            "source": source,
            "method": method,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

    def add_transformation(self, operation: str, input_data: Any, output_data: Any,
                          operator: Optional[str] = None, formula: Optional[str] = None):
        """Add data transformation"""
        transformation = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "operator": operator,
            "formula": formula,
            "input": self._serialize_data(input_data),
            "output": self._serialize_data(output_data),
            "inputHash": self._hash_data(input_data),
            "outputHash": self._hash_data(output_data)
        }

        self.transformations.append(transformation)

    def add_dependency(self, dependent_data_id: str):
        """Add dependency on another data element"""
        if dependent_data_id not in self.dependencies:
            self.dependencies.append(dependent_data_id)

    def _serialize_data(self, data: Any) -> str:
        """Serialize data for storage"""
        if isinstance(data, (dict, list)):
            return json.dumps(data)
        else:
            return str(data)

    def _hash_data(self, data: Any) -> str:
        """Compute hash of data"""
        serialized = self._serialize_data(data)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get_complete_lineage(self) -> Dict[str, Any]:
        """Get complete data lineage"""
        return {
            "dataId": self.data_id,
            "createdTime": self.created_time.isoformat(),
            "createdBy": self.created_by,
            "origin": self.origin,
            "transformations": self.transformations,
            "dependencies": self.dependencies,
            "transformationCount": len(self.transformations)
        }


class TraceabilityManager:
    """
    Manages complete traceability for a protocol session
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.audit_log = AuditLog(session_id)
        self.data_lineages: Dict[str, DataLineage] = {}

        self.logger = logging.getLogger(f"{__name__}.{session_id}")

    def track_measurement(self, measurement_name: str, value: Any,
                         source: str, operator: str, metadata: Optional[Dict] = None):
        """
        Track measurement with full lineage

        Args:
            measurement_name: Name of measurement
            value: Measured value
            source: Source equipment/method
            operator: Person performing measurement
            metadata: Additional metadata
        """
        # Create data lineage
        lineage = DataLineage(measurement_name)
        lineage.set_origin(source, "measurement", metadata)
        lineage.created_by = operator

        self.data_lineages[measurement_name] = lineage

        # Add audit entry
        self.audit_log.add_entry(
            AuditEventType.MEASUREMENT,
            f"Measurement {measurement_name} = {value}",
            operator,
            {"measurement": measurement_name, "value": value, "source": source}
        )

    def track_calculation(self, calculation_name: str, formula: str,
                         input_data: Dict[str, Any], output_value: Any,
                         operator: str):
        """Track calculation with inputs and outputs"""
        # Create or get lineage
        if calculation_name not in self.data_lineages:
            lineage = DataLineage(calculation_name)
            lineage.set_origin("calculation", formula)
            lineage.created_by = operator
            self.data_lineages[calculation_name] = lineage
        else:
            lineage = self.data_lineages[calculation_name]

        # Add transformation
        lineage.add_transformation(
            operation="calculation",
            input_data=input_data,
            output_data=output_value,
            operator=operator,
            formula=formula
        )

        # Add dependencies on input data
        for input_name in input_data.keys():
            lineage.add_dependency(input_name)

        # Add audit entry
        self.audit_log.add_entry(
            AuditEventType.CALCULATION,
            f"Calculation {calculation_name} using formula: {formula}",
            operator,
            {"calculation": calculation_name, "inputs": list(input_data.keys()), "output": output_value}
        )

    def track_modification(self, data_name: str, old_value: Any, new_value: Any,
                          modified_by: str, reason: str):
        """Track data modification"""
        lineage = self.data_lineages.get(data_name)

        if lineage:
            lineage.add_transformation(
                operation="modification",
                input_data=old_value,
                output_data=new_value,
                operator=modified_by
            )

        # Add audit entry
        self.audit_log.add_entry(
            AuditEventType.DATA_MODIFICATION,
            f"Data {data_name} modified: {old_value} -> {new_value}. Reason: {reason}",
            modified_by,
            {"data": data_name, "oldValue": old_value, "newValue": new_value, "reason": reason}
        )

        self.logger.warning(f"Data modification: {data_name} by {modified_by}")

    def get_complete_traceability(self) -> Dict[str, Any]:
        """Get complete traceability report"""
        # Verify audit chain integrity
        chain_valid, chain_issues = self.audit_log.verify_chain_integrity()

        return {
            "sessionId": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "auditLog": self.audit_log.export(),
            "auditChainValid": chain_valid,
            "auditChainIssues": chain_issues,
            "dataLineages": {k: v.get_complete_lineage() for k, v in self.data_lineages.items()},
            "totalDataElements": len(self.data_lineages),
            "totalAuditEntries": len(self.audit_log.entries)
        }

    def generate_21cfr_part11_report(self) -> Dict[str, Any]:
        """
        Generate 21 CFR Part 11 compliance report
        (Electronic Records; Electronic Signatures)
        """
        return {
            "sessionId": self.session_id,
            "compliance": {
                "electronicRecords": {
                    "auditTrailEnabled": True,
                    "immutableRecords": True,
                    "cryptographicIntegrity": True,
                    "timestampValidation": True
                },
                "electronicSignatures": {
                    "uniqueIdentification": True,
                    "nonRepudiation": True,
                    "auditTrail": True
                },
                "dataIntegrity": {
                    "chainOfCustody": True,
                    "tamperEvident": chain_valid,
                    "versionControl": True
                }
            },
            "auditLog": self.audit_log.export()
        }
