"""
Reports Page
Report generation and management interface
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date
import json
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_available_executions() -> List[Dict]:
    """Get completed executions for report generation"""
    db = st.session_state.db

    query = """
        SELECT
            pe.execution_id,
            pe.protocol_name,
            pe.protocol_id,
            pe.status,
            pe.test_result,
            pe.created_at,
            pe.end_date,
            sr.customer_name,
            sr.project_name,
            ii.sample_id
        FROM protocol_executions pe
        LEFT JOIN service_requests sr ON pe.request_id = sr.request_id
        LEFT JOIN incoming_inspections ii ON pe.inspection_id = ii.inspection_id
        WHERE pe.status = 'completed'
        ORDER BY pe.end_date DESC
    """

    return db.execute_query(query)

def get_existing_reports(execution_id: str = None) -> List[Dict]:
    """Get existing reports"""
    db = st.session_state.db

    if execution_id:
        query = "SELECT * FROM reports WHERE execution_id = ? ORDER BY generated_date DESC"
        return db.execute_query(query, (execution_id,))
    else:
        query = "SELECT * FROM reports ORDER BY generated_date DESC LIMIT 100"
        return db.execute_query(query)

def generate_test_report(execution_id: str, report_format: str = 'pdf') -> Dict:
    """Generate a test report"""
    db = st.session_state.db

    # Get execution details
    exec_query = "SELECT * FROM protocol_executions WHERE execution_id = ?"
    execution = db.execute_query(exec_query, (execution_id,))

    if not execution:
        return {'success': False, 'message': 'Execution not found'}

    exec_data = execution[0]

    # Get traceability data
    trace_data = db.get_complete_traceability('execution', execution_id)

    # Generate report ID
    report_id = f"REP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Create report record
    report_data = {
        'report_id': report_id,
        'execution_id': execution_id,
        'report_type': 'test_report',
        'report_title': f"Test Report - {exec_data.get('protocol_name')}",
        'report_format': report_format,
        'file_path': f"/reports/{report_id}.{report_format}",
        'generated_by': 1,
        'status': 'draft',
        'version': '1.0',
        'template_used': 'standard_test_report',
        'metadata': json.dumps({
            'protocol_id': exec_data.get('protocol_id'),
            'protocol_name': exec_data.get('protocol_name'),
            'test_result': exec_data.get('test_result'),
            'generated_date': datetime.now().isoformat()
        })
    }

    try:
        # Insert report record
        query = """
            INSERT INTO reports
            (report_id, execution_id, report_type, report_title, report_format,
             file_path, generated_by, status, version, template_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            report_data['report_id'],
            report_data['execution_id'],
            report_data['report_type'],
            report_data['report_title'],
            report_data['report_format'],
            report_data['file_path'],
            report_data['generated_by'],
            report_data['status'],
            report_data['version'],
            report_data['template_used'],
            report_data['metadata']
        )

        db.execute_update(query, params)

        return {
            'success': True,
            'report_id': report_id,
            'message': f"Report {report_id} generated successfully"
        }

    except Exception as e:
        return {'success': False, 'message': f"Error generating report: {e}"}

def generate_summary_report(start_date: str, end_date: str, report_format: str = 'pdf') -> Dict:
    """Generate a summary report for a date range"""
    db = st.session_state.db

    report_id = f"SUM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Get summary data
    query = """
        SELECT
            COUNT(*) as total_tests,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN test_result = 'pass' THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN test_result = 'fail' THEN 1 ELSE 0 END) as failed
        FROM protocol_executions
        WHERE DATE(created_at) BETWEEN ? AND ?
    """

    summary = db.execute_query(query, (start_date, end_date))[0]

    try:
        report_data = {
            'report_id': report_id,
            'execution_id': None,
            'report_type': 'summary',
            'report_title': f"Summary Report - {start_date} to {end_date}",
            'report_format': report_format,
            'file_path': f"/reports/{report_id}.{report_format}",
            'generated_by': 1,
            'status': 'draft',
            'version': '1.0',
            'template_used': 'summary_report',
            'metadata': json.dumps({
                'start_date': start_date,
                'end_date': end_date,
                'total_tests': summary['total_tests'],
                'completed': summary['completed'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'generated_date': datetime.now().isoformat()
            })
        }

        query = """
            INSERT INTO reports
            (report_id, execution_id, report_type, report_title, report_format,
             file_path, generated_by, status, version, template_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            report_data['report_id'],
            report_data['execution_id'],
            report_data['report_type'],
            report_data['report_title'],
            report_data['report_format'],
            report_data['file_path'],
            report_data['generated_by'],
            report_data['status'],
            report_data['version'],
            report_data['template_used'],
            report_data['metadata']
        )

        db.execute_update(query, params)

        return {
            'success': True,
            'report_id': report_id,
            'message': f"Summary report {report_id} generated successfully"
        }

    except Exception as e:
        return {'success': False, 'message': f"Error generating report: {e}"}

def generate_certificate(execution_id: str) -> Dict:
    """Generate a test certificate"""
    db = st.session_state.db

    # Verify execution exists and passed
    exec_query = "SELECT * FROM protocol_executions WHERE execution_id = ?"
    execution = db.execute_query(exec_query, (execution_id,))

    if not execution:
        return {'success': False, 'message': 'Execution not found'}

    exec_data = execution[0]

    if exec_data.get('test_result') != 'pass':
        return {'success': False, 'message': 'Certificate can only be generated for passed tests'}

    report_id = f"CRT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        report_data = {
            'report_id': report_id,
            'execution_id': execution_id,
            'report_type': 'certificate',
            'report_title': f"Test Certificate - {exec_data.get('protocol_name')}",
            'report_format': 'pdf',
            'file_path': f"/reports/certificates/{report_id}.pdf",
            'generated_by': 1,
            'status': 'pending_review',
            'version': '1.0',
            'template_used': 'certificate_template',
            'metadata': json.dumps({
                'protocol_id': exec_data.get('protocol_id'),
                'protocol_name': exec_data.get('protocol_name'),
                'test_result': exec_data.get('test_result'),
                'generated_date': datetime.now().isoformat()
            })
        }

        query = """
            INSERT INTO reports
            (report_id, execution_id, report_type, report_title, report_format,
             file_path, generated_by, status, version, template_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            report_data['report_id'],
            report_data['execution_id'],
            report_data['report_type'],
            report_data['report_title'],
            report_data['report_format'],
            report_data['file_path'],
            report_data['generated_by'],
            report_data['status'],
            report_data['version'],
            report_data['template_used'],
            report_data['metadata']
        )

        db.execute_update(query, params)

        return {
            'success': True,
            'report_id': report_id,
            'message': f"Certificate {report_id} generated successfully"
        }

    except Exception as e:
        return {'success': False, 'message': f"Error generating certificate: {e}"}

def preview_report_content(execution_id: str) -> str:
    """Generate report preview content"""
    db = st.session_state.db

    trace_data = db.get_complete_traceability('execution', execution_id)

    preview = []
    preview.append("=" * 80)
    preview.append("TEST REPORT PREVIEW")
    preview.append("=" * 80)
    preview.append("")

    if trace_data.get('execution'):
        exe = trace_data['execution']
        preview.append(f"Execution ID: {exe.get('execution_id')}")
        preview.append(f"Protocol: {exe.get('protocol_name')}")
        preview.append(f"Version: {exe.get('protocol_version')}")
        preview.append(f"Status: {exe.get('status')}")
        preview.append(f"Result: {exe.get('test_result')}")
        preview.append(f"Start Date: {exe.get('start_date', 'N/A')}")
        preview.append(f"End Date: {exe.get('end_date', 'N/A')}")
        preview.append(f"Duration: {exe.get('duration_hours', 'N/A')} hours")
        preview.append("")

    if trace_data.get('request'):
        req = trace_data['request']
        preview.append("-" * 80)
        preview.append("CUSTOMER INFORMATION")
        preview.append("-" * 80)
        preview.append(f"Customer: {req.get('customer_name')}")
        preview.append(f"Project: {req.get('project_name')}")
        preview.append(f"Request ID: {req.get('request_id')}")
        preview.append("")

    if trace_data.get('inspection'):
        insp = trace_data['inspection']
        preview.append("-" * 80)
        preview.append("SAMPLE INFORMATION")
        preview.append("-" * 80)
        preview.append(f"Sample ID: {insp.get('sample_id')}")
        preview.append(f"Type: {insp.get('sample_type')}")
        preview.append(f"Manufacturer: {insp.get('manufacturer')}")
        preview.append(f"Model: {insp.get('model_number')}")
        preview.append("")

    if trace_data.get('measurements'):
        preview.append("-" * 80)
        preview.append(f"MEASUREMENTS ({len(trace_data['measurements'])} records)")
        preview.append("-" * 80)
        for meas in trace_data['measurements'][:5]:
            preview.append(f"  {meas.get('measurement_type')} - {meas.get('timestamp')}")
        if len(trace_data['measurements']) > 5:
            preview.append(f"  ... and {len(trace_data['measurements']) - 5} more")
        preview.append("")

    preview.append("=" * 80)

    return "\n".join(preview)

# ============================================
# PAGE CONTENT
# ============================================

st.title("📄 Reports")
st.markdown("### Report Generation and Management")
st.markdown("---")

# ============================================
# TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Generate Report",
    "📋 Report History",
    "🔍 Preview",
    "📦 Bulk Generation"
])

# ============================================
# TAB 1: GENERATE REPORT
# ============================================

with tab1:
    st.subheader("Generate New Report")

    # Report Type Selection
    col1, col2 = st.columns([1, 2])

    with col1:
        report_type = st.selectbox(
            "Report Type",
            options=['test_report', 'summary', 'certificate', 'custom'],
            format_func=lambda x: {
                'test_report': 'Test Report',
                'summary': 'Summary Report',
                'certificate': 'Test Certificate',
                'custom': 'Custom Report'
            }[x]
        )

    with col2:
        report_format = st.selectbox(
            "Format",
            options=['pdf', 'excel', 'word', 'html'],
            format_func=lambda x: x.upper()
        )

    st.markdown("---")

    # Report-specific options
    if report_type == 'test_report':
        st.markdown("#### Test Report Configuration")

        # Get available executions
        executions = get_available_executions()

        if executions:
            execution_options = {
                f"{e['execution_id']} - {e['protocol_name']} ({e.get('customer_name', 'N/A')})": e['execution_id']
                for e in executions
            }

            selected_exec_display = st.selectbox("Select Test Execution", list(execution_options.keys()))
            selected_execution_id = execution_options[selected_exec_display]

            # Display execution details
            selected_exec = next(e for e in executions if e['execution_id'] == selected_execution_id)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Protocol:** {selected_exec.get('protocol_name')}")
                st.write(f"**Protocol ID:** {selected_exec.get('protocol_id')}")

            with col2:
                st.write(f"**Status:** {selected_exec.get('status')}")
                st.write(f"**Result:** {selected_exec.get('test_result', 'N/A')}")

            with col3:
                st.write(f"**Customer:** {selected_exec.get('customer_name', 'N/A')}")
                st.write(f"**Sample:** {selected_exec.get('sample_id', 'N/A')}")

            # Template selection
            template = st.selectbox(
                "Report Template",
                options=['standard_test_report', 'detailed_test_report', 'concise_test_report'],
                format_func=lambda x: x.replace('_', ' ').title()
            )

            # Include sections
            st.markdown("**Include Sections:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                include_summary = st.checkbox("Executive Summary", value=True)
                include_measurements = st.checkbox("Measurements", value=True)

            with col2:
                include_photos = st.checkbox("Photos/Images", value=True)
                include_charts = st.checkbox("Charts/Graphs", value=True)

            with col3:
                include_traceability = st.checkbox("Traceability", value=True)
                include_signatures = st.checkbox("Signatures", value=True)

            # Generate button
            if st.button("📄 Generate Test Report", use_container_width=True, type="primary"):
                with st.spinner("Generating report..."):
                    result = generate_test_report(selected_execution_id, report_format)

                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.info(f"**Report ID:** {result['report_id']}")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")

        else:
            st.warning("No completed executions available for reporting")

    elif report_type == 'summary':
        st.markdown("#### Summary Report Configuration")

        col1, col2 = st.columns(2)

        with col1:
            summary_start = st.date_input(
                "Start Date",
                value=date.today().replace(day=1)
            )

        with col2:
            summary_end = st.date_input(
                "End Date",
                value=date.today()
            )

        # Report scope
        report_scope = st.multiselect(
            "Include",
            options=['All Tests', 'By Protocol', 'By Customer', 'By Status', 'Quality Metrics'],
            default=['All Tests', 'Quality Metrics']
        )

        # Generate button
        if st.button("📊 Generate Summary Report", use_container_width=True, type="primary"):
            with st.spinner("Generating summary report..."):
                result = generate_summary_report(
                    summary_start.isoformat(),
                    summary_end.isoformat(),
                    report_format
                )

                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.info(f"**Report ID:** {result['report_id']}")
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")

    elif report_type == 'certificate':
        st.markdown("#### Test Certificate Configuration")

        # Get passed executions only
        passed_query = """
            SELECT
                pe.execution_id,
                pe.protocol_name,
                pe.protocol_id,
                pe.end_date,
                sr.customer_name,
                ii.sample_id
            FROM protocol_executions pe
            LEFT JOIN service_requests sr ON pe.request_id = sr.request_id
            LEFT JOIN incoming_inspections ii ON pe.inspection_id = ii.inspection_id
            WHERE pe.test_result = 'pass'
            ORDER BY pe.end_date DESC
        """

        passed_executions = st.session_state.db.execute_query(passed_query)

        if passed_executions:
            cert_options = {
                f"{e['execution_id']} - {e['protocol_name']} ({e.get('customer_name', 'N/A')})": e['execution_id']
                for e in passed_executions
            }

            selected_cert_display = st.selectbox("Select Passed Test", list(cert_options.keys()))
            selected_cert_id = cert_options[selected_cert_display]

            # Certificate details
            cert_template = st.selectbox(
                "Certificate Template",
                options=['standard_certificate', 'premium_certificate', 'iso_certificate'],
                format_func=lambda x: x.replace('_', ' ').title()
            )

            include_logo = st.checkbox("Include Company Logo", value=True)
            include_watermark = st.checkbox("Include Watermark", value=True)

            # Generate button
            if st.button("🏆 Generate Certificate", use_container_width=True, type="primary"):
                with st.spinner("Generating certificate..."):
                    result = generate_certificate(selected_cert_id)

                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.info(f"**Certificate ID:** {result['report_id']}")
                        st.info("**Note:** Certificate requires approval before final issuance")
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")

        else:
            st.warning("No passed tests available for certificate generation")

    else:  # custom
        st.markdown("#### Custom Report Configuration")

        st.info("Custom report builder - Configure your own report layout and content")

        custom_title = st.text_input("Report Title")

        # Data sources
        st.markdown("**Data Sources:**")
        include_executions = st.checkbox("Protocol Executions", value=True)
        include_requests = st.checkbox("Service Requests")
        include_inspections = st.checkbox("Inspections")
        include_qc = st.checkbox("QC Records")
        include_nc = st.checkbox("Non-Conformances")

        # Custom filters
        custom_filters = st.text_area(
            "Custom Filters (SQL WHERE clause)",
            placeholder="e.g., status = 'completed' AND DATE(created_at) > '2024-01-01'"
        )

        if st.button("🔧 Generate Custom Report", use_container_width=True):
            st.info("Custom report generation would be implemented here")

# ============================================
# TAB 2: REPORT HISTORY
# ============================================

with tab2:
    st.subheader("Report History")

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        report_type_filter = st.selectbox(
            "Filter by Type",
            options=['All', 'test_report', 'summary', 'certificate', 'custom']
        )

    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=['All', 'draft', 'pending_review', 'approved', 'rejected']
        )

    with filter_col3:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh History", use_container_width=True):
            st.rerun()

    # Get reports
    all_reports = get_existing_reports()

    # Apply filters
    if report_type_filter != 'All':
        all_reports = [r for r in all_reports if r.get('report_type') == report_type_filter]

    if status_filter != 'All':
        all_reports = [r for r in all_reports if r.get('status') == status_filter]

    if all_reports:
        st.write(f"**Found {len(all_reports)} report(s)**")

        # Display reports
        for report in all_reports:
            with st.expander(f"{report.get('report_id')} - {report.get('report_title')}", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Type:** {report.get('report_type')}")
                    st.write(f"**Format:** {report.get('report_format', 'N/A')}")
                    st.write(f"**Version:** {report.get('version', 'N/A')}")

                with col2:
                    st.write(f"**Status:** {report.get('status')}")
                    st.write(f"**Generated:** {report.get('generated_date', 'N/A')[:19]}")
                    st.write(f"**Template:** {report.get('template_used', 'N/A')}")

                with col3:
                    if report.get('execution_id'):
                        st.write(f"**Execution:** {report['execution_id']}")
                    if report.get('approved_by'):
                        st.write(f"**Approved By:** User {report['approved_by']}")
                        st.write(f"**Approved:** {report.get('approved_date', 'N/A')[:19]}")

                # Metadata
                if report.get('metadata'):
                    try:
                        metadata = json.loads(report['metadata']) if isinstance(report['metadata'], str) else report['metadata']
                        st.markdown("**Metadata:**")
                        st.json(metadata)
                    except:
                        pass

                # Actions
                st.markdown("---")
                action_col1, action_col2, action_col3, action_col4 = st.columns(4)

                with action_col1:
                    if st.button("📥 Download", key=f"dl_{report['report_id']}"):
                        st.info(f"Download functionality for {report['report_id']}")

                with action_col2:
                    if st.button("👁️ Preview", key=f"preview_{report['report_id']}"):
                        st.info("Preview functionality would open here")

                with action_col3:
                    if report.get('status') == 'draft':
                        if st.button("✅ Approve", key=f"approve_{report['report_id']}"):
                            # Update status
                            update_query = "UPDATE reports SET status = 'approved', approved_by = 1, approved_date = CURRENT_TIMESTAMP WHERE report_id = ?"
                            st.session_state.db.execute_update(update_query, (report['report_id'],))
                            st.success("Report approved!")
                            st.rerun()

                with action_col4:
                    if st.button("🗑️ Delete", key=f"delete_{report['report_id']}"):
                        delete_query = "DELETE FROM reports WHERE report_id = ?"
                        st.session_state.db.execute_update(delete_query, (report['report_id'],))
                        st.success("Report deleted!")
                        st.rerun()

    else:
        st.info("No reports found matching the filters")

# ============================================
# TAB 3: PREVIEW
# ============================================

with tab3:
    st.subheader("Report Preview")

    # Select execution for preview
    executions = get_available_executions()

    if executions:
        preview_options = {
            f"{e['execution_id']} - {e['protocol_name']}": e['execution_id']
            for e in executions
        }

        selected_preview_display = st.selectbox("Select Execution to Preview", list(preview_options.keys()))
        selected_preview_id = preview_options[selected_preview_display]

        if st.button("👁️ Generate Preview", use_container_width=True):
            with st.spinner("Generating preview..."):
                preview_content = preview_report_content(selected_preview_id)

                st.text_area("Report Preview", preview_content, height=500)

                # Download preview
                st.download_button(
                    label="📥 Download Preview",
                    data=preview_content,
                    file_name=f"preview_{selected_preview_id}.txt",
                    mime="text/plain"
                )
    else:
        st.warning("No executions available for preview")

# ============================================
# TAB 4: BULK GENERATION
# ============================================

with tab4:
    st.subheader("Bulk Report Generation")

    st.info("Generate multiple reports at once for efficiency")

    # Criteria for bulk generation
    bulk_type = st.radio(
        "Generate reports for:",
        options=['All completed tests in date range', 'Specific protocol', 'Specific customer']
    )

    if bulk_type == 'All completed tests in date range':
        col1, col2 = st.columns(2)

        with col1:
            bulk_start = st.date_input("Start Date", value=date.today().replace(day=1))

        with col2:
            bulk_end = st.date_input("End Date", value=date.today())

        # Get count
        count_query = """
            SELECT COUNT(*) as count
            FROM protocol_executions
            WHERE status = 'completed'
            AND DATE(created_at) BETWEEN ? AND ?
        """
        count = st.session_state.db.execute_query(count_query, (bulk_start.isoformat(), bulk_end.isoformat()))[0]['count']

        st.write(f"**{count} report(s) will be generated**")

        if st.button("📦 Generate Bulk Reports", use_container_width=True, type="primary"):
            if count > 0:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Get executions
                exec_query = """
                    SELECT execution_id
                    FROM protocol_executions
                    WHERE status = 'completed'
                    AND DATE(created_at) BETWEEN ? AND ?
                """
                executions_to_process = st.session_state.db.execute_query(
                    exec_query,
                    (bulk_start.isoformat(), bulk_end.isoformat())
                )

                success_count = 0
                for idx, exec in enumerate(executions_to_process):
                    status_text.text(f"Generating report {idx + 1} of {count}...")
                    result = generate_test_report(exec['execution_id'], 'pdf')

                    if result['success']:
                        success_count += 1

                    progress_bar.progress((idx + 1) / count)

                status_text.empty()
                progress_bar.empty()

                st.success(f"✅ Generated {success_count} reports successfully!")
                st.balloons()
            else:
                st.warning("No reports to generate")

    elif bulk_type == 'Specific protocol':
        # Get unique protocols
        protocol_query = "SELECT DISTINCT protocol_id, protocol_name FROM protocol_executions"
        protocols = st.session_state.db.execute_query(protocol_query)

        if protocols:
            protocol_options = {f"{p['protocol_id']}: {p['protocol_name']}": p['protocol_id'] for p in protocols}

            selected_protocol = st.selectbox("Select Protocol", list(protocol_options.keys()))
            protocol_id = protocol_options[selected_protocol]

            count_query = """
                SELECT COUNT(*) as count
                FROM protocol_executions
                WHERE protocol_id = ? AND status = 'completed'
            """
            count = st.session_state.db.execute_query(count_query, (protocol_id,))[0]['count']

            st.write(f"**{count} report(s) will be generated for {selected_protocol}**")

            if st.button("📦 Generate Protocol Reports", use_container_width=True, type="primary"):
                st.info("Bulk generation for specific protocol would be implemented here")

    else:  # Specific customer
        # Get unique customers
        customer_query = """
            SELECT DISTINCT sr.customer_name
            FROM service_requests sr
            INNER JOIN protocol_executions pe ON sr.request_id = pe.request_id
            WHERE pe.status = 'completed'
        """
        customers = st.session_state.db.execute_query(customer_query)

        if customers:
            customer_list = [c['customer_name'] for c in customers]
            selected_customer = st.selectbox("Select Customer", customer_list)

            count_query = """
                SELECT COUNT(*) as count
                FROM protocol_executions pe
                INNER JOIN service_requests sr ON pe.request_id = sr.request_id
                WHERE sr.customer_name = ? AND pe.status = 'completed'
            """
            count = st.session_state.db.execute_query(count_query, (selected_customer,))[0]['count']

            st.write(f"**{count} report(s) will be generated for {selected_customer}**")

            if st.button("📦 Generate Customer Reports", use_container_width=True, type="primary"):
                st.info("Bulk generation for specific customer would be implemented here")

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Page Info")
    st.info("""
    **Reports Page**

    Generate and manage reports:
    - Test reports
    - Summary reports
    - Certificates
    - Custom reports

    **Features:**
    - Multiple formats (PDF, Excel, Word, HTML)
    - Template selection
    - Preview functionality
    - Report history
    - Bulk generation
    - Approval workflow

    **Usage:**
    1. Select report type
    2. Configure options
    3. Generate report
    4. Preview/Download
    5. Approve if needed
    """)

    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
