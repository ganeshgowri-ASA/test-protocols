"""
Report Generator
Creates reports in various formats (PDF, Excel, Word, HTML)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class ReportGenerator:
    """Generates test reports in various formats"""

    def __init__(self, output_dir: str = "data/reports"):
        """
        Initialize report generator

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_test_report(
        self,
        execution_data: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        report_format: str = "pdf",
        template: str = "standard"
    ) -> str:
        """
        Generate test report

        Args:
            execution_data: Protocol execution data
            measurements: List of measurements
            analysis: Analysis results
            report_format: Output format (pdf, excel, word, html)
            template: Report template to use

        Returns:
            Path to generated report file
        """
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = f"{report_id}_{execution_data.get('protocol_id', 'UNKNOWN')}.{report_format}"
        filepath = self.output_dir / filename

        # Generate report content
        content = self._build_report_content(execution_data, measurements, analysis)

        # Format-specific generation
        if report_format == "html":
            html_content = self._generate_html(content, template)
            with open(filepath, 'w') as f:
                f.write(html_content)

        elif report_format == "json":
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2, default=str)

        else:
            # For PDF, Excel, Word - create placeholder
            # In production, use libraries like reportlab, openpyxl, python-docx
            with open(filepath, 'w') as f:
                f.write(f"Report: {report_id}\n")
                f.write(f"Format: {report_format}\n")
                f.write(json.dumps(content, indent=2, default=str))

        return str(filepath)

    def _build_report_content(
        self,
        execution_data: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build report content structure"""

        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'Test Report',
                'protocol_id': execution_data.get('protocol_id'),
                'protocol_name': execution_data.get('protocol_name'),
                'execution_id': execution_data.get('execution_id')
            },
            'test_information': {
                'sample_id': execution_data.get('sample_id'),
                'start_date': execution_data.get('start_date'),
                'end_date': execution_data.get('end_date'),
                'operator': execution_data.get('operator_id'),
                'equipment_id': execution_data.get('equipment_id')
            },
            'protocol_inputs': json.loads(execution_data.get('protocol_inputs', '{}')),
            'measurements': {
                'count': len(measurements),
                'data': measurements
            },
            'analysis': analysis,
            'result': {
                'status': execution_data.get('status'),
                'test_result': execution_data.get('test_result'),
                'overall_grade': execution_data.get('overall_grade')
            }
        }

    def _generate_html(self, content: Dict[str, Any], template: str) -> str:
        """Generate HTML report"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {content['report_metadata']['protocol_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #1f77b4; }}
        h2 {{ color: #333; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #1f77b4; color: white; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .info-box {{ background-color: #f0f0f0; padding: 15px; margin: 10px 0; border-left: 4px solid #1f77b4; }}
    </style>
</head>
<body>
    <h1>PV Testing Protocol Report</h1>

    <div class="info-box">
        <h3>{content['report_metadata']['protocol_name']}</h3>
        <p><strong>Protocol ID:</strong> {content['report_metadata']['protocol_id']}</p>
        <p><strong>Execution ID:</strong> {content['report_metadata']['execution_id']}</p>
        <p><strong>Generated:</strong> {content['report_metadata']['generated_at']}</p>
    </div>

    <h2>Test Information</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>Sample ID</td><td>{content['test_information'].get('sample_id', 'N/A')}</td></tr>
        <tr><td>Start Date</td><td>{content['test_information'].get('start_date', 'N/A')}</td></tr>
        <tr><td>End Date</td><td>{content['test_information'].get('end_date', 'N/A')}</td></tr>
        <tr><td>Equipment ID</td><td>{content['test_information'].get('equipment_id', 'N/A')}</td></tr>
    </table>

    <h2>Test Results</h2>
    <div class="info-box">
        <p><strong>Status:</strong> {content['result'].get('status', 'N/A')}</p>
        <p><strong>Result:</strong> <span class="{content['result'].get('test_result', 'unknown').lower()}">{content['result'].get('test_result', 'N/A')}</span></p>
    </div>

    <h2>Measurements</h2>
    <p>Total measurements: {content['measurements']['count']}</p>

    <h2>Analysis</h2>
    <pre>{json.dumps(content['analysis'], indent=2)}</pre>

    <footer>
        <hr>
        <p>PV Testing Protocol System | Report generated automatically</p>
    </footer>
</body>
</html>
"""
        return html

    def generate_certificate(
        self,
        execution_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate test certificate (only for passed tests)"""

        if execution_data.get('test_result') != 'pass':
            raise ValueError("Certificate can only be generated for passed tests")

        cert_id = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = f"{cert_id}.html"
        filepath = self.output_dir / filename

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Certificate</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 0; padding: 40px; text-align: center; }}
        .certificate {{ border: 10px double #1f77b4; padding: 40px; margin: 20px; }}
        h1 {{ font-size: 36px; color: #1f77b4; margin: 20px 0; }}
        .cert-body {{ margin: 30px 0; text-align: left; }}
        .signature {{ margin-top: 60px; }}
    </style>
</head>
<body>
    <div class="certificate">
        <h1>CERTIFICATE OF COMPLIANCE</h1>

        <div class="cert-body">
            <p><strong>Certificate No:</strong> {cert_id}</p>
            <p><strong>Issue Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>

            <p style="margin-top: 30px;">This is to certify that the photovoltaic module:</p>

            <p style="margin-left: 40px;">
                <strong>Sample ID:</strong> {execution_data.get('sample_id')}<br>
                <strong>Protocol:</strong> {execution_data.get('protocol_name')}<br>
                <strong>Test Standard:</strong> IEC 61215
            </p>

            <p>Has been tested and found to be in compliance with the specified requirements.</p>

            <p style="margin-top: 30px;">
                <strong>Test Result:</strong> PASS<br>
                <strong>Execution ID:</strong> {execution_data.get('execution_id')}
            </p>
        </div>

        <div class="signature">
            <p>_______________________</p>
            <p>Authorized Signature</p>
            <p>PV Testing Laboratory</p>
        </div>
    </div>
</body>
</html>
"""

        with open(filepath, 'w') as f:
            f.write(html)

        return str(filepath)
