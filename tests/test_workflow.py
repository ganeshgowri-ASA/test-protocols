"""
Unit tests for workflow orchestration components.
"""

import pytest
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from workflow.orchestrator import WorkflowOrchestrator, WorkflowStage, WorkflowStatus
from handlers.service_request_handler import ServiceRequestHandler
from utils.validators import ServiceRequestValidator


class TestServiceRequestHandler:
    """Tests for Service Request Handler"""

    def setup_method(self):
        """Setup test fixtures"""
        self.handler = ServiceRequestHandler(data_dir="data/test/service_requests")
        self.validator = ServiceRequestValidator()

    def test_create_service_request(self):
        """Test service request creation"""
        request_data = {
            "requested_by": {
                "name": "Test User",
                "email": "test@example.com",
                "department": "R&D"
            },
            "project_customer": {
                "type": "Internal Project",
                "name": "Test Project"
            },
            "sample_details": {
                "sample_type": "PV Module",
                "quantity": 1
            },
            "protocols_requested": [
                {
                    "protocol_id": "IEC-61215-1",
                    "protocol_name": "Test Protocol"
                }
            ],
            "priority": "Normal"
        }

        success, message, request = self.handler.create_service_request(request_data)

        assert success is True
        assert request is not None
        assert "request_id" in request
        assert request["request_id"].startswith("SR-")

    def test_request_id_generation(self):
        """Test request ID generation"""
        request_id = self.validator.generate_request_id()

        assert request_id.startswith("SR-")
        assert self.validator.validate_request_id(request_id)

    def test_workflow_metadata_addition(self):
        """Test workflow metadata addition"""
        data = {"test": "data"}
        updated_data = self.validator.add_workflow_metadata(data)

        assert "workflow_metadata" in updated_data
        assert "status" in updated_data["workflow_metadata"]
        assert updated_data["workflow_metadata"]["status"] == "Draft"


class TestWorkflowOrchestrator:
    """Tests for Workflow Orchestrator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.orchestrator = WorkflowOrchestrator(base_data_dir="data/test")

    def test_workflow_initiation(self):
        """Test workflow initiation"""
        service_request_data = {
            "request_id": "SR-2025-TEST01",
            "priority": "Normal",
            "protocols_requested": [
                {"protocol_id": "IEC-61215-1"}
            ],
            "requested_by": {"name": "Test User"}
        }

        workflow = self.orchestrator.initiate_workflow(service_request_data)

        assert workflow is not None
        assert "workflow_id" in workflow
        assert workflow["status"] == WorkflowStatus.INITIATED.value
        assert workflow["current_stage"] == WorkflowStage.SERVICE_REQUEST.value

    def test_workflow_id_generation(self):
        """Test workflow ID generation"""
        workflow_id = self.orchestrator._generate_workflow_id()

        assert workflow_id.startswith("WF-")
        assert len(workflow_id) > 5

    def test_progress_calculation(self):
        """Test workflow progress calculation"""
        workflow = {
            "workflow_id": "WF-TEST",
            "current_stage": WorkflowStage.EQUIPMENT_PLANNING.value
        }

        progress = self.orchestrator._calculate_progress(workflow)

        assert progress == 30  # Equipment planning is 30% progress


class TestValidators:
    """Tests for validation utilities"""

    def test_email_validation(self):
        """Test email validation"""
        from utils.validators import validate_email

        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False

    def test_date_format_validation(self):
        """Test date format validation"""
        from utils.validators import validate_date_format

        valid_date = datetime.now().isoformat()
        assert validate_date_format(valid_date) is True
        assert validate_date_format("invalid-date") is False


# Run tests with: pytest tests/test_workflow.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
