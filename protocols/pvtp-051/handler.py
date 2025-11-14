"""
PVTP-051: Reverse Current Overload Test Handler
Data processing for bypass diode and reverse bias testing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime


class ReverseCurrentHandler:
    """Handler for reverse current overload testing"""

    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.temperature_data = []
        self.current_data = []

    def process_diode_test(self, voltage_data: List[float],
                          current_data: List[float],
                          temperature_data: List[float],
                          timestamps: List[str]) -> Dict[str, Any]:
        """Process bypass diode test data"""
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(timestamps),
            'voltage': voltage_data,
            'current': current_data,
            'temperature': temperature_data
        })

        # Calculate diode resistance
        resistance = df['voltage'] / df['current']

        # Calculate power dissipation
        power = df['voltage'] * df['current']

        analysis = {
            'average_voltage': float(df['voltage'].mean()),
            'max_voltage': float(df['voltage'].max()),
            'average_temperature': float(df['temperature'].mean()),
            'max_temperature': float(df['temperature'].max()),
            'average_resistance': float(resistance.mean()),
            'average_power_dissipation': float(power.mean()),
            'max_power_dissipation': float(power.max()),
            'thermal_equilibrium': self._check_thermal_equilibrium(df['temperature']),
            'voltage_stable': bool(df['voltage'].std() < 0.05)
        }

        self.results['diode_test'] = analysis
        return analysis

    def analyze_thermal_profile(self, ir_images: List[Dict]) -> Dict[str, Any]:
        """Analyze thermal profile from IR imaging"""
        hotspots = []
        max_temps = []

        for image in ir_images:
            temps = np.array(image.get('temperature_data', []))
            if len(temps) > 0:
                avg_temp = np.mean(temps)
                max_temp = np.max(temps)
                max_temps.append(max_temp)

                # Detect hotspots (>15°C above average)
                hotspot_mask = temps > (avg_temp + 15)
                if np.any(hotspot_mask):
                    hotspots.append({
                        'timestamp': image.get('timestamp'),
                        'max_temperature': float(max_temp),
                        'hotspot_count': int(np.sum(hotspot_mask)),
                        'average_temperature': float(avg_temp)
                    })

        analysis = {
            'hotspots_detected': len(hotspots) > 0,
            'hotspot_events': hotspots,
            'max_temperature_overall': float(max(max_temps)) if max_temps else 0,
            'temperature_trend': 'increasing' if self._is_increasing(max_temps) else 'stable'
        }

        self.results['thermal_analysis'] = analysis
        return analysis

    def evaluate_reverse_current_stress(self, stress_data: Dict) -> Dict[str, Any]:
        """Evaluate module response to reverse current stress"""
        current_levels = stress_data.get('current_levels', [])

        results_by_level = []
        for level_data in current_levels:
            current = level_data.get('current')
            duration = level_data.get('duration_minutes')
            max_temp = level_data.get('max_temperature')
            diode_voltage = level_data.get('diode_voltage')

            results_by_level.append({
                'current_level': current,
                'duration_minutes': duration,
                'max_temperature': max_temp,
                'diode_voltage': diode_voltage,
                'passed': max_temp < 100 and diode_voltage < 1.0
            })

        evaluation = {
            'stress_levels_tested': len(current_levels),
            'results_by_level': results_by_level,
            'all_levels_passed': all(r['passed'] for r in results_by_level),
            'max_current_survived': max([r['current_level'] for r in results_by_level if r['passed']], default=0)
        }

        self.results['reverse_current_stress'] = evaluation
        return evaluation

    def compare_pre_post_performance(self, pre_iv: pd.DataFrame,
                                    post_iv: pd.DataFrame) -> Dict[str, Any]:
        """Compare pre-test and post-test performance"""
        pre_pmax = pre_iv['power'].max()
        post_pmax = post_iv['power'].max()

        degradation = ((pre_pmax - post_pmax) / pre_pmax) * 100

        comparison = {
            'pre_test_pmax': float(pre_pmax),
            'post_test_pmax': float(post_pmax),
            'power_degradation_percent': float(degradation),
            'degradation_acceptable': degradation < 2,
            'pre_test_voc': float(pre_iv['voltage'].max()),
            'post_test_voc': float(post_iv['voltage'].max()),
            'pre_test_isc': float(pre_iv['current'].max()),
            'post_test_isc': float(post_iv['current'].max())
        }

        self.results['performance_comparison'] = comparison
        return comparison

    def _check_thermal_equilibrium(self, temperatures: pd.Series) -> bool:
        """Check if thermal equilibrium was reached"""
        if len(temperatures) < 10:
            return False

        # Check last 10 minutes of data
        last_segment = temperatures.iloc[-10:]
        temp_change = last_segment.max() - last_segment.min()

        return temp_change < 2.0  # Less than 2°C variation

    def _is_increasing(self, values: List[float]) -> bool:
        """Check if values show increasing trend"""
        if len(values) < 2:
            return False

        # Linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        return slope > 0.5  # More than 0.5°C per measurement

    def generate_report_data(self) -> Dict[str, Any]:
        """Compile all data for report generation"""
        return {
            'protocol_id': 'PVTP-051',
            'test_date': datetime.now().isoformat(),
            'results': self.results,
            'summary': self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        diode_test = self.results.get('diode_test', {})
        thermal = self.results.get('thermal_analysis', {})
        stress = self.results.get('reverse_current_stress', {})
        performance = self.results.get('performance_comparison', {})

        overall_pass = all([
            diode_test.get('max_temperature', 999) < 100,
            diode_test.get('max_voltage', 999) < 1.0,
            not thermal.get('hotspots_detected', True),
            stress.get('all_levels_passed', False),
            performance.get('degradation_acceptable', False)
        ])

        return {
            'overall_result': 'PASS' if overall_pass else 'FAIL',
            'max_diode_temperature': diode_test.get('max_temperature'),
            'max_diode_voltage': diode_test.get('max_voltage'),
            'hotspots_detected': thermal.get('hotspots_detected'),
            'power_degradation': performance.get('power_degradation_percent'),
            'recommendation': 'Module passed reverse current test' if overall_pass else 'Module failed reverse current test'
        }
