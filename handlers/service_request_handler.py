"""
Service Request Handler - Processes and manages service request submissions.

Handles:
- Service request validation
- Request ID generation
- Work order creation
- Request approval workflow
- Integration with incoming inspection stage
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.validators import ServiceRequestValidator

logger = logging.getLogger(__name__)


class ServiceRequestHandler:
    """Handler for service request processing and management."""

    def __init__(self, data_dir: str = "data/service_requests"):
        """
        Initialize service request handler.

        Args:
            data_dir: Directory for storing service request data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.validator = ServiceRequestValidator()

        # Load existing requests into cache
        self.requests_cache: Dict[str, Dict[str, Any]] = {}
        self._load_existing_requests()

    def _load_existing_requests(self):
        """Load existing service requests from disk into cache."""
        for request_file in self.data_dir.glob("SR-*.json"):
            try:
                with open(request_file, 'r') as f:
                    request_data = json.load(f)
                    request_id = request_data.get("request_id")
                    if request_id:
                        self.requests_cache[request_id] = request_data
            except Exception as e:
                logger.warning(f"Failed to load request file {request_file}: {str(e)}")

    def create_service_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Create a new service request.

        Args:
            request_data: Service request data dictionary

        Returns:
            Tuple of (success, message, request_object)
        """
        try:
            # Generate request ID if not present
            if "request_id" not in request_data:
                request_data["request_id"] = self.validator.generate_request_id()

            # Add/update workflow metadata
            request_data = self.validator.add_workflow_metadata(request_data)

            # Set initial timestamps
            if "request_date" not in request_data:
                request_data["request_date"] = datetime.now().isoformat()

            # Validate against schema
            is_valid, error_msg = self.validator.validate(request_data)
            if not is_valid:
                return False, f"Validation failed: {error_msg}", None

            # Save to disk
            request_id = request_data["request_id"]
            request_file = self.data_dir / f"{request_id}.json"

            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2)

            # Update cache
            self.requests_cache[request_id] = request_data

            logger.info(f"Service request {request_id} created successfully")
            return True, f"Service request {request_id} created successfully", request_data

        except Exception as e:
            logger.error(f"Failed to create service request: {str(e)}")
            return False, f"Error creating service request: {str(e)}", None

    def submit_service_request(self, request_id: str) -> Tuple[bool, str]:
        """
        Submit a service request for approval.

        Args:
            request_id: Service request ID

        Returns:
            Tuple of (success, message)
        """
        try:
            request_data = self.get_service_request(request_id)
            if not request_data:
                return False, f"Service request {request_id} not found"

            # Update status
            request_data["workflow_metadata"]["status"] = "Submitted"
            request_data["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Add submission note
            if "workflow_metadata" in request_data:
                if "notes" not in request_data["workflow_metadata"]:
                    request_data["workflow_metadata"]["notes"] = []

                request_data["workflow_metadata"]["notes"].append({
                    "timestamp": datetime.now().isoformat(),
                    "user": "System",
                    "note": "Service request submitted for approval"
                })

            # Save updated request
            self._save_request(request_data)

            logger.info(f"Service request {request_id} submitted for approval")
            return True, f"Service request {request_id} submitted successfully"

        except Exception as e:
            logger.error(f"Failed to submit service request {request_id}: {str(e)}")
            return False, f"Error submitting request: {str(e)}"

    def approve_service_request(self, request_id: str, approved_by: str) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Approve a service request and generate work orders.

        Args:
            request_id: Service request ID
            approved_by: Name/ID of approver

        Returns:
            Tuple of (success, message, list_of_work_order_ids)
        """
        try:
            request_data = self.get_service_request(request_id)
            if not request_data:
                return False, f"Service request {request_id} not found", None

            # Update approval metadata
            request_data["workflow_metadata"]["status"] = "Approved"
            request_data["workflow_metadata"]["approved_by"] = approved_by
            request_data["workflow_metadata"]["approved_at"] = datetime.now().isoformat()
            request_data["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Generate work orders for each protocol
            work_order_ids = self._generate_work_orders(request_data)
            request_data["workflow_metadata"]["work_order_ids"] = work_order_ids

            # Add approval note
            if "notes" not in request_data["workflow_metadata"]:
                request_data["workflow_metadata"]["notes"] = []

            request_data["workflow_metadata"]["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "user": approved_by,
                "note": f"Service request approved. {len(work_order_ids)} work order(s) generated."
            })

            # Save updated request
            self._save_request(request_data)

            logger.info(f"Service request {request_id} approved by {approved_by}")
            return True, f"Service request approved. Generated {len(work_order_ids)} work orders.", work_order_ids

        except Exception as e:
            logger.error(f"Failed to approve service request {request_id}: {str(e)}")
            return False, f"Error approving request: {str(e)}", None

    def reject_service_request(self, request_id: str, rejected_by: str, reason: str) -> Tuple[bool, str]:
        """
        Reject a service request.

        Args:
            request_id: Service request ID
            rejected_by: Name/ID of person rejecting
            reason: Rejection reason

        Returns:
            Tuple of (success, message)
        """
        try:
            request_data = self.get_service_request(request_id)
            if not request_data:
                return False, f"Service request {request_id} not found"

            # Update status
            request_data["workflow_metadata"]["status"] = "Rejected"
            request_data["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Add rejection note
            if "notes" not in request_data["workflow_metadata"]:
                request_data["workflow_metadata"]["notes"] = []

            request_data["workflow_metadata"]["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "user": rejected_by,
                "note": f"Service request rejected. Reason: {reason}"
            })

            # Save updated request
            self._save_request(request_data)

            logger.info(f"Service request {request_id} rejected by {rejected_by}")
            return True, f"Service request {request_id} rejected"

        except Exception as e:
            logger.error(f"Failed to reject service request {request_id}: {str(e)}")
            return False, f"Error rejecting request: {str(e)}"

    def _generate_work_orders(self, request_data: Dict[str, Any]) -> List[str]:
        """
        Generate work orders from approved service request.

        Args:
            request_data: Service request data

        Returns:
            List of generated work order IDs
        """
        work_order_ids = []

        # Create one work order per protocol requested
        for protocol in request_data.get("protocols_requested", []):
            work_order_id = self._generate_work_order_id()

            work_order = {
                "work_order_id": work_order_id,
                "service_request_id": request_data["request_id"],
                "protocol_id": protocol["protocol_id"],
                "protocol_name": protocol["protocol_name"],
                "status": "Created",
                "created_at": datetime.now().isoformat(),
                "priority": request_data.get("priority", "Normal"),
                "sample_details": request_data.get("sample_details"),
                "special_requirements": request_data.get("special_requirements"),
                "requested_by": request_data.get("requested_by"),
                "project_customer": request_data.get("project_customer")
            }

            # Save work order
            work_orders_dir = Path("data/work_orders")
            work_orders_dir.mkdir(parents=True, exist_ok=True)

            work_order_file = work_orders_dir / f"{work_order_id}.json"
            with open(work_order_file, 'w') as f:
                json.dump(work_order, f, indent=2)

            work_order_ids.append(work_order_id)
            logger.info(f"Work order {work_order_id} created for protocol {protocol['protocol_id']}")

        return work_order_ids

    def _generate_work_order_id(self) -> str:
        """Generate unique work order ID."""
        timestamp = datetime.now().strftime("%Y%H%M%S")
        return f"WO-{timestamp}"

    def get_service_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve service request by ID.

        Args:
            request_id: Service request ID

        Returns:
            Service request data or None if not found
        """
        # Check cache first
        if request_id in self.requests_cache:
            return self.requests_cache[request_id]

        # Try loading from disk
        request_file = self.data_dir / f"{request_id}.json"
        if request_file.exists():
            with open(request_file, 'r') as f:
                request_data = json.load(f)
                self.requests_cache[request_id] = request_data
                return request_data

        return None

    def update_service_request(self, request_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update an existing service request.

        Args:
            request_id: Service request ID
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success, message)
        """
        try:
            request_data = self.get_service_request(request_id)
            if not request_data:
                return False, f"Service request {request_id} not found"

            # Apply updates
            request_data.update(updates)
            request_data["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Validate updated data
            is_valid, error_msg = self.validator.validate(request_data)
            if not is_valid:
                return False, f"Update validation failed: {error_msg}"

            # Save updated request
            self._save_request(request_data)

            logger.info(f"Service request {request_id} updated successfully")
            return True, f"Service request {request_id} updated successfully"

        except Exception as e:
            logger.error(f"Failed to update service request {request_id}: {str(e)}")
            return False, f"Error updating request: {str(e)}"

    def list_service_requests(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all service requests, optionally filtered by status.

        Args:
            status_filter: Optional status to filter by

        Returns:
            List of service request summaries
        """
        requests = []

        for request_id, request_data in self.requests_cache.items():
            status = request_data.get("workflow_metadata", {}).get("status")

            if status_filter and status != status_filter:
                continue

            requests.append({
                "request_id": request_id,
                "request_date": request_data.get("request_date"),
                "requested_by": request_data.get("requested_by", {}).get("name"),
                "project_customer": request_data.get("project_customer", {}).get("name"),
                "protocols_count": len(request_data.get("protocols_requested", [])),
                "priority": request_data.get("priority"),
                "status": status
            })

        return sorted(requests, key=lambda x: x["request_date"], reverse=True)

    def _save_request(self, request_data: Dict[str, Any]):
        """Save service request to disk and update cache."""
        request_id = request_data["request_id"]
        request_file = self.data_dir / f"{request_id}.json"

        with open(request_file, 'w') as f:
            json.dump(request_data, f, indent=2)

        self.requests_cache[request_id] = request_data

    def add_note(self, request_id: str, note: str, user: str) -> Tuple[bool, str]:
        """
        Add a note to a service request.

        Args:
            request_id: Service request ID
            note: Note text
            user: User adding the note

        Returns:
            Tuple of (success, message)
        """
        try:
            request_data = self.get_service_request(request_id)
            if not request_data:
                return False, f"Service request {request_id} not found"

            if "workflow_metadata" not in request_data:
                request_data["workflow_metadata"] = {}

            if "notes" not in request_data["workflow_metadata"]:
                request_data["workflow_metadata"]["notes"] = []

            request_data["workflow_metadata"]["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "user": user,
                "note": note
            })

            request_data["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            self._save_request(request_data)

            return True, "Note added successfully"

        except Exception as e:
            logger.error(f"Failed to add note to request {request_id}: {str(e)}")
            return False, f"Error adding note: {str(e)}"
