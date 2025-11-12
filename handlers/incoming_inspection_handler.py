"""
Incoming Inspection Handler - Manages sample receipt and inspection workflow.

Following LID/LIS framework structure for comprehensive incoming inspection.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.validators import IncomingInspectionValidator

logger = logging.getLogger(__name__)


class IncomingInspectionHandler:
    """Handler for incoming inspection processing and sample acceptance."""

    def __init__(self, data_dir: str = "data/inspections"):
        """Initialize incoming inspection handler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.validator = IncomingInspectionValidator()
        self.inspections_cache: Dict[str, Dict[str, Any]] = {}

    def create_inspection(self, service_request_id: str, inspector_info: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Create a new incoming inspection record.

        Args:
            service_request_id: Associated service request ID
            inspector_info: Inspector information dictionary

        Returns:
            Tuple of (success, message, inspection_object)
        """
        try:
            inspection_id = self.validator.generate_inspection_id()

            inspection_data = {
                "inspection_id": inspection_id,
                "inspection_date": datetime.now().isoformat(),
                "service_request_id": service_request_id,
                "inspector": inspector_info,
                "sample_receipt": self._init_sample_receipt(),
                "visual_inspection": self._init_visual_inspection(),
                "documentation_check": self._init_documentation_check(),
                "condition_assessment": self._init_condition_assessment(),
                "acceptance_decision": {},
                "workflow_metadata": {
                    "status": "Scheduled",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "notes": []
            }

            # Save inspection
            self._save_inspection(inspection_data)

            logger.info(f"Inspection {inspection_id} created for service request {service_request_id}")
            return True, f"Inspection {inspection_id} created successfully", inspection_data

        except Exception as e:
            logger.error(f"Failed to create inspection: {str(e)}")
            return False, f"Error creating inspection: {str(e)}", None

    def _init_sample_receipt(self) -> Dict[str, Any]:
        """Initialize sample receipt section."""
        return {
            "received_date": datetime.now().isoformat(),
            "received_by": "",
            "quantity_received": 0,
            "quantity_expected": 0,
            "quantity_match": False,
            "packaging_condition": "Good",
            "shipping_method": "",
            "tracking_number": ""
        }

    def _init_visual_inspection(self) -> Dict[str, Any]:
        """Initialize visual inspection section."""
        return {
            "overall_condition": "Good",
            "checklist": [],
            "physical_damage": {
                "present": False,
                "description": "",
                "severity": "None"
            },
            "contamination": {
                "present": False,
                "type": "",
                "severity": "None"
            },
            "labeling": {
                "present": True,
                "matches_documentation": True,
                "serial_numbers_visible": True
            }
        }

    def _init_documentation_check(self) -> Dict[str, Any]:
        """Initialize documentation check section."""
        return {
            "completeness_status": "Complete",
            "required_documents": [
                {"document_name": "Packing List", "required": True, "received": False, "acceptable": False},
                {"document_name": "Certificate of Conformity", "required": True, "received": False, "acceptable": False},
                {"document_name": "Test Report", "required": False, "received": False, "acceptable": False},
                {"document_name": "Material Safety Data Sheet", "required": False, "received": False, "acceptable": False}
            ],
            "chain_of_custody": {
                "present": False,
                "complete": False,
                "signed": False
            }
        }

    def _init_condition_assessment(self) -> Dict[str, Any]:
        """Initialize condition assessment section."""
        return {
            "ready_for_testing": False,
            "overall_rating": "Acceptable",
            "dimensional_check": {
                "performed": False,
                "within_tolerance": True
            },
            "electrical_safety_check": {
                "performed": False,
                "safe": True
            },
            "acclimation_required": {
                "required": False,
                "duration_hours": 24
            }
        }

    def update_inspection(self, inspection_id: str, section: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update specific section of inspection.

        Args:
            inspection_id: Inspection ID
            section: Section name to update
            data: Updated data for the section

        Returns:
            Tuple of (success, message)
        """
        try:
            inspection = self.get_inspection(inspection_id)
            if not inspection:
                return False, f"Inspection {inspection_id} not found"

            # Update specific section
            if section in inspection:
                inspection[section] = data
                inspection["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

                # Save updated inspection
                self._save_inspection(inspection)

                logger.info(f"Inspection {inspection_id} section '{section}' updated")
                return True, f"Inspection section '{section}' updated successfully"
            else:
                return False, f"Invalid section: {section}"

        except Exception as e:
            logger.error(f"Failed to update inspection {inspection_id}: {str(e)}")
            return False, f"Error updating inspection: {str(e)}"

    def make_acceptance_decision(self, inspection_id: str, decision: str, decision_by: str,
                                rationale: str, **kwargs) -> Tuple[bool, str]:
        """
        Make final acceptance decision for samples.

        Args:
            inspection_id: Inspection ID
            decision: Accept/Accept with Conditions/Hold/Reject
            decision_by: Person making decision
            rationale: Decision rationale
            **kwargs: Additional decision parameters

        Returns:
            Tuple of (success, message)
        """
        try:
            inspection = self.get_inspection(inspection_id)
            if not inspection:
                return False, f"Inspection {inspection_id} not found"

            # Create acceptance decision
            acceptance_decision = {
                "decision": decision,
                "decision_date": datetime.now().isoformat(),
                "decision_by": decision_by,
                "rationale": rationale
            }

            # Add optional fields
            if "conditions" in kwargs:
                acceptance_decision["conditions"] = kwargs["conditions"]
            if "hold_reason" in kwargs:
                acceptance_decision["hold_reason"] = kwargs["hold_reason"]
            if "reject_reason" in kwargs:
                acceptance_decision["reject_reason"] = kwargs["reject_reason"]

            inspection["acceptance_decision"] = acceptance_decision
            inspection["workflow_metadata"]["status"] = "Completed"
            inspection["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Update condition assessment based on decision
            if decision in ["Accept", "Accept with Conditions"]:
                inspection["condition_assessment"]["ready_for_testing"] = True

            # Save updated inspection
            self._save_inspection(inspection)

            logger.info(f"Acceptance decision '{decision}' made for inspection {inspection_id}")
            return True, f"Acceptance decision '{decision}' recorded successfully"

        except Exception as e:
            logger.error(f"Failed to make acceptance decision for {inspection_id}: {str(e)}")
            return False, f"Error making acceptance decision: {str(e)}"

    def get_inspection(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve inspection by ID."""
        if inspection_id in self.inspections_cache:
            return self.inspections_cache[inspection_id]

        inspection_file = self.data_dir / f"{inspection_id}.json"
        if inspection_file.exists():
            with open(inspection_file, 'r') as f:
                inspection_data = json.load(f)
                self.inspections_cache[inspection_id] = inspection_data
                return inspection_data

        return None

    def list_inspections(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all inspections, optionally filtered by status."""
        inspections = []

        for inspection_file in self.data_dir.glob("II-*.json"):
            try:
                with open(inspection_file, 'r') as f:
                    inspection = json.load(f)
                    status = inspection.get("workflow_metadata", {}).get("status")

                    if status_filter and status != status_filter:
                        continue

                    inspections.append({
                        "inspection_id": inspection["inspection_id"],
                        "service_request_id": inspection["service_request_id"],
                        "inspection_date": inspection["inspection_date"],
                        "inspector": inspection["inspector"]["name"],
                        "status": status,
                        "acceptance_decision": inspection.get("acceptance_decision", {}).get("decision")
                    })
            except Exception as e:
                logger.warning(f"Failed to load inspection {inspection_file}: {str(e)}")

        return sorted(inspections, key=lambda x: x["inspection_date"], reverse=True)

    def _save_inspection(self, inspection_data: Dict[str, Any]):
        """Save inspection to disk and cache."""
        inspection_id = inspection_data["inspection_id"]
        inspection_file = self.data_dir / f"{inspection_id}.json"

        with open(inspection_file, 'w') as f:
            json.dump(inspection_data, f, indent=2)

        self.inspections_cache[inspection_id] = inspection_data

    def add_note(self, inspection_id: str, note: str, author: str, category: str = "General") -> Tuple[bool, str]:
        """Add note to inspection."""
        try:
            inspection = self.get_inspection(inspection_id)
            if not inspection:
                return False, f"Inspection {inspection_id} not found"

            if "notes" not in inspection:
                inspection["notes"] = []

            inspection["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "author": author,
                "note": note,
                "category": category
            })

            inspection["workflow_metadata"]["updated_at"] = datetime.now().isoformat()
            self._save_inspection(inspection)

            return True, "Note added successfully"

        except Exception as e:
            return False, f"Error adding note: {str(e)}"
