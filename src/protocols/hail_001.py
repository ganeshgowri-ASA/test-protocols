"""
HAIL-001 Hail Impact Test Protocol Implementation
IEC 61215 MQT 17
"""

from typing import Dict, Any, List, Optional
from .base import BaseProtocol
from ..analysis.calculations import PowerDegradationCalculator, StatisticalAnalyzer


class HAIL001Protocol(BaseProtocol):
    """Implementation of HAIL-001 Hail Impact Test protocol"""

    def __init__(self, protocol_data: Dict[str, Any]):
        """
        Initialize HAIL-001 protocol

        Args:
            protocol_data: Protocol definition dictionary
        """
        super().__init__(protocol_data)
        self.standard_params = self.test_parameters['standard_test']
        self.extended_params = self.test_parameters.get('extended_test', {})

    def validate_test_data(self, test_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate test data for HAIL-001

        Args:
            test_data: Test execution data

        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []

        # Validate pre-test data
        if 'pre_test_data' not in test_data:
            errors.append("Missing pre_test_data")
        else:
            pre_test = test_data['pre_test_data']
            if 'Pmax_initial' not in pre_test:
                errors.append("Missing initial Pmax measurement")
            if 'insulation_resistance_initial' not in pre_test:
                errors.append("Missing initial insulation resistance")

        # Validate test execution data
        if 'test_execution_data' not in test_data:
            errors.append("Missing test_execution_data")
        else:
            exec_data = test_data['test_execution_data']
            if 'impacts' not in exec_data:
                errors.append("Missing impact data")
            else:
                impacts = exec_data['impacts']
                if len(impacts) != 11:
                    errors.append(f"Expected 11 impacts, found {len(impacts)}")

                # Validate each impact
                for i, impact in enumerate(impacts, 1):
                    if 'actual_velocity_kmh' not in impact:
                        errors.append(f"Impact {i}: Missing velocity data")
                    else:
                        velocity = impact['actual_velocity_kmh']
                        target = self.standard_params['impact_velocity_kmh']
                        if abs(velocity - target) > 2:
                            errors.append(f"Impact {i}: Velocity {velocity} km/h out of tolerance (±2 km/h)")

                    if 'time_delta_seconds' not in impact:
                        errors.append(f"Impact {i}: Missing time delta")
                    elif impact['time_delta_seconds'] > 60:
                        errors.append(f"Impact {i}: Time delta {impact['time_delta_seconds']}s exceeds 60s limit")

        # Validate post-test data
        if 'post_test_data' not in test_data:
            errors.append("Missing post_test_data")
        else:
            post_test = test_data['post_test_data']
            if 'Pmax_final' not in post_test:
                errors.append("Missing final Pmax measurement")
            if 'insulation_resistance_final' not in post_test:
                errors.append("Missing final insulation resistance")

        return (len(errors) == 0, errors)

    def analyze_results(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze HAIL-001 test results

        Args:
            test_data: Test execution data

        Returns:
            Dictionary containing analysis results
        """
        pre_test = test_data.get('pre_test_data', {})
        post_test = test_data.get('post_test_data', {})
        exec_data = test_data.get('test_execution_data', {})

        # Calculate power degradation
        pmax_initial = pre_test.get('Pmax_initial', 0)
        pmax_final = post_test.get('Pmax_final', 0)

        power_calc = PowerDegradationCalculator()
        power_degradation = power_calc.calculate_degradation(pmax_initial, pmax_final)

        # Analyze impact data
        impacts = exec_data.get('impacts', [])
        velocity_data = [imp.get('actual_velocity_kmh', 0) for imp in impacts]
        time_compliance = [imp.get('time_delta_seconds', 0) <= 60 for imp in impacts]
        open_circuits = [imp.get('open_circuit_detected', False) for imp in impacts]

        stat_analyzer = StatisticalAnalyzer()
        velocity_stats = stat_analyzer.calculate_statistics(velocity_data)

        # Visual defects analysis
        visual_defects = post_test.get('visual_defects', {})

        # Insulation resistance analysis
        ir_initial = pre_test.get('insulation_resistance_initial', 0)
        ir_final = post_test.get('insulation_resistance_final', 0)
        ir_degradation = ((ir_initial - ir_final) / ir_initial * 100) if ir_initial > 0 else 0

        return {
            'power_analysis': {
                'Pmax_initial': pmax_initial,
                'Pmax_final': pmax_final,
                'degradation_percent': power_degradation,
                'degradation_watts': pmax_initial - pmax_final
            },
            'impact_analysis': {
                'total_impacts': len(impacts),
                'velocity_mean': velocity_stats.get('mean', 0),
                'velocity_std': velocity_stats.get('std', 0),
                'velocity_min': velocity_stats.get('min', 0),
                'velocity_max': velocity_stats.get('max', 0),
                'time_compliance_count': sum(time_compliance),
                'time_compliance_rate': sum(time_compliance) / len(time_compliance) if time_compliance else 0,
                'open_circuit_count': sum(open_circuits),
                'open_circuit_detected': any(open_circuits)
            },
            'visual_analysis': {
                'front_glass_cracks': visual_defects.get('front_glass_cracks', False),
                'cell_cracks': visual_defects.get('cell_cracks', False),
                'backsheet_cracks': visual_defects.get('backsheet_cracks', False),
                'delamination': visual_defects.get('delamination', False),
                'junction_box_damage': visual_defects.get('junction_box_damage', False),
                'frame_damage': visual_defects.get('frame_damage', False)
            },
            'insulation_analysis': {
                'initial_resistance': ir_initial,
                'final_resistance': ir_final,
                'degradation_percent': ir_degradation,
                'meets_minimum': ir_final >= 400  # Typical 400 MΩ minimum
            }
        }

    def evaluate_pass_fail(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pass/fail criteria for HAIL-001

        Args:
            analysis_results: Results from analyze_results()

        Returns:
            Dictionary containing pass/fail evaluation
        """
        criteria_results = {}

        # Power degradation criterion (≤5%)
        power_deg = analysis_results['power_analysis']['degradation_percent']
        criteria_results['power_degradation'] = {
            'pass': power_deg <= 5.0,
            'value': power_deg,
            'threshold': 5.0,
            'unit': '%',
            'description': 'Power degradation ≤5%'
        }

        # Visual inspection criterion
        visual = analysis_results['visual_analysis']
        has_major_defects = (
            visual.get('front_glass_cracks', False) or
            visual.get('backsheet_cracks', False) or
            visual.get('delamination', False)
        )
        criteria_results['visual_inspection'] = {
            'pass': not has_major_defects,
            'value': 'PASS' if not has_major_defects else 'FAIL',
            'description': 'No major visual defects'
        }

        # Insulation resistance criterion (≥400 MΩ typical)
        insulation = analysis_results['insulation_analysis']
        criteria_results['insulation_resistance'] = {
            'pass': insulation['meets_minimum'],
            'value': insulation['final_resistance'],
            'threshold': 400,
            'unit': 'MΩ',
            'description': 'Insulation resistance ≥400 MΩ'
        }

        # Open circuit criterion
        open_circuit = analysis_results['impact_analysis']['open_circuit_detected']
        criteria_results['open_circuit'] = {
            'pass': not open_circuit,
            'value': 'Detected' if open_circuit else 'Not detected',
            'description': 'No intermittent open-circuit during test'
        }

        # Overall pass/fail
        all_pass = all(c['pass'] for c in criteria_results.values())

        return {
            'overall_result': 'PASS' if all_pass else 'FAIL',
            'criteria': criteria_results,
            'summary': self._generate_summary(criteria_results, all_pass)
        }

    def _generate_summary(self, criteria: Dict[str, Any], overall_pass: bool) -> str:
        """
        Generate human-readable summary of test results

        Args:
            criteria: Pass/fail criteria results
            overall_pass: Overall pass/fail status

        Returns:
            Summary string
        """
        summary_lines = [
            f"Test Result: {'PASS' if overall_pass else 'FAIL'}",
            "",
            "Criteria Evaluation:"
        ]

        for criterion_name, criterion_data in criteria.items():
            status = "✓ PASS" if criterion_data['pass'] else "✗ FAIL"
            summary_lines.append(f"  {status}: {criterion_data['description']}")

        return "\n".join(summary_lines)

    def generate_impact_locations(self) -> List[Dict[str, Any]]:
        """
        Generate standard 11 impact locations for module

        Returns:
            List of impact location coordinates (normalized 0-1)
        """
        # Standard impact locations as per IEC 61215
        # Coordinates are normalized (0-1) relative to module dimensions
        return [
            {'id': 1, 'x': 0.5, 'y': 0.5, 'description': 'Center'},
            {'id': 2, 'x': 0.1, 'y': 0.1, 'description': 'Corner - Top Left'},
            {'id': 3, 'x': 0.9, 'y': 0.1, 'description': 'Corner - Top Right'},
            {'id': 4, 'x': 0.1, 'y': 0.9, 'description': 'Corner - Bottom Left'},
            {'id': 5, 'x': 0.9, 'y': 0.9, 'description': 'Corner - Bottom Right'},
            {'id': 6, 'x': 0.5, 'y': 0.1, 'description': 'Edge - Top Center'},
            {'id': 7, 'x': 0.5, 'y': 0.9, 'description': 'Edge - Bottom Center'},
            {'id': 8, 'x': 0.1, 'y': 0.5, 'description': 'Edge - Left Center'},
            {'id': 9, 'x': 0.9, 'y': 0.5, 'description': 'Edge - Right Center'},
            {'id': 10, 'x': 0.25, 'y': 0.25, 'description': 'Quarter - Top Left'},
            {'id': 11, 'x': 0.75, 'y': 0.75, 'description': 'Quarter - Bottom Right'}
        ]
