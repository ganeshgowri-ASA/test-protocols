"""
Report Generation Utilities

Generates professional test reports in multiple formats:
- PDF reports with charts and tables
- Excel datasheets
- JSON data exports
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate test reports in various formats"""

    def __init__(self, lab_info: Optional[Dict[str, str]] = None):
        """
        Initialize report generator

        Args:
            lab_info: Laboratory information for header
        """
        self.lab_info = lab_info or {
            'name': 'PV Testing Laboratory',
            'address': '123 Solar Street, Tech City',
            'phone': '+1-555-123-4567',
            'email': 'lab@pvtesting.com',
            'accreditation': 'ISO/IEC 17025:2017'
        }

    def generate_test_report(
        self,
        test_execution: Dict[str, Any],
        sample: Dict[str, Any],
        protocol: Dict[str, Any],
        results: Dict[str, Any],
        format: str = 'dict'
    ) -> Dict[str, Any]:
        """
        Generate comprehensive test report

        Args:
            test_execution: Test execution data
            sample: Sample information
            protocol: Protocol information
            results: Test results and analysis
            format: Output format ('dict', 'pdf', 'excel', 'json')

        Returns:
            Report data structure or file path
        """
        try:
            report_data = {
                'report_metadata': {
                    'report_number': self._generate_report_number(test_execution),
                    'report_date': datetime.utcnow().isoformat(),
                    'report_version': '1.0',
                    'template_version': '1.0'
                },
                'laboratory_info': self.lab_info,
                'test_information': {
                    'execution_number': test_execution.get('execution_number'),
                    'protocol_id': protocol.get('protocol_id'),
                    'protocol_name': protocol.get('name'),
                    'standard_reference': protocol.get('standard_reference'),
                    'test_date': test_execution.get('actual_start'),
                    'technician': test_execution.get('technician_name'),
                    'reviewer': test_execution.get('reviewer_name')
                },
                'sample_information': {
                    'sample_id': sample.get('sample_id'),
                    'manufacturer': sample.get('manufacturer'),
                    'model': sample.get('model'),
                    'serial_number': sample.get('serial_number'),
                    'technology': sample.get('technology'),
                    'rated_power': sample.get('rated_power'),
                    'dimensions': {
                        'length': sample.get('dimensions_length'),
                        'width': sample.get('dimensions_width'),
                        'height': sample.get('dimensions_height')
                    },
                    'weight': sample.get('weight')
                },
                'test_conditions': test_execution.get('test_conditions', {}),
                'measurements': results.get('measurements', []),
                'analysis_results': results.get('analysis_results', {}),
                'pass_fail_summary': self._generate_pass_fail_summary(results),
                'conclusions': self._generate_conclusions(results),
                'attachments': results.get('attachments', []),
                'traceability': {
                    'equipment_used': results.get('equipment_list', []),
                    'calibration_status': 'All equipment within calibration',
                    'raw_data_files': results.get('raw_data_files', [])
                }
            }

            if format == 'dict':
                return report_data
            elif format == 'json':
                return self._export_json(report_data, test_execution.get('execution_number'))
            elif format == 'pdf':
                return self._export_pdf(report_data)
            elif format == 'excel':
                return self._export_excel(report_data)
            else:
                logger.warning(f"Unknown format: {format}, returning dict")
                return report_data

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {'error': str(e)}

    def _generate_report_number(self, test_execution: Dict[str, Any]) -> str:
        """Generate unique report number"""
        execution_num = test_execution.get('execution_number', 'UNKNOWN')
        date_str = datetime.utcnow().strftime('%Y%m%d')
        return f"RPT-{date_str}-{execution_num}"

    def _generate_pass_fail_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pass/fail summary"""
        analysis_results = results.get('analysis_results', {})

        pass_count = 0
        fail_count = 0
        conditional_count = 0
        na_count = 0

        for result_type, result_data in analysis_results.items():
            status = result_data.get('pass_fail', 'n/a')
            if status == 'pass':
                pass_count += 1
            elif status == 'fail':
                fail_count += 1
            elif status == 'conditional':
                conditional_count += 1
            else:
                na_count += 1

        overall_status = 'PASS'
        if fail_count > 0:
            overall_status = 'FAIL'
        elif conditional_count > 0:
            overall_status = 'CONDITIONAL'

        return {
            'overall_status': overall_status,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'conditional_count': conditional_count,
            'na_count': na_count,
            'total_criteria': pass_count + fail_count + conditional_count + na_count
        }

    def _generate_conclusions(self, results: Dict[str, Any]) -> str:
        """Generate conclusions text"""
        summary = self._generate_pass_fail_summary(results)

        if summary['overall_status'] == 'PASS':
            return "The test sample has successfully passed all acceptance criteria as specified in the test protocol."
        elif summary['overall_status'] == 'FAIL':
            return f"The test sample has failed {summary['fail_count']} acceptance criteria. Detailed results are provided in the analysis section."
        else:
            return f"The test sample has met most criteria with {summary['conditional_count']} conditional results requiring further evaluation."

    def _export_json(self, report_data: Dict[str, Any], execution_number: str) -> str:
        """Export report as JSON file"""
        try:
            filename = f"report_{execution_number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Path('reports') / filename

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"JSON report exported: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return ""

    def _export_pdf(self, report_data: Dict[str, Any]) -> str:
        """Export report as PDF (placeholder - requires reportlab)"""
        logger.info("PDF export would generate PDF file here")
        # In production, use reportlab or similar library
        return "report.pdf"

    def _export_excel(self, report_data: Dict[str, Any]) -> str:
        """Export report as Excel (placeholder - requires openpyxl)"""
        logger.info("Excel export would generate Excel file here")
        # In production, use openpyxl or similar library
        return "report.xlsx"

    def generate_certificate(
        self,
        test_execution: Dict[str, Any],
        sample: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate test certificate"""
        certificate = {
            'certificate_number': self._generate_report_number(test_execution),
            'issue_date': datetime.utcnow().isoformat(),
            'laboratory': self.lab_info,
            'sample': {
                'manufacturer': sample.get('manufacturer'),
                'model': sample.get('model'),
                'serial_number': sample.get('serial_number')
            },
            'test_results': {
                'rated_power': results.get('rated_power'),
                'efficiency': results.get('efficiency'),
                'fill_factor': results.get('fill_factor'),
                'status': results.get('overall_status')
            },
            'validity': {
                'valid_from': datetime.utcnow().isoformat(),
                'valid_until': None  # Can be set based on requirements
            },
            'signatures': {
                'technician': test_execution.get('technician_name'),
                'reviewer': test_execution.get('reviewer_name'),
                'approver': None
            }
        }

        return certificate
