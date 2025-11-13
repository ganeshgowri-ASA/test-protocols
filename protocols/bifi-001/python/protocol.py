"""
Main protocol handler for BIFI-001 Bifacial Performance testing
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from .validator import BifacialValidator
from .calculator import BifacialCalculator, IVParameters


class BifacialProtocol:
    """
    Main protocol handler for BIFI-001 Bifacial Performance testing
    Implements IEC 60904-1-2 standard
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize protocol handler

        Args:
            schema_path: Path to protocol schema (optional)
        """
        self.validator = BifacialValidator(schema_path)
        self.calculator = BifacialCalculator()
        self.data = None

    def load_template(self) -> Dict:
        """
        Load data template

        Returns:
            Template data dictionary
        """
        template_path = Path(__file__).parent.parent / "schemas" / "data_template.json"
        with open(template_path, 'r') as f:
            return json.load(f)

    def create_test(self, metadata: Dict, device_info: Dict, test_conditions: Dict) -> Dict:
        """
        Create a new test data structure

        Args:
            metadata: Test metadata (operator, date, etc.)
            device_info: Device under test information
            test_conditions: Test condition parameters

        Returns:
            Initialized test data dictionary
        """
        self.data = self.load_template()

        # Update with provided data
        self.data["metadata"].update(metadata)
        self.data["device_under_test"].update(device_info)
        self.data["test_conditions"].update(test_conditions)

        # Set test date to now if not provided
        if "test_date" not in self.data["metadata"]:
            self.data["metadata"]["test_date"] = datetime.utcnow().isoformat() + "Z"

        return self.data

    def add_iv_measurement(self, side: str, iv_curve: List[Dict],
                          irradiance: float, area: float = None) -> IVParameters:
        """
        Add I-V curve measurement for front or rear side

        Args:
            side: "front" or "rear"
            iv_curve: List of voltage-current measurement points
            irradiance: Irradiance during measurement (W/m²)
            area: Active area in cm² (optional)

        Returns:
            Calculated I-V parameters
        """
        if self.data is None:
            raise ValueError("No test data initialized. Call create_test() first.")

        if side not in ["front", "rear"]:
            raise ValueError("side must be 'front' or 'rear'")

        # Use device area if not provided
        if area is None:
            area = self.data["device_under_test"].get(f"area_{side}", 25000)

        # Calculate parameters
        params = self.calculator.calculate_iv_parameters(iv_curve, area, irradiance)

        # Store in data structure
        side_data = self.data["measurements"][f"{side}_side"]
        side_data["iv_curve"] = iv_curve
        side_data["isc"] = params.isc
        side_data["voc"] = params.voc
        side_data["pmax"] = params.pmax
        side_data["imp"] = params.imp
        side_data["vmp"] = params.vmp
        side_data["fill_factor"] = params.fill_factor
        if params.efficiency is not None:
            side_data["efficiency"] = params.efficiency

        return params

    def calculate_bifacial_parameters(self) -> Dict:
        """
        Calculate bifacial performance parameters

        Returns:
            Dictionary with bifacial parameters
        """
        if self.data is None:
            raise ValueError("No test data initialized")

        front = self.data["measurements"]["front_side"]
        rear = self.data["measurements"]["rear_side"]

        if not front.get("pmax") or not rear.get("pmax"):
            raise ValueError("Both front and rear measurements required")

        # Calculate bifaciality factor
        bifaciality = self.calculator.calculate_bifaciality(
            front["pmax"],
            rear["pmax"]
        )

        # Calculate bifacial gain
        front_irr = self.data["test_conditions"]["front_irradiance"]["value"]
        rear_irr = self.data["test_conditions"]["rear_irradiance"]["value"]

        bifacial_gain = self.calculator.calculate_bifacial_gain(
            front["pmax"],
            rear["pmax"],
            front_irr,
            rear_irr
        )

        # Calculate equivalent efficiency
        area = self.data["device_under_test"].get("area_front", 25000)
        front_params = IVParameters(
            isc=front["isc"],
            voc=front["voc"],
            pmax=front["pmax"],
            imp=front["imp"],
            vmp=front["vmp"],
            fill_factor=front["fill_factor"]
        )
        rear_params = IVParameters(
            isc=rear["isc"],
            voc=rear["voc"],
            pmax=rear["pmax"],
            imp=rear["imp"],
            vmp=rear["vmp"],
            fill_factor=rear["fill_factor"]
        )

        equiv_eff = self.calculator.calculate_equivalent_efficiency(
            front_params,
            rear_params,
            front_irr,
            rear_irr,
            area
        )

        # Update data structure
        bifacial_data = {
            "measured_bifaciality": round(bifaciality, 4),
            "bifacial_gain": round(bifacial_gain, 2),
            "equivalent_front_efficiency": round(equiv_eff, 2)
        }

        self.data["measurements"]["bifacial_measurements"].update(bifacial_data)

        return bifacial_data

    def run_validation(self) -> Dict:
        """
        Run complete validation on test data

        Returns:
            Validation results dictionary
        """
        if self.data is None:
            raise ValueError("No test data to validate")

        results = self.validator.validate_all(self.data)

        # Add validation checks to QC section
        self.data["quality_control"]["validation_checks"] = results["checks"]

        # Calculate uncertainty
        uncertainty = self.calculator.calculate_uncertainty(self.data["measurements"])
        self.data["quality_control"]["uncertainty_analysis"] = uncertainty

        return results

    def analyze_performance(self) -> Dict:
        """
        Analyze device performance against specifications

        Returns:
            Analysis results dictionary
        """
        if self.data is None:
            raise ValueError("No test data to analyze")

        device = self.data["device_under_test"]
        measurements = self.data["measurements"]

        deviations = []
        recommendations = []

        # Check front side performance
        if device.get("rated_power_front"):
            rated_front = device["rated_power_front"]
            measured_front = measurements["front_side"]["pmax"]
            deviation_pct = ((measured_front - rated_front) / rated_front) * 100

            deviations.append({
                "parameter": "Front Side Pmax",
                "expected": rated_front,
                "measured": measured_front,
                "deviation_percent": round(deviation_pct, 2)
            })

            if deviation_pct < -5:
                recommendations.append(
                    f"Front side power is {abs(deviation_pct):.1f}% below rated. "
                    "Check for module degradation or measurement conditions."
                )

        # Check rear side performance
        if device.get("rated_power_rear"):
            rated_rear = device["rated_power_rear"]
            measured_rear = measurements["rear_side"]["pmax"]
            deviation_pct = ((measured_rear - rated_rear) / rated_rear) * 100

            deviations.append({
                "parameter": "Rear Side Pmax",
                "expected": rated_rear,
                "measured": measured_rear,
                "deviation_percent": round(deviation_pct, 2)
            })

            if deviation_pct < -5:
                recommendations.append(
                    f"Rear side power is {abs(deviation_pct):.1f}% below rated. "
                    "Verify rear surface condition and measurement setup."
                )

        # Check bifaciality factor
        if device.get("bifaciality_factor"):
            expected_bf = device["bifaciality_factor"]
            measured_bf = measurements["bifacial_measurements"]["measured_bifaciality"]
            deviation_pct = ((measured_bf - expected_bf) / expected_bf) * 100

            deviations.append({
                "parameter": "Bifaciality Factor",
                "expected": expected_bf,
                "measured": measured_bf,
                "deviation_percent": round(deviation_pct, 2)
            })

            if abs(deviation_pct) > 10:
                recommendations.append(
                    f"Bifaciality factor deviates {abs(deviation_pct):.1f}% from specification. "
                    "Review measurement conditions and device condition."
                )

        # Determine pass/fail status
        major_deviations = [d for d in deviations if abs(d["deviation_percent"]) > 10]
        if major_deviations:
            status = "fail"
        elif any(abs(d["deviation_percent"]) > 5 for d in deviations):
            status = "conditional"
        else:
            status = "pass"

        analysis_results = {
            "pass_fail_status": status,
            "deviations": deviations,
            "recommendations": recommendations
        }

        self.data["analysis_results"] = analysis_results

        return analysis_results

    def save(self, filepath: str):
        """
        Save test data to JSON file

        Args:
            filepath: Path to save file
        """
        if self.data is None:
            raise ValueError("No test data to save")

        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def load(self, filepath: str) -> Dict:
        """
        Load test data from JSON file

        Args:
            filepath: Path to load file

        Returns:
            Loaded test data
        """
        with open(filepath, 'r') as f:
            self.data = json.load(f)
        return self.data

    def generate_report_data(self) -> Dict:
        """
        Generate formatted data for report generation

        Returns:
            Report data dictionary
        """
        if self.data is None:
            raise ValueError("No test data available")

        report = {
            "title": "BIFI-001 Bifacial Performance Test Report",
            "standard": self.data["metadata"]["standard"],
            "test_date": self.data["metadata"]["test_date"],
            "operator": self.data["metadata"]["operator"],
            "device": {
                "id": self.data["device_under_test"]["device_id"],
                "manufacturer": self.data["device_under_test"]["manufacturer"],
                "model": self.data["device_under_test"]["model"],
                "serial": self.data["device_under_test"].get("serial_number", "N/A")
            },
            "conditions": {
                "front_irradiance": self.data["test_conditions"]["front_irradiance"]["value"],
                "rear_irradiance": self.data["test_conditions"]["rear_irradiance"]["value"],
                "temperature": self.data["test_conditions"]["temperature"]["value"],
                "stc": self.data["test_conditions"].get("stc_conditions", False)
            },
            "results": {
                "front": self.data["measurements"]["front_side"],
                "rear": self.data["measurements"]["rear_side"],
                "bifacial": self.data["measurements"]["bifacial_measurements"]
            },
            "validation": self.data["quality_control"].get("validation_checks", []),
            "uncertainty": self.data["quality_control"].get("uncertainty_analysis", {}),
            "analysis": self.data.get("analysis_results", {}),
            "status": self.data.get("analysis_results", {}).get("pass_fail_status", "unknown")
        }

        return report
