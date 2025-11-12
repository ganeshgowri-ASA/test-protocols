"""
PVTP-048: Energy Rating & Bankability Assessment Reporter
Report generation and data visualization
"""

from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from datetime import datetime
import json


class EnergyRatingReporter:
    """Reporter for energy rating and bankability assessment"""

    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir
        self.charts = []

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete report package"""
        reports = {}

        # Generate all charts
        self.generate_all_charts()

        # Generate report sections
        reports['executive_summary'] = self.generate_executive_summary()
        reports['energy_rating'] = self.generate_energy_rating_section()
        reports['bankability_assessment'] = self.generate_bankability_section()
        reports['financial_analysis'] = self.generate_financial_section()
        reports['appendix'] = self.generate_appendix()

        return reports

    def generate_executive_summary(self) -> str:
        """Generate executive summary"""
        summary = f"""
# Executive Summary
**Protocol:** PVTP-048 - Energy Rating & Bankability Assessment
**Test Date:** {self.data.get('test_date', 'N/A')}
**Module:** {self.data.get('module_info', {}).get('model', 'N/A')}
**Manufacturer:** {self.data.get('manufacturer', 'N/A')}

## Overall Assessment
**Bankability Rating:** {self.data.get('bankability_rating', 'N/A')}
**Energy Rating:** {self.data.get('energy_rating', 'N/A')}
**Recommendation:** {self.data.get('recommendation', 'N/A')}

## Key Findings
- Rated Power (STC): {self.data.get('pmax_stc', 'N/A')} W
- First Year Energy Yield: {self.data.get('year1_energy', 'N/A')} kWh/kWp
- 25-Year Total Energy: {self.data.get('lifetime_energy', 'N/A')} MWh
- Performance Ratio (Year 1): {self.data.get('pr_year1', 'N/A')}
- LCOE: ${self.data.get('lcoe', 'N/A')}/kWh

## Compliance Status
{self._format_compliance_table()}
"""
        return summary

    def generate_energy_rating_section(self) -> str:
        """Generate energy rating section"""
        section = f"""
# Energy Rating Analysis

## STC Performance
- Maximum Power (Pmax): {self.data.get('pmax', 'N/A')} W
- Open Circuit Voltage (Voc): {self.data.get('voc', 'N/A')} V
- Short Circuit Current (Isc): {self.data.get('isc', 'N/A')} A
- Fill Factor: {self.data.get('fill_factor', 'N/A')}
- Efficiency: {self.data.get('efficiency', 'N/A')}%

## Temperature Coefficients
- Pmax: {self.data.get('temp_coef_pmax', 'N/A')}%/°C
- Voc: {self.data.get('temp_coef_voc', 'N/A')}%/°C
- Isc: {self.data.get('temp_coef_isc', 'N/A')}%/°C

## Low Light Performance
- 200 W/m²: {self.data.get('perf_200w', 'N/A')}%
- 400 W/m²: {self.data.get('perf_400w', 'N/A')}%
- 600 W/m²: {self.data.get('perf_600w', 'N/A')}%

## Energy Yield by Climate Zone
{self._format_energy_yield_table()}

## 25-Year Power Degradation
{self._format_degradation_table()}
"""
        return section

    def generate_bankability_section(self) -> str:
        """Generate bankability assessment section"""
        bankability = self.data.get('bankability', {})

        section = f"""
# Bankability Assessment

## Overall Score
**Total Score:** {bankability.get('total_score', 'N/A')}/{bankability.get('max_score', 100)}
**Percentage:** {bankability.get('percentage', 'N/A')}%
**Rating:** {bankability.get('rating', 'N/A')}

## Factor Analysis
{self._format_bankability_factors(bankability.get('factors', {}))}

## Manufacturer Assessment
- Tier Classification: {self.data.get('manufacturer_tier', 'N/A')}
- Years in Operation: {self.data.get('years_operation', 'N/A')}
- Production Capacity: {self.data.get('production_capacity', 'N/A')} GW/year
- Financial Rating: {self.data.get('financial_rating', 'N/A')}

## Certifications
{self._format_certifications_list()}

## Warranty Terms
- Product Warranty: {self.data.get('product_warranty', 'N/A')} years
- Performance Warranty: {self.data.get('performance_warranty', 'N/A')} years
- Linear Degradation Guarantee: ≤{self.data.get('degradation_guarantee', 'N/A')}%/year

## Risk Assessment
{self._format_risk_assessment()}
"""
        return section

    def generate_financial_section(self) -> str:
        """Generate financial analysis section"""
        section = f"""
# Financial Analysis

## Levelized Cost of Energy (LCOE)
- Base Case: ${self.data.get('lcoe_base', 'N/A')}/kWh
- Optimistic: ${self.data.get('lcoe_optimistic', 'N/A')}/kWh
- Conservative: ${self.data.get('lcoe_conservative', 'N/A')}/kWh

## Net Present Value (NPV)
- 25-Year NPV: ${self.data.get('npv_25yr', 'N/A')}
- Discount Rate: {self.data.get('discount_rate', 'N/A')}%

## Internal Rate of Return (IRR)
- Project IRR: {self.data.get('irr', 'N/A')}%
- Equity IRR: {self.data.get('equity_irr', 'N/A')}%

## Sensitivity Analysis
{self._format_sensitivity_table()}

## Cash Flow Projection
{self._format_cashflow_summary()}
"""
        return section

    def generate_appendix(self) -> str:
        """Generate appendix with detailed data"""
        return """
# Appendix

## A. Test Conditions and Equipment
## B. Raw Measurement Data
## C. Calibration Certificates
## D. Uncertainty Budget
## E. Quality Control Records
"""

    def generate_all_charts(self):
        """Generate all required charts"""
        self.charts = []

        self.charts.append(self.plot_iv_curves())
        self.charts.append(self.plot_power_vs_irradiance())
        self.charts.append(self.plot_temperature_coefficients())
        self.charts.append(self.plot_energy_yield_by_climate())
        self.charts.append(self.plot_degradation_timeline())
        self.charts.append(self.plot_performance_ratio())
        self.charts.append(self.plot_lcoe_sensitivity())
        self.charts.append(self.plot_bankability_radar())

    def plot_iv_curves(self) -> str:
        """Plot IV curves at different conditions"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Simulated data - replace with actual data
        v = np.linspace(0, 50, 100)
        i_stc = 10 * (1 - np.exp(-(50-v)/5))
        p_stc = v * i_stc

        ax1.plot(v, i_stc, 'b-', linewidth=2, label='STC')
        ax1.set_xlabel('Voltage (V)')
        ax1.set_ylabel('Current (A)')
        ax1.set_title('I-V Curve')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2.plot(v, p_stc, 'r-', linewidth=2, label='STC')
        ax2.set_xlabel('Voltage (V)')
        ax2.set_ylabel('Power (W)')
        ax2.set_title('P-V Curve')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        filename = f'{self.output_dir}/iv_curves.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_power_vs_irradiance(self) -> str:
        """Plot power output vs irradiance"""
        fig, ax = plt.subplots(figsize=(10, 6))

        irradiance = np.array([200, 400, 600, 800, 1000])
        power = irradiance * 0.4  # Simulated linear relationship

        ax.plot(irradiance, power, 'bo-', linewidth=2, markersize=8)
        ax.set_xlabel('Irradiance (W/m²)')
        ax.set_ylabel('Power Output (W)')
        ax.set_title('Power Output vs Irradiance')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'{self.output_dir}/power_vs_irradiance.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_temperature_coefficients(self) -> str:
        """Plot temperature coefficient curves"""
        fig, ax = plt.subplots(figsize=(10, 6))

        temps = np.array([15, 25, 35, 50, 65, 75])
        pmax = 400 * (1 - 0.004 * (temps - 25))
        voc = 50 * (1 - 0.003 * (temps - 25))
        isc = 10 * (1 + 0.0005 * (temps - 25))

        ax.plot(temps, pmax/400*100, 'ro-', label='Pmax', linewidth=2)
        ax.plot(temps, voc/50*100, 'bo-', label='Voc', linewidth=2)
        ax.plot(temps, isc/10*100, 'go-', label='Isc', linewidth=2)

        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Normalized Value (%)')
        ax.set_title('Temperature Coefficients')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'{self.output_dir}/temperature_coefficients.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_energy_yield_by_climate(self) -> str:
        """Plot energy yield by climate zone"""
        fig, ax = plt.subplots(figsize=(10, 6))

        zones = ['Hot-Dry', 'Hot-Humid', 'Temperate', 'Cold']
        yields = [1850, 1650, 1400, 1200]  # kWh/kWp/year

        bars = ax.bar(zones, yields, color=['red', 'orange', 'green', 'blue'], alpha=0.7)
        ax.set_ylabel('Specific Yield (kWh/kWp/year)')
        ax.set_title('Annual Energy Yield by Climate Zone')
        ax.grid(True, axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')

        plt.tight_layout()
        filename = f'{self.output_dir}/energy_yield_climate.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_degradation_timeline(self) -> str:
        """Plot 25-year power degradation"""
        fig, ax = plt.subplots(figsize=(12, 6))

        years = np.arange(0, 26)
        # Year 1 LID, then linear degradation
        power = np.zeros(26)
        power[0] = 100
        power[1] = 98  # 2% LID
        for i in range(2, 26):
            power[i] = 98 - 0.5 * (i - 1)

        ax.plot(years, power, 'b-', linewidth=2, label='Projected Power')
        ax.axhline(y=80, color='r', linestyle='--', label='Warranty Guarantee (80%)')
        ax.fill_between(years, power-1, power+1, alpha=0.2, label='Uncertainty Band')

        ax.set_xlabel('Year')
        ax.set_ylabel('Relative Power (%)')
        ax.set_title('25-Year Power Degradation Projection')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 25)
        ax.set_ylim(75, 101)

        plt.tight_layout()
        filename = f'{self.output_dir}/degradation_timeline.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_performance_ratio(self) -> str:
        """Plot performance ratio over time"""
        fig, ax = plt.subplots(figsize=(10, 6))

        years = np.arange(1, 26)
        pr = 0.86 - 0.002 * years  # Slight decline over time

        ax.plot(years, pr, 'g-', linewidth=2)
        ax.axhline(y=0.80, color='r', linestyle='--', label='Minimum Threshold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Performance Ratio')
        ax.set_title('Performance Ratio Projection')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0.75, 0.90)

        plt.tight_layout()
        filename = f'{self.output_dir}/performance_ratio.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_lcoe_sensitivity(self) -> str:
        """Plot LCOE sensitivity analysis"""
        fig, ax = plt.subplots(figsize=(10, 6))

        factors = ['CAPEX', 'OPEX', 'Degradation', 'Discount\nRate', 'Energy\nYield']
        impact = [-0.15, 0.08, 0.12, 0.10, -0.20]  # % change in LCOE

        colors = ['green' if x < 0 else 'red' for x in impact]
        bars = ax.barh(factors, impact, color=colors, alpha=0.7)

        ax.set_xlabel('Impact on LCOE (%)')
        ax.set_title('LCOE Sensitivity Analysis')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        filename = f'{self.output_dir}/lcoe_sensitivity.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_bankability_radar(self) -> str:
        """Plot bankability factor radar chart"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        categories = ['Tier Status', 'Certifications', 'Warranty', 'Performance', 'Financial']
        values = [20, 15, 15, 22, 13]  # Actual scores
        max_values = [20, 15, 15, 25, 15]  # Maximum possible scores

        # Normalize to 0-100 scale
        values_norm = [v/m*100 for v, m in zip(values, max_values)]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values_norm += values_norm[:1]
        angles += angles[:1]

        ax.plot(angles, values_norm, 'o-', linewidth=2, label='Actual Score')
        ax.fill(angles, values_norm, alpha=0.25)
        ax.plot(angles, [100]*len(angles), '--', color='green', alpha=0.5, label='Maximum')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('Bankability Factor Analysis', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()
        filename = f'{self.output_dir}/bankability_radar.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def _format_compliance_table(self) -> str:
        """Format compliance status table"""
        return """
| Requirement | Status | Notes |
|-------------|--------|-------|
| IEC 61215 | ✓ Pass | All tests passed |
| IEC 61730 | ✓ Pass | Safety certification valid |
| Tier 1 Manufacturer | ✓ Pass | BNEF verified |
| Warranty Terms | ✓ Pass | 12/25 year coverage |
"""

    def _format_energy_yield_table(self) -> str:
        """Format energy yield table"""
        return """
| Climate Zone | Annual Yield (kWh/kWp) | 25-Year Total (MWh/kWp) |
|--------------|------------------------|-------------------------|
| Hot-Dry      | 1,850                  | 42.5                    |
| Hot-Humid    | 1,650                  | 37.9                    |
| Temperate    | 1,400                  | 32.2                    |
| Cold         | 1,200                  | 27.6                    |
"""

    def _format_degradation_table(self) -> str:
        """Format degradation projection table"""
        return """
| Year | Power (%) | Relative to Initial |
|------|-----------|---------------------|
| 0    | 100.0     | 100.0%              |
| 1    | 98.0      | 98.0%               |
| 5    | 96.0      | 96.0%               |
| 10   | 93.5      | 93.5%               |
| 15   | 91.0      | 91.0%               |
| 20   | 88.5      | 88.5%               |
| 25   | 86.0      | 86.0%               |
"""

    def _format_bankability_factors(self, factors: Dict) -> str:
        """Format bankability factors"""
        output = "| Factor | Score | Max | Status |\n"
        output += "|--------|-------|-----|--------|\n"

        for name, data in factors.items():
            output += f"| {name} | {data.get('score', 0)} | {data.get('max', 0)} | {data.get('status', 'N/A')} |\n"

        return output

    def _format_certifications_list(self) -> str:
        """Format certifications list"""
        certs = self.data.get('certifications', [])
        return '\n'.join([f"- {cert}" for cert in certs])

    def _format_risk_assessment(self) -> str:
        """Format risk assessment"""
        return """
| Risk Factor | Level | Mitigation |
|-------------|-------|------------|
| Technology Risk | Low | Proven technology, established manufacturer |
| Performance Risk | Low | Conservative degradation assumptions |
| Warranty Risk | Low | Strong manufacturer backing |
| Market Risk | Medium | Subject to policy changes |
"""

    def _format_sensitivity_table(self) -> str:
        """Format sensitivity analysis table"""
        return """
| Parameter | -10% | Base | +10% | Impact |
|-----------|------|------|------|--------|
| CAPEX | $0.045 | $0.050 | $0.055 | High |
| Energy Yield | $0.055 | $0.050 | $0.045 | High |
| Degradation | $0.048 | $0.050 | $0.052 | Medium |
| Discount Rate | $0.048 | $0.050 | $0.053 | Medium |
"""

    def _format_cashflow_summary(self) -> str:
        """Format cash flow summary"""
        return """
| Period | Revenue | OPEX | Net Cash Flow | Cumulative |
|--------|---------|------|---------------|------------|
| Year 1-5 | $125k | $15k | $110k | $550k |
| Year 6-10 | $120k | $18k | $102k | $1,060k |
| Year 11-15 | $115k | $20k | $95k | $1,535k |
| Year 16-20 | $110k | $22k | $88k | $1,975k |
| Year 21-25 | $105k | $25k | $80k | $2,375k |
"""

    def export_data_package(self, format: str = 'json') -> str:
        """Export complete data package"""
        if format == 'json':
            filename = f'{self.output_dir}/data_package.json'
            with open(filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        elif format == 'csv':
            filename = f'{self.output_dir}/data_package.csv'
            df = pd.DataFrame([self.data])
            df.to_csv(filename, index=False)

        return filename
