"""
Validation utilities for all schema types in the workflow orchestration system.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
import re


class SchemaValidator:
    """Base class for schema validation with common utilities."""

    def __init__(self, schema_path: str):
        """
        Initialize validator with schema file.

        Args:
            schema_path: Path to JSON schema file
        """
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load schema from {self.schema_path}: {str(e)}")

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data against schema.

        Args:
            data: Data dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validate(instance=data, schema=self.schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def validate_and_raise(self, data: Dict[str, Any]) -> None:
        """
        Validate data and raise exception if invalid.

        Args:
            data: Data dictionary to validate

        Raises:
            ValidationError: If validation fails
        """
        is_valid, error_msg = self.validate(data)
        if not is_valid:
            raise ValidationError(error_msg)


class ServiceRequestValidator(SchemaValidator):
    """Validator for Service Request forms."""

    def __init__(self):
        schema_path = Path(__file__).parent.parent / "schemas/service_request/service_request_schema.json"
        super().__init__(schema_path)

    def generate_request_id(self) -> str:
        """
        Generate unique service request ID in format SR-YYYY-NNNNNN.

        Returns:
            Generated request ID
        """
        year = datetime.now().year
        # In production, this would query database for last ID
        # For now, generate based on timestamp
        sequence = datetime.now().strftime("%H%M%S")
        return f"SR-{year}-{sequence}"

    def validate_request_id(self, request_id: str) -> bool:
        """Validate request ID format."""
        pattern = r"^SR-\d{4}-\d{6}$"
        return bool(re.match(pattern, request_id))

    def add_workflow_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add workflow metadata to service request.

        Args:
            data: Service request data

        Returns:
            Updated data with workflow metadata
        """
        if "workflow_metadata" not in data:
            data["workflow_metadata"] = {}

        metadata = data["workflow_metadata"]

        # Set default values if not present
        if "status" not in metadata:
            metadata["status"] = "Draft"

        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now().isoformat()

        metadata["updated_at"] = datetime.now().isoformat()

        return data


class IncomingInspectionValidator(SchemaValidator):
    """Validator for Incoming Inspection records."""

    def __init__(self):
        schema_path = Path(__file__).parent.parent / "schemas/incoming_inspection/incoming_inspection_schema.json"
        super().__init__(schema_path)

    def generate_inspection_id(self) -> str:
        """Generate unique inspection ID in format II-YYYY-NNNNNN."""
        year = datetime.now().year
        sequence = datetime.now().strftime("%H%M%S")
        return f"II-{year}-{sequence}"


class EquipmentPlanningValidator(SchemaValidator):
    """Validator for Equipment Planning records."""

    def __init__(self):
        schema_path = Path(__file__).parent.parent / "schemas/equipment_planning/equipment_planning_schema.json"
        super().__init__(schema_path)

    def generate_equipment_id(self) -> str:
        """Generate unique equipment ID in format EQ-YYYY-NNNNNN."""
        year = datetime.now().year
        sequence = datetime.now().strftime("%H%M%S")
        return f"EQ-{year}-{sequence}"


class ProtocolValidator(SchemaValidator):
    """Validator for Protocol execution records."""

    def __init__(self, protocol_schema_path: str):
        super().__init__(protocol_schema_path)

    def generate_protocol_execution_id(self, protocol_id: str) -> str:
        """
        Generate unique protocol execution ID.

        Args:
            protocol_id: Protocol identifier (e.g., IEC-61215-1)

        Returns:
            Execution ID in format PE-{PROTOCOL_ID}-YYYY-NNNNNN
        """
        year = datetime.now().year
        sequence = datetime.now().strftime("%H%M%S")
        # Clean protocol_id to remove special characters
        clean_id = re.sub(r'[^A-Z0-9]', '', protocol_id.upper())
        return f"PE-{clean_id}-{year}-{sequence}"

    def add_workflow_links(self, data: Dict[str, Any],
                          service_request_id: str,
                          inspection_id: str,
                          equipment_assigned: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add workflow linkage metadata to protocol data.

        Args:
            data: Protocol execution data
            service_request_id: Originating service request ID
            inspection_id: Related inspection ID
            equipment_assigned: Equipment allocation details

        Returns:
            Updated protocol data with workflow links
        """
        if "workflow_metadata" not in data:
            data["workflow_metadata"] = {}

        data["workflow_metadata"].update({
            "service_request_id": service_request_id,
            "inspection_id": inspection_id,
            "equipment_assigned": equipment_assigned,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })

        return data


class WorkOrderValidator:
    """Validator for work orders generated from service requests."""

    @staticmethod
    def generate_work_order_id() -> str:
        """Generate unique work order ID in format WO-YYYY-NNNNNN."""
        year = datetime.now().year
        sequence = datetime.now().strftime("%H%M%S")
        return f"WO-{year}-{sequence}"

    @staticmethod
    def validate_work_order_status(status: str) -> bool:
        """Validate work order status."""
        valid_statuses = [
            "Created",
            "Scheduled",
            "In Progress",
            "Testing",
            "Analysis",
            "Review",
            "Completed",
            "On Hold",
            "Cancelled"
        ]
        return status in valid_statuses


def validate_date_format(date_string: str) -> bool:
    """
    Validate ISO format date string.

    Args:
        date_string: Date string to validate

    Returns:
        True if valid ISO format
    """
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except:
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# Convenience functions for quick validation
def validate_service_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Quick validation of service request data."""
    validator = ServiceRequestValidator()
    return validator.validate(data)


def validate_incoming_inspection(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Quick validation of incoming inspection data."""
    validator = IncomingInspectionValidator()
    return validator.validate(data)


def validate_equipment_planning(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Quick validation of equipment planning data."""
    validator = EquipmentPlanningValidator()
    return validator.validate(data)
