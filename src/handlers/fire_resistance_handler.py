"""
Fire Resistance Testing Protocol Handler
IEC 61730-2 MST 23

This module provides the main handler class for executing and managing
fire resistance tests according to the protocol specification.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..models.fire_resistance_model import (
    SampleInformation,
    EnvironmentalConditions,
    EquipmentCalibration,
    RealTimeMeasurement,
    TestObservations,
    AcceptanceCriteriaResult,
    TestResults,
    TestReport,
    TestStatus,
    PassFailResult,
    SmokeLevel,
    MaterialIntegrity
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FireResistanceProtocolHandler:
    """
    Main handler for Fire Resistance Testing Protocol (FIRE-001)

    This class manages the complete test workflow including:
    - Protocol loading and validation
    - Test execution and data collection
    - Acceptance criteria evaluation
    - Report generation
    - LIMS/QMS integration
    """

    def __init__(self, protocol_path: Optional[str] = None):
        """
        Initialize the protocol handler

        Args:
            protocol_path: Path to the protocol JSON file
        """
        self.protocol_path = protocol_path or self._get_default_protocol_path()
        self.protocol_data = self._load_protocol()
        self.current_test: Optional[TestResults] = None
        self.test_status = TestStatus.RECEIVED

    def _get_default_protocol_path(self) -> str:
        """Get default protocol file path"""
        return str(Path(__file__).parent.parent.parent /
                   "protocols/FIRE-001/json/fire_resistance_protocol.json")

    def _load_protocol(self) -> Dict[str, Any]:
        """Load protocol from JSON file"""
        try:
            with open(self.protocol_path, 'r') as f:
                protocol = json.load(f)
            logger.info(f"Loaded protocol: {protocol['protocol_id']} v{protocol['version']}")
            return protocol
        except FileNotFoundError:
            logger.error(f"Protocol file not found: {self.protocol_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in protocol file: {e}")
            raise

    def validate_equipment_calibration(
        self,
        equipment_list: List[EquipmentCalibration]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required equipment is calibrated and current

        Args:
            equipment_list: List of equipment calibration records

        Returns:
            Tuple of (is_valid, list of issues)
        """
        required_equipment = {
            eq['id']: eq for eq in self.protocol_data['equipment_required']
            if eq.get('calibration_required', False)
        }

        issues = []
        equipment_dict = {eq.equipment_id: eq for eq in equipment_list}

        for eq_id, eq_spec in required_equipment.items():
            if eq_id not in equipment_dict:
                issues.append(f"Missing required equipment: {eq_spec['name']} ({eq_id})")
                continue

            equipment = equipment_dict[eq_id]
            if not equipment.check_validity():
                issues.append(
                    f"Calibration expired for {equipment.equipment_name} "
                    f"(due: {equipment.calibration_due_date.strftime('%Y-%m-%d')})"
                )

        return len(issues) == 0, issues

    def validate_environmental_conditions(
        self,
        conditions: EnvironmentalConditions
    ) -> Tuple[bool, List[str]]:
        """
        Validate environmental conditions against specification

        Args:
            conditions: Environmental conditions to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        spec = self.protocol_data['test_overview']['test_conditions']

        # Temperature check (23 ± 5°C)
        if not (18 <= conditions.temperature_c <= 28):
            issues.append(
                f"Temperature {conditions.temperature_c}°C outside "
                f"specification range (18-28°C)"
            )

        # Humidity check (50 ± 20%)
        if not (30 <= conditions.relative_humidity <= 70):
            issues.append(
                f"Relative humidity {conditions.relative_humidity}% outside "
                f"specification range (30-70%)"
            )

        return len(issues) == 0, issues

    def check_sample_conditioning(
        self,
        conditioning_start: datetime,
        conditioning_end: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """
        Check if sample conditioning period meets minimum requirement

        Args:
            conditioning_start: Start time of conditioning
            conditioning_end: End time of conditioning (default: now)

        Returns:
            Tuple of (is_adequate, message)
        """
        if conditioning_end is None:
            conditioning_end = datetime.now()

        duration = conditioning_end - conditioning_start
        minimum_hours = 24

        if duration.total_seconds() >= minimum_hours * 3600:
            return True, f"Conditioning period: {duration.total_seconds() / 3600:.1f} hours (OK)"
        else:
            remaining = minimum_hours - (duration.total_seconds() / 3600)
            return False, f"Insufficient conditioning. {remaining:.1f} hours remaining"

    def evaluate_acceptance_criteria(
        self,
        observations: TestObservations
    ) -> List[AcceptanceCriteriaResult]:
        """
        Evaluate test results against acceptance criteria

        Args:
            observations: Test observations and measurements

        Returns:
            List of acceptance criteria evaluation results
        """
        criteria_results = []

        # Critical Criterion 1: No Sustained Burning
        self_ext_time = observations.self_extinguishing_time_seconds or 0
        criteria_results.append(AcceptanceCriteriaResult(
            criterion_name="No Sustained Burning",
            requirement="Module must self-extinguish within 60 seconds after flame removal",
            measured_value=self_ext_time,
            pass_condition="<= 60 seconds",
            result=PassFailResult.PASS if self_ext_time <= 60 else PassFailResult.FAIL,
            severity="critical",
            notes=f"Self-extinguishing time: {self_ext_time} seconds"
        ))

        # Critical Criterion 2: Limited Flame Spread
        flame_spread = observations.max_flame_spread_mm
        criteria_results.append(AcceptanceCriteriaResult(
            criterion_name="Limited Flame Spread",
            requirement="Flame spread must not exceed 100 mm from flame application point",
            measured_value=flame_spread,
            pass_condition="<= 100 mm",
            result=PassFailResult.PASS if flame_spread <= 100 else PassFailResult.FAIL,
            severity="critical",
            notes=f"Maximum flame spread: {flame_spread} mm"
        ))

        # Critical Criterion 3: No Flaming Drips
        criteria_results.append(AcceptanceCriteriaResult(
            criterion_name="No Flaming Drips",
            requirement="No flaming material shall drip from the module",
            measured_value=observations.flaming_drips,
            pass_condition="No flaming drips observed",
            result=PassFailResult.PASS if not observations.flaming_drips else PassFailResult.FAIL,
            severity="critical",
            notes="Flaming drips observed" if observations.flaming_drips else "No flaming drips"
        ))

        # Major Criterion 1: Material Integrity
        integrity_ok = observations.material_integrity in [
            MaterialIntegrity.INTACT,
            MaterialIntegrity.MINOR_DAMAGE
        ]
        criteria_results.append(AcceptanceCriteriaResult(
            criterion_name="Material Integrity",
            requirement="Module structure must remain substantially intact",
            measured_value=observations.material_integrity.value,
            pass_condition="No through-penetration or structural failure",
            result=PassFailResult.PASS if integrity_ok else PassFailResult.FAIL,
            severity="major",
            notes=f"Material integrity: {observations.material_integrity.value}"
        ))

        return criteria_results

    def create_test_session(
        self,
        sample: SampleInformation,
        test_personnel: List[str],
        test_id: Optional[str] = None
    ) -> TestResults:
        """
        Create a new test session

        Args:
            sample: Sample information
            test_personnel: List of personnel conducting the test
            test_id: Optional test ID (auto-generated if not provided)

        Returns:
            TestResults object
        """
        if test_id is None:
            test_id = f"FIRE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.current_test = TestResults(
            test_id=test_id,
            sample=sample,
            test_date=datetime.now(),
            test_personnel=test_personnel,
            environmental_conditions=EnvironmentalConditions(
                temperature_c=23.0,
                relative_humidity=50.0
            ),
            equipment_used=[],
            real_time_data=[],
            observations=TestObservations(),
            acceptance_results=[],
            overall_result=PassFailResult.PENDING
        )

        self.test_status = TestStatus.READY_FOR_TEST
        logger.info(f"Created test session: {test_id}")
        return self.current_test

    def record_measurement(
        self,
        elapsed_time_seconds: float,
        surface_temperature_c: float,
        flame_spread_mm: Optional[float] = None,
        observations: str = ""
    ) -> RealTimeMeasurement:
        """
        Record a real-time measurement during test

        Args:
            elapsed_time_seconds: Time since test start
            surface_temperature_c: Surface temperature measurement
            flame_spread_mm: Flame spread distance (optional)
            observations: Text observations (optional)

        Returns:
            RealTimeMeasurement object
        """
        if self.current_test is None:
            raise ValueError("No active test session")

        measurement = RealTimeMeasurement(
            timestamp=datetime.now(),
            elapsed_time_seconds=elapsed_time_seconds,
            surface_temperature_c=surface_temperature_c,
            flame_spread_mm=flame_spread_mm,
            observations=observations
        )

        self.current_test.real_time_data.append(measurement)
        logger.debug(f"Recorded measurement at t={elapsed_time_seconds}s: T={surface_temperature_c}°C")
        return measurement

    def finalize_test(
        self,
        observations: TestObservations,
        post_test_photos: Optional[List[str]] = None
    ) -> TestResults:
        """
        Finalize test and evaluate results

        Args:
            observations: Final test observations
            post_test_photos: List of post-test photo file paths

        Returns:
            Completed TestResults object
        """
        if self.current_test is None:
            raise ValueError("No active test session")

        # Update observations
        self.current_test.observations = observations

        # Add post-test photos
        if post_test_photos:
            self.current_test.post_test_photos = post_test_photos

        # Evaluate acceptance criteria
        self.current_test.acceptance_results = self.evaluate_acceptance_criteria(observations)

        # Determine overall result
        self.current_test.evaluate_acceptance_criteria()

        # Update test duration
        if self.current_test.real_time_data:
            max_time = max(m.elapsed_time_seconds for m in self.current_test.real_time_data)
            self.current_test.test_duration_minutes = max_time / 60

        self.test_status = TestStatus.TEST_COMPLETE
        logger.info(
            f"Test {self.current_test.test_id} completed: "
            f"{self.current_test.overall_result.value}"
        )

        return self.current_test

    def generate_report(
        self,
        test_results: Optional[TestResults] = None,
        report_id: Optional[str] = None,
        prepared_by: str = "",
        reviewed_by: str = "",
        approved_by: str = ""
    ) -> TestReport:
        """
        Generate comprehensive test report

        Args:
            test_results: Test results to report (uses current test if not provided)
            report_id: Optional report ID
            prepared_by: Name of person preparing report
            reviewed_by: Name of reviewer
            approved_by: Name of approver

        Returns:
            TestReport object
        """
        if test_results is None:
            if self.current_test is None:
                raise ValueError("No test results available")
            test_results = self.current_test

        if report_id is None:
            report_id = f"RPT-{test_results.test_id}"

        report = TestReport(
            report_id=report_id,
            protocol_id=self.protocol_data['protocol_id'],
            protocol_version=self.protocol_data['version'],
            results=test_results,
            prepared_by=prepared_by,
            reviewed_by=reviewed_by,
            approved_by=approved_by
        )

        # Generate executive summary
        report.generate_executive_summary()

        # Generate analysis
        report.analysis = self._generate_analysis(test_results)

        # Generate conclusion
        report.conclusion = self._generate_conclusion(test_results)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(test_results)

        logger.info(f"Generated report: {report_id}")
        return report

    def _generate_analysis(self, results: TestResults) -> str:
        """Generate analysis section of report"""
        analysis_parts = []

        analysis_parts.append("## Test Performance Analysis\n")

        # Temperature analysis
        if results.real_time_data:
            temps = [m.surface_temperature_c for m in results.real_time_data]
            max_temp = max(temps)
            avg_temp = sum(temps) / len(temps)
            analysis_parts.append(
                f"- Maximum surface temperature: {max_temp:.1f}°C\n"
                f"- Average surface temperature: {avg_temp:.1f}°C\n"
            )

        # Flame spread analysis
        analysis_parts.append(
            f"- Maximum flame spread: {results.observations.max_flame_spread_mm} mm\n"
        )

        # Ignition analysis
        if results.observations.ignition_occurred:
            analysis_parts.append(
                f"- Ignition occurred at {results.observations.time_to_ignition_seconds} seconds\n"
            )
            if results.observations.self_extinguishing:
                analysis_parts.append(
                    f"- Self-extinguished after {results.observations.self_extinguishing_time_seconds} seconds\n"
                )
        else:
            analysis_parts.append("- No ignition occurred during test\n")

        # Acceptance criteria summary
        analysis_parts.append("\n## Acceptance Criteria Evaluation\n")
        for criterion in results.acceptance_results:
            status = "✓ PASS" if criterion.result == PassFailResult.PASS else "✗ FAIL"
            analysis_parts.append(
                f"- {criterion.criterion_name}: {status}\n"
                f"  - Measured: {criterion.measured_value}\n"
                f"  - Required: {criterion.pass_condition}\n"
            )

        return "".join(analysis_parts)

    def _generate_conclusion(self, results: TestResults) -> str:
        """Generate conclusion section of report"""
        conclusion_parts = []

        conclusion_parts.append(
            f"Based on testing conducted in accordance with IEC 61730-2 MST 23, "
            f"the sample {results.sample.manufacturer} {results.sample.model_number} "
            f"(S/N: {results.sample.serial_number}) "
        )

        if results.overall_result == PassFailResult.PASS:
            conclusion_parts.append(
                "**PASSED** all fire resistance requirements.\n\n"
                "The module demonstrated adequate fire resistance with no sustained burning, "
                "limited flame spread, and no flaming drips."
            )
        elif results.overall_result == PassFailResult.FAIL:
            failed_critical = [
                c for c in results.acceptance_results
                if c.severity == "critical" and c.result == PassFailResult.FAIL
            ]
            conclusion_parts.append(
                f"**FAILED** fire resistance requirements.\n\n"
                f"The following critical criteria were not met:\n"
            )
            for criterion in failed_critical:
                conclusion_parts.append(f"- {criterion.criterion_name}\n")
        else:
            conclusion_parts.append(
                "results are **CONDITIONAL** pending engineering review.\n\n"
                "Major criteria failures require further evaluation."
            )

        return "".join(conclusion_parts)

    def _generate_recommendations(self, results: TestResults) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if results.overall_result == PassFailResult.FAIL:
            recommendations.append(
                "Material composition should be reviewed for fire retardant properties"
            )
            recommendations.append(
                "Consider alternative backsheet or encapsulation materials"
            )

            if results.observations.flaming_drips:
                recommendations.append(
                    "Investigate polymer materials that do not produce flaming drips"
                )

            if results.observations.max_flame_spread_mm > 100:
                recommendations.append(
                    "Improve fire barrier properties to limit flame propagation"
                )

        elif results.overall_result == PassFailResult.CONDITIONAL:
            recommendations.append(
                "Engineering review recommended to assess major criterion failures"
            )

        else:
            recommendations.append(
                "Module meets fire resistance requirements for intended application"
            )
            recommendations.append(
                "Maintain current material specifications and manufacturing processes"
            )

        return recommendations

    def export_results(
        self,
        test_results: TestResults,
        output_dir: str,
        formats: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Export test results in multiple formats

        Args:
            test_results: Test results to export
            output_dir: Output directory path
            formats: List of formats (json, csv, pdf). Default: all

        Returns:
            Dictionary mapping format to output file path
        """
        if formats is None:
            formats = ['json', 'csv']

        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        # Export JSON
        if 'json' in formats:
            json_path = output_dir_path / f"{test_results.test_id}_results.json"
            test_results.to_json(str(json_path))
            exported_files['json'] = str(json_path)
            logger.info(f"Exported JSON: {json_path}")

        # Export CSV
        if 'csv' in formats:
            csv_path = output_dir_path / f"{test_results.test_id}_measurements.csv"
            report = self.generate_report(test_results)
            report.export_to_csv(str(csv_path))
            exported_files['csv'] = str(csv_path)
            logger.info(f"Exported CSV: {csv_path}")

        return exported_files

    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol information summary"""
        return {
            'protocol_id': self.protocol_data['protocol_id'],
            'protocol_name': self.protocol_data['protocol_name'],
            'version': self.protocol_data['version'],
            'standard': self.protocol_data['standard'],
            'category': self.protocol_data['category']
        }
