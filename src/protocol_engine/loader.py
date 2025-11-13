"""Protocol loader for reading and parsing protocol JSON files."""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class ProtocolLoader:
    """Load and parse protocol definitions from JSON files."""

    def __init__(self, protocols_dir: Optional[Path] = None) -> None:
        """Initialize the protocol loader.

        Args:
            protocols_dir: Directory containing protocol definitions
        """
        if protocols_dir is None:
            # Default to protocols directory relative to project root
            self.protocols_dir = Path(__file__).parent.parent.parent / "protocols"
        else:
            self.protocols_dir = Path(protocols_dir)

    def load_schema(self, protocol_id: str) -> Dict[str, Any]:
        """Load the JSON schema for a protocol.

        Args:
            protocol_id: Protocol identifier (e.g., 'iam-001')

        Returns:
            Dictionary containing the protocol schema

        Raises:
            FileNotFoundError: If schema file not found
            json.JSONDecodeError: If schema file is invalid JSON
        """
        schema_path = self.protocols_dir / protocol_id / "schema.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as f:
            return json.load(f)

    def load_template(self, protocol_id: str) -> Dict[str, Any]:
        """Load the template for a protocol.

        Args:
            protocol_id: Protocol identifier (e.g., 'iam-001')

        Returns:
            Dictionary containing the protocol template

        Raises:
            FileNotFoundError: If template file not found
            json.JSONDecodeError: If template file is invalid JSON
        """
        template_path = self.protocols_dir / protocol_id / "template.json"

        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, "r") as f:
            return json.load(f)

    def load_config(self, protocol_id: str) -> Dict[str, Any]:
        """Load the configuration for a protocol.

        Args:
            protocol_id: Protocol identifier (e.g., 'iam-001')

        Returns:
            Dictionary containing the protocol configuration

        Raises:
            FileNotFoundError: If config file not found
            json.JSONDecodeError: If config file is invalid JSON
        """
        config_path = self.protocols_dir / protocol_id / "config.json"

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            return json.load(f)

    def load_protocol(self, file_path: Path) -> Dict[str, Any]:
        """Load a protocol instance from a JSON file.

        Args:
            file_path: Path to the protocol JSON file

        Returns:
            Dictionary containing the protocol data

        Raises:
            FileNotFoundError: If protocol file not found
            json.JSONDecodeError: If protocol file is invalid JSON
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Protocol file not found: {file_path}")

        with open(file_path, "r") as f:
            return json.load(f)

    def save_protocol(self, protocol_data: Dict[str, Any], file_path: Path) -> None:
        """Save a protocol instance to a JSON file.

        Args:
            protocol_data: Protocol data dictionary
            file_path: Path where to save the protocol
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(protocol_data, f, indent=2)

    def create_from_template(self, protocol_id: str, **overrides: Any) -> Dict[str, Any]:
        """Create a new protocol instance from template with optional overrides.

        Args:
            protocol_id: Protocol identifier (e.g., 'iam-001')
            **overrides: Key-value pairs to override template values

        Returns:
            New protocol instance dictionary
        """
        template = self.load_template(protocol_id)

        # Update test date to current time
        if "protocol_info" in template:
            template["protocol_info"]["test_date"] = datetime.utcnow().isoformat() + "Z"

        # Apply overrides
        self._apply_overrides(template, overrides)

        return template

    def _apply_overrides(self, data: Dict[str, Any], overrides: Dict[str, Any]) -> None:
        """Recursively apply overrides to template data.

        Args:
            data: Template data dictionary (modified in place)
            overrides: Overrides to apply (dot notation supported)
        """
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys with dot notation
                keys = key.split(".")
                current = data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            else:
                data[key] = value

    def list_protocols(self) -> list[str]:
        """List all available protocol IDs.

        Returns:
            List of protocol identifiers
        """
        if not self.protocols_dir.exists():
            return []

        protocols = []
        for item in self.protocols_dir.iterdir():
            if item.is_dir() and (item / "schema.json").exists():
                protocols.append(item.name)

        return sorted(protocols)
