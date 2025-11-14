"""Protocol loader and validator for JSON-based test protocols."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import jsonschema

logger = logging.getLogger(__name__)


class ProtocolLoader:
    """Loads and validates test protocol definitions from JSON files."""

    def __init__(self, protocols_dir: Optional[Path] = None, schema_path: Optional[Path] = None):
        """Initialize the protocol loader.

        Args:
            protocols_dir: Directory containing protocol JSON files
            schema_path: Path to JSON schema file for validation
        """
        if protocols_dir is None:
            # Default to protocols directory in project root
            self.protocols_dir = Path(__file__).parent.parent.parent / 'protocols'
        else:
            self.protocols_dir = Path(protocols_dir)

        if schema_path is None:
            self.schema_path = self.protocols_dir / 'schema' / 'protocol-schema.json'
        else:
            self.schema_path = Path(schema_path)

        self.schema = self._load_schema()

        logger.info(f"ProtocolLoader initialized with protocols_dir: {self.protocols_dir}")

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema for protocol validation.

        Returns:
            Schema dictionary

        Raises:
            FileNotFoundError: If schema file not found
        """
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found: {self.schema_path}")
            return {}

        with open(self.schema_path, 'r') as f:
            schema = json.load(f)

        logger.info(f"Loaded protocol schema from {self.schema_path}")
        return schema

    def load_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """Load a protocol definition by ID.

        Args:
            protocol_id: Protocol identifier (e.g., 'SEAL-001')

        Returns:
            Protocol definition dictionary

        Raises:
            FileNotFoundError: If protocol file not found
            jsonschema.ValidationError: If protocol doesn't match schema
        """
        # Search for protocol file
        protocol_file = self._find_protocol_file(protocol_id)

        if not protocol_file:
            raise FileNotFoundError(f"Protocol {protocol_id} not found in {self.protocols_dir}")

        # Load protocol JSON
        with open(protocol_file, 'r') as f:
            protocol_def = json.load(f)

        logger.info(f"Loaded protocol {protocol_id} from {protocol_file}")

        # Validate against schema
        if self.schema:
            self.validate_protocol(protocol_def)

        return protocol_def

    def _find_protocol_file(self, protocol_id: str) -> Optional[Path]:
        """Find protocol file by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Path to protocol file, or None if not found
        """
        # Search in all subdirectories
        for json_file in self.protocols_dir.rglob('*.json'):
            # Skip schema files
            if 'schema' in json_file.parts:
                continue

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if data.get('protocol_id') == protocol_id:
                        return json_file
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def validate_protocol(self, protocol_def: Dict[str, Any]) -> None:
        """Validate protocol definition against schema.

        Args:
            protocol_def: Protocol definition to validate

        Raises:
            jsonschema.ValidationError: If validation fails
        """
        if not self.schema:
            logger.warning("No schema available for validation")
            return

        try:
            jsonschema.validate(instance=protocol_def, schema=self.schema)
            logger.info(f"Protocol {protocol_def.get('protocol_id')} validated successfully")
        except jsonschema.ValidationError as e:
            logger.error(f"Protocol validation failed: {e.message}")
            raise

    def list_protocols(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available protocols.

        Args:
            category: Optional category filter (e.g., 'degradation')

        Returns:
            List of protocol summary dictionaries
        """
        protocols = []

        for json_file in self.protocols_dir.rglob('*.json'):
            # Skip schema files
            if 'schema' in json_file.parts:
                continue

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                    # Filter by category if specified
                    if category and data.get('category', '').lower() != category.lower():
                        continue

                    protocols.append({
                        'protocol_id': data.get('protocol_id'),
                        'name': data.get('name'),
                        'version': data.get('version'),
                        'category': data.get('category'),
                        'description': data.get('description'),
                        'file_path': str(json_file)
                    })

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error reading protocol file {json_file}: {e}")
                continue

        logger.info(f"Found {len(protocols)} protocols" + (f" in category '{category}'" if category else ""))

        return protocols

    def get_protocol_instance(self, protocol_id: str):
        """Load protocol and instantiate appropriate protocol class.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol instance (BaseProtocol subclass)

        Raises:
            ValueError: If protocol type not recognized
        """
        protocol_def = self.load_protocol(protocol_id)

        # Import appropriate protocol class based on protocol_id
        if protocol_id == 'SEAL-001':
            from ..protocols.degradation.seal_001 import SEAL001Protocol
            return SEAL001Protocol(protocol_def)

        # Add more protocol types here as they are implemented
        # elif protocol_id.startswith('CORR-'):
        #     from ..protocols.degradation.corrosion import CorrosionProtocol
        #     return CorrosionProtocol(protocol_def)

        else:
            # Fall back to base protocol (if abstract methods implemented)
            from ..protocols.base_protocol import BaseProtocol
            logger.warning(
                f"No specific implementation for {protocol_id}, "
                f"using BaseProtocol"
            )
            raise ValueError(
                f"No implementation available for protocol {protocol_id}"
            )

    def validate_all_protocols(self) -> Dict[str, Any]:
        """Validate all protocol files against schema.

        Returns:
            Dictionary with validation results
        """
        results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for json_file in self.protocols_dir.rglob('*.json'):
            # Skip schema files
            if 'schema' in json_file.parts:
                continue

            results['total'] += 1

            try:
                with open(json_file, 'r') as f:
                    protocol_def = json.load(f)

                self.validate_protocol(protocol_def)
                results['valid'] += 1

            except jsonschema.ValidationError as e:
                results['invalid'] += 1
                results['errors'].append({
                    'file': str(json_file),
                    'error': e.message,
                    'path': list(e.path)
                })

            except Exception as e:
                results['invalid'] += 1
                results['errors'].append({
                    'file': str(json_file),
                    'error': str(e),
                    'path': []
                })

        logger.info(
            f"Validation complete: {results['valid']}/{results['total']} valid"
        )

        return results


class ProtocolRegistry:
    """Registry of available protocol implementations."""

    def __init__(self):
        """Initialize protocol registry."""
        self._protocols = {}
        self._register_builtin_protocols()

    def _register_builtin_protocols(self):
        """Register built-in protocol implementations."""
        from ..protocols.degradation.seal_001 import SEAL001Protocol

        self.register('SEAL-001', SEAL001Protocol)

        logger.info("Registered built-in protocols")

    def register(self, protocol_id: str, protocol_class):
        """Register a protocol implementation.

        Args:
            protocol_id: Protocol identifier
            protocol_class: Protocol class (BaseProtocol subclass)
        """
        self._protocols[protocol_id] = protocol_class
        logger.info(f"Registered protocol implementation: {protocol_id}")

    def get_implementation(self, protocol_id: str):
        """Get protocol implementation class.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol class

        Raises:
            KeyError: If protocol not registered
        """
        if protocol_id not in self._protocols:
            raise KeyError(f"No implementation registered for {protocol_id}")

        return self._protocols[protocol_id]

    def is_registered(self, protocol_id: str) -> bool:
        """Check if protocol is registered.

        Args:
            protocol_id: Protocol identifier

        Returns:
            True if registered
        """
        return protocol_id in self._protocols

    def list_registered(self) -> List[str]:
        """List all registered protocol IDs.

        Returns:
            List of protocol IDs
        """
        return list(self._protocols.keys())
