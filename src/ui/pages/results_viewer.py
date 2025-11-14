"""Results Viewer page for analyzing test results."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from src.utils.db import get_db_manager
from src.ui.components.chart_utils import create_time_series_chart, create_distribution_chart


def render_results_viewer() -> None:
    """Render the results viewer page."""
    st.markdown('<p class="main-header">Results Viewer</p>', unsafe_allow_html=True)
    st.markdown("View and analyze test results")

    db_manager = get_db_manager()

    # Get list of test runs
    try:
        with db_manager.get_session() as session:
            from sqlalchemy import text
            result = session.execute(text("SELECT run_id, protocol_id, status, start_time FROM test_runs ORDER BY start_time DESC LIMIT 20"))
            runs = [dict(row._mapping) for row in result.fetchall()]

        if runs:
            # Run selection
            st.markdown("### Select Test Run")

            run_options = [
                f"{run['run_id']} - {run['protocol_id']} ({run['status']}) - {run['start_time']}"
                for run in runs
            ]

            selected_idx = st.selectbox("Test Run", range(len(run_options)), format_func=lambda x: run_options[x])
            selected_run = runs[selected_idx]

            # Display run details
            render_run_details(selected_run['run_id'], db_manager)

        else:
            st.info("No test runs found. Run a test from the Test Dashboard to see results here.")

    except Exception as e:
        st.error(f"Error loading test runs: {str(e)}")
        st.info("Database may not be initialized. Run a test first to create the database.")


def render_run_details(run_id: str, db_manager) -> None:
    """Render detailed results for a test run."""
    st.markdown("---")
    st.markdown("### Test Run Details")

    # Get run summary
    summary = db_manager.get_test_run(run_id)

    if summary:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Protocol", summary.get('protocol_id', 'N/A'))

        with col2:
            st.metric("Status", summary.get('status', 'N/A'))

        with col3:
            st.metric("Measurements", summary.get('measurement_count', 0))

        with col4:
            st.metric("Duration", f"{summary.get('duration_seconds', 0) / 60:.1f} min")

        # Get measurements
        measurements = db_manager.get_measurements(run_id)

        if measurements:
            st.markdown("---")
            st.markdown("### Measurement Data")

            # Convert to DataFrame
            df = pd.DataFrame(measurements)

            # Metric selection
            available_metrics = df['metric_name'].unique()
            selected_metrics = st.multiselect(
                "Select Metrics to Display",
                available_metrics,
                default=list(available_metrics)[:3]
            )

            if selected_metrics:
                # Time series charts
                st.markdown("#### Time Series")

                for metric in selected_metrics:
                    metric_df = df[df['metric_name'] == metric]

                    if len(metric_df) > 0:
                        fig = create_time_series_chart(
                            metric_df,
                            metric,
                            metric_df['metric_unit'].iloc[0] if len(metric_df) > 0 else ''
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # Distribution charts
                st.markdown("#### Distributions")

                dist_cols = st.columns(min(len(selected_metrics), 3))

                for idx, metric in enumerate(selected_metrics):
                    metric_df = df[df['metric_name'] == metric]

                    if len(metric_df) > 0:
                        with dist_cols[idx % 3]:
                            fig = create_distribution_chart(metric_df, metric)
                            st.plotly_chart(fig, use_container_width=True)

                # Statistics table
                st.markdown("#### Statistical Summary")

                stats_data = []
                for metric in selected_metrics:
                    metric_values = df[df['metric_name'] == metric]['metric_value']

                    if len(metric_values) > 0:
                        stats_data.append({
                            'Metric': metric,
                            'Count': len(metric_values),
                            'Mean': f"{metric_values.mean():.3f}",
                            'Std Dev': f"{metric_values.std():.3f}",
                            'Min': f"{metric_values.min():.3f}",
                            'Max': f"{metric_values.max():.3f}",
                            'Median': f"{metric_values.median():.3f}"
                        })

                if stats_data:
                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

                # Raw data
                with st.expander("📋 View Raw Data"):
                    filtered_df = df[df['metric_name'].isin(selected_metrics)]
                    st.dataframe(filtered_df, use_container_width=True)

        else:
            st.info("No measurements found for this test run.")
