"""
SOLDER-001: Solder Bond Degradation Testing Validator
Data validation and acceptance criteria checking
"""

from typing import Dict, List, Tuple, Any
import numpy as np


class SolderBondValidator:
    """Validator for solder bond degradation testing"""

    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Run all validation checks"""
        self.violations = []

        # Run validation checks
        self.validate_power_degradation(test_data.get('power_analysis', {}))
        self.validate_resistance_increase(test_data.get('resistance_analysis', {}))
        self.validate_series_resistance(test_data.get('series_resistance', {}))
        self.validate_mechanical_strength(test_data.get('pull_test_results', {}))
        self.validate_visual_inspection(test_data.get('visual_defects', {}))
        self.validate_thermal_imaging(test_data.get('thermal_imaging', {}))
        self.validate_hotspot_criteria(test_data.get('thermal_imaging', {}))

        is_valid = len([v for v in self.violations if v['severity'] == 'CRITICAL']) == 0
        return is_valid, self.violations

    def validate_power_degradation(self, power_data: Dict) -> bool:
        """Validate power degradation is within acceptable limits"""
        all_valid = True

        # After 200 cycles
        power_loss_200 = power_data.get('power_loss_200_cycles', 0)
        if power_loss_200 > 2.0:
            self.violations.append({
                'parameter': 'power_degradation_200_cycles',
                'severity': 'MINOR',
                'message': f'Power degradation {power_loss_200:.2f}% after 200 cycles exceeds 2% limit',
                'measured': power_loss_200,
                'expected': 2.0,
                'unit': '%',
                'checkpoint': 200
            })
            all_valid = False

        # After 600 cycles
        power_loss_600 = power_data.get('power_loss_600_cycles', 0)
        if power_loss_600 > 5.0:
            self.violations.append({
                'parameter': 'power_degradation_600_cycles',
                'severity': 'CRITICAL',
                'message': f'Power degradation {power_loss_600:.2f}% after 600 cycles exceeds 5% limit',
                'measured': power_loss_600,
                'expected': 5.0,
                'unit': '%',
                'checkpoint': 600
            })
            all_valid = False

        return all_valid

    def validate_resistance_increase(self, resistance_data: Dict) -> bool:
        """Validate resistance increase is within acceptable limits"""
        all_valid = True

        # After 200 cycles
        resistance_increase_200 = resistance_data.get('resistance_increase_200_cycles', 0)
        if resistance_increase_200 > 10.0:
            self.violations.append({
                'parameter': 'resistance_increase_200_cycles',
                'severity': 'MINOR',
                'message': f'Resistance increase {resistance_increase_200:.2f}% after 200 cycles exceeds 10% limit',
                'measured': resistance_increase_200,
                'expected': 10.0,
                'unit': '%',
                'checkpoint': 200
            })
            all_valid = False

        # After 600 cycles
        resistance_increase_600 = resistance_data.get('resistance_increase_600_cycles', 0)
        if resistance_increase_600 > 20.0:
            self.violations.append({
                'parameter': 'resistance_increase_600_cycles',
                'severity': 'CRITICAL',
                'message': f'Resistance increase {resistance_increase_600:.2f}% after 600 cycles exceeds 20% limit',
                'measured': resistance_increase_600,
                'expected': 20.0,
                'unit': '%',
                'checkpoint': 600
            })
            all_valid = False

        return all_valid

    def validate_cell_interconnect_resistance(self, resistance_value: float,
                                             baseline: float = None) -> bool:
        """Validate individual cell interconnect resistance"""
        max_initial = 5.0  # mΩ
        max_increase_abs = 2.0  # mΩ
        max_increase_pct = 20.0  # %

        if resistance_value > max_initial:
            self.violations.append({
                'parameter': 'cell_interconnect_resistance',
                'severity': 'MAJOR',
                'message': f'Cell interconnect resistance {resistance_value:.2f} mΩ exceeds {max_initial} mΩ limit',
                'measured': resistance_value,
                'expected': max_initial,
                'unit': 'mΩ'
            })
            return False

        if baseline is not None:
            absolute_increase = resistance_value - baseline
            percentage_increase = (absolute_increase / baseline * 100) if baseline > 0 else 0

            if absolute_increase > max_increase_abs:
                self.violations.append({
                    'parameter': 'cell_interconnect_resistance_increase_abs',
                    'severity': 'MAJOR',
                    'message': f'Cell interconnect resistance increased by {absolute_increase:.2f} mΩ, exceeds {max_increase_abs} mΩ limit',
                    'measured': absolute_increase,
                    'expected': max_increase_abs,
                    'unit': 'mΩ'
                })
                return False

            if percentage_increase > max_increase_pct:
                self.violations.append({
                    'parameter': 'cell_interconnect_resistance_increase_pct',
                    'severity': 'MAJOR',
                    'message': f'Cell interconnect resistance increased by {percentage_increase:.2f}%, exceeds {max_increase_pct}% limit',
                    'measured': percentage_increase,
                    'expected': max_increase_pct,
                    'unit': '%'
                })
                return False

        return True

    def validate_busbar_resistance(self, resistance_value: float,
                                   baseline: float = None) -> bool:
        """Validate busbar resistance"""
        max_initial = 10.0  # mΩ
        max_increase_abs = 3.0  # mΩ
        max_increase_pct = 15.0  # %

        if resistance_value > max_initial:
            self.violations.append({
                'parameter': 'busbar_resistance',
                'severity': 'MAJOR',
                'message': f'Busbar resistance {resistance_value:.2f} mΩ exceeds {max_initial} mΩ limit',
                'measured': resistance_value,
                'expected': max_initial,
                'unit': 'mΩ'
            })
            return False

        if baseline is not None:
            absolute_increase = resistance_value - baseline
            percentage_increase = (absolute_increase / baseline * 100) if baseline > 0 else 0

            if absolute_increase > max_increase_abs:
                self.violations.append({
                    'parameter': 'busbar_resistance_increase_abs',
                    'severity': 'MAJOR',
                    'message': f'Busbar resistance increased by {absolute_increase:.2f} mΩ, exceeds {max_increase_abs} mΩ limit',
                    'measured': absolute_increase,
                    'expected': max_increase_abs,
                    'unit': 'mΩ'
                })
                return False

            if percentage_increase > max_increase_pct:
                self.violations.append({
                    'parameter': 'busbar_resistance_increase_pct',
                    'severity': 'MAJOR',
                    'message': f'Busbar resistance increased by {percentage_increase:.2f}%, exceeds {max_increase_pct}% limit',
                    'measured': percentage_increase,
                    'expected': max_increase_pct,
                    'unit': '%'
                })
                return False

        return True

    def validate_series_resistance(self, series_resistance_data: Dict) -> bool:
        """Validate series resistance from IV curve analysis"""
        all_valid = True

        # Check resistance increase
        resistance_increase = series_resistance_data.get('increase_percentage', 0)
        if resistance_increase > 20.0:
            self.violations.append({
                'parameter': 'series_resistance_increase',
                'severity': 'CRITICAL',
                'message': f'Series resistance increased by {resistance_increase:.2f}%, exceeds 20% limit',
                'measured': resistance_increase,
                'expected': 20.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def validate_mechanical_strength(self, pull_test_data: Dict) -> bool:
        """Validate mechanical pull test results"""
        all_valid = True

        # Fresh sample minimum
        fresh_avg = pull_test_data.get('fresh_mean_force', 0)
        if fresh_avg < 30.0:
            self.violations.append({
                'parameter': 'pull_test_fresh',
                'severity': 'CRITICAL',
                'message': f'Fresh sample pull test force {fresh_avg:.2f} N below 30 N minimum',
                'measured': fresh_avg,
                'expected': 30.0,
                'unit': 'N'
            })
            all_valid = False

        # Aged sample minimum
        aged_avg = pull_test_data.get('aged_mean_force', 0)
        if aged_avg < 24.0:
            self.violations.append({
                'parameter': 'pull_test_aged',
                'severity': 'CRITICAL',
                'message': f'Aged sample pull test force {aged_avg:.2f} N below 24 N minimum',
                'measured': aged_avg,
                'expected': 24.0,
                'unit': 'N'
            })
            all_valid = False

        # Check degradation percentage
        strength_degradation = pull_test_data.get('percentage_loss', 0)
        if strength_degradation > 20.0:
            self.violations.append({
                'parameter': 'pull_test_degradation',
                'severity': 'CRITICAL',
                'message': f'Pull test force degradation {strength_degradation:.2f}% exceeds 20% limit',
                'measured': strength_degradation,
                'expected': 20.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def validate_shear_strength(self, shear_test_data: Dict) -> bool:
        """Validate shear strength test results"""
        all_valid = True

        # Fresh sample minimum
        fresh_avg = shear_test_data.get('fresh_mean_force', 0)
        if fresh_avg < 25.0:
            self.violations.append({
                'parameter': 'shear_test_fresh',
                'severity': 'CRITICAL',
                'message': f'Fresh sample shear test force {fresh_avg:.2f} N below 25 N minimum',
                'measured': fresh_avg,
                'expected': 25.0,
                'unit': 'N'
            })
            all_valid = False

        # Aged sample minimum
        aged_avg = shear_test_data.get('aged_mean_force', 0)
        if aged_avg < 20.0:
            self.violations.append({
                'parameter': 'shear_test_aged',
                'severity': 'CRITICAL',
                'message': f'Aged sample shear test force {aged_avg:.2f} N below 20 N minimum',
                'measured': aged_avg,
                'expected': 20.0,
                'unit': 'N'
            })
            all_valid = False

        # Check degradation percentage
        strength_degradation = shear_test_data.get('percentage_loss', 0)
        if strength_degradation > 20.0:
            self.violations.append({
                'parameter': 'shear_test_degradation',
                'severity': 'CRITICAL',
                'message': f'Shear test force degradation {strength_degradation:.2f}% exceeds 20% limit',
                'measured': strength_degradation,
                'expected': 20.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def validate_visual_inspection(self, visual_data: Dict) -> bool:
        """Validate visual inspection results"""
        all_valid = True

        # Solder cracks
        crack_count = visual_data.get('solder_cracks', 0)
        if crack_count > 0:
            self.violations.append({
                'parameter': 'solder_cracks',
                'severity': 'CRITICAL',
                'message': f'Detected {crack_count} solder crack(s), zero tolerance policy',
                'measured': crack_count,
                'expected': 0,
                'unit': 'count'
            })
            all_valid = False

        # Ribbon detachment
        detachment_count = visual_data.get('ribbon_detachment', 0)
        if detachment_count > 0:
            self.violations.append({
                'parameter': 'ribbon_detachment',
                'severity': 'CRITICAL',
                'message': f'Detected {detachment_count} ribbon detachment(s), zero tolerance policy',
                'measured': detachment_count,
                'expected': 0,
                'unit': 'count'
            })
            all_valid = False

        # Delamination
        delamination_pct = visual_data.get('delamination_percentage', 0)
        if delamination_pct > 0:
            self.violations.append({
                'parameter': 'delamination',
                'severity': 'CRITICAL',
                'message': f'Delamination detected at {delamination_pct:.2f}%, zero tolerance policy',
                'measured': delamination_pct,
                'expected': 0,
                'unit': '%'
            })
            all_valid = False

        # Minor discoloration
        discoloration_pct = visual_data.get('discoloration_percentage', 0)
        if discoloration_pct > 10.0:
            self.violations.append({
                'parameter': 'discoloration',
                'severity': 'MINOR',
                'message': f'Discoloration at {discoloration_pct:.2f}% exceeds 10% limit',
                'measured': discoloration_pct,
                'expected': 10.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def validate_thermal_imaging(self, thermal_data: Dict) -> bool:
        """Validate thermal imaging results"""
        all_valid = True

        max_delta_t = thermal_data.get('max_delta_t', 0)
        if max_delta_t > 15.0:
            self.violations.append({
                'parameter': 'hotspot_temperature',
                'severity': 'MAJOR',
                'message': f'Maximum temperature delta {max_delta_t:.2f}°C exceeds 15°C limit',
                'measured': max_delta_t,
                'expected': 15.0,
                'unit': '°C'
            })
            all_valid = False

        return all_valid

    def validate_hotspot_criteria(self, thermal_data: Dict) -> bool:
        """Validate hotspot development over time"""
        all_valid = True

        hotspot_count = thermal_data.get('hotspot_count', 0)
        new_hotspots = thermal_data.get('new_hotspots', 0)

        if new_hotspots > 5:
            self.violations.append({
                'parameter': 'new_hotspots',
                'severity': 'MAJOR',
                'message': f'{new_hotspots} new hotspots detected during testing, indicates degradation',
                'measured': new_hotspots,
                'expected': 5,
                'unit': 'count'
            })
            all_valid = False

        return all_valid

    def validate_checkpoint_compliance(self, checkpoint_data: Dict,
                                      checkpoint_number: int) -> bool:
        """Validate data at specific checkpoint"""
        all_valid = True

        # Get criteria for this checkpoint
        if checkpoint_number == 200:
            max_power_loss = 2.0
            max_resistance_increase = 10.0
        elif checkpoint_number == 600:
            max_power_loss = 5.0
            max_resistance_increase = 20.0
        else:
            # Interpolate or use conservative limits
            max_power_loss = 5.0
            max_resistance_increase = 20.0

        power_loss = checkpoint_data.get('power_loss_pct', 0)
        if power_loss > max_power_loss:
            severity = 'CRITICAL' if checkpoint_number >= 600 else 'MINOR'
            self.violations.append({
                'parameter': f'checkpoint_{checkpoint_number}_power_loss',
                'severity': severity,
                'message': f'Checkpoint {checkpoint_number}: Power loss {power_loss:.2f}% exceeds {max_power_loss}% limit',
                'measured': power_loss,
                'expected': max_power_loss,
                'unit': '%',
                'checkpoint': checkpoint_number
            })
            all_valid = False

        resistance_increase = checkpoint_data.get('resistance_increase_pct', 0)
        if resistance_increase > max_resistance_increase:
            severity = 'CRITICAL' if checkpoint_number >= 600 else 'MINOR'
            self.violations.append({
                'parameter': f'checkpoint_{checkpoint_number}_resistance',
                'severity': severity,
                'message': f'Checkpoint {checkpoint_number}: Resistance increase {resistance_increase:.2f}% exceeds {max_resistance_increase}% limit',
                'measured': resistance_increase,
                'expected': max_resistance_increase,
                'unit': '%',
                'checkpoint': checkpoint_number
            })
            all_valid = False

        return all_valid

    def validate_lifetime_prediction(self, lifetime_data: Dict) -> bool:
        """Validate predicted lifetime meets requirements"""
        all_valid = True

        predicted_lifetime = lifetime_data.get('predicted_lifetime_years', 0)
        if predicted_lifetime < 25.0:
            self.violations.append({
                'parameter': 'predicted_lifetime',
                'severity': 'CRITICAL',
                'message': f'Predicted lifetime {predicted_lifetime:.1f} years below 25-year requirement',
                'measured': predicted_lifetime,
                'expected': 25.0,
                'unit': 'years'
            })
            all_valid = False

        # Check 25-year projection
        year_25_projection = lifetime_data.get('year_25_projection', {})
        resistance_at_25yr = year_25_projection.get('resistance_increase_pct', 0)
        power_loss_at_25yr = year_25_projection.get('power_loss_pct', 0)

        if resistance_at_25yr > 20.0:
            self.violations.append({
                'parameter': 'year_25_resistance_projection',
                'severity': 'CRITICAL',
                'message': f'Projected resistance increase at year 25: {resistance_at_25yr:.2f}% exceeds 20% limit',
                'measured': resistance_at_25yr,
                'expected': 20.0,
                'unit': '%'
            })
            all_valid = False

        if power_loss_at_25yr > 20.0:
            self.violations.append({
                'parameter': 'year_25_power_projection',
                'severity': 'CRITICAL',
                'message': f'Projected power loss at year 25: {power_loss_at_25yr:.2f}% exceeds 20% limit',
                'measured': power_loss_at_25yr,
                'expected': 20.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def validate_measurement_quality(self, measurement_data: Dict) -> bool:
        """Validate measurement quality and repeatability"""
        all_valid = True

        # Coefficient of variation for resistance measurements
        resistance_cv = measurement_data.get('resistance_cv_percent', 0)
        if resistance_cv > 5.0:
            self.violations.append({
                'parameter': 'resistance_measurement_cv',
                'severity': 'MAJOR',
                'message': f'Resistance measurement CV {resistance_cv:.2f}% exceeds 5% limit (poor repeatability)',
                'measured': resistance_cv,
                'expected': 5.0,
                'unit': '%'
            })
            all_valid = False

        # Power measurement difference
        power_difference = measurement_data.get('power_measurement_difference_pct', 0)
        if power_difference > 1.0:
            self.violations.append({
                'parameter': 'power_measurement_difference',
                'severity': 'MAJOR',
                'message': f'Power measurement difference {power_difference:.2f}% exceeds 1% limit',
                'measured': power_difference,
                'expected': 1.0,
                'unit': '%'
            })
            all_valid = False

        return all_valid

    def get_violations_by_severity(self, severity: str) -> List[Dict]:
        """Get violations filtered by severity"""
        return [v for v in self.violations if v['severity'] == severity]

    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by severity"""
        return {
            'CRITICAL': len(self.get_violations_by_severity('CRITICAL')),
            'MAJOR': len(self.get_violations_by_severity('MAJOR')),
            'MINOR': len(self.get_violations_by_severity('MINOR')),
            'TOTAL': len(self.violations)
        }

    def get_violations_by_checkpoint(self, checkpoint: int) -> List[Dict]:
        """Get violations for a specific checkpoint"""
        return [v for v in self.violations if v.get('checkpoint') == checkpoint]

    def passes_acceptance_criteria(self) -> bool:
        """Determine if overall test passes acceptance criteria"""
        # No critical violations allowed
        critical_count = len(self.get_violations_by_severity('CRITICAL'))

        # Maximum 3 major violations allowed
        major_count = len(self.get_violations_by_severity('MAJOR'))

        return critical_count == 0 and major_count <= 3

    def get_overall_status(self) -> str:
        """Get overall test status"""
        critical_count = len(self.get_violations_by_severity('CRITICAL'))
        major_count = len(self.get_violations_by_severity('MAJOR'))
        minor_count = len(self.get_violations_by_severity('MINOR'))

        if critical_count > 0:
            return 'FAIL'
        elif major_count > 3:
            return 'FAIL'
        elif major_count > 0 or minor_count > 0:
            return 'MARGINAL'
        else:
            return 'PASS'

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report summary"""
        return {
            'overall_status': self.get_overall_status(),
            'passes_criteria': self.passes_acceptance_criteria(),
            'violation_summary': self.get_violation_summary(),
            'critical_violations': self.get_violations_by_severity('CRITICAL'),
            'major_violations': self.get_violations_by_severity('MAJOR'),
            'minor_violations': self.get_violations_by_severity('MINOR'),
            'total_violations': len(self.violations)
        }
