"""
Test Runner Module
==================

Manages test execution workflow, state transitions, and data collection.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    INVALID = "invalid"


class TestResult(Enum):
    """Test result enumeration"""
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class TestExecution:
    """Represents a test execution instance"""
    protocol_id: str
    module_id: str
    operator_name: str
    test_date: str
    status: str = TestStatus.PENDING.value
    result: Optional[str] = None
    test_data: Dict[str, Any] = field(default_factory=dict)
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    qc_checks: List[Dict[str, Any]] = field(default_factory=list)
    execution_id: Optional[int] = None
    test_start_time: Optional[str] = None
    test_end_time: Optional[str] = None
    notes: str = ""
    failure_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestExecution':
        """Create from dictionary"""
        return cls(**data)


class TestRunner:
    """
    Test Runner class for managing test execution workflow.

    Features:
    - Initialize test execution
    - Manage test state transitions
    - Collect measurements
    - Perform quality checks
    - Determine pass/fail result
    - Generate test reports
    """

    def __init__(self, protocol_config: Dict[str, Any]):
        """
        Initialize the Test Runner.

        Args:
            protocol_config: Protocol configuration dictionary
        """
        self.protocol_config = protocol_config
        self.protocol_id = protocol_config.get('protocol_id', 'UNKNOWN')
        self.current_execution: Optional[TestExecution] = None

    def start_test(
        self,
        module_id: str,
        operator_name: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> TestExecution:
        """
        Start a new test execution.

        Args:
            module_id: Module identifier
            operator_name: Name of operator
            initial_data: Initial test data

        Returns:
            TestExecution object
        """
        execution = TestExecution(
            protocol_id=self.protocol_id,
            module_id=module_id,
            operator_name=operator_name,
            test_date=datetime.now().date().isoformat(),
            status=TestStatus.IN_PROGRESS.value,
            test_start_time=datetime.now().isoformat(),
            test_data=initial_data or {}
        )

        self.current_execution = execution
        logger.info(f"Started test execution for module {module_id}")

        return execution

    def update_status(self, execution: TestExecution, status: TestStatus):
        """
        Update test execution status.

        Args:
            execution: TestExecution object
            status: New status
        """
        old_status = execution.status
        execution.status = status.value

        logger.info(f"Test status changed: {old_status} -> {status.value}")

    def add_measurement(
        self,
        execution: TestExecution,
        measurement_name: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a measurement to the test execution.

        Args:
            execution: TestExecution object
            measurement_name: Name of measurement
            value: Measured value
            unit: Unit of measurement
            timestamp: Measurement timestamp (defaults to now)
            metadata: Additional metadata
        """
        measurement = {
            'measurement_name': measurement_name,
            'value': value,
            'unit': unit,
            'timestamp': (timestamp or datetime.now()).isoformat(),
            'metadata': metadata or {}
        }

        execution.measurements.append(measurement)
        logger.debug(f"Added measurement: {measurement_name} = {value} {unit}")

    def perform_qc_check(
        self,
        execution: TestExecution,
        check_name: str,
        expected_value: Any,
        actual_value: Any,
        check_type: str = "comparison",
        is_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Perform a quality control check.

        Args:
            execution: TestExecution object
            check_name: Name of QC check
            expected_value: Expected value
            actual_value: Actual value
            check_type: Type of check
            is_critical: Whether check is critical

        Returns:
            QC check result dictionary
        """
        # Determine pass/fail
        passed = self._evaluate_qc_check(expected_value, actual_value, check_type)

        qc_check = {
            'check_name': check_name,
            'expected_value': expected_value,
            'actual_value': actual_value,
            'check_type': check_type,
            'is_critical': is_critical,
            'result': 'pass' if passed else 'fail',
            'timestamp': datetime.now().isoformat()
        }

        execution.qc_checks.append(qc_check)
        logger.info(f"QC Check: {check_name} - {'PASS' if passed else 'FAIL'}")

        return qc_check

    def _evaluate_qc_check(
        self,
        expected: Any,
        actual: Any,
        check_type: str
    ) -> bool:
        """Evaluate QC check based on type"""
        if check_type == "comparison":
            return expected == actual
        elif check_type == "range":
            if isinstance(expected, dict) and 'min' in expected and 'max' in expected:
                return expected['min'] <= actual <= expected['max']
        elif check_type == "boolean":
            return bool(actual) == bool(expected)

        return False

    def evaluate_acceptance_criteria(
        self,
        execution: TestExecution
    ) -> TestResult:
        """
        Evaluate test data against acceptance criteria.

        Args:
            execution: TestExecution object

        Returns:
            TestResult enumeration
        """
        acceptance_criteria = self.protocol_config.get('acceptance_criteria', {})

        # Check if any critical QC checks failed
        critical_failures = [
            qc for qc in execution.qc_checks
            if qc['is_critical'] and qc['result'] == 'fail'
        ]

        if critical_failures:
            logger.warning(f"Critical QC failures: {len(critical_failures)}")
            return TestResult.FAIL

        # Evaluate each acceptance criterion
        failures = []
        for criterion_name, criterion in acceptance_criteria.items():
            if isinstance(criterion, dict):
                if not self._check_acceptance_criterion(criterion_name, criterion, execution.test_data):
                    failures.append(criterion_name)

        if failures:
            logger.warning(f"Acceptance criteria failures: {failures}")
            return TestResult.FAIL

        logger.info("All acceptance criteria passed")
        return TestResult.PASS

    def _check_acceptance_criterion(
        self,
        criterion_name: str,
        criterion: Dict[str, Any],
        test_data: Dict[str, Any]
    ) -> bool:
        """Check a single acceptance criterion"""
        # Find matching data field
        data_field = criterion_name
        if data_field not in test_data:
            for key in test_data.keys():
                if criterion_name in key:
                    data_field = key
                    break

        if data_field not in test_data:
            return True  # Skip if not applicable

        value = test_data[data_field]
        if value is None:
            return True

        condition = criterion.get('condition')

        if condition == 'greater_than_or_equal':
            min_value = criterion.get('min_value')
            if min_value is not None:
                return value >= min_value

        elif condition == 'less_than_or_equal':
            max_value = criterion.get('max_value')
            if max_value is not None:
                return value <= max_value

        elif condition == 'equal':
            expected_value = criterion.get('value')
            if expected_value is not None:
                return value == expected_value

        # Boolean criteria
        if 'allowed' in criterion:
            allowed = criterion['allowed']
            if isinstance(value, bool):
                return value == allowed

        return True

    def complete_test(
        self,
        execution: TestExecution,
        result: Optional[TestResult] = None
    ) -> TestExecution:
        """
        Complete the test execution.

        Args:
            execution: TestExecution object
            result: Test result (auto-evaluated if not provided)

        Returns:
            Updated TestExecution object
        """
        # Auto-evaluate result if not provided
        if result is None:
            result = self.evaluate_acceptance_criteria(execution)

        execution.result = result.value
        execution.status = TestStatus.COMPLETED.value
        execution.test_end_time = datetime.now().isoformat()

        logger.info(f"Test completed with result: {result.value}")

        return execution

    def abort_test(
        self,
        execution: TestExecution,
        reason: str
    ) -> TestExecution:
        """
        Abort the test execution.

        Args:
            execution: TestExecution object
            reason: Reason for abortion

        Returns:
            Updated TestExecution object
        """
        execution.status = TestStatus.ABORTED.value
        execution.failure_reason = reason
        execution.test_end_time = datetime.now().isoformat()

        logger.warning(f"Test aborted: {reason}")

        return execution

    def get_test_summary(self, execution: TestExecution) -> Dict[str, Any]:
        """
        Get test execution summary.

        Args:
            execution: TestExecution object

        Returns:
            Summary dictionary
        """
        return {
            'protocol_id': execution.protocol_id,
            'module_id': execution.module_id,
            'test_date': execution.test_date,
            'operator': execution.operator_name,
            'status': execution.status,
            'result': execution.result,
            'duration': self._calculate_duration(execution),
            'total_measurements': len(execution.measurements),
            'qc_checks_passed': sum(1 for qc in execution.qc_checks if qc['result'] == 'pass'),
            'qc_checks_failed': sum(1 for qc in execution.qc_checks if qc['result'] == 'fail'),
            'critical_failures': sum(
                1 for qc in execution.qc_checks
                if qc['is_critical'] and qc['result'] == 'fail'
            )
        }

    def _calculate_duration(self, execution: TestExecution) -> Optional[float]:
        """Calculate test duration in seconds"""
        if not execution.test_start_time or not execution.test_end_time:
            return None

        try:
            start = datetime.fromisoformat(execution.test_start_time)
            end = datetime.fromisoformat(execution.test_end_time)
            duration = (end - start).total_seconds()
            return duration
        except ValueError:
            return None

    def export_execution(
        self,
        execution: TestExecution,
        file_path: str,
        format: str = 'json'
    ) -> bool:
        """
        Export test execution to file.

        Args:
            execution: TestExecution object
            file_path: Output file path
            format: Export format ('json' or 'csv')

        Returns:
            True if successful
        """
        try:
            if format == 'json':
                with open(file_path, 'w') as f:
                    json.dump(execution.to_dict(), f, indent=2)
                logger.info(f"Execution exported to: {file_path}")
                return True
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            logger.error(f"Error exporting execution: {e}")
            return False
