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
    Register all 54 protocol definitions for Solar PV Testing
    Based on IEC 61215, IEC 61730, and related standards
    """

    # All 54 protocols organized by category
    all_protocols = [
        # =============================================
        # PERFORMANCE TESTING (P1-P12) - 12 protocols
        # =============================================
        {
            "protocol_id": "P1",
            "name": "I-V Performance Characterization",
            "category": "performance",
            "description": "Measure current-voltage characteristics under STC (Standard Test Conditions)",
            "standard_reference": "IEC 61215-2:2021 MQT 06",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer"]
        },
        {
            "protocol_id": "P2",
            "name": "P-V Performance Analysis",
            "category": "performance",
            "description": "Power-voltage characteristic measurement and maximum power point analysis",
            "standard_reference": "IEC 61215-2:2021 MQT 06",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer"]
        },
        {
            "protocol_id": "P3",
            "name": "STC Power Rating",
            "category": "performance",
            "description": "Power rating at Standard Test Conditions (1000 W/m², 25°C, AM1.5G)",
            "standard_reference": "IEC 61215-1:2021",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer", "reference_cell"]
        },
        {
            "protocol_id": "P4",
            "name": "NOCT Determination",
            "category": "performance",
            "description": "Nominal Operating Cell Temperature determination",
            "standard_reference": "IEC 61215-2:2021 MQT 05",
            "estimated_duration_hours": 8.0,
            "required_equipment": ["outdoor_test_stand", "temperature_sensors", "pyranometer"]
        },
        {
            "protocol_id": "P5",
            "name": "Temperature Coefficient Measurement",
            "category": "performance",
            "description": "Determine temperature coefficients for Isc, Voc, and Pmax",
            "standard_reference": "IEC 61215-2:2021 MQT 04",
            "estimated_duration_hours": 6.0,
            "required_equipment": ["solar_simulator", "climate_chamber", "iv_tracer"]
        },
        {
            "protocol_id": "P6",
            "name": "Low Irradiance Performance",
            "category": "performance",
            "description": "Performance measurement at 200 W/m² irradiance",
            "standard_reference": "IEC 61215-2:2021 MQT 07",
            "estimated_duration_hours": 3.0,
            "required_equipment": ["solar_simulator", "iv_tracer"]
        },
        {
            "protocol_id": "P7",
            "name": "Performance Matrix Test",
            "category": "performance",
            "description": "Multi-condition performance mapping (IEC 61853-1)",
            "standard_reference": "IEC 61853-1:2011",
            "estimated_duration_hours": 24.0,
            "required_equipment": ["solar_simulator", "climate_chamber", "iv_tracer"]
        },
        {
            "protocol_id": "P8",
            "name": "Spectral Response Measurement",
            "category": "performance",
            "description": "Measure spectral response and quantum efficiency",
            "standard_reference": "IEC 60904-8:2014",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["spectral_response_system", "monochromator"]
        },
        {
            "protocol_id": "P9",
            "name": "Incidence Angle Modifier (IAM)",
            "category": "performance",
            "description": "Measure power output vs. angle of incidence",
            "standard_reference": "IEC 61853-2:2016",
            "estimated_duration_hours": 6.0,
            "required_equipment": ["solar_simulator", "rotatable_mount", "iv_tracer"]
        },
        {
            "protocol_id": "P10",
            "name": "Bifacial Performance Test",
            "category": "performance",
            "description": "Characterization of bifacial module performance and bifaciality factor",
            "standard_reference": "IEC TS 60904-1-2:2019",
            "estimated_duration_hours": 8.0,
            "required_equipment": ["solar_simulator", "iv_tracer", "albedo_reflector"]
        },
        {
            "protocol_id": "P11",
            "name": "Energy Rating Test",
            "category": "performance",
            "description": "Energy yield prediction and rating under reference conditions",
            "standard_reference": "IEC 61853-3:2018",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["solar_simulator", "iv_tracer", "energy_rating_software"]
        },
        {
            "protocol_id": "P12",
            "name": "Bypass Diode Functionality",
            "category": "performance",
            "description": "Verify bypass diode operation under partial shading",
            "standard_reference": "IEC 61215-2:2021 MQT 18",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["solar_simulator", "iv_tracer", "thermal_camera"]
        },

        # =============================================
        # DEGRADATION TESTING (P13-P27) - 15 protocols
        # =============================================
        {
            "protocol_id": "P13",
            "name": "Light-Induced Degradation (LID)",
            "category": "degradation",
            "description": "Assess power degradation under continuous light exposure",
            "standard_reference": "IEC 61215-2:2021 MQT 19",
            "estimated_duration_hours": 48.0,
            "required_equipment": ["solar_simulator", "climate_chamber"]
        },
        {
            "protocol_id": "P14",
            "name": "Light & Elevated Temperature ID (LETID)",
            "category": "degradation",
            "description": "Light and elevated temperature induced degradation test",
            "standard_reference": "IEC TS 63202-1:2021",
            "estimated_duration_hours": 162.0,
            "required_equipment": ["solar_simulator", "climate_chamber", "iv_tracer"]
        },
        {
            "protocol_id": "P15",
            "name": "Potential-Induced Degradation (PID)",
            "category": "degradation",
            "description": "Test for voltage stress induced degradation",
            "standard_reference": "IEC TS 62804-1:2015",
            "estimated_duration_hours": 96.0,
            "required_equipment": ["pid_test_chamber", "high_voltage_source"]
        },
        {
            "protocol_id": "P16",
            "name": "PID Recovery Test",
            "category": "degradation",
            "description": "Evaluate PID reversibility under recovery conditions",
            "standard_reference": "IEC TS 62804-1:2015",
            "estimated_duration_hours": 48.0,
            "required_equipment": ["pid_test_chamber", "high_voltage_source"]
        },
        {
            "protocol_id": "P17",
            "name": "UV Degradation Test",
            "category": "degradation",
            "description": "Assess degradation from UV exposure (UV preconditioning)",
            "standard_reference": "IEC 61215-2:2021 MQT 10",
            "estimated_duration_hours": 120.0,
            "required_equipment": ["uv_exposure_chamber", "uv_lamp_array"]
        },
        {
            "protocol_id": "P18",
            "name": "Hot Spot Endurance Test",
            "category": "degradation",
            "description": "Verify module resilience to localized heating (hot spots)",
            "standard_reference": "IEC 61215-2:2021 MQT 09",
            "estimated_duration_hours": 5.0,
            "required_equipment": ["solar_simulator", "thermal_camera", "shading_masks"]
        },
        {
            "protocol_id": "P19",
            "name": "Snail Trail Assessment",
            "category": "degradation",
            "description": "Visual and electrical assessment of snail trail formation",
            "standard_reference": "IEC 62759-1:2015",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["el_imaging_system", "visual_inspection_station"]
        },
        {
            "protocol_id": "P20",
            "name": "Cell Crack Detection",
            "category": "degradation",
            "description": "Electroluminescence imaging for micro-crack detection",
            "standard_reference": "IEC TS 60904-13:2018",
            "estimated_duration_hours": 1.0,
            "required_equipment": ["el_imaging_system", "power_supply"]
        },
        {
            "protocol_id": "P21",
            "name": "Solder Bond Degradation",
            "category": "degradation",
            "description": "Evaluate solder joint integrity and interconnect degradation",
            "standard_reference": "IEC 61215-1:2021",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["el_imaging_system", "thermal_camera"]
        },
        {
            "protocol_id": "P22",
            "name": "Delamination Assessment",
            "category": "degradation",
            "description": "Identify and quantify delamination in module layers",
            "standard_reference": "IEC 61215-1:2021",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["visual_inspection_station", "el_imaging_system"]
        },
        {
            "protocol_id": "P23",
            "name": "Yellowing/Browning Test",
            "category": "degradation",
            "description": "Assess encapsulant discoloration and its effect on performance",
            "standard_reference": "IEC 62788-1-6:2017",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["colorimeter", "spectrophotometer"]
        },
        {
            "protocol_id": "P24",
            "name": "Corrosion Assessment",
            "category": "degradation",
            "description": "Evaluate corrosion of metallic components and interconnects",
            "standard_reference": "IEC 61701:2020",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["visual_inspection_station", "multimeter"]
        },
        {
            "protocol_id": "P25",
            "name": "Backsheet Chalking Test",
            "category": "degradation",
            "description": "Assess backsheet surface degradation and chalking",
            "standard_reference": "IEC 62788-2-1:2021",
            "estimated_duration_hours": 1.0,
            "required_equipment": ["adhesion_tester", "visual_inspection_station"]
        },
        {
            "protocol_id": "P26",
            "name": "Junction Box Degradation",
            "category": "degradation",
            "description": "Evaluate junction box integrity and connector condition",
            "standard_reference": "IEC 62790:2020",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["insulation_tester", "multimeter"]
        },
        {
            "protocol_id": "P27",
            "name": "Long-term Outdoor Exposure",
            "category": "degradation",
            "description": "Natural weathering and outdoor degradation monitoring",
            "standard_reference": "IEC 61215-1:2021",
            "estimated_duration_hours": 8760.0,
            "required_equipment": ["outdoor_test_rack", "weather_station", "data_logger"]
        },

        # =============================================
        # ENVIRONMENTAL TESTING (P28-P39) - 12 protocols
        # =============================================
        {
            "protocol_id": "P28",
            "name": "Humidity Freeze Test",
            "category": "environmental",
            "description": "Assess module resistance to humidity freeze cycles (10 cycles)",
            "standard_reference": "IEC 61215-2:2021 MQT 12",
            "estimated_duration_hours": 240.0,
            "required_equipment": ["climate_chamber"]
        },
        {
            "protocol_id": "P29",
            "name": "Damp Heat Test (1000h)",
            "category": "environmental",
            "description": "Exposure to 85°C/85% RH for 1000 hours",
            "standard_reference": "IEC 61215-2:2021 MQT 13",
            "estimated_duration_hours": 1000.0,
            "required_equipment": ["climate_chamber"]
        },
        {
            "protocol_id": "P30",
            "name": "Damp Heat Extended (2000h)",
            "category": "environmental",
            "description": "Extended damp heat test for enhanced durability",
            "standard_reference": "IEC 61215-2:2021",
            "estimated_duration_hours": 2000.0,
            "required_equipment": ["climate_chamber"]
        },
        {
            "protocol_id": "P31",
            "name": "Thermal Cycling Test (200 cycles)",
            "category": "environmental",
            "description": "Temperature cycling from -40°C to +85°C (200 cycles)",
            "standard_reference": "IEC 61215-2:2021 MQT 11",
            "estimated_duration_hours": 800.0,
            "required_equipment": ["thermal_cycling_chamber"]
        },
        {
            "protocol_id": "P32",
            "name": "Salt Mist Corrosion Test",
            "category": "environmental",
            "description": "Exposure to salt spray for coastal environment simulation",
            "standard_reference": "IEC 61701:2020",
            "estimated_duration_hours": 500.0,
            "required_equipment": ["salt_spray_chamber"]
        },
        {
            "protocol_id": "P33",
            "name": "Ammonia Corrosion Test",
            "category": "environmental",
            "description": "Ammonia exposure for agricultural environment simulation",
            "standard_reference": "IEC 62716:2013",
            "estimated_duration_hours": 500.0,
            "required_equipment": ["ammonia_test_chamber"]
        },
        {
            "protocol_id": "P34",
            "name": "Sand/Dust Abrasion Test",
            "category": "environmental",
            "description": "Sand and dust abrasion resistance testing",
            "standard_reference": "IEC 60068-2-68:1994",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["sand_dust_chamber"]
        },
        {
            "protocol_id": "P35",
            "name": "SO2/H2S Corrosion Test",
            "category": "environmental",
            "description": "Sulfur dioxide and hydrogen sulfide exposure",
            "standard_reference": "IEC 60068-2-42:2003",
            "estimated_duration_hours": 240.0,
            "required_equipment": ["corrosive_gas_chamber"]
        },
        {
            "protocol_id": "P36",
            "name": "Desert Climate Simulation",
            "category": "environmental",
            "description": "High temperature, low humidity, and UV stress testing",
            "standard_reference": "IEC 62892:2019",
            "estimated_duration_hours": 720.0,
            "required_equipment": ["climate_chamber", "uv_lamp_array"]
        },
        {
            "protocol_id": "P37",
            "name": "Tropical Climate Simulation",
            "category": "environmental",
            "description": "High humidity and temperature cycling for tropical environments",
            "standard_reference": "IEC 62892:2019",
            "estimated_duration_hours": 720.0,
            "required_equipment": ["climate_chamber"]
        },
        {
            "protocol_id": "P38",
            "name": "Snow Load Test",
            "category": "environmental",
            "description": "Static load test simulating accumulated snow",
            "standard_reference": "IEC 61215-2:2021 MQT 16",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["mechanical_load_tester"]
        },
        {
            "protocol_id": "P39",
            "name": "UV Exposure Test",
            "category": "environmental",
            "description": "Accelerated UV exposure (15 kWh/m² minimum)",
            "standard_reference": "IEC 61215-2:2021 MQT 10",
            "estimated_duration_hours": 120.0,
            "required_equipment": ["uv_exposure_chamber"]
        },

        # =============================================
        # MECHANICAL TESTING (P40-P47) - 8 protocols
        # =============================================
        {
            "protocol_id": "P40",
            "name": "Mechanical Load Test",
            "category": "mechanical",
            "description": "Static and cyclic mechanical load testing (2400 Pa / 5400 Pa)",
            "standard_reference": "IEC 61215-2:2021 MQT 16",
            "estimated_duration_hours": 8.0,
            "required_equipment": ["mechanical_load_tester"]
        },
        {
            "protocol_id": "P41",
            "name": "Dynamic Mechanical Load",
            "category": "mechanical",
            "description": "Dynamic loading cycles (1000 cycles at 1000 Pa)",
            "standard_reference": "IEC TS 62782:2016",
            "estimated_duration_hours": 24.0,
            "required_equipment": ["dynamic_load_tester"]
        },
        {
            "protocol_id": "P42",
            "name": "Hail Impact Test",
            "category": "mechanical",
            "description": "Impact resistance test with ice balls (25mm @ 23 m/s)",
            "standard_reference": "IEC 61215-2:2021 MQT 17",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["hail_impact_tester"]
        },
        {
            "protocol_id": "P43",
            "name": "Wind Load Simulation",
            "category": "mechanical",
            "description": "Cyclic wind load simulation for structural integrity",
            "standard_reference": "IEC 61215-2:2021 MQT 16",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["mechanical_load_tester"]
        },
        {
            "protocol_id": "P44",
            "name": "Module Twist Test",
            "category": "mechanical",
            "description": "Torsional stress test for frame and laminate integrity",
            "standard_reference": "IEC 62892:2019",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["twist_test_fixture"]
        },
        {
            "protocol_id": "P45",
            "name": "Vibration Test",
            "category": "mechanical",
            "description": "Transportation and installation vibration simulation",
            "standard_reference": "IEC 60068-2-6:2007",
            "estimated_duration_hours": 6.0,
            "required_equipment": ["vibration_table"]
        },
        {
            "protocol_id": "P46",
            "name": "Frame/Mounting Stress Test",
            "category": "mechanical",
            "description": "Mounting point load test and frame integrity verification",
            "standard_reference": "IEC 61215-2:2021",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["mechanical_load_tester"]
        },
        {
            "protocol_id": "P47",
            "name": "Robustness of Terminations",
            "category": "mechanical",
            "description": "Pull and push test on cables and connectors",
            "standard_reference": "IEC 61215-2:2021 MQT 14",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["force_gauge", "pull_tester"]
        },

        # =============================================
        # SAFETY & ELECTRICAL TESTING (P48-P54) - 7 protocols
        # =============================================
        {
            "protocol_id": "P48",
            "name": "Wet Leakage Current Test",
            "category": "safety",
            "description": "Measure leakage current under wet conditions",
            "standard_reference": "IEC 61215-2:2021 MQT 15",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["insulation_tester", "wetting_system"]
        },
        {
            "protocol_id": "P49",
            "name": "Insulation Resistance Test",
            "category": "safety",
            "description": "Dry insulation resistance measurement (1000V DC)",
            "standard_reference": "IEC 61215-2:2021 MQT 03",
            "estimated_duration_hours": 1.0,
            "required_equipment": ["insulation_tester"]
        },
        {
            "protocol_id": "P50",
            "name": "Dielectric Withstand Test",
            "category": "safety",
            "description": "High voltage insulation test (system voltage + 1000V)",
            "standard_reference": "IEC 61730-2:2016 MST 16",
            "estimated_duration_hours": 1.0,
            "required_equipment": ["hipot_tester"]
        },
        {
            "protocol_id": "P51",
            "name": "Ground Continuity Test",
            "category": "safety",
            "description": "Frame grounding and continuity verification",
            "standard_reference": "IEC 61730-2:2016 MST 13",
            "estimated_duration_hours": 0.5,
            "required_equipment": ["continuity_tester"]
        },
        {
            "protocol_id": "P52",
            "name": "Fire Resistance Test",
            "category": "safety",
            "description": "Spread of flame test for building-integrated applications",
            "standard_reference": "IEC 61730-2:2016 MST 23-25",
            "estimated_duration_hours": 4.0,
            "required_equipment": ["fire_test_apparatus"]
        },
        {
            "protocol_id": "P53",
            "name": "Reverse Current Overload",
            "category": "safety",
            "description": "Bypass diode thermal test under reverse current",
            "standard_reference": "IEC 61215-2:2021 MQT 18",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["power_supply", "thermal_camera"]
        },
        {
            "protocol_id": "P54",
            "name": "Impulse Voltage Test",
            "category": "safety",
            "description": "Lightning impulse withstand test (1.2/50 μs)",
            "standard_reference": "IEC 61730-2:2016 MST 14",
            "estimated_duration_hours": 2.0,
            "required_equipment": ["impulse_voltage_generator"]
        },
    ]

    for protocol_data in all_protocols:
        metadata = ProtocolMetadata(**protocol_data)
        registry.register_protocol(metadata)


# Cache protocol registry in Streamlit session
@st.cache_resource
def get_cached_protocol_registry() -> ProtocolRegistry:
    """Get cached protocol registry for Streamlit"""
    return get_protocol_registry()
