"""Protocol loader for loading and validating test protocols."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import jsonschema

from ..models.protocol import Protocol, ProtocolWrapper


class ProtocolLoader:
    """Loads and validates test protocol definitions from JSON files."""

    def __init__(self, protocols_dir: Optional[Path] = None, schema_path: Optional[Path] = None):
        """Initialize the protocol loader.

        Args:
            protocols_dir: Directory containing protocol JSON files
            schema_path: Path to JSON schema for validation
        """
        if protocols_dir is None:
            # Default to protocols directory in project root
            protocols_dir = Path(__file__).parent.parent.parent / "protocols"

        if schema_path is None:
            # Default to base protocol schema
            schema_path = protocols_dir / "schemas" / "base_protocol.schema.json"

        self.protocols_dir = Path(protocols_dir)
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load JSON schema for validation."""
        if not self.schema_path.exists():
            return None

        with open(self.schema_path, 'r') as f:
            return json.load(f)

    def list_protocols(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """List all available protocols.

        Args:
            category: Optional category filter (mechanical, environmental, etc.)

        Returns:
            List of protocol metadata dictionaries
        """
        protocols = []

        # Search in category directories
        if category:
            search_dirs = [self.protocols_dir / category]
        else:
            search_dirs = [
                self.protocols_dir / "mechanical",
                self.protocols_dir / "environmental",
                self.protocols_dir / "electrical"
            ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for protocol_file in search_dir.glob("*.json"):
                try:
                    with open(protocol_file, 'r') as f:
                        data = json.load(f)

                    protocol_data = data.get('protocol', {})
                    protocols.append({
                        'id': protocol_data.get('id'),
                        'name': protocol_data.get('name'),
                        'category': protocol_data.get('category'),
                        'version': protocol_data.get('version'),
                        'file_path': str(protocol_file)
                    })
                except Exception as e:
                    print(f"Error loading protocol {protocol_file}: {e}")

        return sorted(protocols, key=lambda x: x['id'])

    def load_protocol(self, protocol_id: str) -> Protocol:
        """Load a specific protocol by ID.

        Args:
            protocol_id: Protocol identifier (e.g., 'VIBR-001')

        Returns:
            Protocol object

        Raises:
            FileNotFoundError: If protocol file not found
            jsonschema.ValidationError: If protocol JSON is invalid
            ValueError: If protocol data is invalid
        """
        # Find protocol file
        protocol_file = self._find_protocol_file(protocol_id)

        if not protocol_file:
            raise FileNotFoundError(f"Protocol {protocol_id} not found")

        # Load JSON
        with open(protocol_file, 'r') as f:
            data = json.load(f)

        # Validate against JSON schema
        if self.schema:
            try:
                jsonschema.validate(instance=data, schema=self.schema)
            except jsonschema.ValidationError as e:
                raise jsonschema.ValidationError(
                    f"Protocol {protocol_id} failed schema validation: {e.message}"
                )

        # Parse with Pydantic model
        try:
            protocol_wrapper = ProtocolWrapper(**data)
            return protocol_wrapper.protocol
        except Exception as e:
            raise ValueError(f"Error parsing protocol {protocol_id}: {e}")

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """Find protocol file by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Path to protocol file or None if not found
        """
        # Search in all category directories
        for category_dir in self.protocols_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name == "schemas":
                continue

            protocol_file = category_dir / f"{protocol_id}.json"
            if protocol_file.exists():
                return protocol_file

        return None

    def validate_protocol_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate a protocol JSON file.

        Args:
            file_path: Path to protocol JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Validate against JSON schema
            if self.schema:
                jsonschema.validate(instance=data, schema=self.schema)

            # Validate with Pydantic model
            ProtocolWrapper(**data)

            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except jsonschema.ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
        except Exception as e:
            return False, f"Validation error: {e}"

    def get_protocol_info(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Get protocol information without full loading.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Dictionary with protocol metadata
        """
        protocol_file = self._find_protocol_file(protocol_id)

        if not protocol_file:
            return None

        try:
            with open(protocol_file, 'r') as f:
                data = json.load(f)

            protocol_data = data.get('protocol', {})
            return {
                'id': protocol_data.get('id'),
                'name': protocol_data.get('name'),
                'version': protocol_data.get('version'),
                'standard': protocol_data.get('standard'),
                'category': protocol_data.get('category'),
                'test_type': protocol_data.get('test_type'),
                'description': protocol_data.get('metadata', {}).get('description'),
                'estimated_duration_hours': protocol_data.get('metadata', {}).get('estimated_duration_hours'),
                'file_path': str(protocol_file)
            }
        except Exception:
            return None
