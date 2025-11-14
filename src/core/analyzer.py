"""Protocol data analysis and QC."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProtocolAnalyzer:
    """Analyzes test data and performs QC checks."""

    def __init__(
        self,
        qc_criteria: Dict[str, Any],
        analysis_methods: Dict[str, Any]
    ) -> None:
        """Initialize analyzer.

        Args:
            qc_criteria: Quality control criteria
            analysis_methods: Analysis method configuration
        """
        self.qc_criteria = qc_criteria
        self.analysis_methods = analysis_methods

    def analyze(self, measurements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform comprehensive analysis on measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            List of analysis results
        """
        if not measurements:
            logger.warning("No measurements to analyze")
            return []

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(measurements)

        results = []

        # Statistical analysis
        statistical_results = self._statistical_analysis(df)
        results.extend(statistical_results)

        # QC checks
        qc_results = self._qc_checks(df)
        results.extend(qc_results)

        # Performance indices
        performance_results = self._calculate_performance_indices(df)
        results.extend(performance_results)

        return results

    def _statistical_analysis(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Perform statistical analysis.

        Args:
            df: Measurements DataFrame

        Returns:
            List of statistical results
        """
        results = []

        # Get analysis methods configuration
        stat_config = self.analysis_methods.get('statistical_analysis', {})
        methods = stat_config.get('methods', ['mean', 'median', 'std_dev'])
        parameters = stat_config.get('parameters', [])

        # Group by metric name
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name]['metric_value']

            if parameters and metric_name not in parameters:
                continue

            stats = {}

            if 'mean' in methods:
                stats['mean'] = float(np.mean(metric_data))

            if 'median' in methods:
                stats['median'] = float(np.median(metric_data))

            if 'std_dev' in methods:
                stats['std_dev'] = float(np.std(metric_data))

            if 'percentile_95' in methods:
                stats['percentile_95'] = float(np.percentile(metric_data, 95))

            if 'percentile_99' in methods:
                stats['percentile_99'] = float(np.percentile(metric_data, 99))

            # Create result entry
            for stat_name, stat_value in stats.items():
                results.append({
                    'result_type': 'statistical',
                    'metric_name': metric_name,
                    'calculated_value': stat_value,
                    'calculation_method': stat_name,
                    'result_data': {
                        'count': len(metric_data),
                        'min': float(metric_data.min()),
                        'max': float(metric_data.max())
                    }
                })

        return results

    def _qc_checks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Perform QC checks.

        Args:
            df: Measurements DataFrame

        Returns:
            List of QC results
        """
        results = []

        # Data completeness check
        completeness = self._check_data_completeness(df)
        min_completeness = self.qc_criteria.get('data_completeness', 95)

        results.append({
            'result_type': 'qc',
            'metric_name': 'data_completeness',
            'calculated_value': completeness,
            'unit': 'percentage',
            'pass_fail': 'pass' if completeness >= min_completeness else 'fail',
            'threshold': min_completeness,
            'calculation_method': 'data_completeness_check',
            'result_data': {
                'total_expected': len(df),
                'total_received': len(df[df['quality_flag'] == 'good'])
            }
        })

        # Validation rules checks
        validation_rules = self.qc_criteria.get('validation_rules', [])
        for rule in validation_rules:
            rule_result = self._apply_validation_rule(df, rule)
            if rule_result:
                results.append(rule_result)

        return results

    def _check_data_completeness(self, df: pd.DataFrame) -> float:
        """Check data completeness percentage.

        Args:
            df: Measurements DataFrame

        Returns:
            Completeness percentage
        """
        if len(df) == 0:
            return 0.0

        good_data = len(df[df['quality_flag'] == 'good'])
        return (good_data / len(df)) * 100

    def _apply_validation_rule(
        self,
        df: pd.DataFrame,
        rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Apply a validation rule.

        Args:
            df: Measurements DataFrame
            rule: Validation rule configuration

        Returns:
            Validation result or None
        """
        parameter = rule.get('parameter')
        condition = rule.get('condition')
        threshold = rule.get('threshold')

        metric_data = df[df['metric_name'] == parameter]['metric_value']

        if len(metric_data) == 0:
            return None

        calculated_value = None
        pass_fail = 'pass'

        if condition == 'percentile_95':
            calculated_value = float(np.percentile(metric_data, 95))
            pass_fail = 'pass' if calculated_value <= threshold else 'fail'

        elif condition == 'max':
            calculated_value = float(metric_data.max())
            pass_fail = 'pass' if calculated_value <= threshold else 'fail'

        elif condition == 'min':
            calculated_value = float(metric_data.min())
            pass_fail = 'pass' if calculated_value >= threshold else 'fail'

        return {
            'result_type': 'validation',
            'metric_name': parameter,
            'calculated_value': calculated_value,
            'unit': rule.get('unit'),
            'pass_fail': pass_fail,
            'threshold': threshold,
            'calculation_method': f"validation_rule_{rule.get('rule_id')}",
            'result_data': {
                'rule_id': rule.get('rule_id'),
                'description': rule.get('description'),
                'condition': condition
            }
        }

    def _calculate_performance_indices(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate performance indices.

        Args:
            df: Measurements DataFrame

        Returns:
            List of performance index results
        """
        results = []

        performance_indices = self.analysis_methods.get('performance_indices', [])

        for index_config in performance_indices:
            # This is a simplified implementation
            # In practice, you'd parse and evaluate the formula
            name = index_config.get('name')
            formula = index_config.get('formula')
            unit = index_config.get('unit')

            # Placeholder for actual calculation
            calculated_value = 0.0

            results.append({
                'result_type': 'performance_index',
                'metric_name': name,
                'calculated_value': calculated_value,
                'unit': unit,
                'calculation_method': 'performance_index',
                'result_data': {
                    'formula': formula
                }
            })

        return results
