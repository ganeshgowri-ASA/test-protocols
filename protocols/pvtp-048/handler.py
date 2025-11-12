"""
PVTP-048: Energy Rating & Bankability Assessment Handler
Data processing and analysis for energy rating and bankability evaluation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime
import json


class EnergyRatingHandler:
    """Handler for energy rating and bankability assessment"""

    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}

    def process_flash_test(self, iv_data: pd.DataFrame) -> Dict[str, float]:
        """Process initial flash test data at STC"""
        pmax = iv_data['power'].max()
        voc = iv_data['voltage'].max()
        isc = iv_data['current'].max()

        # Find MPP
        mpp_idx = iv_data['power'].idxmax()
        vmpp = iv_data.loc[mpp_idx, 'voltage']
        impp = iv_data.loc[mpp_idx, 'current']

        # Calculate fill factor
        ff = (vmpp * impp) / (voc * isc)

        return {
            'pmax': pmax,
            'voc': voc,
            'isc': isc,
            'vmpp': vmpp,
            'impp': impp,
            'fill_factor': ff,
            'timestamp': datetime.now().isoformat()
        }

    def analyze_low_irradiance(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Analyze low irradiance performance"""
        results = {}

        for measurement in measurements:
            irradiance = measurement['irradiance']
            power = measurement['power']

            # Normalize to STC equivalent
            stc_power = self.results.get('stc_power', 1)
            normalized = (power / irradiance) * 1000 / stc_power

            results[f'performance_{irradiance}w'] = {
                'absolute_power': power,
                'normalized': normalized,
                'efficiency_ratio': normalized
            }

        return results

    def calculate_temperature_coefficients(self, temp_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate temperature coefficients from measurement data"""
        # Group by temperature
        temps = temp_data['temperature'].unique()

        pmax_values = []
        voc_values = []
        isc_values = []

        for temp in sorted(temps):
            temp_subset = temp_data[temp_data['temperature'] == temp]
            pmax_values.append(temp_subset['power'].max())
            voc_values.append(temp_subset['voltage'].max())
            isc_values.append(temp_subset['current'].max())

        # Linear regression for coefficients
        pmax_coef = np.polyfit(temps, pmax_values, 1)[0] / pmax_values[0] * 100
        voc_coef = np.polyfit(temps, voc_values, 1)[0] / voc_values[0] * 100
        isc_coef = np.polyfit(temps, isc_values, 1)[0] / isc_values[0] * 100

        return {
            'pmax_temp_coef': pmax_coef,
            'voc_temp_coef': voc_coef,
            'isc_temp_coef': isc_coef,
            'reference_temp': 25.0,
            'temp_range': [temps.min(), temps.max()]
        }

    def build_energy_matrix(self, matrix_data: pd.DataFrame) -> np.ndarray:
        """Build IEC 61853-1 energy matrix"""
        # Standard matrix: 6 irradiance x 6 temperature points
        irradiance_bins = [100, 200, 400, 600, 800, 1000]
        temp_bins = [15, 25, 35, 50, 65, 75]

        matrix = np.zeros((len(temp_bins), len(irradiance_bins)))

        for i, temp in enumerate(temp_bins):
            for j, irr in enumerate(irradiance_bins):
                # Find nearest measurement
                subset = matrix_data[
                    (abs(matrix_data['temperature'] - temp) < 2) &
                    (abs(matrix_data['irradiance'] - irr) < 50)
                ]
                if not subset.empty:
                    matrix[i, j] = subset['power'].max()

        return matrix

    def model_energy_yield(self, energy_matrix: np.ndarray,
                          climate_data: pd.DataFrame) -> Dict[str, float]:
        """Model annual energy yield for different climate zones"""
        results = {}

        climate_zones = climate_data['zone'].unique()

        for zone in climate_zones:
            zone_data = climate_data[climate_data['zone'] == zone]

            # Weight matrix by typical conditions
            total_energy = 0
            for _, row in zone_data.iterrows():
                temp_idx = self._find_nearest_index([15, 25, 35, 50, 65, 75], row['avg_temp'])
                irr_idx = self._find_nearest_index([100, 200, 400, 600, 800, 1000], row['avg_irradiance'])

                power = energy_matrix[temp_idx, irr_idx]
                hours = row['hours_per_year']

                total_energy += power * hours / 1000  # kWh

            results[zone] = {
                'annual_energy_kwh': total_energy,
                'specific_yield_kwh_kwp': total_energy / (energy_matrix[1, 5] / 1000)
            }

        return results

    def project_degradation(self, initial_power: float,
                           degradation_rate: float = 0.5,
                           years: int = 25) -> pd.DataFrame:
        """Project power degradation over lifetime"""
        # Year 1 LID (typically 2%)
        lid = 0.02
        year1_power = initial_power * (1 - lid)

        # Linear degradation years 2-25
        timeline = []
        for year in range(0, years + 1):
            if year == 0:
                power = initial_power
            elif year == 1:
                power = year1_power
            else:
                power = year1_power * (1 - (degradation_rate / 100) * (year - 1))

            timeline.append({
                'year': year,
                'power_w': power,
                'power_percent': (power / initial_power) * 100
            })

        return pd.DataFrame(timeline)

    def calculate_performance_ratio(self, actual_energy: float,
                                   theoretical_energy: float) -> float:
        """Calculate performance ratio"""
        return actual_energy / theoretical_energy if theoretical_energy > 0 else 0

    def assess_bankability(self, module_data: Dict,
                          manufacturer_data: Dict) -> Dict[str, Any]:
        """Comprehensive bankability assessment"""
        score = 0
        max_score = 100
        factors = {}

        # Tier 1 manufacturer (20 points)
        if manufacturer_data.get('tier') == 1:
            score += 20
            factors['tier_status'] = {'score': 20, 'max': 20, 'status': 'PASS'}
        else:
            factors['tier_status'] = {'score': 0, 'max': 20, 'status': 'FAIL'}

        # Certifications (15 points)
        required_certs = ['IEC 61215', 'IEC 61730', 'IEC 62804']
        cert_score = 0
        for cert in required_certs:
            if cert in manufacturer_data.get('certifications', []):
                cert_score += 5
        score += cert_score
        factors['certifications'] = {'score': cert_score, 'max': 15,
                                     'status': 'PASS' if cert_score >= 15 else 'PARTIAL'}

        # Warranty terms (15 points)
        warranty_score = 0
        if manufacturer_data.get('product_warranty_years', 0) >= 12:
            warranty_score += 7
        if manufacturer_data.get('performance_warranty_years', 0) >= 25:
            warranty_score += 8
        score += warranty_score
        factors['warranty'] = {'score': warranty_score, 'max': 15,
                              'status': 'PASS' if warranty_score >= 15 else 'PARTIAL'}

        # Performance metrics (25 points)
        perf_score = 0
        if module_data.get('pmax_tolerance', 0) <= 3:
            perf_score += 8
        if module_data.get('low_light_200w', 0) >= 0.90:
            perf_score += 9
        if abs(module_data.get('temp_coef_pmax', 0)) <= 0.40:
            perf_score += 8
        score += perf_score
        factors['performance'] = {'score': perf_score, 'max': 25,
                                 'status': 'PASS' if perf_score >= 20 else 'PARTIAL'}

        # Financial stability (15 points)
        financial_score = 0
        if manufacturer_data.get('years_operation', 0) >= 5:
            financial_score += 7
        if manufacturer_data.get('production_capacity_gw', 0) >= 1:
            financial_score += 8
        score += financial_score
        factors['financial_stability'] = {'score': financial_score, 'max': 15,
                                          'status': 'PASS' if financial_score >= 12 else 'PARTIAL'}

        # Degradation rate (10 points)
        deg_score = 0
        if module_data.get('degradation_rate', 1.0) <= 0.55:
            deg_score = 10
        elif module_data.get('degradation_rate', 1.0) <= 0.70:
            deg_score = 6
        score += deg_score
        factors['degradation'] = {'score': deg_score, 'max': 10,
                                 'status': 'PASS' if deg_score >= 8 else 'PARTIAL'}

        # Overall assessment
        percentage = (score / max_score) * 100

        if percentage >= 85:
            rating = 'A+ (Highly Bankable)'
        elif percentage >= 75:
            rating = 'A (Bankable)'
        elif percentage >= 65:
            rating = 'B+ (Moderately Bankable)'
        elif percentage >= 55:
            rating = 'B (Marginally Bankable)'
        else:
            rating = 'C (Not Recommended)'

        return {
            'total_score': score,
            'max_score': max_score,
            'percentage': percentage,
            'rating': rating,
            'factors': factors,
            'recommendation': self._generate_recommendation(rating, factors)
        }

    def calculate_lcoe(self, capex: float, opex_annual: float,
                      energy_annual: float, degradation_rate: float,
                      discount_rate: float = 0.05, years: int = 25) -> float:
        """Calculate Levelized Cost of Energy"""
        total_cost = capex
        total_energy = 0

        for year in range(1, years + 1):
            # Discounted OPEX
            opex_discounted = opex_annual / ((1 + discount_rate) ** year)
            total_cost += opex_discounted

            # Degraded energy production
            if year == 1:
                energy = energy_annual * 0.98  # LID
            else:
                energy = energy_annual * 0.98 * (1 - (degradation_rate / 100) * (year - 1))

            # Discounted energy
            energy_discounted = energy / ((1 + discount_rate) ** year)
            total_energy += energy_discounted

        return total_cost / total_energy if total_energy > 0 else float('inf')

    def _find_nearest_index(self, array: List, value: float) -> int:
        """Find nearest index in array"""
        return min(range(len(array)), key=lambda i: abs(array[i] - value))

    def _generate_recommendation(self, rating: str, factors: Dict) -> str:
        """Generate bankability recommendation"""
        if 'A+' in rating or 'A' in rating:
            return "Module recommended for financing. All key criteria met."
        elif 'B+' in rating:
            return "Module acceptable with additional due diligence. Review partial factors."
        elif 'B' in rating:
            return "Module marginally acceptable. Enhanced warranties or guarantees recommended."
        else:
            return "Module not recommended for financing without significant risk mitigation."

    def generate_report_data(self) -> Dict[str, Any]:
        """Compile all data for report generation"""
        return {
            'protocol_id': 'PVTP-048',
            'test_date': datetime.now().isoformat(),
            'results': self.results,
            'summary': self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            'pass_fail': self._determine_overall_status(),
            'key_findings': self._extract_key_findings(),
            'recommendations': self._compile_recommendations()
        }

    def _determine_overall_status(self) -> str:
        """Determine overall pass/fail status"""
        # Logic to determine based on all criteria
        return "PASS"  # Placeholder

    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from analysis"""
        return []  # Placeholder

    def _compile_recommendations(self) -> List[str]:
        """Compile recommendations"""
        return []  # Placeholder
