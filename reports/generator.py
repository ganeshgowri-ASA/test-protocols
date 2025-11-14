"""Report generator for test protocol results."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class ReportGenerator:
    """Generate reports from test execution data."""

    def __init__(self, protocol_definition: Dict[str, Any]):
        """Initialize report generator.

        Args:
            protocol_definition: Protocol definition dictionary
        """
        self.protocol_def = protocol_definition
        self.report_templates = protocol_definition.get('report_templates', {})

    def generate_summary_report(
        self,
        test_execution: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> str:
        """Generate executive summary report in HTML format.

        Args:
            test_execution: Test execution data
            test_results: Test results and analysis

        Returns:
            HTML report content
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Report - {self.protocol_def['protocol_id']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .pass {{
            background-color: #27ae60;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
        }}
        .fail {{
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #34495e;
            color: white;
        }}
        .section {{
            margin: 30px 0;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #34495e;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.protocol_def['name']}</h1>
        <p>Protocol: {self.protocol_def['protocol_id']} - Version {self.protocol_def['version']}</p>
    </div>

    <div class="section">
        <h2>Test Information</h2>
        <table>
            <tr>
                <th>Test Number</th>
                <td>{test_execution.get('test_number', 'N/A')}</td>
            </tr>
            <tr>
                <th>Specimen</th>
                <td>{test_execution.get('specimen_code', 'N/A')}</td>
            </tr>
            <tr>
                <th>Operator</th>
                <td>{test_execution.get('operator_name', 'N/A')}</td>
            </tr>
            <tr>
                <th>Start Date</th>
                <td>{test_execution.get('start_datetime', 'N/A')}</td>
            </tr>
            <tr>
                <th>End Date</th>
                <td>{test_execution.get('end_datetime', 'N/A')}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Overall Result</h2>
        <div class="{'pass' if test_results.get('pass_fail', {}).get('overall_pass') else 'fail'}">
            {('PASS' if test_results.get('pass_fail', {}).get('overall_pass') else 'FAIL')}
        </div>
    </div>

    <div class="section">
        <h2>Pass/Fail Criteria Evaluation</h2>
        <table>
            <tr>
                <th>Criterion</th>
                <th>Initial Value</th>
                <th>Final Value</th>
                <th>Retention (%)</th>
                <th>Requirement</th>
                <th>Result</th>
            </tr>
"""

        # Add criteria results
        criteria_results = test_results.get('pass_fail', {}).get('criteria_results', {})
        for criterion_name, result in criteria_results.items():
            pass_status = '✅ PASS' if result.get('pass') else '❌ FAIL'
            html += f"""
            <tr>
                <td>{criterion_name.replace('_', ' ').title()}</td>
                <td>{result.get('initial_value', 'N/A')}</td>
                <td>{result.get('final_value', 'N/A')}</td>
                <td>{result.get('retention_pct', 0):.2f}%</td>
                <td>{result.get('message', 'N/A')}</td>
                <td>{pass_status}</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="section">
        <h2>Summary Statistics</h2>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Initial</th>
                <th>Final</th>
                <th>Change</th>
                <th>Change (%)</th>
                <th>Retention (%)</th>
            </tr>
"""

        # Add summary statistics
        summary_stats = test_results.get('summary_stats', {})
        for param, stats in summary_stats.items():
            html += f"""
            <tr>
                <td>{param.upper()}</td>
                <td>{stats.get('initial', 0):.3f}</td>
                <td>{stats.get('final', 0):.3f}</td>
                <td>{stats.get('change', 0):.3f}</td>
                <td>{stats.get('change_pct', 0):.2f}%</td>
                <td>{stats.get('retention_pct', 0):.2f}%</td>
            </tr>
"""

        html += f"""
        </table>
    </div>

    <div class="footer">
        <p>Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>Standard Reference: {self.protocol_def.get('standard_reference', 'N/A')}</p>
        <p>{self.protocol_def.get('author', 'PV Testing Laboratory')}</p>
    </div>
</body>
</html>
"""

        return html

    def generate_detailed_report(
        self,
        test_execution: Dict[str, Any],
        test_results: Dict[str, Any],
        measurements: List[Dict[str, Any]]
    ) -> str:
        """Generate detailed technical report.

        Args:
            test_execution: Test execution data
            test_results: Test results and analysis
            measurements: All measurement data points

        Returns:
            HTML report content
        """
        # This would be a more comprehensive report
        # For now, include the summary report plus additional sections
        summary_html = self.generate_summary_report(test_execution, test_results)

        # Add measurements section
        measurements_html = """
    <div class="section">
        <h2>Detailed Measurements</h2>
        <table>
            <tr>
                <th>Measurement Point</th>
                <th>Timestamp</th>
                <th>Parameter</th>
                <th>Value</th>
                <th>Unit</th>
            </tr>
"""

        for measurement in measurements:
            measurements_html += f"""
            <tr>
                <td>{measurement.get('measurement_point', 'N/A')}</td>
                <td>{measurement.get('timestamp', 'N/A')}</td>
                <td>{measurement.get('parameter', 'N/A')}</td>
                <td>{measurement.get('value', 'N/A')}</td>
                <td>{measurement.get('unit', 'N/A')}</td>
            </tr>
"""

        measurements_html += """
        </table>
    </div>
"""

        # Insert before footer
        detailed_html = summary_html.replace(
            '<div class="footer">',
            measurements_html + '\n    <div class="footer">'
        )

        return detailed_html

    def export_to_json(
        self,
        test_execution: Dict[str, Any],
        test_results: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        output_path: Path
    ) -> None:
        """Export test data to JSON format.

        Args:
            test_execution: Test execution data
            test_results: Test results and analysis
            measurements: All measurement data points
            output_path: Path to save JSON file
        """
        data = {
            'protocol': {
                'protocol_id': self.protocol_def['protocol_id'],
                'name': self.protocol_def['name'],
                'version': self.protocol_def['version']
            },
            'test_execution': test_execution,
            'test_results': test_results,
            'measurements': measurements,
            'export_timestamp': datetime.utcnow().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def save_report(
        self,
        html_content: str,
        output_path: Path,
        format: str = 'html'
    ) -> None:
        """Save report to file.

        Args:
            html_content: HTML report content
            output_path: Path to save report
            format: Output format ('html' or 'pdf')
        """
        if format == 'html':
            with open(output_path, 'w') as f:
                f.write(html_content)

        elif format == 'pdf':
            # PDF generation would require additional library like WeasyPrint
            # For now, save as HTML with .pdf extension suggestion
            html_path = output_path.with_suffix('.html')
            with open(html_path, 'w') as f:
                f.write(html_content)

            # Note: In production, use WeasyPrint or similar:
            # from weasyprint import HTML
            # HTML(string=html_content).write_pdf(output_path)
