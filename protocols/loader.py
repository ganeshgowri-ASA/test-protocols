"""
Protocol loader for loading protocol templates and schemas.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger


class ProtocolLoader:
    """Loads protocol templates and schemas."""

    def __init__(self, templates_dir: Optional[Path] = None, schemas_dir: Optional[Path] = None):
        """
        Initialize protocol loader.

        Args:
            templates_dir: Directory containing protocol templates
            schemas_dir: Directory containing JSON schemas
        """
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.schemas_dir = schemas_dir or Path(__file__).parent / "schemas"
        self._protocol_cache: Dict[str, dict] = {}
        self._schema_cache: Dict[str, dict] = {}

    def load_template(self, protocol_id: str) -> Dict:
        """
        Load a protocol template by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol template as dictionary

        Raises:
            FileNotFoundError: If template file not found
        """
        # Check cache first
        if protocol_id in self._protocol_cache:
            logger.debug(f"Loading protocol {protocol_id} from cache")
            return self._protocol_cache[protocol_id].copy()

        # Find template file
        template_file = self._find_template_file(protocol_id)
        if not template_file:
            raise FileNotFoundError(f"Protocol template not found: {protocol_id}")

        # Load template
        logger.info(f"Loading protocol template: {protocol_id}")
        with open(template_file, "r") as f:
            template_data = json.load(f)

        # Cache the template
        self._protocol_cache[protocol_id] = template_data

        return template_data.copy()

    def _find_template_file(self, protocol_id: str) -> Optional[Path]:
        """
        Find template file by protocol ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Path to template file or None
        """
        # Try exact match with .json extension
        for file in self.templates_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    if data.get("protocol_id") == protocol_id:
                        return file
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def load_schema(self, schema_name: str) -> Dict:
        """
        Load a JSON schema by name.

        Args:
            schema_name: Schema file name (without .json extension)

        Returns:
            JSON schema as dictionary

        Raises:
            FileNotFoundError: If schema file not found
        """
        # Check cache first
        if schema_name in self._schema_cache:
            logger.debug(f"Loading schema {schema_name} from cache")
            return self._schema_cache[schema_name].copy()

        # Load schema file
        schema_file = self.schemas_dir / f"{schema_name}.json"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema not found: {schema_name}")

        logger.info(f"Loading schema: {schema_name}")
        with open(schema_file, "r") as f:
            schema_data = json.load(f)

        # Cache the schema
        self._schema_cache[schema_name] = schema_data

        return schema_data.copy()

    def list_available_protocols(self) -> List[Dict[str, str]]:
        """
        List all available protocol templates.

        Returns:
            List of dictionaries with protocol metadata
        """
        protocols = []

        for file in self.templates_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    protocols.append({
                        "protocol_id": data.get("protocol_id", ""),
                        "protocol_name": data.get("protocol_name", ""),
                        "protocol_type": data.get("protocol_type", ""),
                        "version": data.get("version", ""),
                        "file": str(file.name),
                    })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to read protocol template {file}: {e}")
                continue

        return sorted(protocols, key=lambda x: x["protocol_id"])

    def get_protocol_catalog(self) -> Dict:
        """
        Load the protocol catalog from schema registry.

        Returns:
            Protocol catalog dictionary
        """
        try:
            registry_file = self.schemas_dir / "schema_registry.json"
            with open(registry_file, "r") as f:
                registry = json.load(f)
            return registry.get("protocol_catalog", {})
        except FileNotFoundError:
            logger.warning("Schema registry not found")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse schema registry: {e}")
            return {}

    def clear_cache(self):
        """Clear protocol and schema caches."""
        self._protocol_cache.clear()
        self._schema_cache.clear()
        logger.info("Protocol and schema caches cleared")
