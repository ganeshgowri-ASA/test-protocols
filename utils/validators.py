"""Validation utilities for test protocols."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema import Draft7Validator, ValidationError

from .logging import get_logger

logger = get_logger(__name__)


def validate_schema(instance: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate an instance against a JSON schema.

    Args:
        instance: Data to validate
        schema: JSON schema to validate against

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If validation fails
    """
    try:
        jsonschema.validate(instance=instance, schema=schema)
        logger.debug("Schema validation successful")
        return True
    except ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        raise


def validate_parameters(
    params: Dict[str, Any],
    schema: Dict[str, Any],
    required_fields: Optional[List[str]] = None
) -> bool:
    """Validate test parameters.

    Args:
        params: Parameters to validate
        schema: JSON schema defining parameter structure
        required_fields: List of required field names

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in params]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Validate against schema if provided
    if schema:
        try:
            validate_schema(params, schema)
        except ValidationError as e:
            raise ValueError(f"Parameter validation failed: {e.message}")

    logger.debug("Parameter validation successful")
    return True


def load_json_schema(schema_path: str) -> Dict[str, Any]:
    """Load JSON schema from file.

    Args:
        schema_path: Path to JSON schema file

    Returns:
        Parsed JSON schema

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(path, 'r') as f:
        schema = json.load(f)

    logger.debug(f"Loaded schema from {schema_path}")
    return schema


def get_validation_errors(
    instance: Dict[str, Any],
    schema: Dict[str, Any]
) -> List[str]:
    """Get list of validation errors without raising exception.

    Args:
        instance: Data to validate
        schema: JSON schema to validate against

    Returns:
        List of error messages (empty if valid)
    """
    validator = Draft7Validator(schema)
    errors = [error.message for error in validator.iter_errors(instance)]
    return errors
