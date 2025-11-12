"""
Traceability Engine - Complete audit trail system for workflow orchestration.

Tracks data lineage from Service Request → Inspection → Equipment → Protocol → Analysis → Report
Provides unique tracking IDs, timestamps, versioning, and comprehensive audit reports.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import sys

sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class TraceabilityEvent:
    """Represents a single traceability event in the audit trail."""

    def __init__(self, event_type: str, entity_type: str, entity_id: str,
                 action: str, user: str, data: Dict[str, Any] = None):
        """
        Initialize traceability event.

        Args:
            event_type: Type of event (create, update, approve, reject, etc.)
            entity_type: Type of entity (service_request, inspection, equipment_plan, etc.)
            entity_id: Unique identifier of the entity
            action: Action performed
            user: User who performed the action
            data: Additional event data
        """
        self.event_id = self._generate_event_id()
        self.timestamp = datetime.now().isoformat()
        self.event_type = event_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.user = user
        self.data = data or {}
        self.data_hash = self._calculate_data_hash()

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"EVT-{timestamp}"

    def _calculate_data_hash(self) -> str:
        """Calculate hash of event data for integrity verification."""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "user": self.user,
            "data": self.data,
            "data_hash": self.data_hash
        }


class TraceabilityEngine:
    """
    Engine for tracking complete data lineage and audit trails.

    Maintains comprehensive traceability across all workflow stages with
    version control, integrity verification, and audit reporting.
    """

    def __init__(self, data_dir: str = "data/traceability"):
        """
        Initialize traceability engine.

        Args:
            data_dir: Directory for storing traceability data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Audit trail storage
        self.audit_trail: List[TraceabilityEvent] = []

        # Entity relationship mapping
        self.entity_relationships: Dict[str, Dict[str, Any]] = {}

        # Load existing audit trail
        self._load_audit_trail()

    def _load_audit_trail(self):
        """Load existing audit trail from disk."""
        trail_file = self.data_dir / "audit_trail.json"
        if trail_file.exists():
            try:
                with open(trail_file, 'r') as f:
                    trail_data = json.load(f)
                    # Convert back to TraceabilityEvent objects
                    for event_data in trail_data:
                        event = TraceabilityEvent(
                            event_data["event_type"],
                            event_data["entity_type"],
                            event_data["entity_id"],
                            event_data["action"],
                            event_data["user"],
                            event_data.get("data", {})
                        )
                        event.event_id = event_data["event_id"]
                        event.timestamp = event_data["timestamp"]
                        event.data_hash = event_data["data_hash"]
                        self.audit_trail.append(event)
            except Exception as e:
                logger.warning(f"Failed to load audit trail: {str(e)}")

    def record_event(self, event_type: str, entity_type: str, entity_id: str,
                    action: str, user: str, data: Dict[str, Any] = None) -> str:
        """
        Record a traceability event.

        Args:
            event_type: Type of event
            entity_type: Type of entity
            entity_id: Entity identifier
            action: Action performed
            user: User who performed action
            data: Additional event data

        Returns:
            Event ID
        """
        event = TraceabilityEvent(event_type, entity_type, entity_id, action, user, data)
        self.audit_trail.append(event)

        # Save to disk
        self._save_audit_trail()

        logger.info(f"Traceability event {event.event_id} recorded: {action} on {entity_type} {entity_id}")

        return event.event_id

    def record_entity_link(self, source_entity_type: str, source_entity_id: str,
                          target_entity_type: str, target_entity_id: str,
                          relationship_type: str):
        """
        Record relationship between entities for data lineage tracking.

        Args:
            source_entity_type: Source entity type
            source_entity_id: Source entity ID
            target_entity_type: Target entity type
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
        """
        link_key = f"{source_entity_type}:{source_entity_id}"

        if link_key not in self.entity_relationships:
            self.entity_relationships[link_key] = {
                "entity_type": source_entity_type,
                "entity_id": source_entity_id,
                "links": []
            }

        self.entity_relationships[link_key]["links"].append({
            "target_entity_type": target_entity_type,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type,
            "created_at": datetime.now().isoformat()
        })

        # Save relationships
        self._save_relationships()

        logger.info(f"Entity link recorded: {source_entity_id} -> {target_entity_id} ({relationship_type})")

    def get_entity_lineage(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Get complete lineage for an entity.

        Args:
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Lineage dictionary showing all related entities
        """
        link_key = f"{entity_type}:{entity_id}"

        if link_key not in self.entity_relationships:
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "links": [],
                "upstream_entities": [],
                "downstream_entities": []
            }

        lineage = self.entity_relationships[link_key].copy()

        # Find upstream entities (entities that link to this one)
        upstream = []
        for key, relationship in self.entity_relationships.items():
            for link in relationship["links"]:
                if (link["target_entity_type"] == entity_type and
                    link["target_entity_id"] == entity_id):
                    upstream.append({
                        "entity_type": relationship["entity_type"],
                        "entity_id": relationship["entity_id"],
                        "relationship_type": link["relationship_type"]
                    })

        lineage["upstream_entities"] = upstream
        lineage["downstream_entities"] = lineage["links"]

        return lineage

    def get_audit_trail(self, entity_type: Optional[str] = None,
                       entity_id: Optional[str] = None,
                       user: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filters.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            user: Filter by user
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)

        Returns:
            List of audit events matching filters
        """
        filtered_events = []

        for event in self.audit_trail:
            # Apply filters
            if entity_type and event.entity_type != entity_type:
                continue
            if entity_id and event.entity_id != entity_id:
                continue
            if user and event.user != user:
                continue
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue

            filtered_events.append(event.to_dict())

        return sorted(filtered_events, key=lambda x: x["timestamp"], reverse=True)

    def generate_traceability_report(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive traceability report for an entity.

        Args:
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            Comprehensive traceability report
        """
        # Get lineage
        lineage = self.get_entity_lineage(entity_type, entity_id)

        # Get audit events
        audit_events = self.get_audit_trail(entity_type=entity_type, entity_id=entity_id)

        # Build complete chain
        complete_chain = self._build_complete_chain(entity_type, entity_id)

        report = {
            "report_id": f"TRC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "entity": {
                "entity_type": entity_type,
                "entity_id": entity_id
            },
            "lineage": lineage,
            "audit_events": audit_events,
            "complete_chain": complete_chain,
            "statistics": {
                "total_events": len(audit_events),
                "unique_users": len(set(e["user"] for e in audit_events)),
                "first_event": audit_events[-1]["timestamp"] if audit_events else None,
                "last_event": audit_events[0]["timestamp"] if audit_events else None,
                "upstream_entities_count": len(lineage.get("upstream_entities", [])),
                "downstream_entities_count": len(lineage.get("downstream_entities", []))
            }
        }

        # Save report
        report_file = self.data_dir / f"{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Traceability report {report['report_id']} generated for {entity_type} {entity_id}")

        return report

    def _build_complete_chain(self, entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
        """
        Build complete workflow chain from service request to report.

        Args:
            entity_type: Starting entity type
            entity_id: Starting entity ID

        Returns:
            List of entities in workflow chain
        """
        chain = []

        # Start with the entity
        chain.append({
            "stage": self._entity_type_to_stage(entity_type),
            "entity_type": entity_type,
            "entity_id": entity_id
        })

        # Follow links downstream
        link_key = f"{entity_type}:{entity_id}"
        if link_key in self.entity_relationships:
            for link in self.entity_relationships[link_key]["links"]:
                chain.append({
                    "stage": self._entity_type_to_stage(link["target_entity_type"]),
                    "entity_type": link["target_entity_type"],
                    "entity_id": link["target_entity_id"],
                    "relationship": link["relationship_type"]
                })

        return chain

    def _entity_type_to_stage(self, entity_type: str) -> str:
        """Map entity type to workflow stage."""
        mapping = {
            "service_request": "1. Service Request",
            "inspection": "2. Incoming Inspection",
            "equipment_plan": "3. Equipment Planning",
            "protocol_execution": "4. Protocol Execution",
            "analysis": "5. Analysis",
            "report": "6. Report Generation"
        }
        return mapping.get(entity_type, entity_type)

    def verify_integrity(self, event_id: str) -> Tuple[bool, str]:
        """
        Verify integrity of an audit event.

        Args:
            event_id: Event ID to verify

        Returns:
            Tuple of (is_valid, message)
        """
        for event in self.audit_trail:
            if event.event_id == event_id:
                # Recalculate hash
                data_str = json.dumps(event.data, sort_keys=True)
                calculated_hash = hashlib.sha256(data_str.encode()).hexdigest()

                if calculated_hash == event.data_hash:
                    return True, "Event integrity verified"
                else:
                    return False, "Event integrity check failed - data may have been tampered with"

        return False, f"Event {event_id} not found"

    def export_audit_trail(self, output_format: str = "json") -> Tuple[bool, str, Optional[str]]:
        """
        Export complete audit trail.

        Args:
            output_format: Output format (json, csv)

        Returns:
            Tuple of (success, message, file_path)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            if output_format == "json":
                export_file = self.data_dir / f"audit_trail_export_{timestamp}.json"
                with open(export_file, 'w') as f:
                    json.dump([e.to_dict() for e in self.audit_trail], f, indent=2)

            elif output_format == "csv":
                export_file = self.data_dir / f"audit_trail_export_{timestamp}.csv"
                # CSV export logic would go here
                return False, "CSV export not yet implemented", None

            else:
                return False, f"Unsupported output format: {output_format}", None

            logger.info(f"Audit trail exported to {export_file}")
            return True, f"Audit trail exported successfully", str(export_file)

        except Exception as e:
            logger.error(f"Failed to export audit trail: {str(e)}")
            return False, f"Export failed: {str(e)}", None

    def _save_audit_trail(self):
        """Save audit trail to disk."""
        trail_file = self.data_dir / "audit_trail.json"
        with open(trail_file, 'w') as f:
            json.dump([e.to_dict() for e in self.audit_trail], f, indent=2)

    def _save_relationships(self):
        """Save entity relationships to disk."""
        rel_file = self.data_dir / "entity_relationships.json"
        with open(rel_file, 'w') as f:
            json.dump(self.entity_relationships, f, indent=2)

    def get_statistics(self) -> Dict[str, Any]:
        """Get traceability statistics."""
        return {
            "total_events": len(self.audit_trail),
            "total_entity_relationships": len(self.entity_relationships),
            "entity_types": list(set(e.entity_type for e in self.audit_trail)),
            "event_types": list(set(e.event_type for e in self.audit_trail)),
            "unique_users": list(set(e.user for e in self.audit_trail)),
            "date_range": {
                "first_event": self.audit_trail[0].timestamp if self.audit_trail else None,
                "last_event": self.audit_trail[-1].timestamp if self.audit_trail else None
            }
        }
