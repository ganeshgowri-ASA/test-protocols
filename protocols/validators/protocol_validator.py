"""
Protocol Validator
Validates protocol definitions against JSON schema and business rules
"""

from typing import Dict, List, Tuple, Any, Optional
import jsonschema
import json
from pathlib import Path


class ProtocolValidator:
    """
    Validates protocol definitions against base schema and business rules
    """

    def __init__(self, base_schema_path: Optional[str] = None):
        """
        Initialize validator with base schema

        Args:
            base_schema_path: Path to base protocol schema JSON
        """
        if base_schema_path is None:
            # Default to base schema in schemas directory
            base_schema_path = Path(__file__).parent.parent / "schemas" / "base-protocol-schema.json"

        with open(base_schema_path, 'r') as f:
            self.base_schema = json.load(f)

        self.validator = jsonschema.Draft7Validator(self.base_schema)

    def validate_protocol(self, protocol_def: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate protocol definition

        Args:
            protocol_def: Protocol definition dictionary

        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []
        is_valid = True

        # JSON Schema validation
        schema_valid, schema_messages = self._validate_schema(protocol_def)
        messages.extend(schema_messages)
        is_valid = is_valid and schema_valid

        # Business rules validation
        rules_valid, rules_messages = self._validate_business_rules(protocol_def)
        messages.extend(rules_messages)
        is_valid = is_valid and rules_valid

        return is_valid, messages

    def _validate_schema(self, protocol_def: Dict) -> Tuple[bool, List[str]]:
        """Validate against JSON schema"""
        messages = []
        is_valid = True

        errors = list(self.validator.iter_errors(protocol_def))

        for error in errors:
            is_valid = False
            path = " -> ".join(str(p) for p in error.path)
            messages.append(f"SCHEMA ERROR at {path}: {error.message}")

        return is_valid, messages

    def _validate_business_rules(self, protocol_def: Dict) -> Tuple[bool, List[str]]:
        """Validate business rules"""
        messages = []
        is_valid = True

        # Rule 1: Safety interlocks must include pre-test equipment check
        interlocks = protocol_def.get("safetyInterlocks", [])
        has_equipment_check = any(
            i.get("type") == "pre-test" and "calibration" in i.get("condition", "")
            for i in interlocks
        )
        if not has_equipment_check:
            messages.append("WARNING: No equipment calibration interlock found")

        # Rule 2: Critical safety interlocks must have 'block' or 'emergency-stop' action
        for interlock in interlocks:
            if interlock.get("severity") == "critical":
                action = interlock.get("action")
                if action not in ["block", "emergency-stop"]:
                    messages.append(
                        f"ERROR: Critical interlock {interlock.get('interlockId')} "
                        f"must have 'block' or 'emergency-stop' action"
                    )
                    is_valid = False

        # Rule 3: Final approval gate must exist
        approval_gates = protocol_def.get("approvalGates", [])
        has_final_approval = any(g.get("stage") == "final-approval" for g in approval_gates)
        if not has_final_approval:
            messages.append("ERROR: Final approval gate is required")
            is_valid = False

        # Rule 4: High voltage tests must have discharge interlock
        test_params = protocol_def.get("testParameters", {})
        has_high_voltage = False
        for param_name, param_value in test_params.items():
            if isinstance(param_value, dict):
                if param_value.get("unit") in ["V", "V DC", "V AC"]:
                    if param_value.get("value", 0) >= 50:  # > 50V is high voltage
                        has_high_voltage = True
                        break

        if has_high_voltage:
            has_discharge = any(
                "discharge" in i.get("condition", "").lower() or
                "discharge" in i.get("message", "").lower()
                for i in interlocks if i.get("type") == "post-test"
            )
            if not has_discharge:
                messages.append("ERROR: High voltage test must include discharge safety interlock")
                is_valid = False

        # Rule 5: Traceability must be enabled for certification tests
        if protocol_def.get("category") in ["certification", "safety"]:
            if not protocol_def.get("traceability", {}).get("enabled", False):
                messages.append("ERROR: Traceability must be enabled for certification/safety tests")
                is_valid = False

        # Rule 6: Validate acceptance criteria exist
        if not protocol_def.get("acceptanceCriteria"):
            messages.append("WARNING: No acceptance criteria defined")

        return is_valid, messages

    def validate_test_data(self, protocol_def: Dict, test_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate test data against protocol definition

        Args:
            protocol_def: Protocol definition
            test_data: Test data to validate

        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []
        is_valid = True

        # Check required device identification
        dut = test_data.get("deviceUnderTest", {})
        required_fields = ["serialNumber", "modelNumber"]

        for field in required_fields:
            if not dut.get("identification", {}).get(field):
                messages.append(f"ERROR: Device {field} is required")
                is_valid = False

        # Validate measurements against acceptance criteria
        criteria = protocol_def.get("acceptanceCriteria", {})
        measurements = test_data.get("measurements", {})

        for criterion_name, criterion_value in criteria.items():
            if isinstance(criterion_value, dict) and "max" in criterion_value:
                # Check if measurement exists
                measured_value = measurements.get(criterion_name, {}).get("value")

                if measured_value is not None:
                    if measured_value > criterion_value["max"]:
                        messages.append(
                            f"FAIL: {criterion_name} = {measured_value} exceeds maximum {criterion_value['max']}"
                        )
                        is_valid = False

            if isinstance(criterion_value, dict) and "min" in criterion_value:
                measured_value = measurements.get(criterion_name, {}).get("value")

                if measured_value is not None:
                    if measured_value < criterion_value["min"]:
                        messages.append(
                            f"FAIL: {criterion_name} = {measured_value} below minimum {criterion_value['min']}"
                        )
                        is_valid = False

        return is_valid, messages


class SafetyValidator:
    """
    Specialized validator for safety-critical protocols
    """

    @staticmethod
    def validate_high_voltage_safety(protocol_def: Dict) -> Tuple[bool, List[str]]:
        """Validate high voltage safety requirements"""
        messages = []
        is_valid = True

        interlocks = protocol_def.get("safetyInterlocks", [])

        # Required high voltage interlocks
        required_interlocks = [
            "operator qualification",
            "equipment calibration",
            "grounding",
            "discharge"
        ]

        for required in required_interlocks:
            found = any(
                required.lower() in i.get("condition", "").lower() or
                required.lower() in i.get("message", "").lower()
                for i in interlocks
            )

            if not found:
                messages.append(f"ERROR: Missing required high voltage interlock: {required}")
                is_valid = False

        return is_valid, messages

    @staticmethod
    def validate_fire_test_safety(protocol_def: Dict) -> Tuple[bool, List[str]]:
        """Validate fire test safety requirements"""
        messages = []
        is_valid = True

        interlocks = protocol_def.get("safetyInterlocks", [])

        # Required fire test safety items
        required_items = [
            "fire suppression",
            "ventilation",
            "personnel trained",
            "ppe"
        ]

        for required in required_items:
            found = any(
                required.lower() in i.get("condition", "").lower() or
                required.lower() in i.get("message", "").lower()
                for i in interlocks
            )

            if not found:
                messages.append(f"WARNING: Consider adding fire test safety check: {required}")

        return is_valid, messages


class DataValidator:
    """
    Validator for test data quality and consistency
    """

    @staticmethod
    def validate_time_series_data(time_series: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate time series data quality"""
        messages = []
        is_valid = True

        if len(time_series) == 0:
            messages.append("WARNING: No time series data collected")
            return True, messages

        # Check for data gaps
        timestamps = [point["timestamp"] for point in time_series]
        # Would check for gaps, outliers, etc.

        # Check for missing parameters
        if len(time_series) > 0:
            first_params = set(time_series[0].get("data", {}).keys())
            for point in time_series:
                point_params = set(point.get("data", {}).keys())
                if point_params != first_params:
                    messages.append("WARNING: Inconsistent parameters in time series data")
                    break

        return is_valid, messages

    @staticmethod
    def validate_measurement_uncertainty(measurements: Dict) -> Tuple[bool, List[str]]:
        """Validate measurement uncertainty is within acceptable ranges"""
        messages = []
        is_valid = True

        for name, measurement in measurements.items():
            uncertainty = measurement.get("uncertainty")
            value = measurement.get("value")

            if uncertainty is not None and value is not None:
                if abs(uncertainty / value) > 0.10:  # > 10% uncertainty
                    messages.append(
                        f"WARNING: High measurement uncertainty for {name}: {uncertainty/value*100:.1f}%"
                    )

        return is_valid, messages
