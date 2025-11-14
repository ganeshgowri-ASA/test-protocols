"""
Protocol Loader Module

Handles loading and validation of JSON-based test protocols.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProtocolLoader:
    """Loads and validates test protocol definitions from JSON files."""

    def __init__(self, protocol_dir: str = "protocols/templates",
                 schema_dir: str = "protocols/schemas"):
        """
        Initialize the protocol loader.

        Args:
            protocol_dir: Directory containing protocol JSON files
            schema_dir: Directory containing JSON schema files
        """
        self.protocol_dir = Path(protocol_dir)
        self.schema_dir = Path(schema_dir)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load the protocol validation schema."""
        schema_path = self.schema_dir / "protocol-schema.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, 'r') as f:
            return json.load(f)

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Load a protocol by its ID.

        Args:
            protocol_id: Protocol identifier (e.g., 'JBOX-001' or 'jbox-001')

        Returns:
            Dict containing the protocol definition

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            jsonschema.ValidationError: If protocol doesn't match schema
        """
        # Normalize protocol ID to lowercase for filename
        protocol_file = self.protocol_dir / f"{protocol_id.lower()}.json"

        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        with open(protocol_file, 'r') as f:
            protocol = json.load(f)

        # Validate against schema
        self.validate_protocol(protocol)

        return protocol

    def validate_protocol(self, protocol: Dict[str, Any]) -> None:
        """
        Validate a protocol against the schema.

        Args:
            protocol: Protocol dictionary to validate

        Raises:
            jsonschema.ValidationError: If validation fails
        """
        jsonschema.validate(instance=protocol, schema=self.schema)

    def list_protocols(self) -> list:
        """
        List all available protocols.

        Returns:
            List of dictionaries with protocol metadata
        """
        protocols = []

        for protocol_file in self.protocol_dir.glob("*.json"):
            try:
                protocol = self.load_protocol(protocol_file.stem)
                protocols.append({
                    'protocol_id': protocol['protocol_id'],
                    'name': protocol['name'],
                    'version': protocol['version'],
                    'category': protocol['category'],
                    'description': protocol['metadata']['description']
                })
            except Exception as e:
                print(f"Warning: Could not load {protocol_file}: {e}")

        return protocols

    def get_protocol_metadata(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary containing protocol metadata
        """
        protocol = self.load_protocol(protocol_id)
        return protocol['metadata']

    def get_test_phases(self, protocol_id: str) -> list:
        """
        Get test phases for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of test phase definitions
        """
        protocol = self.load_protocol(protocol_id)
        return protocol['test_phases']

    def get_measurements(self, protocol_id: str) -> list:
        """
        Get measurement definitions for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of measurement definitions
        """
        protocol = self.load_protocol(protocol_id)
        return protocol['measurements']

    def get_qc_criteria(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get QC criteria for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary containing QC criteria
        """
        protocol = self.load_protocol(protocol_id)
        return protocol['qc_criteria']

    def export_protocol_summary(self, protocol_id: str,
                                output_file: Optional[str] = None) -> str:
        """
        Export a human-readable summary of the protocol.

        Args:
            protocol_id: Protocol identifier
            output_file: Optional file path to write summary

        Returns:
            String containing the protocol summary
        """
        protocol = self.load_protocol(protocol_id)

        summary = []
        summary.append(f"Protocol: {protocol['name']} ({protocol['protocol_id']})")
        summary.append(f"Version: {protocol['version']}")
        summary.append(f"Category: {protocol['category']}")
        summary.append(f"\nDescription:")
        summary.append(protocol['metadata']['description'])
        summary.append(f"\nStandards:")
        for standard in protocol['metadata']['standards']:
            summary.append(f"  - {standard}")

        summary.append(f"\nTest Phases ({len(protocol['test_phases'])}):")
        for phase in protocol['test_phases']:
            summary.append(f"  {phase['phase_id']}: {phase['name']}")
            if 'duration' in phase:
                summary.append(f"    Duration: {phase['duration']['value']} {phase['duration']['unit']}")

        summary.append(f"\nMeasurements ({len(protocol['measurements'])}):")
        for measurement in protocol['measurements']:
            summary.append(f"  - {measurement['name']} ({measurement['unit']})")

        summary.append(f"\nAcceptance Criteria ({len(protocol['qc_criteria']['acceptance_criteria'])}):")
        for criterion in protocol['qc_criteria']['acceptance_criteria']:
            summary.append(f"  {criterion['criterion_id']}: {criterion['description']} [{criterion['severity']}]")

        summary_text = "\n".join(summary)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(summary_text)

        return summary_text


if __name__ == "__main__":
    # Example usage
    loader = ProtocolLoader()

    # Load JBOX-001 protocol
    protocol = loader.load_protocol("JBOX-001")
    print(f"Loaded protocol: {protocol['name']}")

    # List all protocols
    print("\nAvailable protocols:")
    for p in loader.list_protocols():
        print(f"  - {p['protocol_id']}: {p['name']}")

    # Export summary
    summary = loader.export_protocol_summary("JBOX-001")
    print("\n" + summary)
