"""
JSON Schema validator for protocol data.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator
from loguru import logger


class SchemaValidator:
    """Validates protocol data against JSON schemas."""

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize schema validator.

        Args:
            schemas_dir: Directory containing JSON schemas
        """
        self.schemas_dir = schemas_dir or Path(__file__).parent.parent / "protocols" / "schemas"
        self._schema_cache: Dict[str, dict] = {}

    def validate(
        self, data: Dict[str, Any], schema_name: str = "base_protocol_schema"
    ) -> Dict[str, Any]:
        """
        Validate data against a JSON schema.

        Args:
            data: Data to validate
            schema_name: Name of schema file (without .json extension)

        Returns:
            Validation result dictionary with keys:
                - is_valid: bool
                - errors: list of error messages
                - warnings: list of warning messages
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        try:
            # Load schema
            schema = self._load_schema(schema_name)

            # Validate against schema
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(data))

            if errors:
                result["is_valid"] = False
                result["errors"] = [self._format_error(error) for error in errors]
                logger.warning(f"Schema validation failed with {len(errors)} error(s)")
            else:
                logger.debug(f"Schema validation passed for {schema_name}")

        except FileNotFoundError as e:
            result["is_valid"] = False
            result["errors"].append(f"Schema not found: {schema_name}")
            logger.error(str(e))
        except json.JSONDecodeError as e:
            result["is_valid"] = False
            result["errors"].append(f"Invalid JSON in schema: {e}")
            logger.error(str(e))
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
            logger.error(f"Unexpected validation error: {e}")

        return result

    def validate_protocol(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate protocol data using appropriate schema based on protocol type.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            Validation result dictionary
        """
        # Determine schema based on protocol type
        protocol_type = protocol_data.get("protocol_type", "")
        schema_map = {
            "electrical": "electrical_protocol_schema",
            "thermal": "thermal_protocol_schema",
            "mechanical": "mechanical_protocol_schema",
        }

        schema_name = schema_map.get(protocol_type, "base_protocol_schema")
        return self.validate(protocol_data, schema_name)

    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load JSON schema from file.

        Args:
            schema_name: Schema file name without extension

        Returns:
            Schema dictionary

        Raises:
            FileNotFoundError: If schema file not found
        """
        # Check cache
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Load from file
        schema_file = self.schemas_dir / f"{schema_name}.json"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        with open(schema_file, "r") as f:
            schema = json.load(f)

        # Cache the schema
        self._schema_cache[schema_name] = schema
        return schema

    def _format_error(self, error: ValidationError) -> str:
        """
        Format validation error message.

        Args:
            error: ValidationError instance

        Returns:
            Formatted error message
        """
        path = ".".join(str(p) for p in error.absolute_path)
        if path:
            return f"{path}: {error.message}"
        return error.message

    def clear_cache(self):
        """Clear schema cache."""
        self._schema_cache.clear()
        logger.debug("Schema cache cleared")
