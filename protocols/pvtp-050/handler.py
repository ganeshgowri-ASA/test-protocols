"""
PVTP-050: Comparative Module Testing Handler
Data processing and statistical analysis for multi-manufacturer comparison
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime
from scipy import stats
import json


class ComparativeTestingHandler:
    """Handler for comparative module testing and benchmarking"""

    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.manufacturers = {}
        self.statistical_results = {}

    def register_manufacturer(self, manufacturer_id: str, manufacturer_name: str,
                             module_info: Dict) -> None:
        """Register a manufacturer for comparison"""
        self.manufacturers[manufacturer_id] = {
            'name': manufacturer_name,
            'module_model': module_info.get('model'),
            'technology': module_info.get('technology'),
            'nameplate_power': module_info.get('nameplate_power'),
            'modules': [],
            'measurements': []
        }

    def add_module_data(self, manufacturer_id: str, module_serial: str,
                       test_data: Dict) -> None:
        """Add test data for a specific module"""
        if manufacturer_id not in self.manufacturers:
            raise ValueError(f"Manufacturer {manufacturer_id} not registered")

        module_data = {
            'serial_number': module_serial,
            'pmax': test_data.get('pmax'),
            'voc': test_data.get('voc'),
            'isc': test_data.get('isc'),
            'vmpp': test_data.get('vmpp'),
            'impp': test_data.get('impp'),
            'fill_factor': test_data.get('fill_factor'),
            'efficiency': test_data.get('efficiency'),
            'temp_coef_pmax': test_data.get('temp_coef_pmax'),
            'low_light_200w': test_data.get('low_light_200w'),
            'test_timestamp': test_data.get('timestamp', datetime.now().isoformat())
        }

        self.manufacturers[manufacturer_id]['modules'].append(module_data)

    def calculate_descriptive_statistics(self) -> Dict[str, Any]:
        """Calculate descriptive statistics for each manufacturer"""
        stats_summary = {}

        for mfr_id, mfr_data in self.manufacturers.items():
            modules = mfr_data['modules']
            if not modules:
                continue

            df = pd.DataFrame(modules)

            stats_summary[mfr_id] = {
                'manufacturer': mfr_data['name'],
                'sample_size': len(modules),
                'pmax': {
                    'mean': float(df['pmax'].mean()),
                    'std': float(df['pmax'].std()),
                    'cv': float(df['pmax'].std() / df['pmax'].mean() * 100),
                    'min': float(df['pmax'].min()),
                    'max': float(df['pmax'].max()),
                    'median': float(df['pmax'].median()),
                    'ci_95': self._confidence_interval(df['pmax'].values)
                },
                'efficiency': {
                    'mean': float(df['efficiency'].mean()),
                    'std': float(df['efficiency'].std()),
                    'cv': float(df['efficiency'].std() / df['efficiency'].mean() * 100)
                },
                'fill_factor': {
                    'mean': float(df['fill_factor'].mean()),
                    'std': float(df['fill_factor'].std())
                },
                'temp_coef_pmax': {
                    'mean': float(df['temp_coef_pmax'].mean()),
                    'std': float(df['temp_coef_pmax'].std())
                },
                'low_light_performance': {
                    'mean': float(df['low_light_200w'].mean()),
                    'std': float(df['low_light_200w'].std())
                }
            }

        self.results['descriptive_statistics'] = stats_summary
        return stats_summary

    def perform_anova(self, parameter: str = 'pmax') -> Dict[str, Any]:
        """Perform one-way ANOVA to compare manufacturers"""
        groups = []
        labels = []

        for mfr_id, mfr_data in self.manufacturers.items():
            modules = mfr_data['modules']
            if modules:
                values = [m[parameter] for m in modules if m.get(parameter) is not None]
                if values:
                    groups.append(values)
                    labels.append(mfr_data['name'])

        if len(groups) < 2:
            return {'error': 'Need at least 2 manufacturers for comparison'}

        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*groups)

        # Test assumptions
        # Normality test (Shapiro-Wilk for each group)
        normality_tests = []
        for i, group in enumerate(groups):
            if len(group) >= 3:
                stat, p = stats.shapiro(group)
                normality_tests.append({
                    'manufacturer': labels[i],
                    'test': 'Shapiro-Wilk',
                    'statistic': float(stat),
                    'p_value': float(p),
                    'normal': p > 0.05
                })

        # Levene's test for homogeneity of variance
        levene_stat, levene_p = stats.levene(*groups)

        anova_results = {
            'parameter': parameter,
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'manufacturers_compared': labels,
            'assumptions': {
                'normality_tests': normality_tests,
                'levene_test': {
                    'statistic': float(levene_stat),
                    'p_value': float(levene_p),
                    'homogeneous_variance': levene_p > 0.05
                }
            }
        }

        # If significant, perform post-hoc tests
        if p_value < 0.05:
            anova_results['posthoc'] = self._perform_posthoc_tests(groups, labels, parameter)

        self.statistical_results['anova'] = anova_results
        return anova_results

    def _perform_posthoc_tests(self, groups: List[List[float]],
                               labels: List[str], parameter: str) -> Dict:
        """Perform Tukey HSD post-hoc test"""
        from itertools import combinations

        pairwise_comparisons = []

        for i, j in combinations(range(len(groups)), 2):
            # t-test with Bonferroni correction
            t_stat, p_val = stats.ttest_ind(groups[i], groups[j])
            bonferroni_p = p_val * (len(groups) * (len(groups) - 1) / 2)

            mean_diff = np.mean(groups[i]) - np.mean(groups[j])

            pairwise_comparisons.append({
                'manufacturer_1': labels[i],
                'manufacturer_2': labels[j],
                'mean_difference': float(mean_diff),
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'bonferroni_p': float(min(bonferroni_p, 1.0)),
                'significant': bonferroni_p < 0.05
            })

        return {
            'method': 'Bonferroni-corrected t-tests',
            'comparisons': pairwise_comparisons
        }

    def calculate_performance_indices(self, baseline_mfr: str = None) -> Dict[str, Any]:
        """Calculate performance indices relative to baseline"""
        if not self.results.get('descriptive_statistics'):
            self.calculate_descriptive_statistics()

        stats_data = self.results['descriptive_statistics']

        # Determine baseline
        if baseline_mfr and baseline_mfr in stats_data:
            baseline = stats_data[baseline_mfr]
        else:
            # Use highest mean power as baseline
            baseline_mfr = max(stats_data.items(),
                             key=lambda x: x[1]['pmax']['mean'])[0]
            baseline = stats_data[baseline_mfr]

        indices = {}

        for mfr_id, stats in stats_data.items():
            power_index = (stats['pmax']['mean'] / baseline['pmax']['mean']) * 100
            efficiency_index = (stats['efficiency']['mean'] / baseline['efficiency']['mean']) * 100
            low_light_index = (stats['low_light_performance']['mean'] /
                             baseline['low_light_performance']['mean']) * 100

            # Temperature robustness (lower is better, so invert)
            temp_baseline = abs(baseline['temp_coef_pmax']['mean'])
            temp_actual = abs(stats['temp_coef_pmax']['mean'])
            temp_index = (temp_baseline / temp_actual) * 100 if temp_actual > 0 else 100

            indices[mfr_id] = {
                'manufacturer': stats['manufacturer'],
                'power_index': float(power_index),
                'efficiency_index': float(efficiency_index),
                'low_light_index': float(low_light_index),
                'temperature_index': float(temp_index),
                'overall_score': self._calculate_overall_score({
                    'power': power_index,
                    'efficiency': efficiency_index,
                    'low_light': low_light_index,
                    'temperature': temp_index,
                    'uniformity': 100 - stats['pmax']['cv']  # Lower CV is better
                })
            }

        self.results['performance_indices'] = indices
        self.results['baseline_manufacturer'] = baseline_mfr
        return indices

    def _calculate_overall_score(self, indices: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weights = self.config.get('acceptance_criteria', {}).get('ranking_criteria', {})

        score = 0.0
        score += indices.get('power', 100) * weights.get('stc_power', {}).get('weight', 0.30)
        score += indices.get('low_light', 100) * weights.get('low_light_performance', {}).get('weight', 0.20)
        score += indices.get('temperature', 100) * weights.get('temperature_coefficient', {}).get('weight', 0.15)
        score += indices.get('efficiency', 100) * weights.get('efficiency', {}).get('weight', 0.15)
        score += indices.get('uniformity', 100) * weights.get('uniformity', {}).get('weight', 0.10)

        return float(score)

    def generate_ranking(self) -> List[Dict[str, Any]]:
        """Generate final performance ranking"""
        if 'performance_indices' not in self.results:
            self.calculate_performance_indices()

        indices = self.results['performance_indices']

        ranking = sorted(
            indices.items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        )

        ranked_list = []
        for rank, (mfr_id, data) in enumerate(ranking, 1):
            ranked_list.append({
                'rank': rank,
                'manufacturer_id': mfr_id,
                'manufacturer': data['manufacturer'],
                'overall_score': data['overall_score'],
                'power_index': data['power_index'],
                'efficiency_index': data['efficiency_index'],
                'low_light_index': data['low_light_index'],
                'temperature_index': data['temperature_index']
            })

        self.results['ranking'] = ranked_list
        return ranked_list

    def _confidence_interval(self, data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval"""
        mean = np.mean(data)
        sem = stats.sem(data)
        interval = sem * stats.t.ppf((1 + confidence) / 2., len(data) - 1)
        return (float(mean - interval), float(mean + interval))

    def detect_outliers(self, manufacturer_id: str, parameter: str = 'pmax') -> List[Dict]:
        """Detect statistical outliers using modified Z-score"""
        if manufacturer_id not in self.manufacturers:
            return []

        modules = self.manufacturers[manufacturer_id]['modules']
        values = np.array([m[parameter] for m in modules if m.get(parameter) is not None])

        if len(values) < 3:
            return []

        median = np.median(values)
        mad = np.median(np.abs(values - median))
        modified_z_scores = 0.6745 * (values - median) / mad if mad > 0 else np.zeros_like(values)

        outliers = []
        for i, (value, z_score) in enumerate(zip(values, modified_z_scores)):
            if abs(z_score) > 3.5:
                outliers.append({
                    'index': i,
                    'serial_number': modules[i]['serial_number'],
                    'value': float(value),
                    'z_score': float(z_score),
                    'deviation_from_median': float(value - median)
                })

        return outliers

    def generate_report_data(self) -> Dict[str, Any]:
        """Compile all data for report generation"""
        # Ensure all analyses are complete
        if 'descriptive_statistics' not in self.results:
            self.calculate_descriptive_statistics()
        if 'anova' not in self.statistical_results:
            self.perform_anova('pmax')
        if 'ranking' not in self.results:
            self.generate_ranking()

        return {
            'protocol_id': 'PVTP-050',
            'test_date': datetime.now().isoformat(),
            'manufacturers_tested': len(self.manufacturers),
            'total_modules': sum(len(m['modules']) for m in self.manufacturers.values()),
            'descriptive_statistics': self.results.get('descriptive_statistics', {}),
            'statistical_tests': self.statistical_results,
            'performance_indices': self.results.get('performance_indices', {}),
            'ranking': self.results.get('ranking', []),
            'baseline_manufacturer': self.results.get('baseline_manufacturer'),
            'summary': self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        ranking = self.results.get('ranking', [])

        if ranking:
            top_performer = ranking[0]
            return {
                'top_performer': top_performer['manufacturer'],
                'top_score': top_performer['overall_score'],
                'manufacturers_tested': len(self.manufacturers),
                'statistically_significant': self.statistical_results.get('anova', {}).get('significant', False),
                'recommendation': f"Top performer: {top_performer['manufacturer']} with overall score of {top_performer['overall_score']:.1f}"
            }
        else:
            return {'error': 'No ranking available'}
