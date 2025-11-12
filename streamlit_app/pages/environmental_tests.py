"""
Environmental Tests UI
Combined interface for Humidity-Freeze (PVTP-003-HF) and Damp Heat (PVTP-004-DH) protocols
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json
import time

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))
from protocols.environmental_handler import EnvironmentalProtocolHandler

# Page configuration
st.set_page_config(
    page_title="Environmental Stress Tests",
    page_icon="🌡️",
    layout="wide"
)

# Initialize session state
if 'env_handler' not in st.session_state:
    st.session_state.env_handler = None
if 'test_running' not in st.session_state:
    st.session_state.test_running = False
if 'test_data' not in st.session_state:
    st.session_state.test_data = []
if 'email_alerts_enabled' not in st.session_state:
    st.session_state.email_alerts_enabled = False
if 'alert_email' not in st.session_state:
    st.session_state.alert_email = ""


def send_email_alert(subject: str, message: str):
    """Send email alert for test milestones"""
    if st.session_state.email_alerts_enabled and st.session_state.alert_email:
        # In production, integrate with actual email service
        st.success(f"📧 Email alert sent to {st.session_state.alert_email}: {subject}")
        # TODO: Implement actual email sending


def format_duration(hours: float) -> str:
    """Format hours into readable duration"""
    if hours < 0:
        return "Completed"

    days = int(hours // 24)
    remaining_hours = int(hours % 24)
    minutes = int((hours * 60) % 60)

    if days > 0:
        return f"{days}d {remaining_hours}h {minutes}m"
    elif remaining_hours > 0:
        return f"{remaining_hours}h {minutes}m"
    else:
        return f"{minutes}m"


def render_phase_indicator():
    """Render phase indicator for humidity-freeze protocol"""
    if st.session_state.env_handler and st.session_state.env_handler.protocol_type == "humidity_freeze":
        st.subheader("🔄 Current Phase")

        progress = st.session_state.env_handler.get_test_progress()
        current_phase = progress['current_phase']
        current_cycle = progress['current_cycle']
        max_cycles = progress['max_cycles']

        # Phase indicator
        col1, col2, col3, col4 = st.columns(4)

        phases = {
            "humidity": ("💧", "Humidity\n85°C / 85%RH", col1),
            "transition_to_freeze": ("⚡", "Transition\nto Freeze", col2),
            "freeze": ("❄️", "Freeze\n-40°C", col3),
            "transition_to_humidity": ("⚡", "Transition\nto Humidity", col4)
        }

        for phase_name, (icon, label, col) in phases.items():
            with col:
                if current_phase == phase_name:
                    st.markdown(f"""
                        <div style='text-align: center; padding: 20px;
                                    background-color: #28a745; border-radius: 10px;'>
                            <h1>{icon}</h1>
                            <p style='color: white; font-weight: bold;'>{label}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='text-align: center; padding: 20px;
                                    background-color: #6c757d; border-radius: 10px; opacity: 0.5;'>
                            <h1>{icon}</h1>
                            <p style='color: white;'>{label}</p>
                        </div>
                    """, unsafe_allow_html=True)

        # Cycle progress bar
        st.markdown("---")
        st.subheader(f"Cycle {current_cycle} of {max_cycles}")
        st.progress(current_cycle / max_cycles if max_cycles > 0 else 0)


def render_countdown_timer():
    """Render countdown timer for long-duration tests"""
    if st.session_state.env_handler:
        progress = st.session_state.env_handler.get_test_progress()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("⏱️ Elapsed Time", format_duration(progress['elapsed_hours']))

        with col2:
            if 'estimated_remaining_hours' in progress:
                remaining = progress['estimated_remaining_hours']
                st.metric("⏳ Remaining Time", format_duration(remaining))

        with col3:
            st.metric("📊 Progress", f"{progress['progress_percentage']:.1f}%")


def render_environmental_data_chart():
    """Render real-time environmental data chart"""
    if st.session_state.env_handler and st.session_state.env_handler.continuous_data:
        st.subheader("📈 Environmental Conditions")

        data = st.session_state.env_handler.continuous_data

        # Prepare data for plotting
        timestamps = [d.timestamp for d in data]
        temperatures = [d.temperature for d in data]
        humidities = [d.humidity for d in data]

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Temperature (°C)", "Relative Humidity (%)"),
            vertical_spacing=0.15
        )

        # Temperature plot
        fig.add_trace(
            go.Scatter(x=timestamps, y=temperatures, name="Temperature",
                      line=dict(color='red', width=2)),
            row=1, col=1
        )

        # Add target temperature line
        protocol_type = st.session_state.env_handler.protocol_type
        if protocol_type == "damp_heat":
            target_temp = 85
            fig.add_hline(y=target_temp, line_dash="dash", line_color="orange",
                         annotation_text="Target: 85°C", row=1, col=1)

        # Humidity plot
        fig.add_trace(
            go.Scatter(x=timestamps, y=humidities, name="Humidity",
                      line=dict(color='blue', width=2)),
            row=2, col=1
        )

        # Add target humidity line
        if protocol_type == "damp_heat":
            target_rh = 85
            fig.add_hline(y=target_rh, line_dash="dash", line_color="lightblue",
                         annotation_text="Target: 85%RH", row=2, col=1)

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=2, col=1)

        fig.update_layout(height=600, showlegend=False)

        st.plotly_chart(fig, use_container_width=True)


def render_performance_tracking():
    """Render module performance tracking"""
    if st.session_state.env_handler and st.session_state.env_handler.measurements:
        st.subheader("⚡ Module Performance Tracking")

        measurements = st.session_state.env_handler.measurements

        # Prepare data
        intervals = [m.interval for m in measurements]
        power_loss = [m.power_loss_percentage for m in measurements]
        insulation_r = [m.insulation_resistance for m in measurements]

        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Power Degradation (%)", "Insulation Resistance (MΩ)"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Power degradation
        fig.add_trace(
            go.Scatter(x=intervals, y=power_loss, name="Power Loss",
                      mode='lines+markers', line=dict(color='red', width=2),
                      marker=dict(size=8)),
            row=1, col=1
        )

        # Add acceptance limit line
        protocol_type = st.session_state.env_handler.protocol_type
        if protocol_type == "damp_heat":
            fig.add_hline(y=5.0, line_dash="dash", line_color="orange",
                         annotation_text="5% Limit", row=1, col=1)

        # Insulation resistance
        fig.add_trace(
            go.Scatter(x=intervals, y=insulation_r, name="Insulation R",
                      mode='lines+markers', line=dict(color='green', width=2),
                      marker=dict(size=8)),
            row=1, col=2
        )

        # Add minimum threshold line
        fig.add_hline(y=40, line_dash="dash", line_color="red",
                     annotation_text="40 MΩ Min", row=1, col=2)

        fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
        fig.update_xaxes(title_text="Time (hours)", row=1, col=2)
        fig.update_yaxes(title_text="Power Loss (%)", row=1, col=1)
        fig.update_yaxes(title_text="Insulation R (MΩ)", row=1, col=2)

        fig.update_layout(height=400, showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

        # Display measurements table
        with st.expander("📋 View Detailed Measurements"):
            df = pd.DataFrame([
                {
                    "Time (h)": m.interval,
                    "Pmax (W)": m.Pmax,
                    "Voc (V)": m.Voc,
                    "Isc (A)": m.Isc,
                    "FF": m.FF,
                    "Power Loss (%)": m.power_loss_percentage,
                    "Insulation R (MΩ)": m.insulation_resistance,
                    "Visual Defects": ", ".join(m.visual_defects) if m.visual_defects else "None"
                }
                for m in measurements
            ])
            st.dataframe(df, use_container_width=True)


def render_nonconformance_log():
    """Render nonconformance log"""
    if st.session_state.env_handler:
        st.subheader("⚠️ Nonconformance Register")

        ncs = st.session_state.env_handler.nonconformances

        if ncs:
            df = pd.DataFrame(ncs)
            st.dataframe(df, use_container_width=True)

            # Summary
            impact_counts = df['impact_assessment'].value_counts()
            st.info(f"Total Nonconformances: {len(ncs)} | "
                   f"Major: {impact_counts.get('major', 0)} | "
                   f"Moderate: {impact_counts.get('moderate', 0)} | "
                   f"Minor: {impact_counts.get('minor', 0)}")
        else:
            st.success("✅ No nonconformances recorded")


# Main UI
st.title("🌡️ Environmental Stress Testing")
st.markdown("Humidity-Freeze (PVTP-003-HF) & Damp Heat (PVTP-004-DH) Protocols")

# Sidebar - Test Setup
with st.sidebar:
    st.header("🔧 Test Setup")

    # Protocol selection
    protocol_type = st.selectbox(
        "Select Protocol",
        ["humidity_freeze", "damp_heat"],
        format_func=lambda x: "Humidity-Freeze (PVTP-003-HF)" if x == "humidity_freeze"
                             else "Damp Heat (PVTP-004-DH)"
    )

    # Protocol info
    if protocol_type == "humidity_freeze":
        st.info("""
        **Humidity-Freeze Cycling**
        - 10 cycles
        - Humidity: 85°C / 85%RH (20h)
        - Freeze: -40°C (4h)
        - IEC 61215-2:2016 MQT 13
        """)
        protocol_path = Path(__file__).parent.parent.parent / "templates" / "humidity_freeze.json"
    else:
        st.info("""
        **Damp Heat Test**
        - Duration: 1000 hours
        - Conditions: 85°C / 85%RH
        - Continuous exposure
        - IEC 61215-2:2016 MQT 14
        """)
        protocol_path = Path(__file__).parent.parent.parent / "templates" / "damp_heat.json"

    # Module configuration
    st.markdown("---")
    st.subheader("Module Configuration")
    module_input = st.text_area(
        "Module Serial Numbers (one per line)",
        height=100,
        placeholder="MOD-2025-001\nMOD-2025-002\nMOD-2025-003"
    )

    # Email alerts
    st.markdown("---")
    st.subheader("📧 Email Alerts")
    st.session_state.email_alerts_enabled = st.checkbox(
        "Enable email alerts",
        value=st.session_state.email_alerts_enabled
    )
    if st.session_state.email_alerts_enabled:
        st.session_state.alert_email = st.text_input(
            "Alert Email",
            value=st.session_state.alert_email,
            placeholder="engineer@example.com"
        )

    # Start test button
    st.markdown("---")
    if st.button("▶️ Start Test", type="primary", disabled=st.session_state.test_running):
        if module_input.strip():
            module_list = [line.strip() for line in module_input.split('\n') if line.strip()]

            # Initialize handler
            st.session_state.env_handler = EnvironmentalProtocolHandler(
                protocol_type=protocol_type,
                protocol_path=str(protocol_path)
            )

            # Start test
            session_info = st.session_state.env_handler.start_test(module_list)
            st.session_state.test_running = True

            st.success(f"✅ Test started: {session_info['protocol_name']}")
            send_email_alert(
                "Test Started",
                f"Protocol {session_info['protocol_id']} started with {len(module_list)} modules"
            )
        else:
            st.error("Please enter at least one module serial number")

    # Stop test button
    if st.button("⏹️ Stop Test", disabled=not st.session_state.test_running):
        st.session_state.test_running = False
        st.warning("⏹️ Test stopped")
        if st.session_state.env_handler:
            progress = st.session_state.env_handler.get_test_progress()
            send_email_alert(
                "Test Stopped",
                f"Test stopped at {progress['elapsed_hours']:.1f} hours"
            )

# Main content area
if st.session_state.test_running and st.session_state.env_handler:
    # Test status banner
    st.success("🟢 Test Running")

    # Phase indicator (for humidity-freeze)
    if st.session_state.env_handler.protocol_type == "humidity_freeze":
        render_phase_indicator()
        st.markdown("---")

    # Countdown timer
    render_countdown_timer()
    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Real-time Data",
        "⚡ Performance",
        "🔄 Phase Control",
        "⚠️ Nonconformances",
        "💾 Export"
    ])

    with tab1:
        # Real-time environmental data
        render_environmental_data_chart()

        # Manual data logging
        st.markdown("---")
        st.subheader("📝 Log Environmental Data")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            temp_input = st.number_input("Temperature (°C)", value=85.0, step=0.1)
        with col2:
            humidity_input = st.number_input("Humidity (%)", value=85.0, step=0.1)
        with col3:
            status_input = st.selectbox("Chamber Status",
                                       ["normal", "stabilizing", "transitioning", "alarm", "paused"])
        with col4:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("📥 Log Data"):
                result = st.session_state.env_handler.log_environmental_data(
                    temperature=temp_input,
                    humidity=humidity_input,
                    chamber_status=status_input
                )

                if result['validation']['overall_valid']:
                    st.success("✅ Data logged - Conditions in specification")
                else:
                    st.warning(f"⚠️ Data logged - Deviations: {', '.join(result['validation']['deviations'])}")

    with tab2:
        # Performance tracking
        render_performance_tracking()

        # Manual performance logging
        st.markdown("---")
        st.subheader("📝 Log Performance Measurement")

        col1, col2, col3 = st.columns(3)
        with col1:
            pmax = st.number_input("Pmax (W)", value=300.0, step=0.1)
            voc = st.number_input("Voc (V)", value=45.0, step=0.1)
        with col2:
            isc = st.number_input("Isc (A)", value=9.0, step=0.1)
            ff = st.number_input("Fill Factor", value=0.75, step=0.01)
        with col3:
            insulation_r = st.number_input("Insulation R (MΩ)", value=100.0, step=1.0)
            visual_defects = st.text_input("Visual Defects (comma-separated)", "")

        if st.button("📥 Log Performance"):
            defects_list = [d.strip() for d in visual_defects.split(',') if d.strip()]
            result = st.session_state.env_handler.log_performance_measurement(
                Pmax=pmax,
                Voc=voc,
                Isc=isc,
                FF=ff,
                insulation_resistance=insulation_r,
                visual_defects=defects_list
            )

            acceptance = result['acceptance_check']
            if acceptance['overall'] == "PASS":
                st.success("✅ Performance measurement logged - All criteria PASS")
            else:
                st.error(f"❌ Performance measurement logged - FAIL: {', '.join(acceptance['failures'])}")
                send_email_alert(
                    "Performance Failure",
                    f"Module failed acceptance criteria: {', '.join(acceptance['failures'])}"
                )

    with tab3:
        # Phase control (humidity-freeze only)
        if st.session_state.env_handler.protocol_type == "humidity_freeze":
            st.subheader("🔄 Phase Transition Control")

            col1, col2 = st.columns(2)

            with col1:
                new_phase = st.selectbox(
                    "Transition to Phase",
                    ["humidity", "transition_to_freeze", "freeze", "transition_to_humidity"]
                )

                if st.button("➡️ Transition Phase"):
                    result = st.session_state.env_handler.transition_phase(new_phase)
                    st.success(f"✅ Transitioned to {new_phase}")

                    if "transition" in new_phase.lower():
                        st.info("⚠️ Monitor transition rate (max 3°C/min)")

                if st.button("🔄 Complete Cycle"):
                    result = st.session_state.env_handler.increment_cycle()
                    st.success(f"✅ Cycle {result['current_cycle']} of {result['max_cycles']} completed")

                    # Check if milestone for measurement
                    if result['current_cycle'] in [0, 5, 10]:
                        st.warning(f"📊 Performance measurement required at cycle {result['current_cycle']}")
                        send_email_alert(
                            "Measurement Required",
                            f"Performance measurement required at cycle {result['current_cycle']}"
                        )

            with col2:
                st.info("""
                **Phase Sequence:**
                1. Humidity (85°C/85%RH) - 20h
                2. Transition to Freeze (max 3°C/min)
                3. Freeze (-40°C) - 4h
                4. Transition to Humidity (max 3°C/min)
                5. Repeat

                **Measurements at:** Cycles 0, 5, 10
                """)
        else:
            st.info("Phase control is only applicable to Humidity-Freeze protocol")

    with tab4:
        # Nonconformance logging
        render_nonconformance_log()

        st.markdown("---")
        st.subheader("📝 Log Nonconformance")

        col1, col2 = st.columns(2)
        with col1:
            nc_type = st.selectbox("Type", [
                "temperature_excursion",
                "humidity_excursion",
                "chamber_failure",
                "power_interruption",
                "data_loss",
                "operator_error",
                "other"
            ])
            nc_description = st.text_area("Description")
            nc_duration = st.number_input("Duration (hours)", value=0.0, step=0.1)

        with col2:
            nc_impact = st.selectbox("Impact", ["none", "minor", "moderate", "major", "test_invalid"])
            nc_action = st.text_area("Corrective Action")
            nc_disposition = st.selectbox("Disposition", ["continue", "extend_test", "restart_test", "abort_test"])
            nc_approver = st.text_input("Approved By")

        if st.button("📥 Log Nonconformance"):
            if nc_description and nc_action and nc_approver:
                result = st.session_state.env_handler.log_nonconformance(
                    nc_type=nc_type,
                    description=nc_description,
                    duration=nc_duration,
                    impact=nc_impact,
                    corrective_action=nc_action,
                    disposition=nc_disposition,
                    approved_by=nc_approver
                )
                st.success(f"✅ Nonconformance logged: {result['nc_id']}")

                if nc_impact in ["major", "test_invalid"]:
                    send_email_alert(
                        f"URGENT: {nc_impact.upper()} Nonconformance",
                        f"NC-{result['nc_id']}: {nc_description}"
                    )
            else:
                st.error("Please fill in all required fields")

    with tab5:
        # Export data
        st.subheader("💾 Export Test Data")

        if st.button("📊 Generate Report"):
            export_data = st.session_state.env_handler.export_test_data()

            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Measurements", len(export_data['measurements']))
            with col2:
                st.metric("Nonconformances", len(export_data['nonconformances']))
            with col3:
                st.metric("Progress", f"{export_data['progress']['progress_percentage']:.1f}%")

            # Download JSON
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"environmental_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

            # Insulation resistance trend analysis
            if len(export_data['measurements']) >= 2:
                st.markdown("---")
                st.subheader("📈 Insulation Resistance Trend Analysis")
                trend = st.session_state.env_handler.calculate_insulation_resistance_trend()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Trend", trend['trend'].upper())
                with col2:
                    st.metric("Current Value", f"{trend['current_value']:.1f} MΩ")
                with col3:
                    st.metric("Change", f"{trend['change']:+.1f} MΩ")

                if trend['hours_to_threshold']:
                    st.warning(f"⚠️ Projected to reach 40 MΩ threshold in {trend['hours_to_threshold']:.1f} hours")

else:
    # Welcome screen
    st.info("👈 Configure test parameters in the sidebar and click 'Start Test' to begin")

    # Protocol comparison
    st.subheader("📋 Protocol Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🔄 Humidity-Freeze (PVTP-003-HF)

        **Purpose:** Evaluate resistance to moisture ingress and thermal shock

        **Test Profile:**
        - 10 cycles
        - Humidity phase: 85°C / 85%RH for 20 hours
        - Freeze phase: -40°C for 4 hours
        - Transition rate: ≤3°C/min

        **Duration:** ~240 hours (10 days)

        **Measurements:** At cycles 0, 5, and 10

        **Acceptance Criteria:**
        - Power loss ≤2% (cycles 0-5)
        - Power loss ≤5% (cycles 5-10)
        - Insulation resistance >40 MΩ
        """)

    with col2:
        st.markdown("""
        ### 🌡️ Damp Heat (PVTP-004-DH)

        **Purpose:** Evaluate long-term resistance to moisture and corrosion

        **Test Profile:**
        - Continuous exposure
        - Constant: 85°C / 85%RH
        - Duration: 1000 hours

        **Duration:** 1000 hours (~42 days)

        **Measurements:** At 0, 250, 500, 750, and 1000 hours

        **Acceptance Criteria:**
        - Power loss ≤5% after 1000h
        - Insulation resistance >40 MΩ at all intervals
        """)

# Auto-refresh for real-time updates
if st.session_state.test_running:
    time.sleep(1)
    st.rerun()
