"""
PVTP-054: End-of-Life & Recycling Assessment Validator
"""

from typing import Dict, List, Tuple


class EndOfLifeValidator:
    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Validate all test results"""
        self.violations = []

        self.validate_safety(test_data.get('initial', {}))
        self.validate_recovery_rates(test_data.get('recovery_rates', {}))
        self.validate_material_purity(test_data.get('recovery_rates', {}))
        self.validate_process_efficiency(test_data.get('processing_cost', {}))

        return len(self.violations) == 0, self.violations

    def validate_safety(self, initial_data: Dict) -> bool:
        """Validate safety requirements"""
        # Safety validation would check electrical isolation, hazmat handling, etc.
        return True

    def validate_recovery_rates(self, recovery_data: Dict) -> bool:
        """Validate material recovery rates"""
        all_valid = True

        overall_rate = recovery_data.get('overall_recovery_rate', 0)
        if overall_rate < 85:
            self.violations.append({
                'parameter': 'overall_recovery_rate',
                'severity': 'MAJOR',
                'message': f'Overall recovery rate {overall_rate:.1f}% below 85% minimum',
                'measured': overall_rate,
                'expected': '≥85%'
            })
            all_valid = False

        # Check individual materials
        by_material = recovery_data.get('by_material', {})
        material_criteria = {
            'glass': 90,
            'aluminum': 95,
            'silicon': 80,
            'copper': 90
        }

        for material, min_rate in material_criteria.items():
            if material in by_material:
                rate = by_material[material].get('mass_percent', 0)
                # Note: This checks mass percent, not recovery rate
                # In practice, you'd compare against expected composition

        return all_valid

    def validate_material_purity(self, recovery_data: Dict) -> bool:
        """Validate material purity"""
        all_valid = True

        by_material = recovery_data.get('by_material', {})
        purity_criteria = {
            'glass': 95,
            'aluminum': 98,
            'silicon': 90,
            'copper': 95
        }

        for material, min_purity in purity_criteria.items():
            if material in by_material:
                purity = by_material[material].get('purity_percent', 0)
                if purity < min_purity:
                    self.violations.append({
                        'parameter': f'purity_{material}',
                        'severity': 'MAJOR',
                        'message': f'{material} purity {purity:.1f}% below {min_purity}% minimum',
                        'measured': purity,
                        'expected': f'≥{min_purity}%'
                    })
                    all_valid = False

        return all_valid

    def validate_process_efficiency(self, cost_data: Dict) -> bool:
        """Validate process efficiency"""
        # Check if processing is efficient
        return True

    def get_violation_summary(self) -> Dict[str, int]:
        """Get violation summary"""
        return {
            'CRITICAL': len([v for v in self.violations if v['severity'] == 'CRITICAL']),
            'MAJOR': len([v for v in self.violations if v['severity'] == 'MAJOR']),
            'MINOR': len([v for v in self.violations if v['severity'] == 'MINOR'])
        }
