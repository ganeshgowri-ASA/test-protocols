"""
WIND-001 - Wind Load Test Protocol Implementation
Implements wind load testing for PV modules according to IEC 61215 and UL 1703
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    INCOMPLETE = "incomplete"
    IN_PROGRESS = "in_progress"


class LoadType(Enum):
    """Wind load type"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CYCLIC = "cyclic"


@dataclass
class ElectricalPerformance:
    """Electrical performance measurements"""
    voc: float  # Open circuit voltage (V)
    isc: float  # Short circuit current (A)
    vmp: float  # Voltage at max power (V)
    imp: float  # Current at max power (A)
    pmax: float  # Maximum power (W)

    def calculate_degradation(self, baseline: 'ElectricalPerformance') -> float:
        """Calculate power degradation percentage"""
        if baseline.pmax == 0:
            return 0.0
        return ((baseline.pmax - self.pmax) / baseline.pmax) * 100


@dataclass
class CycleMeasurement:
    """Measurement data for a single test cycle"""
    cycle_number: int
    timestamp: str
    actual_pressure: float  # Pa
    deflection_center: float  # mm
    deflection_edges: List[float]  # mm
    observations: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class WindLoadTest:
    """Wind Load Test Protocol (WIND-001) implementation"""

    PROTOCOL_ID = "WIND-001"
    VERSION = "1.0.0"

    def __init__(self, protocol_dir: Optional[Path] = None):
        """
        Initialize wind load test protocol

        Args:
            protocol_dir: Path to protocol configuration directory
        """
        self.protocol_dir = protocol_dir or Path(__file__).parent.parent.parent / "protocols/mechanical/wind-001"
        self.schema = self._load_json("schema.json")
        self.config = self._load_json("config.json")
        self.test_data: Dict[str, Any] = {}
        self.cycle_measurements: List[CycleMeasurement] = []

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file"""
        filepath = self.protocol_dir / filename
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            return {}

    def initialize_test(self, test_metadata: Dict[str, Any],
                       sample_info: Dict[str, Any],
                       test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize a new wind load test

        Args:
            test_metadata: Test identification and operator information
            sample_info: PV module sample information
            test_parameters: Test execution parameters

        Returns:
            Initialized test data structure
        """
        self.test_data = {
            "test_metadata": {
                **test_metadata,
                "test_date": datetime.now().isoformat(),
                "protocol_id": self.PROTOCOL_ID,
                "protocol_version": self.VERSION
            },
            "sample_info": sample_info,
            "test_parameters": test_parameters,
            "measurements": {
                "pre_test": {},
                "during_test": [],
                "post_test": {}
            },
            "acceptance_criteria": self.config.get("default_parameters", {}).get("acceptance_criteria", {}),
            "results": {
                "test_status": TestStatus.IN_PROGRESS.value
            },
            "attachments": []
        }

        logger.info(f"Initialized test {test_metadata.get('test_id')} for sample {sample_info.get('sample_id')}")
        return self.test_data

    def record_pre_test_measurements(self,
                                    visual_inspection: str,
                                    electrical_performance: ElectricalPerformance,
                                    insulation_resistance: float) -> None:
        """
        Record pre-test baseline measurements

        Args:
            visual_inspection: Visual inspection notes
            electrical_performance: Baseline electrical measurements
            insulation_resistance: Insulation resistance in MΩ
        """
        self.test_data["measurements"]["pre_test"] = {
            "visual_inspection": visual_inspection,
            "electrical_performance": asdict(electrical_performance),
            "insulation_resistance": insulation_resistance,
            "timestamp": datetime.now().isoformat()
        }
        logger.info("Pre-test measurements recorded")

    def record_cycle_measurement(self, measurement: CycleMeasurement) -> None:
        """
        Record measurement data for a test cycle

        Args:
            measurement: Cycle measurement data
        """
        self.cycle_measurements.append(measurement)
        self.test_data["measurements"]["during_test"].append(measurement.to_dict())
        logger.info(f"Recorded cycle {measurement.cycle_number} measurement")

    def record_post_test_measurements(self,
                                     visual_inspection: str,
                                     electrical_performance: ElectricalPerformance,
                                     insulation_resistance: float,
                                     defects_observed: List[str]) -> None:
        """
        Record post-test measurements

        Args:
            visual_inspection: Post-test visual inspection notes
            electrical_performance: Final electrical measurements
            insulation_resistance: Final insulation resistance in MΩ
            defects_observed: List of observed defects
        """
        self.test_data["measurements"]["post_test"] = {
            "visual_inspection": visual_inspection,
            "electrical_performance": asdict(electrical_performance),
            "insulation_resistance": insulation_resistance,
            "defects_observed": defects_observed,
            "timestamp": datetime.now().isoformat()
        }
        logger.info("Post-test measurements recorded")

    def calculate_results(self) -> Dict[str, Any]:
        """
        Calculate test results and determine pass/fail status

        Returns:
            Results dictionary with test status and analysis
        """
        pre_test = self.test_data["measurements"]["pre_test"]
        post_test = self.test_data["measurements"]["post_test"]
        criteria = self.test_data["acceptance_criteria"]

        # Calculate power degradation
        pre_perf = ElectricalPerformance(**pre_test["electrical_performance"])
        post_perf = ElectricalPerformance(**post_test["electrical_performance"])
        power_degradation = post_perf.calculate_degradation(pre_perf)

        # Find maximum deflection
        max_deflection = max(
            (m["deflection_center"] for m in self.test_data["measurements"]["during_test"]),
            default=0.0
        )

        # Evaluate pass/fail criteria
        failure_modes = []

        # Check power degradation
        max_degradation = criteria.get("max_power_degradation_percent", 5)
        if power_degradation > max_degradation:
            failure_modes.append(f"Power degradation {power_degradation:.2f}% exceeds limit {max_degradation}%")

        # Check insulation resistance
        min_insulation = criteria.get("min_insulation_resistance_mohm", 40)
        if post_test["insulation_resistance"] < min_insulation:
            failure_modes.append(f"Insulation resistance {post_test['insulation_resistance']} MΩ below limit {min_insulation} MΩ")

        # Check visual defects
        defects = post_test.get("defects_observed", [])
        if criteria.get("no_visual_defects", True) and any(d != "none" for d in defects):
            failure_modes.append(f"Visual defects observed: {', '.join(d for d in defects if d != 'none')}")

        # Determine test status
        if failure_modes:
            test_status = TestStatus.FAIL.value
        else:
            test_status = TestStatus.PASS.value

        results = {
            "test_status": test_status,
            "power_degradation": round(power_degradation, 2),
            "max_deflection_measured": round(max_deflection, 2),
            "failure_modes": failure_modes,
            "notes": "",
            "analysis_timestamp": datetime.now().isoformat()
        }

        self.test_data["results"] = results
        logger.info(f"Test results calculated: {test_status}")

        return results

    def validate_test_data(self) -> tuple[bool, List[str]]:
        """
        Validate test data against schema

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required sections
        required_sections = ["test_metadata", "sample_info", "test_parameters", "measurements", "results"]
        for section in required_sections:
            if section not in self.test_data:
                errors.append(f"Missing required section: {section}")

        # Validate measurements exist
        if "measurements" in self.test_data:
            measurements = self.test_data["measurements"]
            if not measurements.get("pre_test"):
                errors.append("Missing pre-test measurements")
            if not measurements.get("post_test"):
                errors.append("Missing post-test measurements")
            if not measurements.get("during_test"):
                errors.append("No cycle measurements recorded")

        # Validate pressure accuracy
        if "during_test" in self.test_data.get("measurements", {}):
            target_pressure = self.test_data["test_parameters"].get("pressure", 0)
            for cycle in self.test_data["measurements"]["during_test"]:
                actual = cycle.get("actual_pressure", 0)
                if target_pressure > 0:
                    accuracy = abs(actual - target_pressure) / target_pressure
                    if accuracy > 0.05:  # 5% tolerance
                        errors.append(f"Cycle {cycle.get('cycle_number')}: Pressure accuracy {accuracy*100:.1f}% exceeds 5%")

        is_valid = len(errors) == 0
        return is_valid, errors

    def export_test_data(self, filepath: Path) -> None:
        """
        Export test data to JSON file

        Args:
            filepath: Output file path
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.test_data, f, indent=2)
        logger.info(f"Test data exported to {filepath}")

    def import_test_data(self, filepath: Path) -> None:
        """
        Import test data from JSON file

        Args:
            filepath: Input file path
        """
        with open(filepath, 'r') as f:
            self.test_data = json.load(f)

        # Rebuild cycle measurements list
        self.cycle_measurements = [
            CycleMeasurement(**cycle)
            for cycle in self.test_data.get("measurements", {}).get("during_test", [])
        ]

        logger.info(f"Test data imported from {filepath}")

    def generate_summary_report(self) -> str:
        """
        Generate a text summary report

        Returns:
            Formatted summary report string
        """
        metadata = self.test_data.get("test_metadata", {})
        sample = self.test_data.get("sample_info", {})
        results = self.test_data.get("results", {})

        report = f"""
========================================
WIND-001 Wind Load Test Summary Report
========================================

Test ID: {metadata.get('test_id')}
Test Date: {metadata.get('test_date')}
Operator: {metadata.get('operator')}
Standard: {metadata.get('standard')}

Sample Information:
------------------
Sample ID: {sample.get('sample_id')}
Manufacturer: {sample.get('manufacturer')}
Model: {sample.get('model')}
Serial Number: {sample.get('serial_number', 'N/A')}
Rated Power: {sample.get('rated_power', 'N/A')} W

Test Results:
-------------
Status: {results.get('test_status', 'N/A').upper()}
Power Degradation: {results.get('power_degradation', 'N/A')}%
Max Deflection: {results.get('max_deflection_measured', 'N/A')} mm

"""

        if results.get('failure_modes'):
            report += "Failure Modes:\n"
            for mode in results['failure_modes']:
                report += f"  - {mode}\n"

        report += "\n========================================\n"

        return report


def main():
    """Example usage of Wind Load Test protocol"""
    # Initialize protocol
    protocol = WindLoadTest()

    # Initialize test
    test_data = protocol.initialize_test(
        test_metadata={
            "test_id": "WIND-001-2024-001",
            "operator": "John Doe",
            "standard": "IEC 61215-2:2021",
            "equipment_id": "WT-001",
            "calibration_date": "2024-01-15"
        },
        sample_info={
            "sample_id": "PV-MOD-12345",
            "manufacturer": "SolarTech Inc.",
            "model": "ST-400-M",
            "serial_number": "SN123456",
            "technology": "mono-Si",
            "rated_power": 400,
            "dimensions": {
                "length": 1755,
                "width": 1038,
                "thickness": 35
            }
        },
        test_parameters={
            "load_type": "cyclic",
            "pressure": 2400,
            "duration": 60,
            "cycles": 3,
            "temperature": 25,
            "humidity": 50,
            "mounting_configuration": "fixed_tilt"
        }
    )

    # Record pre-test measurements
    protocol.record_pre_test_measurements(
        visual_inspection="No defects observed",
        electrical_performance=ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        ),
        insulation_resistance=500.0
    )

    # Simulate test cycles
    for cycle in range(1, 4):
        measurement = CycleMeasurement(
            cycle_number=cycle,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0],
            observations="Normal deflection observed"
        )
        protocol.record_cycle_measurement(measurement)

    # Record post-test measurements
    protocol.record_post_test_measurements(
        visual_inspection="No defects observed after testing",
        electrical_performance=ElectricalPerformance(
            voc=48.3, isc=10.1, vmp=39.8, imp=9.9, pmax=394.0
        ),
        insulation_resistance=480.0,
        defects_observed=["none"]
    )

    # Calculate results
    results = protocol.calculate_results()

    # Validate and export
    is_valid, errors = protocol.validate_test_data()
    if is_valid:
        print(protocol.generate_summary_report())
        protocol.export_test_data(Path("test_output.json"))
    else:
        print("Validation errors:", errors)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
