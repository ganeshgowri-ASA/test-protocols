"""Protocol validation using JSON Schema"""

import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


class ProtocolValidator:
    """
    Validates protocol definitions and test data against JSON schemas.
    """

    def __init__(self, schema_path: str = None):
        """
        Initialize validator with optional schema path.

        Args:
            schema_path: Path to JSON schema file
        """
        self.schema: Dict[str, Any] = {}
        if schema_path:
            self.load_schema(schema_path)

    def load_schema(self, schema_path: str) -> None:
        """
        Load JSON schema from file.

        Args:
            schema_path: Path to schema file
        """
        try:
            with open(schema_path, "r") as f:
                self.schema = json.load(f)
            logger.info(f"Loaded schema from: {schema_path}")
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            raise

    def validate_data(
        self, data: Dict[str, Any], schema: Dict[str, Any] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema: Schema to validate against (uses loaded schema if not provided)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        schema_to_use = schema if schema else self.schema

        if not schema_to_use:
            logger.error("No schema available for validation")
            return False, ["No schema available"]

        validator = Draft7Validator(schema_to_use)
        errors = list(validator.iter_errors(data))

        if errors:
            error_messages = [self._format_error(error) for error in errors]
            logger.warning(f"Validation failed with {len(errors)} errors")
            return False, error_messages
        else:
            logger.info("Validation successful")
            return True, []

    def _format_error(self, error: ValidationError) -> str:
        """
        Format a validation error into readable message.

        Args:
            error: ValidationError object

        Returns:
            Formatted error message
        """
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        return f"{path}: {error.message}"

    def validate_protocol_definition(self, protocol_def: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a protocol definition structure.

        Args:
            protocol_def: Protocol definition dictionary

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        required_fields = [
            "protocol_id",
            "name",
            "version",
            "category",
            "test_parameters",
            "test_steps",
        ]

        errors = []
        for field in required_fields:
            if field not in protocol_def:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Validate version format (semver)
        version = protocol_def.get("version", "")
        if not self._is_valid_semver(version):
            errors.append(f"Invalid version format: {version} (expected semver)")

        # Validate protocol_id format
        protocol_id = protocol_def.get("protocol_id", "")
        if not protocol_id or not protocol_id.replace("-", "").replace("_", "").isalnum():
            errors.append(f"Invalid protocol_id format: {protocol_id}")

        return (len(errors) == 0), errors

    def _is_valid_semver(self, version: str) -> bool:
        """
        Check if version string follows semantic versioning.

        Args:
            version: Version string to check

        Returns:
            True if valid semver format
        """
        import re

        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def validate_test_results(
        self, results: Dict[str, Any], protocol_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate test results against protocol schema.

        Args:
            results: Test results dictionary
            protocol_id: Protocol identifier for schema lookup

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        # Check if results match the protocol
        if results.get("protocol_id") != protocol_id:
            return False, [
                f"Protocol ID mismatch: expected {protocol_id}, got {results.get('protocol_id')}"
            ]

        return self.validate_data(results)

    def get_validation_report(
        self, data: Dict[str, Any], schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed validation report.

        Args:
            data: Data to validate
            schema: Schema to validate against

        Returns:
            Validation report dictionary
        """
        is_valid, errors = self.validate_data(data, schema)

        return {
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "validated_at": json.dumps(
                {"timestamp": "now"}, default=str
            ),  # Placeholder for timestamp
        }


def load_protocol_definition(protocol_path: str) -> Dict[str, Any]:
    """
    Load protocol definition from JSON file.

    Args:
        protocol_path: Path to protocol JSON file

    Returns:
        Protocol definition dictionary
    """
    with open(protocol_path, "r") as f:
        return json.load(f)


def load_protocol_schema(schema_path: str) -> Dict[str, Any]:
    """
    Load protocol schema from JSON file.

    Args:
        schema_path: Path to schema JSON file

    Returns:
        Schema dictionary
    """
    with open(schema_path, "r") as f:
        return json.load(f)
