"""SEAL-001: Edge Seal Degradation Protocol Implementation."""

from typing import Dict, Any, List
import logging
from datetime import datetime

from ..base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class SEAL001Protocol(BaseProtocol):
    """Edge Seal Degradation Protocol Implementation.

    This protocol implements accelerated aging tests for PV module edge seals
    using humidity-freeze cycling according to IEC 61215-2:2021.
    """

    def __init__(self, protocol_definition: Dict[str, Any]):
        """Initialize SEAL-001 protocol.

        Args:
            protocol_definition: JSON protocol definition
        """
        super().__init__(protocol_definition)
        self.chamber_id: str = None
        self.sample_ids: List[str] = []
        self.cycle_data: List[Dict[str, Any]] = []

        logger.info("SEAL-001 Edge Seal Degradation Protocol initialized")

    def validate_equipment(self) -> bool:
        """Verify environmental chamber and inspection equipment.

        Returns:
            True if all equipment is ready and calibrated
        """
        logger.info("Validating equipment for SEAL-001")

        required_equipment = self.definition.get('equipment', [])

        for equipment in required_equipment:
            logger.info(f"Checking equipment: {equipment['name']}")

            # In production, this would check equipment database
            # and verify calibration status
            if equipment['calibration_required']:
                logger.info(
                    f"  - Calibration required for {equipment['name']}"
                )
                # Would check calibration date here

        # For now, return True as placeholder
        # In production, implement actual equipment verification
        return True

    def prepare_samples(self) -> bool:
        """Prepare PV module samples for edge seal testing.

        Returns:
            True if samples are prepared successfully
        """
        requirements = self.definition.get('sample_requirements', {})
        quantity = requirements.get('quantity', 0)

        logger.info(f"Preparing {quantity} samples for SEAL-001 testing")

        # In production, this would:
        # 1. Verify sample availability
        # 2. Execute preparation steps
        # 3. Document initial condition
        # 4. Assign sample IDs

        for step in requirements.get('preparation', []):
            logger.info(f"  - {step}")

        return True

    def perform_initial_inspection(
        self,
        inspector: str,
        inspection_data: Dict[str, Any]
    ) -> None:
        """Perform initial visual inspection and baseline measurements.

        Args:
            inspector: Name of inspector
            inspection_data: Dictionary containing all measurement data
        """
        logger.info("Performing initial inspection (SEAL-001-01)")

        measurements = {
            'edge_seal_width_top_1': inspection_data.get('edge_seal_width_top_1'),
            'edge_seal_width_top_2': inspection_data.get('edge_seal_width_top_2'),
            'edge_seal_width_bottom_1': inspection_data.get('edge_seal_width_bottom_1'),
            'edge_seal_width_bottom_2': inspection_data.get('edge_seal_width_bottom_2'),
            'edge_seal_width_left_1': inspection_data.get('edge_seal_width_left_1'),
            'edge_seal_width_left_2': inspection_data.get('edge_seal_width_left_2'),
            'edge_seal_width_right_1': inspection_data.get('edge_seal_width_right_1'),
            'edge_seal_width_right_2': inspection_data.get('edge_seal_width_right_2'),
            'initial_defects_count': inspection_data.get('initial_defects_count', 0),
            'initial_defect_description': inspection_data.get('initial_defect_description', ''),
            'baseline_image_top': inspection_data.get('baseline_image_top'),
            'baseline_image_bottom': inspection_data.get('baseline_image_bottom'),
            'baseline_image_left': inspection_data.get('baseline_image_left'),
            'baseline_image_right': inspection_data.get('baseline_image_right'),
        }

        self.execute_step('SEAL-001-01', measurements, inspector)

        # Calculate average seal width for reference
        widths = [
            v for k, v in measurements.items()
            if 'edge_seal_width' in k and v is not None
        ]
        if widths:
            avg_width = sum(widths) / len(widths)
            logger.info(f"Average initial seal width: {avg_width:.2f} mm")

    def execute_humidity_freeze_cycle(
        self,
        cycle_number: int,
        chamber_data: Dict[str, Any],
        operator: str
    ) -> None:
        """Execute a single humidity-freeze cycle.

        Args:
            cycle_number: Current cycle number (1-50)
            chamber_data: Environmental chamber measurements
            operator: Name of operator
        """
        logger.info(f"Executing humidity-freeze cycle {cycle_number}/50")

        measurements = {
            'cycle_number': cycle_number,
            'actual_temperature_damp_heat': chamber_data.get('temp_damp_heat'),
            'actual_humidity_damp_heat': chamber_data.get('humidity_damp_heat'),
            'actual_temperature_freeze': chamber_data.get('temp_freeze'),
            'chamber_deviation_flag': chamber_data.get('deviation_flag', False),
            'deviation_notes': chamber_data.get('deviation_notes', '')
        }

        result = self.execute_step('SEAL-001-02', measurements, operator)

        # Store cycle data for analysis
        self.cycle_data.append({
            'cycle': cycle_number,
            'timestamp': result.timestamp,
            'status': result.status,
            'data': measurements
        })

        if result.status == 'warning':
            logger.warning(
                f"Cycle {cycle_number} completed with warnings - "
                f"chamber deviation detected"
            )

    def perform_intermediate_inspection(
        self,
        inspector: str,
        inspection_data: Dict[str, Any]
    ) -> None:
        """Perform intermediate inspection at cycle 25.

        Args:
            inspector: Name of inspector
            inspection_data: Inspection measurements
        """
        logger.info("Performing intermediate inspection at cycle 25 (SEAL-001-03)")

        measurements = {
            'intermediate_delamination_length': inspection_data.get('delamination_length', 0),
            'intermediate_moisture_ingress': inspection_data.get('moisture_detected', False),
            'intermediate_visual_defects': inspection_data.get('visual_defects', ''),
            'intermediate_images': inspection_data.get('images')
        }

        result = self.execute_step('SEAL-001-03', measurements, inspector)

        if measurements['intermediate_moisture_ingress']:
            logger.warning("Moisture ingress detected at intermediate checkpoint!")

    def perform_final_inspection(
        self,
        inspector: str,
        inspection_data: Dict[str, Any]
    ) -> None:
        """Perform final post-conditioning inspection.

        Args:
            inspector: Name of inspector
            inspection_data: Final inspection measurements
        """
        logger.info("Performing final inspection (SEAL-001-04)")

        measurements = {
            'final_delamination_length_top': inspection_data.get('delamination_top', 0),
            'final_delamination_length_bottom': inspection_data.get('delamination_bottom', 0),
            'final_delamination_length_left': inspection_data.get('delamination_left', 0),
            'final_delamination_length_right': inspection_data.get('delamination_right', 0),
            'moisture_ingress_detected': inspection_data.get('moisture_detected', False),
            'moisture_location': inspection_data.get('moisture_location', ''),
            'adhesion_loss_percentage': inspection_data.get('adhesion_loss', 0),
            'final_image_top': inspection_data.get('image_top'),
            'final_image_bottom': inspection_data.get('image_bottom'),
            'final_image_left': inspection_data.get('image_left'),
            'final_image_right': inspection_data.get('image_right'),
            'final_condition_notes': inspection_data.get('notes', '')
        }

        self.execute_step('SEAL-001-04', measurements, inspector)

        # Log summary
        total_delam = sum([
            measurements['final_delamination_length_top'],
            measurements['final_delamination_length_bottom'],
            measurements['final_delamination_length_left'],
            measurements['final_delamination_length_right']
        ])

        logger.info(f"Total delamination length: {total_delam} mm")

        if measurements['moisture_ingress_detected']:
            logger.warning(
                f"CRITICAL: Moisture ingress detected at {measurements['moisture_location']}"
            )

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive SEAL-001 test report.

        Returns:
            Dictionary containing complete test report
        """
        logger.info("Generating SEAL-001 test report")

        calculations = self.calculate_results()
        pass_fail = self.evaluate_pass_fail()

        # Collect all images
        images = self._collect_images()

        # Build report structure
        report = {
            'protocol': {
                'id': self.protocol_id,
                'name': self.name,
                'version': self.version,
                'category': self.category,
                'standards': self.definition.get('standards', [])
            },
            'test_summary': {
                'start_date': self.results[0].timestamp.isoformat() if self.results else None,
                'end_date': self.results[-1].timestamp.isoformat() if self.results else None,
                'total_duration_hours': self._calculate_duration(),
                'overall_result': 'PASS' if pass_fail['overall_pass'] else 'FAIL',
                'sample_ids': self.sample_ids,
                'chamber_id': self.chamber_id
            },
            'equipment': self.definition.get('equipment', []),
            'measurements': self._format_measurements(),
            'calculations': calculations,
            'evaluation': pass_fail,
            'cycle_summary': self._summarize_cycles(),
            'visual_documentation': {
                'baseline_images': self._get_baseline_images(),
                'final_images': self._get_final_images(),
                'comparison': self._generate_comparison_data()
            },
            'deviations': self._identify_deviations(),
            'conclusions': self._generate_conclusions(pass_fail),
            'recommendations': self._generate_recommendations(pass_fail),
            'metadata': {
                'report_generated': datetime.now().isoformat(),
                'generated_by': 'SEAL-001 Protocol Engine v1.0.0'
            }
        }

        return report

    def _collect_images(self) -> List[str]:
        """Collect all image references from results.

        Returns:
            List of image file paths
        """
        images = []

        for result in self.results:
            for key, value in result.measurements.items():
                if 'image' in key.lower() and value:
                    images.append(value)

        return images

    def _calculate_duration(self) -> float:
        """Calculate total test duration in hours.

        Returns:
            Duration in hours
        """
        if not self.results or len(self.results) < 2:
            return 0.0

        start = self.results[0].timestamp
        end = self.results[-1].timestamp
        duration = (end - start).total_seconds() / 3600

        return round(duration, 2)

    def _format_measurements(self) -> List[Dict[str, Any]]:
        """Format all measurements for reporting.

        Returns:
            List of formatted measurement records
        """
        formatted = []

        for result in self.results:
            formatted.append({
                'step_id': result.step_id,
                'step_name': next(
                    (s.name for s in self.steps if s.step_id == result.step_id),
                    'Unknown'
                ),
                'timestamp': result.timestamp.isoformat(),
                'operator': result.operator,
                'measurements': result.measurements,
                'status': result.status,
                'notes': result.notes
            })

        return formatted

    def _summarize_cycles(self) -> Dict[str, Any]:
        """Summarize humidity-freeze cycle data.

        Returns:
            Cycle summary statistics
        """
        if not self.cycle_data:
            return {}

        total_cycles = len(self.cycle_data)
        warning_cycles = sum(1 for c in self.cycle_data if c['status'] == 'warning')

        return {
            'total_cycles': total_cycles,
            'completed_successfully': total_cycles - warning_cycles,
            'cycles_with_warnings': warning_cycles,
            'warning_rate': f"{(warning_cycles / total_cycles * 100):.1f}%" if total_cycles > 0 else "0%"
        }

    def _get_baseline_images(self) -> Dict[str, str]:
        """Get baseline inspection images.

        Returns:
            Dictionary of edge -> image path
        """
        if not self.results:
            return {}

        baseline_result = next(
            (r for r in self.results if r.step_id == 'SEAL-001-01'),
            None
        )

        if not baseline_result:
            return {}

        return {
            'top': baseline_result.measurements.get('baseline_image_top'),
            'bottom': baseline_result.measurements.get('baseline_image_bottom'),
            'left': baseline_result.measurements.get('baseline_image_left'),
            'right': baseline_result.measurements.get('baseline_image_right')
        }

    def _get_final_images(self) -> Dict[str, str]:
        """Get final inspection images.

        Returns:
            Dictionary of edge -> image path
        """
        final_result = next(
            (r for r in self.results if r.step_id == 'SEAL-001-04'),
            None
        )

        if not final_result:
            return {}

        return {
            'top': final_result.measurements.get('final_image_top'),
            'bottom': final_result.measurements.get('final_image_bottom'),
            'left': final_result.measurements.get('final_image_left'),
            'right': final_result.measurements.get('final_image_right')
        }

    def _generate_comparison_data(self) -> List[Dict[str, Any]]:
        """Generate before/after comparison data.

        Returns:
            List of comparison records
        """
        baseline = self._get_baseline_images()
        final = self._get_final_images()

        comparisons = []

        for edge in ['top', 'bottom', 'left', 'right']:
            comparisons.append({
                'edge': edge,
                'baseline_image': baseline.get(edge),
                'final_image': final.get(edge)
            })

        return comparisons

    def _identify_deviations(self) -> List[Dict[str, Any]]:
        """Identify test deviations from protocol.

        Returns:
            List of deviation records
        """
        deviations = []

        # Check for warning status results
        for result in self.results:
            if result.status == 'warning':
                deviations.append({
                    'step_id': result.step_id,
                    'timestamp': result.timestamp.isoformat(),
                    'type': 'QC Warning',
                    'description': result.notes or 'QC criteria triggered warning',
                    'operator': result.operator
                })

        # Check cycle data for chamber deviations
        for cycle in self.cycle_data:
            if cycle['data'].get('chamber_deviation_flag'):
                deviations.append({
                    'step_id': 'SEAL-001-02',
                    'cycle': cycle['cycle'],
                    'timestamp': cycle['timestamp'].isoformat(),
                    'type': 'Chamber Deviation',
                    'description': cycle['data'].get('deviation_notes', 'Chamber parameter deviation'),
                    'operator': 'System'
                })

        return deviations

    def _generate_conclusions(self, pass_fail: Dict[str, Any]) -> List[str]:
        """Generate test conclusions.

        Args:
            pass_fail: Pass/fail evaluation results

        Returns:
            List of conclusion statements
        """
        conclusions = []

        if pass_fail['overall_pass']:
            conclusions.append(
                "The module edge seals PASSED all acceptance criteria for "
                "degradation resistance under humidity-freeze cycling."
            )
        else:
            conclusions.append(
                "The module edge seals FAILED to meet one or more critical "
                "acceptance criteria."
            )

        # Add specific findings
        for criterion in pass_fail['criteria']:
            if not criterion['passed'] and criterion['severity'] == 'critical':
                conclusions.append(
                    f"CRITICAL FAILURE: {criterion['parameter']} = {criterion['value']} "
                    f"(requirement: {criterion['operator']} {criterion['threshold']})"
                )

        return conclusions

    def _generate_recommendations(self, pass_fail: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on results.

        Args:
            pass_fail: Pass/fail evaluation results

        Returns:
            List of recommendations
        """
        recommendations = []

        if pass_fail['overall_pass']:
            recommendations.append(
                "Edge seal design is adequate for field deployment under "
                "specified environmental conditions."
            )
        else:
            recommendations.append(
                "Edge seal design requires improvement before field deployment."
            )

            # Check for moisture ingress
            final_result = next(
                (r for r in self.results if r.step_id == 'SEAL-001-04'),
                None
            )

            if final_result and final_result.measurements.get('moisture_ingress_detected'):
                recommendations.append(
                    "CRITICAL: Investigate moisture ingress pathway and improve "
                    "hermetic seal design."
                )
                recommendations.append(
                    "Consider alternative sealant materials or application methods."
                )

        # Always recommend documentation
        recommendations.append(
            "Document all findings and update design specifications accordingly."
        )

        return recommendations
