"""
Analytics Dashboard
Advanced analytics and performance metrics for PV testing
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import json
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_execution_analytics(start_date: str = None, end_date: str = None,
                            protocol_id: str = None, status: str = None) -> List[Dict]:
    """Get protocol execution analytics with filters"""
    db = st.session_state.db

    query = """
        SELECT
            execution_id,
            protocol_id,
            protocol_name,
            status,
            test_result,
            start_date,
            end_date,
            duration_hours,
            created_at,
            updated_at
        FROM protocol_executions
        WHERE 1=1
    """

    params = []

    if start_date:
        query += " AND DATE(created_at) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(created_at) <= ?"
        params.append(end_date)

    if protocol_id:
        query += " AND protocol_id = ?"
        params.append(protocol_id)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"

    return db.execute_query(query, tuple(params))

def get_performance_metrics(start_date: str = None, end_date: str = None) -> Dict:
    """Calculate performance metrics"""
    db = st.session_state.db

    metrics = {}

    # Total executions
    query = "SELECT COUNT(*) as count FROM protocol_executions WHERE 1=1"
    params = []

    if start_date:
        query += " AND DATE(created_at) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(created_at) <= ?"
        params.append(end_date)

    metrics['total_executions'] = db.execute_query(query, tuple(params))[0]['count']

    # Completed tests
    completed_query = query + " AND status = 'completed'"
    metrics['completed'] = db.execute_query(completed_query, tuple(params))[0]['count']

    # Success rate
    pass_query = query + " AND test_result = 'pass'"
    metrics['passed'] = db.execute_query(pass_query, tuple(params))[0]['count']

    metrics['success_rate'] = (metrics['passed'] / metrics['total_executions'] * 100) if metrics['total_executions'] > 0 else 0

    # Average duration
    duration_query = """
        SELECT AVG(duration_hours) as avg_duration
        FROM protocol_executions
        WHERE duration_hours IS NOT NULL
    """
    if params:
        duration_query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"

    avg_result = db.execute_query(duration_query, tuple(params))
    metrics['avg_duration'] = avg_result[0]['avg_duration'] if avg_result and avg_result[0]['avg_duration'] else 0

    return metrics

def get_duration_analysis() -> List[Dict]:
    """Analyze test durations by protocol"""
    db = st.session_state.db

    query = """
        SELECT
            protocol_id,
            protocol_name,
            AVG(duration_hours) as avg_duration,
            MIN(duration_hours) as min_duration,
            MAX(duration_hours) as max_duration,
            COUNT(*) as count
        FROM protocol_executions
        WHERE duration_hours IS NOT NULL
        GROUP BY protocol_id, protocol_name
        ORDER BY avg_duration DESC
    """

    return db.execute_query(query)

def get_success_rate_by_protocol() -> List[Dict]:
    """Calculate success rate by protocol"""
    db = st.session_state.db

    query = """
        SELECT
            protocol_id,
            protocol_name,
            COUNT(*) as total,
            SUM(CASE WHEN test_result = 'pass' THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN test_result = 'fail' THEN 1 ELSE 0 END) as failed
        FROM protocol_executions
        WHERE test_result IS NOT NULL
        GROUP BY protocol_id, protocol_name
        HAVING COUNT(*) > 0
        ORDER BY total DESC
    """

    results = db.execute_query(query)

    # Calculate success rate
    for item in results:
        item['success_rate'] = (item['passed'] / item['total'] * 100) if item['total'] > 0 else 0

    return results

def get_equipment_utilization() -> List[Dict]:
    """Analyze equipment utilization"""
    db = st.session_state.db

    query = """
        SELECT
            equipment_id,
            equipment_name,
            equipment_type,
            COUNT(*) as usage_count,
            availability_status
        FROM equipment_planning
        WHERE equipment_id IS NOT NULL
        GROUP BY equipment_id, equipment_name, equipment_type, availability_status
        ORDER BY usage_count DESC
    """

    return db.execute_query(query)

def get_timeline_distribution(days: int = 30) -> List[Dict]:
    """Get test distribution over time"""
    db = st.session_state.db

    query = f"""
        SELECT
            DATE(created_at) as date,
            COUNT(*) as count,
            SUM(CASE WHEN test_result = 'pass' THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN test_result = 'fail' THEN 1 ELSE 0 END) as failed
        FROM protocol_executions
        WHERE created_at >= DATE('now', '-{days} days')
        GROUP BY DATE(created_at)
        ORDER BY date
    """

    return db.execute_query(query)

def get_protocol_categories() -> Dict[str, int]:
    """Group protocols by category"""
    db = st.session_state.db

    query = """
        SELECT protocol_id, COUNT(*) as count
        FROM protocol_executions
        GROUP BY protocol_id
    """

    results = db.execute_query(query)

    categories = {
        'Electrical': 0,
        'Reliability': 0,
        'Mechanical': 0,
        'Quality Control': 0,
        'Other': 0
    }

    # Categorize based on protocol ID patterns
    for item in results:
        protocol_id = item['protocol_id']

        # Simple categorization based on common protocol IDs
        if any(x in protocol_id for x in ['026', '027', '022', '001']):  # I-V, STC, Temp Coeff, LID/LIS
            categories['Electrical'] += item['count']
        elif any(x in protocol_id for x in ['002', '003', '004', '030']):  # Thermal, Damp Heat, Humidity, PID
            categories['Reliability'] += item['count']
        elif any(x in protocol_id for x in ['011', '012', '014']):  # Mechanical Load, Hail, Twist
            categories['Mechanical'] += item['count']
        elif any(x in protocol_id for x in ['034', '035', '036', '051']):  # EL, Thermo, Visual, Flash
            categories['Quality Control'] += item['count']
        else:
            categories['Other'] += item['count']

    return categories

def get_monthly_statistics() -> List[Dict]:
    """Get monthly statistics for trend analysis"""
    db = st.session_state.db

    query = """
        SELECT
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as total_tests,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN test_result = 'pass' THEN 1 ELSE 0 END) as passed,
            AVG(duration_hours) as avg_duration
        FROM protocol_executions
        WHERE created_at >= DATE('now', '-12 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month
    """

    return db.execute_query(query)

# ============================================
# PAGE CONTENT
# ============================================

st.title("📊 Analytics Dashboard")
st.markdown("### Advanced Analytics and Performance Metrics")
st.markdown("---")

# ============================================
# FILTERS
# ============================================

st.subheader("🔍 Filters")

filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

with filter_col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=30),
        max_value=date.today()
    )

with filter_col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        max_value=date.today()
    )

with filter_col3:
    # Get unique protocols
    protocol_query = "SELECT DISTINCT protocol_id, protocol_name FROM protocol_executions ORDER BY protocol_id"
    protocols = st.session_state.db.execute_query(protocol_query)
    protocol_options = {"All Protocols": None}
    protocol_options.update({f"{p['protocol_id']}: {p['protocol_name'][:30]}": p['protocol_id'] for p in protocols})

    selected_protocol_display = st.selectbox("Protocol", list(protocol_options.keys()))
    selected_protocol = protocol_options[selected_protocol_display]

with filter_col4:
    status_filter = st.selectbox(
        "Status",
        options=["All", "not_started", "in_progress", "completed", "failed", "cancelled"]
    )

with filter_col5:
    st.write("")
    st.write("")
    apply_filters = st.button("📊 Apply Filters", use_container_width=True)

# Set filter values
if apply_filters:
    filter_start = start_date.isoformat()
    filter_end = end_date.isoformat()
    filter_protocol = selected_protocol
    filter_status = None if status_filter == "All" else status_filter
else:
    filter_start = (date.today() - timedelta(days=30)).isoformat()
    filter_end = date.today().isoformat()
    filter_protocol = None
    filter_status = None

st.markdown("---")

# ============================================
# PERFORMANCE METRICS
# ============================================

try:
    st.subheader("📈 Performance Metrics")

    metrics = get_performance_metrics(filter_start, filter_end)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Total Executions", metrics['total_executions'])

    with metric_col2:
        st.metric("Completed Tests", metrics['completed'])

    with metric_col3:
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")

    with metric_col4:
        st.metric("Avg Duration", f"{metrics['avg_duration']:.1f}h")

    st.markdown("---")

    # ============================================
    # CHARTS ROW 1: DURATION & SUCCESS RATE
    # ============================================

    st.subheader("📊 Protocol Analysis")

    chart_col1, chart_col2 = st.columns(2)

    # Duration Analysis
    with chart_col1:
        st.markdown("#### Average Duration by Protocol")

        duration_data = get_duration_analysis()

        if duration_data:
            # Take top 15 protocols by count
            top_duration = sorted(duration_data, key=lambda x: x['count'], reverse=True)[:15]

            fig_duration = go.Figure()

            fig_duration.add_trace(go.Bar(
                x=[item['avg_duration'] for item in top_duration],
                y=[f"{item['protocol_id']}: {item['protocol_name'][:25]}" for item in top_duration],
                orientation='h',
                marker=dict(
                    color=[item['avg_duration'] for item in top_duration],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=[f"{item['avg_duration']:.1f}h" for item in top_duration],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Avg Duration: %{x:.2f}h<br>Tests: %{customdata}<extra></extra>',
                customdata=[item['count'] for item in top_duration]
            ))

            fig_duration.update_layout(
                height=500,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Average Duration (hours)",
                yaxis_title="Protocol"
            )

            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("No duration data available")

    # Success Rate by Protocol
    with chart_col2:
        st.markdown("#### Success Rate by Protocol")

        success_data = get_success_rate_by_protocol()

        if success_data:
            # Take top 15 protocols by total
            top_success = sorted(success_data, key=lambda x: x['total'], reverse=True)[:15]

            fig_success = go.Figure()

            fig_success.add_trace(go.Bar(
                x=[item['success_rate'] for item in top_success],
                y=[f"{item['protocol_id']}: {item['protocol_name'][:25]}" for item in top_success],
                orientation='h',
                marker=dict(
                    color=[item['success_rate'] for item in top_success],
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=100,
                    showscale=True
                ),
                text=[f"{item['success_rate']:.1f}%" for item in top_success],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Success Rate: %{x:.1f}%<br>Passed: %{customdata[0]}/%{customdata[1]}<extra></extra>',
                customdata=[[item['passed'], item['total']] for item in top_success]
            ))

            fig_success.update_layout(
                height=500,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Success Rate (%)",
                xaxis=dict(range=[0, 100]),
                yaxis_title="Protocol"
            )

            st.plotly_chart(fig_success, use_container_width=True)
        else:
            st.info("No success rate data available")

    st.markdown("---")

    # ============================================
    # TIMELINE DISTRIBUTION
    # ============================================

    st.subheader("📅 Test Distribution Over Time")

    timeline_col1, timeline_col2 = st.columns([1, 3])

    with timeline_col1:
        timeline_days = st.selectbox(
            "Time Range",
            options=[7, 14, 30, 60, 90, 180],
            index=2,
            format_func=lambda x: f"Last {x} days"
        )

    timeline_data = get_timeline_distribution(timeline_days)

    if timeline_data:
        fig_timeline = go.Figure()

        fig_timeline.add_trace(go.Scatter(
            x=[item['date'] for item in timeline_data],
            y=[item['count'] for item in timeline_data],
            mode='lines+markers',
            name='Total Tests',
            line=dict(width=3, color='#636EFA'),
            marker=dict(size=8)
        ))

        fig_timeline.add_trace(go.Scatter(
            x=[item['date'] for item in timeline_data],
            y=[item['passed'] for item in timeline_data],
            mode='lines+markers',
            name='Passed',
            line=dict(width=2, color='#00CC96'),
            marker=dict(size=6)
        ))

        fig_timeline.add_trace(go.Scatter(
            x=[item['date'] for item in timeline_data],
            y=[item['failed'] for item in timeline_data],
            mode='lines+markers',
            name='Failed',
            line=dict(width=2, color='#EF553B'),
            marker=dict(size=6)
        ))

        fig_timeline.update_layout(
            height=350,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title="Date",
            yaxis_title="Number of Tests",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            hovermode='x unified'
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available")

    st.markdown("---")

    # ============================================
    # PROTOCOL CATEGORIES & EQUIPMENT
    # ============================================

    st.subheader("📊 Additional Analytics")

    cat_col, equip_col = st.columns(2)

    # Protocol Categories
    with cat_col:
        st.markdown("#### Tests by Category")

        categories = get_protocol_categories()

        if any(v > 0 for v in categories.values()):
            fig_categories = go.Figure(data=[go.Pie(
                labels=list(categories.keys()),
                values=list(categories.values()),
                hole=0.4,
                marker=dict(
                    colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
                )
            )])

            fig_categories.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("No category data available")

    # Equipment Utilization
    with equip_col:
        st.markdown("#### Equipment Utilization")

        equipment_data = get_equipment_utilization()

        if equipment_data:
            # Take top 10 equipment by usage
            top_equipment = sorted(equipment_data, key=lambda x: x['usage_count'], reverse=True)[:10]

            fig_equipment = go.Figure(data=[go.Bar(
                x=[item['usage_count'] for item in top_equipment],
                y=[f"{item['equipment_id']}: {item.get('equipment_name', 'N/A')[:20]}" for item in top_equipment],
                orientation='h',
                marker=dict(color='#AB63FA')
            )])

            fig_equipment.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Usage Count",
                yaxis_title="Equipment"
            )

            st.plotly_chart(fig_equipment, use_container_width=True)
        else:
            st.info("No equipment data available")

    st.markdown("---")

    # ============================================
    # MONTHLY TRENDS
    # ============================================

    st.subheader("📈 Monthly Trends (Last 12 Months)")

    monthly_data = get_monthly_statistics()

    if monthly_data:
        fig_monthly = go.Figure()

        # Total tests
        fig_monthly.add_trace(go.Bar(
            x=[item['month'] for item in monthly_data],
            y=[item['total_tests'] for item in monthly_data],
            name='Total Tests',
            marker=dict(color='#636EFA')
        ))

        # Completed tests
        fig_monthly.add_trace(go.Bar(
            x=[item['month'] for item in monthly_data],
            y=[item['completed'] for item in monthly_data],
            name='Completed',
            marker=dict(color='#00CC96')
        ))

        # Success line
        fig_monthly.add_trace(go.Scatter(
            x=[item['month'] for item in monthly_data],
            y=[item['passed'] for item in monthly_data],
            name='Passed',
            mode='lines+markers',
            line=dict(width=3, color='#FFA15A'),
            marker=dict(size=8),
            yaxis='y2'
        ))

        fig_monthly.update_layout(
            height=400,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title="Month",
            yaxis_title="Number of Tests",
            yaxis2=dict(
                title="Passed Tests",
                overlaying='y',
                side='right'
            ),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            hovermode='x unified',
            barmode='group'
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

        # Display summary table
        st.markdown("#### Monthly Summary Table")

        monthly_table = []
        for item in monthly_data:
            total = item['total_tests']
            completed = item['completed']
            passed = item['passed']
            success_rate = (passed / total * 100) if total > 0 else 0

            monthly_table.append({
                'Month': item['month'],
                'Total Tests': total,
                'Completed': completed,
                'Passed': passed,
                'Success Rate': f"{success_rate:.1f}%",
                'Avg Duration': f"{item['avg_duration']:.1f}h" if item['avg_duration'] else "N/A"
            })

        st.dataframe(monthly_table, use_container_width=True)
    else:
        st.info("No monthly data available")

except Exception as e:
    st.error(f"Error loading analytics: {e}")
    import traceback
    st.code(traceback.format_exc())

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Page Info")
    st.info("""
    **Analytics Dashboard**

    Advanced analytics for:
    - Protocol execution performance
    - Duration analysis
    - Success rate tracking
    - Equipment utilization
    - Timeline trends
    - Monthly statistics

    **Features:**
    - Interactive charts
    - Advanced filtering
    - Date range selection
    - Protocol comparison
    - Category analysis

    **Usage:**
    1. Set filters
    2. Apply filters
    3. Review metrics
    4. Analyze trends
    """)

    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
