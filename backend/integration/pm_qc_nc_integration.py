"""
PM/QC/NC Integration Framework
Integrates with Project Management, Quality Control, and Non-Conformance systems
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging


class NCCategory(Enum):
    """Non-conformance categories"""
    TEST_FAILURE = "test-failure"
    EQUIPMENT_ISSUE = "equipment-issue"
    PROCEDURE_DEVIATION = "procedure-deviation"
    DOCUMENTATION_ERROR = "documentation-error"
    SAFETY_VIOLATION = "safety-violation"
    CALIBRATION_EXPIRED = "calibration-expired"


class NCSeverity(Enum):
    """Non-conformance severity"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class NCStatus(Enum):
    """Non-conformance status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CORRECTIVE_ACTION = "corrective-action"
    VERIFICATION = "verification"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class NonConformanceReport:
    """
    Non-conformance report
    """

    def __init__(self, nc_id: str, category: NCCategory, severity: NCSeverity):
        self.nc_id = nc_id
        self.category = category
        self.severity = severity
        self.status = NCStatus.OPEN

        self.created_time = datetime.now()
        self.created_by: Optional[str] = None
        self.assigned_to: Optional[str] = None

        self.description: str = ""
        self.root_cause: str = ""
        self.corrective_action: str = ""
        self.preventive_action: str = ""

        self.related_protocol: Optional[str] = None
        self.related_session: Optional[str] = None
        self.related_device: Optional[str] = None

        self.resolution_time: Optional[datetime] = None
        self.verified_by: Optional[str] = None

        self.logger = logging.getLogger(f"{__name__}.{nc_id}")

    def update_status(self, new_status: NCStatus, updated_by: str, notes: str = ""):
        """Update NC status"""
        old_status = self.status
        self.status = new_status

        self.logger.info(f"NC {self.nc_id} status changed from {old_status.value} to {new_status.value} by {updated_by}")

        if new_status == NCStatus.CLOSED:
            self.resolution_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ncId": self.nc_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "createdTime": self.created_time.isoformat(),
            "createdBy": self.created_by,
            "assignedTo": self.assigned_to,
            "description": self.description,
            "rootCause": self.root_cause,
            "correctiveAction": self.corrective_action,
            "preventiveAction": self.preventive_action,
            "relatedProtocol": self.related_protocol,
            "relatedSession": self.related_session,
            "relatedDevice": self.related_device,
            "resolutionTime": self.resolution_time.isoformat() if self.resolution_time else None,
            "verifiedBy": self.verified_by
        }


class NCManager:
    """
    Non-conformance management system
    """

    def __init__(self):
        self.ncs: Dict[str, NonConformanceReport] = {}
        self.logger = logging.getLogger(__name__)

    def create_nc(self, category: NCCategory, severity: NCSeverity,
                  description: str, created_by: str,
                  protocol_id: Optional[str] = None,
                  session_id: Optional[str] = None) -> NonConformanceReport:
        """
        Create new non-conformance report

        Args:
            category: NC category
            severity: NC severity
            description: Description of non-conformance
            created_by: Person creating NC
            protocol_id: Related protocol ID
            session_id: Related session ID

        Returns:
            NonConformanceReport object
        """
        nc_id = self._generate_nc_id()

        nc = NonConformanceReport(nc_id, category, severity)
        nc.description = description
        nc.created_by = created_by
        nc.related_protocol = protocol_id
        nc.related_session = session_id

        self.ncs[nc_id] = nc

        self.logger.info(f"Created NC {nc_id}: {category.value} - {severity.value}")

        return nc

    def get_nc(self, nc_id: str) -> Optional[NonConformanceReport]:
        """Get NC by ID"""
        return self.ncs.get(nc_id)

    def get_open_ncs(self) -> List[NonConformanceReport]:
        """Get all open NCs"""
        return [nc for nc in self.ncs.values() if nc.status == NCStatus.OPEN]

    def get_ncs_for_protocol(self, protocol_id: str) -> List[NonConformanceReport]:
        """Get all NCs for a protocol"""
        return [nc for nc in self.ncs.values() if nc.related_protocol == protocol_id]

    def _generate_nc_id(self) -> str:
        """Generate unique NC ID"""
        from uuid import uuid4
        return f"NC-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"


class QCInspection:
    """
    Quality control inspection record
    """

    def __init__(self, inspection_id: str, inspector: str, stage: str):
        self.inspection_id = inspection_id
        self.inspector = inspector
        self.stage = stage
        self.timestamp = datetime.now()

        self.checklist: Dict[str, bool] = {}
        self.observations: List[str] = []
        self.defects: List[str] = []

        self.passed = False
        self.comments: str = ""

    def perform_inspection(self, checklist: Dict[str, bool], observations: List[str] = None):
        """Perform inspection with checklist"""
        self.checklist = checklist
        self.observations = observations or []

        # Check if all critical items passed
        self.passed = all(checklist.values())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "inspectionId": self.inspection_id,
            "inspector": self.inspector,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat(),
            "checklist": self.checklist,
            "observations": self.observations,
            "defects": self.defects,
            "passed": self.passed,
            "comments": self.comments
        }


class QCManager:
    """
    Quality control management system
    """

    def __init__(self):
        self.inspections: Dict[str, QCInspection] = {}
        self.logger = logging.getLogger(__name__)

    def create_inspection(self, inspector: str, stage: str,
                         protocol_id: Optional[str] = None,
                         session_id: Optional[str] = None) -> QCInspection:
        """Create new QC inspection"""
        inspection_id = self._generate_inspection_id()

        inspection = QCInspection(inspection_id, inspector, stage)

        self.inspections[inspection_id] = inspection

        self.logger.info(f"Created QC inspection {inspection_id} at stage {stage} by {inspector}")

        return inspection

    def get_inspection(self, inspection_id: str) -> Optional[QCInspection]:
        """Get inspection by ID"""
        return self.inspections.get(inspection_id)

    def _generate_inspection_id(self) -> str:
        """Generate unique inspection ID"""
        from uuid import uuid4
        return f"QCI-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"


class ProjectTask:
    """
    Project management task
    """

    def __init__(self, task_id: str, project_id: str, task_name: str):
        self.task_id = task_id
        self.project_id = project_id
        self.task_name = task_name

        self.status = "pending"
        self.progress = 0
        self.assigned_to: Optional[str] = None

        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.due_date: Optional[datetime] = None

        self.related_protocols: List[str] = []
        self.related_sessions: List[str] = []

    def update_progress(self, progress: int, updated_by: str):
        """Update task progress"""
        self.progress = min(100, max(0, progress))

        if self.progress == 100:
            self.status = "completed"
            self.end_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "taskId": self.task_id,
            "projectId": self.project_id,
            "taskName": self.task_name,
            "status": self.status,
            "progress": self.progress,
            "assignedTo": self.assigned_to,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "dueDate": self.due_date.isoformat() if self.due_date else None,
            "relatedProtocols": self.related_protocols,
            "relatedSessions": self.related_sessions
        }


class PMManager:
    """
    Project management system
    """

    def __init__(self):
        self.projects: Dict[str, Dict] = {}
        self.tasks: Dict[str, ProjectTask] = {}
        self.logger = logging.getLogger(__name__)

    def create_task(self, project_id: str, task_name: str,
                   assigned_to: Optional[str] = None) -> ProjectTask:
        """Create new project task"""
        task_id = self._generate_task_id()

        task = ProjectTask(task_id, project_id, task_name)
        task.assigned_to = assigned_to

        self.tasks[task_id] = task

        self.logger.info(f"Created task {task_id}: {task_name} in project {project_id}")

        return task

    def get_task(self, task_id: str) -> Optional[ProjectTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def link_task_to_session(self, task_id: str, session_id: str, protocol_id: str):
        """Link task to test session"""
        task = self.get_task(task_id)
        if task:
            task.related_sessions.append(session_id)
            task.related_protocols.append(protocol_id)

            self.logger.info(f"Linked task {task_id} to session {session_id}")

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        from uuid import uuid4
        return f"TASK-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"


class IntegratedWorkflow:
    """
    Integrated workflow manager combining PM, QC, and NC systems
    """

    def __init__(self):
        self.nc_manager = NCManager()
        self.qc_manager = QCManager()
        self.pm_manager = PMManager()

        self.logger = logging.getLogger(__name__)

    def handle_test_failure(self, session_data: Dict[str, Any],
                          failures: List[str], created_by: str) -> NonConformanceReport:
        """
        Handle test failure - create NC and update PM

        Args:
            session_data: Test session data
            failures: List of failure descriptions
            created_by: Person creating NC

        Returns:
            Created NonConformanceReport
        """
        protocol_id = session_data.get("summary", {}).get("protocolId")
        session_id = session_data.get("summary", {}).get("sessionId")

        # Create NC
        nc = self.nc_manager.create_nc(
            category=NCCategory.TEST_FAILURE,
            severity=NCSeverity.MAJOR,
            description=f"Test failures: {'; '.join(failures)}",
            created_by=created_by,
            protocol_id=protocol_id,
            session_id=session_id
        )

        # Update related PM task if exists
        # Would query PM system for related tasks

        self.logger.info(f"Created NC {nc.nc_id} for test failure in session {session_id}")

        return nc

    def request_qc_approval(self, session_data: Dict[str, Any],
                          stage: str, inspector: str) -> QCInspection:
        """Request QC approval for test stage"""
        protocol_id = session_data.get("summary", {}).get("protocolId")
        session_id = session_data.get("summary", {}).get("sessionId")

        inspection = self.qc_manager.create_inspection(
            inspector=inspector,
            stage=stage,
            protocol_id=protocol_id,
            session_id=session_id
        )

        self.logger.info(f"QC inspection requested for session {session_id}, stage {stage}")

        return inspection

    def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """Get complete workflow status for session"""
        return {
            "sessionId": session_id,
            "openNCs": len(self.nc_manager.get_open_ncs()),
            "timestamp": datetime.now().isoformat()
        }
