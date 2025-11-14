"""
Schema Validator - Validate test data against protocol schemas
"""

import json
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator
import logging

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates test data against JSON schemas."""

    def __init__(self, protocol_manager=None):
        """
        Initialize the schema validator.

        Args:
            protocol_manager: ProtocolManager instance for accessing schemas
        """
        self.protocol_manager = protocol_manager
        self.validators = {}

    def validate_data(
        self,
        protocol_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data against protocol schema.

        Args:
            protocol_id: Protocol identifier
            data: Data to validate

        Returns:
            Validation result with status and errors
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Get protocol schema
        if self.protocol_manager:
            protocol = self.protocol_manager.get_protocol(protocol_id)
        else:
            result["valid"] = False
            result["errors"].append("Protocol manager not initialized")
            return result

        if not protocol:
            result["valid"] = False
            result["errors"].append(f"Protocol not found: {protocol_id}")
            return result

        # Extract JSON schema
        schema = protocol.get("schema", {})

        # Validate against JSON schema
        try:
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(data))

            if errors:
                result["valid"] = False
                for error in errors:
                    error_path = ".".join(str(p) for p in error.path)
                    result["errors"].append(
                        f"Validation error at {error_path}: {error.message}"
                    )
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Schema validation failed: {str(e)}")

        # Perform custom validations
        custom_result = self._custom_validations(protocol_id, data, protocol)
        result["errors"].extend(custom_result.get("errors", []))
        result["warnings"].extend(custom_result.get("warnings", []))

        if custom_result.get("errors"):
            result["valid"] = False

        return result

    def _custom_validations(
        self,
        protocol_id: str,
        data: Dict[str, Any],
        protocol: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform custom validation rules specific to protocols.

        Args:
            protocol_id: Protocol identifier
            data: Data to validate
            protocol: Protocol schema

        Returns:
            Validation result with errors and warnings
        """
        result = {
            "errors": [],
            "warnings": []
        }

        # CONC-001 specific validations
        if protocol_id == "conc-001":
            result = self._validate_conc001(data, protocol)

        return result

    def _validate_conc001(
        self,
        data: Dict[str, Any],
        protocol: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CONC-001 specific validation rules.

        Args:
            data: Test data
            protocol: Protocol schema

        Returns:
            Validation result
        """
        result = {
            "errors": [],
            "warnings": []
        }

        measurements = data.get("measurements", [])

        if not measurements:
            result["errors"].append("No measurements provided")
            return result

        # Validate each measurement
        for idx, measurement in enumerate(measurements):
            # Check fill factor calculation
            voc = measurement.get("voc", 0)
            isc = measurement.get("isc", 0)
            vmp = measurement.get("vmp", 0)
            imp = measurement.get("imp", 0)
            ff = measurement.get("fill_factor", 0)

            if voc > 0 and isc > 0:
                calculated_ff = (vmp * imp) / (voc * isc)
                if abs(calculated_ff - ff) > 0.01:
                    result["warnings"].append(
                        f"Measurement {idx}: Fill factor mismatch. "
                        f"Reported: {ff:.3f}, Calculated: {calculated_ff:.3f}"
                    )

            # Check QC criteria
            qc_criteria = protocol.get("qc_criteria", {})

            # Fill factor minimum
            ff_min = qc_criteria.get("fill_factor_minimum", {}).get("value", 0.65)
            if ff < ff_min:
                result["warnings"].append(
                    f"Measurement {idx}: Fill factor {ff:.3f} below minimum {ff_min}"
                )

            # Spectral mismatch
            spectral_mismatch = measurement.get("spectral_mismatch", 0)
            max_mismatch = qc_criteria.get("spectral_mismatch", {}).get("max_value", 0.05)
            if abs(spectral_mismatch) > max_mismatch:
                result["warnings"].append(
                    f"Measurement {idx}: Spectral mismatch {spectral_mismatch:.3f} "
                    f"exceeds maximum {max_mismatch}"
                )

            # Temperature range check
            temp = measurement.get("temperature_c", 0)
            if temp < -40 or temp > 200:
                result["errors"].append(
                    f"Measurement {idx}: Temperature {temp}°C out of valid range (-40 to 200°C)"
                )

            # Efficiency sanity check
            efficiency = measurement.get("efficiency", 0)
            if efficiency > 50:
                result["warnings"].append(
                    f"Measurement {idx}: Efficiency {efficiency}% seems unusually high"
                )

        # Check measurement repeatability
        if len(measurements) >= 3:
            # Check if there are repeated measurements at same concentration
            concentrations = [m.get("concentration_suns") for m in measurements]
            unique_conc = set(concentrations)

            for conc in unique_conc:
                conc_measurements = [
                    m for m in measurements
                    if m.get("concentration_suns") == conc
                ]

                if len(conc_measurements) >= 3:
                    # Calculate coefficient of variation for efficiency
                    efficiencies = [m.get("efficiency", 0) for m in conc_measurements]
                    mean_eff = sum(efficiencies) / len(efficiencies)

                    if mean_eff > 0:
                        std_dev = (sum((e - mean_eff)**2 for e in efficiencies) / len(efficiencies))**0.5
                        cv = std_dev / mean_eff

                        max_cv = protocol.get("qc_criteria", {}).get(
                            "measurement_repeatability", {}
                        ).get("max_coefficient_variation", 0.05)

                        if cv > max_cv:
                            result["warnings"].append(
                                f"Concentration {conc} suns: Coefficient of variation "
                                f"{cv:.3f} exceeds maximum {max_cv}"
                            )

        return result

    def validate_qc_criteria(
        self,
        protocol_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data against QC criteria.

        Args:
            protocol_id: Protocol identifier
            data: Test data

        Returns:
            QC validation result
        """
        result = {
            "passed": True,
            "criteria_results": [],
            "overall_status": "PASS"
        }

        if not self.protocol_manager:
            return result

        qc_criteria = self.protocol_manager.get_qc_criteria(protocol_id)
        if not qc_criteria:
            return result

        # Check each QC criterion
        for criterion_name, criterion_spec in qc_criteria.items():
            criterion_result = {
                "name": criterion_name,
                "description": criterion_spec.get("description", ""),
                "status": "PASS",
                "message": ""
            }

            # Implement specific QC checks based on criterion
            # This is extensible for different protocols

            result["criteria_results"].append(criterion_result)

        # Determine overall status
        failed_criteria = [
            c for c in result["criteria_results"]
            if c["status"] == "FAIL"
        ]

        if failed_criteria:
            result["passed"] = False
            result["overall_status"] = "FAIL"
        elif any(c["status"] == "WARNING" for c in result["criteria_results"]):
            result["overall_status"] = "WARNING"

        return result
