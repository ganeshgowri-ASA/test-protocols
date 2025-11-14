"""
KPI Dashboard - Key Performance Indicators tracking
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from utils.data_generator import get_sample_data
from utils.helpers import format_datetime, calculate_percentage, get_trend_icon, calculate_trend
from visualizations.charts import ChartBuilder
from analytics.protocol_analytics import ProtocolAnalytics

# Page configuration
st.set_page_config(
    page_title="KPI Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 KPI Dashboard")
st.markdown("### Key Performance Indicators & Metrics Tracking")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_sample_data()

data = load_data()
protocols = data['protocols']
service_requests = data['service_requests']
equipment = data['equipment']
kpi_metrics = data['kpi_metrics']

# Initialize analytics
analytics = ProtocolAnalytics(protocols)
chart_builder = ChartBuilder()

# Sidebar - Date range selector
st.sidebar.header("📅 Date Range")
date_range_option = st.sidebar.selectbox(
    "Select Period",
    ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"],
    index=1
)

if date_range_option == "Custom Range":
    start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", datetime.now())
else:
    days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
    days = days_map.get(date_range_option, 30)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

# Filter metrics by date
filtered_metrics = [
    m for m in kpi_metrics
    if start_date.date() <= m.date.date() <= end_date.date()
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Metrics Period:** {len(filtered_metrics)} days")

# Main content
st.markdown("---")

# Top-level KPI Summary
st.subheader("🎯 KPI Summary")

if filtered_metrics:
    latest_metric = filtered_metrics[-1]

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    # Calculate trends
    pass_rates = [m.pass_rate for m in filtered_metrics]
    tat_values = [m.average_tat for m in filtered_metrics]
    throughput_values = [m.throughput_daily for m in filtered_metrics]
    utilization_values = [m.equipment_utilization for m in filtered_metrics]

    with kpi_col1:
        trend = calculate_trend(pass_rates)
        st.metric(
            label="Pass Rate",
            value=f"{latest_metric.pass_rate:.1f}%",
            delta=f"{trend} {get_trend_icon(trend)}",
            delta_color="normal" if trend == "increasing" else "inverse" if trend == "decreasing" else "off"
        )

    with kpi_col2:
        trend = calculate_trend(tat_values)
        st.metric(
            label="Avg TAT (hours)",
            value=f"{latest_metric.average_tat:.1f}",
            delta=f"{trend} {get_trend_icon(trend)}",
            delta_color="inverse" if trend == "increasing" else "normal" if trend == "decreasing" else "off"
        )

    with kpi_col3:
        st.metric(
            label="Throughput (daily)",
            value=latest_metric.throughput_daily,
            delta=f"{calculate_trend(throughput_values)} {get_trend_icon(calculate_trend(throughput_values))}"
        )

    with kpi_col4:
        st.metric(
            label="Equipment Utilization",
            value=f"{latest_metric.equipment_utilization:.1f}%",
            delta=f"{calculate_trend(utilization_values)} {get_trend_icon(calculate_trend(utilization_values))}"
        )

    with kpi_col5:
        st.metric(
            label="First-Time Pass Rate",
            value=f"{latest_metric.first_time_pass_rate:.1f}%",
            delta="Target: 90%"
        )

    # Detailed KPI Charts
    st.markdown("---")
    st.subheader("📊 KPI Trends")

    # Multi-metric chart
    multi_chart = chart_builder.create_multi_metric_chart(filtered_metrics)
    st.plotly_chart(multi_chart, use_container_width=True)

    # Individual KPI trend charts
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Throughput Metrics",
        "⏱️ TAT Analysis",
        "✅ Quality Metrics",
        "🔧 Resource Utilization"
    ])

    with tab1:
        st.subheader("Throughput Metrics")

        col1, col2 = st.columns(2)

        with col1:
            # Samples processed trend
            throughput_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'throughput_daily')
            st.plotly_chart(throughput_chart, use_container_width=True)

            # Statistics
            st.markdown("##### Statistics")
            total_samples = sum(m.total_samples for m in filtered_metrics)
            avg_daily = total_samples / len(filtered_metrics) if filtered_metrics else 0

            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Total Samples", total_samples)
                st.metric("Avg Daily", f"{avg_daily:.1f}")

            with stat_col2:
                max_daily = max(m.throughput_daily for m in filtered_metrics)
                min_daily = min(m.throughput_daily for m in filtered_metrics)
                st.metric("Peak Daily", max_daily)
                st.metric("Min Daily", min_daily)

        with col2:
            # Completed vs Pending
            completed_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'completed_protocols')
            st.plotly_chart(completed_chart, use_container_width=True)

            # Statistics
            st.markdown("##### Protocol Status")
            total_completed = sum(m.completed_protocols for m in filtered_metrics)
            total_pending = sum(m.pending_protocols for m in filtered_metrics)
            total_failed = sum(m.failed_protocols for m in filtered_metrics)

            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Completed", total_completed)
                st.metric("Pending", total_pending)

            with stat_col2:
                st.metric("Failed", total_failed)
                fail_rate = calculate_percentage(total_failed, total_completed + total_failed)
                st.metric("Failure Rate", f"{fail_rate:.2f}%")

    with tab2:
        st.subheader("Turn Around Time (TAT) Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # TAT trend
            tat_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'average_tat')
            st.plotly_chart(tat_chart, use_container_width=True)

            # TAT Statistics
            st.markdown("##### TAT Statistics")
            avg_tat = sum(m.average_tat for m in filtered_metrics) / len(filtered_metrics)
            max_tat = max(m.average_tat for m in filtered_metrics)
            min_tat = min(m.average_tat for m in filtered_metrics)

            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Average TAT", f"{avg_tat:.1f}h")
                st.metric("Target TAT", "48h")

            with stat_col2:
                st.metric("Maximum TAT", f"{max_tat:.1f}h")
                st.metric("Minimum TAT", f"{min_tat:.1f}h")

            # TAT Performance
            within_target = sum(1 for m in filtered_metrics if m.average_tat <= 48)
            target_compliance = calculate_percentage(within_target, len(filtered_metrics))

            st.markdown("##### Target Compliance")
            st.progress(target_compliance / 100)
            st.markdown(f"**{target_compliance:.1f}%** of days met TAT target (≤48h)")

        with col2:
            # Performance indicator
            st.markdown("##### TAT Performance Rating")

            if avg_tat <= 48:
                st.success(f"✅ Excellent - Average TAT is {avg_tat:.1f}h (Target: 48h)")
            elif avg_tat <= 60:
                st.warning(f"⚠️ Good - Average TAT is {avg_tat:.1f}h (Target: 48h)")
            else:
                st.error(f"❌ Needs Improvement - Average TAT is {avg_tat:.1f}h (Target: 48h)")

            # TAT Distribution
            st.markdown("##### TAT Distribution")
            tat_ranges = {
                "< 24h": len([m for m in filtered_metrics if m.average_tat < 24]),
                "24-48h": len([m for m in filtered_metrics if 24 <= m.average_tat <= 48]),
                "48-72h": len([m for m in filtered_metrics if 48 < m.average_tat <= 72]),
                "> 72h": len([m for m in filtered_metrics if m.average_tat > 72])
            }

            for range_label, count in tat_ranges.items():
                percentage = calculate_percentage(count, len(filtered_metrics))
                st.write(f"**{range_label}:** {count} days ({percentage:.1f}%)")

    with tab3:
        st.subheader("Quality Metrics")

        col1, col2 = st.columns(2)

        with col1:
            # Pass rate trend
            pass_rate_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'pass_rate')
            st.plotly_chart(pass_rate_chart, use_container_width=True)

            # Quality Statistics
            st.markdown("##### Quality Statistics")
            avg_pass_rate = sum(m.pass_rate for m in filtered_metrics) / len(filtered_metrics)
            avg_ftp_rate = sum(m.first_time_pass_rate for m in filtered_metrics) / len(filtered_metrics)

            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Avg Pass Rate", f"{avg_pass_rate:.1f}%")
                st.metric("Target", "95%")

            with stat_col2:
                st.metric("First-Time Pass", f"{avg_ftp_rate:.1f}%")
                st.metric("Target", "90%")

        with col2:
            # First-time pass rate trend
            ftp_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'first_time_pass_rate')
            st.plotly_chart(ftp_chart, use_container_width=True)

            # Quality Performance
            st.markdown("##### Quality Performance Rating")

            if avg_pass_rate >= 95:
                st.success(f"✅ Excellent - Pass rate is {avg_pass_rate:.1f}% (Target: 95%)")
            elif avg_pass_rate >= 90:
                st.warning(f"⚠️ Good - Pass rate is {avg_pass_rate:.1f}% (Target: 95%)")
            else:
                st.error(f"❌ Needs Improvement - Pass rate is {avg_pass_rate:.1f}% (Target: 95%)")

    with tab4:
        st.subheader("Resource Utilization")

        col1, col2 = st.columns(2)

        with col1:
            # Equipment utilization trend
            util_chart = chart_builder.create_kpi_trend_chart(filtered_metrics, 'equipment_utilization')
            st.plotly_chart(util_chart, use_container_width=True)

            # Utilization Statistics
            st.markdown("##### Utilization Statistics")
            avg_util = sum(m.equipment_utilization for m in filtered_metrics) / len(filtered_metrics)
            max_util = max(m.equipment_utilization for m in filtered_metrics)
            min_util = min(m.equipment_utilization for m in filtered_metrics)

            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("Average Utilization", f"{avg_util:.1f}%")
                st.metric("Target", "80%")

            with stat_col2:
                st.metric("Peak Utilization", f"{max_util:.1f}%")
                st.metric("Lowest", f"{min_util:.1f}%")

        with col2:
            # Equipment utilization by equipment
            eq_util_chart = chart_builder.create_equipment_utilization_chart(equipment[:10])
            st.plotly_chart(eq_util_chart, use_container_width=True)

            # Performance rating
            st.markdown("##### Utilization Performance")

            if avg_util >= 80:
                st.success(f"✅ Excellent - Utilization is {avg_util:.1f}% (Target: 80%)")
            elif avg_util >= 70:
                st.warning(f"⚠️ Good - Utilization is {avg_util:.1f}% (Target: 80%)")
            else:
                st.error(f"❌ Underutilized - Utilization is {avg_util:.1f}% (Target: 80%)")

    # Protocol Type Performance
    st.markdown("---")
    st.subheader("📊 Protocol Type Performance")

    type_breakdown = analytics.get_protocol_type_breakdown()

    if type_breakdown:
        type_data = []
        for ptype, stats in type_breakdown.items():
            type_data.append({
                'Protocol Type': ptype,
                'Total': stats['total'],
                'Completed': stats['completed'],
                'In Progress': stats['in_progress'],
                'Pending': stats['pending'],
                'Completion Rate': f"{stats['completion_rate']:.1f}%",
                'Pass Rate': f"{stats['pass_rate']:.1f}%",
                'Avg Duration': f"{stats['average_duration']:.1f}h"
            })

        type_df = pd.DataFrame(type_data)
        st.dataframe(type_df, use_container_width=True, height=400)

    # Export section
    st.markdown("---")
    st.subheader("📥 Export KPI Report")

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.info("Excel export functionality - Coming soon!")

    with export_col2:
        if st.button("📄 Export to PDF", use_container_width=True):
            st.info("PDF export functionality - Coming soon!")

    with export_col3:
        if st.button("📋 Export to CSV", use_container_width=True):
            # Create CSV from metrics
            metrics_data = []
            for m in filtered_metrics:
                metrics_data.append({
                    'Date': m.date.strftime('%Y-%m-%d'),
                    'Total Samples': m.total_samples,
                    'Completed': m.completed_protocols,
                    'Pending': m.pending_protocols,
                    'Failed': m.failed_protocols,
                    'Avg TAT': m.average_tat,
                    'Pass Rate': m.pass_rate,
                    'FTP Rate': m.first_time_pass_rate,
                    'Equipment Util': m.equipment_utilization,
                    'Throughput': m.throughput_daily
                })

            metrics_df = pd.DataFrame(metrics_data)
            csv_data = metrics_df.to_csv(index=False)

            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"kpi_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

else:
    st.warning("No metrics data available for the selected period.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    f"KPI Dashboard v1.0 | Tracking {len(filtered_metrics)} days of metrics | "
    f"Last Updated: {format_datetime(datetime.now())}"
    "</div>",
    unsafe_allow_html=True
)
