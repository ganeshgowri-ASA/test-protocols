"""
PVTP-053: Module Cleaning Efficiency Validator
"""

from typing import Dict, List, Tuple


class CleaningEfficiencyValidator:
    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Validate all test results"""
        self.violations = []

        self.validate_cleaning_effectiveness(test_data)
        self.validate_recovery_rates(test_data)
        self.validate_resource_usage(test_data)

        return len(self.violations) == 0, self.violations

    def validate_cleaning_effectiveness(self, test_data: Dict) -> bool:
        """Validate cleaning method effectiveness"""
        all_valid = True

        for method, data_list in test_data.items():
            if method in ['soiling_analysis', 'method_comparison']:
                continue

            for data in data_list if isinstance(data_list, list) else [data_list]:
                recovery = data.get('recovery_rate_percent', 0)
                min_recovery = 95 if 'water' in method else 90

                if recovery < min_recovery:
                    self.violations.append({
                        'parameter': f'recovery_{method}',
                        'severity': 'MAJOR',
                        'message': f'Recovery rate {recovery:.1f}% below {min_recovery}% minimum',
                        'measured': recovery,
                        'expected': f'>={min_recovery}%'
                    })
                    all_valid = False

        return all_valid

    def validate_recovery_rates(self, test_data: Dict) -> bool:
        """Validate recovery rates meet criteria"""
        return True  # Covered in cleaning effectiveness

    def validate_resource_usage(self, test_data: Dict) -> bool:
        """Validate resource usage is reasonable"""
        all_valid = True

        for method, data_list in test_data.items():
            if method in ['soiling_analysis', 'method_comparison']:
                continue

            for data in data_list if isinstance(data_list, list) else [data_list]:
                water = data.get('water_usage_liters', 0)
                time = data.get('time_minutes', 0)

                if water > 50:  # Example limit
                    self.violations.append({
                        'parameter': f'water_usage_{method}',
                        'severity': 'MINOR',
                        'message': f'Excessive water usage: {water}L',
                        'measured': water,
                        'expected': '≤50L'
                    })

                if time > 30:
                    self.violations.append({
                        'parameter': f'time_{method}',
                        'severity': 'MINOR',
                        'message': f'Excessive cleaning time: {time} minutes',
                        'measured': time,
                        'expected': '≤30 minutes'
                    })

        return all_valid

    def get_violation_summary(self) -> Dict[str, int]:
        """Get violation summary"""
        return {
            'CRITICAL': len([v for v in self.violations if v['severity'] == 'CRITICAL']),
            'MAJOR': len([v for v in self.violations if v['severity'] == 'MAJOR']),
            'MINOR': len([v for v in self.violations if v['severity'] == 'MINOR'])
        }
