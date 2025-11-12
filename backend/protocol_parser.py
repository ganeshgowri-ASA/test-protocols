"""
Protocol Parser Module

This module handles loading, validation, and parsing of protocol JSON files.
It provides functionality to dynamically generate form structures from protocol definitions.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError


class ProtocolParserError(Exception):
    """Custom exception for protocol parsing errors."""
    pass


class ProtocolParser:
    """
    Main class for parsing and validating protocol JSON files.
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the protocol parser.

        Args:
            schema_path: Path to the JSON schema file. If None, uses default location.
        """
        if schema_path is None:
            # Default to templates/base_protocol_schema.json
            base_dir = Path(__file__).parent.parent
            schema_path = base_dir / "templates" / "base_protocol_schema.json"

        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.protocol_cache = {}

    def _load_schema(self) -> Dict[str, Any]:
        """Load the protocol JSON schema."""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ProtocolParserError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise ProtocolParserError(f"Invalid JSON in schema file: {e}")

    def load_protocol(self, protocol_path: str, validate_schema: bool = True) -> Dict[str, Any]:
        """
        Load a protocol JSON file.

        Args:
            protocol_path: Path to the protocol JSON file
            validate_schema: Whether to validate against schema

        Returns:
            Dictionary containing the protocol data

        Raises:
            ProtocolParserError: If protocol cannot be loaded or is invalid
        """
        protocol_path = Path(protocol_path)

        try:
            with open(protocol_path, 'r') as f:
                protocol_data = json.load(f)
        except FileNotFoundError:
            raise ProtocolParserError(f"Protocol file not found: {protocol_path}")
        except json.JSONDecodeError as e:
            raise ProtocolParserError(f"Invalid JSON in protocol file: {e}")

        if validate_schema:
            self.validate_protocol(protocol_data)

        # Cache the protocol
        self.protocol_cache[str(protocol_path)] = protocol_data

        return protocol_data

    def validate_protocol(self, protocol_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate protocol data against the schema.

        Args:
            protocol_data: Protocol data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validate(instance=protocol_data, schema=self.schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def get_available_protocols(self, templates_dir: str) -> List[Dict[str, str]]:
        """
        Get list of available protocols from the templates directory.

        Args:
            templates_dir: Path to templates directory

        Returns:
            List of protocol metadata dictionaries
        """
        templates_path = Path(templates_dir)
        protocols = []

        if not templates_path.exists():
            return protocols

        for json_file in templates_path.glob("*.json"):
            # Skip the schema file
            if json_file.name == "base_protocol_schema.json":
                continue

            try:
                protocol_data = self.load_protocol(str(json_file), validate_schema=False)
                metadata = protocol_data.get("protocol_metadata", {})

                protocols.append({
                    "path": str(json_file),
                    "id": metadata.get("protocol_id", json_file.stem),
                    "name": metadata.get("protocol_name", json_file.stem),
                    "version": metadata.get("version", "1.0.0"),
                    "category": metadata.get("category", "Unknown"),
                    "description": metadata.get("description", "")
                })
            except Exception as e:
                print(f"Warning: Could not load protocol {json_file}: {e}")
                continue

        return sorted(protocols, key=lambda x: x["name"])

    def extract_form_fields(self, protocol_data: Dict[str, Any], section: str) -> List[Dict[str, Any]]:
        """
        Extract form fields from a specific protocol section.

        Args:
            protocol_data: Protocol data dictionary
            section: Section name (e.g., 'general_data', 'sample_info')

        Returns:
            List of field definitions
        """
        section_data = protocol_data.get(section, {})
        return section_data.get("fields", [])

    def get_protocol_metadata(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract protocol metadata.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            Metadata dictionary
        """
        return protocol_data.get("protocol_metadata", {})

    def get_sections(self, protocol_data: Dict[str, Any]) -> List[str]:
        """
        Get list of available sections in the protocol.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            List of section names
        """
        sections = []
        possible_sections = [
            "general_data",
            "sample_info",
            "protocol_inputs",
            "live_readings",
            "analysis",
            "charts",
            "quality_control",
            "maintenance",
            "project_management",
            "nc_register"
        ]

        for section in possible_sections:
            if section in protocol_data and protocol_data[section]:
                sections.append(section)

        return sections

    def get_validation_rules(self, protocol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract validation rules from protocol.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            List of validation rules
        """
        qc_section = protocol_data.get("quality_control", {})
        return qc_section.get("validation_rules", [])

    def get_calculations(self, protocol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract calculation definitions from protocol.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            List of calculation definitions
        """
        analysis_section = protocol_data.get("analysis", {})
        return analysis_section.get("calculations", [])

    def get_chart_configs(self, protocol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract chart configurations from protocol.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            List of chart configurations
        """
        charts_section = protocol_data.get("charts", {})
        return charts_section.get("visualizations", [])

    def generate_form_structure(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete form structure from protocol data.

        Args:
            protocol_data: Protocol data dictionary

        Returns:
            Dictionary containing organized form structure
        """
        structure = {
            "metadata": self.get_protocol_metadata(protocol_data),
            "sections": {},
            "validations": self.get_validation_rules(protocol_data),
            "calculations": self.get_calculations(protocol_data),
            "charts": self.get_chart_configs(protocol_data)
        }

        # Extract all sections
        for section in self.get_sections(protocol_data):
            section_data = protocol_data[section]

            if "fields" in section_data:
                structure["sections"][section] = {
                    "type": "form",
                    "fields": section_data["fields"]
                }
            elif "sections" in section_data:
                # For protocol_inputs with sub-sections
                structure["sections"][section] = {
                    "type": "multi_section",
                    "subsections": section_data["sections"]
                }
            elif "tables" in section_data:
                # For live_readings with table structure
                structure["sections"][section] = {
                    "type": "table",
                    "tables": section_data["tables"]
                }
            else:
                structure["sections"][section] = section_data

        return structure

    def export_protocol_template(self, protocol_data: Dict[str, Any], output_path: str) -> None:
        """
        Export protocol data to a JSON file.

        Args:
            protocol_data: Protocol data to export
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            json.dump(protocol_data, f, indent=2)


# Utility functions
def create_sample_protocol(protocol_name: str) -> Dict[str, Any]:
    """
    Create a minimal sample protocol structure.

    Args:
        protocol_name: Name of the protocol

    Returns:
        Sample protocol dictionary
    """
    return {
        "protocol_metadata": {
            "protocol_id": protocol_name.lower().replace(" ", "_"),
            "protocol_name": protocol_name,
            "version": "1.0.0",
            "category": "electrical",
            "description": f"Sample protocol: {protocol_name}",
            "tags": ["sample"]
        },
        "general_data": {
            "fields": [
                {
                    "field_id": "test_date",
                    "field_name": "Test Date",
                    "field_type": "date",
                    "required": True
                },
                {
                    "field_id": "operator_name",
                    "field_name": "Operator Name",
                    "field_type": "text",
                    "required": True
                },
                {
                    "field_id": "test_facility",
                    "field_name": "Test Facility",
                    "field_type": "text",
                    "required": False
                }
            ]
        },
        "sample_info": {
            "fields": [
                {
                    "field_id": "sample_id",
                    "field_name": "Sample ID",
                    "field_type": "text",
                    "required": True
                },
                {
                    "field_id": "manufacturer",
                    "field_name": "Manufacturer",
                    "field_type": "text",
                    "required": False
                }
            ]
        }
    }


if __name__ == "__main__":
    # Example usage
    parser = ProtocolParser()

    # Create a sample protocol
    sample = create_sample_protocol("Sample Test Protocol")

    # Validate it
    is_valid, error = parser.validate_protocol(sample)
    print(f"Sample protocol valid: {is_valid}")
    if error:
        print(f"Validation error: {error}")
