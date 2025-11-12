"""
Safety Interlock Engine
Manages safety interlocks, approval gates, and state transitions
"""

from typing import Dict, List, Tuple, Optional, Callable, Any
from datetime import datetime
from enum import Enum
import logging


class InterlockAction(Enum):
    """Actions when interlock triggers"""
    BLOCK = "block"
    WARN = "warn"
    REQUIRE_APPROVAL = "require-approval"
    EMERGENCY_STOP = "emergency-stop"


class InterlockSeverity(Enum):
    """Interlock severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SafetyInterlock:
    """
    Represents a single safety interlock rule
    """

    def __init__(self, interlock_def: Dict[str, Any]):
        """
        Initialize safety interlock

        Args:
            interlock_def: Interlock definition from protocol JSON
        """
        self.interlock_id = interlock_def["interlockId"]
        self.type = interlock_def["type"]
        self.condition = interlock_def["condition"]
        self.action = InterlockAction(interlock_def["action"])
        self.message = interlock_def["message"]
        self.severity = InterlockSeverity(interlock_def.get("severity", "high"))

        self.triggered = False
        self.trigger_count = 0
        self.last_check_time: Optional[datetime] = None
        self.last_trigger_time: Optional[datetime] = None

        self.logger = logging.getLogger(f"{__name__}.{self.interlock_id}")

    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if interlock condition is satisfied

        Args:
            context: Current test context (equipment state, measurements, etc.)

        Returns:
            True if condition satisfied (safe), False if triggered
        """
        self.last_check_time = datetime.now()

        try:
            # Evaluate condition (simplified - production would use safe expression evaluator)
            result = self._evaluate_condition(context)

            if not result:
                self.triggered = True
                self.trigger_count += 1
                self.last_trigger_time = datetime.now()
                self.logger.warning(f"Interlock {self.interlock_id} TRIGGERED: {self.message}")
            else:
                self.triggered = False

            return result

        except Exception as e:
            self.logger.error(f"Error evaluating interlock {self.interlock_id}: {str(e)}")
            # Fail-safe: treat evaluation errors as triggered
            self.triggered = True
            return False

    def _evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate interlock condition expression

        Args:
            context: Test context dictionary

        Returns:
            True if condition satisfied (safe)
        """
        # Simplified condition evaluation
        # Production implementation would use safe eval or rules engine

        # Example conditions and their evaluation:
        # "equipment.calibration.valid === true"
        # "operator.qualification.highVoltage === true"
        # "voltage.discharged === true"
        # "leakageCurrent < 10.0"

        # For now, check common patterns
        condition_lower = self.condition.lower()

        if "calibration" in condition_lower:
            return context.get("equipment", {}).get("calibration", {}).get("valid", False)

        if "qualification" in condition_lower:
            return context.get("operator", {}).get("qualified", False)

        if "grounded" in condition_lower or "ground" in condition_lower:
            return context.get("device", {}).get("grounded", False)

        if "discharged" in condition_lower:
            return context.get("voltage", {}).get("discharged", False)

        if "leakagecurrent" in condition_lower.replace(" ", ""):
            current = context.get("leakageCurrent", 0)
            # Parse threshold from condition (simplified)
            try:
                if "<" in self.condition:
                    threshold = float(self.condition.split("<")[1].strip())
                    return current < threshold
                elif ">" in self.condition:
                    threshold = float(self.condition.split(">")[1].strip())
                    return current > threshold
            except:
                pass

        # Default to safe (would be fail-safe in production)
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current interlock status"""
        return {
            "interlockId": self.interlock_id,
            "type": self.type,
            "action": self.action.value,
            "severity": self.severity.value,
            "triggered": self.triggered,
            "triggerCount": self.trigger_count,
            "message": self.message if self.triggered else None,
            "lastCheckTime": self.last_check_time.isoformat() if self.last_check_time else None,
            "lastTriggerTime": self.last_trigger_time.isoformat() if self.last_trigger_time else None
        }


class SafetyInterlockEngine:
    """
    Manages all safety interlocks for a protocol
    """

    def __init__(self, protocol_def: Dict[str, Any]):
        """
        Initialize safety interlock engine

        Args:
            protocol_def: Protocol definition with safetyInterlocks
        """
        self.protocol_id = protocol_def.get("protocolId", "UNKNOWN")
        self.interlocks: List[SafetyInterlock] = []

        # Create interlock objects
        for interlock_def in protocol_def.get("safetyInterlocks", []):
            interlock = SafetyInterlock(interlock_def)
            self.interlocks.append(interlock)

        self.logger = logging.getLogger(f"{__name__}.{self.protocol_id}")
        self.check_history: List[Dict] = []

    def check_all(self, context: Dict[str, Any], interlock_type: Optional[str] = None) -> Tuple[bool, List[SafetyInterlock]]:
        """
        Check all interlocks (optionally filtered by type)

        Args:
            context: Current test context
            interlock_type: Optional filter by type ('pre-test', 'during-test', 'post-test')

        Returns:
            Tuple of (all_passed, list of triggered interlocks)
        """
        triggered = []

        for interlock in self.interlocks:
            # Filter by type if specified
            if interlock_type and interlock.type != interlock_type:
                continue

            # Check interlock
            passed = interlock.check(context)

            if not passed:
                triggered.append(interlock)

        all_passed = len(triggered) == 0

        # Log check results
        check_record = {
            "timestamp": datetime.now().isoformat(),
            "interlockType": interlock_type,
            "totalChecked": len(self.interlocks) if interlock_type is None else sum(1 for i in self.interlocks if i.type == interlock_type),
            "triggered": len(triggered),
            "passed": all_passed
        }
        self.check_history.append(check_record)

        if not all_passed:
            self.logger.warning(f"Safety check failed: {len(triggered)} interlocks triggered")
            for interlock in triggered:
                self.logger.warning(f"  - [{interlock.severity.value}] {interlock.interlock_id}: {interlock.message}")

        return all_passed, triggered

    def check_critical(self, context: Dict[str, Any]) -> Tuple[bool, List[SafetyInterlock]]:
        """Check only critical interlocks"""
        triggered = []

        for interlock in self.interlocks:
            if interlock.severity == InterlockSeverity.CRITICAL:
                passed = interlock.check(context)
                if not passed:
                    triggered.append(interlock)

        return len(triggered) == 0, triggered

    def get_emergency_stop_interlocks(self) -> List[SafetyInterlock]:
        """Get all interlocks that trigger emergency stop"""
        return [i for i in self.interlocks if i.action == InterlockAction.EMERGENCY_STOP]

    def get_blocking_interlocks(self) -> List[SafetyInterlock]:
        """Get all interlocks that block test execution"""
        return [i for i in self.interlocks if i.action == InterlockAction.BLOCK]

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all interlock statuses"""
        return {
            "protocolId": self.protocol_id,
            "totalInterlocks": len(self.interlocks),
            "interlocks": [i.get_status() for i in self.interlocks],
            "currentlyTriggered": sum(1 for i in self.interlocks if i.triggered),
            "totalChecks": len(self.check_history),
            "criticalInterlocks": sum(1 for i in self.interlocks if i.severity == InterlockSeverity.CRITICAL)
        }

    def reset_all(self):
        """Reset all interlocks"""
        for interlock in self.interlocks:
            interlock.triggered = False

        self.logger.info("All interlocks reset")


class ApprovalGate:
    """
    Represents an approval gate in the workflow
    """

    def __init__(self, gate_def: Dict[str, Any]):
        """
        Initialize approval gate

        Args:
            gate_def: Gate definition from protocol JSON
        """
        self.gate_id = gate_def["gateId"]
        self.stage = gate_def["stage"]
        self.role = gate_def["role"]
        self.required = gate_def.get("required", True)
        self.criteria = gate_def.get("criteria", [])

        self.approved = False
        self.approver: Optional[str] = None
        self.approval_time: Optional[datetime] = None
        self.comments: str = ""
        self.criteria_checklist: Dict[str, bool] = {c: False for c in self.criteria}

    def approve(self, approver: str, comments: str = "", criteria_checklist: Optional[Dict] = None):
        """
        Approve this gate

        Args:
            approver: Person providing approval
            comments: Approval comments
            criteria_checklist: Optional checklist of criteria
        """
        self.approved = True
        self.approver = approver
        self.approval_time = datetime.now()
        self.comments = comments

        if criteria_checklist:
            self.criteria_checklist.update(criteria_checklist)

    def reject(self, approver: str, comments: str):
        """Reject this gate"""
        self.approved = False
        self.approver = approver
        self.approval_time = datetime.now()
        self.comments = comments

    def get_status(self) -> Dict[str, Any]:
        """Get gate status"""
        return {
            "gateId": self.gate_id,
            "stage": self.stage,
            "role": self.role,
            "required": self.required,
            "approved": self.approved,
            "approver": self.approver,
            "approvalTime": self.approval_time.isoformat() if self.approval_time else None,
            "comments": self.comments,
            "criteria": self.criteria,
            "criteriaChecklist": self.criteria_checklist
        }


class ApprovalWorkflow:
    """
    Manages approval workflow for protocol
    """

    def __init__(self, protocol_def: Dict[str, Any]):
        """
        Initialize approval workflow

        Args:
            protocol_def: Protocol definition with approvalGates
        """
        self.protocol_id = protocol_def.get("protocolId", "UNKNOWN")
        self.gates: List[ApprovalGate] = []

        # Create gate objects
        for gate_def in protocol_def.get("approvalGates", []):
            gate = ApprovalGate(gate_def)
            self.gates.append(gate)

        self.logger = logging.getLogger(f"{__name__}.{self.protocol_id}")

    def check_stage_approved(self, stage: str) -> Tuple[bool, List[ApprovalGate]]:
        """
        Check if all required gates for a stage are approved

        Args:
            stage: Approval stage name

        Returns:
            Tuple of (all_approved, list of pending gates)
        """
        stage_gates = [g for g in self.gates if g.stage == stage]
        pending = [g for g in stage_gates if g.required and not g.approved]

        return len(pending) == 0, pending

    def get_pending_approvals(self) -> List[ApprovalGate]:
        """Get all pending required approvals"""
        return [g for g in self.gates if g.required and not g.approved]

    def get_gate(self, gate_id: str) -> Optional[ApprovalGate]:
        """Get specific gate by ID"""
        for gate in self.gates:
            if gate.gate_id == gate_id:
                return gate
        return None

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get complete workflow status"""
        return {
            "protocolId": self.protocol_id,
            "totalGates": len(self.gates),
            "gates": [g.get_status() for g in self.gates],
            "pendingApprovals": len(self.get_pending_approvals()),
            "completedGates": sum(1 for g in self.gates if g.approved)
        }
