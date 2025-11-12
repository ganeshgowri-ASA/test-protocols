"""
Base Protocol Handler
Abstract base class for all protocol handlers with common functionality
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import json
import logging


class ProtocolState(Enum):
    """Protocol execution states"""
    INITIALIZED = "initialized"
    SETUP = "setup"
    PRE_TEST_REVIEW = "pre_test_review"
    EQUIPMENT_CHECK = "equipment_check"
    RUNNING = "running"
    PAUSED = "paused"
    EMERGENCY_STOP = "emergency_stop"
    POST_TEST_REVIEW = "post_test_review"
    DATA_REVIEW = "data_review"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestResult(Enum):
    """Test result outcomes"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional-pass"
    NOT_TESTED = "not-tested"
    IN_PROGRESS = "in-progress"


class BaseProtocolHandler(ABC):
    """
    Base handler for all PV testing protocols
    Implements common functionality for protocol execution, validation, and reporting
    """

    def __init__(self, protocol_def: Dict[str, Any], config: Optional[Dict] = None):
        """
        Initialize protocol handler

        Args:
            protocol_def: Protocol definition dictionary (from JSON)
            config: Optional configuration overrides
        """
        self.protocol_def = protocol_def
        self.config = config or {}
        self.state = ProtocolState.INITIALIZED
        self.result = TestResult.NOT_TESTED

        # Data storage
        self.test_data: Dict[str, Any] = {}
        self.time_series_data: List[Dict] = []
        self.measurements: Dict[str, Any] = {}
        self.images: List[Dict] = []
        self.approvals: List[Dict] = []

        # Audit trail
        self.audit_log: List[Dict] = []
        self.state_history: List[Dict] = []

        # Metadata
        self.session_id = self._generate_session_id()
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.operator: Optional[str] = None

        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{protocol_def.get('protocolId', 'UNKNOWN')}")

        self._log_audit("INITIALIZED", f"Protocol {self.protocol_id} handler initialized")

    @property
    def protocol_id(self) -> str:
        """Get protocol ID"""
        return self.protocol_def.get("protocolId", "UNKNOWN")

    @property
    def protocol_name(self) -> str:
        """Get protocol name"""
        return self.protocol_def.get("protocolName", "Unknown Protocol")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        from uuid import uuid4
        return f"{self.protocol_def.get('protocolId', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid4())[:8]}"

    def _log_audit(self, event_type: str, description: str, data: Optional[Dict] = None):
        """
        Log audit trail entry

        Args:
            event_type: Type of event (e.g., 'STATE_CHANGE', 'MEASUREMENT', 'APPROVAL')
            description: Human-readable description
            data: Optional additional data
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sessionId": self.session_id,
            "eventType": event_type,
            "description": description,
            "operator": self.operator,
            "state": self.state.value,
            "data": data or {}
        }
        self.audit_log.append(entry)
        self.logger.info(f"[AUDIT] {event_type}: {description}")

    def _change_state(self, new_state: ProtocolState, reason: str = ""):
        """
        Change protocol state with audit logging

        Args:
            new_state: New state to transition to
            reason: Reason for state change
        """
        old_state = self.state
        self.state = new_state

        state_change = {
            "timestamp": datetime.now().isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason
        }
        self.state_history.append(state_change)

        self._log_audit("STATE_CHANGE", f"State changed from {old_state.value} to {new_state.value}: {reason}")

    @abstractmethod
    def validate_prerequisites(self) -> Tuple[bool, List[str]]:
        """
        Validate all prerequisites before test execution

        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        pass

    @abstractmethod
    def setup(self) -> bool:
        """
        Perform test setup

        Returns:
            True if setup successful
        """
        pass

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the main test protocol

        Returns:
            True if test executed successfully (not necessarily passed)
        """
        pass

    @abstractmethod
    def analyze_results(self) -> TestResult:
        """
        Analyze test results and determine pass/fail

        Returns:
            Test result enum
        """
        pass

    @abstractmethod
    def generate_report(self, formats: Optional[List[str]] = None) -> Dict[str, bytes]:
        """
        Generate test reports in requested formats

        Args:
            formats: List of formats ('pdf', 'excel', 'json', 'html')

        Returns:
            Dictionary mapping format to report bytes
        """
        pass

    def check_safety_interlocks(self) -> Tuple[bool, List[Dict]]:
        """
        Check all safety interlocks for current state

        Returns:
            Tuple of (all_passed, list of triggered interlocks)
        """
        interlocks = self.protocol_def.get("safetyInterlocks", [])
        triggered = []

        for interlock in interlocks:
            # Filter by interlock type based on current state
            interlock_type = interlock.get("type")

            if not self._should_check_interlock(interlock_type):
                continue

            # Evaluate interlock condition (simplified - would need expression evaluator)
            passed = self._evaluate_interlock_condition(interlock)

            if not passed:
                triggered.append(interlock)
                self._log_audit(
                    "INTERLOCK_TRIGGERED",
                    f"Safety interlock {interlock.get('interlockId')} triggered: {interlock.get('message')}",
                    interlock
                )

        all_passed = len(triggered) == 0
        return all_passed, triggered

    def _should_check_interlock(self, interlock_type: str) -> bool:
        """Determine if interlock should be checked based on current state"""
        state_interlock_map = {
            ProtocolState.SETUP: ["pre-test"],
            ProtocolState.PRE_TEST_REVIEW: ["pre-test"],
            ProtocolState.EQUIPMENT_CHECK: ["pre-test", "equipment-ready"],
            ProtocolState.RUNNING: ["during-test", "emergency-stop"],
            ProtocolState.POST_TEST_REVIEW: ["post-test"]
        }

        return interlock_type in state_interlock_map.get(self.state, [])

    def _evaluate_interlock_condition(self, interlock: Dict) -> bool:
        """
        Evaluate interlock condition
        Would need proper expression evaluator in production
        """
        # Simplified evaluation - in production would use safe eval or rules engine
        condition = interlock.get("condition", "true")

        # For now, return True (passed) as placeholder
        # Production implementation would evaluate against current test data
        return True

    def check_approval_gates(self, stage: str) -> Tuple[bool, List[Dict]]:
        """
        Check if required approvals are present for given stage

        Args:
            stage: Approval stage (e.g., 'pre-test-review', 'final-approval')

        Returns:
            Tuple of (all_approved, list of pending approvals)
        """
        approval_gates = self.protocol_def.get("approvalGates", [])
        pending = []

        for gate in approval_gates:
            if gate.get("stage") == stage and gate.get("required", True):
                # Check if approval exists
                approval_found = any(
                    a.get("gateId") == gate.get("gateId") and a.get("approved", False)
                    for a in self.approvals
                )

                if not approval_found:
                    pending.append(gate)

        all_approved = len(pending) == 0
        return all_approved, pending

    def add_approval(self, gate_id: str, approver: str, approved: bool,
                    comments: str = "", criteria_checklist: Optional[Dict] = None):
        """
        Add approval for specific gate

        Args:
            gate_id: Gate identifier
            approver: Person providing approval
            approved: Whether approved or rejected
            comments: Optional comments
            criteria_checklist: Optional checklist of criteria
        """
        approval = {
            "gateId": gate_id,
            "approver": approver,
            "approved": approved,
            "timestamp": datetime.now().isoformat(),
            "comments": comments,
            "criteriaChecklist": criteria_checklist or {}
        }

        self.approvals.append(approval)

        self._log_audit(
            "APPROVAL",
            f"Gate {gate_id} {'approved' if approved else 'rejected'} by {approver}",
            approval
        )

    def record_measurement(self, name: str, value: Any, unit: str = "",
                          timestamp: Optional[datetime] = None, metadata: Optional[Dict] = None):
        """
        Record a measurement

        Args:
            name: Measurement name
            value: Measurement value
            unit: Unit of measurement
            timestamp: Optional timestamp (defaults to now)
            metadata: Optional additional metadata
        """
        measurement = {
            "name": name,
            "value": value,
            "unit": unit,
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "metadata": metadata or {}
        }

        self.measurements[name] = measurement

        self._log_audit("MEASUREMENT", f"Recorded {name} = {value} {unit}", measurement)

    def add_time_series_point(self, parameters: Dict[str, float]):
        """
        Add time series data point

        Args:
            parameters: Dictionary of parameter names to values
        """
        point = {
            "timestamp": datetime.now().isoformat(),
            "data": parameters
        }
        self.time_series_data.append(point)

    def capture_image(self, stage: str, image_data: bytes, filename: str,
                     metadata: Optional[Dict] = None):
        """
        Capture image at specific test stage

        Args:
            stage: Test stage (e.g., 'pre-test', 'during-test')
            image_data: Image data bytes
            filename: Image filename
            metadata: Optional metadata (resolution, camera, etc.)
        """
        image_record = {
            "stage": stage,
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "size": len(image_data),
            "metadata": metadata or {}
        }

        self.images.append(image_record)

        # In production, would save image_data to storage
        # For now, just record metadata

        self._log_audit("IMAGE_CAPTURE", f"Captured image at {stage}: {filename}", image_record)

    def get_test_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive test summary

        Returns:
            Dictionary containing test summary
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            "sessionId": self.session_id,
            "protocolId": self.protocol_id,
            "protocolName": self.protocol_name,
            "state": self.state.value,
            "result": self.result.value,
            "operator": self.operator,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "deviceUnderTest": self.protocol_def.get("deviceUnderTest", {}),
            "measurements": self.measurements,
            "approvals": self.approvals,
            "imageCount": len(self.images),
            "timeSeriesPoints": len(self.time_series_data),
            "auditTrailEntries": len(self.audit_log)
        }

    def save_session(self, filepath: str):
        """
        Save complete session data to file

        Args:
            filepath: Path to save session data
        """
        session_data = {
            "summary": self.get_test_summary(),
            "protocolDefinition": self.protocol_def,
            "testData": self.test_data,
            "measurements": self.measurements,
            "timeSeriesData": self.time_series_data,
            "images": self.images,
            "approvals": self.approvals,
            "auditLog": self.audit_log,
            "stateHistory": self.state_history
        }

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

        self._log_audit("SESSION_SAVED", f"Session data saved to {filepath}")

    def load_session(self, filepath: str):
        """
        Load session data from file

        Args:
            filepath: Path to load session data from
        """
        with open(filepath, 'r') as f:
            session_data = json.load(f)

        self.test_data = session_data.get("testData", {})
        self.measurements = session_data.get("measurements", {})
        self.time_series_data = session_data.get("timeSeriesData", [])
        self.images = session_data.get("images", [])
        self.approvals = session_data.get("approvals", [])
        self.audit_log = session_data.get("auditLog", [])
        self.state_history = session_data.get("stateHistory", [])

        # Restore state from summary
        summary = session_data.get("summary", {})
        self.session_id = summary.get("sessionId", self.session_id)
        self.operator = summary.get("operator")

        self._log_audit("SESSION_LOADED", f"Session data loaded from {filepath}")
