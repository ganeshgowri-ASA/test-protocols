"""Report generation for test protocols."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Template, Environment, FileSystemLoader
import pandas as pd


class ReportGenerator:
    """Generates test reports in various formats."""

    def __init__(self, template_dir: str = "src/reports/templates"):
        """Initialize report generator.

        Args:
            template_dir: Directory containing report templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir / "html"))
        )

    def generate_html_report(
        self,
        test_run_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        qc_results: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """Generate HTML report.

        Args:
            test_run_data: Test run metadata and measurements
            analysis_results: Analysis results
            qc_results: QC check results
            output_path: Optional output file path

        Returns:
            HTML content as string
        """
        # Create report context
        context = {
            'test_run': test_run_data.get('test_run', {}),
            'protocol': test_run_data.get('protocol', {}),
            'analysis': analysis_results,
            'qc_results': qc_results,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_status': self._determine_overall_status(qc_results)
        }

        # Render template
        html_content = self._render_html_template(context)

        # Save to file if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(html_content)

        return html_content

    def generate_json_report(
        self,
        test_run_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        qc_results: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """Generate JSON report.

        Args:
            test_run_data: Test run metadata and measurements
            analysis_results: Analysis results
            qc_results: QC check results
            output_path: Optional output file path

        Returns:
            JSON content as string
        """
        report_data = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0',
                'report_type': 'performance_test'
            },
            'test_run': test_run_data.get('test_run', {}),
            'protocol': test_run_data.get('protocol', {}),
            'measurements': test_run_data.get('measurements', []),
            'analysis_results': analysis_results,
            'qc_results': qc_results,
            'overall_status': self._determine_overall_status(qc_results)
        }

        json_content = json.dumps(report_data, indent=2, default=str)

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(json_content)

        return json_content

    def generate_excel_report(
        self,
        test_run_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        qc_results: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """Generate Excel report with multiple sheets.

        Args:
            test_run_data: Test run metadata and measurements
            analysis_results: Analysis results
            qc_results: QC check results
            output_path: Output file path
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Summary sheet
            summary_df = self._create_summary_dataframe(
                test_run_data, analysis_results, qc_results
            )
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Measurements sheet
            measurements = test_run_data.get('measurements', [])
            if measurements:
                measurements_df = pd.DataFrame(measurements)
                measurements_df.to_excel(writer, sheet_name='Measurements', index=False)

            # Analysis results sheet
            per_irradiance = analysis_results.get('per_irradiance', [])
            if per_irradiance:
                analysis_df = pd.DataFrame(per_irradiance)
                analysis_df.to_excel(writer, sheet_name='Analysis', index=False)

            # QC results sheet
            if qc_results:
                qc_df = pd.DataFrame(qc_results)
                qc_df.to_excel(writer, sheet_name='QC Results', index=False)

    def _render_html_template(self, context: Dict[str, Any]) -> str:
        """Render HTML template with context data."""
        # Simple HTML template (can be customized)
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Report - {{ test_run.run_number }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }
        .header {
            background-color: #1f77b4;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .section {
            margin: 30px 0;
        }
        .section h2 {
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .status-pass {
            color: green;
            font-weight: bold;
        }
        .status-fail {
            color: red;
            font-weight: bold;
        }
        .status-warning {
            color: orange;
            font-weight: bold;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PV Module Performance Test Report</h1>
        <p>{{ protocol.name }}</p>
    </div>

    <div class="section">
        <h2>Test Run Information</h2>
        <table>
            <tr><th>Run Number</th><td>{{ test_run.run_number }}</td></tr>
            <tr><th>Protocol</th><td>{{ test_run.protocol_id }}</td></tr>
            <tr><th>Operator</th><td>{{ test_run.operator }}</td></tr>
            <tr><th>Module Serial</th><td>{{ test_run.module_serial }}</td></tr>
            <tr><th>Start Time</th><td>{{ test_run.start_time }}</td></tr>
            <tr><th>Status</th><td>{{ test_run.status }}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Analysis Results</h2>
        <table>
            <tr>
                <th>Irradiance (W/m²)</th>
                <th>Pmax (W)</th>
                <th>Voc (V)</th>
                <th>Isc (A)</th>
                <th>Fill Factor (%)</th>
                <th>Efficiency (%)</th>
            </tr>
            {% for result in analysis.per_irradiance %}
            <tr>
                <td>{{ result.irradiance_level }}</td>
                <td>{{ "%.2f"|format(result.pmax|default(0)) }}</td>
                <td>{{ "%.2f"|format(result.voc|default(0)) }}</td>
                <td>{{ "%.3f"|format(result.isc|default(0)) }}</td>
                <td>{{ "%.2f"|format(result.fill_factor|default(0)) }}</td>
                <td>{{ "%.2f"|format(result.efficiency|default(0)) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Quality Control Results</h2>
        <table>
            <tr>
                <th>Check Name</th>
                <th>Status</th>
                <th>Severity</th>
                <th>Message</th>
            </tr>
            {% for qc in qc_results %}
            <tr>
                <td>{{ qc.check_name }}</td>
                <td class="status-{{ qc.status }}">{{ qc.status|upper }}</td>
                <td>{{ qc.severity|default('normal') }}</td>
                <td>{{ qc.message|default('') }}</td>
            </tr>
            {% endfor %}
        </table>
        <p><strong>Overall Status:</strong>
            <span class="status-{{ overall_status }}">{{ overall_status|upper }}</span>
        </p>
    </div>

    <div class="footer">
        <p>Report generated on {{ generated_at }}</p>
        <p>PV Testing Protocol Framework v1.0</p>
    </div>
</body>
</html>
"""
        template = Template(template_str)
        return template.render(**context)

    def _create_summary_dataframe(
        self,
        test_run_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        qc_results: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Create summary dataframe for Excel report."""
        test_run = test_run_data.get('test_run', {})

        summary_data = [
            ['Run Number', test_run.get('run_number', 'N/A')],
            ['Protocol', test_run.get('protocol_id', 'N/A')],
            ['Operator', test_run.get('operator', 'N/A')],
            ['Module Serial', test_run.get('module_serial', 'N/A')],
            ['Start Time', test_run.get('start_time', 'N/A')],
            ['Status', test_run.get('status', 'N/A')],
            ['', ''],
            ['Overall QC Status', self._determine_overall_status(qc_results)]
        ]

        return pd.DataFrame(summary_data, columns=['Field', 'Value'])

    def _determine_overall_status(self, qc_results: List[Dict[str, Any]]) -> str:
        """Determine overall status from QC results."""
        if not qc_results:
            return 'na'

        statuses = [qc.get('status', 'na') for qc in qc_results]

        if 'fail' in statuses:
            return 'fail'
        elif 'warning' in statuses:
            return 'warning'
        elif all(s == 'pass' for s in statuses):
            return 'pass'
        else:
            return 'na'
