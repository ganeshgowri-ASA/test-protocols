"""
PVTP-051: Reverse Current Overload Test Validator
Validation for reverse current and bypass diode testing
"""

from typing import Dict, List, Tuple


class ReverseCurrentValidator:
    """Validator for reverse current overload testing"""

    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Run all validation checks"""
        self.violations = []

        self.validate_diode_performance(test_data.get('diode_test', {}))
        self.validate_thermal_limits(test_data.get('thermal_analysis', {}))
        self.validate_power_degradation(test_data.get('performance_comparison', {}))
        self.validate_safety_compliance(test_data)

        return len(self.violations) == 0, self.violations

    def validate_diode_performance(self, diode_data: Dict) -> bool:
        """Validate bypass diode performance"""
        all_valid = True

        max_temp = diode_data.get('max_temperature', 0)
        if max_temp > 100:
            self.violations.append({
                'parameter': 'diode_temperature',
                'severity': 'CRITICAL',
                'message': f'Bypass diode temperature {max_temp}°C exceeds 100°C limit',
                'measured': max_temp,
                'expected': '≤100°C'
            })
            all_valid = False

        max_voltage = diode_data.get('max_voltage', 0)
        if max_voltage > 1.0:
            self.violations.append({
                'parameter': 'diode_voltage',
                'severity': 'MAJOR',
                'message': f'Bypass diode voltage {max_voltage}V exceeds 1.0V limit',
                'measured': max_voltage,
                'expected': '≤1.0V'
            })
            all_valid = False

        return all_valid

    def validate_thermal_limits(self, thermal_data: Dict) -> bool:
        """Validate thermal performance"""
        all_valid = True

        if thermal_data.get('hotspots_detected'):
            self.violations.append({
                'parameter': 'thermal_hotspots',
                'severity': 'MAJOR',
                'message': 'Thermal hotspots detected during test',
                'measured': 'Hotspots present',
                'expected': 'No hotspots'
            })
            all_valid = False

        max_temp = thermal_data.get('max_temperature_overall', 0)
        if max_temp > 90:
            self.violations.append({
                'parameter': 'junction_box_temperature',
                'severity': 'CRITICAL',
                'message': f'Junction box temperature {max_temp}°C exceeds 90°C limit',
                'measured': max_temp,
                'expected': '≤90°C'
            })
            all_valid = False

        return all_valid

    def validate_power_degradation(self, performance_data: Dict) -> bool:
        """Validate power degradation is within limits"""
        degradation = performance_data.get('power_degradation_percent', 0)

        if degradation > 2:
            self.violations.append({
                'parameter': 'power_degradation',
                'severity': 'MAJOR',
                'message': f'Power degradation {degradation:.2f}% exceeds 2% limit',
                'measured': degradation,
                'expected': '≤2%'
            })
            return False

        return True

    def validate_safety_compliance(self, test_data: Dict) -> bool:
        """Validate safety compliance"""
        all_valid = True

        # Check for any critical failures
        if any(v['severity'] == 'CRITICAL' for v in self.violations):
            all_valid = False

        return all_valid

    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations"""
        return {
            'CRITICAL': len([v for v in self.violations if v['severity'] == 'CRITICAL']),
            'MAJOR': len([v for v in self.violations if v['severity'] == 'MAJOR']),
            'MINOR': len([v for v in self.violations if v['severity'] == 'MINOR'])
        }
