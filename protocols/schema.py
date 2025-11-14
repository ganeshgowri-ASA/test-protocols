"""
Protocol Schema Validation
JSON schema validation for protocols
"""

import jsonschema
from jsonschema import validate, ValidationError
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ProtocolValidator:
    """Validates protocol JSON against schema"""

    PROTOCOL_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["metadata", "test_parameters", "test_procedure"],
        "properties": {
            "metadata": {
                "type": "object",
                "required": ["id", "name", "category", "version"],
                "properties": {
                    "id": {"type": "string"},
                    "protocol_number": {"type": "string"},
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "subcategory": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "standard_references": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "author": {"type": "string"},
                    "created_date": {"type": "string"},
                    "last_modified": {"type": "string"},
                    "status": {"type": "string", "enum": ["active", "draft", "deprecated"]}
                }
            },
            "test_parameters": {
                "type": "object",
                "patternProperties": {
                    ".*": {
                        "type": "object",
                        "required": ["type", "description", "unit"],
                        "properties": {
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "default": {},
                            "min": {"type": "number"},
                            "max": {"type": "number"},
                            "unit": {"type": "string"},
                            "validation": {"type": "string"},
                            "tolerance": {"type": "number"}
                        }
                    }
                }
            },
            "test_procedure": {
                "type": "object"
            },
            "data_collection": {
                "type": "object"
            },
            "qc_checks": {
                "type": "array"
            },
            "pass_fail_criteria": {
                "type": "object"
            }
        }
    }

    @classmethod
    def validate(cls, protocol_data: Dict[str, Any]) -> tuple[bool, Optional[List[str]]]:
        """
        Validate protocol data against schema

        Args:
            protocol_data: Protocol JSON data

        Returns:
            Tuple of (is_valid, list of errors)
        """
        try:
            validate(instance=protocol_data, schema=cls.PROTOCOL_SCHEMA)
            return True, None
        except ValidationError as e:
            logger.error(f"Protocol validation failed: {e.message}")
            return False, [e.message]
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            return False, [str(e)]

    @classmethod
    def validate_parameter_values(
        cls,
        parameters: Dict[str, Any],
        parameter_definitions: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate parameter values against definitions

        Args:
            parameters: Parameter values
            parameter_definitions: Parameter definitions from protocol

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        for param_name, param_def in parameter_definitions.items():
            value = parameters.get(param_name)

            # Check required parameters
            if param_def.get("validation") == "required" and value is None:
                errors.append(f"Required parameter '{param_name}' is missing")
                continue

            if value is None:
                continue

            # Validate type
            expected_type = param_def.get("type")
            if expected_type == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param_name}' must be a number")
                    continue
            elif expected_type == "integer":
                if not isinstance(value, int):
                    errors.append(f"Parameter '{param_name}' must be an integer")
                    continue

            # Validate range
            min_val = param_def.get("min")
            max_val = param_def.get("max")
            if min_val is not None and value < min_val:
                errors.append(f"Parameter '{param_name}' must be >= {min_val}")
            if max_val is not None and value > max_val:
                errors.append(f"Parameter '{param_name}' must be <= {max_val}")

        return len(errors) == 0, errors
