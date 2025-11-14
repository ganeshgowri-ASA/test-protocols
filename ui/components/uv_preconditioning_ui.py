"""
GenSpark UI Component for UV-001 Preconditioning Protocol

Streamlit-based interface with Plotly graphs for real-time monitoring,
cumulative UV dose tracking, temperature monitoring, and automated calculations.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from protocols.environmental.uv_preconditioning import (
    UVPreconditioningProtocol,
    TestSession,
    TestStatus,
    ComplianceStatus
)


class UVPreconditioningUI:
    """Streamlit UI for UV Preconditioning Protocol"""

    def __init__(self):
        """Initialize UI component"""
        self.protocol = UVPreconditioningProtocol()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'protocol_instance' not in st.session_state:
            st.session_state.protocol_instance = self.protocol

        if 'test_active' not in st.session_state:
            st.session_state.test_active = False

        if 'refresh_interval' not in st.session_state:
            st.session_state.refresh_interval = 5  # seconds

    def render(self):
        """Render the main UI"""
        st.set_page_config(
            page_title="UV-001 Preconditioning Protocol",
            page_icon="☀️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.title("☀️ UV-001: UV Preconditioning Protocol")
        st.markdown("**IEC 61215 MQT 10** - UV Exposure Testing for PV Modules")

        # Sidebar for controls
        self._render_sidebar()

        # Main content area
        if st.session_state.test_active and self.protocol.current_session:
            self._render_active_test()
        else:
            self._render_start_screen()

    def _render_sidebar(self):
        """Render sidebar with controls and protocol info"""
        with st.sidebar:
            st.header("Protocol Information")

            st.metric("Protocol ID", "UV-001")
            st.metric("Standard", "IEC 61215 MQT 10")
            st.metric("Category", "Environmental")

            st.divider()

            st.subheader("Test Parameters")
            st.info(f"""
            **Target UV Dose:** {self.protocol.TARGET_UV_DOSE} kWh/m²
            **Wavelength Range:** {self.protocol.WAVELENGTH_MIN}-{self.protocol.WAVELENGTH_MAX} nm
            **Irradiance:** {self.protocol.IRRADIANCE_MIN}-{self.protocol.IRRADIANCE_MAX} W/m²
            **Module Temperature:** {self.protocol.MODULE_TEMP_TARGET} ± {self.protocol.MODULE_TEMP_TOLERANCE}°C
            """)

            st.divider()

            if st.session_state.test_active:
                st.subheader("Test Controls")

                if st.button("⏸️ Pause Test", use_container_width=True):
                    st.warning("Test paused")

                if st.button("⏹️ Stop Test", type="primary", use_container_width=True):
                    self._stop_test()

                if st.button("🚨 Abort Test", use_container_width=True):
                    self._abort_test()

                st.divider()

                # Refresh interval control
                st.subheader("Display Settings")
                st.session_state.refresh_interval = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=1,
                    max_value=60,
                    value=st.session_state.refresh_interval
                )

    def _render_start_screen(self):
        """Render the test start screen"""
        st.header("Start New Test Session")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Test Configuration")

            session_id = st.text_input(
                "Session ID",
                value=f"UV001_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="Unique identifier for this test session"
            )

            sample_id = st.text_input(
                "Sample/Module ID",
                help="Identifier for the module under test"
            )

            operator = st.text_input(
                "Operator Name",
                help="Name of the test operator"
            )

            notes = st.text_area(
                "Test Notes",
                help="Additional notes or observations"
            )

        with col2:
            st.subheader("Protocol Overview")

            st.markdown("""
            ### Test Procedure
            1. **Pre-Test Characterization**
               - I-V curve measurement
               - Visual inspection
               - Initial documentation

            2. **UV Exposure**
               - Total dose: 15 kWh/m²
               - Duration: ~50-60 hours
               - Continuous monitoring

            3. **Post-Test Analysis**
               - I-V curve measurement
               - Degradation analysis
               - Visual inspection

            ### Acceptance Criteria
            - Power degradation ≤ 5%
            - No major visual defects
            - Insulation resistance ≥ 40 MΩ
            """)

        st.divider()

        if st.button("▶️ Start Test Session", type="primary", use_container_width=True):
            if not sample_id or not operator:
                st.error("Please provide Sample ID and Operator Name")
            else:
                self._start_test(session_id, sample_id, operator, notes)

    def _render_active_test(self):
        """Render active test monitoring interface"""
        session = self.protocol.current_session

        # Header with key metrics
        self._render_test_header(session)

        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Live Monitoring",
            "📈 Cumulative Dose",
            "🌡️ Environmental",
            "🌈 Spectral Analysis",
            "⚡ Electrical Data"
        ])

        with tab1:
            self._render_live_monitoring(session)

        with tab2:
            self._render_cumulative_dose(session)

        with tab3:
            self._render_environmental_monitoring(session)

        with tab4:
            self._render_spectral_analysis(session)

        with tab5:
            self._render_electrical_data(session)

    def _render_test_header(self, session: TestSession):
        """Render test header with key metrics"""
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Cumulative Dose",
                f"{session.cumulative_uv_dose:.2f} kWh/m²",
                f"{self.protocol.get_dose_completion_percentage():.1f}% complete"
            )

        with col2:
            st.metric(
                "Remaining Dose",
                f"{self.protocol.get_remaining_dose():.2f} kWh/m²"
            )

        with col3:
            st.metric(
                "Exposure Time",
                f"{session.total_exposure_time:.1f} hrs"
            )

        with col4:
            est_remaining = self.protocol.estimate_remaining_time()
            st.metric(
                "Est. Remaining Time",
                f"{est_remaining:.1f} hrs" if est_remaining else "N/A"
            )

        with col5:
            st.metric(
                "Avg Irradiance",
                f"{session.average_irradiance:.1f} W/m²"
            )

        # Progress bar
        progress = self.protocol.get_dose_completion_percentage() / 100
        st.progress(min(progress, 1.0))

        # Status indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Session ID:** {session.session_id}")
        with col2:
            st.info(f"**Sample ID:** {session.sample_id}")
        with col3:
            status_emoji = {"in_progress": "🟢", "paused": "🟡", "completed": "✅"}
            st.info(f"**Status:** {status_emoji.get(session.status.value, '⚪')} {session.status.value.upper()}")

    def _render_live_monitoring(self, session: TestSession):
        """Render live monitoring dashboard"""
        st.subheader("Real-Time Monitoring")

        if not session.irradiance_measurements:
            st.info("No measurement data available yet. Start logging measurements to see live data.")
            return

        # Create sample data button for demo
        if st.button("🎲 Add Sample Measurement (Demo)"):
            self._add_demo_measurement()
            st.rerun()

        # Multi-parameter chart
        fig = self._create_live_monitoring_chart(session)
        st.plotly_chart(fig, use_container_width=True)

        # Current values
        st.subheader("Current Values")
        col1, col2, col3, col4 = st.columns(4)

        if session.irradiance_measurements:
            latest_irr = session.irradiance_measurements[-1]

            with col1:
                compliance = self.protocol._check_irradiance_compliance(latest_irr.uv_irradiance)
                color = "green" if compliance == ComplianceStatus.COMPLIANT else "red"
                st.markdown(f"**UV Irradiance**  \n:{color}[{latest_irr.uv_irradiance:.1f} W/m²]")

        if session.environmental_measurements:
            latest_env = session.environmental_measurements[-1]

            with col2:
                st.markdown(f"**Module Temp**  \n{latest_env.module_temperature:.1f}°C")

            with col3:
                st.markdown(f"**Ambient Temp**  \n{latest_env.ambient_temperature:.1f}°C")

            with col4:
                st.markdown(f"**Humidity**  \n{latest_env.relative_humidity:.1f}%")

    def _render_cumulative_dose(self, session: TestSession):
        """Render cumulative UV dose tracking"""
        st.subheader("Cumulative UV Dose Tracking")

        if not session.irradiance_measurements:
            st.info("No dose data available yet.")
            return

        # Calculate cumulative dose over time
        timestamps = [m.timestamp for m in session.irradiance_measurements]
        cumulative_doses = []

        # Recalculate cumulative dose for plotting
        cumulative = 0.0
        for i, measurement in enumerate(session.irradiance_measurements):
            if i > 0:
                time_delta = (measurement.timestamp - session.irradiance_measurements[i-1].timestamp).total_seconds() / 3600
                avg_irr = (measurement.uv_irradiance + session.irradiance_measurements[i-1].uv_irradiance) / 2
                cumulative += (avg_irr * time_delta) / 1000
            cumulative_doses.append(cumulative)

        # Create dose chart
        fig = go.Figure()

        # Cumulative dose line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cumulative_doses,
            mode='lines',
            name='Cumulative Dose',
            line=dict(color='#2E86DE', width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 222, 0.2)'
        ))

        # Target dose line
        fig.add_hline(
            y=self.protocol.TARGET_UV_DOSE,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Target: {self.protocol.TARGET_UV_DOSE} kWh/m²",
            annotation_position="right"
        )

        # Tolerance bands
        fig.add_hrect(
            y0=self.protocol.TARGET_UV_DOSE * (1 - self.protocol.TARGET_UV_DOSE_TOLERANCE),
            y1=self.protocol.TARGET_UV_DOSE * (1 + self.protocol.TARGET_UV_DOSE_TOLERANCE),
            fillcolor="green",
            opacity=0.1,
            line_width=0,
            annotation_text="Acceptable Range",
            annotation_position="top left"
        )

        fig.update_layout(
            title="Cumulative UV Dose Over Time",
            xaxis_title="Time",
            yaxis_title="Cumulative Dose (kWh/m²)",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Dose statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Dose",
                f"{session.cumulative_uv_dose:.3f} kWh/m²",
                f"{self.protocol.get_dose_completion_percentage():.1f}%"
            )

        with col2:
            dose_rate = session.cumulative_uv_dose / session.total_exposure_time if session.total_exposure_time > 0 else 0
            st.metric(
                "Dose Rate",
                f"{dose_rate:.4f} kWh/m²/hr"
            )

        with col3:
            target_reached = self.protocol.check_dose_target_reached()
            st.metric(
                "Target Status",
                "✅ Reached" if target_reached else "⏳ In Progress"
            )

    def _render_environmental_monitoring(self, session: TestSession):
        """Render environmental conditions monitoring"""
        st.subheader("Environmental Conditions")

        if not session.environmental_measurements:
            st.info("No environmental data available yet.")
            return

        # Create environmental chart
        fig = self._create_environmental_chart(session)
        st.plotly_chart(fig, use_container_width=True)

        # Temperature distribution
        st.subheader("Temperature Distribution")

        temps = [m.module_temperature for m in session.environmental_measurements]

        col1, col2 = st.columns(2)

        with col1:
            # Temperature histogram
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=temps,
                nbinsx=30,
                name='Module Temperature',
                marker_color='#EE5A6F'
            ))

            # Add target range
            fig_hist.add_vline(
                x=self.protocol.MODULE_TEMP_TARGET,
                line_dash="dash",
                line_color="green",
                annotation_text="Target"
            )

            fig_hist.update_layout(
                title="Module Temperature Distribution",
                xaxis_title="Temperature (°C)",
                yaxis_title="Frequency",
                height=400
            )

            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            # Statistics
            st.markdown("### Temperature Statistics")

            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Target', 'Tolerance'],
                'Value': [
                    f"{np.mean(temps):.2f}°C",
                    f"{np.std(temps):.2f}°C",
                    f"{np.min(temps):.2f}°C",
                    f"{np.max(temps):.2f}°C",
                    f"{self.protocol.MODULE_TEMP_TARGET}°C",
                    f"± {self.protocol.MODULE_TEMP_TOLERANCE}°C"
                ]
            })

            st.dataframe(stats_df, use_container_width=True, hide_index=True)

            # Compliance check
            in_spec_count = sum(
                1 for t in temps
                if abs(t - self.protocol.MODULE_TEMP_TARGET) <= self.protocol.MODULE_TEMP_TOLERANCE
            )
            compliance_rate = (in_spec_count / len(temps)) * 100

            st.metric("Temperature Compliance", f"{compliance_rate:.1f}%")

    def _render_spectral_analysis(self, session: TestSession):
        """Render spectral irradiance analysis"""
        st.subheader("Spectral Irradiance Analysis")

        if not session.spectral_measurements:
            st.info("No spectral data available yet. Spectral measurements are typically taken every 60 minutes.")

            # Demo button
            if st.button("🎲 Add Sample Spectral Data (Demo)"):
                self._add_demo_spectral_measurement()
                st.rerun()

            return

        # Latest spectral measurement
        latest = session.spectral_measurements[-1]

        col1, col2 = st.columns([2, 1])

        with col1:
            # Spectral distribution chart
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=latest.wavelengths,
                y=latest.irradiance_values,
                mode='lines',
                name='Spectral Irradiance',
                line=dict(color='#6C5CE7', width=2),
                fill='tozeroy',
                fillcolor='rgba(108, 92, 231, 0.3)'
            ))

            # Mark UVB and UVA regions
            fig.add_vrect(
                x0=280, x1=320,
                fillcolor="blue",
                opacity=0.1,
                annotation_text="UVB",
                annotation_position="top left"
            )

            fig.add_vrect(
                x0=320, x1=400,
                fillcolor="purple",
                opacity=0.1,
                annotation_text="UVA",
                annotation_position="top right"
            )

            # Mark peak wavelength
            fig.add_vline(
                x=latest.peak_wavelength,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Peak: {latest.peak_wavelength:.1f} nm"
            )

            fig.update_layout(
                title=f"Spectral Irradiance Distribution - {latest.timestamp.strftime('%Y-%m-%d %H:%M')}",
                xaxis_title="Wavelength (nm)",
                yaxis_title="Irradiance (W/m²/nm)",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Spectral Metrics")

            st.metric("Peak Wavelength", f"{latest.peak_wavelength:.1f} nm")
            st.metric("Total UV Irradiance", f"{latest.total_uv_irradiance:.1f} W/m²")

            st.divider()

            st.markdown("### Distribution")

            # UVA/UVB pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['UVA (320-400 nm)', 'UVB (280-320 nm)'],
                values=[latest.uv_a_percentage, latest.uv_b_percentage],
                hole=0.3,
                marker_colors=['#A29BFE', '#6C5CE7']
            )])

            fig_pie.update_layout(height=250, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

            # Compliance indicators
            st.divider()
            st.markdown("### Compliance")

            uvb_compliant = self.protocol.UVB_PERCENTAGE_MIN <= latest.uv_b_percentage <= self.protocol.UVB_PERCENTAGE_MAX
            uva_compliant = self.protocol.UVA_PERCENTAGE_MIN <= latest.uv_a_percentage <= self.protocol.UVA_PERCENTAGE_MAX

            st.markdown(f"**UVA:** {'✅' if uva_compliant else '❌'} {latest.uv_a_percentage:.1f}%")
            st.markdown(f"**UVB:** {'✅' if uvb_compliant else '❌'} {latest.uv_b_percentage:.1f}%")

        # Historical spectral trends
        if len(session.spectral_measurements) > 1:
            st.subheader("Spectral Trends")

            times = [m.timestamp for m in session.spectral_measurements]
            peaks = [m.peak_wavelength for m in session.spectral_measurements]
            uva = [m.uv_a_percentage for m in session.spectral_measurements]
            uvb = [m.uv_b_percentage for m in session.spectral_measurements]

            fig_trends = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Peak Wavelength Over Time", "UVA/UVB Distribution Over Time"),
                vertical_spacing=0.15
            )

            fig_trends.add_trace(
                go.Scatter(x=times, y=peaks, mode='lines+markers', name='Peak Wavelength'),
                row=1, col=1
            )

            fig_trends.add_trace(
                go.Scatter(x=times, y=uva, mode='lines+markers', name='UVA %'),
                row=2, col=1
            )

            fig_trends.add_trace(
                go.Scatter(x=times, y=uvb, mode='lines+markers', name='UVB %'),
                row=2, col=1
            )

            fig_trends.update_xaxes(title_text="Time", row=2, col=1)
            fig_trends.update_yaxes(title_text="Wavelength (nm)", row=1, col=1)
            fig_trends.update_yaxes(title_text="Percentage (%)", row=2, col=1)

            fig_trends.update_layout(height=600, showlegend=True)

            st.plotly_chart(fig_trends, use_container_width=True)

    def _render_electrical_data(self, session: TestSession):
        """Render electrical characterization data"""
        st.subheader("Electrical Characterization")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Pre-Test Characterization")
            if session.pre_test_electrical:
                self._display_electrical_params(session.pre_test_electrical)
            else:
                st.info("Pre-test electrical data not available.")

                if st.button("📊 Add Pre-Test Data (Demo)"):
                    self._add_demo_electrical_data(is_pre_test=True)
                    st.rerun()

        with col2:
            st.markdown("### Post-Test Characterization")
            if session.post_test_electrical:
                self._display_electrical_params(session.post_test_electrical)
            else:
                st.info("Post-test electrical data not available.")

                if session.pre_test_electrical and st.button("📊 Add Post-Test Data (Demo)"):
                    self._add_demo_electrical_data(is_pre_test=False)
                    st.rerun()

        # Degradation analysis
        if session.pre_test_electrical and session.post_test_electrical:
            st.divider()
            self._render_degradation_analysis(session)

    def _display_electrical_params(self, params):
        """Display electrical parameters"""
        st.markdown(f"**Timestamp:** {params.timestamp.strftime('%Y-%m-%d %H:%M')}")

        metrics_col1, metrics_col2 = st.columns(2)

        with metrics_col1:
            st.metric("Voc", f"{params.open_circuit_voltage:.2f} V")
            st.metric("Isc", f"{params.short_circuit_current:.2f} A")

        with metrics_col2:
            st.metric("Pmax", f"{params.maximum_power:.2f} W")
            st.metric("FF", f"{params.fill_factor:.3f}")

        if params.efficiency:
            st.metric("Efficiency", f"{params.efficiency:.2f}%")

    def _render_degradation_analysis(self, session: TestSession):
        """Render degradation analysis"""
        st.subheader("Degradation Analysis")

        pre = session.pre_test_electrical
        post = session.post_test_electrical

        # Calculate changes
        power_deg = self.protocol.calculate_power_degradation()
        voc_change = ((post.open_circuit_voltage - pre.open_circuit_voltage) / pre.open_circuit_voltage) * 100
        isc_change = ((post.short_circuit_current - pre.short_circuit_current) / pre.short_circuit_current) * 100
        ff_change = ((post.fill_factor - pre.fill_factor) / pre.fill_factor) * 100

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Power Degradation",
                f"{power_deg:.2f}%",
                delta=f"{power_deg:.2f}%",
                delta_color="inverse"
            )

        with col2:
            st.metric(
                "Voc Change",
                f"{voc_change:+.2f}%",
                delta=f"{voc_change:.2f}%",
                delta_color="normal"
            )

        with col3:
            st.metric(
                "Isc Change",
                f"{isc_change:+.2f}%",
                delta=f"{isc_change:.2f}%",
                delta_color="normal"
            )

        with col4:
            st.metric(
                "FF Change",
                f"{ff_change:+.2f}%",
                delta=f"{ff_change:.2f}%",
                delta_color="normal"
            )

        # Pass/Fail assessment
        st.divider()
        acceptance = self.protocol.check_acceptance_criteria()

        if acceptance['overall_pass']:
            st.success("✅ **PASS** - Module meets acceptance criteria")
        else:
            st.error("❌ **FAIL** - Module does not meet acceptance criteria")

        # Detailed criteria
        st.markdown("### Acceptance Criteria Details")

        criteria_df = pd.DataFrame([
            {
                'Parameter': 'Power Degradation',
                'Value': f"{power_deg:.2f}%",
                'Limit': f"≤ {self.protocol.MAX_POWER_DEGRADATION}%",
                'Status': '✅ Pass' if power_deg <= self.protocol.MAX_POWER_DEGRADATION else '❌ Fail'
            },
            {
                'Parameter': 'UV Dose',
                'Value': f"{session.cumulative_uv_dose:.2f} kWh/m²",
                'Limit': f"{self.protocol.TARGET_UV_DOSE} ± {self.protocol.TARGET_UV_DOSE_TOLERANCE*100}%",
                'Status': '✅ Pass' if self.protocol.check_dose_target_reached() else '❌ Fail'
            }
        ])

        st.dataframe(criteria_df, use_container_width=True, hide_index=True)

    def _create_live_monitoring_chart(self, session: TestSession) -> go.Figure:
        """Create multi-parameter live monitoring chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("UV Irradiance", "Temperature"),
            vertical_spacing=0.15,
            specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
        )

        # UV Irradiance
        if session.irradiance_measurements:
            times = [m.timestamp for m in session.irradiance_measurements]
            irradiances = [m.uv_irradiance for m in session.irradiance_measurements]

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=irradiances,
                    mode='lines',
                    name='UV Irradiance',
                    line=dict(color='#F39C12', width=2)
                ),
                row=1, col=1
            )

            # Target range
            fig.add_hrect(
                y0=self.protocol.IRRADIANCE_MIN,
                y1=self.protocol.IRRADIANCE_MAX,
                fillcolor="green",
                opacity=0.1,
                line_width=0,
                row=1, col=1
            )

        # Temperatures
        if session.environmental_measurements:
            times = [m.timestamp for m in session.environmental_measurements]
            module_temps = [m.module_temperature for m in session.environmental_measurements]
            ambient_temps = [m.ambient_temperature for m in session.environmental_measurements]

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=module_temps,
                    mode='lines',
                    name='Module Temp',
                    line=dict(color='#E74C3C', width=2)
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=ambient_temps,
                    mode='lines',
                    name='Ambient Temp',
                    line=dict(color='#3498DB', width=2)
                ),
                row=2, col=1, secondary_y=True
            )

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Irradiance (W/m²)", row=1, col=1)
        fig.update_yaxes(title_text="Module Temp (°C)", row=2, col=1)
        fig.update_yaxes(title_text="Ambient Temp (°C)", row=2, col=1, secondary_y=True)

        fig.update_layout(height=700, hovermode='x unified')

        return fig

    def _create_environmental_chart(self, session: TestSession) -> go.Figure:
        """Create environmental conditions chart"""
        times = [m.timestamp for m in session.environmental_measurements]
        module_temps = [m.module_temperature for m in session.environmental_measurements]
        ambient_temps = [m.ambient_temperature for m in session.environmental_measurements]
        humidity = [m.relative_humidity for m in session.environmental_measurements]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Temperature Profile", "Relative Humidity"),
            vertical_spacing=0.12
        )

        # Temperatures
        fig.add_trace(
            go.Scatter(x=times, y=module_temps, mode='lines', name='Module Temp',
                      line=dict(color='#E74C3C', width=2)),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=times, y=ambient_temps, mode='lines', name='Ambient Temp',
                      line=dict(color='#3498DB', width=2)),
            row=1, col=1
        )

        # Humidity
        fig.add_trace(
            go.Scatter(x=times, y=humidity, mode='lines', name='Humidity',
                      line=dict(color='#16A085', width=2),
                      fill='tozeroy', fillcolor='rgba(22, 160, 133, 0.2)'),
            row=2, col=1
        )

        # Add humidity limit
        fig.add_hline(
            y=self.protocol.HUMIDITY_MAX,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Max: {self.protocol.HUMIDITY_MAX}%",
            row=2, col=1
        )

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=2, col=1)

        fig.update_layout(height=600, hovermode='x unified')

        return fig

    def _start_test(self, session_id: str, sample_id: str, operator: str, notes: str):
        """Start test session"""
        self.protocol.start_test_session(session_id, sample_id, operator, notes)
        st.session_state.test_active = True
        st.session_state.protocol_instance = self.protocol
        st.success(f"Test session {session_id} started!")
        st.rerun()

    def _stop_test(self):
        """Stop test session"""
        if self.protocol.current_session:
            self.protocol.complete_test_session()
            st.session_state.test_active = False
            st.success("Test session completed!")
            st.rerun()

    def _abort_test(self):
        """Abort test session"""
        if self.protocol.current_session:
            self.protocol.abort_test_session("User aborted test")
            st.session_state.test_active = False
            st.warning("Test session aborted!")
            st.rerun()

    def _add_demo_measurement(self):
        """Add demo measurement data"""
        if not self.protocol.current_session:
            return

        # Simulate realistic UV exposure data
        base_irradiance = 300 + np.random.normal(0, 10)
        self.protocol.add_irradiance_measurement(
            uv_irradiance=max(250, min(400, base_irradiance)),
            sensor_temperature=35 + np.random.normal(0, 2)
        )

        self.protocol.add_environmental_measurement(
            module_temperature=60 + np.random.normal(0, 3),
            ambient_temperature=25 + np.random.normal(0, 2),
            relative_humidity=50 + np.random.normal(0, 5),
            air_velocity=1.0 + np.random.normal(0, 0.2)
        )

    def _add_demo_spectral_measurement(self):
        """Add demo spectral measurement"""
        if not self.protocol.current_session:
            return

        # Generate realistic spectral data
        wavelengths = list(range(280, 401, 5))
        peak = 340 + np.random.normal(0, 10)

        irradiances = [
            max(0, 100 * np.exp(-((w - peak) ** 2) / (2 * 30 ** 2)) + np.random.normal(0, 5))
            for w in wavelengths
        ]

        self.protocol.add_spectral_measurement(wavelengths, irradiances)

    def _add_demo_electrical_data(self, is_pre_test: bool):
        """Add demo electrical characterization data"""
        if not self.protocol.current_session:
            return

        if is_pre_test:
            voc, isc, pmax, ff = 45.2, 9.8, 350.0, 0.79
        else:
            # Simulate degradation
            degradation = np.random.uniform(1, 4)  # 1-4% degradation
            voc, isc = 45.0, 9.75
            pmax = 350.0 * (1 - degradation / 100)
            ff = 0.78

        self.protocol.add_electrical_characterization(
            voc=voc,
            isc=isc,
            pmax=pmax,
            ff=ff,
            efficiency=18.5 if is_pre_test else 17.8,
            is_pre_test=is_pre_test
        )


def main():
    """Main entry point for Streamlit app"""
    ui = UVPreconditioningUI()
    ui.render()


if __name__ == "__main__":
    main()
