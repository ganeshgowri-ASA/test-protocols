"""
PVTP-051: Reverse Current Overload Test Reporter
Report generation for reverse current testing
"""

from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from datetime import datetime


class ReverseCurrentReporter:
    """Reporter for reverse current overload testing"""

    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete report"""
        reports = {}
        reports['summary'] = self.generate_summary()
        reports['thermal_analysis'] = self.generate_thermal_section()
        reports['diode_analysis'] = self.generate_diode_section()
        reports['performance'] = self.generate_performance_section()
        return reports

    def generate_summary(self) -> str:
        """Generate executive summary"""
        summary = self.data.get('summary', {})
        return f"""
# Reverse Current Overload Test Report

## Overall Result: {summary.get('overall_result', 'N/A')}

## Key Findings
- Max Diode Temperature: {summary.get('max_diode_temperature', 'N/A')}°C
- Max Diode Voltage: {summary.get('max_diode_voltage', 'N/A')}V
- Hotspots Detected: {'Yes' if summary.get('hotspots_detected') else 'No'}
- Power Degradation: {summary.get('power_degradation', 'N/A'):.2f}%

## Recommendation
{summary.get('recommendation', 'See detailed analysis')}
"""

    def generate_thermal_section(self) -> str:
        """Generate thermal analysis section"""
        thermal = self.data.get('results', {}).get('thermal_analysis', {})
        return f"""
# Thermal Analysis

## IR Thermography Results
- Max Temperature: {thermal.get('max_temperature_overall', 'N/A')}°C
- Hotspots Detected: {'Yes' if thermal.get('hotspots_detected') else 'No'}
- Temperature Trend: {thermal.get('temperature_trend', 'N/A')}

## Hotspot Events
{self._format_hotspots(thermal.get('hotspot_events', []))}
"""

    def generate_diode_section(self) -> str:
        """Generate bypass diode analysis section"""
        diode = self.data.get('results', {}).get('diode_test', {})
        return f"""
# Bypass Diode Performance

## Electrical Characteristics
- Average Voltage: {diode.get('average_voltage', 'N/A'):.3f} V
- Max Voltage: {diode.get('max_voltage', 'N/A'):.3f} V
- Average Resistance: {diode.get('average_resistance', 'N/A'):.4f} Ω

## Thermal Performance
- Average Temperature: {diode.get('average_temperature', 'N/A'):.1f}°C
- Max Temperature: {diode.get('max_temperature', 'N/A'):.1f}°C
- Thermal Equilibrium: {'Yes' if diode.get('thermal_equilibrium') else 'No'}

## Power Dissipation
- Average: {diode.get('average_power_dissipation', 'N/A'):.2f} W
- Maximum: {diode.get('max_power_dissipation', 'N/A'):.2f} W
"""

    def generate_performance_section(self) -> str:
        """Generate performance comparison section"""
        perf = self.data.get('results', {}).get('performance_comparison', {})
        return f"""
# Performance Comparison (Pre/Post Test)

## Power Output
- Pre-test Pmax: {perf.get('pre_test_pmax', 'N/A'):.2f} W
- Post-test Pmax: {perf.get('post_test_pmax', 'N/A'):.2f} W
- Degradation: {perf.get('power_degradation_percent', 'N/A'):.2f}%
- Acceptable: {'Yes' if perf.get('degradation_acceptable') else 'No'}

## IV Parameters
- Pre Voc: {perf.get('pre_test_voc', 'N/A'):.2f} V → Post Voc: {perf.get('post_test_voc', 'N/A'):.2f} V
- Pre Isc: {perf.get('pre_test_isc', 'N/A'):.2f} A → Post Isc: {perf.get('post_test_isc', 'N/A'):.2f} A
"""

    def _format_hotspots(self, hotspots: List[Dict]) -> str:
        """Format hotspot events"""
        if not hotspots:
            return "No hotspot events detected"

        output = "| Timestamp | Max Temp (°C) | Hotspot Count | Avg Temp (°C) |\n"
        output += "|-----------|---------------|---------------|---------------|\n"
        for h in hotspots:
            output += f"| {h.get('timestamp', 'N/A')} | {h.get('max_temperature', 0):.1f} | "
            output += f"{h.get('hotspot_count', 0)} | {h.get('average_temperature', 0):.1f} |\n"
        return output
