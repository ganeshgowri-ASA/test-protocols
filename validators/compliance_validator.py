"""
Compliance validator for IEC standards and regulations.
"""
from typing import Dict, Any, List
from loguru import logger


class ComplianceValidator:
    """Validates protocols against IEC standards and regulations."""

    # IEC 61215 compliance requirements
    IEC61215_REQUIREMENTS = {
        "visual_inspection": {
            "required_checks": [
                "no_broken_cells",
                "no_delamination",
                "frame_integrity",
                "junction_box_secure",
            ],
            "standard": "IEC 61215-10-1",
        },
        "insulation_test": {
            "min_resistance": 40,  # MΩ per kV
            "test_voltage": 1000,  # V
            "standard": "IEC 61215-10-3",
        },
        "thermal_cycling": {
            "min_cycles": 200,
            "temp_range": [-40, 85],
            "max_power_degradation": 5,  # %
            "standard": "IEC 61215-10-10",
        },
        "humidity_freeze": {
            "min_cycles": 10,
            "temp_range": [-40, 85],
            "humidity": 85,  # %RH at 85°C
            "max_power_degradation": 5,  # %
            "standard": "IEC 61215-10-11",
        },
        "damp_heat": {
            "duration": 1000,  # hours
            "temperature": 85,  # °C
            "humidity": 85,  # %RH
            "max_power_degradation": 5,  # %
            "standard": "IEC 61215-10-12",
        },
        "mechanical_load": {
            "front_load": 2400,  # Pa
            "back_load": 2400,  # Pa
            "cycles": 3,
            "max_power_degradation": 5,  # %
            "standard": "IEC 61215-10-15",
        },
        "hail_impact": {
            "ice_ball_diameter": 25,  # mm
            "impact_velocity": 23,  # m/s
            "impact_points": 11,
            "standard": "IEC 61215-10-16",
        },
    }

    # IEC 61730 safety requirements
    IEC61730_REQUIREMENTS = {
        "accessibility": {
            "max_voltage_accessible": 120,  # V DC or 30 V AC
            "standard": "IEC 61730-MST-02",
        },
        "edge_strength": {
            "min_force": 250,  # N
            "standard": "IEC 61730-MST-23",
        },
    }

    def __init__(self):
        """Initialize compliance validator."""
        self.standards = {
            "IEC61215": self.IEC61215_REQUIREMENTS,
            "IEC61730": self.IEC61730_REQUIREMENTS,
        }

    def validate_protocol_compliance(
        self, protocol_data: Dict[str, Any], standard: str = "IEC61215"
    ) -> Dict[str, Any]:
        """
        Validate protocol against standard requirements.

        Args:
            protocol_data: Protocol data dictionary
            standard: Standard to validate against (IEC61215 or IEC61730)

        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "compliant": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        standard_reqs = self.standards.get(standard)
        if not standard_reqs:
            result["warnings"].append(f"Unknown standard: {standard}")
            return result

        protocol_id = protocol_data.get("protocol_id", "")
        protocol_type = self._get_protocol_type_from_id(protocol_id)

        # Get relevant requirements
        requirements = standard_reqs.get(protocol_type)
        if not requirements:
            result["warnings"].append(
                f"No compliance requirements found for protocol type: {protocol_type}"
            )
            return result

        # Validate against requirements
        check_results = self._check_requirements(protocol_data, requirements)
        result["checks"] = check_results

        # Aggregate results
        for check_name, check_result in check_results.items():
            if not check_result["passed"]:
                result["compliant"] = False
                result["is_valid"] = False
                result["errors"].append(
                    f"{check_name}: {check_result.get('message', 'Failed')}"
                )

        if result["compliant"]:
            logger.info(f"Protocol {protocol_id} is compliant with {standard}")
        else:
            logger.warning(
                f"Protocol {protocol_id} is NOT compliant with {standard}"
            )

        return result

    def _get_protocol_type_from_id(self, protocol_id: str) -> str:
        """Extract protocol type from protocol ID."""
        # Map protocol IDs to types
        id_map = {
            "10-1": "visual_inspection",
            "10-3": "insulation_test",
            "10-10": "thermal_cycling",
            "10-11": "humidity_freeze",
            "10-12": "damp_heat",
            "10-15": "mechanical_load",
            "10-16": "hail_impact",
        }

        for key, value in id_map.items():
            if key in protocol_id:
                return value

        return "unknown"

    def _check_requirements(
        self, protocol_data: Dict[str, Any], requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Check protocol data against requirements.

        Args:
            protocol_data: Protocol data
            requirements: Requirements dictionary

        Returns:
            Dictionary of check results
        """
        checks = {}
        parameters = protocol_data.get("parameters", {})

        # Check numeric requirements
        for req_key, req_value in requirements.items():
            if req_key == "standard":
                continue

            if isinstance(req_value, (int, float)):
                param_value = parameters.get(req_key)
                if param_value is None:
                    checks[req_key] = {
                        "passed": False,
                        "message": f"Required parameter '{req_key}' not found",
                    }
                elif isinstance(req_value, (int, float)):
                    if "min_" in req_key:
                        passed = param_value >= req_value
                    elif "max_" in req_key:
                        passed = param_value <= req_value
                    else:
                        passed = param_value == req_value

                    checks[req_key] = {
                        "passed": passed,
                        "expected": req_value,
                        "actual": param_value,
                        "message": f"Expected {req_value}, got {param_value}",
                    }

            elif isinstance(req_value, list):
                # Check list requirements (e.g., temp_range)
                param_value = parameters.get(req_key)
                checks[req_key] = {
                    "passed": param_value == req_value if param_value else False,
                    "expected": req_value,
                    "actual": param_value,
                }

        return checks

    def get_standard_requirements(self, standard: str, test_type: str) -> Dict[str, Any]:
        """
        Get requirements for a specific test type.

        Args:
            standard: Standard name (IEC61215, IEC61730)
            test_type: Test type (e.g., 'thermal_cycling')

        Returns:
            Requirements dictionary or empty dict
        """
        standard_reqs = self.standards.get(standard, {})
        return standard_reqs.get(test_type, {})

    def list_supported_standards(self) -> List[str]:
        """
        List all supported standards.

        Returns:
            List of standard names
        """
        return list(self.standards.keys())

    def list_test_types(self, standard: str) -> List[str]:
        """
        List test types for a standard.

        Args:
            standard: Standard name

        Returns:
            List of test type names
        """
        standard_reqs = self.standards.get(standard, {})
        return list(standard_reqs.keys())
