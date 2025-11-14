"""
GenSpark UI Component for SAND-001 Real-Time Monitoring
Streamlit-based dashboard for Sand/Dust Resistance Test monitoring
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'src' / 'python'))

try:
    from protocols.sand_dust_test import (
        SandDustResistanceTest, TestPhase, SeverityLevel,
        SpecimenData, TestConfiguration
    )
except ImportError:
    st.error("Unable to import test protocols. Please check your installation.")


class SandDustMonitorUI:
    """Real-time monitoring UI for Sand/Dust Resistance Test"""

    def __init__(self):
        """Initialize the monitoring UI"""
        self.setup_page_config()
        self.initialize_session_state()

    @staticmethod
    def setup_page_config():
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="SAND-001 Real-Time Monitor",
            page_icon="🏜️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        if 'test_active' not in st.session_state:
            st.session_state.test_active = False
        if 'test_instance' not in st.session_state:
            st.session_state.test_instance = None
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None
        if 'alert_history' not in st.session_state:
            st.session_state.alert_history = []

    def render_header(self):
        """Render page header"""
        col1, col2, col3 = st.columns([2, 3, 1])

        with col1:
            st.title("🏜️ SAND-001 Monitor")
            st.caption("Sand/Dust Resistance Test - IEC 60068-2-68")

        with col2:
            if st.session_state.test_active:
                duration = datetime.now() - st.session_state.start_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                st.metric("Test Duration", f"{hours}h {minutes}m")

        with col3:
            if st.session_state.test_active:
                st.success("🟢 ACTIVE")
            else:
                st.info("⚪ IDLE")

    def render_sidebar(self):
        """Render sidebar with test controls"""
        with st.sidebar:
            st.header("Test Control")

            # Test identification
            st.subheader("Test ID")
            test_id = st.text_input("Session ID", value=f"SAND-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

            # Test configuration
            st.subheader("Configuration")

            with st.expander("Dust Parameters", expanded=False):
                dust_type = st.selectbox(
                    "Dust Type",
                    ["Arizona Test Dust", "ISO 12103-1 A2", "ISO 12103-1 A3", "ISO 12103-1 A4", "Quartz sand"]
                )
                dust_concentration = st.number_input(
                    "Dust Concentration (kg/m³)",
                    min_value=0.001, max_value=0.1, value=0.01, step=0.001, format="%.3f"
                )

            with st.expander("Environmental Conditions", expanded=False):
                target_temp = st.number_input("Temperature (°C)", min_value=-10.0, max_value=85.0, value=25.0)
                target_humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=95.0, value=50.0)
                air_velocity = st.number_input("Air Velocity (m/s)", min_value=0.5, max_value=15.0, value=2.0)

            with st.expander("Test Duration", expanded=False):
                exposure_time = st.number_input("Exposure Time (hours)", min_value=1.0, max_value=48.0, value=8.0)
                cycles = st.number_input("Cycles", min_value=1, max_value=10, value=1)
                settling_time = st.number_input("Settling Time (hours)", min_value=0.5, max_value=4.0, value=1.0)

            # Specimen information
            st.subheader("Specimen")
            with st.expander("Specimen Details", expanded=False):
                specimen_id = st.text_input("Specimen ID", value="SPEC-001")
                specimen_type = st.selectbox("Type", ["PV Module", "Junction Box", "Connector", "Frame", "Enclosure"])
                manufacturer = st.text_input("Manufacturer", value="")
                model = st.text_input("Model", value="")

            # Control buttons
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                if not st.session_state.test_active:
                    if st.button("▶️ Start Test", use_container_width=True, type="primary"):
                        self.start_test(test_id, {
                            'dust_type': dust_type,
                            'dust_concentration': dust_concentration,
                            'target_temperature': target_temp,
                            'target_humidity': target_humidity,
                            'target_air_velocity': air_velocity,
                            'exposure_time_hours': exposure_time,
                            'cycles': cycles,
                            'settling_time_hours': settling_time
                        }, {
                            'specimen_id': specimen_id,
                            'specimen_type': specimen_type,
                            'manufacturer': manufacturer,
                            'model': model
                        })
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        st.warning("Test paused")

            with col2:
                if st.session_state.test_active:
                    if st.button("⏹️ Stop Test", use_container_width=True, type="secondary"):
                        self.stop_test()

            # Export options
            if st.session_state.test_active or st.session_state.test_instance:
                st.divider()
                st.subheader("Export")
                if st.button("📊 Export Data", use_container_width=True):
                    st.info("Export functionality - connect to database export")
                if st.button("📄 Generate Report", use_container_width=True):
                    st.info("Report generation - integrate with reporting system")

    def start_test(self, test_id: str, config: Dict, specimen_info: Dict):
        """Start a new test"""
        # Create test configuration
        test_config = TestConfiguration(
            dust_type=config['dust_type'],
            particle_size_range=(0.1, 200, 50),
            dust_concentration=config['dust_concentration'],
            target_temperature=config['target_temperature'],
            target_humidity=config['target_humidity'],
            target_air_velocity=config['target_air_velocity'],
            exposure_time_hours=config['exposure_time_hours'],
            cycles=config['cycles'],
            settling_time_hours=config['settling_time_hours']
        )

        # Create specimen data
        specimen = SpecimenData(
            specimen_id=specimen_info['specimen_id'],
            specimen_type=specimen_info['specimen_type'],
            manufacturer=specimen_info['manufacturer'],
            model=specimen_info['model'],
            serial_number="",
            initial_weight=0.0,
            initial_dimensions=(0.0, 0.0, 0.0),
            initial_surface_roughness=0.0
        )

        # Create test instance
        test = SandDustResistanceTest(test_id, test_config, specimen)
        test.start_test()

        # Update session state
        st.session_state.test_instance = test
        st.session_state.test_active = True
        st.session_state.start_time = datetime.now()
        st.session_state.alert_history = []

        st.success(f"Test {test_id} started successfully!")
        st.rerun()

    def stop_test(self):
        """Stop the current test"""
        if st.session_state.test_instance:
            st.session_state.test_instance.complete_test()

        st.session_state.test_active = False
        st.info("Test stopped")
        st.rerun()

    def render_phase_indicator(self):
        """Render current test phase indicator"""
        if not st.session_state.test_instance:
            return

        test = st.session_state.test_instance
        phases = [
            ("Pre-Conditioning", TestPhase.PRE_CONDITIONING),
            ("Chamber Prep", TestPhase.CHAMBER_PREP),
            ("Stabilization", TestPhase.STABILIZATION),
            ("Dust Exposure", TestPhase.DUST_EXPOSURE),
            ("Settling", TestPhase.SETTLING),
            ("Post-Assessment", TestPhase.POST_ASSESSMENT),
        ]

        st.subheader("Test Phase")

        # Create phase progress bar
        cols = st.columns(len(phases))
        current_phase_idx = next((i for i, (_, p) in enumerate(phases) if p == test.phase), 0)

        for idx, (col, (name, phase)) in enumerate(zip(cols, phases)):
            with col:
                if idx < current_phase_idx:
                    st.success(f"✅ {name}")
                elif idx == current_phase_idx:
                    st.info(f"▶️ {name}")
                else:
                    st.text(f"⏳ {name}")

    def render_environmental_monitoring(self):
        """Render environmental monitoring section"""
        st.subheader("Environmental Conditions")

        if not st.session_state.test_instance:
            st.info("No active test. Start a test to see real-time monitoring.")
            return

        test = st.session_state.test_instance

        # Simulate real-time data (in production, this would come from sensors)
        current_data = self.get_simulated_environmental_data(test)

        # Display current values
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            temp_delta = current_data['temperature'] - test.config.target_temperature
            st.metric(
                "Temperature",
                f"{current_data['temperature']:.1f} °C",
                f"{temp_delta:+.1f} °C",
                delta_color="inverse" if abs(temp_delta) > 3 else "off"
            )

        with col2:
            humidity_delta = current_data['humidity'] - test.config.target_humidity
            st.metric(
                "Humidity",
                f"{current_data['humidity']:.1f} %",
                f"{humidity_delta:+.1f} %",
                delta_color="inverse" if abs(humidity_delta) > 5 else "off"
            )

        with col3:
            velocity_delta = current_data['air_velocity'] - test.config.target_air_velocity
            st.metric(
                "Air Velocity",
                f"{current_data['air_velocity']:.2f} m/s",
                f"{velocity_delta:+.2f} m/s",
                delta_color="inverse" if abs(velocity_delta) > 0.5 else "off"
            )

        with col4:
            conc_delta = current_data['dust_concentration'] - test.config.dust_concentration
            st.metric(
                "Dust Concentration",
                f"{current_data['dust_concentration']:.4f} kg/m³",
                f"{conc_delta:+.4f}",
                delta_color="inverse" if abs(conc_delta) > 0.002 else "off"
            )

        # Environmental trends chart
        st.subheader("Environmental Trends")
        self.render_environmental_chart(test)

    def render_environmental_chart(self, test: SandDustResistanceTest):
        """Render environmental data chart"""
        # Generate historical data (simulated)
        historical_data = self.generate_historical_environmental_data(test)

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Temperature", "Humidity", "Air Velocity", "Dust Concentration"),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # Temperature
        fig.add_trace(
            go.Scatter(x=historical_data['timestamp'], y=historical_data['temperature'],
                      mode='lines', name='Temperature', line=dict(color='#FF6B6B', width=2)),
            row=1, col=1
        )
        fig.add_hline(y=test.config.target_temperature, line_dash="dash", line_color="gray",
                     row=1, col=1, annotation_text="Target")

        # Humidity
        fig.add_trace(
            go.Scatter(x=historical_data['timestamp'], y=historical_data['humidity'],
                      mode='lines', name='Humidity', line=dict(color='#4ECDC4', width=2)),
            row=1, col=2
        )
        fig.add_hline(y=test.config.target_humidity, line_dash="dash", line_color="gray",
                     row=1, col=2, annotation_text="Target")

        # Air Velocity
        fig.add_trace(
            go.Scatter(x=historical_data['timestamp'], y=historical_data['air_velocity'],
                      mode='lines', name='Air Velocity', line=dict(color='#95E1D3', width=2)),
            row=2, col=1
        )
        fig.add_hline(y=test.config.target_air_velocity, line_dash="dash", line_color="gray",
                     row=2, col=1, annotation_text="Target")

        # Dust Concentration
        fig.add_trace(
            go.Scatter(x=historical_data['timestamp'], y=historical_data['dust_concentration'],
                      mode='lines', name='Dust Conc.', line=dict(color='#F38181', width=2)),
            row=2, col=2
        )
        fig.add_hline(y=test.config.dust_concentration, line_dash="dash", line_color="gray",
                     row=2, col=2, annotation_text="Target")

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=2)
        fig.update_yaxes(title_text="°C", row=1, col=1)
        fig.update_yaxes(title_text="%", row=1, col=2)
        fig.update_yaxes(title_text="m/s", row=2, col=1)
        fig.update_yaxes(title_text="kg/m³", row=2, col=2)

        fig.update_layout(height=500, showlegend=False, margin=dict(t=50, b=20))

        st.plotly_chart(fig, use_container_width=True)

    def render_particle_tracking(self):
        """Render particle tracking visualization"""
        st.subheader("Particle Tracking & Distribution")

        if not st.session_state.test_instance:
            st.info("No active test. Start a test to see particle tracking.")
            return

        test = st.session_state.test_instance

        col1, col2 = st.columns(2)

        with col1:
            # 3D particle distribution
            st.write("**Spatial Distribution**")
            particle_data = self.generate_particle_distribution_data()
            fig = go.Figure(data=[go.Scatter3d(
                x=particle_data['x'],
                y=particle_data['y'],
                z=particle_data['z'],
                mode='markers',
                marker=dict(
                    size=particle_data['concentration'] * 1000,
                    color=particle_data['concentration'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Concentration<br>kg/m³"),
                    opacity=0.7
                ),
                text=[f"Point {i+1}<br>Conc: {c:.4f} kg/m³"
                      for i, c in enumerate(particle_data['concentration'])],
                hoverinfo='text'
            )])

            fig.update_layout(
                scene=dict(
                    xaxis_title='X (mm)',
                    yaxis_title='Y (mm)',
                    zaxis_title='Z (mm)',
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
                ),
                height=400,
                margin=dict(l=0, r=0, t=0, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Particle size distribution
            st.write("**Size Distribution**")
            size_dist_data = self.generate_particle_size_distribution()

            fig = go.Figure(data=[
                go.Bar(
                    x=size_dist_data['size_range'],
                    y=size_dist_data['count'],
                    marker_color='indianred',
                    text=size_dist_data['count'],
                    textposition='auto'
                )
            ])

            fig.update_layout(
                xaxis_title="Particle Size Range (μm)",
                yaxis_title="Count",
                height=400,
                margin=dict(t=20)
            )

            st.plotly_chart(fig, use_container_width=True)

        # Uniformity metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            uniformity = 0.85  # Simulated
            st.metric("Spatial Uniformity", f"{uniformity:.2%}", "Good" if uniformity > 0.7 else "Poor")

        with col2:
            deposition_rate = 2.5  # Simulated g/m²/h
            st.metric("Deposition Rate", f"{deposition_rate:.2f} g/m²/h")

        with col3:
            particle_count = 15234  # Simulated
            st.metric("Total Particle Count", f"{particle_count:,}")

    def render_alerts_and_deviations(self):
        """Render alerts and deviations section"""
        st.subheader("Alerts & Deviations")

        if not st.session_state.test_instance:
            st.info("No alerts")
            return

        # Display recent alerts
        if st.session_state.alert_history:
            for alert in st.session_state.alert_history[-5:]:  # Show last 5
                if alert['severity'] == 'critical':
                    st.error(f"🔴 {alert['timestamp']}: {alert['message']}")
                elif alert['severity'] == 'warning':
                    st.warning(f"🟡 {alert['timestamp']}: {alert['message']}")
                else:
                    st.info(f"🔵 {alert['timestamp']}: {alert['message']}")
        else:
            st.success("✅ No alerts - all parameters within tolerance")

        # Deviation log
        with st.expander("Deviation Log", expanded=False):
            test = st.session_state.test_instance
            if test.deviations:
                for dev in test.deviations:
                    st.text(f"• {dev}")
            else:
                st.text("No deviations recorded")

    def render_test_progress(self):
        """Render test progress and timeline"""
        if not st.session_state.test_instance:
            return

        test = st.session_state.test_instance

        st.subheader("Test Progress")

        # Calculate progress
        if test.phase == TestPhase.DUST_EXPOSURE:
            elapsed = (datetime.now() - st.session_state.start_time).total_seconds() / 3600
            target_duration = test.config.exposure_time_hours
            progress = min(elapsed / target_duration, 1.0)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(progress)
            with col2:
                remaining = max(0, target_duration - elapsed)
                st.metric("Time Remaining", f"{remaining:.1f}h")

            # Timeline
            st.write("**Test Timeline**")
            timeline_data = pd.DataFrame({
                'Phase': ['Pre-Conditioning', 'Chamber Prep', 'Stabilization', 'Dust Exposure', 'Settling', 'Post-Assessment'],
                'Duration (h)': [2, 0.5, 1, test.config.exposure_time_hours, test.config.settling_time_hours, 2],
                'Status': ['✅', '✅', '✅', '▶️', '⏳', '⏳']
            })
            st.dataframe(timeline_data, use_container_width=True, hide_index=True)

    def get_simulated_environmental_data(self, test: SandDustResistanceTest) -> Dict:
        """Generate simulated current environmental data"""
        # Add small random variations to targets
        return {
            'temperature': test.config.target_temperature + np.random.normal(0, 1),
            'humidity': test.config.target_humidity + np.random.normal(0, 2),
            'air_velocity': test.config.target_air_velocity + np.random.normal(0, 0.1),
            'dust_concentration': test.config.dust_concentration + np.random.normal(0, 0.0005),
            'pressure': 101.325
        }

    def generate_historical_environmental_data(self, test: SandDustResistanceTest) -> pd.DataFrame:
        """Generate simulated historical environmental data"""
        if not st.session_state.start_time:
            return pd.DataFrame()

        duration = (datetime.now() - st.session_state.start_time).total_seconds()
        num_points = min(int(duration / 60), 100)  # One point per minute, max 100 points

        if num_points < 2:
            num_points = 2

        timestamps = [st.session_state.start_time + timedelta(seconds=i * duration / num_points)
                     for i in range(num_points)]

        data = pd.DataFrame({
            'timestamp': timestamps,
            'temperature': test.config.target_temperature + np.random.normal(0, 1, num_points),
            'humidity': test.config.target_humidity + np.random.normal(0, 2, num_points),
            'air_velocity': test.config.target_air_velocity + np.random.normal(0, 0.1, num_points),
            'dust_concentration': test.config.dust_concentration + np.random.normal(0, 0.0005, num_points)
        })

        return data

    def generate_particle_distribution_data(self) -> Dict:
        """Generate simulated particle distribution data"""
        num_points = 12
        return {
            'x': np.random.uniform(0, 1000, num_points),
            'y': np.random.uniform(0, 600, num_points),
            'z': np.random.uniform(0, 400, num_points),
            'concentration': np.random.uniform(0.005, 0.015, num_points)
        }

    def generate_particle_size_distribution(self) -> Dict:
        """Generate simulated particle size distribution"""
        return {
            'size_range': ['0-5', '5-10', '10-25', '25-50', '50-100', '100-200', '>200'],
            'count': [850, 1200, 2100, 3400, 4200, 2100, 1384]
        }

    def run(self):
        """Main run method"""
        self.render_header()
        self.render_sidebar()

        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Real-Time Monitoring",
            "🔬 Particle Tracking",
            "⚠️ Alerts & Deviations",
            "📈 Test Progress"
        ])

        with tab1:
            self.render_phase_indicator()
            st.divider()
            self.render_environmental_monitoring()

        with tab2:
            self.render_particle_tracking()

        with tab3:
            self.render_alerts_and_deviations()

        with tab4:
            self.render_test_progress()

        # Auto-refresh for real-time updates
        if st.session_state.test_active:
            st.markdown(
                """
                <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 5000);  // Refresh every 5 seconds
                </script>
                """,
                unsafe_allow_html=True
            )


def main():
    """Main entry point"""
    ui = SandDustMonitorUI()
    ui.run()


if __name__ == "__main__":
    main()
