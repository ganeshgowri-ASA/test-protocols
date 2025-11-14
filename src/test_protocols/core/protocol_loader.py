"""
Protocol loader and validator.

This module handles loading protocols from JSON files and validating them
against the schema.
"""

import json
import jsonschema
from pathlib import Path
from typing import Union, Optional
from .protocol import Protocol


class ProtocolLoader:
    """Loads and validates test protocols from JSON files."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize protocol loader.

        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        self.schema_path = schema_path
        self.schema = None
        if schema_path and schema_path.exists():
            self.load_schema()

    def load_schema(self) -> dict:
        """Load JSON schema for validation."""
        if not self.schema_path:
            # Use default schema path
            default_schema = Path(__file__).parent.parent / "schemas" / "protocol_schema.json"
            self.schema_path = default_schema

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

        return self.schema

    def validate_json(self, protocol_data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate protocol JSON against schema.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.schema:
            self.load_schema()

        try:
            jsonschema.validate(instance=protocol_data, schema=self.schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
        except jsonschema.SchemaError as e:
            return False, f"Schema error: {str(e)}"

    def load_protocol(self, protocol_path: Union[str, Path]) -> Protocol:
        """
        Load a protocol from a JSON file.

        Args:
            protocol_path: Path to protocol JSON file

        Returns:
            Protocol object

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            ValueError: If protocol JSON is invalid
            jsonschema.ValidationError: If protocol doesn't match schema
        """
        protocol_path = Path(protocol_path)

        if not protocol_path.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_path}")

        # Load JSON
        with open(protocol_path, 'r', encoding='utf-8') as f:
            protocol_data = json.load(f)

        # Validate against schema
        is_valid, error = self.validate_json(protocol_data)
        if not is_valid:
            raise ValueError(f"Protocol validation failed: {error}")

        # Create Protocol object
        protocol = Protocol(**protocol_data)

        # Validate protocol object
        is_valid, errors = protocol.validate()
        if not is_valid:
            raise ValueError(f"Protocol validation errors: {', '.join(errors)}")

        return protocol

    def load_protocol_from_string(self, json_string: str) -> Protocol:
        """
        Load a protocol from a JSON string.

        Args:
            json_string: JSON string containing protocol data

        Returns:
            Protocol object
        """
        protocol_data = json.loads(json_string)

        # Validate against schema
        is_valid, error = self.validate_json(protocol_data)
        if not is_valid:
            raise ValueError(f"Protocol validation failed: {error}")

        # Create Protocol object
        protocol = Protocol(**protocol_data)

        # Validate protocol object
        is_valid, errors = protocol.validate()
        if not is_valid:
            raise ValueError(f"Protocol validation errors: {', '.join(errors)}")

        return protocol

    def save_protocol(self, protocol: Protocol, output_path: Union[str, Path]) -> None:
        """
        Save a protocol to a JSON file.

        Args:
            protocol: Protocol object to save
            output_path: Path where to save the protocol
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert protocol to dict (simplified - would need proper serialization)
        protocol_dict = {
            "protocol_id": protocol.protocol_id,
            "version": protocol.version,
            "name": protocol.name,
            "category": protocol.category,
            "standard": {
                "name": protocol.standard.name,
                "code": protocol.standard.code,
                "version": protocol.standard.version,
                "url": protocol.standard.url,
            },
            "description": protocol.description,
            "duration_minutes": protocol.duration_minutes,
            "equipment_required": [
                {
                    "name": eq.name,
                    "type": eq.type,
                    "model": eq.model,
                    "calibration_required": eq.calibration_required,
                    "calibration_interval_days": eq.calibration_interval_days,
                }
                for eq in protocol.equipment_required
            ],
            "safety_requirements": protocol.safety_requirements,
            "environmental_conditions": protocol.environmental_conditions,
            "tests": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "sequence": step.sequence,
                    "description": step.description,
                    "duration_minutes": step.duration_minutes,
                    "parameters": step.parameters,
                    "measurements": [
                        {
                            "measurement_type": m.measurement_type,
                            "unit": m.unit,
                            "interval_seconds": m.interval_seconds,
                            "sensor_id": m.sensor_id,
                            "min_value": m.min_value,
                            "max_value": m.max_value,
                            "target_value": m.target_value,
                            "tolerance": m.tolerance,
                        }
                        for m in step.measurements
                    ],
                    "acceptance_criteria": step.acceptance_criteria,
                    "operator_instructions": step.operator_instructions,
                }
                for step in protocol.tests
            ],
            "metadata": protocol.metadata,
        }

        # Validate before saving
        is_valid, error = self.validate_json(protocol_dict)
        if not is_valid:
            raise ValueError(f"Protocol validation failed before save: {error}")

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(protocol_dict, f, indent=2, ensure_ascii=False)

    @staticmethod
    def list_protocols(protocols_dir: Union[str, Path]) -> list[Path]:
        """
        List all protocol JSON files in a directory.

        Args:
            protocols_dir: Directory to search for protocols

        Returns:
            List of protocol file paths
        """
        protocols_dir = Path(protocols_dir)
        if not protocols_dir.exists():
            return []

        return list(protocols_dir.rglob("*_protocol.json"))
