"""
SPONGE-001 UI Components
Streamlit/GenSpark UI components for Sponge Effect Testing

Provides interactive interface for test configuration, monitoring, and analysis.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from implementation import (
    SpongeProtocol, TestParameters, TestPhase, TestStatus,
    Measurement, AnalysisResults
)


class SpongeUI:
    """Streamlit UI components for SPONGE-001 protocol"""

    def __init__(self):
        """Initialize UI components"""
        self.protocol = None
        self._init_session_state()

    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'protocol' not in st.session_state:
            st.session_state.protocol = None
        if 'test_plan' not in st.session_state:
            st.session_state.test_plan = None
        if 'current_phase' not in st.session_state:
            st.session_state.current_phase = None

    def render_header(self):
        """Render page header"""
        st.title("🧽 SPONGE-001: Sponge Effect Testing")
        st.markdown("""
        **Moisture Absorption/Desorption Testing Protocol**

        Evaluates reversible and irreversible effects of moisture cycling on PV module performance.
        """)

        # Protocol info
        with st.expander("ℹ️ Protocol Information"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protocol ID", "SPONGE-001")
                st.metric("Category", "Degradation")
            with col2:
                st.metric("Version", "1.0.0")
                st.metric("Standard", "IEC 61215-2:2021")
            with col3:
                st.metric("Min Samples", "3")
                st.metric("Typical Duration", "720 hours")

    def render_configuration_panel(self) -> Optional[TestParameters]:
        """
        Render test configuration panel

        Returns:
            TestParameters if configured, None otherwise
        """
        st.header("⚙️ Test Configuration")

        with st.form("test_config"):
            st.subheader("Cycle Parameters")

            col1, col2 = st.columns(2)

            with col1:
                humidity_cycles = st.number_input(
                    "Number of Humidity Cycles",
                    min_value=5,
                    max_value=50,
                    value=10,
                    step=1,
                    help="Total number of absorption/desorption cycles"
                )

                humid_temp = st.number_input(
                    "Humid Phase Temperature (°C)",
                    min_value=60.0,
                    max_value=95.0,
                    value=85.0,
                    step=0.5
                )

                humid_rh = st.number_input(
                    "Humid Phase Relative Humidity (%)",
                    min_value=60.0,
                    max_value=95.0,
                    value=85.0,
                    step=1.0
                )

                humid_duration = st.number_input(
                    "Humid Phase Duration (hours)",
                    min_value=12,
                    max_value=168,
                    value=24,
                    step=1
                )

            with col2:
                dry_temp = st.number_input(
                    "Dry Phase Temperature (°C)",
                    min_value=20.0,
                    max_value=40.0,
                    value=25.0,
                    step=0.5
                )

                dry_rh = st.number_input(
                    "Dry Phase Relative Humidity (%)",
                    min_value=5.0,
                    max_value=30.0,
                    value=10.0,
                    step=1.0
                )

                dry_duration = st.number_input(
                    "Dry Phase Duration (hours)",
                    min_value=12,
                    max_value=168,
                    value=24,
                    step=1
                )

                measurement_interval = st.number_input(
                    "Measurement Interval (minutes)",
                    min_value=1,
                    max_value=1440,
                    value=60,
                    step=1
                )

            st.subheader("Sample Information")
            sample_ids_input = st.text_area(
                "Sample IDs (one per line)",
                value="MODULE-001\nMODULE-002\nMODULE-003",
                help="Enter sample serial numbers, one per line"
            )

            submitted = st.form_submit_button("Create Test Plan")

            if submitted:
                params = TestParameters(
                    humidity_cycles=humidity_cycles,
                    humid_phase_temperature=humid_temp,
                    humid_phase_rh=humid_rh,
                    humid_phase_duration=humid_duration,
                    dry_phase_temperature=dry_temp,
                    dry_phase_rh=dry_rh,
                    dry_phase_duration=dry_duration,
                    measurement_interval=measurement_interval
                )

                sample_ids = [s.strip() for s in sample_ids_input.split('\n') if s.strip()]

                # Initialize protocol and create test plan
                protocol = SpongeProtocol()
                test_plan = protocol.create_test_plan(params, sample_ids)

                # Store in session state
                st.session_state.protocol = protocol
                st.session_state.test_plan = test_plan

                st.success(f"✅ Test plan created! Test ID: {test_plan['test_id']}")

                return params

        return None

    def render_test_plan_summary(self, test_plan: Dict):
        """Render test plan summary"""
        st.header("📋 Test Plan Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Test ID", test_plan['test_id'][:8] + "...")
            st.metric("Number of Cycles", test_plan['parameters']['humidity_cycles'])

        with col2:
            st.metric("Number of Samples", test_plan['num_samples'])
            st.metric("Total Measurements", test_plan['total_measurements'])

        with col3:
            st.metric("Duration (hours)", f"{test_plan['estimated_duration_hours']}")
            st.metric("Duration (days)", f"{test_plan['estimated_duration_hours'] / 24:.1f}")

        with col4:
            st.metric("Start Time", datetime.fromisoformat(test_plan['start_time']).strftime('%Y-%m-%d %H:%M'))
            st.metric("Est. Completion", datetime.fromisoformat(test_plan['estimated_completion']).strftime('%Y-%m-%d %H:%M'))

        # Measurement schedule
        with st.expander("📅 Measurement Schedule"):
            schedule_df = pd.DataFrame(test_plan['measurement_schedule'])
            schedule_df['time'] = pd.to_datetime(schedule_df['time'])
            schedule_df['actions_str'] = schedule_df['actions'].apply(lambda x: ', '.join(x))

            st.dataframe(
                schedule_df[['time', 'cycle', 'phase', 'actions_str']].rename(
                    columns={'actions_str': 'actions'}
                ),
                use_container_width=True
            )

    def render_data_entry_panel(self, protocol: SpongeProtocol, sample_ids: List[str]):
        """Render data entry panel for measurements"""
        st.header("📊 Data Entry")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_sample = st.selectbox("Sample ID", sample_ids)

        with col2:
            cycle_number = st.number_input("Cycle Number", min_value=0, max_value=50, value=0)

        with col3:
            phase = st.selectbox(
                "Test Phase",
                options=[p.value for p in TestPhase],
                format_func=lambda x: x.title()
            )

        # Measurement inputs
        with st.form("measurement_entry"):
            st.subheader("Measurements")

            col1, col2 = st.columns(2)

            with col1:
                weight_g = st.number_input("Weight (g)", min_value=0.0, step=0.01, format="%.2f")
                pmax_w = st.number_input("Pmax (W)", min_value=0.0, step=0.1, format="%.1f")
                voc_v = st.number_input("Voc (V)", min_value=0.0, step=0.01, format="%.2f")

            with col2:
                isc_a = st.number_input("Isc (A)", min_value=0.0, step=0.01, format="%.2f")
                ff_percent = st.number_input("Fill Factor (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f")

            col3, col4 = st.columns(2)

            with col3:
                temperature_c = st.number_input("Temperature (°C)", min_value=-50.0, max_value=150.0, step=0.1, format="%.1f")

            with col4:
                rh_percent = st.number_input("Relative Humidity (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f")

            submitted = st.form_submit_button("Record Measurement")

            if submitted:
                # Record measurement
                measurement = protocol.record_measurement(
                    sample_id=selected_sample,
                    cycle=cycle_number,
                    phase=TestPhase(phase),
                    weight_g=weight_g if weight_g > 0 else None,
                    pmax_w=pmax_w if pmax_w > 0 else None,
                    voc_v=voc_v if voc_v > 0 else None,
                    isc_a=isc_a if isc_a > 0 else None,
                    ff_percent=ff_percent if ff_percent > 0 else None,
                    temperature_c=temperature_c,
                    rh_percent=rh_percent
                )

                st.success(f"✅ Measurement recorded for {selected_sample} at cycle {cycle_number}, phase {phase}")

                # Update session state
                st.session_state.protocol = protocol

    def render_monitoring_dashboard(self, protocol: SpongeProtocol):
        """Render real-time monitoring dashboard"""
        st.header("📈 Monitoring Dashboard")

        df = protocol.get_measurements_df()

        if df.empty:
            st.info("No measurements recorded yet.")
            return

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Measurements", len(df))

        with col2:
            max_cycle = df['cycle_number'].max()
            st.metric("Current Cycle", int(max_cycle))

        with col3:
            latest_phase = df.iloc[-1]['phase']
            st.metric("Current Phase", latest_phase.title())

        with col4:
            latest_time = df['timestamp'].max()
            st.metric("Last Update", latest_time.strftime('%H:%M:%S'))

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Weight Tracking", "Performance", "Environment", "Data Table"])

        with tab1:
            self._render_weight_charts(df)

        with tab2:
            self._render_performance_charts(df)

        with tab3:
            self._render_environmental_charts(df)

        with tab4:
            st.dataframe(df, use_container_width=True)

    def _render_weight_charts(self, df: pd.DataFrame):
        """Render weight tracking charts"""
        st.subheader("Weight vs. Cycle Number")

        # Filter out null weights
        weight_df = df[df['weight_g'].notna()].copy()

        if weight_df.empty:
            st.info("No weight measurements available.")
            return

        fig = go.Figure()

        for sample_id in weight_df['sample_id'].unique():
            sample_data = weight_df[weight_df['sample_id'] == sample_id]

            fig.add_trace(go.Scatter(
                x=sample_data['cycle_number'],
                y=sample_data['weight_g'],
                mode='lines+markers',
                name=sample_id,
                text=sample_data['phase'],
                hovertemplate='<b>%{text}</b><br>Cycle: %{x}<br>Weight: %{y:.2f} g<extra></extra>'
            ))

        fig.update_layout(
            xaxis_title="Cycle Number",
            yaxis_title="Weight (g)",
            hovermode='closest',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Weight change analysis
        st.subheader("Weight Change Analysis")

        weight_change_data = []
        for sample_id in weight_df['sample_id'].unique():
            sample_data = weight_df[weight_df['sample_id'] == sample_id].sort_values('cycle_number')

            if len(sample_data) > 0:
                initial_weight = sample_data.iloc[0]['weight_g']
                current_weight = sample_data.iloc[-1]['weight_g']
                weight_change_percent = ((current_weight - initial_weight) / initial_weight) * 100

                weight_change_data.append({
                    'Sample ID': sample_id,
                    'Initial Weight (g)': f"{initial_weight:.2f}",
                    'Current Weight (g)': f"{current_weight:.2f}",
                    'Change (%)': f"{weight_change_percent:.3f}"
                })

        if weight_change_data:
            st.table(pd.DataFrame(weight_change_data))

    def _render_performance_charts(self, df: pd.DataFrame):
        """Render performance tracking charts"""
        st.subheader("Pmax Over Cycles")

        pmax_df = df[df['pmax_w'].notna()].copy()

        if pmax_df.empty:
            st.info("No performance measurements available.")
            return

        fig = go.Figure()

        for sample_id in pmax_df['sample_id'].unique():
            sample_data = pmax_df[pmax_df['sample_id'] == sample_id]

            # Normalize to initial value
            initial_pmax = sample_data.iloc[0]['pmax_w']
            sample_data['pmax_normalized'] = (sample_data['pmax_w'] / initial_pmax) * 100

            fig.add_trace(go.Scatter(
                x=sample_data['cycle_number'],
                y=sample_data['pmax_normalized'],
                mode='lines+markers',
                name=sample_id,
                text=sample_data['phase'],
                hovertemplate='<b>%{text}</b><br>Cycle: %{x}<br>Pmax: %{y:.2f}%<extra></extra>'
            ))

        # Add acceptance threshold
        fig.add_hline(y=95, line_dash="dash", line_color="red",
                     annotation_text="95% Threshold (5% degradation limit)")

        fig.update_layout(
            xaxis_title="Cycle Number",
            yaxis_title="Normalized Pmax (%)",
            hovermode='closest',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # IV parameters comparison
        st.subheader("IV Parameters Comparison")

        iv_params_df = df[df['pmax_w'].notna()].copy()

        if not iv_params_df.empty:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Pmax (W)', 'Voc (V)', 'Isc (A)', 'Fill Factor (%)')
            )

            for sample_id in iv_params_df['sample_id'].unique():
                sample_data = iv_params_df[iv_params_df['sample_id'] == sample_id]

                # Pmax
                fig.add_trace(
                    go.Scatter(x=sample_data['cycle_number'], y=sample_data['pmax_w'],
                              name=sample_id, showlegend=True, legendgroup=sample_id),
                    row=1, col=1
                )

                # Voc
                fig.add_trace(
                    go.Scatter(x=sample_data['cycle_number'], y=sample_data['voc_v'],
                              name=sample_id, showlegend=False, legendgroup=sample_id),
                    row=1, col=2
                )

                # Isc
                fig.add_trace(
                    go.Scatter(x=sample_data['cycle_number'], y=sample_data['isc_a'],
                              name=sample_id, showlegend=False, legendgroup=sample_id),
                    row=2, col=1
                )

                # FF
                fig.add_trace(
                    go.Scatter(x=sample_data['cycle_number'], y=sample_data['ff_percent'],
                              name=sample_id, showlegend=False, legendgroup=sample_id),
                    row=2, col=2
                )

            fig.update_xaxes(title_text="Cycle", row=2, col=1)
            fig.update_xaxes(title_text="Cycle", row=2, col=2)
            fig.update_layout(height=600)

            st.plotly_chart(fig, use_container_width=True)

    def _render_environmental_charts(self, df: pd.DataFrame):
        """Render environmental condition charts"""
        st.subheader("Environmental Conditions")

        env_df = df[(df['temperature_c'].notna()) | (df['rh_percent'].notna())].copy()

        if env_df.empty:
            st.info("No environmental data available.")
            return

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Temperature
        if env_df['temperature_c'].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=env_df['timestamp'],
                    y=env_df['temperature_c'],
                    name="Temperature",
                    line=dict(color='red'),
                    mode='lines'
                ),
                secondary_y=False
            )

        # Humidity
        if env_df['rh_percent'].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=env_df['timestamp'],
                    y=env_df['rh_percent'],
                    name="Relative Humidity",
                    line=dict(color='blue'),
                    mode='lines'
                ),
                secondary_y=True
            )

        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
        fig.update_yaxes(title_text="Relative Humidity (%)", secondary_y=True)
        fig.update_layout(height=400, hovermode='x unified')

        st.plotly_chart(fig, use_container_width=True)

    def render_analysis_panel(self, protocol: SpongeProtocol):
        """Render analysis and results panel"""
        st.header("🔬 Analysis & Results")

        df = protocol.get_measurements_df()

        if df.empty:
            st.info("No data available for analysis.")
            return

        sample_ids = df['sample_id'].unique()

        # Analyze each sample
        for sample_id in sample_ids:
            with st.expander(f"📊 {sample_id}", expanded=True):
                try:
                    analysis = protocol.analyze_sample(sample_id)

                    # Display results
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Pmax Degradation",
                            f"{analysis.pmax_degradation_percent:.2f}%",
                            delta=None,
                            delta_color="inverse"
                        )
                        st.metric(
                            "Moisture Absorption",
                            f"{analysis.moisture_absorption_percent:.3f}%"
                        )

                    with col2:
                        st.metric(
                            "Reversible Degradation",
                            f"{analysis.reversible_degradation_percent:.2f}%"
                        )
                        st.metric(
                            "Moisture Desorption",
                            f"{analysis.moisture_desorption_percent:.3f}%"
                        )

                    with col3:
                        st.metric(
                            "Irreversible Degradation",
                            f"{analysis.irreversible_degradation_percent:.2f}%"
                        )
                        st.metric(
                            "Sponge Coefficient",
                            f"{analysis.sponge_coefficient:.3f}"
                        )

                    # Pass/Fail status
                    status_color = {
                        'PASS': '🟢',
                        'WARNING': '🟡',
                        'FAIL': '🔴'
                    }.get(analysis.pass_fail, '⚪')

                    st.markdown(f"### Status: {status_color} {analysis.pass_fail}")

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

    def render_export_panel(self, protocol: SpongeProtocol):
        """Render data export panel"""
        st.header("💾 Export Data")

        col1, col2 = st.columns(2)

        with col1:
            export_format = st.selectbox(
                "Export Format",
                options=['CSV', 'JSON', 'Excel'],
                help="Select output format"
            )

        with col2:
            output_dir = st.text_input(
                "Output Directory",
                value="./data",
                help="Directory to save exported files"
            )

        if st.button("Export Data"):
            try:
                output_path = Path(output_dir)
                exported_files = protocol.export_data(
                    output_path,
                    formats=[export_format.lower()]
                )

                for fmt, file_path in exported_files.items():
                    st.success(f"✅ Exported {fmt.upper()} to: {file_path}")

            except Exception as e:
                st.error(f"Export failed: {str(e)}")

        # Generate report
        st.subheader("Generate Report")

        if st.button("Generate Test Report"):
            try:
                report = protocol.generate_report()

                st.success("✅ Report generated successfully!")

                # Display summary
                st.json({
                    'test_id': report['test_id'],
                    'protocol_version': report['protocol_version'],
                    'summary': report['summary']
                })

                # Download button
                report_json = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="Download Report (JSON)",
                    data=report_json,
                    file_name=f"sponge_001_report_{report['test_id'][:8]}.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="SPONGE-001 Testing",
        page_icon="🧽",
        layout="wide"
    )

    ui = SpongeUI()

    # Render header
    ui.render_header()

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        options=["Configuration", "Data Entry", "Monitoring", "Analysis", "Export"],
        index=0
    )

    # Page routing
    if page == "Configuration":
        ui.render_configuration_panel()

        if st.session_state.test_plan:
            ui.render_test_plan_summary(st.session_state.test_plan)

    elif page == "Data Entry":
        if st.session_state.protocol:
            sample_ids = st.session_state.test_plan['sample_ids']
            ui.render_data_entry_panel(st.session_state.protocol, sample_ids)
        else:
            st.warning("⚠️ Please create a test plan first in Configuration.")

    elif page == "Monitoring":
        if st.session_state.protocol:
            ui.render_monitoring_dashboard(st.session_state.protocol)
        else:
            st.warning("⚠️ Please create a test plan first in Configuration.")

    elif page == "Analysis":
        if st.session_state.protocol:
            ui.render_analysis_panel(st.session_state.protocol)
        else:
            st.warning("⚠️ Please create a test plan first in Configuration.")

    elif page == "Export":
        if st.session_state.protocol:
            ui.render_export_panel(st.session_state.protocol)
        else:
            st.warning("⚠️ Please create a test plan first in Configuration.")


if __name__ == "__main__":
    main()
