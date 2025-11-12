"""
Quality Assurance Dashboard - Streamlit Application

This dashboard provides comprehensive QA metrics, test results,
and protocol validation status visualization.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring import ProtocolMonitor, AlertManager, MetricsCollector
from test_data import ProtocolGenerator, MeasurementGenerator


# Page configuration
st.set_page_config(
    page_title="QA Testing Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'monitor' not in st.session_state:
        st.session_state.monitor = ProtocolMonitor()
    if 'metrics_collector' not in st.session_state:
        st.session_state.metrics_collector = MetricsCollector()
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = AlertManager()


def generate_sample_data():
    """Generate sample data for dashboard."""
    protocol_gen = ProtocolGenerator(seed=42)
    measurement_gen = MeasurementGenerator(seed=42)

    # Generate sample protocols
    protocols = protocol_gen.generate_batch(count=10)

    # Generate sample test results
    test_results = []
    for i in range(50):
        test_results.append({
            "test_name": f"Test_{i+1}",
            "passed": i % 5 != 0,  # 80% pass rate
            "execution_time": 1.5 + i * 0.1,
            "timestamp": datetime.now() - timedelta(hours=i),
        })

    return protocols, test_results


def render_overview_metrics():
    """Render overview metrics cards."""
    st.header("📊 Overview Metrics")

    # Generate sample metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Test Pass Rate",
            value="85.2%",
            delta="2.5%",
            delta_color="normal",
        )

    with col2:
        st.metric(
            label="Code Coverage",
            value="82.7%",
            delta="1.3%",
            delta_color="normal",
        )

    with col3:
        st.metric(
            label="Active Protocols",
            value="12",
            delta="-2",
            delta_color="inverse",
        )

    with col4:
        st.metric(
            label="Critical Alerts",
            value="3",
            delta="1",
            delta_color="inverse",
        )


def render_test_results_chart():
    """Render test results visualization."""
    st.header("🧪 Test Results Over Time")

    # Generate sample data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    test_data = pd.DataFrame({
        'Date': dates,
        'Passed': [45 + i % 10 for i in range(len(dates))],
        'Failed': [5 + i % 3 for i in range(len(dates))],
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=test_data['Date'],
        y=test_data['Passed'],
        name='Passed',
        marker_color='green',
    ))
    fig.add_trace(go.Bar(
        x=test_data['Date'],
        y=test_data['Failed'],
        name='Failed',
        marker_color='red',
    ))

    fig.update_layout(
        barmode='stack',
        title='Test Results Trend',
        xaxis_title='Date',
        yaxis_title='Number of Tests',
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)


def render_protocol_validation_status():
    """Render protocol validation status."""
    st.header("✅ Protocol Validation Status")

    # Sample validation data
    validation_data = pd.DataFrame({
        'Protocol Type': ['Electrical', 'Thermal', 'Mechanical', 'Inspection', 'Environmental'],
        'Validated': [45, 38, 42, 50, 35],
        'Pending': [5, 8, 3, 2, 7],
        'Failed': [2, 1, 0, 0, 3],
    })

    fig = px.bar(
        validation_data,
        x='Protocol Type',
        y=['Validated', 'Pending', 'Failed'],
        title='Protocol Validation by Type',
        barmode='group',
        color_discrete_map={
            'Validated': 'green',
            'Pending': 'orange',
            'Failed': 'red',
        }
    )

    st.plotly_chart(fig, use_container_width=True)


def render_code_coverage():
    """Render code coverage metrics."""
    st.header("📈 Code Coverage")

    col1, col2 = st.columns(2)

    with col1:
        # Coverage by module
        coverage_data = pd.DataFrame({
            'Module': ['protocols', 'validators', 'test_data', 'monitoring', 'handlers'],
            'Coverage': [85.5, 92.3, 78.4, 81.2, 88.9],
        })

        fig = px.bar(
            coverage_data,
            x='Module',
            y='Coverage',
            title='Coverage by Module',
            color='Coverage',
            color_continuous_scale='RdYlGn',
            range_color=[70, 100],
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Overall coverage gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=82.7,
            delta={'reference': 80, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            },
            title={'text': "Overall Coverage"}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def render_error_tracking():
    """Render error tracking and trends."""
    st.header("🚨 Error Tracking")

    col1, col2 = st.columns(2)

    with col1:
        # Error types distribution
        error_data = pd.DataFrame({
            'Error Type': [
                'Validation Error',
                'Range Error',
                'Schema Error',
                'Compliance Error',
                'Data Error'
            ],
            'Count': [12, 8, 5, 3, 7],
        })

        fig = px.pie(
            error_data,
            values='Count',
            names='Error Type',
            title='Error Distribution by Type',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Error trend over time
        dates = pd.date_range(start=datetime.now() - timedelta(days=14), end=datetime.now(), freq='D')
        error_trend = pd.DataFrame({
            'Date': dates,
            'Errors': [15 - i % 8 for i in range(len(dates))],
        })

        fig = px.line(
            error_trend,
            x='Date',
            y='Errors',
            title='Error Trend (Last 14 Days)',
            markers=True,
        )
        fig.update_traces(line_color='red')
        st.plotly_chart(fig, use_container_width=True)


def render_performance_benchmarks():
    """Render performance benchmarks."""
    st.header("⚡ Performance Benchmarks")

    # Sample performance data
    perf_data = pd.DataFrame({
        'Test Suite': [
            'Unit Tests',
            'Integration Tests',
            'E2E Tests',
            'Performance Tests',
        ],
        'Avg Time (s)': [2.3, 15.7, 45.2, 120.5],
        'Tests': [250, 45, 12, 8],
    })

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            perf_data,
            x='Test Suite',
            y='Avg Time (s)',
            title='Average Execution Time',
            color='Avg Time (s)',
            color_continuous_scale='Reds',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            perf_data,
            x='Tests',
            y='Avg Time (s)',
            size='Tests',
            color='Test Suite',
            title='Tests vs Execution Time',
        )
        st.plotly_chart(fig, use_container_width=True)


def render_active_alerts():
    """Render active alerts table."""
    st.header("⚠️ Active Alerts")

    # Sample alerts
    alerts_data = pd.DataFrame({
        'Alert ID': ['ALERT-001', 'ALERT-002', 'ALERT-003'],
        'Type': ['Temperature Anomaly', 'Range Error', 'Execution Time'],
        'Severity': ['Warning', 'Error', 'Warning'],
        'Protocol': ['IEC61215-10-10', 'IEC61215-10-2', 'IEC61215-10-15'],
        'Timestamp': [
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(minutes=30),
        ],
    })

    # Color code severity
    def highlight_severity(val):
        if val == 'Error':
            return 'background-color: #ffcccc'
        elif val == 'Warning':
            return 'background-color: #ffffcc'
        return ''

    styled_df = alerts_data.style.applymap(
        highlight_severity,
        subset=['Severity']
    )

    st.dataframe(styled_df, use_container_width=True)


def render_recent_test_runs():
    """Render recent test runs."""
    st.header("🏃 Recent Test Runs")

    test_runs = pd.DataFrame({
        'Run ID': [f'RUN-{i:04d}' for i in range(1, 11)],
        'Timestamp': [datetime.now() - timedelta(hours=i) for i in range(10)],
        'Tests': [250 + i * 5 for i in range(10)],
        'Passed': [220 + i * 4 for i in range(10)],
        'Failed': [5 + i % 3 for i in range(10)],
        'Duration (s)': [120 + i * 10 for i in range(10)],
    })

    test_runs['Pass Rate %'] = (test_runs['Passed'] / test_runs['Tests'] * 100).round(1)

    st.dataframe(test_runs, use_container_width=True)


def main():
    """Main dashboard function."""
    initialize_session_state()

    # Sidebar
    st.sidebar.title("🔬 QA Testing Dashboard")
    st.sidebar.markdown("---")

    page = st.sidebar.selectbox(
        "Select View",
        [
            "Overview",
            "Test Results",
            "Protocol Validation",
            "Coverage & Quality",
            "Alerts & Errors",
            "Performance",
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "This dashboard provides real-time QA metrics, "
        "test results, and protocol validation status."
    )

    # Main content area
    st.title("🔬 QA Testing Framework Dashboard")
    st.markdown("### Comprehensive Quality Assurance Monitoring")
    st.markdown("---")

    if page == "Overview":
        render_overview_metrics()
        col1, col2 = st.columns(2)
        with col1:
            render_test_results_chart()
        with col2:
            render_code_coverage()

    elif page == "Test Results":
        render_test_results_chart()
        render_recent_test_runs()

    elif page == "Protocol Validation":
        render_protocol_validation_status()

    elif page == "Coverage & Quality":
        render_code_coverage()

    elif page == "Alerts & Errors":
        render_active_alerts()
        render_error_tracking()

    elif page == "Performance":
        render_performance_benchmarks()

    # Footer
    st.markdown("---")
    st.markdown(
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    )


if __name__ == "__main__":
    main()
