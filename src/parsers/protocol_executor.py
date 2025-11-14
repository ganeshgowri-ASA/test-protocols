"""Protocol executor for running test protocols."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from ..models import Protocol, TestRun, TestStep, Measurement
from ..models.test_run import TestStatus, TestResult


class ProtocolExecutor:
    """Executes test protocols and manages test runs."""

    def __init__(self, session):
        """Initialize the protocol executor.

        Args:
            session: Database session.
        """
        self.session = session

    def create_test_run(
        self,
        protocol: Protocol,
        specimen_id: str,
        operator_name: Optional[str] = None,
        **kwargs
    ) -> TestRun:
        """Create a new test run for a protocol.

        Args:
            protocol: The Protocol object to execute.
            specimen_id: Identifier for the test specimen.
            operator_name: Name of the operator running the test.
            **kwargs: Additional test run parameters (manufacturer, model_number, etc.).

        Returns:
            The created TestRun object.
        """
        run_id = f"{protocol.protocol_id}-{uuid.uuid4().hex[:8]}"

        test_run = TestRun(
            run_id=run_id,
            protocol_id=protocol.id,
            specimen_id=specimen_id,
            specimen_description=kwargs.get("specimen_description"),
            manufacturer=kwargs.get("manufacturer"),
            model_number=kwargs.get("model_number"),
            serial_number=kwargs.get("serial_number"),
            operator_name=operator_name,
            facility=kwargs.get("facility"),
            test_station=kwargs.get("test_station"),
            ambient_temperature=kwargs.get("ambient_temperature"),
            ambient_humidity=kwargs.get("ambient_humidity"),
            status=TestStatus.PENDING,
            result=TestResult.NOT_EVALUATED,
        )

        self.session.add(test_run)
        self.session.commit()

        # Create test steps from protocol
        self._initialize_test_steps(test_run, protocol)

        return test_run

    def _initialize_test_steps(self, test_run: TestRun, protocol: Protocol):
        """Initialize test steps for a test run from the protocol.

        Args:
            test_run: The TestRun object.
            protocol: The Protocol object containing step definitions.
        """
        protocol_data = protocol.protocol_data
        test_steps_data = protocol_data.get("test_steps", [])

        for step_data in test_steps_data:
            test_step = TestStep(
                test_run_id=test_run.id,
                step_number=step_data["step_number"],
                description=step_data["description"],
                action=step_data["action"],
                status=TestStatus.PENDING,
            )
            self.session.add(test_step)

        self.session.commit()

    def start_test_run(self, test_run: TestRun) -> TestRun:
        """Start a test run.

        Args:
            test_run: The TestRun object to start.

        Returns:
            The updated TestRun object.
        """
        test_run.status = TestStatus.IN_PROGRESS
        test_run.started_at = datetime.utcnow()
        self.session.commit()
        return test_run

    def complete_test_run(self, test_run: TestRun, result: TestResult) -> TestRun:
        """Complete a test run.

        Args:
            test_run: The TestRun object to complete.
            result: The final test result.

        Returns:
            The updated TestRun object.
        """
        test_run.status = TestStatus.COMPLETED
        test_run.result = result
        test_run.completed_at = datetime.utcnow()
        self.session.commit()
        return test_run

    def abort_test_run(self, test_run: TestRun, reason: str) -> TestRun:
        """Abort a test run.

        Args:
            test_run: The TestRun object to abort.
            reason: Reason for aborting the test.

        Returns:
            The updated TestRun object.
        """
        test_run.status = TestStatus.ABORTED
        test_run.notes = f"{test_run.notes or ''}\nAborted: {reason}"
        test_run.completed_at = datetime.utcnow()
        self.session.commit()
        return test_run

    def start_step(self, test_step: TestStep) -> TestStep:
        """Start a test step.

        Args:
            test_step: The TestStep object to start.

        Returns:
            The updated TestStep object.
        """
        test_step.status = TestStatus.IN_PROGRESS
        test_step.started_at = datetime.utcnow()
        self.session.commit()
        return test_step

    def complete_step(
        self,
        test_step: TestStep,
        observations: Optional[str] = None,
        step_data: Optional[Dict[str, Any]] = None,
        pass_fail: Optional[bool] = None
    ) -> TestStep:
        """Complete a test step.

        Args:
            test_step: The TestStep object to complete.
            observations: Optional observations or notes for the step.
            step_data: Optional data collected during the step.
            pass_fail: Optional pass/fail status for the step.

        Returns:
            The updated TestStep object.
        """
        test_step.status = TestStatus.COMPLETED
        test_step.completed_at = datetime.utcnow()

        if observations:
            test_step.observations = observations

        if step_data:
            test_step.step_data = step_data

        if pass_fail is not None:
            test_step.pass_fail = pass_fail

        self.session.commit()
        return test_step

    def record_measurement(
        self,
        test_run: TestRun,
        measurement_id: str,
        parameter: str,
        value: Any,
        measurement_type: str = "during_test",
        **kwargs
    ) -> Measurement:
        """Record a measurement for a test run.

        Args:
            test_run: The TestRun object.
            measurement_id: Identifier for the measurement (e.g., 'M-001').
            parameter: The parameter being measured.
            value: The measured value.
            measurement_type: Type of measurement (pre_test, during_test, post_test).
            **kwargs: Additional measurement parameters (unit, instrument, etc.).

        Returns:
            The created Measurement object.
        """
        measurement = Measurement(
            test_run_id=test_run.id,
            measurement_id=measurement_id,
            parameter=parameter,
            measurement_type=measurement_type,
            unit=kwargs.get("unit"),
            instrument=kwargs.get("instrument"),
            accuracy=kwargs.get("accuracy"),
            measured_at=kwargs.get("measured_at", datetime.utcnow()),
        )

        # Store value in appropriate field based on type
        if isinstance(value, bool):
            measurement.value_boolean = value
        elif isinstance(value, (int, float)):
            measurement.value_numeric = float(value)
        elif isinstance(value, str):
            measurement.value_text = value
        elif isinstance(value, (list, dict)):
            measurement.value_json = value
        else:
            measurement.value_text = str(value)

        self.session.add(measurement)
        self.session.commit()

        return measurement

    def evaluate_acceptance_criteria(self, test_run: TestRun, protocol: Protocol) -> TestResult:
        """Evaluate acceptance criteria for a test run.

        Args:
            test_run: The TestRun object.
            protocol: The Protocol object containing acceptance criteria.

        Returns:
            The evaluated test result (PASS, FAIL, or CONDITIONAL).
        """
        protocol_data = protocol.protocol_data
        criteria = protocol_data.get("acceptance_criteria", [])

        all_pass = True
        any_fail = False

        for criterion in criteria:
            criterion_id = criterion["criterion_id"]
            evaluation_method = criterion["evaluation_method"]

            # Get the threshold
            threshold = criterion.get("threshold", {})
            parameter = threshold.get("parameter")
            operator = threshold.get("operator")
            expected_value = threshold.get("value")

            # Retrieve the actual measurement or observation
            if evaluation_method == "measurement" or evaluation_method == "calculation":
                # Find the measurement
                measurement = self.session.query(Measurement).filter_by(
                    test_run_id=test_run.id,
                    parameter=parameter
                ).first()

                if measurement:
                    actual_value = measurement.value_numeric or measurement.value_text

                    # Evaluate based on operator
                    result = self._evaluate_threshold(actual_value, operator, expected_value)

                    if not result:
                        any_fail = True
                        all_pass = False
                else:
                    # Measurement not found - treat as conditional
                    all_pass = False

            elif evaluation_method == "visual":
                # Visual inspections need to be manually evaluated
                # For now, we'll treat them as conditional
                pass

        if any_fail:
            return TestResult.FAIL
        elif all_pass:
            return TestResult.PASS
        else:
            return TestResult.CONDITIONAL

    def _evaluate_threshold(self, actual_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a threshold comparison.

        Args:
            actual_value: The actual measured value.
            operator: The comparison operator (>, <, >=, <=, ==, !=, between).
            expected_value: The expected value or threshold.

        Returns:
            True if the condition is met, False otherwise.
        """
        try:
            if operator == ">":
                return float(actual_value) > float(expected_value)
            elif operator == ">=":
                return float(actual_value) >= float(expected_value)
            elif operator == "<":
                return float(actual_value) < float(expected_value)
            elif operator == "<=":
                return float(actual_value) <= float(expected_value)
            elif operator == "==":
                return actual_value == expected_value
            elif operator == "!=":
                return actual_value != expected_value
            elif operator == "between":
                if isinstance(expected_value, list) and len(expected_value) == 2:
                    return expected_value[0] <= float(actual_value) <= expected_value[1]
        except (ValueError, TypeError):
            return False

        return False

    def get_test_run_summary(self, test_run: TestRun) -> Dict[str, Any]:
        """Get a summary of a test run.

        Args:
            test_run: The TestRun object.

        Returns:
            Dictionary containing test run summary.
        """
        # Count completed steps
        total_steps = len(test_run.test_steps)
        completed_steps = sum(1 for step in test_run.test_steps if step.status == TestStatus.COMPLETED)

        # Get all measurements
        measurements = {m.parameter: m.to_dict() for m in test_run.measurements}

        return {
            "test_run": test_run.to_dict(),
            "progress": {
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
            },
            "measurements": measurements,
            "steps": [step.to_dict() for step in test_run.test_steps]
        }
