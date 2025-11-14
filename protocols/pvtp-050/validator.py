"""
PVTP-050: Comparative Module Testing Validator
Data validation for multi-manufacturer comparison testing
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd


class ComparativeTestingValidator:
    """Validator for comparative module testing"""

    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []
        self.warnings = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Run all validation checks"""
        self.violations = []
        self.warnings = []

        self.validate_sample_requirements(test_data.get('sample_info', {}))
        self.validate_test_conditions(test_data.get('conditions', {}))
        self.validate_measurement_quality(test_data.get('measurements', {}))
        self.validate_statistical_requirements(test_data.get('statistics', {}))
        self.validate_data_completeness(test_data)

        is_valid = len(self.violations) == 0
        return is_valid, self.violations

    def validate_sample_requirements(self, sample_info: Dict) -> bool:
        """Validate sample size and selection"""
        all_valid = True

        manufacturers = sample_info.get('manufacturers', {})
        num_manufacturers = len(manufacturers)

        if num_manufacturers < 3:
            self.violations.append({
                'parameter': 'manufacturer_count',
                'severity': 'CRITICAL',
                'message': 'Minimum 3 manufacturers required for meaningful comparison',
                'measured': num_manufacturers,
                'expected': '>=3'
            })
            all_valid = False

        for mfr_id, mfr_data in manufacturers.items():
            module_count = mfr_data.get('module_count', 0)
            if module_count < 6:
                self.violations.append({
                    'parameter': f'sample_size_{mfr_id}',
                    'severity': 'MAJOR',
                    'message': f'Insufficient modules for {mfr_data.get("name", mfr_id)}',
                    'measured': module_count,
                    'expected': 6
                })
                all_valid = False

        return all_valid

    def validate_test_conditions(self, conditions: Dict) -> bool:
        """Validate test conditions consistency"""
        all_valid = True

        required_params = ['temperature', 'irradiance', 'humidity']

        for param in required_params:
            if param not in conditions:
                self.violations.append({
                    'parameter': f'test_condition_{param}',
                    'severity': 'CRITICAL',
                    'message': f'Missing test condition: {param}',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        temp = conditions.get('temperature', {})
        if temp:
            temp_mean = temp.get('mean', 0)
            temp_range = temp.get('range', [0, 0])

            if abs(temp_mean - 25) > 2:
                self.warnings.append({
                    'parameter': 'test_temperature',
                    'severity': 'WARNING',
                    'message': f'Test temperature deviation from 25°C STC',
                    'measured': temp_mean,
                    'expected': '25±2°C'
                })

            if (max(temp_range) - min(temp_range)) > 4:
                self.violations.append({
                    'parameter': 'temperature_stability',
                    'severity': 'MAJOR',
                    'message': 'Excessive temperature variation during testing',
                    'measured': max(temp_range) - min(temp_range),
                    'expected': '≤4°C'
                })
                all_valid = False

        return all_valid

    def validate_measurement_quality(self, measurements: Dict) -> bool:
        """Validate measurement quality and repeatability"""
        all_valid = True

        repeatability = measurements.get('repeatability', {})

        criteria_limits = {
            'pmax': 0.01,
            'voc': 0.005,
            'isc': 0.01
        }

        for param, limit in criteria_limits.items():
            if param in repeatability:
                value = repeatability[param]
                if value > limit:
                    self.violations.append({
                        'parameter': f'repeatability_{param}',
                        'severity': 'MAJOR',
                        'message': f'{param} repeatability exceeds ±{limit*100}%',
                        'measured': value,
                        'expected': limit
                    })
                    all_valid = False

        return all_valid

    def validate_statistical_requirements(self, statistics: Dict) -> bool:
        """Validate statistical analysis requirements"""
        all_valid = True

        for mfr_id, stats in statistics.items():
            cv = stats.get('coefficient_of_variation', 0)
            if cv > 3.0:
                self.warnings.append({
                    'parameter': f'cv_{mfr_id}',
                    'severity': 'WARNING',
                    'message': f'High coefficient of variation for {mfr_id}',
                    'measured': cv,
                    'expected': '≤3%'
                })

        return all_valid

    def validate_data_completeness(self, test_data: Dict) -> bool:
        """Validate all required data is present"""
        all_valid = True

        required_sections = ['sample_info', 'measurements', 'statistics']

        for section in required_sections:
            if section not in test_data or not test_data[section]:
                self.violations.append({
                    'parameter': f'data_section_{section}',
                    'severity': 'CRITICAL',
                    'message': f'Required data section missing: {section}',
                    'measured': None,
                    'expected': 'Required'
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
            'WARNINGS': len(self.warnings)
        }

    def is_comparison_valid(self) -> bool:
        """Determine if comparison is valid"""
        critical = len(self.get_violations_by_severity('CRITICAL'))
        major = len(self.get_violations_by_severity('MAJOR'))
        return critical == 0 and major <= 1
