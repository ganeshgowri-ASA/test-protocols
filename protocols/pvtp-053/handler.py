"""
PVTP-053: Module Cleaning Efficiency Handler
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime


class CleaningEfficiencyHandler:
    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.baseline_power = None
        self.soiling_data = []

    def set_baseline(self, clean_power: float) -> None:
        """Set baseline clean module power"""
        self.baseline_power = clean_power

    def record_soiling_data(self, date: str, power: float, irradiance: float) -> None:
        """Record daily soiling measurements"""
        if self.baseline_power:
            soiling_ratio = power / self.baseline_power
            self.soiling_data.append({
                'date': date,
                'power': power,
                'irradiance': irradiance,
                'soiling_ratio': soiling_ratio,
                'soiling_loss_percent': (1 - soiling_ratio) * 100
            })

    def analyze_soiling_rate(self) -> Dict[str, Any]:
        """Analyze soiling accumulation rate"""
        df = pd.DataFrame(self.soiling_data)

        if len(df) < 2:
            return {'error': 'Insufficient data'}

        days = np.arange(len(df))
        soiling_loss = df['soiling_loss_percent'].values

        # Linear fit
        slope, intercept = np.polyfit(days, soiling_loss, 1)

        analysis = {
            'daily_soiling_rate': float(slope),
            'initial_soiling_loss': float(intercept),
            'final_soiling_loss': float(soiling_loss[-1]),
            'days_monitored': len(df),
            'max_soiling_loss': float(soiling_loss.max())
        }

        self.results['soiling_analysis'] = analysis
        return analysis

    def evaluate_cleaning_method(self, method: str, pre_power: float,
                                 post_power: float, resources: Dict) -> Dict[str, Any]:
        """Evaluate cleaning method effectiveness"""
        if not self.baseline_power:
            return {'error': 'Baseline power not set'}

        recovery = ((post_power - pre_power) / (self.baseline_power - pre_power)) * 100 if (self.baseline_power - pre_power) > 0 else 0
        effectiveness = (post_power / self.baseline_power) * 100

        water_used = resources.get('water_liters', 0)
        time_minutes = resources.get('time_minutes', 0)
        cost_usd = resources.get('cost_usd', 0)

        evaluation = {
            'method': method,
            'pre_cleaning_power': float(pre_power),
            'post_cleaning_power': float(post_power),
            'recovery_rate_percent': float(recovery),
            'effectiveness_percent': float(effectiveness),
            'water_usage_liters': float(water_used),
            'time_minutes': float(time_minutes),
            'cost_usd': float(cost_usd),
            'power_recovered': float(post_power - pre_power),
            'meets_criteria': recovery >= 95
        }

        if method not in self.results:
            self.results[method] = []
        self.results[method].append(evaluation)

        return evaluation

    def calculate_cost_benefit(self, method: str, electricity_price: float = 0.12) -> Dict[str, Any]:
        """Calculate cost-benefit analysis for cleaning method"""
        if method not in self.results:
            return {'error': f'No data for method {method}'}

        method_data = self.results[method]
        avg_recovery = np.mean([d['power_recovered'] for d in method_data])
        avg_cost = np.mean([d['cost_usd'] for d in method_data])

        # Annual energy value (assuming daily operation, kWh)
        daily_energy_kwh = avg_recovery * 6 / 1000  # 6 peak sun hours
        annual_energy_kwh = daily_energy_kwh * 365
        annual_value = annual_energy_kwh * electricity_price

        # Cleaning frequency (monthly for example)
        annual_cleaning_cost = avg_cost * 12

        roi = (annual_value - annual_cleaning_cost) / annual_cleaning_cost * 100 if annual_cleaning_cost > 0 else 0
        payback_months = annual_cleaning_cost / (annual_value / 12) if annual_value > 0 else 999

        analysis = {
            'method': method,
            'avg_power_recovered': float(avg_recovery),
            'avg_cleaning_cost': float(avg_cost),
            'annual_energy_value': float(annual_value),
            'annual_cleaning_cost': float(annual_cleaning_cost),
            'net_annual_benefit': float(annual_value - annual_cleaning_cost),
            'roi_percent': float(roi),
            'payback_period_months': float(payback_months),
            'cost_effective': payback_months < 6
        }

        return analysis

    def compare_methods(self) -> List[Dict[str, Any]]:
        """Compare all cleaning methods"""
        comparison = []

        for method in self.results.keys():
            if method == 'soiling_analysis':
                continue

            method_data = self.results[method]
            avg_recovery = np.mean([d['recovery_rate_percent'] for d in method_data])
            avg_cost = np.mean([d['cost_usd'] for d in method_data])
            avg_time = np.mean([d['time_minutes'] for d in method_data])

            cb_analysis = self.calculate_cost_benefit(method)

            comparison.append({
                'method': method,
                'avg_recovery_percent': float(avg_recovery),
                'avg_cost_usd': float(avg_cost),
                'avg_time_minutes': float(avg_time),
                'cost_effective': cb_analysis.get('cost_effective', False),
                'roi_percent': cb_analysis.get('roi_percent', 0)
            })

        # Rank by ROI
        comparison.sort(key=lambda x: x['roi_percent'], reverse=True)

        self.results['method_comparison'] = comparison
        return comparison

    def generate_report_data(self) -> Dict[str, Any]:
        """Generate complete report data"""
        if 'soiling_analysis' not in self.results:
            self.analyze_soiling_rate()

        if 'method_comparison' not in self.results:
            self.compare_methods()

        return {
            'protocol_id': 'PVTP-053',
            'test_date': datetime.now().isoformat(),
            'baseline_power': self.baseline_power,
            'results': self.results
        }
