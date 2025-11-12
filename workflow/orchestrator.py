"""
Master Workflow Orchestrator - Core coordination engine for the PV Testing Protocol Framework.

This module coordinates all stages of the workflow:
1. Service Request submission and approval
2. Incoming Inspection execution and acceptance
3. Equipment Planning and allocation
4. Protocol Dispatching and execution
5. Report Aggregation and delivery

Complete data traceability from request to final report.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow stages enumeration."""
    SERVICE_REQUEST = "service_request"
    INCOMING_INSPECTION = "incoming_inspection"
    EQUIPMENT_PLANNING = "equipment_planning"
    PROTOCOL_EXECUTION = "protocol_execution"
    ANALYSIS = "analysis"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowOrchestrator:
    """
    Master orchestrator for coordinating all workflow stages.

    This class manages the complete workflow lifecycle, ensuring proper
    sequencing, data flow, and traceability across all stages.
    """

    def __init__(self, base_data_dir: str = "data"):
        """
        Initialize the workflow orchestrator.

        Args:
            base_data_dir: Base directory for data storage
        """
        self.base_data_dir = Path(base_data_dir)
        self._ensure_directories()

        # Initialize stage handlers (will be set via dependency injection)
        self.service_request_handler = None
        self.incoming_inspection_handler = None
        self.equipment_planning_handler = None
        self.protocol_dispatcher = None
        self.report_aggregator = None

        # Workflow state tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            "service_requests",
            "inspections",
            "equipment",
            "protocols",
            "reports",
            "workflows"
        ]
        for dir_name in directories:
            (self.base_data_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def register_handlers(self,
                         service_request_handler,
                         incoming_inspection_handler,
                         equipment_planning_handler,
                         protocol_dispatcher,
                         report_aggregator):
        """
        Register stage handlers with the orchestrator.

        Args:
            service_request_handler: Handler for service requests
            incoming_inspection_handler: Handler for inspections
            equipment_planning_handler: Handler for equipment planning
            protocol_dispatcher: Protocol routing and execution
            report_aggregator: Report consolidation
        """
        self.service_request_handler = service_request_handler
        self.incoming_inspection_handler = incoming_inspection_handler
        self.equipment_planning_handler = equipment_planning_handler
        self.protocol_dispatcher = protocol_dispatcher
        self.report_aggregator = report_aggregator

        logger.info("All workflow stage handlers registered successfully")

    def initiate_workflow(self, service_request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a new workflow from a service request.

        Args:
            service_request_data: Service request data dictionary

        Returns:
            Workflow tracking dictionary
        """
        try:
            # Generate workflow ID
            workflow_id = self._generate_workflow_id()

            # Create workflow tracking object
            workflow = {
                "workflow_id": workflow_id,
                "status": WorkflowStatus.INITIATED.value,
                "current_stage": WorkflowStage.SERVICE_REQUEST.value,
                "service_request_id": service_request_data.get("request_id"),
                "initiated_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "stage_history": [
                    {
                        "stage": WorkflowStage.SERVICE_REQUEST.value,
                        "status": "initiated",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "data_links": {
                    "service_request_id": service_request_data.get("request_id"),
                    "inspection_id": None,
                    "planning_id": None,
                    "protocol_execution_ids": [],
                    "report_ids": []
                },
                "metadata": {
                    "priority": service_request_data.get("priority", "Normal"),
                    "protocols_requested": [
                        p["protocol_id"] for p in service_request_data.get("protocols_requested", [])
                    ],
                    "requested_by": service_request_data.get("requested_by", {}).get("name")
                }
            }

            # Store workflow
            self.active_workflows[workflow_id] = workflow
            self._save_workflow(workflow)

            logger.info(f"Workflow {workflow_id} initiated for service request {service_request_data.get('request_id')}")

            return workflow

        except Exception as e:
            logger.error(f"Failed to initiate workflow: {str(e)}")
            raise

    def advance_workflow(self, workflow_id: str, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advance workflow to next stage based on current stage completion.

        Args:
            workflow_id: Workflow identifier
            stage_data: Data from completed stage

        Returns:
            Updated workflow object
        """
        try:
            workflow = self.get_workflow(workflow_id)
            current_stage = WorkflowStage(workflow["current_stage"])

            # Determine next stage and process accordingly
            if current_stage == WorkflowStage.SERVICE_REQUEST:
                return self._advance_to_inspection(workflow, stage_data)

            elif current_stage == WorkflowStage.INCOMING_INSPECTION:
                return self._advance_to_equipment_planning(workflow, stage_data)

            elif current_stage == WorkflowStage.EQUIPMENT_PLANNING:
                return self._advance_to_protocol_execution(workflow, stage_data)

            elif current_stage == WorkflowStage.PROTOCOL_EXECUTION:
                return self._advance_to_analysis(workflow, stage_data)

            elif current_stage == WorkflowStage.ANALYSIS:
                return self._advance_to_report_generation(workflow, stage_data)

            elif current_stage == WorkflowStage.REPORT_GENERATION:
                return self._complete_workflow(workflow, stage_data)

            else:
                raise ValueError(f"Unknown workflow stage: {current_stage}")

        except Exception as e:
            logger.error(f"Failed to advance workflow {workflow_id}: {str(e)}")
            raise

    def _advance_to_inspection(self, workflow: Dict[str, Any],
                               service_request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow from service request to incoming inspection."""
        # Update workflow
        workflow["current_stage"] = WorkflowStage.INCOMING_INSPECTION.value
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()

        # Add stage history
        workflow["stage_history"].append({
            "stage": WorkflowStage.INCOMING_INSPECTION.value,
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        })

        # Save and return
        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} advanced to INCOMING_INSPECTION")
        return workflow

    def _advance_to_equipment_planning(self, workflow: Dict[str, Any],
                                       inspection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow from inspection to equipment planning."""
        # Check if inspection passed
        acceptance = inspection_data.get("acceptance_decision", {})
        if acceptance.get("decision") not in ["Accept", "Accept with Conditions"]:
            workflow["status"] = WorkflowStatus.ON_HOLD.value
            workflow["updated_at"] = datetime.now().isoformat()
            workflow["stage_history"].append({
                "stage": WorkflowStage.INCOMING_INSPECTION.value,
                "status": "failed",
                "reason": acceptance.get("reject_reason") or acceptance.get("hold_reason"),
                "timestamp": datetime.now().isoformat()
            })
            self._save_workflow(workflow)
            logger.warning(f"Workflow {workflow['workflow_id']} put on hold - inspection not accepted")
            return workflow

        # Update workflow
        workflow["current_stage"] = WorkflowStage.EQUIPMENT_PLANNING.value
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["data_links"]["inspection_id"] = inspection_data.get("inspection_id")

        # Add stage history
        workflow["stage_history"].append({
            "stage": WorkflowStage.EQUIPMENT_PLANNING.value,
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        })

        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} advanced to EQUIPMENT_PLANNING")
        return workflow

    def _advance_to_protocol_execution(self, workflow: Dict[str, Any],
                                       planning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow from equipment planning to protocol execution."""
        workflow["current_stage"] = WorkflowStage.PROTOCOL_EXECUTION.value
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["data_links"]["planning_id"] = planning_data.get("planning_id")

        workflow["stage_history"].append({
            "stage": WorkflowStage.PROTOCOL_EXECUTION.value,
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        })

        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} advanced to PROTOCOL_EXECUTION")
        return workflow

    def _advance_to_analysis(self, workflow: Dict[str, Any],
                            execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow from protocol execution to analysis."""
        workflow["current_stage"] = WorkflowStage.ANALYSIS.value
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()

        # Track protocol execution IDs
        protocol_exec_ids = workflow["data_links"].get("protocol_execution_ids", [])
        if execution_data.get("execution_id"):
            protocol_exec_ids.append(execution_data["execution_id"])
        workflow["data_links"]["protocol_execution_ids"] = protocol_exec_ids

        workflow["stage_history"].append({
            "stage": WorkflowStage.ANALYSIS.value,
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        })

        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} advanced to ANALYSIS")
        return workflow

    def _advance_to_report_generation(self, workflow: Dict[str, Any],
                                      analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow from analysis to report generation."""
        workflow["current_stage"] = WorkflowStage.REPORT_GENERATION.value
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()

        workflow["stage_history"].append({
            "stage": WorkflowStage.REPORT_GENERATION.value,
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        })

        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} advanced to REPORT_GENERATION")
        return workflow

    def _complete_workflow(self, workflow: Dict[str, Any],
                          report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete workflow after report generation."""
        workflow["current_stage"] = WorkflowStage.COMPLETED.value
        workflow["status"] = WorkflowStatus.COMPLETED.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["completed_at"] = datetime.now().isoformat()

        # Track report IDs
        if report_data.get("report_id"):
            workflow["data_links"]["report_ids"].append(report_data["report_id"])

        workflow["stage_history"].append({
            "stage": WorkflowStage.COMPLETED.value,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })

        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow['workflow_id']} COMPLETED successfully")
        return workflow

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Retrieve workflow by ID.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow dictionary
        """
        # Try memory cache first
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]

        # Try loading from disk
        workflow_path = self.base_data_dir / "workflows" / f"{workflow_id}.json"
        if workflow_path.exists():
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
                self.active_workflows[workflow_id] = workflow
                return workflow

        raise ValueError(f"Workflow {workflow_id} not found")

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get current status of workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Status dictionary with current stage, status, and progress
        """
        workflow = self.get_workflow(workflow_id)

        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "current_stage": workflow["current_stage"],
            "initiated_at": workflow["initiated_at"],
            "updated_at": workflow["updated_at"],
            "progress_percentage": self._calculate_progress(workflow),
            "data_links": workflow["data_links"],
            "stage_history": workflow["stage_history"]
        }

    def _calculate_progress(self, workflow: Dict[str, Any]) -> float:
        """Calculate workflow progress percentage."""
        stage_weights = {
            WorkflowStage.SERVICE_REQUEST.value: 10,
            WorkflowStage.INCOMING_INSPECTION.value: 20,
            WorkflowStage.EQUIPMENT_PLANNING.value: 30,
            WorkflowStage.PROTOCOL_EXECUTION.value: 50,
            WorkflowStage.ANALYSIS.value: 70,
            WorkflowStage.REPORT_GENERATION.value: 90,
            WorkflowStage.COMPLETED.value: 100
        }

        current_stage = workflow.get("current_stage")
        return stage_weights.get(current_stage, 0)

    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"WF-{timestamp}"

    def _save_workflow(self, workflow: Dict[str, Any]):
        """Save workflow to disk."""
        workflow_path = self.base_data_dir / "workflows" / f"{workflow['workflow_id']}.json"
        with open(workflow_path, 'w') as f:
            json.dump(workflow, f, indent=2)

    def list_active_workflows(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all active workflows, optionally filtered by status.

        Args:
            status_filter: Optional status to filter by

        Returns:
            List of workflow summaries
        """
        workflows = []
        workflow_dir = self.base_data_dir / "workflows"

        for workflow_file in workflow_dir.glob("*.json"):
            with open(workflow_file, 'r') as f:
                workflow = json.load(f)

                if status_filter and workflow["status"] != status_filter:
                    continue

                workflows.append({
                    "workflow_id": workflow["workflow_id"],
                    "status": workflow["status"],
                    "current_stage": workflow["current_stage"],
                    "service_request_id": workflow["data_links"]["service_request_id"],
                    "initiated_at": workflow["initiated_at"],
                    "priority": workflow["metadata"].get("priority")
                })

        return sorted(workflows, key=lambda x: x["initiated_at"], reverse=True)

    def hold_workflow(self, workflow_id: str, reason: str):
        """Put workflow on hold."""
        workflow = self.get_workflow(workflow_id)
        workflow["status"] = WorkflowStatus.ON_HOLD.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["hold_reason"] = reason
        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow_id} put on hold: {reason}")

    def resume_workflow(self, workflow_id: str):
        """Resume a held workflow."""
        workflow = self.get_workflow(workflow_id)
        workflow["status"] = WorkflowStatus.IN_PROGRESS.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow.pop("hold_reason", None)
        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow_id} resumed")

    def cancel_workflow(self, workflow_id: str, reason: str):
        """Cancel a workflow."""
        workflow = self.get_workflow(workflow_id)
        workflow["status"] = WorkflowStatus.CANCELLED.value
        workflow["updated_at"] = datetime.now().isoformat()
        workflow["cancelled_at"] = datetime.now().isoformat()
        workflow["cancellation_reason"] = reason
        self._save_workflow(workflow)
        logger.info(f"Workflow {workflow_id} cancelled: {reason}")
