"""
Protocol handler for executing and managing test protocols.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from .models import (
    Protocol,
    ProtocolResult,
    ProtocolStatus,
    Measurement,
    MeasurementStatus,
)


class ProtocolHandler:
    """Handles protocol execution and management."""

    def __init__(self):
        """Initialize protocol handler."""
        self.current_protocol: Optional[Protocol] = None
        self.results_history: list = []

    def load_protocol(self, protocol_data: Dict[str, Any]) -> Protocol:
        """
        Load protocol from dictionary data.

        Args:
            protocol_data: Protocol data as dictionary

        Returns:
            Protocol instance

        Raises:
            ValueError: If protocol data is invalid
        """
        try:
            protocol = Protocol(**protocol_data)
            self.current_protocol = protocol
            logger.info(f"Loaded protocol: {protocol.protocol_id}")
            return protocol
        except Exception as e:
            logger.error(f"Failed to load protocol: {e}")
            raise ValueError(f"Invalid protocol data: {e}")

    def load_protocol_from_file(self, file_path: Path) -> Protocol:
        """
        Load protocol from JSON file.

        Args:
            file_path: Path to protocol JSON file

        Returns:
            Protocol instance
        """
        try:
            with open(file_path, "r") as f:
                protocol_data = json.load(f)
            return self.load_protocol(protocol_data)
        except FileNotFoundError:
            logger.error(f"Protocol file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in protocol file: {e}")
            raise ValueError(f"Invalid JSON: {e}")

    def execute_protocol(
        self, protocol: Optional[Protocol] = None
    ) -> ProtocolResult:
        """
        Execute a protocol and return results.

        Args:
            protocol: Protocol to execute (uses current_protocol if None)

        Returns:
            ProtocolResult with execution details
        """
        if protocol is None:
            protocol = self.current_protocol

        if protocol is None:
            raise ValueError("No protocol loaded")

        logger.info(f"Executing protocol: {protocol.protocol_id}")
        start_time = time.time()

        try:
            # Update protocol status
            protocol.status = ProtocolStatus.IN_PROGRESS

            # Validate protocol before execution
            validation_errors = self._validate_protocol(protocol)
            if validation_errors:
                logger.error(f"Protocol validation failed: {validation_errors}")
                return ProtocolResult(
                    protocol_id=protocol.protocol_id,
                    status=ProtocolStatus.FAILED,
                    passed=False,
                    errors=validation_errors,
                    execution_time=time.time() - start_time,
                )

            # Execute protocol (placeholder for actual implementation)
            measurements = self._execute_measurements(protocol)

            # Evaluate acceptance criteria
            passed, errors, warnings = self._evaluate_criteria(
                protocol, measurements
            )

            # Create result
            execution_time = time.time() - start_time
            result = ProtocolResult(
                protocol_id=protocol.protocol_id,
                status=ProtocolStatus.COMPLETED if passed else ProtocolStatus.FAILED,
                passed=passed,
                measurements=measurements,
                errors=errors,
                warnings=warnings,
                execution_time=execution_time,
                completed_at=datetime.now(),
            )

            # Update protocol status
            protocol.status = result.status
            protocol.measurements = measurements

            # Store result in history
            self.results_history.append(result)

            logger.info(
                f"Protocol {protocol.protocol_id} completed: "
                f"{'PASS' if passed else 'FAIL'} in {execution_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Protocol execution failed: {e}")
            protocol.status = ProtocolStatus.FAILED
            return ProtocolResult(
                protocol_id=protocol.protocol_id,
                status=ProtocolStatus.FAILED,
                passed=False,
                errors=[str(e)],
                execution_time=time.time() - start_time,
            )

    def _validate_protocol(self, protocol: Protocol) -> list:
        """
        Validate protocol before execution.

        Args:
            protocol: Protocol to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check required parameters
        if not protocol.parameters:
            errors.append("Protocol parameters are empty")

        # Check module_id if required
        if protocol.parameters.get("module_id") == "":
            errors.append("module_id is required but empty")

        return errors

    def _execute_measurements(self, protocol: Protocol) -> list:
        """
        Execute protocol measurements (placeholder).

        Args:
            protocol: Protocol to execute

        Returns:
            List of measurements
        """
        # This is a placeholder implementation
        # In a real system, this would interface with actual test equipment
        measurements = []

        # Generate sample measurements based on protocol type
        if protocol.protocol_type == "electrical":
            measurements.append(
                Measurement(
                    measurement_id="M001",
                    parameter="voltage",
                    value=24.5,
                    unit="V",
                    timestamp=datetime.now(),
                    status=MeasurementStatus.PASS,
                )
            )
            measurements.append(
                Measurement(
                    measurement_id="M002",
                    parameter="current",
                    value=8.2,
                    unit="A",
                    timestamp=datetime.now(),
                    status=MeasurementStatus.PASS,
                )
            )

        return measurements

    def _evaluate_criteria(
        self, protocol: Protocol, measurements: list
    ) -> tuple:
        """
        Evaluate acceptance criteria against measurements.

        Args:
            protocol: Protocol with acceptance criteria
            measurements: List of measurements

        Returns:
            Tuple of (passed, errors, warnings)
        """
        passed = True
        errors = []
        warnings = []

        if not protocol.acceptance_criteria:
            warnings.append("No acceptance criteria defined")
            return passed, errors, warnings

        # Evaluate each criterion (simplified implementation)
        criteria = protocol.acceptance_criteria

        # Check for failed measurements
        failed_measurements = [
            m for m in measurements if m.status == MeasurementStatus.FAIL
        ]
        if failed_measurements:
            passed = False
            errors.append(
                f"{len(failed_measurements)} measurement(s) failed criteria"
            )

        return passed, errors, warnings

    def get_result_history(self) -> list:
        """
        Get protocol execution history.

        Returns:
            List of ProtocolResult objects
        """
        return self.results_history

    def save_result(self, result: ProtocolResult, output_dir: Path):
        """
        Save protocol result to file.

        Args:
            result: ProtocolResult to save
            output_dir: Directory to save results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.protocol_id}_{timestamp}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(result.dict(), f, indent=2, default=str)

        logger.info(f"Result saved to: {filepath}")
