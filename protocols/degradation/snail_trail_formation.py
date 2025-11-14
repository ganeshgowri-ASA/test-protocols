"""
SNAIL-001 - Snail Trail Formation Test Protocol
Implementation of snail trail degradation assessment for PV modules
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats

import sys
sys.path.append(str(Path(__file__).parent.parent))

from base_protocol import BaseProtocol, ProtocolResult


class SnailTrailFormationProtocol(BaseProtocol):
    """
    Implementation of SNAIL-001 protocol for assessing snail trail formation
    in PV modules under accelerated environmental conditions.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Snail Trail Formation protocol.

        Args:
            config_path: Path to protocol JSON config. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "snail_trail_formation.json"

        super().__init__(config_path)
        self.measurements_df: Optional[pd.DataFrame] = None

    def run(self, test_data: Dict[str, Any]) -> ProtocolResult:
        """
        Execute the SNAIL-001 protocol with provided test data.

        Args:
            test_data: Dictionary containing:
                - input_params: Module information and initial measurements
                - measurements: List of measurement data at each inspection interval

        Returns:
            ProtocolResult object containing execution results
        """
        # Generate unique run ID
        run_id = f"SNAIL-001_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

        # Initialize result object
        self.result = ProtocolResult(
            protocol_id=self.config.protocol_id,
            run_id=run_id,
            timestamp=datetime.now(),
            status="running",
            input_data=test_data.get('input_params', {})
        )

        try:
            # Validate input parameters
            is_valid, errors = self.validate_input(test_data.get('input_params', {}))
            if not is_valid:
                self.result.status = "failed"
                self.result.errors = errors
                return self.result

            # Process measurements
            measurements = test_data.get('measurements', [])
            if not measurements:
                self.result.status = "failed"
                self.result.errors = ["No measurement data provided"]
                return self.result

            # Convert measurements to DataFrame for analysis
            self.measurements_df = pd.DataFrame(measurements)
            self.result.measurements = {
                'raw_data': measurements,
                'inspection_intervals': len(measurements)
            }

            # Perform analysis
            analysis_results = self.analyze_results()
            self.result.analysis_results = analysis_results

            # Perform QC checks
            qc_passed, qc_details = self.perform_qc_checks()
            self.result.qc_passed = qc_passed
            self.result.qc_details = qc_details

            # Determine pass/fail status
            pass_fail_results = self._evaluate_pass_fail_criteria()
            self.result.analysis_results['pass_fail'] = pass_fail_results

            self.result.status = "completed"

        except Exception as e:
            self.result.status = "failed"
            self.result.errors.append(f"Execution error: {str(e)}")

        return self.result

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the test results and generate statistics.

        Returns:
            Dictionary containing comprehensive analysis results
        """
        if self.measurements_df is None or self.measurements_df.empty:
            return {"error": "No measurement data available for analysis"}

        input_params = self.result.input_data
        analysis = {}

        # Calculate degradation metrics
        initial_pmax = input_params.get('initial_pmax_w', 0)
        initial_isc = input_params.get('initial_isc_a', 0)
        initial_voc = input_params.get('initial_voc_v', 0)
        initial_ff = input_params.get('initial_ff_percent', 0)

        # Current (final) values
        final_row = self.measurements_df.iloc[-1]
        current_pmax = final_row['pmax_w']
        current_isc = final_row['isc_a']
        current_voc = final_row['voc_v']
        current_ff = final_row['ff_percent']

        # Calculate degradation percentages
        analysis['power_degradation'] = {
            'initial_w': initial_pmax,
            'final_w': current_pmax,
            'degradation_percent': ((initial_pmax - current_pmax) / initial_pmax * 100) if initial_pmax > 0 else 0,
            'degradation_w': initial_pmax - current_pmax
        }

        analysis['isc_degradation'] = {
            'initial_a': initial_isc,
            'final_a': current_isc,
            'degradation_percent': ((initial_isc - current_isc) / initial_isc * 100) if initial_isc > 0 else 0
        }

        analysis['voc_degradation'] = {
            'initial_v': initial_voc,
            'final_v': current_voc,
            'degradation_percent': ((initial_voc - current_voc) / initial_voc * 100) if initial_voc > 0 else 0
        }

        analysis['ff_degradation'] = {
            'initial_percent': initial_ff,
            'final_percent': current_ff,
            'degradation_percent': ((initial_ff - current_ff) / initial_ff * 100) if initial_ff > 0 else 0
        }

        # Snail trail progression analysis
        final_affected_area = final_row['affected_area_percent']
        final_affected_cells = final_row['affected_cells_count']
        total_test_hours = final_row['inspection_hour']

        analysis['snail_trail_metrics'] = {
            'final_affected_area_percent': final_affected_area,
            'final_affected_cells': int(final_affected_cells),
            'progression_rate_percent_per_hour': (final_affected_area / total_test_hours) if total_test_hours > 0 else 0,
            'final_severity': final_row['visual_snail_trail_severity']
        }

        # Statistical analysis of progression
        if len(self.measurements_df) > 2:
            hours = self.measurements_df['inspection_hour'].values
            affected_area = self.measurements_df['affected_area_percent'].values

            # Linear regression for snail trail progression
            slope, intercept, r_value, p_value, std_err = stats.linregress(hours, affected_area)

            analysis['snail_trail_progression_stats'] = {
                'linear_slope_percent_per_hour': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'progression_model': f"Area(%) = {slope:.4f} * hours + {intercept:.4f}"
            }

            # Power degradation trend
            # Calculate power degradation at each interval
            power_deg_list = []
            for _, row in self.measurements_df.iterrows():
                pmax = row['pmax_w']
                deg = ((initial_pmax - pmax) / initial_pmax * 100) if initial_pmax > 0 else 0
                power_deg_list.append(deg)

            self.measurements_df['power_degradation_percent'] = power_deg_list

            # Power degradation rate analysis
            power_slope, power_intercept, power_r, _, _ = stats.linregress(hours, power_deg_list)

            analysis['power_degradation_trend'] = {
                'linear_slope_percent_per_hour': power_slope,
                'r_squared': power_r ** 2,
                'average_degradation_rate_percent_per_100h': power_slope * 100
            }

        # Correlation between snail trail and power loss
        if len(self.measurements_df) > 2:
            correlation = self.measurements_df['affected_area_percent'].corr(
                self.measurements_df['power_degradation_percent']
            )
            analysis['correlation_snail_trail_power_loss'] = {
                'pearson_correlation': correlation,
                'interpretation': self._interpret_correlation(correlation)
            }

        # Severity distribution
        severity_counts = self.measurements_df['visual_snail_trail_severity'].value_counts().to_dict()
        analysis['severity_distribution'] = severity_counts

        return analysis

    def perform_qc_checks(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform quality control checks on the results.

        Returns:
            Tuple of (qc_passed, qc_details)
        """
        qc_details = {}
        all_checks_passed = True

        # Check 1: Data completeness
        required_intervals = len(self.config.test_conditions['inspection_intervals_hours'])
        actual_intervals = len(self.measurements_df) if self.measurements_df is not None else 0

        completeness_ratio = actual_intervals / required_intervals if required_intervals > 0 else 0
        data_complete = completeness_ratio >= 0.85  # Allow some tolerance

        qc_details['data_completeness'] = {
            'passed': data_complete,
            'expected_intervals': required_intervals,
            'actual_intervals': actual_intervals,
            'completeness_ratio': completeness_ratio,
            'severity': 'critical'
        }

        if not data_complete:
            all_checks_passed = False

        # Check 2: Measurement consistency
        consistency_checks = []
        for idx, row in self.measurements_df.iterrows():
            pmax = row['pmax_w']
            isc = row['isc_a']
            voc = row['voc_v']
            ff = row['ff_percent']

            # Check Pmax <= Isc * Voc
            check1 = pmax <= (isc * voc * 1.01)  # 1% tolerance
            # Check FF in valid range
            check2 = 50 <= ff <= 100

            consistency_checks.append(check1 and check2)

        all_consistent = all(consistency_checks)
        qc_details['measurement_consistency'] = {
            'passed': all_consistent,
            'consistent_measurements': sum(consistency_checks),
            'total_measurements': len(consistency_checks),
            'severity': 'critical'
        }

        if not all_consistent:
            all_checks_passed = False

        # Check 3: Monotonic degradation (warning only)
        power_improvements = []
        if len(self.measurements_df) > 1:
            for i in range(1, len(self.measurements_df)):
                prev_pmax = self.measurements_df.iloc[i-1]['pmax_w']
                curr_pmax = self.measurements_df.iloc[i]['pmax_w']
                improvement = ((curr_pmax - prev_pmax) / prev_pmax * 100) if prev_pmax > 0 else 0
                if improvement > 2.0:  # More than 2% improvement
                    power_improvements.append({
                        'interval': i,
                        'improvement_percent': improvement
                    })

        monotonic_ok = len(power_improvements) == 0
        qc_details['monotonic_degradation'] = {
            'passed': monotonic_ok,
            'unexpected_improvements': power_improvements,
            'severity': 'warning'
        }

        # Check 4: Visual-electrical correlation (warning only)
        final_severity = self.measurements_df.iloc[-1]['visual_snail_trail_severity']
        power_deg = self.result.analysis_results['power_degradation']['degradation_percent']

        correlation_ok = True
        if final_severity == 'severe' and power_deg < 5.0:
            correlation_ok = False

        qc_details['visual_electrical_correlation'] = {
            'passed': correlation_ok,
            'final_severity': final_severity,
            'power_degradation_percent': power_deg,
            'severity': 'warning',
            'note': 'Severe visual degradation should correlate with significant power loss'
        }

        # Overall QC status
        qc_details['overall'] = {
            'all_critical_checks_passed': all_checks_passed,
            'warnings_present': not (monotonic_ok and correlation_ok)
        }

        return all_checks_passed, qc_details

    def _evaluate_pass_fail_criteria(self) -> Dict[str, Any]:
        """Evaluate pass/fail criteria based on protocol thresholds."""
        results = {}

        power_deg = self.result.analysis_results['power_degradation']['degradation_percent']
        affected_area = self.result.analysis_results['snail_trail_metrics']['final_affected_area_percent']

        # Power degradation criterion
        power_limit = 5.0  # 5% max
        results['power_degradation_criterion'] = {
            'threshold_percent': power_limit,
            'actual_percent': power_deg,
            'passed': power_deg <= power_limit,
            'result': 'PASS - Power degradation within acceptable limits' if power_deg <= power_limit
                     else 'FAIL - Excessive power degradation due to snail trail formation'
        }

        # Affected area criterion
        area_limit = 10.0  # 10% max
        results['affected_area_criterion'] = {
            'threshold_percent': area_limit,
            'actual_percent': affected_area,
            'passed': affected_area <= area_limit,
            'result': 'PASS - Snail trail area within acceptable limits' if affected_area <= area_limit
                     else 'FAIL - Excessive snail trail coverage'
        }

        # Overall result
        overall_pass = results['power_degradation_criterion']['passed'] and \
                      results['affected_area_criterion']['passed']

        results['overall'] = {
            'passed': overall_pass,
            'result': 'PASS' if overall_pass else 'FAIL'
        }

        return results

    def generate_report(self, output_path: Path) -> Path:
        """
        Generate comprehensive PDF report for the test results.

        Args:
            output_path: Directory path where the report should be saved

        Returns:
            Path to the generated report file
        """
        if self.result is None:
            raise ValueError("No results available. Run the protocol first.")

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        report_file = output_path / f"{self.result.run_id}_report.pdf"

        # Create PDF
        doc = SimpleDocTemplate(str(report_file), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center
        )

        story.append(Paragraph("SNAIL-001 Test Report", title_style))
        story.append(Paragraph("Snail Trail Formation Assessment", styles['Heading2']))
        story.append(Spacer(1, 0.3 * inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))

        overall_result = self.result.analysis_results['pass_fail']['overall']
        result_color = colors.green if overall_result['passed'] else colors.red

        summary_data = [
            ['Test Result:', overall_result['result']],
            ['Module ID:', self.result.input_data.get('module_id', 'N/A')],
            ['Test Duration:', f"{self.measurements_df.iloc[-1]['inspection_hour']} hours"],
            ['Final Power Degradation:', f"{self.result.analysis_results['power_degradation']['degradation_percent']:.2f}%"],
            ['Final Affected Area:', f"{self.result.analysis_results['snail_trail_metrics']['final_affected_area_percent']:.2f}%"]
        ]

        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (1, 0), (1, 0), result_color),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Module Specifications
        story.append(Paragraph("Module Specifications", styles['Heading2']))
        spec_data = [
            ['Manufacturer:', self.result.input_data.get('manufacturer', 'N/A')],
            ['Model Number:', self.result.input_data.get('model_number', 'N/A')],
            ['Cell Technology:', self.result.input_data.get('cell_technology', 'N/A')],
            ['Nameplate Power:', f"{self.result.input_data.get('nameplate_power_w', 'N/A')} W"],
        ]

        spec_table = Table(spec_data, colWidths=[2.5*inch, 3.5*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(spec_table)
        story.append(Spacer(1, 0.3 * inch))

        # QC Results
        story.append(Paragraph("Quality Control Results", styles['Heading2']))
        qc_overall = self.result.qc_details['overall']['all_critical_checks_passed']
        qc_color = colors.green if qc_overall else colors.red
        story.append(Paragraph(
            f"<b>QC Status:</b> <font color={'green' if qc_overall else 'red'}>{'PASSED' if qc_overall else 'FAILED'}</font>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        doc.build(story)

        return report_file

    @staticmethod
    def _interpret_correlation(correlation: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "Strong correlation"
        elif abs_corr >= 0.5:
            return "Moderate correlation"
        elif abs_corr >= 0.3:
            return "Weak correlation"
        else:
            return "Very weak or no correlation"
