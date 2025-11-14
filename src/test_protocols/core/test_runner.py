"""Test runner for executing protocol tests."""

from typing import Dict, Any, Optional, Type
from datetime import datetime
import pandas as pd
from pathlib import Path
import logging

from ..protocols.base_protocol import BaseProtocol


class TestRunner:
    """Manages test execution for protocols."""

    def __init__(self, protocol: BaseProtocol, logger: Optional[logging.Logger] = None):
        """
        Initialize test runner.

        Args:
            protocol: Protocol instance to run
            logger: Optional logger for test execution
        """
        self.protocol = protocol
        self.logger = logger or logging.getLogger(__name__)
        self.session_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status: str = "initialized"

    def run(
        self,
        data: pd.DataFrame,
        validate_inputs: bool = True,
        run_qc: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute test protocol.

        Args:
            data: Test measurement data
            validate_inputs: Whether to validate inputs before running
            run_qc: Whether to run quality checks

        Returns:
            Dictionary containing test results
        """
        self.session_id = self._generate_session_id()
        self.start_time = datetime.now()
        self.status = "running"

        self.logger.info(f"Starting test session {self.session_id}")
        self.logger.info(f"Protocol: {self.protocol.PROTOCOL_ID} v{self.protocol.VERSION}")

        try:
            # Validate inputs
            if validate_inputs:
                self.logger.info("Validating inputs...")
                is_valid, errors = self.protocol.validate_inputs(data.to_dict())
                if not is_valid:
                    self.status = "failed"
                    self.logger.error(f"Input validation failed: {errors}")
                    return {
                        "session_id": self.session_id,
                        "status": "failed",
                        "error": "Input validation failed",
                        "validation_errors": errors,
                        "start_time": self.start_time.isoformat(),
                    }

            # Run the test
            self.logger.info("Executing test protocol...")
            results = self.protocol.run_test(data)

            # Add session metadata
            results["session_id"] = self.session_id
            results["protocol_id"] = self.protocol.PROTOCOL_ID
            results["protocol_version"] = self.protocol.VERSION
            results["start_time"] = self.start_time.isoformat()

            self.end_time = datetime.now()
            results["end_time"] = self.end_time.isoformat()
            results["duration_seconds"] = (self.end_time - self.start_time).total_seconds()

            # Determine overall status based on QC results
            if run_qc and "qc_results" in results:
                qc_errors = [qc for qc in results["qc_results"]
                           if not qc["passed"] and qc["severity"] == "error"]
                if qc_errors:
                    self.status = "completed_with_errors"
                    results["status"] = "completed_with_errors"
                else:
                    self.status = "completed"
                    results["status"] = "completed"
            else:
                self.status = "completed"
                results["status"] = "completed"

            self.logger.info(f"Test completed with status: {self.status}")

            return results

        except Exception as e:
            self.status = "failed"
            self.end_time = datetime.now()
            self.logger.error(f"Test execution failed: {str(e)}", exc_info=True)

            return {
                "session_id": self.session_id,
                "status": "failed",
                "error": str(e),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
            }

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.protocol.PROTOCOL_ID}_{timestamp}"

    def get_status(self) -> Dict[str, Any]:
        """Get current test session status."""
        return {
            "session_id": self.session_id,
            "protocol_id": self.protocol.PROTOCOL_ID,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time
                else None
            ),
        }


class TestBatch:
    """Manages batch execution of multiple tests."""

    def __init__(self, protocol_class: Type[BaseProtocol]):
        """
        Initialize batch test runner.

        Args:
            protocol_class: Protocol class to use for all tests
        """
        self.protocol_class = protocol_class
        self.results: list[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def add_test(self, data: pd.DataFrame, test_id: str = None) -> None:
        """
        Add a test to the batch.

        Args:
            data: Test data
            test_id: Optional test identifier
        """
        test_id = test_id or f"test_{len(self.results) + 1}"
        self.results.append({"test_id": test_id, "data": data, "status": "pending"})

    def run_batch(self, parallel: bool = False) -> list[Dict[str, Any]]:
        """
        Run all tests in batch.

        Args:
            parallel: Whether to run tests in parallel (not yet implemented)

        Returns:
            List of test results
        """
        self.logger.info(f"Running batch of {len(self.results)} tests")

        batch_results = []

        for i, test in enumerate(self.results):
            self.logger.info(f"Running test {i+1}/{len(self.results)}: {test['test_id']}")

            protocol = self.protocol_class()
            runner = TestRunner(protocol, self.logger)

            result = runner.run(test["data"])
            result["test_id"] = test["test_id"]

            batch_results.append(result)

        self.logger.info(f"Batch execution completed. {len(batch_results)} tests run.")

        return batch_results

    def export_batch_results(self, output_dir: str) -> None:
        """
        Export batch results to directory.

        Args:
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        import json

        for result in self.results:
            if "session_id" in result:
                filename = f"{result['session_id']}.json"
                with open(output_path / filename, "w") as f:
                    json.dump(result, f, indent=2, default=str)

        self.logger.info(f"Batch results exported to {output_dir}")
