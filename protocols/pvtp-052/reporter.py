"""
PVTP-052: Partial Shading Analysis Reporter
"""

from typing import Dict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np


class PartialShadingReporter:
    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete report"""
        return {
            'summary': self.generate_summary(),
            'power_loss_analysis': self.generate_power_loss_section(),
            'thermal_analysis': self.generate_thermal_section(),
            'bypass_diode': self.generate_diode_section()
        }

    def generate_summary(self) -> str:
        """Generate executive summary"""
        tolerance = self.data.get('results', {}).get('tolerance_summary', {})
        return f"""
# Partial Shading Analysis Report

## Overall Assessment
- Patterns Tested: {tolerance.get('patterns_tested', 0)}
- Hot Spots Detected: {tolerance.get('hot_spots_detected', 0)}
- Critical Patterns: {tolerance.get('critical_patterns', 0)}
- Overall Safe: {'Yes' if tolerance.get('overall_safe') else 'No'}

## Performance Impact
- Average Power Loss: {tolerance.get('average_power_loss', 0):.1f}%
- Maximum Power Loss: {tolerance.get('max_power_loss', 0):.1f}%
"""

    def generate_power_loss_section(self) -> str:
        """Generate power loss analysis"""
        results = self.data.get('results', {})
        output = "# Power Loss Analysis\n\n"
        output += "| Pattern | Power Loss % | Max Temp | Safe |\n"
        output += "|---------|--------------|----------|------|\n"

        for pattern, data_list in results.items():
            if pattern in ['bypass_diode', 'tolerance_summary']:
                continue
            for data in data_list if isinstance(data_list, list) else [data_list]:
                output += f"| {pattern} | {data.get('power_loss_percent', 0):.1f} | "
                output += f"{data.get('max_temperature', 0):.1f}°C | "
                output += f"{'✓' if data.get('safe') else '✗'} |\n"

        return output

    def generate_thermal_section(self) -> str:
        """Generate thermal analysis section"""
        return "# Thermal Analysis\n\nSee IR thermography images in appendix."

    def generate_diode_section(self) -> str:
        """Generate bypass diode section"""
        diode = self.data.get('results', {}).get('bypass_diode', {})
        return f"""
# Bypass Diode Performance

- Activation: {'Yes' if diode.get('diode_activated') else 'No'}
- Diode Voltage: {diode.get('diode_voltage', 0):.3f} V
- Current Bypass: {diode.get('current_bypass', 0):.2f} A
- Proper Operation: {'Yes' if diode.get('proper_operation') else 'No'}
"""
