"""
PVTP-054: End-of-Life & Recycling Assessment Handler
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime


class EndOfLifeHandler:
    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.module_weight = None
        self.material_recovery = {}

    def record_initial_characterization(self, module_data: Dict) -> None:
        """Record initial module characterization"""
        self.module_weight = module_data.get('weight_kg', 0)
        self.results['initial'] = {
            'weight_kg': self.module_weight,
            'dimensions': module_data.get('dimensions'),
            'age_years': module_data.get('age_years'),
            'technology': module_data.get('technology'),
            'residual_power': module_data.get('residual_power_w', 0)
        }

    def record_material_recovery(self, material: str, weight_kg: float,
                                 purity_percent: float) -> None:
        """Record recovered material data"""
        self.material_recovery[material] = {
            'weight_kg': weight_kg,
            'purity_percent': purity_percent,
            'mass_percent': (weight_kg / self.module_weight * 100) if self.module_weight else 0
        }

    def calculate_recovery_rates(self) -> Dict[str, Any]:
        """Calculate material recovery rates"""
        total_recovered = sum(m['weight_kg'] for m in self.material_recovery.values())
        recovery_rate = (total_recovered / self.module_weight * 100) if self.module_weight else 0

        recovery_analysis = {
            'total_input_kg': self.module_weight,
            'total_recovered_kg': total_recovered,
            'overall_recovery_rate': recovery_rate,
            'by_material': self.material_recovery,
            'mass_balance_closure': recovery_rate
        }

        self.results['recovery_rates'] = recovery_analysis
        return recovery_analysis

    def assess_material_value(self, commodity_prices: Dict[str, float]) -> Dict[str, Any]:
        """Assess economic value of recovered materials"""
        total_value = 0
        material_values = {}

        for material, data in self.material_recovery.items():
            price_per_kg = commodity_prices.get(material, 0)
            value = data['weight_kg'] * price_per_kg * (data['purity_percent'] / 100)
            total_value += value

            material_values[material] = {
                'weight_kg': data['weight_kg'],
                'price_per_kg': price_per_kg,
                'purity_adjusted_value': value
            }

        value_assessment = {
            'total_material_value': total_value,
            'value_per_module': total_value,
            'value_per_kg': total_value / self.module_weight if self.module_weight else 0,
            'by_material': material_values
        }

        self.results['material_value'] = value_assessment
        return value_assessment

    def calculate_processing_cost(self, cost_data: Dict) -> Dict[str, Any]:
        """Calculate processing costs"""
        labor_cost = cost_data.get('labor_hours', 0) * cost_data.get('labor_rate', 0)
        energy_cost = cost_data.get('energy_kwh', 0) * cost_data.get('energy_rate', 0)
        chemical_cost = cost_data.get('chemical_cost', 0)
        equipment_cost = cost_data.get('equipment_depreciation', 0)

        total_cost = labor_cost + energy_cost + chemical_cost + equipment_cost

        cost_analysis = {
            'labor_cost': labor_cost,
            'energy_cost': energy_cost,
            'chemical_cost': chemical_cost,
            'equipment_cost': equipment_cost,
            'total_processing_cost': total_cost,
            'cost_per_module': total_cost
        }

        self.results['processing_cost'] = cost_analysis
        return cost_analysis

    def calculate_net_value(self) -> float:
        """Calculate net economic value"""
        material_value = self.results.get('material_value', {}).get('total_material_value', 0)
        processing_cost = self.results.get('processing_cost', {}).get('total_processing_cost', 0)

        net_value = material_value - processing_cost

        self.results['net_value'] = {
            'material_value': material_value,
            'processing_cost': processing_cost,
            'net_value': net_value,
            'profitable': net_value > 0
        }

        return net_value

    def assess_environmental_impact(self, impact_data: Dict) -> Dict[str, Any]:
        """Assess environmental impact of recycling"""
        energy_consumed = impact_data.get('energy_kwh', 0)
        carbon_emissions = energy_consumed * impact_data.get('grid_carbon_factor', 0.5)  # kg CO2/kWh

        # Virgin material offset
        virgin_offset = 0
        for material, data in self.material_recovery.items():
            virgin_energy = impact_data.get(f'{material}_virgin_energy_kwh_per_kg', 0)
            virgin_offset += data['weight_kg'] * virgin_energy

        virgin_carbon_offset = virgin_offset * impact_data.get('grid_carbon_factor', 0.5)
        net_carbon = carbon_emissions - virgin_carbon_offset

        env_assessment = {
            'energy_consumed_kwh': energy_consumed,
            'carbon_emissions_kg': carbon_emissions,
            'virgin_material_energy_offset_kwh': virgin_offset,
            'virgin_carbon_offset_kg': virgin_carbon_offset,
            'net_carbon_impact_kg': net_carbon,
            'carbon_negative': net_carbon < 0,
            'landfill_diversion_rate': self.results.get('recovery_rates', {}).get('overall_recovery_rate', 0)
        }

        self.results['environmental_impact'] = env_assessment
        return env_assessment

    def calculate_recyclability_score(self) -> float:
        """Calculate overall recyclability score (0-100)"""
        # Factor 1: Material separation ease (0-100)
        separation_score = 80  # Based on manual assessment

        # Factor 2: Recovery rates (0-100)
        recovery_rate = self.results.get('recovery_rates', {}).get('overall_recovery_rate', 0)
        recovery_score = min(recovery_rate, 100)

        # Factor 3: Material purity (0-100)
        purity_scores = [m['purity_percent'] for m in self.material_recovery.values()]
        avg_purity = np.mean(purity_scores) if purity_scores else 0
        purity_score = avg_purity

        # Factor 4: Economic viability (0-100)
        net_value = self.results.get('net_value', {}).get('net_value', 0)
        economic_score = 100 if net_value > 0 else max(0, 50 + net_value)  # Scaled

        # Factor 5: Environmental benefit (0-100)
        carbon_negative = self.results.get('environmental_impact', {}).get('carbon_negative', False)
        env_score = 100 if carbon_negative else 50

        # Weighted average
        weights = [0.25, 0.25, 0.20, 0.15, 0.15]
        scores = [separation_score, recovery_score, purity_score, economic_score, env_score]

        recyclability_score = sum(w * s for w, s in zip(weights, scores))

        score_card = {
            'overall_score': recyclability_score,
            'factor_scores': {
                'separation_ease': separation_score,
                'recovery_rate': recovery_score,
                'material_purity': purity_score,
                'economic_viability': economic_score,
                'environmental_benefit': env_score
            },
            'rating': self._get_rating(recyclability_score)
        }

        self.results['recyclability_score'] = score_card
        return recyclability_score

    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Acceptable"
        else:
            return "Poor"

    def generate_report_data(self) -> Dict[str, Any]:
        """Generate complete report data"""
        if 'recyclability_score' not in self.results:
            self.calculate_recyclability_score()

        if 'net_value' not in self.results:
            self.calculate_net_value()

        return {
            'protocol_id': 'PVTP-054',
            'test_date': datetime.now().isoformat(),
            'results': self.results,
            'summary': self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            'overall_recovery_rate': self.results.get('recovery_rates', {}).get('overall_recovery_rate', 0),
            'net_value': self.results.get('net_value', {}).get('net_value', 0),
            'recyclability_score': self.results.get('recyclability_score', {}).get('overall_score', 0),
            'recyclability_rating': self.results.get('recyclability_score', {}).get('rating', 'Unknown'),
            'economically_viable': self.results.get('net_value', {}).get('profitable', False),
            'environmentally_beneficial': self.results.get('environmental_impact', {}).get('carbon_negative', False)
        }
