"""
Report Generator Dashboard - Automated report generation and distribution
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from utils.data_generator import get_sample_data
from utils.helpers import format_datetime
from analytics.protocol_analytics import ProtocolAnalytics

# Page configuration
st.set_page_config(
    page_title="Report Generator",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Report Generator Dashboard")
st.markdown("### Automated Report Generation & Distribution")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_sample_data()

data = load_data()
protocols = data['protocols']
service_requests = data['service_requests']
kpi_metrics = data['kpi_metrics']

analytics = ProtocolAnalytics(protocols)

# Tabs for different report functions
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Quick Reports",
    "🔧 Custom Report Builder",
    "⏰ Scheduled Reports",
    "📧 Distribution"
])

with tab1:
    st.subheader("One-Click Report Generation")

    st.markdown("Generate pre-configured reports instantly:")

    # Report templates
    report_col1, report_col2 = st.columns(2)

    with report_col1:
        st.markdown("#### 📊 Executive Summary Report")
        st.write("High-level overview of all operations, KPIs, and key metrics")

        exec_col1, exec_col2 = st.columns(2)
        with exec_col1:
            exec_period = st.selectbox(
                "Period",
                ["Daily", "Weekly", "Monthly", "Quarterly"],
                key="exec_period"
            )
        with exec_col2:
            exec_format = st.selectbox(
                "Format",
                ["PDF", "Excel", "PowerPoint"],
                key="exec_format"
            )

        if st.button("📄 Generate Executive Report", use_container_width=True):
            with st.spinner("Generating report..."):
                # Show preview
                st.success("✅ Report generated successfully!")

                # Display summary
                stats = analytics.get_overall_statistics()

                st.markdown("##### Report Preview")
                preview_data = {
                    'Metric': [
                        'Total Protocols',
                        'Completion Rate',
                        'Pass Rate',
                        'Average Duration',
                        'Total Test Hours'
                    ],
                    'Value': [
                        stats['total_protocols'],
                        f"{stats['completion_rate']:.1f}%",
                        f"{stats['pass_rate']:.1f}%",
                        f"{stats['average_duration_hours']:.1f}h",
                        f"{stats['total_test_hours']:.1f}h"
                    ]
                }
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Report",
                    data="Executive Report Content (Demo)",
                    file_name=f"executive_report_{datetime.now().strftime('%Y%m%d')}.{exec_format.lower()}",
                    mime="application/octet-stream"
                )

        st.markdown("---")

        st.markdown("#### 🔬 Protocol Performance Report")
        st.write("Detailed analysis of protocol execution, trends, and performance metrics")

        proto_col1, proto_col2 = st.columns(2)
        with proto_col1:
            proto_period = st.selectbox(
                "Period",
                ["Last 7 Days", "Last 30 Days", "Last 90 Days"],
                key="proto_period"
            )
        with proto_col2:
            proto_format = st.selectbox(
                "Format",
                ["PDF", "Excel"],
                key="proto_format"
            )

        if st.button("📄 Generate Protocol Report", use_container_width=True):
            with st.spinner("Generating report..."):
                st.success("✅ Report generated successfully!")

                # Show type breakdown
                type_breakdown = analytics.get_protocol_type_breakdown()

                st.markdown("##### Report Preview - Protocol Type Breakdown")
                type_data = []
                for ptype, stats in type_breakdown.items():
                    type_data.append({
                        'Type': ptype,
                        'Total': stats['total'],
                        'Completed': stats['completed'],
                        'Completion Rate': f"{stats['completion_rate']:.1f}%",
                        'Pass Rate': f"{stats['pass_rate']:.1f}%"
                    })

                type_df = pd.DataFrame(type_data)
                st.dataframe(type_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Report",
                    data="Protocol Performance Report Content (Demo)",
                    file_name=f"protocol_report_{datetime.now().strftime('%Y%m%d')}.{proto_format.lower()}",
                    mime="application/octet-stream"
                )

    with report_col2:
        st.markdown("#### ✅ Quality Control Report")
        st.write("QC/NC register summary, failure analysis, and quality metrics")

        qc_col1, qc_col2 = st.columns(2)
        with qc_col1:
            qc_period = st.selectbox(
                "Period",
                ["Daily", "Weekly", "Monthly"],
                key="qc_period"
            )
        with qc_col2:
            qc_format = st.selectbox(
                "Format",
                ["PDF", "Excel"],
                key="qc_format"
            )

        if st.button("📄 Generate QC Report", use_container_width=True):
            with st.spinner("Generating report..."):
                st.success("✅ Report generated successfully!")

                # Show failure analysis
                failure_analysis = analytics.get_failure_mode_analysis()

                st.markdown("##### Report Preview - Failure Analysis")
                st.write(f"**Total Failures:** {failure_analysis['total_failures']}")
                st.write(f"**Overall Failure Rate:** {failure_analysis['overall_failure_rate']:.2f}%")

                if failure_analysis['by_type']:
                    failure_data = []
                    for ptype, stats in failure_analysis['by_type'].items():
                        failure_data.append({
                            'Protocol Type': ptype,
                            'Failures': stats['failures'],
                            'Total Tests': stats['total'],
                            'Failure Rate': f"{stats['failure_rate']:.2f}%"
                        })

                    failure_df = pd.DataFrame(failure_data)
                    st.dataframe(failure_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Report",
                    data="QC Report Content (Demo)",
                    file_name=f"qc_report_{datetime.now().strftime('%Y%m%d')}.{qc_format.lower()}",
                    mime="application/octet-stream"
                )

        st.markdown("---")

        st.markdown("#### 🔧 Equipment Utilization Report")
        st.write("Equipment usage statistics, calibration status, and maintenance tracking")

        eq_col1, eq_col2 = st.columns(2)
        with eq_col1:
            eq_period = st.selectbox(
                "Period",
                ["Weekly", "Monthly", "Quarterly"],
                key="eq_period"
            )
        with eq_col2:
            eq_format = st.selectbox(
                "Format",
                ["PDF", "Excel"],
                key="eq_format"
            )

        if st.button("📄 Generate Equipment Report", use_container_width=True):
            with st.spinner("Generating report..."):
                st.success("✅ Report generated successfully!")

                # Show equipment summary
                equipment = data['equipment']

                st.markdown("##### Report Preview - Equipment Summary")
                eq_data = []
                for eq in equipment[:10]:
                    eq_data.append({
                        'Equipment': eq.equipment_name,
                        'Type': eq.equipment_type,
                        'Status': eq.status,
                        'Utilization': f"{eq.utilization_rate:.1f}%",
                        'Next Calibration': format_datetime(eq.next_calibration, "%Y-%m-%d") if eq.next_calibration else "N/A"
                    })

                eq_df = pd.DataFrame(eq_data)
                st.dataframe(eq_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Report",
                    data="Equipment Report Content (Demo)",
                    file_name=f"equipment_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/octet-stream"
                )

with tab2:
    st.subheader("🔧 Custom Report Builder")

    st.markdown("Build custom reports with selected data and metrics:")

    # Report configuration
    st.markdown("#### Report Configuration")

    config_col1, config_col2 = st.columns(2)

    with config_col1:
        report_name = st.text_input("Report Name", "Custom Report")
        report_description = st.text_area("Description", "Custom generated report")

        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="custom_date_range"
        )

    with config_col2:
        report_format = st.selectbox(
            "Export Format",
            ["PDF", "Excel", "CSV", "JSON"],
            key="custom_format"
        )

        include_charts = st.checkbox("Include Charts", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=False)

    # Section selection
    st.markdown("#### Select Report Sections")

    section_col1, section_col2, section_col3 = st.columns(3)

    with section_col1:
        include_overview = st.checkbox("Executive Overview", value=True)
        include_protocols = st.checkbox("Protocol Details", value=True)
        include_kpis = st.checkbox("KPI Metrics", value=True)

    with section_col2:
        include_quality = st.checkbox("Quality Analysis", value=True)
        include_equipment = st.checkbox("Equipment Status", value=True)
        include_timeline = st.checkbox("Timeline View", value=False)

    with section_col3:
        include_trends = st.checkbox("Trend Analysis", value=True)
        include_comparative = st.checkbox("Comparative Analysis", value=False)
        include_recommendations = st.checkbox("Recommendations", value=False)

    # Generate custom report
    st.markdown("---")

    if st.button("🚀 Generate Custom Report", type="primary", use_container_width=True):
        with st.spinner("Building custom report..."):
            st.success("✅ Custom report generated successfully!")

            # Show report structure
            st.markdown("##### Report Structure")

            report_structure = []
            if include_overview:
                report_structure.append("1. Executive Overview")
            if include_protocols:
                report_structure.append("2. Protocol Details")
            if include_kpis:
                report_structure.append("3. KPI Metrics")
            if include_quality:
                report_structure.append("4. Quality Analysis")
            if include_equipment:
                report_structure.append("5. Equipment Status")
            if include_timeline:
                report_structure.append("6. Timeline View")
            if include_trends:
                report_structure.append("7. Trend Analysis")
            if include_comparative:
                report_structure.append("8. Comparative Analysis")
            if include_recommendations:
                report_structure.append("9. Recommendations")

            for section in report_structure:
                st.write(f"✓ {section}")

            st.download_button(
                "⬇️ Download Custom Report",
                data=f"Custom Report: {report_name}\n{report_description}\n\nSections: {', '.join(report_structure)}",
                file_name=f"{report_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                mime="application/octet-stream"
            )

with tab3:
    st.subheader("⏰ Scheduled Reports")

    st.markdown("Configure automated report generation and delivery:")

    # Create new schedule
    with st.expander("➕ Create New Schedule", expanded=True):
        schedule_col1, schedule_col2 = st.columns(2)

        with schedule_col1:
            schedule_name = st.text_input("Schedule Name", "Weekly Summary Report")
            report_type = st.selectbox(
                "Report Type",
                ["Executive Summary", "Protocol Performance", "QC Report", "Equipment Report", "Custom"]
            )

            frequency = st.selectbox(
                "Frequency",
                ["Daily", "Weekly", "Monthly", "Quarterly"]
            )

        with schedule_col2:
            delivery_time = st.time_input("Delivery Time", datetime.now().time())
            delivery_day = st.selectbox(
                "Delivery Day (for weekly/monthly)",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )

            output_format = st.multiselect(
                "Output Formats",
                ["PDF", "Excel", "CSV"],
                default=["PDF"]
            )

        recipients = st.text_area(
            "Email Recipients (comma-separated)",
            "manager@example.com, qc@example.com"
        )

        if st.button("💾 Save Schedule", use_container_width=True):
            st.success(f"✅ Schedule '{schedule_name}' created successfully!")
            st.info(f"Report will be generated {frequency.lower()} and sent to {len(recipients.split(','))} recipients")

    # Existing schedules
    st.markdown("---")
    st.markdown("#### Existing Schedules")

    schedules_data = [
        {
            'Schedule Name': 'Weekly Executive Summary',
            'Report Type': 'Executive Summary',
            'Frequency': 'Weekly',
            'Next Run': format_datetime(datetime.now() + timedelta(days=3), "%Y-%m-%d %H:%M"),
            'Recipients': '3',
            'Status': '✅ Active'
        },
        {
            'Schedule Name': 'Monthly QC Report',
            'Report Type': 'QC Report',
            'Frequency': 'Monthly',
            'Next Run': format_datetime(datetime.now() + timedelta(days=15), "%Y-%m-%d %H:%M"),
            'Recipients': '5',
            'Status': '✅ Active'
        },
        {
            'Schedule Name': 'Daily Protocol Summary',
            'Report Type': 'Protocol Performance',
            'Frequency': 'Daily',
            'Next Run': format_datetime(datetime.now() + timedelta(hours=10), "%Y-%m-%d %H:%M"),
            'Recipients': '2',
            'Status': '⏸️ Paused'
        }
    ]

    schedules_df = pd.DataFrame(schedules_data)
    st.dataframe(schedules_df, use_container_width=True)

    # Schedule actions
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("▶️ Run Now", use_container_width=True):
            st.info("Selected schedule will run immediately")

    with action_col2:
        if st.button("✏️ Edit", use_container_width=True):
            st.info("Edit schedule configuration")

    with action_col3:
        if st.button("🗑️ Delete", use_container_width=True):
            st.warning("Delete selected schedule")

with tab4:
    st.subheader("📧 Report Distribution")

    st.markdown("Manage report distribution settings and history:")

    # Distribution settings
    dist_col1, dist_col2 = st.columns(2)

    with dist_col1:
        st.markdown("#### Distribution Settings")

        default_sender = st.text_input("Default Sender Email", "reports@test-protocols.com")
        default_subject = st.text_input("Default Subject Template", "[Test Protocols] {report_name} - {date}")

        smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587)

        enable_auto_dist = st.checkbox("Enable Automatic Distribution", value=True)

        if st.button("💾 Save Distribution Settings", use_container_width=True):
            st.success("✅ Distribution settings saved!")

    with dist_col2:
        st.markdown("#### Distribution Groups")

        with st.expander("Management Team"):
            st.text_area("Members", "ceo@example.com\ncoo@example.com\nmanager@example.com", key="mgmt_group")

        with st.expander("QC Team"):
            st.text_area("Members", "qc-lead@example.com\nqc-officer@example.com", key="qc_group")

        with st.expander("Operations Team"):
            st.text_area("Members", "ops-manager@example.com\ntechnician@example.com", key="ops_group")

    # Distribution history
    st.markdown("---")
    st.markdown("#### Distribution History")

    history_data = [
        {
            'Date': format_datetime(datetime.now() - timedelta(hours=2)),
            'Report': 'Executive Summary',
            'Recipients': '3',
            'Format': 'PDF',
            'Status': '✅ Sent',
            'Size': '2.3 MB'
        },
        {
            'Date': format_datetime(datetime.now() - timedelta(days=1)),
            'Report': 'Protocol Performance',
            'Recipients': '5',
            'Format': 'Excel',
            'Status': '✅ Sent',
            'Size': '1.8 MB'
        },
        {
            'Date': format_datetime(datetime.now() - timedelta(days=2)),
            'Report': 'QC Report',
            'Recipients': '4',
            'Format': 'PDF',
            'Status': '❌ Failed',
            'Size': '3.1 MB'
        }
    ]

    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)

    # Statistics
    st.markdown("---")
    st.markdown("#### Distribution Statistics")

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Reports Sent (30d)", "127")

    with stat_col2:
        st.metric("Success Rate", "98.4%")

    with stat_col3:
        st.metric("Total Recipients", "42")

    with stat_col4:
        st.metric("Avg Report Size", "2.1 MB")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    f"Report Generator v1.0 | Multi-format export support | "
    f"Last Updated: {format_datetime(datetime.now())}"
    "</div>",
    unsafe_allow_html=True
)
