"""
Report Generation Module - Auto PDF Reports & Custom Templates
================================================================
Comprehensive report generation system with PDF creation, custom templates,
digital signatures, and multi-language support.

Features:
- Auto PDF Report Generation
- Custom Report Templates
- Digital Signatures
- Multi-Language Support
- Scheduled Report Generation
- Email Distribution
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import io
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from components.report_generator import (
    PDFReportGenerator, ExcelReportGenerator,
    REPORTLAB_AVAILABLE, OPENPYXL_AVAILABLE
)
from database import (
    Sample, TestExecution, ServiceRequest, TestProtocol,
    CompanyProfile, SampleStatus, TestStatus,
    ReportTemplate, GeneratedReport, ScheduledReport
)
from sqlalchemy import select, desc
from sqlalchemy.orm import load_only
import json

# Page configuration
setup_page_config(page_title="Report Generation", page_icon="📝")

# Render navigation
render_header("Report Generation", "Auto PDF Reports & Custom Templates")
render_sidebar_navigation()


def main():
    """Main report generation page"""
    
    # Create reports directory if it doesn't exist
    reports_dir = Path(project_root) / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Generate Report",
        "📋 Templates",
        "⏰ Scheduled",
        "📚 History"
    ])

    with tab1:
        render_generate_report(reports_dir)

    with tab2:
        render_templates()

    with tab3:
        render_scheduled_reports()

    with tab4:
        render_report_history()


def render_generate_report(reports_dir):
    """Render the Generate Report tab"""
    
    st.subheader("🎯 Generate New Report")
    
    # Template selection
    with get_db() as db:
        templates = db.execute(
            select(ReportTemplate)
            .where(ReportTemplate.is_active == True)
            .order_by(ReportTemplate.template_name)
        ).scalars().all()
        
        template_options = {
            t.template_id: f"{t.template_name} (v{t.version or '1.0'})"
            for t in templates
        }
        
        # Create default templates if none exist
        if not template_options:
            _create_default_templates(db)
            templates = db.execute(
                select(ReportTemplate)
                .where(ReportTemplate.is_active == True)
            ).scalars().all()
            template_options = {
                t.template_id: f"{t.template_name} (v{t.version or '1.0'})"
                for t in templates
            }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_template_id = st.selectbox(
            "📋 Select Template",
            options=list(template_options.keys()) if template_options else ["default"],
            format_func=lambda x: template_options.get(x, "Default Template"),
            help="Choose a report template"
        )
    
    with col2:
        language = st.selectbox(
            "🌐 Report Language",
            options=["English", "Hindi", "Spanish"],
            help="Select report language"
        )
    
    st.divider()
    
    # Sample/Test selection
    st.markdown("#### 📦 Select Data for Report")
    
    with get_db() as db:
        # Get samples for reporting - exclude specifications column which may not exist in DB
        samples = db.execute(
            select(Sample)
            .options(load_only(
                Sample.id, Sample.sample_id, Sample.manufacturer, Sample.model_number,
                Sample.status, Sample.created_at
            ))
            .where(Sample.status.in_([
                SampleStatus.COMPLETED,
                SampleStatus.ANALYZED,
                SampleStatus.REPORTED
            ]))
            .order_by(desc(Sample.created_at))
            .limit(100)
        ).scalars().all()

        sample_options = {
            s.sample_id: f"{s.sample_id} - {s.manufacturer or 'N/A'} {s.model_number or ''}"
            for s in samples
        }
    
    if not sample_options:
        st.info("ℹ️ No completed samples available for reporting")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_samples = st.multiselect(
            "Select Samples",
            options=list(sample_options.keys()),
            format_func=lambda x: sample_options.get(x, x),
            help="Select one or more samples to include in the report"
        )
    
    with col2:
        if selected_samples:
            with get_db() as db:
                # Get tests for selected samples
                # TestExecution.sample_id is a string field, not FK, so query directly
                test_executions = db.execute(
                    select(TestExecution)
                    .where(TestExecution.sample_id.in_(selected_samples))
                    .where(TestExecution.status == TestStatus.COMPLETED)
                ).scalars().all()
                
                test_options = {
                    t.execution_number: f"{t.execution_number} - {t.protocol_id or 'N/A'}"
                    for t in test_executions
                }
                
                selected_tests = st.multiselect(
                    "Select Tests (Optional - leave empty for all)",
                    options=list(test_options.keys()),
                    format_func=lambda x: test_options.get(x, x),
                    help="Select specific tests or leave empty to include all"
                )
    
    st.divider()
    
    # Report options
    st.markdown("#### ⚙️ Report Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_charts = st.checkbox("📊 Include Charts", value=True)
        include_raw_data = st.checkbox("📋 Include Raw Data", value=False)
    
    with col2:
        include_photos = st.checkbox("📷 Include Photos", value=True)
        digital_signature = st.checkbox("✍️ Add Digital Signature", value=False)
    
    with col3:
        report_format = st.selectbox(
            "File Format",
            options=["PDF", "Excel", "Both"],
            help="Select output format"
        )
    
    st.divider()
    
    # Generate buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👁️ Preview Report", use_container_width=True):
            if not selected_samples:
                st.warning("⚠️ Please select at least one sample")
            else:
                _preview_report(selected_samples, language)
    
    with col2:
        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
            if not selected_samples:
                st.warning("⚠️ Please select at least one sample")
            else:
                with st.spinner("🔄 Generating report..."):
                    success = _generate_report(
                        template_id=selected_template_id,
                        sample_ids=selected_samples,
                        test_ids=selected_tests if 'selected_tests' in locals() else [],
                        language=language,
                        include_charts=include_charts,
                        include_raw_data=include_raw_data,
                        include_photos=include_photos,
                        digital_signature=digital_signature,
                        report_format=report_format,
                        reports_dir=reports_dir
                    )
                    
                    if success:
                        st.success("✅ Report generated successfully!")
                        st.balloons()


def _generate_report(template_id, sample_ids, test_ids, language, include_charts,
                     include_raw_data, include_photos, digital_signature,
                     report_format, reports_dir):
    """Generate the actual PDF/Excel report"""
    
    try:
        with get_db() as db:
            # Get samples and tests - exclude specifications column which may not exist in DB
            samples = db.execute(
                select(Sample)
                .options(load_only(
                    Sample.id, Sample.sample_id, Sample.manufacturer, Sample.model_number,
                    Sample.serial_number, Sample.status, Sample.tests_completed, Sample.tests_total,
                    Sample.overall_result, Sample.created_at, Sample.updated_at
                ))
                .where(Sample.sample_id.in_(sample_ids))
            ).scalars().all()
            
            if not samples:
                st.error("❌ No samples found")
                return False
            
            # Get test executions
            # TestExecution.sample_id is a string field, not FK, so query directly
            test_executions = db.execute(
                select(TestExecution)
                .where(TestExecution.sample_id.in_(sample_ids))
                .where(TestExecution.status == TestStatus.COMPLETED)
            ).scalars().all()
            
            if test_ids:
                test_executions = [t for t in test_executions if t.execution_number in test_ids]
            
            # Get company profile
            company = CompanyProfile.get_default(db)
            
            # Prepare report data
            test_data = {
                'title': f"Test Report - {', '.join(sample_ids)}",
                'protocol_id': test_executions[0].protocol_id if test_executions else 'N/A',
                'protocol_name': 'Multi-Sample Test Report',
                'sample_id': ', '.join(sample_ids),
                'test_date': datetime.now().strftime('%Y-%m-%d'),
                'operator': st.session_state.get('username', 'System'),
                'equipment': 'Various',
                'conditions': 'Standard Laboratory Conditions',
                'language': language
            }
            
            # Prepare results data
            results_data = []
            for test in test_executions:
                if test.results:
                    try:
                        results = json.loads(test.results) if isinstance(test.results, str) else test.results
                        if isinstance(results, list):
                            results_data.extend(results)
                        elif isinstance(results, dict):
                            results_data.append(results)
                    except:
                        pass
            
            # Generate report ID and number
            report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            existing_reports = db.execute(select(GeneratedReport)).scalars().all()
            report_number = f"TEST-RPT-{len(existing_reports) + 1:05d}"
            
            pdf_bytes = None
            excel_bytes = None
            file_paths = []
            total_size = 0
            
            # Generate PDF
            if report_format in ["PDF", "Both"] and REPORTLAB_AVAILABLE:
                generator = PDFReportGenerator()
                pdf_bytes = generator.generate_test_report(test_data, results_data, include_charts)
                
                if pdf_bytes:
                    pdf_path = reports_dir / f"{report_id}.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_bytes)
                    file_paths.append(str(pdf_path))
                    total_size += len(pdf_bytes)
                    
                    # Offer download
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{report_number}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            # Generate Excel
            if report_format in ["Excel", "Both"] and OPENPYXL_AVAILABLE:
                generator = ExcelReportGenerator()
                excel_bytes = generator.generate_test_report(test_data, results_data)
                
                if excel_bytes:
                    excel_path = reports_dir / f"{report_id}.xlsx"
                    with open(excel_path, 'wb') as f:
                        f.write(excel_bytes)
                    file_paths.append(str(excel_path))
                    total_size += len(excel_bytes)
                    
                    # Offer download
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_bytes,
                        file_name=f"{report_number}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            # Save to database
            signatures_data = []
            if digital_signature:
                signatures_data.append({
                    'role': 'Generated By',
                    'name': st.session_state.get('username', 'System'),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'Pending'
                })
            
            report = GeneratedReport(
                report_id=report_id,
                report_number=report_number,
                report_title=test_data['title'],
                template_id=template_id,
                sample_ids=sample_ids,
                test_ids=test_ids,
                file_path=', '.join(file_paths),
                file_size=total_size,
                language=language,
                status='Draft' if digital_signature else 'Generated',
                signatures=signatures_data if signatures_data else None,
                generated_by=st.session_state.get('username', 'System')
            )
            
            db.add(report)
            db.commit()
            
            # Update sample status
            for sample in samples:
                if sample.status != SampleStatus.REPORTED:
                    sample_record = db.execute(
                        select(Sample)
                        .options(load_only(Sample.id, Sample.status))
                        .where(Sample.id == sample.id)
                    ).scalar()
                    if sample_record:
                        sample_record.status = SampleStatus.REPORTED
            
            db.commit()
            
            return True
            
    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False


def _preview_report(sample_ids, language):
    """Preview report content"""

    st.markdown("### 👁️ Report Preview")

    with get_db() as db:
        samples = db.execute(
            select(Sample)
            .options(load_only(
                Sample.id, Sample.sample_id, Sample.manufacturer, Sample.model_number,
                Sample.serial_number, Sample.status, Sample.tests_completed, Sample.tests_total,
                Sample.overall_result
            ))
            .where(Sample.sample_id.in_(sample_ids))
        ).scalars().all()
        
        for sample in samples:
            with st.expander(f"📦 {sample.sample_id}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")
                    st.markdown(f"**Model:** {sample.model_number or 'N/A'}")
                    st.markdown(f"**Serial:** {sample.serial_number or 'N/A'}")
                
                with col2:
                    st.markdown(f"**Status:** {sample.status.value.upper()}")
                    st.markdown(f"**Tests:** {sample.tests_completed}/{sample.tests_total}")
                    st.markdown(f"**Result:** {sample.overall_result or 'Pending'}")
                
                # Get test results
                test_executions = db.execute(
                    select(TestExecution)
                    .where(TestExecution.sample_id == sample.sample_id)
                    .where(TestExecution.status == TestStatus.COMPLETED)
                ).scalars().all()
                
                if test_executions:
                    st.markdown("**Test Results:**")
                    for test in test_executions:
                        result_icon = "✅" if test.test_passed else "❌" if test.test_passed == False else "⏳"
                        st.markdown(f"- {result_icon} {test.execution_number}: {test.protocol_id or 'N/A'}")


def render_templates():
    """Render the Templates management tab"""
    
    st.subheader("📋 Report Templates")
    
    with get_db() as db:
        templates = db.execute(
            select(ReportTemplate)
            .order_by(desc(ReportTemplate.created_at))
        ).scalars().all()
    
    # Display templates
    if templates:
        for template in templates:
            with st.expander(
                f"📄 {template.template_name} (v{template.version or '1.0'})",
                expanded=False
            ):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Type:** {template.template_type or 'Custom'}")
                    st.markdown(f"**Template ID:** {template.template_id}")
                    if template.description:
                        st.markdown(f"**Description:** {template.description}")
                    st.markdown(f"**Status:** {'🟢 Active' if template.is_active else '🔴 Inactive'}")
                
                with col2:
                    st.markdown(f"**Created:** {template.created_at.strftime('%Y-%m-%d') if template.created_at else 'N/A'}")
                    st.markdown(f"**By:** {template.created_by or 'System'}")
                
                with col3:
                    if st.button("✏️ Edit", key=f"edit_{template.id}"):
                        st.info("Template editing feature")
                    
                    if st.button("📋 Duplicate", key=f"dup_{template.id}"):
                        _duplicate_template(template)
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"del_{template.id}"):
                        with get_db() as db:
                            template_to_delete = db.execute(
                                select(ReportTemplate).where(ReportTemplate.id == template.id)
                            ).scalar()
                            if template_to_delete:
                                db.delete(template_to_delete)
                                db.commit()
                                st.success("Template deleted")
                                st.rerun()
    else:
        st.info("ℹ️ No templates found. Click 'Create New Template' to add one.")
    
    st.divider()
    
    # Create new template
    if st.button("➕ Create New Template", type="primary"):
        with st.form("new_template_form"):
            st.markdown("### Create New Template")
            
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.text_input("Template Name", value="New Template")
                template_type = st.selectbox(
                    "Template Type",
                    options=["IEC 61215", "IEC 61730", "NABL Format", "Custom"]
                )
            
            with col2:
                version = st.text_input("Version", value="1.0")
                description = st.text_area("Description")
            
            if st.form_submit_button("Create Template"):
                _create_template(template_name, template_type, version, description)
                st.success("✅ Template created successfully!")
                st.rerun()


def _create_template(name, template_type, version, description):
    """Create a new template"""
    
    with get_db() as db:
        template_id = f"TMPL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        template = ReportTemplate(
            template_id=template_id,
            template_name=name,
            template_type=template_type,
            version=version,
            description=description,
            header_content={'logo': True, 'company_name': True},
            body_sections=['summary', 'test_info', 'results', 'charts'],
            footer_content={'page_numbers': True, 'signatures': True},
            is_active=True,
            created_by=st.session_state.get('username', 'System')
        )
        
        db.add(template)
        db.commit()


def _duplicate_template(template):
    """Duplicate an existing template"""
    
    with get_db() as db:
        new_template_id = f"TMPL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        new_template = ReportTemplate(
            template_id=new_template_id,
            template_name=f"{template.template_name} (Copy)",
            template_type=template.template_type,
            version=template.version,
            description=template.description,
            header_content=template.header_content,
            body_sections=template.body_sections,
            footer_content=template.footer_content,
            logo_path=template.logo_path,
            color_scheme=template.color_scheme,
            is_active=True,
            created_by=st.session_state.get('username', 'System')
        )
        
        db.add(new_template)
        db.commit()


def _create_default_templates(db):
    """Create default templates if none exist"""
    
    templates_data = [
        {
            'template_id': 'TMPL-IEC61215',
            'template_name': 'IEC 61215 Test Report',
            'template_type': 'IEC 61215',
            'version': '1.0',
            'description': 'Standard template for IEC 61215 PV module testing'
        },
        {
            'template_id': 'TMPL-IEC61730',
            'template_name': 'IEC 61730 Safety Report',
            'template_type': 'IEC 61730',
            'version': '1.0',
            'description': 'Template for IEC 61730 safety qualification'
        },
        {
            'template_id': 'TMPL-NABL',
            'template_name': 'NABL Format Report',
            'template_type': 'NABL Format',
            'version': '1.0',
            'description': 'NABL compliant test report format'
        }
    ]
    
    for tmpl_data in templates_data:
        template = ReportTemplate(
            **tmpl_data,
            header_content={'logo': True, 'company_name': True, 'accreditation': True},
            body_sections=['summary', 'test_info', 'results', 'charts', 'conclusions'],
            footer_content={'page_numbers': True, 'signatures': True, 'lab_info': True},
            is_active=True,
            created_by='System'
        )
        db.add(template)
    
    db.commit()


def render_scheduled_reports():
    """Render the Scheduled Reports tab"""
    
    st.subheader("⏰ Scheduled Reports")
    
    with get_db() as db:
        schedules = db.execute(
            select(ScheduledReport)
            .order_by(desc(ScheduledReport.created_at))
        ).scalars().all()
    
    if schedules:
        for schedule in schedules:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {schedule.schedule_name}")
                st.markdown(f"**Frequency:** {schedule.frequency}")
                st.markdown(f"**Next Run:** {schedule.next_run.strftime('%Y-%m-%d %H:%M') if schedule.next_run else 'Not scheduled'}")
                if schedule.last_run:
                    st.markdown(f"**Last Run:** {schedule.last_run.strftime('%Y-%m-%d %H:%M')} - {schedule.last_status or 'Unknown'}")
            
            with col2:
                is_active = st.toggle(
                    "Active",
                    value=schedule.is_active,
                    key=f"toggle_{schedule.id}"
                )
                if is_active != schedule.is_active:
                    _update_schedule_status(schedule.id, is_active)
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_sched_{schedule.id}"):
                    st.info("Schedule editing feature")
                
                if st.button("🗑️ Delete", key=f"del_sched_{schedule.id}"):
                    _delete_schedule(schedule.id)
                    st.rerun()
            
            st.divider()
    else:
        st.info("ℹ️ No scheduled reports. Create one below.")
    
    # Create new schedule
    if st.button("➕ Create New Schedule", type="primary"):
        with st.form("new_schedule_form"):
            st.markdown("### Create New Schedule")
            
            schedule_name = st.text_input("Schedule Name", value="Weekly Test Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                frequency = st.selectbox(
                    "Frequency",
                    options=["Daily", "Weekly", "Monthly", "On Test Completion"]
                )
                
                with get_db() as db:
                    templates = db.execute(select(ReportTemplate)).scalars().all()
                    template_options = {t.template_id: t.template_name for t in templates}
                
                template_id = st.selectbox(
                    "Template",
                    options=list(template_options.keys()) if template_options else [],
                    format_func=lambda x: template_options.get(x, x)
                )
            
            with col2:
                trigger_time = st.time_input("Trigger Time (if scheduled)")
                recipients = st.text_area(
                    "Email Recipients (comma-separated)",
                    value="test@example.com"
                )
            
            if st.form_submit_button("Create Schedule"):
                _create_schedule(
                    schedule_name, frequency, template_id,
                    trigger_time.strftime('%H:%M'), recipients
                )
                st.success("✅ Schedule created successfully!")
                st.rerun()


def _create_schedule(name, frequency, template_id, trigger_time, recipients):
    """Create a new scheduled report"""
    
    with get_db() as db:
        schedule_id = f"SCHED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate next run
        next_run = datetime.now()
        if frequency == "Daily":
            next_run += timedelta(days=1)
        elif frequency == "Weekly":
            next_run += timedelta(weeks=1)
        elif frequency == "Monthly":
            next_run += timedelta(days=30)
        
        schedule = ScheduledReport(
            schedule_id=schedule_id,
            schedule_name=name,
            template_id=template_id,
            frequency=frequency,
            trigger_time=trigger_time,
            recipients=[r.strip() for r in recipients.split(',')],
            is_active=True,
            next_run=next_run,
            created_by=st.session_state.get('username', 'System')
        )
        
        db.add(schedule)
        db.commit()


def _update_schedule_status(schedule_id, is_active):
    """Update schedule active status"""
    
    with get_db() as db:
        schedule = db.execute(
            select(ScheduledReport).where(ScheduledReport.id == schedule_id)
        ).scalar()
        
        if schedule:
            schedule.is_active = is_active
            db.commit()


def _delete_schedule(schedule_id):
    """Delete a schedule"""
    
    with get_db() as db:
        schedule = db.execute(
            select(ScheduledReport).where(ScheduledReport.id == schedule_id)
        ).scalar()
        
        if schedule:
            db.delete(schedule)
            db.commit()


def render_report_history():
    """Render the Report History tab"""
    
    st.subheader("📚 Report History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Draft", "Generated", "Signed", "Distributed"]
        )
    
    with col2:
        language_filter = st.selectbox(
            "Filter by Language",
            options=["All", "English", "Hindi", "Spanish"]
        )
    
    with col3:
        search_term = st.text_input("🔍 Search", placeholder="Report number or title...")
    
    st.divider()
    
    # Get reports
    with get_db() as db:
        query = select(GeneratedReport).order_by(desc(GeneratedReport.generated_at))
        
        if status_filter != "All":
            query = query.where(GeneratedReport.status == status_filter)
        
        if language_filter != "All":
            query = query.where(GeneratedReport.language == language_filter)
        
        reports = db.execute(query.limit(50)).scalars().all()
        
        # Apply search filter
        if search_term:
            reports = [
                r for r in reports
                if search_term.lower() in r.report_number.lower()
                or search_term.lower() in r.report_title.lower()
            ]
    
    if reports:
        st.markdown(f"**Showing {len(reports)} report(s)**")
        
        for report in reports:
            with st.expander(
                f"📄 {report.report_number} - {report.report_title}",
                expanded=False
            ):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Report ID:** {report.report_id}")
                    st.markdown(f"**Status:** {report.status}")
                    st.markdown(f"**Language:** {report.language}")
                    st.markdown(f"**Samples:** {', '.join(report.sample_ids) if report.sample_ids else 'N/A'}")
                
                with col2:
                    st.markdown(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(f"**By:** {report.generated_by}")
                    st.markdown(f"**Size:** {report.file_size / 1024:.1f} KB" if report.file_size else "Unknown")
                
                with col3:
                    # Download buttons
                    if report.file_path and os.path.exists(report.file_path.split(',')[0]):
                        file_path = report.file_path.split(',')[0]
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                            file_ext = os.path.splitext(file_path)[1]
                            mime_type = "application/pdf" if file_ext == ".pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            
                            st.download_button(
                                label=f"📥 Download{file_ext.upper()}",
                                data=file_data,
                                file_name=f"{report.report_number}{file_ext}",
                                mime=mime_type,
                                key=f"download_{report.id}"
                            )
                    
                    if report.distributed_to:
                        if st.button("📧 Resend Email", key=f"resend_{report.id}"):
                            st.info("Email distribution feature")
                
                # Signature status
                if report.signatures:
                    st.markdown("**Signatures:**")
                    for sig in report.signatures:
                        st.markdown(f"- {sig.get('role', 'Unknown')}: {sig.get('name', 'N/A')} ({sig.get('status', 'Pending')})")
    else:
        st.info("ℹ️ No reports found matching the criteria")


if __name__ == "__main__":
    main()
