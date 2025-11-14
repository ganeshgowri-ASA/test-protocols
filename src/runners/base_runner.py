"""
Base test runner class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from ..models import (
    Protocol, ProtocolVersion, TestExecution, TestMeasurement,
    TestResult, Sample, Equipment, TestStatus, TestOutcome
)

logger = logging.getLogger(__name__)


class BaseTestRunner(ABC):
    """
    Abstract base class for test runners

    All protocol-specific test runners should inherit from this class
    and implement the required abstract methods.
    """

    def __init__(
        self,
        protocol_id: str,
        db_session: Session,
        protocol_json_path: Optional[str] = None
    ):
        """
        Initialize the test runner

        Args:
            protocol_id: Protocol identifier (e.g., 'GROUND-001')
            db_session: SQLAlchemy database session
            protocol_json_path: Optional path to protocol JSON file
        """
        self.protocol_id = protocol_id
        self.db = db_session
        self.protocol_json = self._load_protocol_json(protocol_json_path)
        self.protocol = self._get_or_create_protocol()

    def _load_protocol_json(self, json_path: Optional[str] = None) -> Dict[str, Any]:
        """Load protocol JSON definition"""
        if json_path is None:
            # Default path based on protocol_id
            json_path = f"protocols/{self.protocol_id.lower()}/protocol.json"

        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"Protocol JSON not found: {json_path}")

        with open(path, 'r') as f:
            return json.load(f)

    def _get_or_create_protocol(self) -> Protocol:
        """Get existing protocol or create new one from JSON"""
        protocol = self.db.query(Protocol).filter(
            Protocol.protocol_id == self.protocol_id
        ).first()

        if protocol is None:
            # Create new protocol from JSON
            std = self.protocol_json.get('standard', {})
            protocol = Protocol(
                protocol_id=self.protocol_json['protocol_id'],
                protocol_name=self.protocol_json['protocol_name'],
                category=self.protocol_json['category'],
                standard_name=std.get('name', ''),
                standard_section=std.get('section', ''),
                standard_edition=std.get('edition', ''),
                description=self.protocol_json.get('description', '')
            )
            self.db.add(protocol)
            self.db.commit()
            self.db.refresh(protocol)

            # Create protocol version
            version = ProtocolVersion(
                protocol_id=protocol.id,
                version=self.protocol_json['version'],
                json_definition=self.protocol_json,
                author=self.protocol_json.get('metadata', {}).get('author', ''),
                is_current=True
            )
            self.db.add(version)
            self.db.commit()

        return protocol

    def create_test_execution(
        self,
        sample_id: int,
        operator_id: str,
        operator_name: str,
        equipment_id: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
        scheduled_start: Optional[datetime] = None
    ) -> TestExecution:
        """
        Create a new test execution record

        Args:
            sample_id: ID of the sample being tested
            operator_id: Operator identifier
            operator_name: Operator name
            equipment_id: Optional equipment ID
            parameters: Optional test parameters
            scheduled_start: Optional scheduled start time

        Returns:
            TestExecution object
        """
        # Generate test number
        test_number = self._generate_test_number()

        test_execution = TestExecution(
            test_number=test_number,
            protocol_id=self.protocol.id,
            sample_id=sample_id,
            operator_id=operator_id,
            operator_name=operator_name,
            equipment_id=equipment_id,
            parameters=parameters or {},
            scheduled_start=scheduled_start,
            status=TestStatus.PENDING
        )

        self.db.add(test_execution)
        self.db.commit()
        self.db.refresh(test_execution)

        logger.info(f"Created test execution: {test_number}")
        return test_execution

    def _generate_test_number(self) -> str:
        """Generate unique test number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{self.protocol_id}-{timestamp}"

    def start_test(self, test_execution: TestExecution) -> None:
        """Mark test as started"""
        test_execution.status = TestStatus.RUNNING
        test_execution.actual_start = datetime.utcnow()
        self.db.commit()
        logger.info(f"Test {test_execution.test_number} started")

    def complete_test(
        self,
        test_execution: TestExecution,
        outcome: TestOutcome
    ) -> None:
        """Mark test as completed"""
        test_execution.status = TestStatus.COMPLETED
        test_execution.outcome = outcome
        test_execution.actual_end = datetime.utcnow()

        if test_execution.actual_start:
            duration = (test_execution.actual_end - test_execution.actual_start).total_seconds()
            test_execution.duration_seconds = duration

        self.db.commit()
        logger.info(
            f"Test {test_execution.test_number} completed with outcome: {outcome.value}"
        )

    def abort_test(
        self,
        test_execution: TestExecution,
        reason: str
    ) -> None:
        """Abort test execution"""
        test_execution.status = TestStatus.ABORTED
        test_execution.actual_end = datetime.utcnow()
        test_execution.post_test_notes = f"Test aborted: {reason}"
        self.db.commit()
        logger.warning(f"Test {test_execution.test_number} aborted: {reason}")

    def add_measurement(
        self,
        test_execution: TestExecution,
        measurement_name: str,
        value: Optional[float] = None,
        value_text: Optional[str] = None,
        unit: Optional[str] = None,
        measurement_point: Optional[str] = None,
        within_limits: Optional[bool] = None
    ) -> TestMeasurement:
        """
        Add a measurement to the test execution

        Args:
            test_execution: TestExecution object
            measurement_name: Name of the measurement
            value: Numeric value
            value_text: Text value (for non-numeric measurements)
            unit: Unit of measurement
            measurement_point: Optional measurement point identifier
            within_limits: Optional flag indicating if measurement is within limits

        Returns:
            TestMeasurement object
        """
        measurement = TestMeasurement(
            test_execution_id=test_execution.id,
            measurement_name=measurement_name,
            value=value,
            value_text=value_text,
            unit=unit,
            measurement_point=measurement_point,
            within_limits=within_limits,
            timestamp=datetime.utcnow()
        )

        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)

        logger.debug(
            f"Added measurement: {measurement_name} = {value} {unit}"
        )
        return measurement

    def evaluate_criteria(
        self,
        test_execution: TestExecution,
        measurements: Dict[str, float]
    ) -> List[TestResult]:
        """
        Evaluate pass/fail criteria

        Args:
            test_execution: TestExecution object
            measurements: Dictionary of measurement name to value

        Returns:
            List of TestResult objects
        """
        results = []
        pass_criteria = self.protocol_json.get('pass_criteria', [])

        for criterion in pass_criteria:
            result = self._evaluate_single_criterion(
                test_execution,
                criterion,
                measurements
            )
            results.append(result)

        return results

    def _evaluate_single_criterion(
        self,
        test_execution: TestExecution,
        criterion: Dict[str, Any],
        measurements: Dict[str, float]
    ) -> TestResult:
        """Evaluate a single pass/fail criterion"""
        condition = criterion['condition']
        description = criterion['description']
        severity = criterion.get('severity', 'critical')

        try:
            # Create evaluation context with measurements and parameters
            eval_context = {**measurements, **test_execution.parameters}

            # Add parameters from protocol JSON
            params = self.protocol_json.get('parameters', {})
            for param_name, param_config in params.items():
                if param_config.get('type') == 'constant':
                    eval_context[param_name] = param_config['value']

            # Evaluate condition
            passed = eval(condition, {"__builtins__": {}}, eval_context)

            result = TestResult(
                test_execution_id=test_execution.id,
                criterion_name=description,
                criterion_condition=condition,
                severity=severity,
                passed=bool(passed),
                description=description
            )

        except Exception as e:
            logger.error(f"Error evaluating criterion '{description}': {e}")
            result = TestResult(
                test_execution_id=test_execution.id,
                criterion_name=description,
                criterion_condition=condition,
                severity=severity,
                passed=False,
                description=description,
                failure_reason=f"Evaluation error: {str(e)}"
            )

        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)

        return result

    def check_safety_limits(
        self,
        measurements: Dict[str, float]
    ) -> Optional[str]:
        """
        Check if any safety limits are exceeded

        Args:
            measurements: Current measurement values

        Returns:
            Action to take if limit exceeded, or None if all OK
        """
        safety_limits = self.protocol_json.get('safety_limits', {})

        for limit_name, limit_config in safety_limits.items():
            limit_value = limit_config['value']
            action = limit_config['action']

            # Extract measurement name from limit name
            # e.g., 'max_voltage' -> 'voltage'
            measurement_name = limit_name.replace('max_', '').replace('min_', '')

            if measurement_name in measurements:
                actual_value = measurements[measurement_name]

                if 'max_' in limit_name and actual_value > limit_value:
                    logger.warning(
                        f"Safety limit exceeded: {measurement_name} = {actual_value} > {limit_value}"
                    )
                    return action

                if 'min_' in limit_name and actual_value < limit_value:
                    logger.warning(
                        f"Safety limit exceeded: {measurement_name} = {actual_value} < {limit_value}"
                    )
                    return action

        return None

    @abstractmethod
    def run_test(
        self,
        test_execution: TestExecution,
        **kwargs
    ) -> TestOutcome:
        """
        Execute the test protocol

        This method must be implemented by protocol-specific runners.

        Args:
            test_execution: TestExecution object
            **kwargs: Additional protocol-specific arguments

        Returns:
            TestOutcome indicating pass/fail
        """
        pass

    @abstractmethod
    def calculate_parameters(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate test parameters from inputs

        This method must be implemented by protocol-specific runners.

        Args:
            input_params: Input parameters provided by user

        Returns:
            Dictionary of calculated parameters
        """
        pass
