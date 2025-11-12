"""
Data type and format validator.
"""
from typing import Dict, Any, List
from datetime import datetime
import re
from loguru import logger


class DataValidator:
    """Validates data types and formats."""

    def __init__(self):
        """Initialize data validator."""
        self.validators = {
            "string": self._validate_string,
            "number": self._validate_number,
            "integer": self._validate_integer,
            "boolean": self._validate_boolean,
            "datetime": self._validate_datetime,
            "email": self._validate_email,
            "url": self._validate_url,
            "protocol_id": self._validate_protocol_id,
        }

    def validate_field(
        self, value: Any, field_type: str, constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate a single field value.

        Args:
            value: Value to validate
            field_type: Expected data type
            constraints: Optional validation constraints

        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        constraints = constraints or {}

        # Check if value is None/empty when required
        if constraints.get("required", False) and (value is None or value == ""):
            result["is_valid"] = False
            result["errors"].append("Field is required but empty")
            return result

        # Skip validation if value is None/empty and not required
        if value is None or value == "":
            return result

        # Get appropriate validator
        validator_func = self.validators.get(field_type)
        if not validator_func:
            result["warnings"].append(f"No validator found for type: {field_type}")
            return result

        # Validate value
        try:
            is_valid, error_msg = validator_func(value, constraints)
            if not is_valid:
                result["is_valid"] = False
                result["errors"].append(error_msg)
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
            logger.error(f"Validation error for {field_type}: {e}")

        return result

    def validate_multiple_fields(
        self, data: Dict[str, Any], field_specs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate multiple fields.

        Args:
            data: Data dictionary
            field_specs: Field specifications with types and constraints

        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "field_results": {},
        }

        for field_name, spec in field_specs.items():
            value = data.get(field_name)
            field_type = spec.get("type", "string")
            constraints = spec.get("constraints", {})

            field_result = self.validate_field(value, field_type, constraints)
            result["field_results"][field_name] = field_result

            if not field_result["is_valid"]:
                result["is_valid"] = False
                result["errors"].extend(
                    [f"{field_name}: {err}" for err in field_result["errors"]]
                )

            result["warnings"].extend(
                [f"{field_name}: {warn}" for warn in field_result["warnings"]]
            )

        return result

    def _validate_string(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate string value."""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"

        min_length = constraints.get("min_length")
        max_length = constraints.get("max_length")
        pattern = constraints.get("pattern")

        if min_length and len(value) < min_length:
            return False, f"String too short (min: {min_length})"

        if max_length and len(value) > max_length:
            return False, f"String too long (max: {max_length})"

        if pattern and not re.match(pattern, value):
            return False, f"String does not match pattern: {pattern}"

        return True, ""

    def _validate_number(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate numeric value."""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, f"Expected number, got {type(value).__name__}"

        minimum = constraints.get("minimum")
        maximum = constraints.get("maximum")

        if minimum is not None and num_value < minimum:
            return False, f"Value {num_value} below minimum {minimum}"

        if maximum is not None and num_value > maximum:
            return False, f"Value {num_value} above maximum {maximum}"

        return True, ""

    def _validate_integer(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate integer value."""
        if not isinstance(value, int) or isinstance(value, bool):
            return False, f"Expected integer, got {type(value).__name__}"

        minimum = constraints.get("minimum")
        maximum = constraints.get("maximum")

        if minimum is not None and value < minimum:
            return False, f"Value {value} below minimum {minimum}"

        if maximum is not None and value > maximum:
            return False, f"Value {value} above maximum {maximum}"

        return True, ""

    def _validate_boolean(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate boolean value."""
        if not isinstance(value, bool):
            return False, f"Expected boolean, got {type(value).__name__}"
        return True, ""

    def _validate_datetime(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate datetime string."""
        if not isinstance(value, str):
            return False, f"Expected datetime string, got {type(value).__name__}"

        try:
            # Try ISO format
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True, ""
        except ValueError:
            return False, "Invalid datetime format (expected ISO 8601)"

    def _validate_email(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate email address."""
        if not isinstance(value, str):
            return False, f"Expected email string, got {type(value).__name__}"

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            return False, "Invalid email format"

        return True, ""

    def _validate_url(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate URL."""
        if not isinstance(value, str):
            return False, f"Expected URL string, got {type(value).__name__}"

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(url_pattern, value):
            return False, "Invalid URL format"

        return True, ""

    def _validate_protocol_id(self, value: Any, constraints: Dict[str, Any]) -> tuple:
        """Validate protocol ID format."""
        if not isinstance(value, str):
            return False, f"Expected protocol ID string, got {type(value).__name__}"

        protocol_pattern = r"^[A-Z0-9-]+$"
        if not re.match(protocol_pattern, value):
            return False, "Invalid protocol ID format (use uppercase, numbers, hyphens)"

        return True, ""
