"""
PVTP-052: Partial Shading Analysis Handler
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime


class PartialShadingHandler:
    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.baseline_power = None

    def set_baseline(self, iv_data: pd.DataFrame) -> float:
        """Set baseline power from unshaded test"""
        self.baseline_power = iv_data['power'].max()
        return self.baseline_power

    def analyze_shading_pattern(self, pattern_name: str, iv_data: pd.DataFrame,
                               ir_data: Dict) -> Dict[str, Any]:
        """Analyze a specific shading pattern"""
        power = iv_data['power'].max()
        power_loss = ((self.baseline_power - power) / self.baseline_power) * 100 if self.baseline_power else 0

        # Analyze IR data for hot spots
        temps = np.array(ir_data.get('temperature_data', []))
        avg_temp = np.mean(temps) if len(temps) > 0 else 0
        max_temp = np.max(temps) if len(temps) > 0 else 0
        hot_spot_detected = (max_temp - avg_temp) > 20

        analysis = {
            'pattern': pattern_name,
            'power_output': float(power),
            'power_loss_percent': float(power_loss),
            'max_temperature': float(max_temp),
            'avg_temperature': float(avg_temp),
            'hot_spot_detected': hot_spot_detected,
            'temperature_rise': float(max_temp - avg_temp),
            'safe': max_temp < 85 and (max_temp - avg_temp) < 20
        }

        if pattern_name not in self.results:
            self.results[pattern_name] = []
        self.results[pattern_name].append(analysis)

        return analysis

    def verify_bypass_diode(self, shaded_string_data: Dict) -> Dict[str, Any]:
        """Verify bypass diode activation"""
        diode_voltage = shaded_string_data.get('diode_voltage', 0)
        current_bypass = shaded_string_data.get('current_through_diode', 0)

        verification = {
            'diode_activated': diode_voltage > 0.3 and diode_voltage < 1.0,
            'diode_voltage': float(diode_voltage),
            'current_bypass': float(current_bypass),
            'proper_operation': diode_voltage < 1.0 and current_bypass > 0
        }

        self.results['bypass_diode'] = verification
        return verification

    def calculate_shading_tolerance(self) -> Dict[str, Any]:
        """Calculate overall shading tolerance"""
        all_patterns = []
        for pattern, data_list in self.results.items():
            if pattern != 'bypass_diode':
                for data in data_list:
                    all_patterns.append(data)

        critical_patterns = [p for p in all_patterns if not p.get('safe', True)]
        avg_power_loss = np.mean([p['power_loss_percent'] for p in all_patterns]) if all_patterns else 0

        tolerance = {
            'patterns_tested': len(all_patterns),
            'critical_patterns': len(critical_patterns),
            'average_power_loss': float(avg_power_loss),
            'max_power_loss': float(max([p['power_loss_percent'] for p in all_patterns])) if all_patterns else 0,
            'hot_spots_detected': sum(1 for p in all_patterns if p.get('hot_spot_detected')),
            'overall_safe': len(critical_patterns) == 0
        }

        self.results['tolerance_summary'] = tolerance
        return tolerance

    def generate_report_data(self) -> Dict[str, Any]:
        """Generate report data"""
        if 'tolerance_summary' not in self.results:
            self.calculate_shading_tolerance()

        return {
            'protocol_id': 'PVTP-052',
            'test_date': datetime.now().isoformat(),
            'baseline_power': self.baseline_power,
            'results': self.results
        }
