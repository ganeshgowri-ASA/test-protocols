"""Base protocol class for all test protocols."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml


class BaseProtocol:
    """
    Base class for all test protocol implementations.

    This provides common functionality for loading protocol definitions,
    validating data, and managing test execution.
    """

    def __init__(self, protocol_id: str, config_path: Optional[str] = None):
        """
        Initialize the protocol.

        Args:
            protocol_id: Protocol identifier (e.g., "LID-001")
            config_path: Path to configuration file
        """
        self.protocol_id = protocol_id
        self.definition = self._load_protocol_definition()
        self.config = self._load_config(config_path)

    def _load_protocol_definition(self) -> Dict[str, Any]:
        """
        Load protocol definition from JSON file.

        Returns:
            Protocol definition dictionary
        """
        # Determine protocol definition path
        protocol_file = Path(__file__).parent.parent / "definitions" / f"{self.protocol_id}.json"

        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol definition not found: {protocol_file}")

        with open(protocol_file, 'r') as f:
            definition = json.load(f)

        return definition

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        return config

    def get_protocol_info(self) -> Dict[str, Any]:
        """
        Get protocol metadata.

        Returns:
            Protocol information dictionary
        """
        return {
            "protocol_id": self.definition.get("protocol_id"),
            "protocol_name": self.definition.get("protocol_name"),
            "version": self.definition.get("version"),
            "category": self.definition.get("category"),
            "description": self.definition.get("description"),
            "standards": self.definition.get("standards", []),
        }

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get test parameters.

        Returns:
            Parameters dictionary
        """
        return self.definition.get("parameters", {})

    def get_measurements_spec(self) -> Dict[str, Any]:
        """
        Get measurement specifications.

        Returns:
            Measurements specification dictionary
        """
        return self.definition.get("measurements", {})

    def get_qc_criteria(self) -> Dict[str, Any]:
        """
        Get QC criteria.

        Returns:
            QC criteria dictionary
        """
        return self.definition.get("qc_criteria", {})

    def get_required_fields(self) -> List[str]:
        """
        Get list of required measurement fields.

        Returns:
            List of required field names
        """
        measurements = self.definition.get("measurements", {})
        return measurements.get("required_fields", [])

    def get_field_definition(self, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get definition for a specific field.

        Args:
            field_name: Name of the field

        Returns:
            Field definition dictionary or None
        """
        measurements = self.definition.get("measurements", {})
        field_defs = measurements.get("field_definitions", {})
        return field_defs.get(field_name)

    def validate_measurement(self, measurement: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a measurement against protocol requirements.

        Args:
            measurement: Measurement data dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_fields = self.get_required_fields()
        field_definitions = self.definition.get("measurements", {}).get("field_definitions", {})

        # Check required fields
        for field in required_fields:
            if field not in measurement or measurement[field] is None:
                errors.append(f"Missing required field: {field}")

        # Validate field values
        for field, value in measurement.items():
            if field in field_definitions:
                field_def = field_definitions[field]

                # Check range for numeric fields
                if isinstance(value, (int, float)):
                    if "min" in field_def and value < field_def["min"]:
                        errors.append(
                            f"Field '{field}' value {value} below minimum {field_def['min']}"
                        )
                    if "max" in field_def and value > field_def["max"]:
                        errors.append(
                            f"Field '{field}' value {value} exceeds maximum {field_def['max']}"
                        )

        return len(errors) == 0, errors

    def calculate_test_duration(self) -> float:
        """
        Calculate expected test duration in hours.

        Returns:
            Duration in hours (override in subclass)
        """
        params = self.get_parameters()
        light_exposure = params.get("light_exposure", {})
        return light_exposure.get("duration_hours", 0.0)

    def get_measurement_schedule(self) -> List[Dict[str, Any]]:
        """
        Get the measurement schedule.

        Returns:
            List of measurement points (override in subclass)
        """
        return []

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.protocol_id})>"
