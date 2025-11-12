"""
PVTP-053: Module Cleaning Efficiency Reporter
"""

from typing import Dict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np


class CleaningEfficiencyReporter:
    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete report"""
        return {
            'summary': self.generate_summary(),
            'soiling_analysis': self.generate_soiling_section(),
            'cleaning_comparison': self.generate_comparison_section(),
            'cost_benefit': self.generate_cost_benefit_section()
        }

    def generate_summary(self) -> str:
        """Generate executive summary"""
        comparison = self.data.get('results', {}).get('method_comparison', [])
        best_method = comparison[0] if comparison else {}

        return f"""
# Module Cleaning Efficiency Test Report

## Best Performing Method
- Method: {best_method.get('method', 'N/A')}
- Recovery Rate: {best_method.get('avg_recovery_percent', 0):.1f}%
- ROI: {best_method.get('roi_percent', 0):.1f}%
- Cost Effective: {'Yes' if best_method.get('cost_effective') else 'No'}

## Soiling Impact
{self._format_soiling_summary()}

## Recommendations
{self._generate_recommendations()}
"""

    def generate_soiling_section(self) -> str:
        """Generate soiling analysis section"""
        soiling = self.data.get('results', {}).get('soiling_analysis', {})

        return f"""
# Soiling Analysis

## Soiling Rate
- Daily Soiling Rate: {soiling.get('daily_soiling_rate', 0):.3f}%/day
- Maximum Soiling Loss: {soiling.get('max_soiling_loss', 0):.1f}%
- Monitoring Duration: {soiling.get('days_monitored', 0)} days

## Impact Assessment
- Initial Loss: {soiling.get('initial_soiling_loss', 0):.1f}%
- Final Loss: {soiling.get('final_soiling_loss', 0):.1f}%
"""

    def generate_comparison_section(self) -> str:
        """Generate method comparison section"""
        comparison = self.data.get('results', {}).get('method_comparison', [])

        output = "# Cleaning Method Comparison\n\n"
        output += "| Rank | Method | Recovery % | Cost ($) | Time (min) | ROI % |\n"
        output += "|------|--------|------------|----------|------------|-------|\n"

        for i, method in enumerate(comparison, 1):
            output += f"| {i} | {method.get('method', 'N/A')} | "
            output += f"{method.get('avg_recovery_percent', 0):.1f} | "
            output += f"{method.get('avg_cost_usd', 0):.2f} | "
            output += f"{method.get('avg_time_minutes', 0):.1f} | "
            output += f"{method.get('roi_percent', 0):.1f} |\n"

        return output

    def generate_cost_benefit_section(self) -> str:
        """Generate cost-benefit analysis section"""
        return "# Cost-Benefit Analysis\n\nSee detailed analysis in method comparison table above."

    def _format_soiling_summary(self) -> str:
        """Format soiling summary"""
        soiling = self.data.get('results', {}).get('soiling_analysis', {})
        max_loss = soiling.get('max_soiling_loss', 0)

        if max_loss < 5:
            return "Low soiling impact - minimal cleaning required"
        elif max_loss < 10:
            return "Moderate soiling - quarterly cleaning recommended"
        else:
            return "High soiling - monthly cleaning recommended"

    def _generate_recommendations(self) -> str:
        """Generate recommendations"""
        comparison = self.data.get('results', {}).get('method_comparison', [])

        if not comparison:
            return "Insufficient data for recommendations"

        best = comparison[0]
        return f"""
Recommended Cleaning Method: {best.get('method')}
- Provides best balance of effectiveness and cost
- Expected ROI: {best.get('roi_percent', 0):.1f}%
- Average recovery: {best.get('avg_recovery_percent', 0):.1f}%
"""
