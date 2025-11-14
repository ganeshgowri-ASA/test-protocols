"""
Master Dashboard - Real-time protocol execution monitoring
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from utils.data_generator import get_sample_data
from utils.helpers import (
    format_datetime, get_status_color, get_status_icon,
    calculate_percentage, get_priority_color
)
from visualizations.charts import ChartBuilder
from models.protocol import ProtocolStatus
from analytics.protocol_analytics import ProtocolAnalytics


# Page configuration
st.set_page_config(
    page_title="Master Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .priority-high {
        background-color: #ff4444;
        color: white;
    }
    .priority-urgent {
        background-color: #cc0000;
        color: white;
    }
    .dataframe-container {
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Title and header
st.title("📊 Master Dashboard & Analytics Engine")
st.markdown("### Real-time Visibility Across All 54 Test Protocols")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_sample_data()

data = load_data()
protocols = data['protocols']
service_requests = data['service_requests']
equipment = data['equipment']
kpi_metrics = data['kpi_metrics']
notifications = data['notifications']

# Initialize analytics
analytics = ProtocolAnalytics(protocols)
chart_builder = ChartBuilder()

# Sidebar filters
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.selectbox(
    "Time Period",
    ["Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
    index=2
)

status_filter = st.sidebar.multiselect(
    "Protocol Status",
    ["completed", "in_progress", "pending", "failed", "on_hold"],
    default=["in_progress", "pending"]
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Last updated timestamp
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last Updated:** {format_datetime(datetime.now())}")

# Main dashboard content
st.markdown("---")

# Top-level KPIs
col1, col2, col3, col4, col5 = st.columns(5)

overall_stats = analytics.get_overall_statistics()

with col1:
    st.metric(
        label="📋 Total Protocols",
        value=overall_stats['total_protocols'],
        delta=f"{overall_stats['completion_rate']:.1f}% Complete"
    )

with col2:
    in_progress = overall_stats['in_progress']
    st.metric(
        label="🔄 In Progress",
        value=in_progress,
        delta=f"{len([p for p in protocols if p.is_overdue])} Overdue" if any(p.is_overdue for p in protocols) else "On Track",
        delta_color="inverse" if any(p.is_overdue for p in protocols) else "normal"
    )

with col3:
    active_requests = len([sr for sr in service_requests if sr.status == "active"])
    st.metric(
        label="📝 Active Requests",
        value=active_requests,
        delta=f"{len(service_requests)} Total"
    )

with col4:
    pending_inspections = len([p for p in protocols if p.status == ProtocolStatus.PENDING])
    st.metric(
        label="⏳ Pending Queue",
        value=pending_inspections,
        delta="Awaiting Inspection"
    )

with col5:
    qc_pass_rate = overall_stats['pass_rate']
    st.metric(
        label="✅ QC Pass Rate",
        value=f"{qc_pass_rate:.1f}%",
        delta=f"Target: 95%",
        delta_color="normal" if qc_pass_rate >= 95 else "inverse"
    )

st.markdown("---")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Real-time Status",
    "🔧 Equipment",
    "📋 Service Requests",
    "🔔 Notifications"
])

with tab1:
    st.subheader("Protocol Execution Overview")

    # Two column layout
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Timeline Gantt chart
        st.markdown("##### Protocol Timeline")
        gantt_fig = chart_builder.create_timeline_gantt(
            [p for p in protocols if p.status != ProtocolStatus.PENDING][:20]
        )
        st.plotly_chart(gantt_fig, use_container_width=True)

    with col_right:
        # Status distribution
        st.markdown("##### Status Distribution")
        status_fig = chart_builder.create_protocol_status_distribution(protocols)
        st.plotly_chart(status_fig, use_container_width=True)

    # Performance metrics
    st.markdown("---")
    st.subheader("Performance Indicators")

    perf_col1, perf_col2, perf_col3 = st.columns(3)

    with perf_col1:
        avg_tat = kpi_metrics[-1].average_tat if kpi_metrics else 0
        st.plotly_chart(
            chart_builder.create_status_gauge(
                avg_tat, "Average TAT (hours)", max_value=100, threshold=48, unit=" hrs"
            ),
            use_container_width=True
        )

    with perf_col2:
        pass_rate = kpi_metrics[-1].pass_rate if kpi_metrics else 0
        st.plotly_chart(
            chart_builder.create_status_gauge(
                pass_rate, "Pass Rate", max_value=100, threshold=95
            ),
            use_container_width=True
        )

    with perf_col3:
        eq_util = kpi_metrics[-1].equipment_utilization if kpi_metrics else 0
        st.plotly_chart(
            chart_builder.create_status_gauge(
                eq_util, "Equipment Utilization", max_value=100, threshold=80
            ),
            use_container_width=True
        )

with tab2:
    st.subheader("Real-time Protocol Status")

    # Filter protocols by status
    if status_filter:
        filtered_protocols = [
            p for p in protocols if p.status.value in status_filter
        ]
    else:
        filtered_protocols = protocols

    # Display protocol table
    protocol_data = []
    for protocol in filtered_protocols[:50]:  # Limit to 50 for performance
        protocol_data.append({
            'ID': protocol.protocol_id,
            'Protocol': protocol.protocol_name[:40] + '...' if len(protocol.protocol_name) > 40 else protocol.protocol_name,
            'Type': protocol.protocol_type.value,
            'Status': f"{get_status_icon(protocol.status.value)} {protocol.status.value.title()}",
            'QC': get_status_icon(protocol.qc_result.value),
            'Operator': protocol.operator or 'Unassigned',
            'Duration': f"{protocol.duration_hours:.1f}h" if protocol.duration_hours else "N/A",
            'Started': format_datetime(protocol.start_time, "%m/%d %H:%M") if protocol.start_time else "Not Started"
        })

    if protocol_data:
        df = pd.DataFrame(protocol_data)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No protocols match the selected filters.")

    # Quick stats
    st.markdown("---")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Filtered Protocols", len(filtered_protocols))

    with stat_col2:
        completed_today = len([
            p for p in filtered_protocols
            if p.end_time and p.end_time.date() == datetime.now().date()
        ])
        st.metric("Completed Today", completed_today)

    with stat_col3:
        avg_duration = sum(p.duration_hours for p in filtered_protocols if p.duration_hours) / len([p for p in filtered_protocols if p.duration_hours]) if filtered_protocols else 0
        st.metric("Avg Duration", f"{avg_duration:.1f}h")

    with stat_col4:
        overdue = len([p for p in filtered_protocols if p.is_overdue])
        st.metric("Overdue", overdue, delta_color="inverse")

with tab3:
    st.subheader("Equipment Utilization")

    # Equipment utilization chart
    eq_chart = chart_builder.create_equipment_utilization_chart(equipment[:15])
    st.plotly_chart(eq_chart, use_container_width=True)

    st.markdown("---")

    # Equipment status table
    st.markdown("##### Equipment Status Overview")

    eq_data = []
    for eq in equipment:
        eq_data.append({
            'Equipment ID': eq.equipment_id,
            'Name': eq.equipment_name,
            'Type': eq.equipment_type,
            'Status': f"{get_status_icon(eq.status)} {eq.status.title()}",
            'Utilization': f"{eq.utilization_rate:.1f}%",
            'Next Calibration': format_datetime(eq.next_calibration, "%Y-%m-%d") if eq.next_calibration else "N/A",
            'Alert': "⚠️ Due Soon" if eq.calibration_due_soon else "✅"
        })

    eq_df = pd.DataFrame(eq_data)
    st.dataframe(eq_df, use_container_width=True, height=400)

    # Calibration alerts
    due_soon = [eq for eq in equipment if eq.calibration_due_soon]
    if due_soon:
        st.warning(f"⚠️ {len(due_soon)} equipment items require calibration within 30 days!")

with tab4:
    st.subheader("Active Service Requests")

    # Service request table
    sr_data = []
    for sr in service_requests:
        if sr.status == "active":
            # Count protocols for this request
            sr_protocols = [p for p in protocols if p.service_request_id == sr.request_id]
            completed = len([p for p in sr_protocols if p.status == ProtocolStatus.COMPLETED])
            total = len(sr_protocols)

            sr_data.append({
                'Request ID': sr.request_id,
                'Customer': sr.customer_name,
                'Sample ID': sr.sample_id,
                'Priority': sr.priority.upper(),
                'Protocols': f"{completed}/{total}",
                'Progress': f"{calculate_percentage(completed, total):.0f}%",
                'Assigned To': sr.assigned_to or 'Unassigned',
                'Request Date': format_datetime(sr.request_date, "%Y-%m-%d")
            })

    if sr_data:
        sr_df = pd.DataFrame(sr_data)

        # Apply styling based on priority
        st.dataframe(sr_df, use_container_width=True, height=400)

        # Summary metrics
        st.markdown("---")
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

        with sum_col1:
            st.metric("Active Requests", len(sr_data))

        with sum_col2:
            urgent = len([sr for sr in service_requests if sr.priority == "urgent" and sr.status == "active"])
            st.metric("Urgent Priority", urgent, delta_color="inverse" if urgent > 0 else "normal")

        with sum_col3:
            on_hold = len([sr for sr in service_requests if sr.status == "on_hold"])
            st.metric("On Hold", on_hold)

        with sum_col4:
            completed_requests = len([sr for sr in service_requests if sr.status == "completed"])
            st.metric("Completed", completed_requests)
    else:
        st.info("No active service requests.")

with tab5:
    st.subheader("🔔 Recent Notifications & Alerts")

    # Display notifications
    for notif in notifications[:10]:
        icon_map = {
            'alert': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }

        icon = icon_map.get(notif.notification_type, 'ℹ️')
        time_ago = (datetime.now() - notif.created_at).total_seconds() / 3600

        if notif.notification_type == 'alert':
            st.error(f"{icon} **{notif.title}** - {notif.message} ({time_ago:.1f}h ago)")
        elif notif.notification_type == 'warning':
            st.warning(f"{icon} **{notif.title}** - {notif.message} ({time_ago:.1f}h ago)")
        elif notif.notification_type == 'success':
            st.success(f"{icon} **{notif.title}** - {notif.message} ({time_ago:.1f}h ago)")
        else:
            st.info(f"{icon} **{notif.title}** - {notif.message} ({time_ago:.1f}h ago)")

    # Notification summary
    st.markdown("---")
    notif_col1, notif_col2, notif_col3 = st.columns(3)

    with notif_col1:
        alerts = len([n for n in notifications if n.notification_type == 'alert'])
        st.metric("🚨 Critical Alerts", alerts)

    with notif_col2:
        warnings = len([n for n in notifications if n.notification_type == 'warning'])
        st.metric("⚠️ Warnings", warnings)

    with notif_col3:
        unread = len([n for n in notifications if not n.read])
        st.metric("📬 Unread", unread)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Test Protocols Master Dashboard v1.0 | "
    f"Monitoring {len(protocols)} protocols across 54 test types | "
    f"Last refresh: {format_datetime(datetime.now())}"
    "</div>",
    unsafe_allow_html=True
)
