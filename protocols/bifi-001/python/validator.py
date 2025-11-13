"""
Data validation for BIFI-001 Bifacial Performance Protocol
"""

import json
import jsonschema
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path


class BifacialValidator:
    """Validates bifacial performance test data according to IEC 60904-1-2"""

    def __init__(self, schema_path: str = None):
        """
        Initialize validator with JSON schema

        Args:
            schema_path: Path to protocol_config.json schema file
        """
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schemas" / "protocol_config.json"

        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

    def validate_schema(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate data against JSON schema

        Args:
            data: Test data dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors

    def validate_irradiance_conditions(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate irradiance conditions meet IEC 60904-1-2 requirements

        Args:
            data: Test data dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        conditions = data.get("test_conditions", {})

        # Check front irradiance
        front_irr = conditions.get("front_irradiance", {})
        front_value = front_irr.get("value", 0)

        if front_value < 100:
            errors.append(f"Front irradiance too low: {front_value} W/m². Minimum 100 W/m² recommended.")

        # Check rear irradiance
        rear_irr = conditions.get("rear_irradiance", {})
        rear_value = rear_irr.get("value", 0)

        if rear_value > front_value:
            errors.append(f"Rear irradiance ({rear_value} W/m²) exceeds front irradiance ({front_value} W/m²)")

        # Check for STC conditions if flagged
        if conditions.get("stc_conditions", False):
            if abs(front_value - 1000) > 10:
                errors.append(f"STC conditions require 1000 W/m² front irradiance, got {front_value} W/m²")

            temp = conditions.get("temperature", {}).get("value", 0)
            if abs(temp - 25) > 2:
                errors.append(f"STC conditions require 25°C, got {temp}°C")

        return len(errors) == 0, errors

    def validate_iv_curve(self, iv_data: List[Dict], side: str = "front") -> Tuple[bool, List[str]]:
        """
        Validate I-V curve data quality

        Args:
            iv_data: List of voltage-current measurement points
            side: "front" or "rear" side identifier

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if len(iv_data) < 10:
            errors.append(f"{side} side: I-V curve has insufficient data points ({len(iv_data)} < 10)")

        # Check for monotonic voltage increase
        voltages = [point.get("voltage", 0) for point in iv_data]
        if voltages != sorted(voltages):
            errors.append(f"{side} side: I-V curve voltages are not monotonically increasing")

        # Check for reasonable current decrease
        currents = [point.get("current", 0) for point in iv_data]
        if len(currents) > 1:
            if currents[0] < 0:
                errors.append(f"{side} side: Short-circuit current is negative")

            # Current should generally decrease as voltage increases
            non_decreasing_count = sum(1 for i in range(len(currents)-1) if currents[i+1] > currents[i])
            if non_decreasing_count > len(currents) * 0.2:  # Allow up to 20% noise
                errors.append(f"{side} side: I-V curve shows unusual current behavior")

        return len(errors) == 0, errors

    def validate_measurements(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate measurement data consistency and quality

        Args:
            data: Test data dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        measurements = data.get("measurements", {})

        # Validate front side
        front = measurements.get("front_side", {})
        if front:
            is_valid, front_errors = self.validate_iv_curve(front.get("iv_curve", []), "front")
            errors.extend(front_errors)

            # Check parameter consistency
            isc = front.get("isc", 0)
            voc = front.get("voc", 0)
            pmax = front.get("pmax", 0)

            if isc <= 0 or voc <= 0:
                errors.append("Front side: Isc and Voc must be positive")

            if pmax > isc * voc:
                errors.append(f"Front side: Pmax ({pmax}W) cannot exceed Isc × Voc ({isc * voc}W)")

            # Check fill factor
            ff = front.get("fill_factor", 0)
            if ff <= 0 or ff > 1:
                errors.append(f"Front side: Fill factor ({ff}) must be between 0 and 1")

            expected_ff = pmax / (isc * voc) if (isc * voc) > 0 else 0
            if abs(ff - expected_ff) > 0.05:
                errors.append(f"Front side: Fill factor inconsistency. Expected {expected_ff:.3f}, got {ff:.3f}")

        # Validate rear side
        rear = measurements.get("rear_side", {})
        if rear:
            is_valid, rear_errors = self.validate_iv_curve(rear.get("iv_curve", []), "rear")
            errors.extend(rear_errors)

            isc = rear.get("isc", 0)
            voc = rear.get("voc", 0)
            pmax = rear.get("pmax", 0)

            if isc <= 0 or voc <= 0:
                errors.append("Rear side: Isc and Voc must be positive")

            if pmax > isc * voc:
                errors.append(f"Rear side: Pmax ({pmax}W) cannot exceed Isc × Voc ({isc * voc}W)")

            ff = rear.get("fill_factor", 0)
            if ff <= 0 or ff > 1:
                errors.append(f"Rear side: Fill factor ({ff}) must be between 0 and 1")

        # Validate bifacial measurements
        bifacial = measurements.get("bifacial_measurements", {})
        if bifacial and front and rear:
            measured_bf = bifacial.get("measured_bifaciality", 0)
            expected_bf = rear.get("pmax", 0) / front.get("pmax", 1) if front.get("pmax", 1) > 0 else 0

            if abs(measured_bf - expected_bf) > 0.05:
                errors.append(f"Bifaciality factor inconsistency. Expected {expected_bf:.3f}, got {measured_bf:.3f}")

        return len(errors) == 0, errors

    def validate_calibration(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate calibration status and currency

        Args:
            data: Test data dictionary

        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []
        qc = data.get("quality_control", {})
        calibration = qc.get("calibration_status", {})

        if not calibration:
            warnings.append("No calibration information provided")
            return False, warnings

        # Check calibration dates
        last_cal = calibration.get("last_calibration_date")
        next_cal = calibration.get("next_calibration_due")

        if last_cal and next_cal:
            try:
                last_cal_date = datetime.fromisoformat(last_cal)
                next_cal_date = datetime.fromisoformat(next_cal)
                test_date = datetime.fromisoformat(data.get("metadata", {}).get("test_date", ""))

                if test_date < last_cal_date:
                    warnings.append("Test date is before last calibration date")

                if test_date > next_cal_date:
                    warnings.append("Calibration is overdue")
            except (ValueError, TypeError):
                warnings.append("Invalid date format in calibration data")

        return len(warnings) == 0, warnings

    def validate_all(self, data: Dict) -> Dict[str, Any]:
        """
        Perform comprehensive validation of all data

        Args:
            data: Test data dictionary

        Returns:
            Dictionary with validation results
        """
        results = {
            "overall_valid": True,
            "errors": [],
            "warnings": [],
            "checks": []
        }

        # Schema validation
        is_valid, errors = self.validate_schema(data)
        results["checks"].append({
            "check_name": "Schema Validation",
            "status": "pass" if is_valid else "fail",
            "message": "; ".join(errors) if errors else "Schema validation passed"
        })
        if not is_valid:
            results["overall_valid"] = False
            results["errors"].extend(errors)

        # Irradiance validation
        is_valid, errors = self.validate_irradiance_conditions(data)
        results["checks"].append({
            "check_name": "Irradiance Conditions",
            "status": "pass" if is_valid else "fail",
            "message": "; ".join(errors) if errors else "Irradiance conditions valid"
        })
        if not is_valid:
            results["overall_valid"] = False
            results["errors"].extend(errors)

        # Measurement validation
        is_valid, errors = self.validate_measurements(data)
        results["checks"].append({
            "check_name": "Measurement Data Quality",
            "status": "pass" if is_valid else "fail",
            "message": "; ".join(errors) if errors else "Measurement data valid"
        })
        if not is_valid:
            results["overall_valid"] = False
            results["errors"].extend(errors)

        # Calibration validation (warnings only)
        is_valid, warnings = self.validate_calibration(data)
        results["checks"].append({
            "check_name": "Calibration Status",
            "status": "pass" if is_valid else "warning",
            "message": "; ".join(warnings) if warnings else "Calibration status valid"
        })
        if warnings:
            results["warnings"].extend(warnings)

        return results
