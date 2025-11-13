"""Protocol loader for JSON-based protocol definitions."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class ProtocolLoader:
    """Loads and manages protocol definitions from JSON files."""

    def __init__(self, protocols_dir: str = "protocols"):
        """Initialize protocol loader.

        Args:
            protocols_dir: Root directory containing protocol definitions
        """
        self.protocols_dir = Path(protocols_dir)
        self._protocol_cache: Dict[str, Dict[str, Any]] = {}

    def load(self, protocol_id: str) -> Dict[str, Any]:
        """Load a protocol definition by ID.

        Args:
            protocol_id: Protocol identifier (e.g., 'PERF-002')

        Returns:
            Protocol definition as dictionary

        Raises:
            FileNotFoundError: If protocol file not found
            json.JSONDecodeError: If protocol file is invalid JSON
        """
        # Check cache first
        if protocol_id in self._protocol_cache:
            return self._protocol_cache[protocol_id]

        # Determine protocol category and path
        category = self._get_category_from_id(protocol_id)
        protocol_path = self.protocols_dir / category / protocol_id / "protocol.json"

        if not protocol_path.exists():
            raise FileNotFoundError(f"Protocol {protocol_id} not found at {protocol_path}")

        # Load protocol
        with open(protocol_path, 'r') as f:
            protocol = json.load(f)

        # Validate required fields
        self._validate_protocol_structure(protocol)

        # Cache and return
        self._protocol_cache[protocol_id] = protocol
        return protocol

    def load_schema(self, protocol_id: str) -> Dict[str, Any]:
        """Load validation schema for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            JSON Schema definition

        Raises:
            FileNotFoundError: If schema file not found
        """
        category = self._get_category_from_id(protocol_id)
        schema_path = self.protocols_dir / category / protocol_id / "schema.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema for {protocol_id} not found at {schema_path}")

        with open(schema_path, 'r') as f:
            schema = json.load(f)

        return schema

    def list_protocols(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available protocols.

        Args:
            category: Optional category filter (e.g., 'PERF')

        Returns:
            List of protocol summaries
        """
        protocols = []

        # Determine search directories
        if category:
            search_dirs = [self.protocols_dir / category]
        else:
            # Search all category directories
            search_dirs = [d for d in self.protocols_dir.iterdir() if d.is_dir()]

        for category_dir in search_dirs:
            if not category_dir.is_dir():
                continue

            for protocol_dir in category_dir.iterdir():
                if not protocol_dir.is_dir():
                    continue

                protocol_file = protocol_dir / "protocol.json"
                if protocol_file.exists():
                    try:
                        with open(protocol_file, 'r') as f:
                            protocol = json.load(f)

                        protocols.append({
                            'protocol_id': protocol.get('protocol_id'),
                            'name': protocol.get('name'),
                            'version': protocol.get('version'),
                            'category': protocol.get('category'),
                            'description': protocol.get('description', ''),
                            'path': str(protocol_dir)
                        })
                    except (json.JSONDecodeError, KeyError):
                        continue

        return sorted(protocols, key=lambda x: x['protocol_id'])

    def get_irradiance_levels(self, protocol_id: str) -> List[float]:
        """Get irradiance levels defined in protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of irradiance levels in W/m²
        """
        protocol = self.load(protocol_id)
        test_config = protocol.get('test_configuration', {})
        irradiance_levels = test_config.get('irradiance_levels', [])

        return [level['level'] for level in irradiance_levels]

    def get_required_equipment(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get required equipment for protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of equipment specifications
        """
        protocol = self.load(protocol_id)
        test_config = protocol.get('test_configuration', {})
        return test_config.get('equipment_required', [])

    def get_data_fields(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get data collection fields for protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of field definitions
        """
        protocol = self.load(protocol_id)
        data_collection = protocol.get('data_collection', {})
        return data_collection.get('fields', [])

    def get_qc_checks(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get QC checks for protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of QC check definitions
        """
        protocol = self.load(protocol_id)
        return protocol.get('qc_checks', [])

    def get_calculations(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get analysis calculations for protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of calculation definitions
        """
        protocol = self.load(protocol_id)
        analysis = protocol.get('analysis', {})
        return analysis.get('calculations', [])

    def get_visualizations(self, protocol_id: str) -> List[Dict[str, Any]]:
        """Get visualization configurations for protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            List of chart definitions
        """
        protocol = self.load(protocol_id)
        visualization = protocol.get('visualization', {})
        return visualization.get('charts', [])

    def _get_category_from_id(self, protocol_id: str) -> str:
        """Extract category from protocol ID.

        Args:
            protocol_id: Protocol identifier (e.g., 'PERF-002')

        Returns:
            Category name (e.g., 'PERF')
        """
        return protocol_id.split('-')[0]

    def _validate_protocol_structure(self, protocol: Dict[str, Any]) -> None:
        """Validate that protocol has required top-level fields.

        Args:
            protocol: Protocol definition

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            'protocol_id',
            'version',
            'name',
            'category',
            'test_configuration',
            'data_collection',
            'analysis',
            'qc_checks',
            'visualization'
        ]

        missing_fields = [field for field in required_fields if field not in protocol]

        if missing_fields:
            raise ValueError(
                f"Protocol missing required fields: {', '.join(missing_fields)}"
            )

    def reload(self, protocol_id: str) -> Dict[str, Any]:
        """Force reload protocol from disk (bypass cache).

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol definition
        """
        if protocol_id in self._protocol_cache:
            del self._protocol_cache[protocol_id]

        return self.load(protocol_id)

    def clear_cache(self) -> None:
        """Clear protocol cache."""
        self._protocol_cache.clear()


# Global instance
_protocol_loader: Optional[ProtocolLoader] = None


def get_protocol_loader() -> ProtocolLoader:
    """Get global protocol loader instance.

    Returns:
        ProtocolLoader instance
    """
    global _protocol_loader
    if _protocol_loader is None:
        _protocol_loader = ProtocolLoader()
    return _protocol_loader
