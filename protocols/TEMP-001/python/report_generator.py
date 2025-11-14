"""
Report Generator for TEMP-001 Protocol

Generates comprehensive test reports in various formats according to IEC 60891.

Author: ASA PV Testing
Date: 2025-11-14
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import io
import base64


class TEMP001ReportGenerator:
    """
    Report generator for TEMP-001 Temperature Coefficient Testing
    """

    def __init__(
        self,
        protocol_config_path: Optional[str] = None,
        template_dir: Optional[str] = None
    ):
        """
        Initialize report generator

        Args:
            protocol_config_path: Path to protocol.json
            template_dir: Directory containing report templates
        """
        self.config = self._load_config(protocol_config_path)
        self.template_dir = template_dir

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load protocol configuration"""
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "protocol.json"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def generate_report(
        self,
        test_info: Dict,
        measurement_data: pd.DataFrame,
        analysis_results: Dict,
        validation_report: Dict,
        output_path: Union[str, Path],
        format: str = 'pdf'
    ) -> None:
        """
        Generate comprehensive test report

        Args:
            test_info: Test metadata (module ID, date, operator, etc.)
            measurement_data: Raw measurement DataFrame
            analysis_results: Results from TemperatureCoefficientAnalyzer
            validation_report: Validation results
            output_path: Output file path
            format: Report format ('pdf', 'html', 'json', 'excel')
        """
        if format == 'pdf':
            self._generate_pdf_report(
                test_info, measurement_data, analysis_results,
                validation_report, output_path
            )
        elif format == 'html':
            self._generate_html_report(
                test_info, measurement_data, analysis_results,
                validation_report, output_path
            )
        elif format == 'json':
            self._generate_json_report(
                test_info, measurement_data, analysis_results,
                validation_report, output_path
            )
        elif format == 'excel':
            self._generate_excel_report(
                test_info, measurement_data, analysis_results,
                validation_report, output_path
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_pdf_report(
        self,
        test_info: Dict,
        measurement_data: pd.DataFrame,
        analysis_results: Dict,
        validation_report: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """Generate PDF report"""
        output_path = Path(output_path)

        with PdfPages(output_path) as pdf:
            # Page 1: Title and Summary
            fig = self._create_title_page(test_info, analysis_results, validation_report)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

            # Page 2: Measurement Data Table
            fig = self._create_data_table_page(measurement_data)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

            # Page 3: Regression Plots
            fig = self._create_regression_plots(measurement_data, analysis_results)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

            # Page 4: Results Summary
            fig = self._create_results_summary_page(analysis_results, validation_report)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = f"TEMP-001 Temperature Coefficient Test Report"
            d['Author'] = test_info.get('operator', 'ASA PV Testing')
            d['Subject'] = 'Temperature Coefficient Testing per IEC 60891'
            d['Keywords'] = 'PV, Temperature Coefficients, IEC 60891'
            d['CreationDate'] = datetime.now()

    def _create_title_page(
        self,
        test_info: Dict,
        analysis_results: Dict,
        validation_report: Dict
    ) -> plt.Figure:
        """Create report title page"""
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('TEMP-001 Temperature Coefficient Test Report',
                     fontsize=18, fontweight='bold', y=0.95)

        # Add text sections
        text_y = 0.85

        # Test Information
        test_info_text = f"""
TEST INFORMATION
{'='*60}
Module ID:          {test_info.get('module_id', 'N/A')}
Test Date:          {test_info.get('test_date', 'N/A')}
Operator:           {test_info.get('operator', 'N/A')}
Test Standard:      IEC 60891:2021
Protocol:           TEMP-001 v1.0
Laboratory:         {test_info.get('laboratory', 'N/A')}
        """
        fig.text(0.1, text_y, test_info_text, fontsize=10, family='monospace',
                verticalalignment='top')
        text_y -= 0.25

        # Temperature Coefficients Summary
        alpha_pmp = analysis_results.get('alpha_pmp_relative', 0)
        beta_voc = analysis_results.get('beta_voc_relative', 0)
        alpha_isc = analysis_results.get('alpha_isc_relative', 0)

        results_text = f"""
TEMPERATURE COEFFICIENTS
{'='*60}
Power Coefficient (α_Pmp):      {alpha_pmp:>10.4f} %/°C
Voltage Coefficient (β_Voc):    {beta_voc:>10.4f} %/°C
Current Coefficient (α_Isc):    {alpha_isc:>10.4f} %/°C

REGRESSION QUALITY
{'='*60}
Power R²:                       {analysis_results.get('r_squared_pmp', 0):>10.4f}
Voltage R²:                     {analysis_results.get('r_squared_voc', 0):>10.4f}
Current R²:                     {analysis_results.get('r_squared_isc', 0):>10.4f}
        """
        fig.text(0.1, text_y, results_text, fontsize=10, family='monospace',
                verticalalignment='top')
        text_y -= 0.30

        # STC Performance
        stc_text = f"""
PERFORMANCE AT STC (25°C, 1000 W/m²)
{'='*60}
Maximum Power (Pmp):            {analysis_results.get('pmp_at_stc', 0):>10.2f} W
Open Circuit Voltage (Voc):     {analysis_results.get('voc_at_stc', 0):>10.3f} V
Short Circuit Current (Isc):    {analysis_results.get('isc_at_stc', 0):>10.3f} A
        """
        fig.text(0.1, text_y, stc_text, fontsize=10, family='monospace',
                verticalalignment='top')
        text_y -= 0.22

        # Validation Status
        overall_status = validation_report.get('overall_status', 'unknown')
        status_color = {
            'pass': 'green',
            'warning': 'orange',
            'fail': 'red'
        }.get(overall_status, 'black')

        summary = validation_report.get('summary', {})
        validation_text = f"""
VALIDATION STATUS: {overall_status.upper()}

Total Checks:        {summary.get('total_checks', 0)}
Passed:              {summary.get('passed', 0)}
Warnings:            {summary.get('warnings', 0)}
Critical Failures:   {summary.get('critical_failures', 0)}
        """
        fig.text(0.1, text_y, validation_text, fontsize=10, family='monospace',
                verticalalignment='top', color=status_color, weight='bold')

        # Footer
        fig.text(0.5, 0.05, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ha='center', fontsize=8, style='italic')

        return fig

    def _create_data_table_page(self, measurement_data: pd.DataFrame) -> plt.Figure:
        """Create measurement data table page"""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('tight')
        ax.axis('off')

        # Title
        fig.suptitle('Measurement Data', fontsize=16, fontweight='bold', y=0.98)

        # Select relevant columns
        display_columns = [
            'module_temperature', 'pmax', 'voc', 'isc', 'irradiance'
        ]
        available_columns = [col for col in display_columns if col in measurement_data.columns]

        # Format data for display
        display_data = measurement_data[available_columns].copy()

        # Round numeric columns
        for col in display_data.columns:
            if display_data[col].dtype in [np.float64, np.float32]:
                display_data[col] = display_data[col].round(3)

        # Create table
        table = ax.table(
            cellText=display_data.values,
            colLabels=display_data.columns,
            cellLoc='center',
            loc='upper center',
            bbox=[0, 0.7, 1, 0.25]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Style header row
        for i in range(len(display_data.columns)):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Add statistics
        stats_text = f"""
MEASUREMENT STATISTICS
{'='*50}
Number of Points:     {len(measurement_data)}
Temperature Range:    {measurement_data['module_temperature'].min():.1f} to {measurement_data['module_temperature'].max():.1f} °C
Temperature Span:     {measurement_data['module_temperature'].max() - measurement_data['module_temperature'].min():.1f} °C

Power Range:          {measurement_data['pmax'].min():.2f} to {measurement_data['pmax'].max():.2f} W
Voltage Range:        {measurement_data['voc'].min():.3f} to {measurement_data['voc'].max():.3f} V
Current Range:        {measurement_data['isc'].min():.3f} to {measurement_data['isc'].max():.3f} A
        """

        fig.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
                verticalalignment='top')

        return fig

    def _create_regression_plots(
        self,
        measurement_data: pd.DataFrame,
        analysis_results: Dict
    ) -> plt.Figure:
        """Create regression analysis plots"""
        fig = plt.figure(figsize=(11, 8.5))
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

        temp = measurement_data['module_temperature'].values

        # Use normalized values if available
        pmax = (measurement_data['pmax_normalized'].values
                if 'pmax_normalized' in measurement_data.columns
                else measurement_data['pmax'].values)
        voc = (measurement_data['voc_normalized'].values
               if 'voc_normalized' in measurement_data.columns
               else measurement_data['voc'].values)
        isc = (measurement_data['isc_normalized'].values
               if 'isc_normalized' in measurement_data.columns
               else measurement_data['isc'].values)

        # Plot 1: Power vs Temperature
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.scatter(temp, pmax, color='blue', s=50, alpha=0.6, label='Measured')

        # Add regression line
        slope = analysis_results.get('pmp_slope', 0)
        intercept = analysis_results.get('pmp_intercept', 0)
        temp_fit = np.linspace(temp.min(), temp.max(), 100)
        pmax_fit = slope * temp_fit + intercept
        ax1.plot(temp_fit, pmax_fit, 'r-', linewidth=2, label='Linear Fit')

        r2 = analysis_results.get('r_squared_pmp', 0)
        alpha = analysis_results.get('alpha_pmp_relative', 0)
        ax1.text(0.05, 0.95, f'α_Pmp = {alpha:.4f} %/°C\nR² = {r2:.4f}',
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax1.set_xlabel('Module Temperature (°C)', fontsize=10)
        ax1.set_ylabel('Maximum Power (W)', fontsize=10)
        ax1.set_title('Power vs Temperature', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Voltage vs Temperature
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.scatter(temp, voc, color='green', s=50, alpha=0.6, label='Measured')

        slope = analysis_results.get('voc_slope', 0)
        intercept = analysis_results.get('voc_intercept', 0)
        voc_fit = slope * temp_fit + intercept
        ax2.plot(temp_fit, voc_fit, 'r-', linewidth=2, label='Linear Fit')

        r2 = analysis_results.get('r_squared_voc', 0)
        beta = analysis_results.get('beta_voc_relative', 0)
        ax2.text(0.05, 0.95, f'β_Voc = {beta:.4f} %/°C\nR² = {r2:.4f}',
                transform=ax2.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax2.set_xlabel('Module Temperature (°C)', fontsize=10)
        ax2.set_ylabel('Open Circuit Voltage (V)', fontsize=10)
        ax2.set_title('Voc vs Temperature', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Plot 3: Current vs Temperature
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.scatter(temp, isc, color='orange', s=50, alpha=0.6, label='Measured')

        slope = analysis_results.get('isc_slope', 0)
        intercept = analysis_results.get('isc_intercept', 0)
        isc_fit = slope * temp_fit + intercept
        ax3.plot(temp_fit, isc_fit, 'r-', linewidth=2, label='Linear Fit')

        r2 = analysis_results.get('r_squared_isc', 0)
        alpha_i = analysis_results.get('alpha_isc_relative', 0)
        ax3.text(0.05, 0.05, f'α_Isc = {alpha_i:.4f} %/°C\nR² = {r2:.4f}',
                transform=ax3.transAxes, verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax3.set_xlabel('Module Temperature (°C)', fontsize=10)
        ax3.set_ylabel('Short Circuit Current (A)', fontsize=10)
        ax3.set_title('Isc vs Temperature', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Plot 4: Normalized Power
        ax4 = fig.add_subplot(gs[1, 1])
        pmax_normalized = (pmax / analysis_results.get('pmp_at_stc', 1)) * 100
        ax4.plot(temp, pmax_normalized, 'o-', color='purple', markersize=6)
        ax4.axhline(y=100, color='red', linestyle='--', label='STC Reference (25°C)')
        ax4.set_xlabel('Module Temperature (°C)', fontsize=10)
        ax4.set_ylabel('Normalized Power (%)', fontsize=10)
        ax4.set_title('Normalized Power vs Temperature', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        fig.suptitle('Temperature Coefficient Analysis - Regression Plots',
                    fontsize=14, fontweight='bold')

        return fig

    def _create_results_summary_page(
        self,
        analysis_results: Dict,
        validation_report: Dict
    ) -> plt.Figure:
        """Create results summary and validation page"""
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Test Results Summary and Validation',
                    fontsize=16, fontweight='bold', y=0.95)

        text_y = 0.85

        # Detailed Results
        results_text = f"""
DETAILED TEMPERATURE COEFFICIENT RESULTS
{'='*70}

Power Temperature Coefficient:
  Relative (α_Pmp):              {analysis_results.get('alpha_pmp_relative', 0):>10.4f} %/°C
  Absolute:                      {analysis_results.get('alpha_pmp_absolute', 0):>10.4f} W/°C
  Regression R²:                 {analysis_results.get('r_squared_pmp', 0):>10.4f}
  Regression Equation:           Pmp = {analysis_results.get('pmp_slope', 0):.4f} * T + {analysis_results.get('pmp_intercept', 0):.4f}

Voltage Temperature Coefficient:
  Relative (β_Voc):              {analysis_results.get('beta_voc_relative', 0):>10.4f} %/°C
  Absolute:                      {analysis_results.get('beta_voc_absolute', 0):>10.5f} V/°C
  Regression R²:                 {analysis_results.get('r_squared_voc', 0):>10.4f}
  Regression Equation:           Voc = {analysis_results.get('voc_slope', 0):.5f} * T + {analysis_results.get('voc_intercept', 0):.4f}

Current Temperature Coefficient:
  Relative (α_Isc):              {analysis_results.get('alpha_isc_relative', 0):>10.4f} %/°C
  Absolute:                      {analysis_results.get('alpha_isc_absolute', 0):>10.5f} A/°C
  Regression R²:                 {analysis_results.get('r_squared_isc', 0):>10.4f}
  Regression Equation:           Isc = {analysis_results.get('isc_slope', 0):.5f} * T + {analysis_results.get('isc_intercept', 0):.4f}
        """

        fig.text(0.1, text_y, results_text, fontsize=9, family='monospace',
                verticalalignment='top')
        text_y -= 0.50

        # Validation Results
        validation_text = f"""
QUALITY VALIDATION RESULTS
{'='*70}
Overall Status: {validation_report.get('overall_status', 'unknown').upper()}

Summary:
  Total Checks:                  {validation_report.get('summary', {}).get('total_checks', 0)}
  Passed:                        {validation_report.get('summary', {}).get('passed', 0)}
  Warnings:                      {validation_report.get('summary', {}).get('warnings', 0)}
  Critical Failures:             {validation_report.get('summary', {}).get('critical_failures', 0)}
        """

        status_color = {
            'pass': 'green',
            'warning': 'orange',
            'fail': 'red'
        }.get(validation_report.get('overall_status', 'unknown'), 'black')

        fig.text(0.1, text_y, validation_text, fontsize=9, family='monospace',
                verticalalignment='top', color=status_color, weight='bold')
        text_y -= 0.20

        # Individual check results
        if 'results' in validation_report and validation_report['results']:
            checks_text = "Individual Checks:\n" + "-" * 70 + "\n"
            for result in validation_report['results'][:10]:  # Show first 10
                status_symbol = {
                    'pass': '✓',
                    'warning': '⚠',
                    'fail': '✗'
                }.get(result.get('status', ''), '?')

                checks_text += f"{status_symbol} {result.get('check_name', 'Unknown'):<40} {result.get('status', 'unknown'):>10}\n"
                if result.get('message'):
                    checks_text += f"  → {result['message']}\n"

            fig.text(0.1, text_y, checks_text, fontsize=8, family='monospace',
                    verticalalignment='top')

        return fig

    def _generate_json_report(
        self,
        test_info: Dict,
        measurement_data: pd.DataFrame,
        analysis_results: Dict,
        validation_report: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """Generate JSON report"""
        report = {
            'test_info': test_info,
            'measurement_data': measurement_data.to_dict(orient='records'),
            'analysis_results': analysis_results,
            'validation_report': validation_report,
            'generated_at': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    def _generate_excel_report(
        self,
        test_info: Dict,
        measurement_data: pd.DataFrame,
        analysis_results: Dict,
        validation_report: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """Generate Excel report"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Test Info sheet
            df_info = pd.DataFrame([test_info])
            df_info.to_excel(writer, sheet_name='Test Info', index=False)

            # Measurement Data sheet
            measurement_data.to_excel(writer, sheet_name='Measurements', index=False)

            # Results sheet
            df_results = pd.DataFrame([analysis_results])
            df_results.to_excel(writer, sheet_name='Results', index=False)

            # Validation sheet
            if 'results' in validation_report:
                df_validation = pd.DataFrame(validation_report['results'])
                df_validation.to_excel(writer, sheet_name='Validation', index=False)

    def _generate_html_report(
        self,
        test_info: Dict,
        measurement_data: pd.DataFrame,
        analysis_results: Dict,
        validation_report: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TEMP-001 Temperature Coefficient Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2E7D32; }}
        h2 {{ color: #1976D2; border-bottom: 2px solid #1976D2; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .pass {{ color: green; font-weight: bold; }}
        .warning {{ color: orange; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>TEMP-001 Temperature Coefficient Test Report</h1>

    <h2>Test Information</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>Module ID</td><td>{test_info.get('module_id', 'N/A')}</td></tr>
        <tr><td>Test Date</td><td>{test_info.get('test_date', 'N/A')}</td></tr>
        <tr><td>Operator</td><td>{test_info.get('operator', 'N/A')}</td></tr>
        <tr><td>Standard</td><td>IEC 60891:2021</td></tr>
    </table>

    <h2>Temperature Coefficients</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th><th>Unit</th><th>R²</th></tr>
        <tr>
            <td>Power (α_Pmp)</td>
            <td>{analysis_results.get('alpha_pmp_relative', 0):.4f}</td>
            <td>%/°C</td>
            <td>{analysis_results.get('r_squared_pmp', 0):.4f}</td>
        </tr>
        <tr>
            <td>Voltage (β_Voc)</td>
            <td>{analysis_results.get('beta_voc_relative', 0):.4f}</td>
            <td>%/°C</td>
            <td>{analysis_results.get('r_squared_voc', 0):.4f}</td>
        </tr>
        <tr>
            <td>Current (α_Isc)</td>
            <td>{analysis_results.get('alpha_isc_relative', 0):.4f}</td>
            <td>%/°C</td>
            <td>{analysis_results.get('r_squared_isc', 0):.4f}</td>
        </tr>
    </table>

    <h2>Measurement Data</h2>
    {measurement_data.to_html(index=False)}

    <h2>Validation Status</h2>
    <p class="{validation_report.get('overall_status', 'unknown')}">
        Overall Status: {validation_report.get('overall_status', 'unknown').upper()}
    </p>

    <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body>
</html>
        """

        with open(output_path, 'w') as f:
            f.write(html_content)


def main():
    """Example usage"""
    # Sample data
    test_info = {
        'module_id': 'TEST-MODULE-001',
        'test_date': '2025-11-14',
        'operator': 'John Doe',
        'laboratory': 'ASA PV Testing Lab'
    }

    measurement_data = pd.DataFrame({
        'module_temperature': [20, 30, 40, 50, 60, 70],
        'pmax': [260, 252, 244, 236, 228, 220],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'irradiance': [1000, 1000, 1000, 1000, 1000, 1000]
    })

    analysis_results = {
        'alpha_pmp_relative': -0.4015,
        'alpha_pmp_absolute': -1.600,
        'r_squared_pmp': 0.9998,
        'beta_voc_relative': -0.3200,
        'beta_voc_absolute': -0.0700,
        'r_squared_voc': 0.9999,
        'alpha_isc_relative': 0.0543,
        'alpha_isc_absolute': 0.0050,
        'r_squared_isc': 0.9997,
        'pmp_at_stc': 244.0,
        'voc_at_stc': 37.1,
        'isc_at_stc': 9.30,
        'pmp_slope': -1.600,
        'pmp_intercept': 284.0,
        'voc_slope': -0.0700,
        'voc_intercept': 39.85,
        'isc_slope': 0.0050,
        'isc_intercept': 9.175
    }

    validation_report = {
        'overall_status': 'pass',
        'summary': {
            'total_checks': 8,
            'passed': 7,
            'warnings': 1,
            'critical_failures': 0
        },
        'results': [
            {
                'check_name': 'Data Completeness',
                'status': 'pass',
                'message': 'All required fields present'
            }
        ]
    }

    # Generate reports
    generator = TEMP001ReportGenerator()

    print("Generating PDF report...")
    generator.generate_report(
        test_info, measurement_data, analysis_results,
        validation_report, 'temp_001_report.pdf', format='pdf'
    )

    print("Generating JSON report...")
    generator.generate_report(
        test_info, measurement_data, analysis_results,
        validation_report, 'temp_001_report.json', format='json'
    )

    print("Reports generated successfully!")


if __name__ == "__main__":
    main()
