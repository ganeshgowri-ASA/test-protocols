"""
Protocol Executor Module

Manages execution of protocol test steps and data collection.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a test step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProtocolExecutor:
    """Executes protocol test steps and manages test run state."""

    def __init__(self, protocol: Dict[str, Any], test_run_id: str):
        """
        Initialize the ProtocolExecutor.

        Args:
            protocol: Protocol definition
            test_run_id: Unique identifier for this test run
        """
        self.protocol = protocol
        self.test_run_id = test_run_id
        self.test_data: Dict[str, Any] = {
            'test_run_id': test_run_id,
            'protocol_id': protocol['protocol_id'],
            'protocol_version': protocol['version'],
            'start_time': None,
            'end_time': None,
            'status': StepStatus.PENDING.value,
            'steps': {},
            'measurements': {},
            'qc_flags': [],
            'metadata': {}
        }
        self.current_step_id: Optional[int] = None
        self.current_substep_id: Optional[float] = None

    def start_test(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Start the test run.

        Args:
            metadata: Additional metadata for the test run
        """
        self.test_data['start_time'] = datetime.now().isoformat()
        self.test_data['status'] = StepStatus.IN_PROGRESS.value

        if metadata:
            self.test_data['metadata'].update(metadata)

        logger.info(
            f"Started test run {self.test_run_id} for protocol {self.protocol['protocol_id']}"
        )

    def start_step(self, step_id: int, substep_id: float) -> Dict[str, Any]:
        """
        Start a test step.

        Args:
            step_id: Step ID
            substep_id: Substep ID

        Returns:
            Substep definition
        """
        self.current_step_id = step_id
        self.current_substep_id = substep_id

        # Find substep definition
        substep = self._find_substep(step_id, substep_id)
        if substep is None:
            raise ValueError(
                f"Step {step_id}.{substep_id} not found in protocol"
            )

        # Initialize step data if not exists
        step_key = f"{step_id}.{substep_id}"
        if step_key not in self.test_data['steps']:
            self.test_data['steps'][step_key] = {
                'step_id': step_id,
                'substep_id': substep_id,
                'name': substep['name'],
                'type': substep['type'],
                'status': StepStatus.IN_PROGRESS.value,
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'data': {},
                'notes': []
            }

        logger.info(f"Started step {step_key}: {substep['name']}")
        return substep

    def record_data(
        self,
        step_id: int,
        substep_id: float,
        data: Dict[str, Any]
    ):
        """
        Record data for a test step.

        Args:
            step_id: Step ID
            substep_id: Substep ID
            data: Data to record
        """
        step_key = f"{step_id}.{substep_id}"

        if step_key not in self.test_data['steps']:
            raise ValueError(
                f"Step {step_key} not started. Call start_step() first."
            )

        # Update step data
        self.test_data['steps'][step_key]['data'].update(data)

        # Store in measurements for easy access
        for field_id, value in data.items():
            measurement_key = f"{step_key}.{field_id}"
            self.test_data['measurements'][measurement_key] = {
                'step_id': step_id,
                'substep_id': substep_id,
                'field_id': field_id,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }

        logger.debug(f"Recorded data for step {step_key}: {list(data.keys())}")

    def complete_step(
        self,
        step_id: int,
        substep_id: float,
        status: StepStatus = StepStatus.COMPLETED,
        notes: Optional[str] = None
    ):
        """
        Complete a test step.

        Args:
            step_id: Step ID
            substep_id: Substep ID
            status: Completion status
            notes: Optional notes
        """
        step_key = f"{step_id}.{substep_id}"

        if step_key not in self.test_data['steps']:
            raise ValueError(
                f"Step {step_key} not started. Call start_step() first."
            )

        self.test_data['steps'][step_key]['status'] = status.value
        self.test_data['steps'][step_key]['end_time'] = datetime.now().isoformat()

        if notes:
            self.test_data['steps'][step_key]['notes'].append(notes)

        logger.info(f"Completed step {step_key} with status {status.value}")

    def add_qc_flag(
        self,
        rule_id: str,
        severity: str,
        message: str,
        step_id: Optional[int] = None,
        substep_id: Optional[float] = None
    ):
        """
        Add a QC flag to the test run.

        Args:
            rule_id: QC rule ID
            severity: Severity level (info, warning, error)
            message: QC message
            step_id: Optional step ID where issue occurred
            substep_id: Optional substep ID where issue occurred
        """
        flag = {
            'rule_id': rule_id,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        if step_id is not None:
            flag['step_id'] = step_id
        if substep_id is not None:
            flag['substep_id'] = substep_id

        self.test_data['qc_flags'].append(flag)

        logger.warning(
            f"QC flag added: [{severity}] {rule_id} - {message}"
        )

    def complete_test(self, status: StepStatus = StepStatus.COMPLETED):
        """
        Complete the test run.

        Args:
            status: Final test status
        """
        self.test_data['end_time'] = datetime.now().isoformat()
        self.test_data['status'] = status.value

        logger.info(
            f"Completed test run {self.test_run_id} with status {status.value}"
        )

    def get_test_data(self) -> Dict[str, Any]:
        """
        Get the complete test data.

        Returns:
            Dictionary containing all test data
        """
        return self.test_data

    def get_step_data(self, step_id: int, substep_id: float) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific step.

        Args:
            step_id: Step ID
            substep_id: Substep ID

        Returns:
            Step data or None if not found
        """
        step_key = f"{step_id}.{substep_id}"
        return self.test_data['steps'].get(step_key)

    def get_measurement(
        self,
        step_id: int,
        substep_id: float,
        field_id: str
    ) -> Optional[Any]:
        """
        Get a specific measurement value.

        Args:
            step_id: Step ID
            substep_id: Substep ID
            field_id: Field ID

        Returns:
            Measurement value or None if not found
        """
        measurement_key = f"{step_id}.{substep_id}.{field_id}"
        measurement = self.test_data['measurements'].get(measurement_key)
        return measurement['value'] if measurement else None

    def calculate_field(
        self,
        formula: str,
        context: Dict[str, Any]
    ) -> Optional[float]:
        """
        Calculate a field value based on a formula.

        Args:
            formula: Calculation formula
            context: Context variables for calculation

        Returns:
            Calculated value or None if error
        """
        try:
            # Simple eval for calculations (would need safer implementation)
            # For production, use a proper expression parser
            result = eval(formula, {"__builtins__": {}}, context)
            return float(result) if result is not None else None
        except Exception as e:
            logger.error(f"Error calculating formula '{formula}': {e}")
            return None

    def get_progress(self) -> Dict[str, Any]:
        """
        Get test run progress.

        Returns:
            Dictionary with progress information
        """
        total_steps = len(self.protocol.get('test_sequence', {}).get('steps', []))
        total_substeps = sum(
            len(step.get('substeps', []))
            for step in self.protocol.get('test_sequence', {}).get('steps', [])
        )

        completed_substeps = sum(
            1 for step_data in self.test_data['steps'].values()
            if step_data['status'] == StepStatus.COMPLETED.value
        )

        return {
            'total_steps': total_steps,
            'total_substeps': total_substeps,
            'completed_substeps': completed_substeps,
            'progress_percent': (completed_substeps / total_substeps * 100)
            if total_substeps > 0 else 0,
            'current_step': self.current_step_id,
            'current_substep': self.current_substep_id,
            'status': self.test_data['status'],
            'qc_flags_count': len(self.test_data['qc_flags'])
        }

    def _find_substep(
        self,
        step_id: int,
        substep_id: float
    ) -> Optional[Dict[str, Any]]:
        """Find a substep in the protocol."""
        steps = self.protocol.get('test_sequence', {}).get('steps', [])

        for step in steps:
            if step.get('step_id') == step_id:
                for substep in step.get('substeps', []):
                    if substep.get('substep_id') == substep_id:
                        return substep

        return None
