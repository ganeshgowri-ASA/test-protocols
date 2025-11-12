"""
Edge case and boundary condition test data generator.
"""
from typing import Dict, Any, List
import sys


class EdgeCaseGenerator:
    """Generates edge case and boundary condition test data."""

    def __init__(self):
        """Initialize edge case generator."""
        pass

    def generate_boundary_values(self, parameter: str) -> List[Dict[str, Any]]:
        """
        Generate boundary value test cases for a parameter.

        Args:
            parameter: Parameter name

        Returns:
            List of test cases with boundary values
        """
        boundary_specs = {
            "temperature": {
                "min": -40,
                "max": 150,
                "unit": "°C",
                "critical_points": [-40, -30, 0, 25, 50, 85, 100, 150],
            },
            "irradiance": {
                "min": 0,
                "max": 1500,
                "unit": "W/m²",
                "critical_points": [0, 100, 200, 800, 1000, 1200, 1500],
            },
            "voltage": {
                "min": 0,
                "max": 100,
                "unit": "V",
                "critical_points": [0, 0.1, 10, 24, 48, 60, 100],
            },
            "efficiency": {
                "min": 0,
                "max": 100,
                "unit": "%",
                "critical_points": [0, 5, 10, 15, 20, 25],
            },
        }

        spec = boundary_specs.get(parameter, {})
        if not spec:
            return []

        test_cases = []

        # Add min boundary
        test_cases.append({
            "description": f"{parameter} at minimum boundary",
            "parameter": parameter,
            "value": spec["min"],
            "unit": spec["unit"],
            "expected": "valid",
        })

        # Add just below min (invalid)
        if spec["min"] > 0:
            test_cases.append({
                "description": f"{parameter} below minimum boundary",
                "parameter": parameter,
                "value": spec["min"] - 1,
                "unit": spec["unit"],
                "expected": "invalid",
            })

        # Add just above min
        test_cases.append({
            "description": f"{parameter} just above minimum",
            "parameter": parameter,
            "value": spec["min"] + 0.1,
            "unit": spec["unit"],
            "expected": "valid",
        })

        # Add critical points
        for value in spec.get("critical_points", []):
            test_cases.append({
                "description": f"{parameter} at critical point",
                "parameter": parameter,
                "value": value,
                "unit": spec["unit"],
                "expected": "valid",
            })

        # Add just below max
        test_cases.append({
            "description": f"{parameter} just below maximum",
            "parameter": parameter,
            "value": spec["max"] - 0.1,
            "unit": spec["unit"],
            "expected": "valid",
        })

        # Add max boundary
        test_cases.append({
            "description": f"{parameter} at maximum boundary",
            "parameter": parameter,
            "value": spec["max"],
            "unit": spec["unit"],
            "expected": "valid",
        })

        # Add just above max (invalid)
        test_cases.append({
            "description": f"{parameter} above maximum boundary",
            "parameter": parameter,
            "value": spec["max"] + 1,
            "unit": spec["unit"],
            "expected": "invalid",
        })

        return test_cases

    def generate_null_empty_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for null and empty values.

        Returns:
            List of null/empty test cases
        """
        return [
            {
                "description": "Null protocol_id",
                "data": {
                    "protocol_id": None,
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "invalid",
            },
            {
                "description": "Empty protocol_id",
                "data": {
                    "protocol_id": "",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "invalid",
            },
            {
                "description": "Empty parameters",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "valid",
            },
            {
                "description": "Null parameters",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": None,
                },
                "expected": "invalid",
            },
            {
                "description": "Empty measurements list",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                    "measurements": [],
                },
                "expected": "valid",
            },
        ]

    def generate_type_mismatch_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for type mismatches.

        Returns:
            List of type mismatch test cases
        """
        return [
            {
                "description": "String instead of number for temperature",
                "field": "temperature",
                "value": "twenty-five",
                "expected_type": "number",
                "expected": "invalid",
            },
            {
                "description": "Number instead of string for protocol_id",
                "field": "protocol_id",
                "value": 12345,
                "expected_type": "string",
                "expected": "invalid",
            },
            {
                "description": "Boolean instead of number for irradiance",
                "field": "irradiance",
                "value": True,
                "expected_type": "number",
                "expected": "invalid",
            },
            {
                "description": "List instead of object for parameters",
                "field": "parameters",
                "value": ["param1", "param2"],
                "expected_type": "object",
                "expected": "invalid",
            },
            {
                "description": "Object instead of array for measurements",
                "field": "measurements",
                "value": {"measurement": "data"},
                "expected_type": "array",
                "expected": "invalid",
            },
        ]

    def generate_large_data_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases with large data volumes.

        Returns:
            List of large data test cases
        """
        return [
            {
                "description": "Very long protocol name",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "A" * 500,
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "invalid",  # Exceeds max length
            },
            {
                "description": "Large number of measurements",
                "data": {
                    "protocol_id": "TEST-002",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                    "measurements": [
                        {
                            "measurement_id": f"M{i:06d}",
                            "parameter": "voltage",
                            "value": 24.5,
                            "unit": "V",
                        }
                        for i in range(10000)
                    ],
                },
                "expected": "valid",  # Should handle large datasets
            },
            {
                "description": "Deeply nested parameters",
                "data": {
                    "protocol_id": "TEST-003",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": self._create_deep_nesting(10),
                },
                "expected": "valid",
            },
        ]

    def generate_special_character_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases with special characters.

        Returns:
            List of special character test cases
        """
        return [
            {
                "description": "Protocol ID with lowercase",
                "data": {
                    "protocol_id": "test-001",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "invalid",  # Must be uppercase
            },
            {
                "description": "Protocol ID with special characters",
                "data": {
                    "protocol_id": "TEST@001#",
                    "protocol_name": "Test",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "invalid",
            },
            {
                "description": "Protocol name with unicode",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "测试协议 Test Protocol",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "valid",  # Unicode should be allowed
            },
            {
                "description": "SQL injection attempt in protocol_name",
                "data": {
                    "protocol_id": "TEST-001",
                    "protocol_name": "Test'; DROP TABLE protocols;--",
                    "protocol_type": "electrical",
                    "version": "1.0",
                    "parameters": {},
                },
                "expected": "valid",  # Should be sanitized
            },
        ]

    def generate_concurrent_access_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for concurrent access scenarios.

        Returns:
            List of concurrent access test cases
        """
        return [
            {
                "description": "Multiple protocols with same ID",
                "protocols": [
                    {
                        "protocol_id": "TEST-001",
                        "protocol_name": "Test A",
                        "protocol_type": "electrical",
                        "version": "1.0",
                        "parameters": {},
                    },
                    {
                        "protocol_id": "TEST-001",
                        "protocol_name": "Test B",
                        "protocol_type": "thermal",
                        "version": "1.0",
                        "parameters": {},
                    },
                ],
                "expected": "conflict",
            },
            {
                "description": "Simultaneous modifications",
                "scenario": "Two users modifying same protocol",
                "expected": "last_write_wins_or_conflict",
            },
        ]

    def _create_deep_nesting(self, depth: int) -> Dict[str, Any]:
        """
        Create deeply nested dictionary structure.

        Args:
            depth: Nesting depth

        Returns:
            Nested dictionary
        """
        if depth == 0:
            return {"value": "leaf"}

        return {"nested": self._create_deep_nesting(depth - 1)}

    def generate_all_edge_cases(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate all edge case categories.

        Returns:
            Dictionary of edge case categories
        """
        return {
            "boundary_temperature": self.generate_boundary_values("temperature"),
            "boundary_irradiance": self.generate_boundary_values("irradiance"),
            "boundary_voltage": self.generate_boundary_values("voltage"),
            "null_empty": self.generate_null_empty_cases(),
            "type_mismatch": self.generate_type_mismatch_cases(),
            "large_data": self.generate_large_data_cases(),
            "special_characters": self.generate_special_character_cases(),
            "concurrent_access": self.generate_concurrent_access_cases(),
        }
