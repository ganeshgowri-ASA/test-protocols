"""JSON Schema validator for protocol definitions."""

import jsonschema
from jsonschema import validate, ValidationError
from typing import Dict, Any, List, Tuple


class SchemaValidator:
    """Validate protocol data against JSON schemas."""

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize validator with a schema.

        Args:
            schema: JSON schema dictionary
        """
        self.schema = schema

    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate test parameters against schema.

        Args:
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if test_parameters exists in schema
        if "test_parameters" not in self.schema:
            return False, ["Schema does not define test_parameters"]

        test_params_schema = self.schema["test_parameters"]

        try:
            validate(instance=parameters, schema=test_params_schema)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")
            return False, errors

    def validate_measurement(self, measurement: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate measurement data against schema.

        Args:
            measurement: Measurement data to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if "measurements" not in self.schema:
            return False, ["Schema does not define measurements"]

        measurement_schema = self.schema["measurements"]

        try:
            validate(instance=measurement, schema=measurement_schema)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")
            return False, errors

    def validate_results(self, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate results data against schema.

        Args:
            results: Results data to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if "results" not in self.schema:
            return False, ["Schema does not define results"]

        results_schema = self.schema["results"]

        try:
            validate(instance=results, schema=results_schema)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")
            return False, errors

    def get_parameter_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about parameters from schema.

        Returns:
            Parameter metadata dictionary
        """
        if "test_parameters" not in self.schema:
            return {}

        properties = self.schema["test_parameters"].get("properties", {})
        required = self.schema["test_parameters"].get("required", [])

        metadata = {}
        for param_name, param_def in properties.items():
            metadata[param_name] = {
                "type": param_def.get("type"),
                "description": param_def.get("description"),
                "required": param_name in required,
                "default": param_def.get("default"),
                "minimum": param_def.get("minimum"),
                "maximum": param_def.get("maximum"),
            }

        return metadata
