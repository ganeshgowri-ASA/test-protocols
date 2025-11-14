"""
Base Protocol Classes
Defines abstract base classes for all test protocols
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ProtocolStatus(Enum):
    """Protocol execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class StepStatus(Enum):
    """Individual step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Criticality(Enum):
    """Acceptance criteria criticality levels"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class ProtocolStep:
    """Represents a single step in a protocol phase"""
    step_id: str
    action: str
    description: str
    acceptance_criteria: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    data_collection: Optional[Union[str, List[str]]] = None
    notes: Optional[str] = None
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    operator_notes: str = ""

    def start(self):
        """Mark step as started"""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = datetime.now()

    def complete(self, data: Optional[Dict[str, Any]] = None):
        """Mark step as completed with optional data"""
        self.status = StepStatus.COMPLETED
        self.end_time = datetime.now()
        if data:
            self.data.update(data)

    def fail(self, reason: str):
        """Mark step as failed with reason"""
        self.status = StepStatus.FAILED
        self.end_time = datetime.now()
        self.operator_notes += f"\nFailed: {reason}"

    def skip(self, reason: str):
        """Skip this step with reason"""
        self.status = StepStatus.SKIPPED
        self.operator_notes += f"\nSkipped: {reason}"


@dataclass
class ProtocolPhase:
    """Represents a phase containing multiple steps"""
    phase_id: int
    name: str
    duration: str
    steps: List[ProtocolStep]
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def start(self):
        """Mark phase as started"""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = datetime.now()

    def complete(self):
        """Mark phase as completed"""
        self.status = StepStatus.COMPLETED
        self.end_time = datetime.now()

    def get_progress(self) -> Dict[str, int]:
        """Get phase progress statistics"""
        total = len(self.steps)
        completed = sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)
        failed = sum(1 for step in self.steps if step.status == StepStatus.FAILED)
        in_progress = sum(1 for step in self.steps if step.status == StepStatus.IN_PROGRESS)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress
        }


@dataclass
class AcceptanceCriterion:
    """Represents an acceptance criterion for pass/fail determination"""
    parameter: str
    requirement: str
    criticality: Criticality
    measurement: str
    actual_value: Optional[float] = None
    passed: Optional[bool] = None
    notes: str = ""

    def evaluate(self, value: float, tolerance: Optional[float] = None) -> bool:
        """
        Evaluate if the measured value meets the acceptance criterion

        Args:
            value: Measured value
            tolerance: Optional tolerance for comparison

        Returns:
            True if criterion is met, False otherwise
        """
        self.actual_value = value
        # This is a simplified evaluation - actual logic would parse requirement string
        # and perform appropriate comparison
        # Implementation would depend on requirement format
        self.passed = True  # Placeholder
        return self.passed


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols

    Provides common functionality for protocol loading, execution tracking,
    data collection, and reporting
    """

    def __init__(self, protocol_path: Union[str, Path]):
        """
        Initialize protocol from JSON definition

        Args:
            protocol_path: Path to protocol JSON file
        """
        self.protocol_path = Path(protocol_path)
        self.config = self._load_protocol()
        self.status = ProtocolStatus.NOT_STARTED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.phases: List[ProtocolPhase] = []
        self.acceptance_criteria: List[AcceptanceCriterion] = []
        self.test_data: Dict[str, Any] = {}
        self.module_info: Dict[str, Any] = {}

        self._initialize_phases()
        self._initialize_acceptance_criteria()

    def _load_protocol(self) -> Dict[str, Any]:
        """Load protocol configuration from JSON file"""
        with open(self.protocol_path, 'r') as f:
            return json.load(f)

    def _initialize_phases(self):
        """Initialize protocol phases from configuration"""
        phases_config = self.config.get("test_procedure", {}).get("phases", [])

        for phase_config in phases_config:
            steps = []
            for step_config in phase_config.get("steps", []):
                step = ProtocolStep(
                    step_id=step_config["step"],
                    action=step_config["action"],
                    description=step_config["description"],
                    acceptance_criteria=step_config.get("acceptance_criteria"),
                    parameters=step_config.get("parameters"),
                    data_collection=step_config.get("data_collection"),
                    notes=step_config.get("notes")
                )
                steps.append(step)

            phase = ProtocolPhase(
                phase_id=phase_config["phase"],
                name=phase_config["name"],
                duration=phase_config["duration"],
                steps=steps
            )
            self.phases.append(phase)

    def _initialize_acceptance_criteria(self):
        """Initialize acceptance criteria from configuration"""
        criteria_config = self.config.get("acceptance_criteria", {})

        for category in ["primary", "secondary"]:
            for criterion_config in criteria_config.get(category, []):
                criterion = AcceptanceCriterion(
                    parameter=criterion_config["parameter"],
                    requirement=criterion_config["requirement"],
                    criticality=Criticality(criterion_config["criticality"]),
                    measurement=criterion_config["measurement"]
                )
                self.acceptance_criteria.append(criterion)

    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol metadata"""
        return self.config.get("protocol", {})

    def get_description(self) -> Dict[str, Any]:
        """Get protocol description"""
        return self.config.get("description", {})

    def get_equipment_list(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get required and optional equipment"""
        return self.config.get("equipment", {})

    def get_test_conditions(self) -> Dict[str, Any]:
        """Get test environmental conditions"""
        return self.config.get("test_conditions", {})

    def set_module_info(self, info: Dict[str, Any]):
        """
        Set module information for this test

        Args:
            info: Dictionary containing module metadata
        """
        self.module_info = info
        self.test_data["module_info"] = info

    def start_protocol(self):
        """Start protocol execution"""
        self.status = ProtocolStatus.IN_PROGRESS
        self.start_time = datetime.now()
        self.test_data["start_time"] = self.start_time.isoformat()

    def complete_protocol(self):
        """Mark protocol as completed"""
        self.status = ProtocolStatus.COMPLETED
        self.end_time = datetime.now()
        self.test_data["end_time"] = self.end_time.isoformat()

    def abort_protocol(self, reason: str):
        """
        Abort protocol execution

        Args:
            reason: Reason for aborting
        """
        self.status = ProtocolStatus.ABORTED
        self.end_time = datetime.now()
        self.test_data["abort_reason"] = reason
        self.test_data["end_time"] = self.end_time.isoformat()

    def get_current_phase(self) -> Optional[ProtocolPhase]:
        """Get the currently active phase"""
        for phase in self.phases:
            if phase.status == StepStatus.IN_PROGRESS:
                return phase
        return None

    def get_current_step(self) -> Optional[ProtocolStep]:
        """Get the currently active step"""
        current_phase = self.get_current_phase()
        if current_phase:
            for step in current_phase.steps:
                if step.status == StepStatus.IN_PROGRESS:
                    return step
        return None

    def record_measurement(self, table: str, field: str, value: Any, unit: Optional[str] = None):
        """
        Record a measurement in the test data

        Args:
            table: Measurement table/category
            field: Field name
            value: Measured value
            unit: Optional unit of measurement
        """
        if table not in self.test_data:
            self.test_data[table] = {}

        self.test_data[table][field] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }

    def get_progress(self) -> Dict[str, Any]:
        """Get overall protocol progress"""
        total_steps = sum(len(phase.steps) for phase in self.phases)
        completed_steps = sum(
            sum(1 for step in phase.steps if step.status == StepStatus.COMPLETED)
            for phase in self.phases
        )

        return {
            "status": self.status.value,
            "total_phases": len(self.phases),
            "completed_phases": sum(1 for phase in self.phases if phase.status == StepStatus.COMPLETED),
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percent": (completed_steps / total_steps * 100) if total_steps > 0 else 0
        }

    def evaluate_acceptance(self) -> Dict[str, Any]:
        """
        Evaluate all acceptance criteria

        Returns:
            Dictionary containing pass/fail status and details
        """
        results = {
            "overall_pass": True,
            "critical_failures": [],
            "major_failures": [],
            "minor_failures": [],
            "criteria_results": []
        }

        for criterion in self.acceptance_criteria:
            if criterion.passed is False:
                failure_info = {
                    "parameter": criterion.parameter,
                    "requirement": criterion.requirement,
                    "actual_value": criterion.actual_value,
                    "notes": criterion.notes
                }

                if criterion.criticality == Criticality.CRITICAL:
                    results["critical_failures"].append(failure_info)
                    results["overall_pass"] = False
                elif criterion.criticality == Criticality.MAJOR:
                    results["major_failures"].append(failure_info)
                elif criterion.criticality == Criticality.MINOR:
                    results["minor_failures"].append(failure_info)

            results["criteria_results"].append({
                "parameter": criterion.parameter,
                "requirement": criterion.requirement,
                "criticality": criterion.criticality.value,
                "passed": criterion.passed,
                "actual_value": criterion.actual_value
            })

        return results

    @abstractmethod
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze test results (protocol-specific implementation)

        Returns:
            Analysis results dictionary
        """
        pass

    def export_data(self, format: str = "json") -> Union[str, Dict[str, Any]]:
        """
        Export test data in specified format

        Args:
            format: Export format (json, csv, etc.)

        Returns:
            Exported data in requested format
        """
        if format == "json":
            return self.test_data
        else:
            raise NotImplementedError(f"Export format '{format}' not implemented")

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate test report

        Returns:
            Complete test report with all sections
        """
        report = {
            "protocol_info": self.get_protocol_info(),
            "module_info": self.module_info,
            "test_conditions": self.get_test_conditions(),
            "execution_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "status": self.status.value,
                "progress": self.get_progress()
            },
            "test_data": self.test_data,
            "analysis": self.analyze_results(),
            "acceptance_evaluation": self.evaluate_acceptance(),
            "generated_at": datetime.now().isoformat()
        }

        return report
