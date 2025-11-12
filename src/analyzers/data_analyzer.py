"""
Data Analyzer
Analyzes protocol test data and generates results
"""

from typing import Dict, List, Any, Optional
import statistics
import json


class DataAnalyzer:
    """Analyzes protocol test data"""

    @staticmethod
    def calculate_degradation(initial: float, final: float) -> Dict[str, float]:
        """
        Calculate degradation metrics

        Returns:
            Dict with absolute_change, percentage_change, retention_rate
        """
        absolute_change = initial - final
        percentage_change = (absolute_change / initial) * 100 if initial != 0 else 0
        retention_rate = (final / initial) * 100 if initial != 0 else 0

        return {
            'initial': initial,
            'final': final,
            'absolute_change': absolute_change,
            'percentage_change': percentage_change,
            'retention_rate': retention_rate
        }

    @staticmethod
    def analyze_iv_curve(measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze I-V curve measurements

        Args:
            measurements: List of measurement dicts with pmax, voc, isc, ff

        Returns:
            Analysis results
        """
        if not measurements:
            return {'error': 'No measurements provided'}

        # Extract values
        pmax_values = [m['pmax'] for m in measurements if 'pmax' in m]
        voc_values = [m['voc'] for m in measurements if 'voc' in m]
        isc_values = [m['isc'] for m in measurements if 'isc' in m]
        ff_values = [m['ff'] for m in measurements if 'ff' in m]

        analysis = {
            'pmax': DataAnalyzer._analyze_parameter(pmax_values, 'W'),
            'voc': DataAnalyzer._analyze_parameter(voc_values, 'V'),
            'isc': DataAnalyzer._analyze_parameter(isc_values, 'A'),
            'ff': DataAnalyzer._analyze_parameter(ff_values, '')
        }

        # Calculate overall degradation
        if len(pmax_values) >= 2:
            analysis['degradation'] = DataAnalyzer.calculate_degradation(
                pmax_values[0], pmax_values[-1]
            )

        return analysis

    @staticmethod
    def _analyze_parameter(values: List[float], unit: str) -> Dict[str, Any]:
        """Analyze a single parameter"""
        if not values:
            return {'error': 'No values'}

        result = {
            'count': len(values),
            'initial': values[0],
            'final': values[-1],
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'unit': unit
        }

        if len(values) > 1:
            result['stdev'] = statistics.stdev(values)
            result['change'] = values[-1] - values[0]
            result['change_pct'] = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0

        return result

    @staticmethod
    def determine_pass_fail(degradation_pct: float, standard: str = "IEC 61215") -> Dict[str, Any]:
        """
        Determine pass/fail based on degradation and standard

        Args:
            degradation_pct: Degradation percentage (positive = loss)
            standard: Testing standard

        Returns:
            Dict with result, criteria, margin
        """
        # Define criteria by standard
        criteria_map = {
            "IEC 61215": 5.0,
            "IEC 61730": 8.0,
            "UL 1703": 10.0
        }

        max_degradation = criteria_map.get(standard, 5.0)

        passes = degradation_pct <= max_degradation
        margin = max_degradation - degradation_pct

        return {
            'result': 'PASS' if passes else 'FAIL',
            'degradation_pct': degradation_pct,
            'max_allowed_pct': max_degradation,
            'margin_pct': margin,
            'standard': standard
        }

    @staticmethod
    def analyze_thermal_cycling(measurements: List[Dict[str, Any]], num_cycles: int) -> Dict[str, Any]:
        """Analyze thermal cycling test results"""

        analysis = DataAnalyzer.analyze_iv_curve(measurements)

        # Additional thermal cycling specific analysis
        if measurements:
            # Check for intermediate measurements
            measurement_intervals = [m.get('cycle_number', 0) for m in measurements]

            analysis['test_info'] = {
                'total_cycles': num_cycles,
                'measurements_taken': len(measurements),
                'measurement_intervals': sorted(set(measurement_intervals))
            }

            # Check for visual defects
            defects = [m.get('visual_defects', '') for m in measurements if m.get('visual_defects')]
            if defects:
                analysis['defects_detected'] = defects

        return analysis

    @staticmethod
    def analyze_damp_heat(measurements: List[Dict[str, Any]], duration_hours: int) -> Dict[str, Any]:
        """Analyze damp heat test results"""

        analysis = DataAnalyzer.analyze_iv_curve(measurements)

        # Check insulation resistance trend
        insulation_values = [m.get('insulation_resistance', 0) for m in measurements if 'insulation_resistance' in m]

        if insulation_values:
            analysis['insulation_resistance'] = {
                'initial': insulation_values[0],
                'final': insulation_values[-1],
                'min': min(insulation_values),
                'passes_40mohm': all(v >= 40 for v in insulation_values),
                'values': insulation_values
            }

        analysis['test_info'] = {
            'duration_hours': duration_hours,
            'measurements_taken': len(measurements)
        }

        return analysis

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics"""
        if not values:
            return {}

        stats = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values)
        }

        if len(values) > 1:
            stats['stdev'] = statistics.stdev(values)
            stats['variance'] = statistics.variance(values)

        return stats

    @staticmethod
    def generate_recommendations(analysis: Dict[str, Any], protocol_id: str) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Check degradation
        if 'degradation' in analysis:
            deg = analysis['degradation']['percentage_change']

            if deg > 5:
                recommendations.append("⚠️ Degradation exceeds 5% - investigate root cause")
            elif deg > 3:
                recommendations.append("⚡ Degradation between 3-5% - monitor closely")
            else:
                recommendations.append("✅ Degradation within acceptable limits")

        # Protocol-specific recommendations
        if protocol_id == "PVTP-002" and 'defects_detected' in analysis:
            recommendations.append("🔍 Visual defects detected - perform detailed inspection")

        if protocol_id == "PVTP-003" and 'insulation_resistance' in analysis:
            if not analysis['insulation_resistance'].get('passes_40mohm', False):
                recommendations.append("❌ Insulation resistance below 40 MΩ - module fails safety criteria")

        # Check for measurement consistency
        if 'pmax' in analysis and 'stdev' in analysis['pmax']:
            cv = (analysis['pmax']['stdev'] / analysis['pmax']['mean']) * 100
            if cv > 10:
                recommendations.append("📊 High measurement variability - verify test conditions")

        return recommendations
