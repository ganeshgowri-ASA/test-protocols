"""
GenSpark UI for Tropical Climate Test (TROP-001)
Interactive Streamlit interface for test execution and monitoring
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.protocol_loader import ProtocolLoader
from core.test_engine import TestEngine, TestStatus
from core.models import Module, ModuleType, ElectricalMeasurement, TestPhase
from analysis.data_analyzer import DataAnalyzer
from analysis.chart_generator import ChartGenerator


class TropicalClimateUI:
    """Streamlit UI for TROP-001 Tropical Climate Test"""

    def __init__(self):
        """Initialize the UI"""
        st.set_page_config(
            page_title="TROP-001 Tropical Climate Test",
            page_icon="🌡️",
            layout="wide"
        )

        # Initialize session state
        if 'test_engine' not in st.session_state:
            st.session_state.test_engine = None
        if 'protocol' not in st.session_state:
            st.session_state.protocol = None
        if 'test_started' not in st.session_state:
            st.session_state.test_started = False

    def run(self):
        """Run the Streamlit app"""
        st.title("🌡️ TROP-001 - Tropical Climate Test")
        st.markdown("---")

        # Load protocol
        self._load_protocol()

        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Test Setup",
            "▶️ Test Execution",
            "📊 Monitoring",
            "📈 Analysis",
            "📄 Report"
        ])

        with tab1:
            self._render_test_setup()

        with tab2:
            self._render_test_execution()

        with tab3:
            self._render_monitoring()

        with tab4:
            self._render_analysis()

        with tab5:
            self._render_report()

    def _load_protocol(self):
        """Load the TROP-001 protocol"""
        if st.session_state.protocol is None:
            try:
                loader = ProtocolLoader()
                st.session_state.protocol = loader.load_protocol("TROP-001")
            except Exception as e:
                st.error(f"Error loading protocol: {e}")
                st.stop()

    def _render_test_setup(self):
        """Render test setup tab"""
        st.header("Test Setup")

        protocol = st.session_state.protocol

        # Display protocol information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Protocol ID", protocol['protocol_id'])
            st.metric("Version", protocol['version'])

        with col2:
            st.metric("Category", protocol['category'])
            st.metric("Standard", protocol.get('standard', 'N/A'))

        with col3:
            total_duration = protocol['test_sequence']['total_test_duration']
            duration_unit = protocol['test_sequence']['total_test_duration_unit']
            st.metric("Test Duration", f"{total_duration} {duration_unit}")
            st.metric("Total Cycles", protocol['test_sequence']['total_cycles'])

        st.markdown("---")

        # Test information form
        st.subheader("Test Information")

        test_id = st.text_input("Test ID", value=f"TROP-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        operator = st.text_input("Operator Name")

        # Module information
        st.subheader("Module Information")

        num_modules = st.number_input(
            "Number of Modules",
            min_value=protocol['test_requirements']['sample_size']['minimum'],
            max_value=10,
            value=protocol['test_requirements']['sample_size']['recommended']
        )

        modules = []
        for i in range(int(num_modules)):
            with st.expander(f"Module {i+1}"):
                col1, col2 = st.columns(2)

                with col1:
                    serial = st.text_input(f"Serial Number", key=f"serial_{i}")
                    manufacturer = st.text_input(f"Manufacturer", key=f"mfr_{i}")
                    model = st.text_input(f"Model", key=f"model_{i}")

                with col2:
                    module_type = st.selectbox(
                        f"Module Type",
                        options=[t.value for t in ModuleType],
                        key=f"type_{i}"
                    )
                    rated_power = st.number_input(
                        f"Rated Power (W)",
                        min_value=0.0,
                        value=300.0,
                        key=f"power_{i}"
                    )
                    technology = st.text_input(f"Technology", key=f"tech_{i}")

                if serial:
                    modules.append({
                        'serial_number': serial,
                        'manufacturer': manufacturer,
                        'model': model,
                        'module_type': module_type,
                        'rated_power': rated_power,
                        'technology': technology
                    })

        # Equipment information
        st.subheader("Equipment Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            chamber_id = st.text_input("Chamber ID")
            chamber_cal = st.date_input("Chamber Calibration Date")

        with col2:
            simulator_id = st.text_input("Solar Simulator ID")
            simulator_cal = st.date_input("Simulator Calibration Date")

        with col3:
            logger_id = st.text_input("Data Logger ID")

        # Initialize test button
        st.markdown("---")

        if st.button("Initialize Test", type="primary", use_container_width=True):
            if not operator:
                st.error("Please enter operator name")
            elif len(modules) < protocol['test_requirements']['sample_size']['minimum']:
                st.error(f"Minimum {protocol['test_requirements']['sample_size']['minimum']} modules required")
            else:
                # Initialize test engine
                st.session_state.test_engine = TestEngine(protocol, test_id)

                # Start test
                module_serials = [m['serial_number'] for m in modules]
                result = st.session_state.test_engine.start_test(module_serials, operator)

                st.session_state.test_started = True
                st.success(f"Test {test_id} initialized successfully!")
                st.json(result)

    def _render_test_execution(self):
        """Render test execution tab"""
        st.header("Test Execution")

        if not st.session_state.test_started:
            st.warning("Please initialize the test in the Test Setup tab")
            return

        engine = st.session_state.test_engine

        # Display current status
        status = engine.get_status()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Status", status['status'])

        with col2:
            st.metric("Current Step", status['current_step'])

        with col3:
            st.metric("Current Cycle", status['current_cycle'])

        with col4:
            st.metric("Progress", f"{status['progress_percent']}%")

        # Progress bar
        st.progress(status['progress_percent'] / 100)

        st.markdown("---")

        # Current step details
        protocol = st.session_state.protocol
        steps = protocol['test_sequence']['steps']

        if status['current_step'] < len(steps):
            current_step = steps[status['current_step']]

            st.subheader(f"Current Step: {current_step['name']}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Temperature Target", f"{current_step['temperature']}°C")

            with col2:
                st.metric("Humidity Target", f"{current_step['relative_humidity']}%")

            with col3:
                st.metric("Duration", f"{current_step['duration']} {current_step['duration_unit']}")

            with col4:
                repeat = current_step.get('repeat_count', 1)
                st.metric("Repeat Count", repeat)

            st.info(current_step['description'])

        st.markdown("---")

        # Manual data entry
        st.subheader("Record Measurement")

        col1, col2, col3 = st.columns(3)

        with col1:
            param = st.selectbox("Parameter", ["temperature", "relative_humidity", "Pmax", "Voc", "Isc"])

        with col2:
            value = st.number_input("Value", value=0.0, format="%.2f")

        with col3:
            unit = st.text_input("Unit", value="°C" if param == "temperature" else "%")

        if st.button("Record Measurement"):
            engine.record_measurement(param, value, unit)
            st.success(f"Recorded {param} = {value} {unit}")

        # Control buttons
        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Advance Step", use_container_width=True):
                result = engine.advance_step()
                st.json(result)

        with col2:
            if st.button("Record Deviation", use_container_width=True):
                with st.form("deviation_form"):
                    desc = st.text_area("Description")
                    severity = st.selectbox("Severity", ["MINOR", "MAJOR", "CRITICAL"])
                    action = st.text_area("Corrective Action")

                    if st.form_submit_button("Submit"):
                        engine.record_deviation(desc, severity, action)
                        st.success("Deviation recorded")

        with col3:
            if st.button("Abort Test", type="secondary", use_container_width=True):
                reason = st.text_input("Reason for abort")
                if reason and st.button("Confirm Abort"):
                    engine.abort_test(reason)
                    st.error(f"Test aborted: {reason}")

    def _render_monitoring(self):
        """Render monitoring tab"""
        st.header("Real-time Monitoring")

        if not st.session_state.test_started:
            st.warning("Please initialize the test in the Test Setup tab")
            return

        engine = st.session_state.test_engine

        # Auto-refresh
        st.checkbox("Auto-refresh (every 30s)", value=False, key="auto_refresh")

        # Display measurements
        st.subheader("Recent Measurements")

        if engine.measurements:
            df = pd.DataFrame(engine.measurements[-50:])  # Last 50 measurements
            st.dataframe(df, use_container_width=True)

            # Plot temperature/humidity
            if 'temperature' in df['parameter'].values:
                st.subheader("Temperature Trend")
                temp_df = df[df['parameter'] == 'temperature']
                st.line_chart(temp_df.set_index('timestamp')['value'])

            if 'relative_humidity' in df['parameter'].values:
                st.subheader("Humidity Trend")
                hum_df = df[df['parameter'] == 'relative_humidity']
                st.line_chart(hum_df.set_index('timestamp')['value'])

        else:
            st.info("No measurements recorded yet")

        # Display alerts
        st.subheader("Active Alerts")

        if engine.alerts:
            alert_df = pd.DataFrame(engine.alerts)
            st.dataframe(alert_df, use_container_width=True)
        else:
            st.success("No active alerts")

        # Display deviations
        st.subheader("Deviations")

        if engine.deviations:
            dev_df = pd.DataFrame(engine.deviations)
            st.dataframe(dev_df, use_container_width=True)
        else:
            st.success("No deviations recorded")

    def _render_analysis(self):
        """Render analysis tab"""
        st.header("Data Analysis")

        if not st.session_state.test_started:
            st.warning("Please initialize the test in the Test Setup tab")
            return

        engine = st.session_state.test_engine
        analyzer = DataAnalyzer()

        # Statistics
        if engine.measurements:
            st.subheader("Statistical Summary")

            # Get temperature measurements
            temp_measurements = [
                m['value'] for m in engine.measurements
                if m['parameter'] == 'temperature'
            ]

            if temp_measurements:
                temp_stats = analyzer.calculate_statistics(temp_measurements)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Mean Temp", f"{temp_stats['mean']:.2f}°C")

                with col2:
                    st.metric("Std Dev", f"{temp_stats['std_dev']:.2f}°C")

                with col3:
                    st.metric("Min", f"{temp_stats['min']:.2f}°C")

                with col4:
                    st.metric("Max", f"{temp_stats['max']:.2f}°C")

            # Humidity measurements
            hum_measurements = [
                m['value'] for m in engine.measurements
                if m['parameter'] == 'relative_humidity'
            ]

            if hum_measurements:
                hum_stats = analyzer.calculate_statistics(hum_measurements)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Mean Humidity", f"{hum_stats['mean']:.2f}%")

                with col2:
                    st.metric("Std Dev", f"{hum_stats['std_dev']:.2f}%")

                with col3:
                    st.metric("Min", f"{hum_stats['min']:.2f}%")

                with col4:
                    st.metric("Max", f"{hum_stats['max']:.2f}%")

            # Outlier detection
            st.subheader("Outlier Detection")

            if temp_measurements:
                outliers = analyzer.detect_outliers(temp_measurements)
                if outliers:
                    st.warning(f"Found {len(outliers)} temperature outliers")
                    st.json(outliers)
                else:
                    st.success("No outliers detected")

        else:
            st.info("No data available for analysis")

    def _render_report(self):
        """Render report generation tab"""
        st.header("Test Report")

        if not st.session_state.test_started:
            st.warning("Please initialize the test in the Test Setup tab")
            return

        engine = st.session_state.test_engine
        status = engine.get_status()

        # Report sections
        st.subheader("Executive Summary")

        summary_data = {
            "Test ID": engine.test_id,
            "Protocol": st.session_state.protocol['protocol_id'],
            "Status": status['status'],
            "Start Time": status['start_time'],
            "Progress": f"{status['progress_percent']}%",
            "Total Measurements": status['total_measurements'],
            "Alerts": status['total_alerts'],
            "Deviations": status['total_deviations']
        }

        st.json(summary_data)

        # Generate report button
        if st.button("Generate PDF Report", type="primary"):
            st.info("Report generation feature coming soon...")

        # Export data
        st.subheader("Export Data")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export Measurements (CSV)"):
                if engine.measurements:
                    df = pd.DataFrame(engine.measurements)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"{engine.test_id}_measurements.csv",
                        "text/csv"
                    )

        with col2:
            if st.button("Export Alerts (CSV)"):
                if engine.alerts:
                    df = pd.DataFrame(engine.alerts)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"{engine.test_id}_alerts.csv",
                        "text/csv"
                    )


def main():
    """Main entry point"""
    ui = TropicalClimateUI()
    ui.run()


if __name__ == "__main__":
    main()
