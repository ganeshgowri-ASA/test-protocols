"""Active tests monitoring page with real-time chamber conditions."""

from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from test_protocols.database.connection import db
from test_protocols.models.schema import (
    EnvironmentalLog,
    IVMeasurement,
    TestRun,
    VisualInspection,
)
from test_protocols.protocols.registry import protocol_registry


def show():
    """Show active tests monitoring page."""
    st.title("🔄 Active Tests")
    st.markdown("Monitor running tests and log measurements")
    st.markdown("---")

    # Get active tests
    with db.session_scope() as session:
        active_tests = (
            session.query(TestRun)
            .filter(TestRun.status.in_(["running", "paused"]))
            .order_by(TestRun.start_date.desc())
            .all()
        )

        if not active_tests:
            st.info("No active tests. Start a new test to begin monitoring.")
            return

        # Test selection
        test_options = {
            f"{test.specimen_id} - {test.protocol_code} (ID: {test.id})": test.id
            for test in active_tests
        }

        selected_test_label = st.selectbox("Select Test", options=list(test_options.keys()))
        test_run_id = test_options[selected_test_label]

        # Get selected test details
        test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()

        if not test_run:
            st.error("Test not found")
            return

        # Display test information
        st.markdown("---")
        st.subheader("Test Information")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Specimen ID", test_run.specimen_id)
            st.metric("Protocol", test_run.protocol_code)

        with col2:
            st.metric("Status", test_run.status.upper())
            st.metric("QC Status", test_run.qc_status.upper())

        with col3:
            elapsed = datetime.now() - test_run.start_date
            elapsed_hours = elapsed.total_seconds() / 3600
            st.metric("Elapsed Time", f"{elapsed_hours:.1f} hours")

            if test_run.parameters:
                total_hours = test_run.raw_data.get("results", {}).get("total_duration_hours", 0)
                st.metric("Total Duration", f"{total_hours} hours")

        with col4:
            if test_run.parameters:
                params = test_run.parameters
                st.metric("Severity Level", params.get("severity_level", "N/A").split(" - ")[0])

        st.markdown("---")

        # Real-time chamber conditions
        st.subheader("🌡️ Real-Time Chamber Conditions")

        # Get latest environmental log
        latest_env = (
            session.query(EnvironmentalLog)
            .filter(EnvironmentalLog.test_run_id == test_run_id)
            .order_by(EnvironmentalLog.timestamp.desc())
            .first()
        )

        col1, col2, col3, col4 = st.columns(4)

        if latest_env:
            with col1:
                temp_delta = latest_env.temperature - 35.0  # Compare to target
                st.metric(
                    "Temperature",
                    f"{latest_env.temperature:.1f} °C",
                    delta=f"{temp_delta:+.1f}",
                    delta_color="inverse",
                )

            with col2:
                humidity_delta = latest_env.humidity - 95.0  # Compare to target
                st.metric(
                    "Humidity",
                    f"{latest_env.humidity:.1f} %",
                    delta=f"{humidity_delta:+.1f}",
                    delta_color="inverse",
                )

            with col3:
                if latest_env.salt_concentration:
                    salt_delta = latest_env.salt_concentration - 5.0
                    st.metric(
                        "Salt Conc.",
                        f"{latest_env.salt_concentration:.2f} %",
                        delta=f"{salt_delta:+.2f}",
                        delta_color="inverse",
                    )
                else:
                    st.metric("Salt Conc.", "N/A")

            with col4:
                qc_color = {
                    "pass": "🟢",
                    "warning": "🟡",
                    "fail": "🔴",
                }.get(latest_env.qc_status, "⚪")
                st.metric("QC Status", f"{qc_color} {latest_env.qc_status.upper()}")
        else:
            st.info("No environmental data logged yet")

        # Environmental monitoring chart
        env_logs = (
            session.query(EnvironmentalLog)
            .filter(EnvironmentalLog.test_run_id == test_run_id)
            .order_by(EnvironmentalLog.timestamp)
            .all()
        )

        if env_logs:
            st.subheader("📊 Environmental History")

            timestamps = [log.timestamp for log in env_logs]
            temperatures = [log.temperature for log in env_logs]
            humidities = [log.humidity for log in env_logs]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=temperatures,
                    mode="lines+markers",
                    name="Temperature (°C)",
                    yaxis="y1",
                    line=dict(color="red"),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=humidities,
                    mode="lines+markers",
                    name="Humidity (%)",
                    yaxis="y2",
                    line=dict(color="blue"),
                )
            )

            # Add target ranges
            fig.add_hline(
                y=35.0,
                line_dash="dash",
                line_color="red",
                opacity=0.3,
                annotation_text="Target Temp",
                yref="y1",
            )
            fig.add_hline(
                y=95.0,
                line_dash="dash",
                line_color="blue",
                opacity=0.3,
                annotation_text="Target RH",
                yref="y2",
            )

            fig.update_layout(
                title="Temperature and Humidity Over Time",
                xaxis=dict(title="Time"),
                yaxis=dict(title="Temperature (°C)", side="left", range=[30, 40]),
                yaxis2=dict(
                    title="Humidity (%)",
                    overlaying="y",
                    side="right",
                    range=[90, 100],
                ),
                hovermode="x unified",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Data logging section
        st.subheader("📝 Log New Measurement")

        tab1, tab2, tab3 = st.tabs(
            ["🌡️ Environmental Data", "⚡ I-V Measurement", "👁️ Visual Inspection"]
        )

        # Tab 1: Environmental Data
        with tab1:
            with st.form("environmental_form"):
                st.write("Log environmental conditions")

                col1, col2 = st.columns(2)

                with col1:
                    cycle_number = st.number_input(
                        "Cycle Number", min_value=1, value=1, step=1
                    )
                    phase = st.selectbox("Phase", options=["spray", "dry"])
                    temperature = st.number_input(
                        "Temperature (°C)",
                        min_value=30.0,
                        max_value=40.0,
                        value=35.0,
                        step=0.1,
                    )

                with col2:
                    humidity = st.number_input(
                        "Humidity (%)",
                        min_value=80.0,
                        max_value=100.0,
                        value=95.0,
                        step=0.5,
                    )
                    salt_concentration = st.number_input(
                        "Salt Concentration (%)",
                        min_value=4.0,
                        max_value=6.0,
                        value=5.0,
                        step=0.1,
                    )
                    spray_rate = st.number_input(
                        "Spray Rate (mL/h/80cm²)",
                        min_value=0.0,
                        max_value=3.0,
                        value=1.5,
                        step=0.1,
                    )

                if st.form_submit_button("Log Environmental Data"):
                    # Get protocol and update cycle
                    protocol = protocol_registry.get_protocol(test_run.protocol_code)

                    cycle_data = protocol.update_cycle(
                        cycle_number=cycle_number,
                        phase=phase,
                        temperature=temperature,
                        humidity=humidity,
                        salt_concentration=salt_concentration,
                        spray_rate=spray_rate,
                    )

                    # Save to database
                    env_log = EnvironmentalLog(
                        test_run_id=test_run_id,
                        cycle_number=cycle_number,
                        phase=phase,
                        temperature=temperature,
                        humidity=humidity,
                        salt_concentration=salt_concentration,
                        spray_rate=spray_rate,
                        qc_status=cycle_data["qc_status"],
                        qc_messages=cycle_data["qc_messages"],
                    )
                    session.add(env_log)
                    session.commit()

                    st.success("✅ Environmental data logged successfully!")
                    st.rerun()

        # Tab 2: I-V Measurement
        with tab2:
            with st.form("iv_form"):
                st.write("Log I-V curve measurement")

                elapsed_hours = st.number_input(
                    "Elapsed Hours",
                    min_value=0.0,
                    value=elapsed_hours,
                    step=1.0,
                )

                st.write("**I-V Curve Data (comma-separated values)**")

                col1, col2 = st.columns(2)

                with col1:
                    voltage_input = st.text_area(
                        "Voltage (V)",
                        placeholder="0, 5, 10, 15, 20, 25, 30, 35, 40",
                        help="Enter voltage values separated by commas",
                    )

                with col2:
                    current_input = st.text_area(
                        "Current (A)",
                        placeholder="8.5, 8.4, 8.3, 8.1, 7.5, 6.0, 3.0, 1.0, 0",
                        help="Enter current values separated by commas",
                    )

                col1, col2 = st.columns(2)

                with col1:
                    irradiance = st.number_input(
                        "Irradiance (W/m²)", min_value=0.0, value=1000.0, step=10.0
                    )

                with col2:
                    temp = st.number_input(
                        "Module Temperature (°C)", min_value=0.0, value=25.0, step=0.5
                    )

                if st.form_submit_button("Log I-V Measurement"):
                    try:
                        # Parse voltage and current
                        voltage = [float(v.strip()) for v in voltage_input.split(",")]
                        current = [float(i.strip()) for i in current_input.split(",")]

                        if len(voltage) != len(current):
                            st.error("Voltage and current arrays must have same length")
                        else:
                            # Get protocol and record measurement
                            protocol = protocol_registry.get_protocol(test_run.protocol_code)

                            iv_data = protocol.record_iv_measurement(
                                elapsed_hours=elapsed_hours,
                                voltage=voltage,
                                current=current,
                                irradiance=irradiance,
                                temperature=temp,
                            )

                            # Save to database
                            iv_measurement = IVMeasurement(
                                test_run_id=test_run_id,
                                elapsed_hours=elapsed_hours,
                                voltage=voltage,
                                current=current,
                                power=iv_data["power"],
                                max_power=iv_data["max_power"],
                                voc=iv_data["voc"],
                                isc=iv_data["isc"],
                                fill_factor=iv_data["fill_factor"],
                                degradation_percent=iv_data["degradation_percent"],
                                irradiance=irradiance,
                                temperature=temp,
                            )
                            session.add(iv_measurement)
                            session.commit()

                            st.success(
                                f"✅ I-V measurement logged! Pmax={iv_data['max_power']:.2f}W, "
                                f"Degradation={iv_data['degradation_percent']:.2f}%"
                            )
                            st.rerun()

                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")

        # Tab 3: Visual Inspection
        with tab3:
            with st.form("visual_form"):
                st.write("Log visual inspection")

                elapsed_hours_vis = st.number_input(
                    "Elapsed Hours",
                    min_value=0.0,
                    value=elapsed_hours,
                    step=1.0,
                    key="vis_hours",
                )

                corrosion_rating = st.selectbox(
                    "Corrosion Rating",
                    options=[
                        "0 - No corrosion",
                        "1 - Slight corrosion, <1% of area",
                        "2 - Light corrosion, 1-5% of area",
                        "3 - Moderate corrosion, 5-25% of area",
                        "4 - Heavy corrosion, 25-50% of area",
                        "5 - Severe corrosion, >50% of area",
                    ],
                )

                affected_area = st.slider(
                    "Affected Area (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5
                )

                image_file = st.file_uploader(
                    "Upload Image", type=["jpg", "jpeg", "png"], help="Optional image documentation"
                )

                notes = st.text_area("Inspection Notes", placeholder="Describe observations...")

                if st.form_submit_button("Log Visual Inspection"):
                    # Save image if uploaded
                    image_path = None
                    if image_file:
                        from test_protocols.config import config

                        image_dir = config.image_storage_dir / f"test_{test_run_id}"
                        image_dir.mkdir(parents=True, exist_ok=True)

                        image_filename = f"inspection_{int(elapsed_hours_vis)}h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{image_file.name.split('.')[-1]}"
                        image_path = image_dir / image_filename

                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())

                        image_path = str(image_path)

                    # Get protocol and record inspection
                    protocol = protocol_registry.get_protocol(test_run.protocol_code)

                    inspection_data = protocol.record_visual_inspection(
                        elapsed_hours=elapsed_hours_vis,
                        corrosion_rating=corrosion_rating,
                        image_path=image_path,
                        notes=notes,
                        affected_area_percent=affected_area,
                    )

                    # Save to database
                    visual_inspection = VisualInspection(
                        test_run_id=test_run_id,
                        elapsed_hours=elapsed_hours_vis,
                        corrosion_rating=corrosion_rating,
                        affected_area_percent=affected_area,
                        image_path=image_path,
                        notes=notes,
                    )
                    session.add(visual_inspection)
                    session.commit()

                    st.success("✅ Visual inspection logged successfully!")
                    st.rerun()

        st.markdown("---")

        # Test control buttons
        st.subheader("Test Controls")

        col1, col2, col3 = st.columns(3)

        with col1:
            if test_run.status == "running":
                if st.button("⏸️ Pause Test", use_container_width=True):
                    test_run.status = "paused"
                    session.commit()
                    st.success("Test paused")
                    st.rerun()

        with col2:
            if test_run.status == "paused":
                if st.button("▶️ Resume Test", use_container_width=True):
                    test_run.status = "running"
                    session.commit()
                    st.success("Test resumed")
                    st.rerun()

        with col3:
            if st.button("✅ Complete Test", type="primary", use_container_width=True):
                test_run.status = "completed"
                test_run.end_date = datetime.now()
                session.commit()
                st.success("Test completed!")
                st.rerun()
