"""Results viewing page for Streamlit UI."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.session import get_session
from database.models import TestRun, TestResult, Measurement
from utils.logging import get_logger

logger = get_logger(__name__)


def render_results_page():
    """Render the test results viewing page."""
    st.title("📊 Test Results")
    st.markdown("View and analyze test results")

    # Check if there's an active test with results
    if st.session_state.get('protocol') and st.session_state.get('test_started'):
        render_active_test_results()
    else:
        st.info("No active test. Historical results will be shown here.")
        render_historical_results()


def render_active_test_results():
    """Render results for the currently active test."""
    protocol = st.session_state['protocol']
    params = st.session_state.get('test_params', {})

    st.subheader("📝 Current Test")

    # Display test info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Protocol", "WET-001")
        st.metric("Sample ID", params.get('sample_information', {}).get('sample_id', 'N/A'))

    with col2:
        st.metric("Measurements", len(protocol.measurements))
        if protocol.measurements:
            latest = protocol.measurements[-1]
            st.metric(
                "Latest Leakage Current",
                f"{latest.values.get('leakage_current', 0):.4f} mA"
            )

    with col3:
        st.metric("Status", "In Progress", delta="Active")

    # Analyze if we have measurements
    if len(protocol.measurements) > 0:
        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔬 Analyze Results", type="primary", use_container_width=True):
                try:
                    analysis = protocol.analyze_results()
                    st.session_state['current_analysis'] = analysis

                    # Display pass/fail
                    if analysis['passed']:
                        st.success(f"✅ TEST PASSED")
                    else:
                        st.error(f"❌ TEST FAILED")

                    st.write(analysis['summary'])

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        with col2:
            if st.button("📄 Generate Report", use_container_width=True):
                try:
                    test_result = protocol._create_test_result(
                        params.get('sample_information', {}).get('sample_id', 'UNKNOWN'),
                        params.get('operator_information', {}).get('operator_name')
                    )

                    report_path = protocol.generate_report(test_result, format='html')
                    st.success(f"Report generated: {report_path}")

                    # Offer download
                    with open(report_path, 'r') as f:
                        st.download_button(
                            "⬇️ Download Report",
                            f.read(),
                            file_name=Path(report_path).name,
                            mime="text/html"
                        )

                except Exception as e:
                    st.error(f"Report generation failed: {e}")

        with col3:
            if st.button("💾 Export Data", use_container_width=True):
                try:
                    import json
                    import tempfile

                    data = {
                        'parameters': params,
                        'measurements': [m.to_dict() for m in protocol.measurements]
                    }

                    json_str = json.dumps(data, indent=2)

                    st.download_button(
                        "⬇️ Download JSON",
                        json_str,
                        file_name=f"wet001_data_{params.get('sample_information', {}).get('sample_id', 'test')}.json",
                        mime="application/json"
                    )

                except Exception as e:
                    st.error(f"Export failed: {e}")

        st.divider()

        # Display analysis results if available
        if 'current_analysis' in st.session_state:
            render_analysis_results(st.session_state['current_analysis'], params)

        # Plot measurements
        render_measurement_plots(protocol.measurements)

        # Show measurement table
        render_measurement_table(protocol.measurements)

    else:
        st.info("No measurements recorded yet. Add measurements to see analysis and charts.")


def render_analysis_results(analysis, params):
    """Render analysis results."""
    st.subheader("📈 Analysis Results")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    acceptance = params.get('acceptance_criteria', {})

    with col1:
        max_leakage = analysis.get('max_leakage_current_measured', 0)
        limit = acceptance.get('max_leakage_current', 0.25)
        delta_color = "inverse" if max_leakage <= limit else "normal"

        st.metric(
            "Max Leakage Current",
            f"{max_leakage:.4f} mA",
            delta=f"Limit: {limit} mA",
            delta_color=delta_color
        )

    with col2:
        avg_leakage = analysis.get('average_leakage_current', 0)
        st.metric(
            "Avg Leakage Current",
            f"{avg_leakage:.4f} mA"
        )

    with col3:
        min_insulation = analysis.get('min_insulation_resistance_measured', 0)
        limit = acceptance.get('min_insulation_resistance', 400)
        delta_color = "normal" if min_insulation >= limit else "inverse"

        st.metric(
            "Min Insulation Resistance",
            f"{min_insulation:.2f} MΩ",
            delta=f"Limit: {limit} MΩ",
            delta_color=delta_color
        )

    with col4:
        duration = analysis.get('test_duration_hours', 0)
        st.metric(
            "Test Duration",
            f"{duration:.2f} hrs"
        )

    # Failure reasons if any
    if analysis.get('failure_reasons'):
        st.warning("**Failure Reasons:**")
        for reason in analysis['failure_reasons']:
            st.write(f"- {reason}")

    # Trending analysis
    if 'trending' in analysis:
        trending = analysis['trending']
        if trending.get('trend') != 'insufficient_data':
            st.info(f"**Trend**: {trending.get('trend', 'N/A').capitalize()}")


def render_measurement_plots(measurements):
    """Render plots of measurement data."""
    if not measurements:
        return

    st.subheader("📊 Measurement Charts")

    # Prepare data
    timestamps = [m.timestamp for m in measurements]
    leakage_currents = [m.values.get('leakage_current', 0) for m in measurements]
    voltages = [m.values.get('voltage', 0) for m in measurements]
    temps = [m.values.get('temperature', 0) for m in measurements]
    humidity = [m.values.get('humidity', 0) for m in measurements]
    insulation = [m.values.get('insulation_resistance', 0) for m in measurements]

    # Leakage current over time
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=timestamps,
        y=leakage_currents,
        mode='lines+markers',
        name='Leakage Current',
        line=dict(color='#e74c3c', width=2),
        marker=dict(size=6)
    ))
    fig1.update_layout(
        title='Leakage Current Over Time',
        xaxis_title='Time',
        yaxis_title='Leakage Current (mA)',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Environmental conditions
    col1, col2 = st.columns(2)

    with col1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=timestamps,
            y=temps,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#f39c12', width=2),
            marker=dict(size=6)
        ))
        fig2.update_layout(
            title='Temperature Over Time',
            xaxis_title='Time',
            yaxis_title='Temperature (°C)',
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=timestamps,
            y=humidity,
            mode='lines+markers',
            name='Humidity',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6)
        ))
        fig3.update_layout(
            title='Humidity Over Time',
            xaxis_title='Time',
            yaxis_title='Relative Humidity (%)',
            height=300
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Insulation resistance
    if any(r > 0 for r in insulation):
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=timestamps,
            y=insulation,
            mode='lines+markers',
            name='Insulation Resistance',
            line=dict(color='#27ae60', width=2),
            marker=dict(size=6)
        ))
        fig4.update_layout(
            title='Insulation Resistance Over Time',
            xaxis_title='Time',
            yaxis_title='Insulation Resistance (MΩ)',
            height=400
        )
        st.plotly_chart(fig4, use_container_width=True)


def render_measurement_table(measurements):
    """Render table of measurements."""
    if not measurements:
        return

    st.subheader("📋 Measurement Data")

    # Convert to DataFrame
    data = []
    for i, m in enumerate(measurements):
        data.append({
            'Index': i + 1,
            'Timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Leakage Current (mA)': f"{m.values.get('leakage_current', 0):.4f}",
            'Voltage (V)': f"{m.values.get('voltage', 0):.1f}",
            'Temperature (°C)': f"{m.values.get('temperature', 0):.1f}",
            'Humidity (%)': f"{m.values.get('humidity', 0):.1f}",
            'Insulation (MΩ)': f"{m.values.get('insulation_resistance', 0):.2f}",
            'Notes': m.notes or ''
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_historical_results():
    """Render historical test results from database."""
    st.info("Historical results feature will load test runs from the database.")
    st.write("Once tests are saved to the database, they will appear here for review.")
