"""
PVTP-054: End-of-Life & Recycling Assessment Reporter
"""

from typing import Dict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np


class EndOfLifeReporter:
    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete report"""
        return {
            'summary': self.generate_summary(),
            'material_recovery': self.generate_recovery_section(),
            'economic_analysis': self.generate_economic_section(),
            'environmental_impact': self.generate_environmental_section(),
            'recyclability_score': self.generate_recyclability_section()
        }

    def generate_summary(self) -> str:
        """Generate executive summary"""
        summary = self.data.get('summary', {})

        return f"""
# End-of-Life & Recycling Assessment Report

## Overall Assessment
- Recovery Rate: {summary.get('overall_recovery_rate', 0):.1f}%
- Recyclability Score: {summary.get('recyclability_score', 0):.1f}/100
- Rating: {summary.get('recyclability_rating', 'N/A')}

## Economic Viability
- Net Value: ${summary.get('net_value', 0):.2f} per module
- Economically Viable: {'Yes' if summary.get('economically_viable') else 'No'}

## Environmental Impact
- Carbon Negative: {'Yes' if summary.get('environmentally_beneficial') else 'No'}

## Recommendation
{self._generate_recommendation(summary)}
"""

    def generate_recovery_section(self) -> str:
        """Generate material recovery section"""
        recovery = self.data.get('results', {}).get('recovery_rates', {})

        output = f"""
# Material Recovery Analysis

## Overall Performance
- Total Input: {recovery.get('total_input_kg', 0):.2f} kg
- Total Recovered: {recovery.get('total_recovered_kg', 0):.2f} kg
- Recovery Rate: {recovery.get('overall_recovery_rate', 0):.1f}%

## Recovery by Material
| Material | Weight (kg) | Purity (%) | Mass % |
|----------|-------------|------------|--------|
"""

        by_material = recovery.get('by_material', {})
        for material, data in by_material.items():
            output += f"| {material} | {data.get('weight_kg', 0):.2f} | "
            output += f"{data.get('purity_percent', 0):.1f} | "
            output += f"{data.get('mass_percent', 0):.1f} |\n"

        return output

    def generate_economic_section(self) -> str:
        """Generate economic analysis section"""
        value = self.data.get('results', {}).get('material_value', {})
        cost = self.data.get('results', {}).get('processing_cost', {})
        net = self.data.get('results', {}).get('net_value', {})

        return f"""
# Economic Analysis

## Material Value
- Total Value: ${value.get('total_material_value', 0):.2f}
- Value per kg: ${value.get('value_per_kg', 0):.2f}/kg

## Processing Costs
- Labor: ${cost.get('labor_cost', 0):.2f}
- Energy: ${cost.get('energy_cost', 0):.2f}
- Chemicals: ${cost.get('chemical_cost', 0):.2f}
- Equipment: ${cost.get('equipment_cost', 0):.2f}
- Total: ${cost.get('total_processing_cost', 0):.2f}

## Net Economic Value
- Material Value: ${net.get('material_value', 0):.2f}
- Processing Cost: ${net.get('processing_cost', 0):.2f}
- **Net Value: ${net.get('net_value', 0):.2f}**
- Profitable: {'Yes' if net.get('profitable') else 'No'}
"""

    def generate_environmental_section(self) -> str:
        """Generate environmental impact section"""
        env = self.data.get('results', {}).get('environmental_impact', {})

        return f"""
# Environmental Impact Assessment

## Energy Balance
- Energy Consumed: {env.get('energy_consumed_kwh', 0):.1f} kWh
- Virgin Material Offset: {env.get('virgin_material_energy_offset_kwh', 0):.1f} kWh

## Carbon Footprint
- Recycling Emissions: {env.get('carbon_emissions_kg', 0):.1f} kg CO2e
- Virgin Material Offset: {env.get('virgin_carbon_offset_kg', 0):.1f} kg CO2e
- **Net Carbon Impact: {env.get('net_carbon_impact_kg', 0):.1f} kg CO2e**
- Carbon Negative: {'Yes' if env.get('carbon_negative') else 'No'}

## Waste Diversion
- Landfill Diversion Rate: {env.get('landfill_diversion_rate', 0):.1f}%
"""

    def generate_recyclability_section(self) -> str:
        """Generate recyclability score section"""
        score_card = self.data.get('results', {}).get('recyclability_score', {})
        factors = score_card.get('factor_scores', {})

        output = f"""
# Recyclability Score Card

## Overall Score: {score_card.get('overall_score', 0):.1f}/100
## Rating: {score_card.get('rating', 'N/A')}

## Factor Breakdown
| Factor | Score | Weight |
|--------|-------|--------|
| Separation Ease | {factors.get('separation_ease', 0):.1f} | 25% |
| Recovery Rate | {factors.get('recovery_rate', 0):.1f} | 25% |
| Material Purity | {factors.get('material_purity', 0):.1f} | 20% |
| Economic Viability | {factors.get('economic_viability', 0):.1f} | 15% |
| Environmental Benefit | {factors.get('environmental_benefit', 0):.1f} | 15% |
"""

        return output

    def _generate_recommendation(self, summary: Dict) -> str:
        """Generate recommendation based on results"""
        score = summary.get('recyclability_score', 0)

        if score >= 80:
            return "Excellent recyclability. Recommend establishing recycling partnerships."
        elif score >= 70:
            return "Good recyclability. Viable for commercial recycling operations."
        elif score >= 60:
            return "Acceptable recyclability. May require process optimization for profitability."
        else:
            return "Poor recyclability. Significant improvements needed or alternative disposal required."
