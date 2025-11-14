"""Analysis page with I-V curves and degradation plots."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from test_protocols.database.connection import db
from test_protocols.models.schema import (
    EnvironmentalLog,
    IVMeasurement,
    TestRun,
    VisualInspection,
)


def show():
    """Show analysis page with charts and visualizations."""
    st.title("📊 Test Analysis")
    st.markdown("Analyze test results and performance degradation")
    st.markdown("---")

    # Get all test runs
    with db.session_scope() as session:
        test_runs = session.query(TestRun).order_by(TestRun.created_at.desc()).all()

        if not test_runs:
            st.info("No test data available for analysis")
            return

        # Test selection
        test_options = {
            f"{test.specimen_id} - {test.protocol_code} (ID: {test.id}, {test.status})": test.id
            for test in test_runs
        }

        selected_test_label = st.selectbox("Select Test for Analysis", options=list(test_options.keys()))
        test_run_id = test_options[selected_test_label]

        # Get selected test
        test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()

        if not test_run:
            st.error("Test not found")
            return

        # Test summary
        st.markdown("---")
        st.subheader("Test Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Specimen", test_run.specimen_id)
            st.metric("Protocol", test_run.protocol_code)

        with col2:
            st.metric("Status", test_run.status.upper())
            st.metric("QC Status", test_run.qc_status.upper())

        with col3:
            if test_run.module_type:
                st.metric("Module Type", test_run.module_type)
            if test_run.manufacturer:
                st.metric("Manufacturer", test_run.manufacturer)

        with col4:
            if test_run.end_date:
                duration = test_run.end_date - test_run.start_date
                duration_hours = duration.total_seconds() / 3600
                st.metric("Duration", f"{duration_hours:.1f} hours")

        st.markdown("---")

        # I-V Curve Analysis
        st.subheader("⚡ I-V Curve Analysis")

        iv_measurements = (
            session.query(IVMeasurement)
            .filter(IVMeasurement.test_run_id == test_run_id)
            .order_by(IVMeasurement.elapsed_hours)
            .all()
        )

        if iv_measurements:
            # I-V Curves Overlay
            st.markdown("### I-V Curves Over Time")

            fig_iv = go.Figure()

            # Color scale for time progression
            colors = [
                f"rgb({int(255 * (1 - i / len(iv_measurements)))}, {int(100 + 155 * i / len(iv_measurements))}, {int(255 * i / len(iv_measurements))})"
                for i in range(len(iv_measurements))
            ]

            for idx, iv in enumerate(iv_measurements):
                fig_iv.add_trace(
                    go.Scatter(
                        x=iv.voltage,
                        y=iv.current,
                        mode="lines+markers",
                        name=f"{iv.elapsed_hours}h",
                        line=dict(color=colors[idx]),
                        hovertemplate="V: %{x:.2f}V<br>I: %{y:.2f}A<extra></extra>",
                    )
                )

            fig_iv.update_layout(
                title="I-V Characteristic Curves",
                xaxis_title="Voltage (V)",
                yaxis_title="Current (A)",
                hovermode="closest",
                height=500,
                showlegend=True,
            )

            st.plotly_chart(fig_iv, use_container_width=True)

            # Power Curves
            st.markdown("### Power Curves Over Time")

            fig_power = go.Figure()

            for idx, iv in enumerate(iv_measurements):
                fig_power.add_trace(
                    go.Scatter(
                        x=iv.voltage,
                        y=iv.power,
                        mode="lines+markers",
                        name=f"{iv.elapsed_hours}h",
                        line=dict(color=colors[idx]),
                        hovertemplate="V: %{x:.2f}V<br>P: %{y:.2f}W<extra></extra>",
                    )
                )

            fig_power.update_layout(
                title="Power vs Voltage Curves",
                xaxis_title="Voltage (V)",
                yaxis_title="Power (W)",
                hovermode="closest",
                height=500,
                showlegend=True,
            )

            st.plotly_chart(fig_power, use_container_width=True)

            # Degradation Analysis
            st.markdown("### Power Degradation Over Time")

            elapsed_hours_list = [iv.elapsed_hours for iv in iv_measurements]
            max_powers = [iv.max_power for iv in iv_measurements]
            degradations = [iv.degradation_percent for iv in iv_measurements]

            fig_deg = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("Maximum Power vs Time", "Power Degradation vs Time"),
                vertical_spacing=0.12,
            )

            # Max power plot
            fig_deg.add_trace(
                go.Scatter(
                    x=elapsed_hours_list,
                    y=max_powers,
                    mode="lines+markers",
                    name="Pmax",
                    line=dict(color="blue", width=3),
                    marker=dict(size=8),
                ),
                row=1,
                col=1,
            )

            # Degradation plot
            fig_deg.add_trace(
                go.Scatter(
                    x=elapsed_hours_list,
                    y=degradations,
                    mode="lines+markers",
                    name="Degradation",
                    line=dict(color="red", width=3),
                    marker=dict(size=8),
                    fill="tozeroy",
                    fillcolor="rgba(255, 0, 0, 0.1)",
                ),
                row=2,
                col=1,
            )

            # Add 5% degradation threshold line
            fig_deg.add_hline(
                y=5.0,
                line_dash="dash",
                line_color="orange",
                annotation_text="5% Threshold",
                row=2,
                col=1,
            )

            fig_deg.update_xaxes(title_text="Elapsed Time (hours)", row=2, col=1)
            fig_deg.update_yaxes(title_text="Power (W)", row=1, col=1)
            fig_deg.update_yaxes(title_text="Degradation (%)", row=2, col=1)

            fig_deg.update_layout(height=700, showlegend=False)

            st.plotly_chart(fig_deg, use_container_width=True)

            # Performance metrics table
            st.markdown("### I-V Measurement Summary")

            iv_data = []
            for iv in iv_measurements:
                iv_data.append(
                    {
                        "Time (h)": iv.elapsed_hours,
                        "Pmax (W)": f"{iv.max_power:.2f}",
                        "Voc (V)": f"{iv.voc:.2f}",
                        "Isc (A)": f"{iv.isc:.2f}",
                        "FF (%)": f"{iv.fill_factor:.2f}",
                        "Degradation (%)": f"{iv.degradation_percent:.2f}",
                    }
                )

            st.dataframe(iv_data, use_container_width=True)

        else:
            st.info("No I-V measurements recorded for this test")

        st.markdown("---")

        # Visual Inspection Analysis
        st.subheader("👁️ Visual Inspection & Corrosion Progression")

        visual_inspections = (
            session.query(VisualInspection)
            .filter(VisualInspection.test_run_id == test_run_id)
            .order_by(VisualInspection.elapsed_hours)
            .all()
        )

        if visual_inspections:
            # Corrosion progression chart
            inspection_hours = [vi.elapsed_hours for vi in visual_inspections]
            corrosion_ratings = [
                int(vi.corrosion_rating.split(" - ")[0]) for vi in visual_inspections
            ]
            affected_areas = [vi.affected_area_percent for vi in visual_inspections]

            fig_corr = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("Corrosion Rating Over Time", "Affected Area Over Time"),
                vertical_spacing=0.12,
            )

            # Corrosion rating
            fig_corr.add_trace(
                go.Scatter(
                    x=inspection_hours,
                    y=corrosion_ratings,
                    mode="lines+markers",
                    name="Corrosion Rating",
                    line=dict(color="orange", width=3),
                    marker=dict(size=10),
                ),
                row=1,
                col=1,
            )

            # Affected area
            fig_corr.add_trace(
                go.Scatter(
                    x=inspection_hours,
                    y=affected_areas,
                    mode="lines+markers",
                    name="Affected Area",
                    line=dict(color="red", width=3),
                    marker=dict(size=10),
                    fill="tozeroy",
                    fillcolor="rgba(255, 0, 0, 0.1)",
                ),
                row=2,
                col=1,
            )

            fig_corr.update_xaxes(title_text="Elapsed Time (hours)", row=2, col=1)
            fig_corr.update_yaxes(title_text="Rating (0-5)", row=1, col=1)
            fig_corr.update_yaxes(title_text="Affected Area (%)", row=2, col=1)

            fig_corr.update_layout(height=600, showlegend=False)

            st.plotly_chart(fig_corr, use_container_width=True)

            # Inspection images gallery
            st.markdown("### Inspection Images")

            from test_protocols.config import config

            cols = st.columns(min(4, len(visual_inspections)))

            for idx, vi in enumerate(visual_inspections):
                with cols[idx % 4]:
                    if vi.image_path and Path(vi.image_path).exists():
                        try:
                            from PIL import Image

                            image = Image.open(vi.image_path)
                            st.image(
                                image,
                                caption=f"{vi.elapsed_hours}h - Rating: {vi.corrosion_rating.split(' - ')[0]}",
                                use_container_width=True,
                            )
                        except Exception as e:
                            st.error(f"Failed to load image: {str(e)}")
                    else:
                        st.info(f"{vi.elapsed_hours}h\nNo image")

        else:
            st.info("No visual inspections recorded for this test")

        st.markdown("---")

        # Environmental Conditions Analysis
        st.subheader("🌡️ Environmental Conditions History")

        env_logs = (
            session.query(EnvironmentalLog)
            .filter(EnvironmentalLog.test_run_id == test_run_id)
            .order_by(EnvironmentalLog.timestamp)
            .all()
        )

        if env_logs:
            timestamps = [log.timestamp for log in env_logs]
            temperatures = [log.temperature for log in env_logs]
            humidities = [log.humidity for log in env_logs]

            fig_env = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("Temperature History", "Humidity History"),
                vertical_spacing=0.12,
            )

            # Temperature
            fig_env.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=temperatures,
                    mode="lines",
                    name="Temperature",
                    line=dict(color="red"),
                ),
                row=1,
                col=1,
            )

            # Target range for temperature
            fig_env.add_hrect(
                y0=34.0,
                y1=36.0,
                fillcolor="green",
                opacity=0.1,
                line_width=0,
                row=1,
                col=1,
            )

            # Humidity
            fig_env.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=humidities,
                    mode="lines",
                    name="Humidity",
                    line=dict(color="blue"),
                ),
                row=2,
                col=1,
            )

            # Target range for humidity
            fig_env.add_hrect(
                y0=93.0,
                y1=97.0,
                fillcolor="green",
                opacity=0.1,
                line_width=0,
                row=2,
                col=1,
            )

            fig_env.update_xaxes(title_text="Time", row=2, col=1)
            fig_env.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
            fig_env.update_yaxes(title_text="Humidity (%)", row=2, col=1)

            fig_env.update_layout(height=600, showlegend=False)

            st.plotly_chart(fig_env, use_container_width=True)

            # Environmental statistics
            st.markdown("### Environmental Statistics")

            col1, col2, col3 = st.columns(3)

            with col1:
                avg_temp = np.mean(temperatures)
                std_temp = np.std(temperatures)
                st.metric("Avg Temperature", f"{avg_temp:.2f} °C")
                st.metric("Std Dev", f"{std_temp:.2f} °C")

            with col2:
                avg_humidity = np.mean(humidities)
                std_humidity = np.std(humidities)
                st.metric("Avg Humidity", f"{avg_humidity:.2f} %")
                st.metric("Std Dev", f"{std_humidity:.2f} %")

            with col3:
                temp_in_range = sum(
                    1 for t in temperatures if 34.0 <= t <= 36.0
                ) / len(temperatures) * 100
                humidity_in_range = sum(
                    1 for h in humidities if 93.0 <= h <= 97.0
                ) / len(humidities) * 100

                st.metric("Temp In Range", f"{temp_in_range:.1f} %")
                st.metric("Humidity In Range", f"{humidity_in_range:.1f} %")

        else:
            st.info("No environmental data recorded for this test")
