"""Test executor for running test protocols."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from ..models.protocol import Protocol, TestStage, MeasurementType, ComparisonOperator
from ..models.test_result import (
    TestSession,
    TestResult,
    TestStatus,
    PassFailStatus,
    MeasurementData,
    QCCheckResult,
    CriterionEvaluation,
    Sample
)


class TestExecutor:
    """Executes test protocols and manages test sessions."""

    def __init__(self, protocol: Protocol):
        """Initialize test executor with a protocol.

        Args:
            protocol: Protocol definition to execute
        """
        self.protocol = protocol
        self.session: Optional[TestSession] = None

    def start_session(
        self,
        operator_id: Optional[str] = None,
        operator_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        samples: Optional[List[Sample]] = None
    ) -> TestSession:
        """Start a new test session.

        Args:
            operator_id: Operator identifier
            operator_name: Operator name
            parameters: Test parameters
            samples: List of samples to test

        Returns:
            TestSession object

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if parameters:
            is_valid, errors = self.protocol.validate_parameters(parameters)
            if not is_valid:
                raise ValueError(f"Invalid parameters: {'; '.join(errors)}")

        # Create session
        self.session = TestSession(
            protocol_id=self.protocol.id,
            protocol_version=self.protocol.version,
            operator_id=operator_id,
            operator_name=operator_name,
            status=TestStatus.IN_PROGRESS,
            parameters=parameters or {},
            samples=samples or []
        )

        return self.session

    def add_measurement(
        self,
        measurement_id: str,
        data: Any,
        unit: Optional[str] = None,
        operator: Optional[str] = None,
        notes: Optional[str] = None
    ) -> MeasurementData:
        """Add a measurement to the current session.

        Args:
            measurement_id: Measurement identifier from protocol
            data: Measurement data
            unit: Unit of measurement
            operator: Operator who performed measurement
            notes: Additional notes

        Returns:
            MeasurementData object

        Raises:
            ValueError: If session not started or measurement ID invalid
        """
        if not self.session:
            raise ValueError("No active session. Call start_session() first.")

        # Validate measurement ID
        measurement_def = self.protocol.get_measurement_by_id(measurement_id)
        if not measurement_def:
            raise ValueError(f"Invalid measurement ID: {measurement_id}")

        # Create measurement data
        measurement = MeasurementData(
            measurement_id=measurement_id,
            measurement_name=measurement_def.name,
            measurement_type=measurement_def.type,
            stage=measurement_def.stage,
            data=data,
            unit=unit,
            operator=operator,
            notes=notes
        )

        self.session.add_measurement(measurement)
        return measurement

    def add_qc_check(
        self,
        check_id: str,
        result: PassFailStatus,
        details: Optional[Dict[str, Any]] = None,
        performed_by: Optional[str] = None
    ) -> QCCheckResult:
        """Add a quality control check result.

        Args:
            check_id: QC check identifier from protocol
            result: Pass/fail status
            details: Additional details
            performed_by: Person who performed check

        Returns:
            QCCheckResult object

        Raises:
            ValueError: If session not started or check ID invalid
        """
        if not self.session:
            raise ValueError("No active session. Call start_session() first.")

        # Find QC check definition
        qc_def = None
        if self.protocol.quality_controls:
            for qc in self.protocol.quality_controls:
                if qc.id == check_id:
                    qc_def = qc
                    break

        if not qc_def:
            raise ValueError(f"Invalid QC check ID: {check_id}")

        # Create QC check result
        qc_check = QCCheckResult(
            check_id=check_id,
            check_name=qc_def.name,
            stage=qc_def.stage,
            result=result,
            details=details,
            performed_by=performed_by
        )

        self.session.add_qc_check(qc_check)
        return qc_check

    def complete_session(self) -> TestSession:
        """Complete the current test session.

        Returns:
            Completed TestSession object

        Raises:
            ValueError: If session not started
        """
        if not self.session:
            raise ValueError("No active session.")

        self.session.complete_session()
        return self.session

    def evaluate_results(self) -> TestResult:
        """Evaluate test results against pass criteria.

        Returns:
            TestResult object with evaluation

        Raises:
            ValueError: If session not started or not completed
        """
        if not self.session:
            raise ValueError("No active session.")

        if self.session.status != TestStatus.COMPLETED:
            raise ValueError("Session must be completed before evaluation.")

        # Create test result
        result = TestResult(
            session=self.session,
            overall_status=PassFailStatus.NOT_EVALUATED
        )

        # Evaluate each criterion
        for criterion_name, criterion in self.protocol.pass_criteria.items():
            evaluation = self._evaluate_criterion(criterion_name, criterion)
            result.add_criterion_evaluation(evaluation)

        # Determine overall status
        result.evaluate_overall_status()

        return result

    def _evaluate_criterion(self, criterion_name: str, criterion: Any) -> CriterionEvaluation:
        """Evaluate a single pass criterion.

        Args:
            criterion_name: Name of the criterion
            criterion: Criterion definition

        Returns:
            CriterionEvaluation object
        """
        evaluation = CriterionEvaluation(
            criterion_name=criterion_name,
            status=PassFailStatus.NOT_EVALUATED,
            description=criterion.description if hasattr(criterion, 'description') else None
        )

        # Handle power degradation criterion
        if criterion_name == "power_degradation":
            evaluation = self._evaluate_power_degradation(criterion)

        # Handle visual defects criterion
        elif criterion_name == "visual_defects":
            evaluation = self._evaluate_visual_defects(criterion)

        # Handle insulation resistance criterion
        elif criterion_name == "insulation_resistance":
            evaluation = self._evaluate_insulation_resistance(criterion)

        # Handle electrical parameters criterion
        elif criterion_name == "electrical_parameters":
            evaluation = self._evaluate_electrical_parameters(criterion)

        # Generic numeric criterion
        else:
            evaluation = self._evaluate_numeric_criterion(criterion_name, criterion)

        return evaluation

    def _evaluate_power_degradation(self, criterion: Any) -> CriterionEvaluation:
        """Evaluate power degradation criterion."""
        # Get pre-test and post-test power measurements
        pre_power = self._get_electrical_parameter("Pmax", TestStage.PRE_TEST)
        post_power = self._get_electrical_parameter("Pmax", TestStage.POST_TEST)

        if pre_power is None or post_power is None:
            return CriterionEvaluation(
                criterion_name="power_degradation",
                status=PassFailStatus.NOT_EVALUATED,
                description="Missing power measurements"
            )

        # Calculate degradation percentage
        degradation = ((pre_power - post_power) / pre_power) * 100

        # Evaluate against limit
        max_degradation = criterion.max
        status = PassFailStatus.PASS if degradation <= max_degradation else PassFailStatus.FAIL

        return CriterionEvaluation(
            criterion_name="power_degradation",
            status=status,
            measured_value=degradation,
            limit_value=max_degradation,
            unit="percent",
            description=f"Power degradation: {degradation:.2f}% (limit: {max_degradation}%)",
            details={
                "pre_test_power": pre_power,
                "post_test_power": post_power
            }
        )

    def _evaluate_visual_defects(self, criterion: Any) -> CriterionEvaluation:
        """Evaluate visual defects criterion."""
        # Get post-test visual inspection
        visual_inspection = self.session.get_measurement_by_id("visual_inspection_post")

        if not visual_inspection:
            return CriterionEvaluation(
                criterion_name="visual_defects",
                status=PassFailStatus.NOT_EVALUATED,
                description="Missing visual inspection data"
            )

        # Check for critical defects
        critical_defects = criterion.critical_defects
        found_defects = []

        if isinstance(visual_inspection.data, dict):
            for defect in critical_defects:
                if visual_inspection.data.get(defect, False):
                    found_defects.append(defect)

        # Evaluate
        status = PassFailStatus.PASS if len(found_defects) == 0 else PassFailStatus.FAIL

        return CriterionEvaluation(
            criterion_name="visual_defects",
            status=status,
            description=f"Found {len(found_defects)} critical defects",
            details={
                "critical_defects_found": found_defects,
                "all_critical_defects": critical_defects
            }
        )

    def _evaluate_insulation_resistance(self, criterion: Any) -> CriterionEvaluation:
        """Evaluate insulation resistance criterion."""
        # Get insulation resistance measurement
        measurement = self.session.get_measurement_by_id("insulation_resistance")

        if not measurement:
            return CriterionEvaluation(
                criterion_name="insulation_resistance",
                status=PassFailStatus.NOT_EVALUATED,
                description="Missing insulation resistance data"
            )

        # Extract R_insulation value
        r_insulation = None
        if isinstance(measurement.data, dict):
            r_insulation = measurement.data.get("R_insulation")
        elif isinstance(measurement.data, (int, float)):
            r_insulation = measurement.data

        if r_insulation is None:
            return CriterionEvaluation(
                criterion_name="insulation_resistance",
                status=PassFailStatus.NOT_EVALUATED,
                description="Invalid insulation resistance data"
            )

        # Evaluate against minimum
        min_value = criterion.min
        status = PassFailStatus.PASS if r_insulation >= min_value else PassFailStatus.FAIL

        return CriterionEvaluation(
            criterion_name="insulation_resistance",
            status=status,
            measured_value=r_insulation,
            limit_value=min_value,
            unit=criterion.unit,
            description=f"Insulation resistance: {r_insulation} {criterion.unit} (min: {min_value} {criterion.unit})"
        )

    def _evaluate_electrical_parameters(self, criterion: Any) -> CriterionEvaluation:
        """Evaluate electrical parameters degradation."""
        # Check each parameter
        parameters = ["Voc", "Isc", "FF"]
        failed_parameters = []

        for param in parameters:
            pre_value = self._get_electrical_parameter(param, TestStage.PRE_TEST)
            post_value = self._get_electrical_parameter(param, TestStage.POST_TEST)

            if pre_value is not None and post_value is not None:
                degradation = ((pre_value - post_value) / pre_value) * 100
                max_degradation = getattr(criterion, f"{param}_degradation_max", 5.0)

                if degradation > max_degradation:
                    failed_parameters.append({
                        "parameter": param,
                        "degradation": degradation,
                        "limit": max_degradation
                    })

        status = PassFailStatus.PASS if len(failed_parameters) == 0 else PassFailStatus.FAIL

        return CriterionEvaluation(
            criterion_name="electrical_parameters",
            status=status,
            description=f"{len(failed_parameters)} parameters exceeded degradation limits",
            details={"failed_parameters": failed_parameters}
        )

    def _evaluate_numeric_criterion(self, criterion_name: str, criterion: Any) -> CriterionEvaluation:
        """Evaluate generic numeric criterion."""
        # This is a placeholder for custom criteria
        return CriterionEvaluation(
            criterion_name=criterion_name,
            status=PassFailStatus.NOT_EVALUATED,
            description="Custom criterion evaluation not implemented"
        )

    def _get_electrical_parameter(self, parameter: str, stage: TestStage) -> Optional[float]:
        """Get electrical parameter value from measurements.

        Args:
            parameter: Parameter name (e.g., 'Pmax', 'Voc')
            stage: Test stage (pre_test or post_test)

        Returns:
            Parameter value or None if not found
        """
        # Determine measurement ID based on stage
        measurement_id = f"electrical_performance_{stage.value.split('_')[-1]}"

        measurement = self.session.get_measurement_by_id(measurement_id)

        if not measurement or not isinstance(measurement.data, dict):
            return None

        return measurement.data.get(parameter)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session.

        Returns:
            Dictionary with session summary
        """
        if not self.session:
            return {}

        return {
            "session_id": str(self.session.session_id),
            "protocol_id": self.session.protocol_id,
            "protocol_version": self.session.protocol_version,
            "status": self.session.status.value,
            "start_time": self.session.start_time.isoformat(),
            "end_time": self.session.end_time.isoformat() if self.session.end_time else None,
            "operator": self.session.operator_name or self.session.operator_id,
            "sample_count": len(self.session.samples),
            "measurement_count": len(self.session.measurements),
            "qc_check_count": len(self.session.qc_checks)
        }
