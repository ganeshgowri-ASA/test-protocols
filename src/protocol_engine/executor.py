"""Protocol executor for running test protocols and managing execution flow."""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging

from .loader import ProtocolLoader
from .validator import ProtocolValidator, ValidationError


logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Custom exception for protocol execution errors."""
    pass


class ProtocolExecutor:
    """Execute test protocols and manage execution flow."""

    def __init__(
        self,
        protocol_id: str,
        loader: Optional[ProtocolLoader] = None,
        validator: Optional[ProtocolValidator] = None
    ) -> None:
        """Initialize the protocol executor.

        Args:
            protocol_id: Protocol identifier (e.g., 'iam-001')
            loader: Protocol loader instance
            validator: Protocol validator instance
        """
        self.protocol_id = protocol_id
        self.loader = loader or ProtocolLoader()

        # Load schema and config
        self.schema = self.loader.load_schema(protocol_id)
        self.config = self.loader.load_config(protocol_id)

        # Initialize validator
        self.validator = validator or ProtocolValidator(self.schema)

        # Execution state
        self.protocol_data: Optional[Dict[str, Any]] = None
        self.execution_log: List[Dict[str, Any]] = []

    def load_protocol(self, file_path: Path) -> None:
        """Load a protocol from file.

        Args:
            file_path: Path to protocol JSON file

        Raises:
            ValidationError: If protocol is invalid
        """
        self.protocol_data = self.loader.load_protocol(file_path)

        # Validate loaded protocol
        try:
            self.validator.validate_strict(self.protocol_data)
        except ValidationError as e:
            logger.error(f"Protocol validation failed: {e}")
            raise

        self._log_event("protocol_loaded", {"file": str(file_path)})

    def create_protocol(self, **overrides: Any) -> None:
        """Create a new protocol from template.

        Args:
            **overrides: Key-value pairs to override template values
        """
        self.protocol_data = self.loader.create_from_template(
            self.protocol_id,
            **overrides
        )

        self._log_event("protocol_created", {"protocol_id": self.protocol_id})

    def add_measurement(
        self,
        angle: float,
        isc: float,
        voc: float,
        pmax: float,
        **kwargs: Any
    ) -> None:
        """Add a measurement to the protocol.

        Args:
            angle: Angle of incidence in degrees
            isc: Short-circuit current in amperes
            voc: Open-circuit voltage in volts
            pmax: Maximum power in watts
            **kwargs: Additional measurement parameters
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded. Call load_protocol() or create_protocol() first.")

        measurement = {
            "angle": angle,
            "isc": isc,
            "voc": voc,
            "pmax": pmax,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **kwargs
        }

        # Add to measurements array
        if "measurements" not in self.protocol_data:
            self.protocol_data["measurements"] = []

        self.protocol_data["measurements"].append(measurement)

        self._log_event("measurement_added", {"angle": angle, "pmax": pmax})

    def validate_protocol(self) -> Dict[str, Any]:
        """Validate the current protocol data.

        Returns:
            Validation results dictionary

        Raises:
            ExecutionError: If no protocol loaded
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        validation_results = self.validator.validate_all(
            self.protocol_data,
            self.config
        )

        self._log_event("validation_completed", {
            "status": validation_results["overall_status"],
            "errors": len(validation_results["errors"]),
            "warnings": len(validation_results["warnings"])
        })

        return validation_results

    def execute_analysis(self, analysis_function: Callable) -> None:
        """Execute analysis on the protocol data.

        Args:
            analysis_function: Function that takes protocol_data and config,
                             returns analysis results to be stored in protocol_data

        Raises:
            ExecutionError: If no protocol loaded or analysis fails
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        try:
            analysis_results = analysis_function(self.protocol_data, self.config)

            # Store results in protocol data
            if "analysis_results" not in self.protocol_data:
                self.protocol_data["analysis_results"] = {}

            self.protocol_data["analysis_results"].update(analysis_results)

            self._log_event("analysis_completed", {"results": list(analysis_results.keys())})

        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            raise ExecutionError(f"Analysis failed: {e}") from e

    def save_protocol(self, file_path: Path) -> None:
        """Save the protocol to file.

        Args:
            file_path: Path where to save the protocol

        Raises:
            ExecutionError: If no protocol loaded
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        self.loader.save_protocol(self.protocol_data, file_path)

        self._log_event("protocol_saved", {"file": str(file_path)})

    def get_protocol_data(self) -> Dict[str, Any]:
        """Get the current protocol data.

        Returns:
            Protocol data dictionary

        Raises:
            ExecutionError: If no protocol loaded
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        return self.protocol_data

    def get_measurements(self) -> List[Dict[str, Any]]:
        """Get all measurements from the protocol.

        Returns:
            List of measurement dictionaries

        Raises:
            ExecutionError: If no protocol loaded
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        return self.protocol_data.get("measurements", [])

    def get_analysis_results(self) -> Dict[str, Any]:
        """Get analysis results from the protocol.

        Returns:
            Analysis results dictionary

        Raises:
            ExecutionError: If no protocol loaded
        """
        if self.protocol_data is None:
            raise ExecutionError("No protocol loaded")

        return self.protocol_data.get("analysis_results", {})

    def clear(self) -> None:
        """Clear the current protocol data and execution log."""
        self.protocol_data = None
        self.execution_log = []

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log.

        Returns:
            List of execution log entries
        """
        return self.execution_log.copy()

    def _log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log an execution event.

        Args:
            event_type: Type of event
            details: Event details dictionary
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details
        }
        self.execution_log.append(log_entry)
        logger.info(f"{event_type}: {details}")

    def get_recommended_angles(self) -> List[float]:
        """Get recommended test angles from configuration.

        Returns:
            List of recommended angles in degrees
        """
        return self.config.get("default_settings", {}).get(
            "recommended_angles",
            [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        )

    def get_test_configuration(self) -> Dict[str, Any]:
        """Get test configuration parameters.

        Returns:
            Test configuration dictionary
        """
        if self.protocol_data is None:
            # Return defaults from config
            return self.config.get("default_settings", {})

        return self.protocol_data.get("test_configuration", {})
