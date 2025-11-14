"""
Report generation utilities for test protocols
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class ReportGenerator:
    """Generates test reports in various formats"""

    def __init__(self, protocol_data: Dict[str, Any], test_data: Dict[str, Any],
                 analysis_results: Dict[str, Any], pass_fail_results: Dict[str, Any]):
        """
        Initialize report generator

        Args:
            protocol_data: Protocol definition
            test_data: Test execution data
            analysis_results: Analysis results
            pass_fail_results: Pass/fail evaluation
        """
        self.protocol_data = protocol_data
        self.test_data = test_data
        self.analysis_results = analysis_results
        self.pass_fail_results = pass_fail_results

    def generate_json_report(self, output_path: str) -> None:
        """
        Generate complete JSON report

        Args:
            output_path: Path to output JSON file
        """
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0.0',
                'protocol_id': self.protocol_data['protocol_id'],
                'protocol_version': self.protocol_data['version']
            },
            'test_identification': {
                'test_date': self.test_data.get('test_date', ''),
                'test_operator': self.test_data.get('test_operator', ''),
                'facility': self.test_data.get('facility', '')
            },
            'module_information': self.test_data.get('module_info', {}),
            'test_data': self.test_data,
            'analysis_results': self.analysis_results,
            'pass_fail_evaluation': self.pass_fail_results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    def generate_markdown_report(self) -> str:
        """
        Generate markdown formatted report

        Returns:
            Markdown report string
        """
        lines = []

        # Header
        lines.append(f"# {self.protocol_data['title']}")
        lines.append(f"## Test Report - {self.protocol_data['protocol_id']}")
        lines.append("")

        # Test identification
        lines.append("## Test Identification")
        lines.append(f"- **Test Date**: {self.test_data.get('test_date', 'N/A')}")
        lines.append(f"- **Operator**: {self.test_data.get('test_operator', 'N/A')}")
        lines.append(f"- **Protocol Version**: {self.protocol_data['version']}")
        lines.append(f"- **Standard**: {self.protocol_data['standard']['name']}")
        lines.append("")

        # Module information
        module_info = self.test_data.get('module_info', {})
        lines.append("## Module Information")
        lines.append(f"- **Manufacturer**: {module_info.get('manufacturer', 'N/A')}")
        lines.append(f"- **Model**: {module_info.get('model', 'N/A')}")
        lines.append(f"- **Serial Number**: {module_info.get('serial_number', 'N/A')}")
        lines.append(f"- **Nameplate Power**: {module_info.get('nameplate_power', 'N/A')} W")
        lines.append("")

        # Test results summary
        lines.append("## Test Results Summary")
        overall = self.pass_fail_results.get('overall_result', 'UNKNOWN')
        lines.append(f"### Overall Result: **{overall}**")
        lines.append("")

        # Pass/Fail criteria
        lines.append("### Pass/Fail Criteria Evaluation")
        lines.append("")
        criteria = self.pass_fail_results.get('criteria', {})
        for criterion_name, criterion_data in criteria.items():
            status = "✓ PASS" if criterion_data['pass'] else "✗ FAIL"
            lines.append(f"**{criterion_name.replace('_', ' ').title()}**: {status}")
            lines.append(f"- {criterion_data['description']}")
            if 'value' in criterion_data:
                lines.append(f"- Value: {criterion_data['value']}")
            if 'threshold' in criterion_data:
                unit = criterion_data.get('unit', '')
                lines.append(f"- Threshold: {criterion_data['threshold']} {unit}")
            lines.append("")

        # Analysis results
        lines.append("## Analysis Results")
        lines.append("")

        # Power analysis
        if 'power_analysis' in self.analysis_results:
            power = self.analysis_results['power_analysis']
            lines.append("### Power Analysis")
            lines.append(f"- **Initial Pmax**: {power.get('Pmax_initial', 0)} W")
            lines.append(f"- **Final Pmax**: {power.get('Pmax_final', 0)} W")
            lines.append(f"- **Degradation**: {power.get('degradation_percent', 0)}%")
            lines.append(f"- **Power Loss**: {power.get('degradation_watts', 0)} W")
            lines.append("")

        # Impact analysis
        if 'impact_analysis' in self.analysis_results:
            impact = self.analysis_results['impact_analysis']
            lines.append("### Impact Test Analysis")
            lines.append(f"- **Total Impacts**: {impact.get('total_impacts', 0)}")
            lines.append(f"- **Mean Velocity**: {impact.get('velocity_mean', 0)} km/h")
            lines.append(f"- **Velocity Std Dev**: {impact.get('velocity_std', 0)} km/h")
            lines.append(f"- **Time Compliance**: {impact.get('time_compliance_count', 0)}/{impact.get('total_impacts', 0)}")
            lines.append(f"- **Open Circuit Detected**: {impact.get('open_circuit_detected', False)}")
            lines.append("")

        # Visual analysis
        if 'visual_analysis' in self.analysis_results:
            visual = self.analysis_results['visual_analysis']
            lines.append("### Visual Inspection Results")
            lines.append(f"- **Front Glass Cracks**: {'Yes' if visual.get('front_glass_cracks') else 'No'}")
            lines.append(f"- **Cell Cracks**: {'Yes' if visual.get('cell_cracks') else 'No'}")
            lines.append(f"- **Backsheet Cracks**: {'Yes' if visual.get('backsheet_cracks') else 'No'}")
            lines.append(f"- **Delamination**: {'Yes' if visual.get('delamination') else 'No'}")
            lines.append(f"- **Junction Box Damage**: {'Yes' if visual.get('junction_box_damage') else 'No'}")
            lines.append("")

        # Insulation analysis
        if 'insulation_analysis' in self.analysis_results:
            insulation = self.analysis_results['insulation_analysis']
            lines.append("### Insulation Resistance")
            lines.append(f"- **Initial**: {insulation.get('initial_resistance', 0)} MΩ")
            lines.append(f"- **Final**: {insulation.get('final_resistance', 0)} MΩ")
            lines.append(f"- **Degradation**: {insulation.get('degradation_percent', 0)}%")
            lines.append(f"- **Meets Minimum**: {'Yes' if insulation.get('meets_minimum') else 'No'}")
            lines.append("")

        return "\n".join(lines)

    def generate_summary_table(self) -> List[Dict[str, Any]]:
        """
        Generate summary data for table display

        Returns:
            List of row dictionaries
        """
        rows = []

        criteria = self.pass_fail_results.get('criteria', {})
        for criterion_name, criterion_data in criteria.items():
            row = {
                'Criterion': criterion_name.replace('_', ' ').title(),
                'Result': 'PASS' if criterion_data['pass'] else 'FAIL',
                'Value': str(criterion_data.get('value', 'N/A')),
                'Threshold': f"{criterion_data.get('threshold', '')} {criterion_data.get('unit', '')}".strip(),
                'Description': criterion_data.get('description', '')
            }
            rows.append(row)

        return rows

    def generate_impact_data_table(self) -> List[Dict[str, Any]]:
        """
        Generate impact test data table

        Returns:
            List of impact data rows
        """
        impacts = self.test_data.get('test_execution_data', {}).get('impacts', [])

        rows = []
        for impact in impacts:
            row = {
                'Impact #': impact.get('impact_number', ''),
                'Location': impact.get('impact_location', ''),
                'Velocity (km/h)': impact.get('actual_velocity_kmh', 0),
                'Time (s)': impact.get('time_delta_seconds', 0),
                'Open Circuit': 'Yes' if impact.get('open_circuit_detected', False) else 'No',
                'Visual Damage': impact.get('visual_damage', 'None')
            }
            rows.append(row)

        return rows
