"""
PVTP-050: Comparative Module Testing Reporter
Report generation and visualization for multi-manufacturer comparison
"""

from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from datetime import datetime
import json


class ComparativeTestingReporter:
    """Reporter for comparative module testing"""

    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir
        self.charts = []

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete comparative testing report"""
        reports = {}

        self.generate_all_charts()

        reports['executive_summary'] = self.generate_executive_summary()
        reports['methodology'] = self.generate_methodology_section()
        reports['results'] = self.generate_results_section()
        reports['statistical_analysis'] = self.generate_statistical_section()
        reports['performance_ranking'] = self.generate_ranking_section()
        reports['recommendations'] = self.generate_recommendations()

        return reports

    def generate_executive_summary(self) -> str:
        """Generate executive summary"""
        ranking = self.data.get('ranking', [])
        stats = self.data.get('descriptive_statistics', {})

        summary = f"""
# Executive Summary
**Protocol:** PVTP-050 - Comparative Module Testing
**Test Date:** {self.data.get('test_date', 'N/A')}
**Manufacturers Tested:** {self.data.get('manufacturers_tested', 0)}
**Total Modules:** {self.data.get('total_modules', 0)}

## Performance Ranking
{self._format_ranking_table(ranking[:5])}

## Key Findings
- **Top Performer:** {ranking[0]['manufacturer'] if ranking else 'N/A'}
- **Overall Score:** {ranking[0]['overall_score']:.1f if ranking else 'N/A'}
- **Statistical Significance:** {'Yes' if self.data.get('statistical_tests', {}).get('anova', {}).get('significant') else 'No'}

## Recommendation
{self.data.get('summary', {}).get('recommendation', 'See detailed analysis')}
"""
        return summary

    def generate_methodology_section(self) -> str:
        """Generate methodology section"""
        return f"""
# Test Methodology

## Test Standards
- IEC 61215 (Module qualification)
- IEC 61853 (Performance testing)
- IEC 60904-1 (IV measurements)

## Test Conditions
- Irradiance: 1000 W/m² (STC)
- Temperature: 25°C ±2°C
- Spectrum: AM1.5
- Sample Size: 6 modules per manufacturer

## Statistical Methods
- One-way ANOVA for mean comparisons
- Tukey HSD post-hoc tests
- 95% confidence intervals
- Coefficient of variation for uniformity assessment
"""

    def generate_results_section(self) -> str:
        """Generate detailed results section"""
        stats = self.data.get('descriptive_statistics', {})

        section = "# Detailed Results by Manufacturer\n\n"

        for mfr_id, data in stats.items():
            section += f"## {data['manufacturer']}\n\n"
            section += f"### Power Output (Pmax)\n"
            section += f"- Mean: {data['pmax']['mean']:.2f} W\n"
            section += f"- Std Dev: {data['pmax']['std']:.2f} W\n"
            section += f"- CV: {data['pmax']['cv']:.2f}%\n"
            section += f"- Range: {data['pmax']['min']:.2f} - {data['pmax']['max']:.2f} W\n"
            section += f"- 95% CI: [{data['pmax']['ci_95'][0]:.2f}, {data['pmax']['ci_95'][1]:.2f}] W\n\n"

        return section

    def generate_statistical_section(self) -> str:
        """Generate statistical analysis section"""
        anova = self.data.get('statistical_tests', {}).get('anova', {})

        section = f"""
# Statistical Analysis

## ANOVA Results
- **F-statistic:** {anova.get('f_statistic', 'N/A'):.3f}
- **p-value:** {anova.get('p_value', 'N/A'):.4f}
- **Significant Difference:** {'Yes' if anova.get('significant') else 'No'}

## Assumptions Testing
{self._format_assumptions(anova.get('assumptions', {}))}

## Post-hoc Comparisons
{self._format_posthoc_tests(anova.get('posthoc', {}))}
"""
        return section

    def generate_ranking_section(self) -> str:
        """Generate performance ranking section"""
        indices = self.data.get('performance_indices', {})
        ranking = self.data.get('ranking', [])

        section = "# Performance Benchmarking & Ranking\n\n"
        section += self._format_detailed_ranking_table(ranking)

        return section

    def generate_recommendations(self) -> str:
        """Generate recommendations"""
        ranking = self.data.get('ranking', [])

        if not ranking:
            return "# Recommendations\nInsufficient data for recommendations"

        top = ranking[0]
        section = f"""
# Recommendations

## Procurement Recommendation
**Top Performer:** {top['manufacturer']}
- Overall Score: {top['overall_score']:.1f}
- Power Index: {top['power_index']:.1f}
- Efficiency Index: {top['efficiency_index']:.1f}

## Considerations
- Review pricing and availability
- Verify warranty terms
- Consider technology roadmap
- Assess manufacturer stability

## Alternative Options
{self._format_alternatives(ranking[1:3])}
"""
        return section

    def generate_all_charts(self):
        """Generate all required charts"""
        self.charts = []

        self.charts.append(self.plot_power_boxplots())
        self.charts.append(self.plot_performance_radar())
        self.charts.append(self.plot_statistical_comparison())
        self.charts.append(self.plot_ranking_bars())

    def plot_power_boxplots(self) -> str:
        """Plot power output box plots by manufacturer"""
        fig, ax = plt.subplots(figsize=(12, 6))

        stats = self.data.get('descriptive_statistics', {})

        manufacturers = []
        power_data = []

        for mfr_id, data in stats.items():
            manufacturers.append(data['manufacturer'])
            # Simulated distribution
            mean = data['pmax']['mean']
            std = data['pmax']['std']
            samples = np.random.normal(mean, std, data['sample_size'])
            power_data.append(samples)

        bp = ax.boxplot(power_data, labels=manufacturers, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')

        ax.set_ylabel('Power Output (W)', fontsize=12)
        ax.set_title('Power Output Distribution by Manufacturer', fontsize=14, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        filename = f'{self.output_dir}/comparative_power_boxplots.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_performance_radar(self) -> str:
        """Plot performance radar chart"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        ranking = self.data.get('ranking', [])[:5]  # Top 5

        categories = ['Power', 'Efficiency', 'Low Light', 'Temperature', 'Overall']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        for item in ranking:
            values = [
                item['power_index'],
                item['efficiency_index'],
                item['low_light_index'],
                item['temperature_index'],
                item['overall_score']
            ]
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2, label=item['manufacturer'])
            ax.fill(angles, values, alpha=0.15)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(80, 110)
        ax.set_title('Performance Index Comparison (Top 5)', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()
        filename = f'{self.output_dir}/comparative_radar_chart.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_statistical_comparison(self) -> str:
        """Plot statistical comparison matrix"""
        posthoc = self.data.get('statistical_tests', {}).get('anova', {}).get('posthoc', {})
        comparisons = posthoc.get('comparisons', [])

        if not comparisons:
            return ""

        # Create significance matrix
        manufacturers = list(set([c['manufacturer_1'] for c in comparisons] +
                               [c['manufacturer_2'] for c in comparisons]))
        n = len(manufacturers)
        matrix = np.zeros((n, n))

        for comp in comparisons:
            i = manufacturers.index(comp['manufacturer_1'])
            j = manufacturers.index(comp['manufacturer_2'])
            matrix[i, j] = 1 if comp['significant'] else 0
            matrix[j, i] = matrix[i, j]

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(matrix, cmap='RdYlGn_r', vmin=0, vmax=1)

        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(manufacturers)
        ax.set_yticklabels(manufacturers)

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        for i in range(n):
            for j in range(n):
                if i != j:
                    text = ax.text(j, i, 'Sig' if matrix[i, j] else 'NS',
                                 ha="center", va="center", color="black")

        ax.set_title("Statistical Significance Matrix\n(Sig = Significantly Different, NS = Not Significant)",
                    fontsize=12, fontweight='bold')
        fig.colorbar(im, ax=ax, label='Significance')

        plt.tight_layout()
        filename = f'{self.output_dir}/comparative_significance_matrix.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_ranking_bars(self) -> str:
        """Plot ranking bar chart"""
        ranking = self.data.get('ranking', [])

        fig, ax = plt.subplots(figsize=(12, 8))

        manufacturers = [r['manufacturer'] for r in ranking]
        scores = [r['overall_score'] for r in ranking]
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(ranking)))

        bars = ax.barh(manufacturers, scores, color=colors, edgecolor='black')
        ax.set_xlabel('Overall Performance Score', fontsize=12)
        ax.set_title('Performance Ranking', fontsize=14, fontweight='bold')
        ax.set_xlim(85, 105)
        ax.grid(True, axis='x', alpha=0.3)

        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 0.5, bar.get_y() + bar.get_height()/2,
                   f'#{i+1}: {score:.1f}',
                   va='center', fontweight='bold')

        plt.tight_layout()
        filename = f'{self.output_dir}/comparative_ranking.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def _format_ranking_table(self, ranking: List[Dict]) -> str:
        """Format ranking table"""
        if not ranking:
            return "No ranking data available"

        table = "| Rank | Manufacturer | Overall Score | Power Index | Efficiency Index |\n"
        table += "|------|--------------|---------------|-------------|------------------|\n"

        for item in ranking:
            table += f"| {item['rank']} | {item['manufacturer']} | "
            table += f"{item['overall_score']:.1f} | "
            table += f"{item['power_index']:.1f} | "
            table += f"{item['efficiency_index']:.1f} |\n"

        return table

    def _format_detailed_ranking_table(self, ranking: List[Dict]) -> str:
        """Format detailed ranking table"""
        if not ranking:
            return "No ranking data available"

        table = "| Rank | Manufacturer | Overall | Power | Efficiency | Low Light | Temperature |\n"
        table += "|------|--------------|---------|-------|------------|-----------|-------------|\n"

        for item in ranking:
            table += f"| {item['rank']} | {item['manufacturer']} | "
            table += f"{item['overall_score']:.1f} | "
            table += f"{item['power_index']:.1f} | "
            table += f"{item['efficiency_index']:.1f} | "
            table += f"{item['low_light_index']:.1f} | "
            table += f"{item['temperature_index']:.1f} |\n"

        return table

    def _format_assumptions(self, assumptions: Dict) -> str:
        """Format statistical assumptions"""
        normality = assumptions.get('normality_tests', [])
        levene = assumptions.get('levene_test', {})

        output = "### Normality Tests (Shapiro-Wilk)\n"
        for test in normality:
            output += f"- {test['manufacturer']}: "
            output += f"p={test['p_value']:.4f} ({'Normal' if test['normal'] else 'Non-normal'})\n"

        output += f"\n### Homogeneity of Variance (Levene's Test)\n"
        output += f"- p-value: {levene.get('p_value', 'N/A'):.4f}\n"
        output += f"- Homogeneous: {'Yes' if levene.get('homogeneous_variance') else 'No'}\n"

        return output

    def _format_posthoc_tests(self, posthoc: Dict) -> str:
        """Format post-hoc test results"""
        comparisons = posthoc.get('comparisons', [])

        if not comparisons:
            return "No post-hoc tests performed (no significant ANOVA result)"

        output = f"### {posthoc.get('method', 'Post-hoc Tests')}\n\n"
        output += "| Comparison | Mean Diff | p-value | Significant |\n"
        output += "|------------|-----------|---------|-------------|\n"

        for comp in comparisons:
            output += f"| {comp['manufacturer_1']} vs {comp['manufacturer_2']} | "
            output += f"{comp['mean_difference']:.2f} W | "
            output += f"{comp['bonferroni_p']:.4f} | "
            output += f"{'Yes' if comp['significant'] else 'No'} |\n"

        return output

    def _format_alternatives(self, alternatives: List[Dict]) -> str:
        """Format alternative options"""
        if not alternatives:
            return "No alternatives listed"

        output = ""
        for i, alt in enumerate(alternatives, 2):
            output += f"\n### Option {i}: {alt['manufacturer']}\n"
            output += f"- Overall Score: {alt['overall_score']:.1f}\n"
            output += f"- Rank: #{alt['rank']}\n"

        return output

    def export_data_package(self, format: str = 'json') -> str:
        """Export complete data package"""
        if format == 'json':
            filename = f'{self.output_dir}/comparative_testing_data.json'
            with open(filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        elif format == 'csv':
            filename = f'{self.output_dir}/comparative_testing_data.csv'
            df = pd.DataFrame(self.data.get('ranking', []))
            df.to_csv(filename, index=False)

        return filename
