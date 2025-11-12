"""
PVTP-048: Energy Rating & Bankability Assessment Validator
Data validation and acceptance criteria checking
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd


class EnergyRatingValidator:
    """Validator for energy rating and bankability assessment"""

    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Run all validation checks"""
        self.violations = []

        # Run validation checks
        self.validate_pmax_tolerance(test_data.get('pmax_measured'),
                                     test_data.get('pmax_nameplate'))
        self.validate_low_light_performance(test_data.get('low_light_data', {}))
        self.validate_temperature_coefficients(test_data.get('temp_coefficients', {}))
        self.validate_bankability_factors(test_data.get('manufacturer_data', {}))
        self.validate_certifications(test_data.get('certifications', []))
        self.validate_warranty_terms(test_data.get('warranty', {}))

        is_valid = len(self.violations) == 0
        return is_valid, self.violations

    def validate_pmax_tolerance(self, measured: float, nameplate: float) -> bool:
        """Validate Pmax is within tolerance of nameplate"""
        if measured is None or nameplate is None:
            self.violations.append({
                'parameter': 'pmax',
                'severity': 'CRITICAL',
                'message': 'Missing Pmax measurement or nameplate value',
                'measured': measured,
                'expected': nameplate
            })
            return False

        tolerance = 0.03  # 3%
        deviation = abs(measured - nameplate) / nameplate

        if deviation > tolerance:
            self.violations.append({
                'parameter': 'pmax',
                'severity': 'MAJOR',
                'message': f'Pmax deviation {deviation*100:.2f}% exceeds ±{tolerance*100}%',
                'measured': measured,
                'expected': nameplate,
                'tolerance': tolerance * 100
            })
            return False

        return True

    def validate_low_light_performance(self, low_light_data: Dict) -> bool:
        """Validate low light performance meets criteria"""
        all_valid = True

        # Check 200 W/m² performance
        perf_200 = low_light_data.get('performance_200w', 0)
        if perf_200 < 0.90:
            self.violations.append({
                'parameter': 'low_light_200w',
                'severity': 'MAJOR',
                'message': f'200 W/m² performance {perf_200:.2%} below 90% threshold',
                'measured': perf_200,
                'expected': 0.90
            })
            all_valid = False

        # Check 400 W/m² performance
        perf_400 = low_light_data.get('performance_400w', 0)
        if perf_400 < 0.95:
            self.violations.append({
                'parameter': 'low_light_400w',
                'severity': 'MINOR',
                'message': f'400 W/m² performance {perf_400:.2%} below 95% threshold',
                'measured': perf_400,
                'expected': 0.95
            })
            all_valid = False

        return all_valid

    def validate_temperature_coefficients(self, temp_coefs: Dict) -> bool:
        """Validate temperature coefficients are within acceptable range"""
        all_valid = True

        # Pmax temperature coefficient
        pmax_coef = abs(temp_coefs.get('pmax', 0))
        if pmax_coef > 0.5:
            self.violations.append({
                'parameter': 'temp_coef_pmax',
                'severity': 'MAJOR',
                'message': f'Pmax temp coefficient {pmax_coef:.3f}%/°C exceeds -0.5%/°C limit',
                'measured': -pmax_coef,
                'expected': -0.5,
                'unit': '%/°C'
            })
            all_valid = False

        # Voc temperature coefficient
        voc_coef = abs(temp_coefs.get('voc', 0))
        if voc_coef > 0.35:
            self.violations.append({
                'parameter': 'temp_coef_voc',
                'severity': 'MINOR',
                'message': f'Voc temp coefficient {voc_coef:.3f}%/°C exceeds -0.35%/°C limit',
                'measured': -voc_coef,
                'expected': -0.35,
                'unit': '%/°C'
            })
            all_valid = False

        # Isc temperature coefficient
        isc_coef = temp_coefs.get('isc', 0)
        if isc_coef > 0.1:
            self.violations.append({
                'parameter': 'temp_coef_isc',
                'severity': 'MINOR',
                'message': f'Isc temp coefficient {isc_coef:.3f}%/°C exceeds +0.1%/°C limit',
                'measured': isc_coef,
                'expected': 0.1,
                'unit': '%/°C'
            })
            all_valid = False

        return all_valid

    def validate_bankability_factors(self, manufacturer_data: Dict) -> bool:
        """Validate manufacturer bankability factors"""
        all_valid = True

        # Manufacturer tier
        tier = manufacturer_data.get('tier', 0)
        if tier != 1:
            self.violations.append({
                'parameter': 'manufacturer_tier',
                'severity': 'CRITICAL',
                'message': f'Manufacturer tier {tier} does not meet Tier 1 requirement',
                'measured': tier,
                'expected': 1
            })
            all_valid = False

        # Years of operation
        years_op = manufacturer_data.get('years_operation', 0)
        if years_op < 5:
            self.violations.append({
                'parameter': 'years_operation',
                'severity': 'MAJOR',
                'message': f'Years of operation {years_op} below 5-year minimum',
                'measured': years_op,
                'expected': 5
            })
            all_valid = False

        # Production capacity
        capacity = manufacturer_data.get('production_capacity_gw', 0)
        if capacity < 1.0:
            self.violations.append({
                'parameter': 'production_capacity',
                'severity': 'MAJOR',
                'message': f'Production capacity {capacity} GW below 1 GW minimum',
                'measured': capacity,
                'expected': 1.0,
                'unit': 'GW/year'
            })
            all_valid = False

        return all_valid

    def validate_certifications(self, certifications: List[str]) -> bool:
        """Validate required certifications are present"""
        required = ['IEC 61215', 'IEC 61730']
        recommended = ['IEC 62804', 'UL 1703']

        missing_required = [cert for cert in required if cert not in certifications]
        missing_recommended = [cert for cert in recommended if cert not in certifications]

        if missing_required:
            self.violations.append({
                'parameter': 'certifications',
                'severity': 'CRITICAL',
                'message': f'Missing required certifications: {", ".join(missing_required)}',
                'measured': certifications,
                'expected': required
            })
            return False

        if missing_recommended:
            self.violations.append({
                'parameter': 'certifications',
                'severity': 'MINOR',
                'message': f'Missing recommended certifications: {", ".join(missing_recommended)}',
                'measured': certifications,
                'expected': required + recommended
            })

        return True

    def validate_warranty_terms(self, warranty: Dict) -> bool:
        """Validate warranty terms meet bankability requirements"""
        all_valid = True

        # Product warranty
        product_years = warranty.get('product_warranty_years', 0)
        if product_years < 12:
            self.violations.append({
                'parameter': 'product_warranty',
                'severity': 'MAJOR',
                'message': f'Product warranty {product_years} years below 12-year minimum',
                'measured': product_years,
                'expected': 12,
                'unit': 'years'
            })
            all_valid = False

        # Performance warranty
        performance_years = warranty.get('performance_warranty_years', 0)
        if performance_years < 25:
            self.violations.append({
                'parameter': 'performance_warranty',
                'severity': 'MAJOR',
                'message': f'Performance warranty {performance_years} years below 25-year minimum',
                'measured': performance_years,
                'expected': 25,
                'unit': 'years'
            })
            all_valid = False

        # Degradation rate guarantee
        degradation = warranty.get('linear_degradation_percent', 1.0)
        if degradation > 0.55:
            self.violations.append({
                'parameter': 'warranty_degradation',
                'severity': 'MAJOR',
                'message': f'Warranted degradation {degradation}%/year exceeds 0.55%/year',
                'measured': degradation,
                'expected': 0.55,
                'unit': '%/year'
            })
            all_valid = False

        return all_valid

    def validate_performance_ratio(self, pr_year1: float, pr_year25: float) -> bool:
        """Validate performance ratio projections"""
        all_valid = True

        if pr_year1 < 0.84:
            self.violations.append({
                'parameter': 'performance_ratio_year1',
                'severity': 'MAJOR',
                'message': f'Year 1 PR {pr_year1:.3f} below 0.84 minimum',
                'measured': pr_year1,
                'expected': 0.84
            })
            all_valid = False

        if pr_year25 < 0.80:
            self.violations.append({
                'parameter': 'performance_ratio_year25',
                'severity': 'MAJOR',
                'message': f'Year 25 PR {pr_year25:.3f} below 0.80 minimum',
                'measured': pr_year25,
                'expected': 0.80
            })
            all_valid = False

        return all_valid

    def validate_measurement_uncertainty(self, uncertainties: Dict) -> bool:
        """Validate measurement uncertainties are acceptable"""
        max_uncertainties = {
            'power': 0.02,
            'voltage': 0.005,
            'current': 0.01,
            'temperature': 0.5,
            'irradiance': 0.02
        }

        all_valid = True

        for param, max_unc in max_uncertainties.items():
            measured_unc = uncertainties.get(param, float('inf'))
            if measured_unc > max_unc:
                self.violations.append({
                    'parameter': f'uncertainty_{param}',
                    'severity': 'MAJOR',
                    'message': f'{param} uncertainty {measured_unc:.3f} exceeds {max_unc:.3f}',
                    'measured': measured_unc,
                    'expected': max_unc
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
            'MINOR': len(self.get_violations_by_severity('MINOR'))
        }

    def is_bankable(self) -> bool:
        """Determine if module meets bankability requirements"""
        critical = len(self.get_violations_by_severity('CRITICAL'))
        major = len(self.get_violations_by_severity('MAJOR'))

        # No critical violations, max 2 major violations
        return critical == 0 and major <= 2
