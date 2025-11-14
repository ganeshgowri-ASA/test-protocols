"""
Protocol Registry - Dynamic Protocol Loading and Management
==========================================================
Centralized registry for all 54 testing protocols with auto-discovery.
"""

import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import streamlit as st

from config.settings import config, PROTOCOLS_DIR


@dataclass
class ProtocolMetadata:
    """Protocol metadata structure"""
    protocol_id: str  # P1, P2, etc.
    name: str
    category: str  # performance, degradation, environmental, mechanical, safety
    description: str
    standard_reference: str  # IEC standard
    version: str = "1.0.0"
    is_active: bool = True

    # Technical details
    estimated_duration_hours: float = 0.0
    required_equipment: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    # Module information
    module_path: Optional[str] = None
    json_template_path: Optional[str] = None

    # Functions - will be set by the registry
    render_form: Optional[Callable] = None
    validate_inputs: Optional[Callable] = None
    execute_test: Optional[Callable] = None
    generate_visualizations: Optional[Callable] = None
    calculate_results: Optional[Callable] = None
    generate_report: Optional[Callable] = None


class ProtocolRegistry:
    """
    Central registry for all testing protocols.
    Handles dynamic loading, validation, and access to protocols.
    """

    def __init__(self):
        self._protocols: Dict[str, ProtocolMetadata] = {}
        self._categories: Dict[str, List[str]] = {
            "performance": [],
            "degradation": [],
            "environmental": [],
            "mechanical": [],
            "safety": []
        }
        self._loaded = False

    def register_protocol(self, metadata: ProtocolMetadata):
        """
        Register a protocol in the registry

        Args:
            metadata: ProtocolMetadata instance
        """
        self._protocols[metadata.protocol_id] = metadata

        # Add to category
        if metadata.category in self._categories:
            if metadata.protocol_id not in self._categories[metadata.category]:
                self._categories[metadata.category].append(metadata.protocol_id)

    def register_from_json(self, json_path: Path):
        """
        Register a protocol from JSON template

        Args:
            json_path: Path to protocol JSON template
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            metadata = ProtocolMetadata(
                protocol_id=data.get('protocol_id'),
                name=data.get('name'),
                category=data.get('category'),
                description=data.get('description', ''),
                standard_reference=data.get('standard_reference', ''),
                version=data.get('version', '1.0.0'),
                is_active=data.get('is_active', True),
                estimated_duration_hours=data.get('estimated_duration_hours', 0.0),
                required_equipment=data.get('required_equipment', []),
                prerequisites=data.get('prerequisites', []),
                json_template_path=str(json_path)
            )

            self.register_protocol(metadata)
            return True

        except Exception as e:
            print(f"Error loading protocol from {json_path}: {e}")
            return False

    def register_from_module(self, module_path: str):
        """
        Register a protocol from a Python module

        Args:
            module_path: Python module path (e.g., 'protocols.performance.p1_iv_performance')
        """
        try:
            module = importlib.import_module(module_path)

            # Get metadata from module
            if hasattr(module, 'get_metadata'):
                metadata_dict = module.get_metadata()
                metadata = ProtocolMetadata(**metadata_dict)
                metadata.module_path = module_path

                # Attach functions
                if hasattr(module, 'render_form'):
                    metadata.render_form = module.render_form
                if hasattr(module, 'validate_inputs'):
                    metadata.validate_inputs = module.validate_inputs
                if hasattr(module, 'execute_test'):
                    metadata.execute_test = module.execute_test
                if hasattr(module, 'generate_visualizations'):
                    metadata.generate_visualizations = module.generate_visualizations
                if hasattr(module, 'calculate_results'):
                    metadata.calculate_results = module.calculate_results
                if hasattr(module, 'generate_report'):
                    metadata.generate_report = module.generate_report

                self.register_protocol(metadata)
                return True

        except Exception as e:
            print(f"Error loading protocol from module {module_path}: {e}")
            return False

    def auto_discover_protocols(self):
        """
        Auto-discover and load all protocols from the protocols directory
        """
        # Discover JSON templates
        for json_file in PROTOCOLS_DIR.rglob("*.json"):
            self.register_from_json(json_file)

        # Discover Python modules
        for py_file in PROTOCOLS_DIR.rglob("*.py"):
            if py_file.name.startswith("p") and py_file.name != "__init__.py":
                # Convert path to module name
                relative_path = py_file.relative_to(PROTOCOLS_DIR.parent)
                module_path = str(relative_path.with_suffix('')).replace('/', '.')
                self.register_from_module(module_path)

        self._loaded = True

    def get_protocol(self, protocol_id: str) -> Optional[ProtocolMetadata]:
        """
        Get protocol metadata by ID

        Args:
            protocol_id: Protocol identifier (e.g., "P1")

        Returns:
            ProtocolMetadata or None if not found
        """
        return self._protocols.get(protocol_id)

    def get_protocols_by_category(self, category: str) -> List[ProtocolMetadata]:
        """
        Get all protocols in a category

        Args:
            category: Category name

        Returns:
            List of ProtocolMetadata objects
        """
        protocol_ids = self._categories.get(category, [])
        return [self._protocols[pid] for pid in protocol_ids if pid in self._protocols]

    def get_all_protocols(self) -> List[ProtocolMetadata]:
        """
        Get all registered protocols

        Returns:
            List of all ProtocolMetadata objects
        """
        return list(self._protocols.values())

    def get_active_protocols(self) -> List[ProtocolMetadata]:
        """
        Get all active protocols

        Returns:
            List of active ProtocolMetadata objects
        """
        return [p for p in self._protocols.values() if p.is_active]

    def search_protocols(self, query: str) -> List[ProtocolMetadata]:
        """
        Search protocols by name, ID, or description

        Args:
            query: Search query string

        Returns:
            List of matching ProtocolMetadata objects
        """
        query = query.lower()
        results = []

        for protocol in self._protocols.values():
            if (query in protocol.protocol_id.lower() or
                query in protocol.name.lower() or
                query in protocol.description.lower()):
                results.append(protocol)

        return results

    def get_category_summary(self) -> Dict[str, int]:
        """
        Get summary of protocols by category

        Returns:
            Dictionary with category counts
        """
        return {
            category: len(protocols)
            for category, protocols in self._categories.items()
        }

    def validate_prerequisites(self, protocol_id: str, completed_protocols: List[str]) -> tuple[bool, List[str]]:
        """
        Validate if prerequisites are met for a protocol

        Args:
            protocol_id: Protocol to validate
            completed_protocols: List of completed protocol IDs

        Returns:
            Tuple of (is_valid, missing_prerequisites)
        """
        protocol = self.get_protocol(protocol_id)
        if not protocol or not protocol.prerequisites:
            return True, []

        missing = [p for p in protocol.prerequisites if p not in completed_protocols]
        return len(missing) == 0, missing

    def is_loaded(self) -> bool:
        """Check if protocols have been loaded"""
        return self._loaded

    def get_protocol_count(self) -> int:
        """Get total number of registered protocols"""
        return len(self._protocols)


# Global registry instance
_registry = None


def get_protocol_registry() -> ProtocolRegistry:
    """
    Get the global protocol registry (singleton pattern)

    Returns:
        ProtocolRegistry instance
    """
    global _registry

    if _registry is None:
        _registry = ProtocolRegistry()

        # Auto-discover protocols on first access
        if not _registry.is_loaded():
            _registry.auto_discover_protocols()

            # Register sample protocols if none found
            if _registry.get_protocol_count() == 0:
                register_sample_protocols(_registry)

    return _registry


def register_sample_protocols(registry: ProtocolRegistry):
    """
    Register sample protocol definitions for demonstration
    This will be replaced by actual protocol implementations
    """

    # Sample protocols for each category
    sample_protocols = [
        # Performance (P1-P12)
        {
            "protocol_id": "P1",
            "name": "I-V Performance Characterization",
            "category": "performance",
            "description": "Measure current-voltage characteristics under STC",
            "standard_reference": "IEC 61215-2:2021",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer"]
        },
        {
            "protocol_id": "P2",
            "name": "P-V Performance Analysis",
            "category": "performance",
            "description": "Power-voltage characteristic measurement",
            "standard_reference": "IEC 61215-2:2021",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer"]
        },

        # Degradation (P13-P27)
        {
            "protocol_id": "P13",
            "name": "Light-Induced Degradation (LID)",
            "category": "degradation",
            "description": "Assess power degradation under light exposure",
            "standard_reference": "IEC 61215-2:2021 MQT 19",
            "estimated_duration_hours": 48.0,
            "required_equipment": ["solar_simulator", "climate_chamber"]
        },

        # Environmental (P28-P39)
        {
            "protocol_id": "P28",
            "name": "Humidity Freeze Test",
            "category": "environmental",
            "description": "Assess module resistance to humidity freeze cycles",
            "standard_reference": "IEC 61215-2:2021 MQT 12",
            "estimated_duration_hours": 240.0,
            "required_equipment": ["climate_chamber"]
        },

        # Mechanical (P40-P47)
        {
            "protocol_id": "P40",
            "name": "Mechanical Load Test",
            "category": "mechanical",
            "description": "Assess module resistance to mechanical loads",
            "standard_reference": "IEC 61215-2:2021 MQT 16",
            "estimated_duration_hours": 8.0,
            "required_equipment": ["mechanical_load_tester"]
        },

        # Safety (P48-P54)
        {
            "protocol_id": "P48",
            "name": "Wet Leakage Current Test",
            "category": "safety",
            "description": "Measure leakage current under wet conditions",
            "standard_reference": "IEC 61215-2:2021 MQT 15",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["insulation_tester", "climate_chamber"]
        },
    ]

    for protocol_data in sample_protocols:
        metadata = ProtocolMetadata(**protocol_data)
        registry.register_protocol(metadata)


# Cache protocol registry in Streamlit session
@st.cache_resource
def get_cached_protocol_registry() -> ProtocolRegistry:
    """Get cached protocol registry for Streamlit"""
    return get_protocol_registry()
