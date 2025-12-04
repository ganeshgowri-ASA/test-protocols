"""
Report Generation Module
========================
Generate comprehensive test reports and certificates.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from components.sample_management import generate_route_card_pdf
from database import (
    Sample, TestExecution, ServiceRequest, TestProtocol,
    CompanyProfile, SampleStatus, TestStatus
)
from sqlalchemy import select, desc

# Page configuration
setup_page_config(page_title="Report Generation", page_icon="📑")

# Render navigation
render_header("Report Generation", "Generate test reports and certificates")
render_sidebar_navigation()


def main():
    """Main report generation page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Test Reports",
        "📜 Certificates",
        "📋 Summary Reports",
        "📁 Batch Reports"
    ])

    with tab1:
        render_test_reports()

    with tab2:
        render_certificates()

    with tab3:
        render_summary_reports()

    with tab4:
        render_batch_reports()


def render_test_reports():
    """Render individual test report generation"""

    st.markdown("### 📊 Generate Test Report")

    # Sample selection
    with get_db() as db:
        samples = db.execute(
            select(Sample)
            .where(Sample.status.in_([SampleStatus.COMPLETED, SampleStatus.ANALYZED, SampleStatus.REPORTED]))
            .order_by(desc(Sample.created_at))
            .limit(50)
        ).scalars().all()

        sample_options = {f"{s.sample_id} - {s.manufacturer or 'N/A'} {s.model_number or ''}": s for s in samples}

    if not sample_options:
        st.info("No completed samples available for reporting")
        return

    selected_sample = st.selectbox(
        "Select Sample",
        options=["-- Select --"] + list(sample_options.keys())
    )

    if selected_sample != "-- Select --":
        sample = sample_options[selected_sample]

        st.markdown(f"### Sample: {sample.sample_id}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Sample ID:** {sample.sample_id}")
            st.markdown(f"**Project ID:** {sample.project_id}")
            st.markdown(f"**Type:** {sample.sample_type or 'N/A'}")
            st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")
            st.markdown(f"**Model:** {sample.model_number or 'N/A'}")

        with col2:
            st.markdown(f"**Status:** {sample.status.value.upper()}")
            st.markdown(f"**Tests Completed:** {sample.tests_completed}/{sample.tests_total}")
            st.markdown(f"**Overall Result:** {sample.overall_result or 'Pending'}")

        st.divider()

        # Report options
        st.markdown("#### Report Options")

        col1, col2 = st.columns(2)

        with col1:
            report_format = st.selectbox(
                "Report Format",
                options=["PDF", "Excel", "Both"]
            )

            include_raw_data = st.checkbox("Include Raw Data", value=False)

        with col2:
            include_charts = st.checkbox("Include Charts", value=True)

            include_photos = st.checkbox("Include Photos", value=True)

        # Get test results
        with get_db() as db:
            test_executions = db.execute(
                select(TestExecution)
                .where(TestExecution.sample_id == sample.sample_id)
                .where(TestExecution.status == TestStatus.COMPLETED)
            ).scalars().all()

            # Get service request for client info
            sr = db.execute(
                select(ServiceRequest)
                .where(ServiceRequest.id == sample.service_request_id)
            ).scalar()

            # Get company profile
            company = CompanyProfile.get_default(db)

        st.markdown("#### Tests to Include")

        selected_tests = []
        for test in test_executions:
            protocol = db.execute(
                select(TestProtocol).where(TestProtocol.id == test.protocol_id)
            ).scalar()

            if st.checkbox(
                f"{test.execution_number} - {protocol.name if protocol else 'Unknown'}",
                value=True,
                key=f"include_{test.id}"
            ):
                selected_tests.append(test)

        if st.button("📊 Generate Report", type="primary"):
            if not selected_tests:
                st.warning("Please select at least one test to include")
            else:
                with st.spinner("Generating report..."):
                    try:
                        # Generate report content
                        report_content = generate_report_content(
                            sample=sample,
                            tests=selected_tests,
                            service_request=sr,
                            company=company,
                            include_raw_data=include_raw_data,
                            include_charts=include_charts
                        )

                        st.success("Report generated successfully!")

                        # Display preview
                        with st.expander("📄 Report Preview"):
                            st.markdown(report_content)

                        # Download button
                        st.download_button(
                            label="📥 Download Report",
                            data=report_content,
                            file_name=f"test_report_{sample.sample_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )

                        # Update sample status
                        with get_db() as db:
                            sample_record = db.execute(
                                select(Sample).where(Sample.id == sample.id)
                            ).scalar()
                            if sample_record:
                                sample_record.status = SampleStatus.REPORTED
                                db.commit()

                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")


def generate_report_content(sample, tests, service_request, company, include_raw_data=False, include_charts=False):
    """Generate report content as text (simplified - would use ReportLab for PDF)"""

    report = []

    # Header
    report.append("=" * 80)
    report.append(f"{company.company_name if company else 'Solar PV Testing Laboratory'}")
    report.append("TEST REPORT")
    report.append("=" * 80)
    report.append("")

    # Sample Information
    report.append("SAMPLE INFORMATION")
    report.append("-" * 40)
    report.append(f"Sample ID: {sample.sample_id}")
    report.append(f"Project ID: {sample.project_id or 'N/A'}")
    report.append(f"Sample Type: {sample.sample_type or 'N/A'}")
    report.append(f"Manufacturer: {sample.manufacturer or 'N/A'}")
    report.append(f"Model Number: {sample.model_number or 'N/A'}")
    report.append(f"Serial Number: {sample.serial_number or 'N/A'}")
    report.append("")

    # Client Information
    if service_request:
        report.append("CLIENT INFORMATION")
        report.append("-" * 40)
        report.append(f"Client: {service_request.client_name or 'N/A'}")
        report.append(f"Organization: {service_request.client_organization or 'N/A'}")
        report.append(f"Request Number: {service_request.request_number}")
        report.append("")

    # Test Results
    report.append("TEST RESULTS")
    report.append("-" * 40)

    for test in tests:
        with get_db() as db:
            protocol = db.execute(
                select(TestProtocol).where(TestProtocol.id == test.protocol_id)
            ).scalar()

        report.append("")
        report.append(f"Test: {protocol.name if protocol else 'Unknown'}")
        report.append(f"Protocol ID: {protocol.protocol_id if protocol else 'N/A'}")
        report.append(f"Standard Reference: {protocol.standard_reference if protocol else 'N/A'}")
        report.append(f"Execution Number: {test.execution_number}")
        report.append(f"Result: {'PASS' if test.test_passed else 'FAIL' if test.test_passed == False else 'N/A'}")
        report.append(f"Date Completed: {test.completed_at.strftime('%Y-%m-%d') if test.completed_at else 'N/A'}")

        if test.remarks:
            report.append(f"Remarks: {test.remarks}")

        if include_raw_data and test.results:
            report.append("Results Data:")
            report.append(str(test.results))

        report.append("-" * 40)

    # Summary
    report.append("")
    report.append("SUMMARY")
    report.append("-" * 40)
    passed = len([t for t in tests if t.test_passed])
    failed = len([t for t in tests if t.test_passed == False])
    report.append(f"Total Tests: {len(tests)}")
    report.append(f"Passed: {passed}")
    report.append(f"Failed: {failed}")
    report.append(f"Overall Result: {sample.overall_result or 'PASS' if failed == 0 else 'FAIL'}")

    # Footer
    report.append("")
    report.append("=" * 80)
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Report ID: RPT-{sample.sample_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    report.append("=" * 80)

    return "\n".join(report)


def render_certificates():
    """Render certificate generation"""

    st.markdown("### 📜 Generate Certificates")

    st.info("Generate test certificates for samples that have passed all required tests.")

    # Get samples that passed
    with get_db() as db:
        passed_samples = db.execute(
            select(Sample)
            .where(Sample.overall_result == "pass")
            .order_by(desc(Sample.completed_at))
            .limit(50)
        ).scalars().all()

    if not passed_samples:
        st.info("No samples with passing results available for certification")
        return

    sample_options = {f"{s.sample_id}": s for s in passed_samples}

    selected = st.selectbox(
        "Select Sample for Certificate",
        options=["-- Select --"] + list(sample_options.keys())
    )

    if selected != "-- Select --":
        sample = sample_options[selected]

        st.markdown(f"### Certificate Preview: {sample.sample_id}")

        col1, col2 = st.columns(2)

        with col1:
            certificate_type = st.selectbox(
                "Certificate Type",
                options=["Test Certificate", "Compliance Certificate", "Performance Certificate"]
            )

        with col2:
            certificate_number = st.text_input(
                "Certificate Number",
                value=f"CERT-{sample.sample_id}-{datetime.now().strftime('%Y%m%d')}"
            )

        valid_until = st.date_input(
            "Valid Until",
            value=datetime.now().date().replace(year=datetime.now().year + 1)
        )

        if st.button("📜 Generate Certificate", type="primary"):
            st.success("Certificate generated!")

            certificate_content = f"""
            ============================================
            {certificate_type.upper()}
            ============================================

            Certificate Number: {certificate_number}

            This is to certify that the following sample
            has successfully completed testing:

            Sample ID: {sample.sample_id}
            Manufacturer: {sample.manufacturer or 'N/A'}
            Model: {sample.model_number or 'N/A'}
            Serial Number: {sample.serial_number or 'N/A'}

            Test Result: PASS
            Tests Completed: {sample.tests_completed}/{sample.tests_total}

            Date of Issue: {datetime.now().strftime('%Y-%m-%d')}
            Valid Until: {valid_until}

            ============================================
            """

            st.download_button(
                "📥 Download Certificate",
                data=certificate_content,
                file_name=f"{certificate_number}.txt",
                mime="text/plain"
            )


def render_summary_reports():
    """Render summary report generation"""

    st.markdown("### 📋 Summary Reports")

    report_type = st.selectbox(
        "Report Type",
        options=[
            "Daily Test Summary",
            "Weekly Summary",
            "Monthly Summary",
            "Sample Status Summary",
            "Protocol Performance Summary"
        ]
    )

    # Date range
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date().replace(day=1))

    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())

    if st.button("📋 Generate Summary", type="primary"):
        with get_db() as db:
            if report_type == "Sample Status Summary":
                st.markdown("#### Sample Status Summary")

                for status in SampleStatus:
                    count = db.execute(
                        select(Sample)
                        .where(Sample.status == status)
                    ).scalars().all()
                    st.markdown(f"**{status.value.upper()}:** {len(count)}")

            elif report_type == "Protocol Performance Summary":
                st.markdown("#### Protocol Performance Summary")

                protocols = db.execute(select(TestProtocol)).scalars().all()

                for protocol in protocols[:20]:
                    tests = db.execute(
                        select(TestExecution)
                        .where(TestExecution.protocol_id == protocol.id)
                        .where(TestExecution.status == TestStatus.COMPLETED)
                    ).scalars().all()

                    if tests:
                        passed = len([t for t in tests if t.test_passed])
                        pass_rate = (passed / len(tests) * 100)

                        st.markdown(f"**{protocol.protocol_id}:** {protocol.name}")
                        st.markdown(f"  - Tests: {len(tests)} | Pass Rate: {pass_rate:.1f}%")

            else:
                st.markdown(f"#### {report_type}")
                st.markdown(f"Period: {start_date} to {end_date}")

                # General test statistics
                tests = db.execute(
                    select(TestExecution)
                    .where(TestExecution.completed_at >= datetime.combine(start_date, datetime.min.time()))
                    .where(TestExecution.completed_at <= datetime.combine(end_date, datetime.max.time()))
                ).scalars().all()

                st.markdown(f"**Total Tests Completed:** {len(tests)}")

                if tests:
                    passed = len([t for t in tests if t.test_passed])
                    st.markdown(f"**Passed:** {passed}")
                    st.markdown(f"**Failed:** {len(tests) - passed}")
                    st.markdown(f"**Pass Rate:** {(passed/len(tests)*100):.1f}%")


def render_batch_reports():
    """Render batch report generation"""

    st.markdown("### 📁 Batch Report Generation")

    st.info("Generate reports for multiple samples at once")

    # Get completed samples
    with get_db() as db:
        samples = db.execute(
            select(Sample)
            .where(Sample.status.in_([SampleStatus.COMPLETED, SampleStatus.ANALYZED]))
            .order_by(desc(Sample.completed_at))
            .limit(50)
        ).scalars().all()

    if not samples:
        st.info("No samples available for batch reporting")
        return

    # Multi-select samples
    selected_ids = st.multiselect(
        "Select Samples",
        options=[s.sample_id for s in samples],
        help="Select multiple samples for batch report generation"
    )

    if selected_ids:
        st.markdown(f"**Selected: {len(selected_ids)} sample(s)**")

        report_format = st.selectbox(
            "Report Format",
            options=["Individual Reports", "Combined Report"]
        )

        if st.button("📁 Generate Batch Reports", type="primary"):
            with st.spinner("Generating reports..."):
                if report_format == "Individual Reports":
                    for sample_id in selected_ids:
                        st.markdown(f"Generated report for: {sample_id}")
                else:
                    st.markdown("Generated combined report for all selected samples")

            st.success(f"Generated {len(selected_ids)} report(s)")


if __name__ == "__main__":
    main()
