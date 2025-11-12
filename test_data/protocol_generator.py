"""
Protocol data generator for creating synthetic test protocols.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
from faker import Faker


class ProtocolGenerator:
    """Generates synthetic protocol data for testing."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize protocol generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            random.seed(seed)
            Faker.seed(seed)

        self.fake = Faker()
        self.protocol_types = [
            "inspection", "electrical", "mechanical", "thermal",
            "environmental", "performance", "reliability", "safety"
        ]

    def generate_protocol(
        self, protocol_type: Optional[str] = None, protocol_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete protocol data structure.

        Args:
            protocol_type: Type of protocol to generate
            protocol_id: Specific protocol ID (auto-generated if None)

        Returns:
            Protocol data dictionary
        """
        protocol_type = protocol_type or random.choice(self.protocol_types)
        protocol_id = protocol_id or self._generate_protocol_id(protocol_type)

        protocol = {
            "protocol_id": protocol_id,
            "protocol_name": self._generate_protocol_name(protocol_type),
            "protocol_type": protocol_type,
            "version": f"{random.randint(1, 3)}.{random.randint(0, 9)}",
            "standard": self._generate_standard(),
            "description": self.fake.text(max_nb_chars=200),
            "parameters": self._generate_parameters(protocol_type),
            "measurements": [],
            "acceptance_criteria": self._generate_acceptance_criteria(protocol_type),
            "metadata": self._generate_metadata(),
            "status": random.choice(["pending", "in_progress", "completed"]),
        }

        return protocol

    def generate_batch(
        self, count: int, protocol_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple protocols.

        Args:
            count: Number of protocols to generate
            protocol_types: List of protocol types to use (random if None)

        Returns:
            List of protocol data dictionaries
        """
        protocols = []
        types_to_use = protocol_types or self.protocol_types

        for i in range(count):
            protocol_type = random.choice(types_to_use)
            protocol = self.generate_protocol(protocol_type=protocol_type)
            protocols.append(protocol)

        return protocols

    def _generate_protocol_id(self, protocol_type: str) -> str:
        """Generate a protocol ID."""
        prefix_map = {
            "inspection": "IEC61215-10",
            "electrical": "IEC61215-10",
            "thermal": "IEC61215-10",
            "mechanical": "IEC61215-10",
            "environmental": "IEC61215-10",
            "safety": "IEC61730-MST",
        }

        prefix = prefix_map.get(protocol_type, "CUSTOM")
        number = random.randint(1, 20)
        return f"{prefix}-{number}"

    def _generate_protocol_name(self, protocol_type: str) -> str:
        """Generate a protocol name."""
        name_templates = {
            "inspection": [
                "Visual Inspection",
                "Physical Examination",
                "Quality Control Check",
            ],
            "electrical": [
                "I-V Curve Measurement",
                "Maximum Power Determination",
                "Insulation Resistance Test",
                "Flash Test Performance",
            ],
            "thermal": [
                "Thermal Cycling Test",
                "Hot Spot Endurance",
                "NOCT Measurement",
                "Thermal Imaging",
            ],
            "mechanical": [
                "Mechanical Load Test",
                "Hail Impact Test",
                "Twist Test",
                "Pull Test",
            ],
        }

        templates = name_templates.get(protocol_type, ["Generic Test"])
        return random.choice(templates)

    def _generate_standard(self) -> str:
        """Generate a standards reference."""
        standards = [
            "IEC 61215",
            "IEC 61730",
            "IEC 61853",
            "IEC 62804",
            "UL 1703",
        ]
        return random.choice(standards)

    def _generate_parameters(self, protocol_type: str) -> Dict[str, Any]:
        """Generate protocol parameters."""
        base_params = {
            "module_id": f"MOD-{self.fake.bothify('???-####')}",
            "test_type": protocol_type,
        }

        type_specific = {
            "electrical": {
                "irradiance": random.randint(800, 1200),
                "temperature": random.randint(20, 30),
                "voltage_range": {"min": 0, "max": random.randint(40, 60)},
                "current_range": {"min": 0, "max": random.randint(8, 12)},
            },
            "thermal": {
                "temperature_profile": {
                    "min_temp": -40,
                    "max_temp": 85,
                    "ramp_rate": random.randint(50, 150),
                    "dwell_time": random.randint(20, 40),
                },
                "number_of_cycles": random.choice([50, 200, 500]),
            },
            "mechanical": {
                "load_profile": {
                    "load_value": random.choice([2400, 5400]),
                    "load_direction": random.choice(["front", "back"]),
                    "duration": random.randint(1800, 7200),
                    "cycles": random.randint(1, 3),
                },
            },
        }

        base_params.update(type_specific.get(protocol_type, {}))
        return base_params

    def _generate_acceptance_criteria(self, protocol_type: str) -> Dict[str, Any]:
        """Generate acceptance criteria."""
        criteria_templates = {
            "electrical": {
                "min_power": random.randint(200, 300),
                "min_efficiency": random.uniform(15, 20),
                "fill_factor_min": random.uniform(0.70, 0.75),
            },
            "thermal": {
                "max_power_degradation": 5,
                "no_major_visual_defects": True,
            },
            "mechanical": {
                "max_deflection": 40,
                "max_power_degradation": 5,
                "no_cracks": True,
                "no_delamination": True,
            },
        }

        return criteria_templates.get(protocol_type, {})

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata."""
        return {
            "timestamp": datetime.now().isoformat(),
            "operator": self.fake.name(),
            "facility": f"{self.fake.city()} Test Lab",
            "equipment": [
                "Solar Simulator",
                "I-V Curve Tracer",
                "Data Acquisition System",
            ],
        }

    def generate_invalid_protocol(self) -> Dict[str, Any]:
        """
        Generate an intentionally invalid protocol for negative testing.

        Returns:
            Invalid protocol data
        """
        invalid_choices = [
            # Missing required fields
            {"protocol_id": "TEST-001"},
            # Invalid protocol type
            {
                "protocol_id": "TEST-002",
                "protocol_name": "Test",
                "protocol_type": "invalid_type",
                "version": "1.0",
                "parameters": {},
            },
            # Invalid version format
            {
                "protocol_id": "TEST-003",
                "protocol_name": "Test",
                "protocol_type": "electrical",
                "version": "invalid",
                "parameters": {},
            },
        ]

        return random.choice(invalid_choices)
