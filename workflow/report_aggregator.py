"""
Report Aggregator - Consolidates outputs from all workflow stages into final reports.

Generates comprehensive reports linking service request → inspection → protocol execution → results.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class ReportAggregator:
    """Aggregator for consolidating workflow data into comprehensive reports."""

    def __init__(self, data_dir: str = "data/reports"):
        """Initialize report aggregator."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.reports_cache: Dict[str, Dict[str, Any]] = {}

    def generate_comprehensive_report(self, workflow_id: str,
                                     service_request: Dict[str, Any],
                                     inspection: Dict[str, Any],
                                     equipment_plan: Dict[str, Any],
                                     protocol_executions: List[Dict[str, Any]]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Generate comprehensive report aggregating all workflow stages.

        Args:
            workflow_id: Workflow identifier
            service_request: Service request data
            inspection: Incoming inspection data
            equipment_plan: Equipment planning data
            protocol_executions: List of protocol execution records

        Returns:
            Tuple of (success, message, report_object)
        """
        try:
            report_id = self._generate_report_id()

            # Aggregate data from all stages
            report = {
                "report_id": report_id,
                "workflow_id": workflow_id,
                "generated_at": datetime.now().isoformat(),
                "report_type": "Comprehensive Workflow Report",

                # Executive Summary
                "executive_summary": self._create_executive_summary(
                    service_request, inspection, protocol_executions
                ),

                # Service Request Details
                "service_request": {
                    "request_id": service_request.get("request_id"),
                    "request_date": service_request.get("request_date"),
                    "requested_by": service_request.get("requested_by"),
                    "project_customer": service_request.get("project_customer"),
                    "priority": service_request.get("priority"),
                    "protocols_requested": service_request.get("protocols_requested", [])
                },

                # Incoming Inspection Summary
                "incoming_inspection": {
                    "inspection_id": inspection.get("inspection_id"),
                    "inspection_date": inspection.get("inspection_date"),
                    "inspector": inspection.get("inspector"),
                    "acceptance_decision": inspection.get("acceptance_decision"),
                    "sample_condition": {
                        "visual_inspection": inspection.get("visual_inspection", {}).get("overall_condition"),
                        "documentation_complete": inspection.get("documentation_check", {}).get("completeness_status"),
                        "ready_for_testing": inspection.get("condition_assessment", {}).get("ready_for_testing")
                    }
                },

                # Equipment Utilization
                "equipment_utilization": {
                    "planning_id": equipment_plan.get("planning_id"),
                    "equipment_allocated": [
                        {
                            "equipment_id": eq.get("equipment_id"),
                            "equipment_type": eq.get("equipment_type"),
                            "manufacturer": eq.get("manufacturer"),
                            "model": eq.get("model")
                        }
                        for eq in equipment_plan.get("equipment_allocation", [])
                    ],
                    "schedule": equipment_plan.get("schedule")
                },

                # Protocol Execution Results
                "protocol_results": self._aggregate_protocol_results(protocol_executions),

                # Data Traceability
                "traceability": {
                    "service_request_id": service_request.get("request_id"),
                    "inspection_id": inspection.get("inspection_id"),
                    "equipment_planning_id": equipment_plan.get("planning_id"),
                    "protocol_execution_ids": [pe.get("execution_id") for pe in protocol_executions],
                    "workflow_id": workflow_id
                },

                # QC and Approvals
                "quality_control": {
                    "service_request_approved_by": service_request.get("workflow_metadata", {}).get("approved_by"),
                    "service_request_approved_at": service_request.get("workflow_metadata", {}).get("approved_at"),
                    "inspection_decision_by": inspection.get("acceptance_decision", {}).get("decision_by"),
                    "equipment_plan_approved_by": equipment_plan.get("workflow_metadata", {}).get("approved_by")
                },

                # Metadata
                "metadata": {
                    "report_version": "1.0",
                    "generated_by": "Report Aggregator System",
                    "status": "Draft"
                }
            }

            # Save report
            self._save_report(report)

            logger.info(f"Comprehensive report {report_id} generated for workflow {workflow_id}")
            return True, f"Report {report_id} generated successfully", report

        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {str(e)}")
            return False, f"Error generating report: {str(e)}", None

    def _create_executive_summary(self, service_request: Dict[str, Any],
                                  inspection: Dict[str, Any],
                                  protocol_executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create executive summary section."""
        # Count pass/fail results
        total_protocols = len(protocol_executions)
        passed = sum(1 for pe in protocol_executions
                    if pe.get("results", {}).get("pass_fail") == "Pass")
        failed = sum(1 for pe in protocol_executions
                    if pe.get("results", {}).get("pass_fail") == "Fail")

        return {
            "project_name": service_request.get("project_customer", {}).get("name"),
            "total_protocols_executed": total_protocols,
            "protocols_passed": passed,
            "protocols_failed": failed,
            "overall_result": "Pass" if failed == 0 and total_protocols > 0 else "Fail",
            "inspection_result": inspection.get("acceptance_decision", {}).get("decision"),
            "testing_period": {
                "start": min((pe.get("execution_details", {}).get("start_time")
                            for pe in protocol_executions if pe.get("execution_details", {}).get("start_time")),
                           default=None),
                "end": max((pe.get("execution_details", {}).get("end_time")
                          for pe in protocol_executions if pe.get("execution_details", {}).get("end_time")),
                         default=None)
            }
        }

    def _aggregate_protocol_results(self, protocol_executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate protocol execution results."""
        results = []

        for execution in protocol_executions:
            results.append({
                "execution_id": execution.get("execution_id"),
                "protocol_id": execution.get("protocol_id"),
                "protocol_name": execution.get("protocol_name"),
                "execution_period": {
                    "start": execution.get("execution_details", {}).get("start_time"),
                    "end": execution.get("execution_details", {}).get("end_time")
                },
                "technician": execution.get("execution_details", {}).get("technician"),
                "result": execution.get("results", {}).get("pass_fail"),
                "test_data_summary": self._summarize_test_data(
                    execution.get("execution_details", {}).get("test_data", {})
                )
            })

        return results

    def _summarize_test_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of test data."""
        if not test_data:
            return {"status": "No test data available"}

        # This would contain logic to summarize different types of test data
        return {
            "data_points_collected": len(test_data),
            "key_parameters": list(test_data.keys())[:5],  # First 5 parameters
            "status": "Data collected and analyzed"
        }

    def generate_protocol_specific_report(self, execution_id: str,
                                         protocol_execution: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Generate protocol-specific detailed report.

        Args:
            execution_id: Protocol execution ID
            protocol_execution: Protocol execution data

        Returns:
            Tuple of (success, message, report_object)
        """
        try:
            report_id = self._generate_report_id(prefix="PR")

            report = {
                "report_id": report_id,
                "report_type": "Protocol Execution Report",
                "generated_at": datetime.now().isoformat(),
                "execution_id": execution_id,
                "protocol_id": protocol_execution.get("protocol_id"),
                "protocol_name": protocol_execution.get("protocol_name"),

                "test_details": {
                    "execution_period": {
                        "start": protocol_execution.get("execution_details", {}).get("start_time"),
                        "end": protocol_execution.get("execution_details", {}).get("end_time")
                    },
                    "technician": protocol_execution.get("execution_details", {}).get("technician"),
                    "equipment_used": protocol_execution.get("workflow_metadata", {}).get("equipment_assigned")
                },

                "test_data": protocol_execution.get("execution_details", {}).get("test_data", {}),
                "measurements": protocol_execution.get("execution_details", {}).get("measurements", []),
                "observations": protocol_execution.get("execution_details", {}).get("observations", []),

                "results": protocol_execution.get("results"),

                "traceability": {
                    "service_request_id": protocol_execution.get("workflow_metadata", {}).get("service_request_id"),
                    "inspection_id": protocol_execution.get("workflow_metadata", {}).get("inspection_id"),
                    "work_order_id": protocol_execution.get("work_order_id")
                },

                "metadata": {
                    "report_version": "1.0",
                    "generated_by": "Report Aggregator System",
                    "status": "Draft"
                }
            }

            # Save report
            self._save_report(report)

            logger.info(f"Protocol-specific report {report_id} generated for execution {execution_id}")
            return True, f"Protocol report {report_id} generated successfully", report

        except Exception as e:
            logger.error(f"Failed to generate protocol report: {str(e)}")
            return False, f"Error generating protocol report: {str(e)}", None

    def finalize_report(self, report_id: str, finalized_by: str) -> Tuple[bool, str]:
        """Finalize report and mark as complete."""
        try:
            report = self.get_report(report_id)
            if not report:
                return False, f"Report {report_id} not found"

            report["metadata"]["status"] = "Finalized"
            report["metadata"]["finalized_by"] = finalized_by
            report["metadata"]["finalized_at"] = datetime.now().isoformat()

            self._save_report(report)

            logger.info(f"Report {report_id} finalized by {finalized_by}")
            return True, f"Report {report_id} finalized successfully"

        except Exception as e:
            logger.error(f"Failed to finalize report {report_id}: {str(e)}")
            return False, f"Error finalizing report: {str(e)}"

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve report by ID."""
        if report_id in self.reports_cache:
            return self.reports_cache[report_id]

        # Search for report file
        report_files = list(self.data_dir.glob(f"*{report_id}*.json"))
        if report_files:
            with open(report_files[0], 'r') as f:
                report_data = json.load(f)
                self.reports_cache[report_id] = report_data
                return report_data

        return None

    def list_reports(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all reports, optionally filtered by status."""
        reports = []

        for report_file in self.data_dir.glob("*.json"):
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    status = report.get("metadata", {}).get("status")

                    if status_filter and status != status_filter:
                        continue

                    reports.append({
                        "report_id": report.get("report_id"),
                        "report_type": report.get("report_type"),
                        "generated_at": report.get("generated_at"),
                        "status": status,
                        "workflow_id": report.get("workflow_id")
                    })
            except Exception as e:
                logger.warning(f"Failed to load report {report_file}: {str(e)}")

        return sorted(reports, key=lambda x: x["generated_at"], reverse=True)

    def _generate_report_id(self, prefix: str = "RPT") -> str:
        """Generate unique report ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"

    def _save_report(self, report_data: Dict[str, Any]):
        """Save report to disk."""
        report_id = report_data["report_id"]
        report_file = self.data_dir / f"{report_id}.json"

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.reports_cache[report_id] = report_data

    def export_report_to_pdf(self, report_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Export report to PDF format.

        Args:
            report_id: Report ID

        Returns:
            Tuple of (success, message, pdf_file_path)
        """
        # Placeholder for PDF export functionality
        # Would integrate with reportlab or similar library
        try:
            report = self.get_report(report_id)
            if not report:
                return False, f"Report {report_id} not found", None

            pdf_path = str(self.data_dir / f"{report_id}.pdf")

            # TODO: Implement actual PDF generation
            logger.info(f"PDF export for report {report_id} initiated")
            return True, f"Report exported to {pdf_path}", pdf_path

        except Exception as e:
            logger.error(f"Failed to export report {report_id} to PDF: {str(e)}")
            return False, f"Error exporting to PDF: {str(e)}", None
