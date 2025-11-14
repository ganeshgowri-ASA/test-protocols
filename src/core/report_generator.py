"""Report generation utilities."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.utils.logging_config import get_logger
from src.utils.db import DatabaseManager

logger = get_logger(__name__)


class ReportGenerator:
    """Generates test reports in various formats."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        """Initialize report generator.

        Args:
            db_manager: Optional database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()

    def generate_report(
        self,
        run_id: str,
        report_type: str = "comprehensive",
        output_format: str = "html"
    ) -> str:
        """Generate a test report.

        Args:
            run_id: Test run ID
            report_type: Type of report (comprehensive, summary, charts)
            output_format: Output format (html, pdf, json)

        Returns:
            Path to generated report file
        """
        # Get test run data
        run_summary = self.db_manager.get_test_run(run_id)
        measurements = self.db_manager.get_measurements(run_id)

        if not run_summary:
            raise ValueError(f"Test run {run_id} not found")

        # Generate report based on type
        if report_type == "comprehensive":
            report_content = self._generate_comprehensive_report(
                run_summary, measurements
            )
        elif report_type == "summary":
            report_content = self._generate_summary_report(run_summary)
        elif report_type == "charts":
            report_content = self._generate_charts_report(measurements)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Save report
        output_dir = Path("data/reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{run_id}_{report_type}_{timestamp}.{output_format}"
        output_path = output_dir / filename

        if output_format == "json":
            with open(output_path, 'w') as f:
                json.dump(report_content, f, indent=2, default=str)
        elif output_format == "html":
            self._save_html_report(report_content, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Report generated: {output_path}")
        return str(output_path)

    def _generate_comprehensive_report(
        self,
        run_summary: Dict[str, Any],
        measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive report content.

        Args:
            run_summary: Test run summary
            measurements: Measurement data

        Returns:
            Report content dictionary
        """
        df = pd.DataFrame(measurements)

        # Statistical summary
        stats_summary = {}
        for metric_name in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric_name]['metric_value']
            stats_summary[metric_name] = {
                'count': len(metric_data),
                'mean': float(metric_data.mean()),
                'std': float(metric_data.std()),
                'min': float(metric_data.min()),
                'max': float(metric_data.max()),
                'median': float(metric_data.median())
            }

        return {
            'run_summary': run_summary,
            'statistics': stats_summary,
            'measurement_count': len(measurements),
            'metrics': list(df['metric_name'].unique()),
            'generated_at': datetime.now().isoformat()
        }

    def _generate_summary_report(self, run_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report.

        Args:
            run_summary: Test run summary

        Returns:
            Summary report dictionary
        """
        return {
            'run_summary': run_summary,
            'generated_at': datetime.now().isoformat()
        }

    def _generate_charts_report(self, measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate charts for report.

        Args:
            measurements: Measurement data

        Returns:
            Chart data dictionary
        """
        df = pd.DataFrame(measurements)
        charts = {}

        # Time series chart for each metric
        for metric_name in df['metric_name'].unique():
            metric_df = df[df['metric_name'] == metric_name]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=metric_df['timestamp'],
                y=metric_df['metric_value'],
                mode='lines+markers',
                name=metric_name
            ))

            fig.update_layout(
                title=f"{metric_name} over time",
                xaxis_title="Time",
                yaxis_title=f"{metric_name} ({metric_df['metric_unit'].iloc[0] if len(metric_df) > 0 else ''})"
            )

            charts[metric_name] = fig.to_json()

        return {'charts': charts}

    def _save_html_report(self, content: Dict[str, Any], output_path: Path) -> None:
        """Save report as HTML.

        Args:
            content: Report content
            output_path: Output file path
        """
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Protocol Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Test Protocol Report</h1>
            <pre>{json.dumps(content, indent=2, default=str)}</pre>
        </body>
        </html>
        """

        with open(output_path, 'w') as f:
            f.write(html_template)
