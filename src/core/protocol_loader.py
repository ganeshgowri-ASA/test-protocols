"""
Protocol Loader Module
======================

Loads and manages test protocol definitions from JSON files.
Provides caching, validation, and query capabilities for protocols.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProtocolMetadata:
    """Metadata for a loaded protocol"""
    protocol_id: str
    protocol_name: str
    version: str
    standard: str
    category: str
    file_path: str
    loaded_at: datetime
    is_valid: bool


class ProtocolLoader:
    """
    Protocol Loader class for loading and managing test protocol configurations.

    Features:
    - Load protocols from JSON files
    - Validate protocol structure
    - Cache loaded protocols
    - Query protocols by various criteria
    - Support for protocol versioning
    """

    def __init__(self, protocols_base_path: str = "./protocols"):
        """
        Initialize the Protocol Loader.

        Args:
            protocols_base_path: Base directory path containing protocol definitions
        """
        self.protocols_base_path = Path(protocols_base_path)
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}
        self._metadata_cache: Dict[str, ProtocolMetadata] = {}

        if not self.protocols_base_path.exists():
            logger.warning(f"Protocols directory does not exist: {self.protocols_base_path}")
            self.protocols_base_path.mkdir(parents=True, exist_ok=True)

    def load_protocol(self, protocol_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load a protocol by its ID.

        Args:
            protocol_id: Unique protocol identifier (e.g., 'DIEL-001')
            use_cache: Whether to use cached protocol if available

        Returns:
            Protocol configuration dictionary or None if not found
        """
        # Check cache first
        if use_cache and protocol_id in self._protocol_cache:
            logger.debug(f"Loading protocol {protocol_id} from cache")
            return self._protocol_cache[protocol_id]

        # Construct file path
        protocol_file = self.protocols_base_path / protocol_id / "protocol.json"

        if not protocol_file.exists():
            logger.error(f"Protocol file not found: {protocol_file}")
            return None

        try:
            with open(protocol_file, 'r', encoding='utf-8') as f:
                protocol_data = json.load(f)

            # Validate basic structure
            if not self._validate_basic_structure(protocol_data):
                logger.error(f"Invalid protocol structure for {protocol_id}")
                return None

            # Cache the protocol
            self._protocol_cache[protocol_id] = protocol_data

            # Create and cache metadata
            metadata = ProtocolMetadata(
                protocol_id=protocol_data.get('protocol_id', protocol_id),
                protocol_name=protocol_data.get('protocol_name', 'Unknown'),
                version=protocol_data.get('version', '1.0.0'),
                standard=protocol_data.get('standard', 'Unknown'),
                category=protocol_data.get('category', 'unknown'),
                file_path=str(protocol_file),
                loaded_at=datetime.now(),
                is_valid=True
            )
            self._metadata_cache[protocol_id] = metadata

            logger.info(f"Successfully loaded protocol: {protocol_id}")
            return protocol_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for protocol {protocol_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading protocol {protocol_id}: {e}")
            return None

    def load_all_protocols(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all available protocols from the protocols directory.

        Returns:
            Dictionary mapping protocol_id to protocol configuration
        """
        protocols = {}

        # Scan for protocol directories
        if not self.protocols_base_path.exists():
            logger.warning("Protocols base path does not exist")
            return protocols

        for protocol_dir in self.protocols_base_path.iterdir():
            if protocol_dir.is_dir() and not protocol_dir.name.startswith('.'):
                protocol_id = protocol_dir.name
                protocol_data = self.load_protocol(protocol_id)
                if protocol_data:
                    protocols[protocol_id] = protocol_data

        logger.info(f"Loaded {len(protocols)} protocols")
        return protocols

    def get_protocol_metadata(self, protocol_id: str) -> Optional[ProtocolMetadata]:
        """
        Get metadata for a protocol without loading full configuration.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol metadata or None
        """
        if protocol_id in self._metadata_cache:
            return self._metadata_cache[protocol_id]

        # Load protocol to populate metadata
        self.load_protocol(protocol_id)
        return self._metadata_cache.get(protocol_id)

    def list_available_protocols(self) -> List[ProtocolMetadata]:
        """
        List all available protocols.

        Returns:
            List of protocol metadata objects
        """
        # Ensure all protocols are loaded
        self.load_all_protocols()
        return list(self._metadata_cache.values())

    def get_protocols_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all protocols in a specific category.

        Args:
            category: Protocol category (e.g., 'safety', 'performance')

        Returns:
            List of protocol configurations
        """
        protocols = self.load_all_protocols()
        return [
            p for p in protocols.values()
            if p.get('category', '').lower() == category.lower()
        ]

    def get_protocols_by_standard(self, standard: str) -> List[Dict[str, Any]]:
        """
        Get all protocols for a specific standard.

        Args:
            standard: Standard identifier (e.g., 'IEC 61730')

        Returns:
            List of protocol configurations
        """
        protocols = self.load_all_protocols()
        return [
            p for p in protocols.values()
            if standard.lower() in p.get('standard', '').lower()
        ]

    def reload_protocol(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Reload a protocol from disk, bypassing cache.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Reloaded protocol configuration
        """
        # Clear from cache
        self._protocol_cache.pop(protocol_id, None)
        self._metadata_cache.pop(protocol_id, None)

        return self.load_protocol(protocol_id, use_cache=False)

    def clear_cache(self):
        """Clear all cached protocols"""
        self._protocol_cache.clear()
        self._metadata_cache.clear()
        logger.info("Protocol cache cleared")

    def get_test_parameters(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test parameters for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Test parameters dictionary
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('test_parameters', {})
        return None

    def get_acceptance_criteria(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get acceptance criteria for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Acceptance criteria dictionary
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('acceptance_criteria', {})
        return None

    def get_data_points(self, protocol_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get data point definitions for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of data point definitions
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('data_points', [])
        return None

    def get_test_procedure(self, protocol_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get test procedure steps for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of procedure steps
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('test_procedure', [])
        return None

    def get_equipment_requirements(self, protocol_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get equipment requirements for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of equipment requirements
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('equipment', [])
        return None

    def get_safety_requirements(self, protocol_id: str) -> Optional[List[str]]:
        """
        Get safety requirements for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of safety requirements
        """
        protocol = self.load_protocol(protocol_id)
        if protocol:
            return protocol.get('safety_requirements', [])
        return None

    def _validate_basic_structure(self, protocol_data: Dict[str, Any]) -> bool:
        """
        Validate basic protocol structure.

        Args:
            protocol_data: Protocol configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'protocol_id',
            'protocol_name',
            'version',
            'standard',
            'category',
            'description'
        ]

        for field in required_fields:
            if field not in protocol_data:
                logger.error(f"Missing required field: {field}")
                return False

        return True

    def validate_protocol_against_schema(
        self,
        protocol_id: str,
        schema_path: Optional[str] = None
    ) -> tuple[bool, List[str]]:
        """
        Validate protocol against JSON schema.

        Args:
            protocol_id: Protocol identifier
            schema_path: Path to JSON schema file (optional)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        try:
            import jsonschema
        except ImportError:
            logger.warning("jsonschema not installed, skipping schema validation")
            return True, []

        protocol = self.load_protocol(protocol_id)
        if not protocol:
            return False, ["Protocol not found"]

        # Load schema
        if schema_path is None:
            schema_path = self.protocols_base_path / "protocol_schema.json"

        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)

            # Validate
            jsonschema.validate(instance=protocol, schema=schema)
            return True, []

        except jsonschema.ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False, [str(e)]

    def export_protocol(
        self,
        protocol_id: str,
        output_path: str,
        include_metadata: bool = True
    ) -> bool:
        """
        Export protocol to a JSON file.

        Args:
            protocol_id: Protocol identifier
            output_path: Output file path
            include_metadata: Whether to include loader metadata

        Returns:
            True if successful, False otherwise
        """
        protocol = self.load_protocol(protocol_id)
        if not protocol:
            return False

        export_data = protocol.copy()

        if include_metadata:
            metadata = self.get_protocol_metadata(protocol_id)
            if metadata:
                export_data['_export_metadata'] = {
                    'exported_at': datetime.now().isoformat(),
                    'loaded_from': metadata.file_path,
                    'loader_version': '1.0.0'
                }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Protocol exported to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting protocol: {e}")
            return False


# Convenience functions

def load_protocol(protocol_id: str, protocols_path: str = "./protocols") -> Optional[Dict[str, Any]]:
    """
    Convenience function to load a single protocol.

    Args:
        protocol_id: Protocol identifier
        protocols_path: Base path for protocols

    Returns:
        Protocol configuration or None
    """
    loader = ProtocolLoader(protocols_path)
    return loader.load_protocol(protocol_id)


def list_protocols(protocols_path: str = "./protocols") -> List[ProtocolMetadata]:
    """
    Convenience function to list all available protocols.

    Args:
        protocols_path: Base path for protocols

    Returns:
        List of protocol metadata
    """
    loader = ProtocolLoader(protocols_path)
    return loader.list_available_protocols()
