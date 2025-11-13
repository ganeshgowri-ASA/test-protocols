"""Report Generation Utilities for PV Testing Protocols"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import pandas as pd


class ReportTemplates:
    """Standard report templates"""

    @staticmethod
    def get_header_template() -> Dict[str, str]:
        """Get standard report header template"""
        return {
            "company": "PV Testing Laboratory",
            "report_type": "Test Protocol Execution Report",
            "logo_path": "assets/logo.png",
            "accreditation": "ISO/IEC 17025:2017 Accredited"
        }

    @staticmethod
    def get_executive_summary_template() -> List[str]:
        """Get executive summary template sections"""
        return [
            "Test Objective",
            "Module Information",
            "Test Conditions",
            "Key Results",
            "Pass/Fail Status",
            "Recommendations"
        ]


class ReportGenerator:
    """Generate test reports in multiple formats"""

    def __init__(self, protocol_data: Dict[str, Any]):
        """
        Initialize report generator.

        Args:
            protocol_data: Complete protocol execution data
        """
        self.data = protocol_data
        self.generated_at = datetime.now()

    def generate_json(self, output_path: Optional[Path] = None) -> str:
        """
        Generate JSON report.

        Args:
            output_path: Optional path to save report

        Returns:
            JSON string
        """
        report = {
            "metadata": {
                "report_id": f"RPT-{self.generated_at.strftime('%Y%m%d-%H%M%S')}",
                "generated_at": self.generated_at.isoformat(),
                "protocol_id": self.data.get("protocol_id"),
                "execution_id": self.data.get("execution_id")
            },
            "protocol_data": self.data
        }

        json_str = json.dumps(report, indent=2, default=str)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)

        return json_str

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate executive summary.

        Returns:
            Summary dictionary
        """
        return {
            "protocol_id": self.data.get("protocol_id"),
            "protocol_name": self.data.get("metadata", {}).get("protocol_name"),
            "execution_id": self.data.get("execution_id"),
            "status": self.data.get("status"),
            "completed_at": self.data.get("timing", {}).get("completed_at"),
            "duration_seconds": self.data.get("timing", {}).get("duration_seconds"),
            "validation_summary": self.data.get("validation_summary", {}),
            "key_results": self._extract_key_results()
        }

    def _extract_key_results(self) -> Dict[str, Any]:
        """Extract key results from protocol data"""
        results = self.data.get("results", {})

        # Common results across protocols
        key_results = {}

        if "pmax" in results:
            key_results["maximum_power"] = f"{results['pmax']:.2f} W"
        if "efficiency" in results:
            key_results["efficiency"] = f"{results['efficiency']:.2f} %"
        if "pass_fail" in results:
            key_results["status"] = "PASS" if results["pass_fail"] else "FAIL"

        return key_results

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert results to DataFrame for easy export.

        Returns:
            Pandas DataFrame
        """
        results = self.data.get("results", {})
        return pd.DataFrame([results])
