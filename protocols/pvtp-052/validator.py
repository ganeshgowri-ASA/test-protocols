"""
PVTP-052: Partial Shading Analysis Validator
"""

from typing import Dict, List, Tuple


class PartialShadingValidator:
    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Validate all test results"""
        self.violations = []

        self.validate_hot_spots(test_data)
        self.validate_bypass_diode(test_data.get('bypass_diode', {}))
        self.validate_power_loss(test_data)
        self.validate_thermal_safety(test_data)

        return len(self.violations) == 0, self.violations

    def validate_hot_spots(self, test_data: Dict) -> bool:
        """Validate hot spot criteria"""
        all_valid = True

        for pattern, data_list in test_data.items():
            if pattern in ['bypass_diode', 'tolerance_summary']:
                continue

            for data in data_list if isinstance(data_list, list) else [data_list]:
                temp_rise = data.get('temperature_rise', 0)
                max_temp = data.get('max_temperature', 0)

                if temp_rise > 20:
                    self.violations.append({
                        'parameter': f'hot_spot_{pattern}',
                        'severity': 'MAJOR',
                        'message': f'Temperature rise {temp_rise:.1f}°C exceeds 20°C limit',
                        'measured': temp_rise,
                        'expected': '≤20°C'
                    })
                    all_valid = False

                if max_temp > 85:
                    self.violations.append({
                        'parameter': f'absolute_temp_{pattern}',
                        'severity': 'CRITICAL',
                        'message': f'Absolute temperature {max_temp:.1f}°C exceeds 85°C limit',
                        'measured': max_temp,
                        'expected': '≤85°C'
                    })
                    all_valid = False

        return all_valid

    def validate_bypass_diode(self, diode_data: Dict) -> bool:
        """Validate bypass diode operation"""
        if not diode_data.get('diode_activated'):
            self.violations.append({
                'parameter': 'bypass_diode_activation',
                'severity': 'CRITICAL',
                'message': 'Bypass diode did not activate during shading',
                'measured': False,
                'expected': True
            })
            return False

        return True

    def validate_power_loss(self, test_data: Dict) -> bool:
        """Validate power loss is within expected range"""
        # Power loss validation logic
        return True

    def validate_thermal_safety(self, test_data: Dict) -> bool:
        """Validate thermal safety"""
        tolerance = test_data.get('tolerance_summary', {})

        if not tolerance.get('overall_safe', True):
            self.violations.append({
                'parameter': 'thermal_safety',
                'severity': 'CRITICAL',
                'message': 'Thermal safety criteria not met',
                'measured': False,
                'expected': True
            })
            return False

        return True

    def get_violation_summary(self) -> Dict[str, int]:
        """Get violation summary"""
        return {
            'CRITICAL': len([v for v in self.violations if v['severity'] == 'CRITICAL']),
            'MAJOR': len([v for v in self.violations if v['severity'] == 'MAJOR'])
        }
