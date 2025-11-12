"""
Report Generator
Automated report generation in multiple formats with charts and audit trails
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json


class ReportGenerator:
    """
    Base report generator for test protocols
    Generates reports in PDF, Excel, JSON, and HTML formats
    """

    def __init__(self, protocol_data: Dict[str, Any], config: Optional[Dict] = None):
        """
        Initialize report generator

        Args:
            protocol_data: Complete protocol execution data
            config: Optional configuration
        """
        self.protocol_data = protocol_data
        self.config = config or {}

        self.protocol_def = protocol_data.get("protocolDefinition", {})
        self.summary = protocol_data.get("summary", {})
        self.measurements = protocol_data.get("measurements", {})
        self.time_series = protocol_data.get("timeSeriesData", [])
        self.images = protocol_data.get("images", [])
        self.approvals = protocol_data.get("approvals", [])
        self.audit_log = protocol_data.get("auditLog", [])

    def generate(self, formats: Optional[List[str]] = None) -> Dict[str, bytes]:
        """
        Generate reports in requested formats

        Args:
            formats: List of formats ('pdf', 'excel', 'json', 'html')

        Returns:
            Dictionary mapping format to report bytes
        """
        formats = formats or ['pdf', 'excel', 'json']
        reports = {}

        for fmt in formats:
            if fmt == 'json':
                reports['json'] = self.generate_json()
            elif fmt == 'pdf':
                reports['pdf'] = self.generate_pdf()
            elif fmt == 'excel':
                reports['excel'] = self.generate_excel()
            elif fmt == 'html':
                reports['html'] = self.generate_html()

        return reports

    def generate_json(self) -> bytes:
        """Generate JSON report"""
        report = {
            "reportMetadata": {
                "generated": datetime.now().isoformat(),
                "protocolId": self.protocol_def.get("protocolId"),
                "protocolName": self.protocol_def.get("protocolName"),
                "sessionId": self.summary.get("sessionId"),
                "reportVersion": "1.0.0"
            },
            "summary": self.summary,
            "deviceUnderTest": self.protocol_def.get("deviceUnderTest"),
            "testParameters": self.protocol_def.get("testParameters"),
            "acceptanceCriteria": self.protocol_def.get("acceptanceCriteria"),
            "measurements": self.measurements,
            "result": self.summary.get("result"),
            "approvals": self.approvals,
            "auditLog": self.audit_log if self.config.get("includeAuditTrail", True) else [],
            "timeSeriesDataPoints": len(self.time_series),
            "imagesCaptured": len(self.images)
        }

        return json.dumps(report, indent=2).encode('utf-8')

    def generate_pdf(self) -> bytes:
        """
        Generate PDF report
        Would use ReportLab or similar library in production
        """
        # This is a placeholder - production would use ReportLab
        report_text = self._generate_report_text()

        return f"""
PDF REPORT PLACEHOLDER
======================

{report_text}

This would be a formatted PDF with:
- Cover page with protocol info
- Executive summary
- Test parameters and conditions
- Measurement results with charts
- Pass/fail analysis
- Approval signatures
- Audit trail
- Appendices with images

Generated: {datetime.now().isoformat()}
""".encode('utf-8')

    def generate_excel(self) -> bytes:
        """
        Generate Excel report
        Would use openpyxl or similar library in production
        """
        # Placeholder - production would use openpyxl
        return b"Excel report placeholder with raw data tables"

    def generate_html(self) -> bytes:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.protocol_def.get('protocolName')} - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #003366; color: white; padding: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ccc; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.protocol_def.get('protocolName')}</h1>
        <p>Protocol ID: {self.protocol_def.get('protocolId')}</p>
        <p>Session ID: {self.summary.get('sessionId')}</p>
    </div>

    <div class="section">
        <h2>Test Summary</h2>
        <p><strong>Result:</strong> <span class="{self.summary.get('result')}">{self.summary.get('result', '').upper()}</span></p>
        <p><strong>Start Time:</strong> {self.summary.get('startTime')}</p>
        <p><strong>End Time:</strong> {self.summary.get('endTime')}</p>
        <p><strong>Duration:</strong> {self.summary.get('duration')} seconds</p>
        <p><strong>Operator:</strong> {self.summary.get('operator')}</p>
    </div>

    <div class="section">
        <h2>Device Under Test</h2>
        {self._format_device_info()}
    </div>

    <div class="section">
        <h2>Measurements</h2>
        {self._format_measurements_table()}
    </div>

    <div class="section">
        <h2>Approvals</h2>
        {self._format_approvals_table()}
    </div>

    <div class="section">
        <h2>Audit Trail</h2>
        <p>Total audit entries: {len(self.audit_log)}</p>
    </div>

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc;">
        <p>Report generated: {datetime.now().isoformat()}</p>
        <p>PV Testing Protocol Framework v1.0</p>
    </footer>
</body>
</html>
"""
        return html.encode('utf-8')

    def _generate_report_text(self) -> str:
        """Generate plain text report content"""
        lines = []
        lines.append(f"Protocol: {self.protocol_def.get('protocolName')}")
        lines.append(f"ID: {self.protocol_def.get('protocolId')}")
        lines.append(f"Session: {self.summary.get('sessionId')}")
        lines.append(f"Result: {self.summary.get('result', '').upper()}")
        lines.append("")
        lines.append("Measurements:")
        for name, measurement in self.measurements.items():
            lines.append(f"  {name}: {measurement.get('value')} {measurement.get('unit')}")

        return "\n".join(lines)

    def _format_device_info(self) -> str:
        """Format device info as HTML"""
        dut = self.protocol_def.get("deviceUnderTest", {})
        ident = dut.get("identification", {})

        return f"""
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Serial Number</td><td>{ident.get('serialNumber', 'N/A')}</td></tr>
            <tr><td>Model Number</td><td>{ident.get('modelNumber', 'N/A')}</td></tr>
            <tr><td>Manufacturer</td><td>{ident.get('manufacturer', 'N/A')}</td></tr>
        </table>
        """

    def _format_measurements_table(self) -> str:
        """Format measurements as HTML table"""
        if not self.measurements:
            return "<p>No measurements recorded</p>"

        rows = []
        for name, measurement in self.measurements.items():
            rows.append(f"""
            <tr>
                <td>{name}</td>
                <td>{measurement.get('value')}</td>
                <td>{measurement.get('unit')}</td>
                <td>{measurement.get('timestamp')}</td>
            </tr>
            """)

        return f"""
        <table>
            <tr><th>Measurement</th><th>Value</th><th>Unit</th><th>Timestamp</th></tr>
            {''.join(rows)}
        </table>
        """

    def _format_approvals_table(self) -> str:
        """Format approvals as HTML table"""
        if not self.approvals:
            return "<p>No approvals recorded</p>"

        rows = []
        for approval in self.approvals:
            status = "✓ Approved" if approval.get("approved") else "✗ Rejected"
            rows.append(f"""
            <tr>
                <td>{approval.get('gateId')}</td>
                <td>{status}</td>
                <td>{approval.get('approver')}</td>
                <td>{approval.get('timestamp')}</td>
                <td>{approval.get('comments', '')}</td>
            </tr>
            """)

        return f"""
        <table>
            <tr><th>Gate</th><th>Status</th><th>Approver</th><th>Timestamp</th><th>Comments</th></tr>
            {''.join(rows)}
        </table>
        """


class CertificationReportGenerator(ReportGenerator):
    """
    Specialized report generator for certification-compliant reports
    Includes all requirements for IEC/UL certification submission
    """

    def generate_certification_package(self) -> Dict[str, bytes]:
        """
        Generate complete certification package

        Returns:
            Dictionary of all required certification documents
        """
        package = {}

        # Main test report
        package['test_report.pdf'] = self.generate_pdf()

        # Raw data
        package['raw_data.json'] = self.generate_json()
        package['raw_data.xlsx'] = self.generate_excel()

        # Certificate of conformity (if passed)
        if self.summary.get('result') == 'pass':
            package['certificate_of_conformity.pdf'] = self._generate_certificate()

        # Audit trail
        package['audit_trail.json'] = self._generate_audit_trail_report()

        # Calibration certificates (references)
        package['calibration_references.json'] = self._generate_calibration_references()

        return package

    def _generate_certificate(self) -> bytes:
        """Generate certificate of conformity"""
        cert_text = f"""
CERTIFICATE OF CONFORMITY

Protocol: {self.protocol_def.get('protocolName')}
Standard: {self.protocol_def.get('standard', {}).get('name')}
Section: {self.protocol_def.get('standard', {}).get('section')}

Device: {self.protocol_def.get('deviceUnderTest', {}).get('identification', {}).get('serialNumber')}

Result: PASS

This certifies that the above device has been tested in accordance with
{self.protocol_def.get('standard', {}).get('name')} and meets all requirements.

Date: {datetime.now().strftime('%Y-%m-%d')}
Test Laboratory: [Laboratory Name]
Authorized Signature: _____________________
"""
        return cert_text.encode('utf-8')

    def _generate_audit_trail_report(self) -> bytes:
        """Generate detailed audit trail report"""
        audit_report = {
            "protocolId": self.protocol_def.get("protocolId"),
            "sessionId": self.summary.get("sessionId"),
            "auditTrail": self.audit_log,
            "traceability": {
                "dataLineage": "complete",
                "approvalChain": self.approvals,
                "modifications": []
            }
        }

        return json.dumps(audit_report, indent=2).encode('utf-8')

    def _generate_calibration_references(self) -> bytes:
        """Generate calibration references document"""
        cal_refs = {
            "sessionId": self.summary.get("sessionId"),
            "calibrationRecords": [
                {
                    "equipment": "placeholder",
                    "calibrationDate": "placeholder",
                    "certificateNumber": "placeholder",
                    "dueDate": "placeholder"
                }
            ]
        }

        return json.dumps(cal_refs, indent=2).encode('utf-8')
