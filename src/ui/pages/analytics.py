"""Analytics page for test data analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.models.base import get_session
from src.models import TestRun, Protocol
from src.models.test_run import TestStatus, TestResult


def render_analytics_page():
    """Render the analytics page."""
    st.title("📈 Analytics & Insights")
    st.markdown("Analyze test trends and performance metrics")

    session = get_session(st.session_state.engine)
    test_runs = session.query(TestRun).all()

    if not test_runs:
        st.info("No test data available for analysis yet. Run some tests to see analytics here.")
        session.close()
        return

    # Date range filter
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )

    # Filter test runs by date
    filtered_runs = [
        r for r in test_runs
        if r.created_at.date() >= start_date and r.created_at.date() <= end_date
    ]

    st.markdown("---")

    # Key metrics
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_tests = len(filtered_runs)
        st.metric("Total Tests", total_tests)

    with col2:
        completed = len([r for r in filtered_runs if r.status == TestStatus.COMPLETED])
        completion_rate = (completed / total_tests * 100) if total_tests > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")

    with col3:
        passed = len([r for r in filtered_runs if r.result == TestResult.PASS])
        pass_rate = (passed / completed * 100) if completed > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")

    with col4:
        failed = len([r for r in filtered_runs if r.result == TestResult.FAIL])
        st.metric("Failed Tests", failed)

    st.markdown("---")

    # Charts
    tab1, tab2, tab3 = st.tabs(["Test Status Distribution", "Results by Protocol", "Test Timeline"])

    with tab1:
        render_status_distribution(filtered_runs)

    with tab2:
        render_results_by_protocol(filtered_runs, session)

    with tab3:
        render_test_timeline(filtered_runs)

    session.close()


def render_status_distribution(test_runs):
    """Render test status distribution chart."""
    st.subheader("Test Status Distribution")

    if not test_runs:
        st.info("No data to display.")
        return

    # Count by status
    status_counts = {}
    for run in test_runs:
        status = run.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    # Create pie chart
    fig = px.pie(
        names=list(status_counts.keys()),
        values=list(status_counts.values()),
        title="Distribution of Test Status"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_results_by_protocol(test_runs, session):
    """Render test results grouped by protocol."""
    st.subheader("Results by Protocol")

    if not test_runs:
        st.info("No data to display.")
        return

    # Group by protocol
    protocol_stats = {}

    for run in test_runs:
        protocol_id = run.protocol.protocol_id if run.protocol else "Unknown"

        if protocol_id not in protocol_stats:
            protocol_stats[protocol_id] = {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "other": 0
            }

        protocol_stats[protocol_id]["total"] += 1

        if run.result == TestResult.PASS:
            protocol_stats[protocol_id]["pass"] += 1
        elif run.result == TestResult.FAIL:
            protocol_stats[protocol_id]["fail"] += 1
        else:
            protocol_stats[protocol_id]["other"] += 1

    # Create DataFrame
    df_data = []
    for protocol_id, stats in protocol_stats.items():
        df_data.append({
            "Protocol": protocol_id,
            "Total Tests": stats["total"],
            "Passed": stats["pass"],
            "Failed": stats["fail"],
            "Other": stats["other"],
            "Pass Rate": f"{(stats['pass'] / stats['total'] * 100):.1f}%" if stats["total"] > 0 else "0%"
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

    # Bar chart
    if df_data:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name="Passed",
            x=[d["Protocol"] for d in df_data],
            y=[d["Passed"] for d in df_data],
            marker_color="green"
        ))

        fig.add_trace(go.Bar(
            name="Failed",
            x=[d["Protocol"] for d in df_data],
            y=[d["Failed"] for d in df_data],
            marker_color="red"
        ))

        fig.add_trace(go.Bar(
            name="Other",
            x=[d["Protocol"] for d in df_data],
            y=[d["Other"] for d in df_data],
            marker_color="gray"
        ))

        fig.update_layout(
            title="Test Results by Protocol",
            xaxis_title="Protocol",
            yaxis_title="Number of Tests",
            barmode="stack"
        )

        st.plotly_chart(fig, use_container_width=True)


def render_test_timeline(test_runs):
    """Render test timeline chart."""
    st.subheader("Test Timeline")

    if not test_runs:
        st.info("No data to display.")
        return

    # Group by date
    date_counts = {}

    for run in test_runs:
        date = run.created_at.date()
        if date not in date_counts:
            date_counts[date] = 0
        date_counts[date] += 1

    # Create line chart
    dates = sorted(date_counts.keys())
    counts = [date_counts[d] for d in dates]

    fig = px.line(
        x=dates,
        y=counts,
        title="Tests Executed Over Time",
        labels={"x": "Date", "y": "Number of Tests"}
    )

    fig.update_traces(mode="lines+markers")

    st.plotly_chart(fig, use_container_width=True)
