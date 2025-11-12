"""
Thermal Cycling Protocol - Streamlit UI
Interactive interface for thermal cycling test data entry, monitoring, and analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.protocols.thermal_cycling_handler import (
    ThermalCyclingHandler,
    CycleData,
    MeasurementData,
    prepare_temp_profile_data,
    prepare_degradation_trend_data
)

# Page configuration
st.set_page_config(
    page_title="Thermal Cycling Protocol - PVTP-002-TC",
    page_icon="🌡️",
    layout="wide"
)

# Initialize session state
if 'handler' not in st.session_state:
    st.session_state.handler = ThermalCyclingHandler()

if 'test_started' not in st.session_state:
    st.session_state.test_started = False

if 'current_phase' not in st.session_state:
    st.session_state.current_phase = "Setup"


# ==================== HEADER ====================

st.title("🌡️ Thermal Cycling Test Protocol")
st.subheader("PVTP-002-TC | IEC 61215-2:2016 MQT 12")

# Protocol metadata display
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Protocol ID", "PVTP-002-TC")
with col2:
    st.metric("Test Phase", st.session_state.current_phase)
with col3:
    current_cycle = st.session_state.handler.get_current_cycle()
    st.metric("Current Cycle", current_cycle)
with col4:
    if st.session_state.test_started:
        total_cycles = st.session_state.get('total_cycles', 200)
        completion = (current_cycle / total_cycles) * 100
        st.metric("Completion", f"{completion:.1f}%")
    else:
        st.metric("Status", "Not Started")

st.divider()

# ==================== SIDEBAR - NAVIGATION ====================

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Section",
    [
        "Test Setup",
        "Cycle Monitoring",
        "Measurements",
        "Analysis & Results",
        "Data Management"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "**Thermal Cycling Test**\n\n"
    "Evaluates module resistance to thermal fatigue and temperature extremes.\n\n"
    "**Standards:**\n"
    "- IEC 61215-2:2016 MQT 12\n"
    "- TC50 or TC200 cycles\n"
    "- Temperature: -40°C to +85°C"
)


# ==================== PAGE: TEST SETUP ====================

if page == "Test Setup":
    st.header("Test Setup & Configuration")

    tab1, tab2, tab3 = st.tabs(["General Data", "Sample Information", "Protocol Inputs"])

    with tab1:
        st.subheader("General Test Data")
        col1, col2 = st.columns(2)

        with col1:
            test_facility = st.text_input("Test Facility", placeholder="e.g., ABC Labs, California")
            project = st.text_input("Project Name/ID", placeholder="e.g., PRJ-2025-001")
            client = st.text_input("Client Name", placeholder="e.g., Solar Corp Inc.")

        with col2:
            test_date = st.date_input("Test Start Date", datetime.now())
            technician = st.text_input("Lead Technician", placeholder="e.g., John Smith")
            chamber_id = st.text_input("Chamber ID", placeholder="e.g., TC-CHAMBER-01")

        test_reference = st.text_input("Test Reference Number (Optional)", placeholder="e.g., TR-2025-TC-001")

    with tab2:
        st.subheader("Sample Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Module Specifications**")
            manufacturer = st.text_input("Manufacturer", placeholder="e.g., First Solar")
            model_number = st.text_input("Model Number", placeholder="e.g., FS-6-450W")
            technology = st.selectbox(
                "Technology",
                ["Mono-Si", "Poly-Si", "Thin-Film", "PERC", "HJT", "TOPCon", "Bifacial"]
            )
            rated_power = st.number_input("Rated Power (W)", min_value=0, value=450)
            cell_count = st.number_input("Cell Count", min_value=0, value=144)

        with col2:
            st.markdown("**Sample Details**")
            module_quantity = st.number_input("Number of Modules", min_value=1, value=3)

            st.markdown("**Module Serial Numbers**")
            serial_numbers = st.text_area(
                "Enter serial numbers (one per line)",
                placeholder="SN001\nSN002\nSN003",
                height=150
            )

        # Pre-test measurements
        st.markdown("**Pre-Test Power Measurements**")
        if serial_numbers:
            sn_list = [sn.strip() for sn in serial_numbers.split('\n') if sn.strip()]

            pre_test_data = []
            for sn in sn_list:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.text_input(f"SN", value=sn, disabled=True, key=f"sn_{sn}")
                with col2:
                    pmax = st.number_input(f"Pmax (W)", min_value=0.0, key=f"pmax_{sn}")
                with col3:
                    voc = st.number_input(f"Voc (V)", min_value=0.0, key=f"voc_{sn}")
                with col4:
                    isc = st.number_input(f"Isc (A)", min_value=0.0, key=f"isc_{sn}")

    with tab3:
        st.subheader("Protocol Parameters")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Cycle Configuration**")
            test_type = st.selectbox("Test Type", ["TC200", "TC50"])
            cycle_count = 200 if test_type == "TC200" else 50

            st.metric("Total Cycles", cycle_count)

            st.markdown("**Temperature Range**")
            col_a, col_b = st.columns(2)
            with col_a:
                min_temp = st.number_input("Min Temp (°C)", value=-40)
            with col_b:
                max_temp = st.number_input("Max Temp (°C)", value=85)

        with col2:
            st.markdown("**Timing Parameters**")
            col_a, col_b = st.columns(2)
            with col_a:
                cold_dwell = st.number_input("Cold Dwell (min)", value=30)
            with col_b:
                hot_dwell = st.number_input("Hot Dwell (min)", value=30)

            transition_rate = st.text_input("Max Transition Rate", value="≤100°C/hour", disabled=True)
            humidity_level = st.text_input("Max Humidity", value="<75% RH", disabled=True)

            st.markdown("**Measurement Intervals**")
            measurement_points = st.multiselect(
                "Cycle numbers for intermediate measurements",
                options=list(range(0, cycle_count + 1, 25)),
                default=[0, 50, 100, 150, 200] if cycle_count == 200 else [0, 25, 50]
            )

    # Save setup button
    if st.button("💾 Save Test Setup", type="primary"):
        st.session_state.test_started = True
        st.session_state.total_cycles = cycle_count
        st.session_state.current_phase = "Testing"

        st.success("✅ Test setup saved! Proceed to Cycle Monitoring.")


# ==================== PAGE: CYCLE MONITORING ====================

elif page == "Cycle Monitoring":
    st.header("Cycle Monitoring & Real-Time Data")

    if not st.session_state.test_started:
        st.warning("⚠️ Please complete Test Setup first.")
    else:
        # Cycle counter widget
        st.subheader("Cycle Counter")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            current_cycle = st.session_state.handler.get_current_cycle()
            total_cycles = st.session_state.get('total_cycles', 200)
            st.metric("Current Cycle", f"{current_cycle} / {total_cycles}")

        with col2:
            completion_pct = (current_cycle / total_cycles) * 100 if total_cycles > 0 else 0
            st.metric("Progress", f"{completion_pct:.1f}%")

        with col3:
            # Estimate remaining time (assuming 2 hours per cycle)
            remaining_cycles = total_cycles - current_cycle
            remaining_hours = remaining_cycles * 2
            st.metric("Est. Time Remaining", f"{remaining_hours:.0f} hrs")

        with col4:
            cycle_phase = st.selectbox(
                "Current Phase",
                ["heating", "hot_dwell", "cooling", "cold_dwell"]
            )

        # Progress bar
        st.progress(completion_pct / 100)

        st.divider()

        # Real-time temperature monitoring
        st.subheader("Real-Time Temperature Monitoring")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Temperature input form
            with st.form("cycle_data_entry"):
                st.markdown("**Record Cycle Data**")

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    chamber_temp = st.number_input(
                        "Chamber Temp (°C)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=25.0
                    )

                with col_b:
                    humidity = st.number_input(
                        "Humidity (% RH)",
                        min_value=0.0,
                        max_value=100.0,
                        value=50.0
                    )

                with col_c:
                    module_temp = st.number_input(
                        "Module Temp (°C)",
                        min_value=-50.0,
                        max_value=100.0,
                        value=25.0
                    )

                alarms = st.text_input("Alarms/Notes (if any)", placeholder="Optional")

                submitted = st.form_submit_button("📊 Record Data Point", type="primary")

                if submitted:
                    # Create cycle data
                    cycle_data = CycleData(
                        cycle_number=current_cycle + 1,
                        timestamp=datetime.now(),
                        chamber_temp=chamber_temp,
                        humidity=humidity,
                        module_temps={"module_1": module_temp},
                        cycle_phase=cycle_phase,
                        alarms=[alarms] if alarms else []
                    )

                    st.session_state.handler.add_cycle_data(cycle_data)
                    st.success(f"✅ Data recorded for cycle {current_cycle + 1}")
                    st.rerun()

        with col2:
            st.markdown("**Current Readings**")
            if st.session_state.handler.cycle_data:
                latest = st.session_state.handler.cycle_data[-1]
                st.metric("Chamber", f"{latest.chamber_temp:.1f}°C")
                st.metric("Humidity", f"{latest.humidity:.1f}%")
                st.metric("Phase", latest.cycle_phase.replace('_', ' ').title())
            else:
                st.info("No data recorded yet")

        # Temperature profile chart
        if st.session_state.handler.cycle_data:
            st.divider()
            st.subheader("Temperature Profile - Current Cycle")

            # Get data for current cycle
            current_cycle_num = st.session_state.handler.get_current_cycle()
            if current_cycle_num > 0:
                profile_data = prepare_temp_profile_data(
                    st.session_state.handler,
                    current_cycle_num
                )

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=profile_data['time_minutes'],
                    y=profile_data['temperature'],
                    mode='lines+markers',
                    name='Chamber Temperature',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=6)
                ))

                # Add target temperature lines
                fig.add_hline(y=85, line_dash="dash", line_color="red",
                             annotation_text="Max Temp (85°C)")
                fig.add_hline(y=-40, line_dash="dash", line_color="blue",
                             annotation_text="Min Temp (-40°C)")

                fig.update_layout(
                    title=f"Cycle {current_cycle_num} Temperature Profile",
                    xaxis_title="Time (minutes)",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

        # Cycle validation
        st.divider()
        st.subheader("Cycle Validation")

        if current_cycle > 0:
            if st.button("🔍 Validate Current Cycle"):
                validation = st.session_state.handler.validate_temperature_profile(
                    current_cycle,
                    temp_range=(-40, 85)
                )

                if validation['valid']:
                    st.success("✅ Cycle validation PASSED")
                else:
                    st.error("❌ Cycle validation FAILED")

                # Display results
                col1, col2 = st.columns(2)

                with col1:
                    if validation.get('errors'):
                        st.markdown("**Errors:**")
                        for error in validation['errors']:
                            st.error(f"• {error}")

                    if validation.get('warnings'):
                        st.markdown("**Warnings:**")
                        for warning in validation['warnings']:
                            st.warning(f"• {warning}")

                with col2:
                    st.markdown("**Statistics:**")
                    stats = validation.get('statistics', {})
                    st.write(f"Min Temp Achieved: {stats.get('min_temp_achieved', 'N/A')}°C")
                    st.write(f"Max Temp Achieved: {stats.get('max_temp_achieved', 'N/A')}°C")
                    st.write(f"Max Transition Rate: {stats.get('max_transition_rate', 'N/A'):.1f}°C/hr")
        else:
            st.info("Complete at least one cycle to perform validation")


# ==================== PAGE: MEASUREMENTS ====================

elif page == "Measurements":
    st.header("Intermediate Measurements")

    if not st.session_state.test_started:
        st.warning("⚠️ Please complete Test Setup first.")
    else:
        current_cycle = st.session_state.handler.get_current_cycle()

        st.info(
            f"📊 Current cycle: {current_cycle}. "
            "Enter electrical measurements at specified intervals."
        )

        # Measurement entry form
        st.subheader("Record Measurements")

        with st.form("measurement_entry"):
            col1, col2 = st.columns(2)

            with col1:
                serial_number = st.text_input("Module Serial Number", placeholder="e.g., SN001")
                cycle_number = st.number_input(
                    "Cycle Number",
                    min_value=0,
                    value=current_cycle
                )

            with col2:
                st.markdown("**Measurement Date**")
                measurement_date = st.date_input("Date", datetime.now())

            st.markdown("**Electrical Parameters**")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                pmax = st.number_input("Pmax (W)", min_value=0.0, format="%.2f")
                voc = st.number_input("Voc (V)", min_value=0.0, format="%.2f")

            with col2:
                isc = st.number_input("Isc (A)", min_value=0.0, format="%.2f")
                vmp = st.number_input("Vmp (V)", min_value=0.0, format="%.2f")

            with col3:
                imp = st.number_input("Imp (A)", min_value=0.0, format="%.2f")
                ff = st.number_input("FF (%)", min_value=0.0, max_value=100.0, format="%.2f")

            with col4:
                rs = st.number_input("Rs (Ω) - Optional", min_value=0.0, format="%.4f")
                rsh = st.number_input("Rsh (Ω) - Optional", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("💾 Save Measurement", type="primary")

            if submitted:
                if not serial_number:
                    st.error("❌ Serial number is required")
                else:
                    measurement = MeasurementData(
                        serial_number=serial_number,
                        cycle_number=cycle_number,
                        pmax=pmax,
                        voc=voc,
                        isc=isc,
                        vmp=vmp,
                        imp=imp,
                        ff=ff,
                        rs=rs if rs > 0 else None,
                        rsh=rsh if rsh > 0 else None
                    )

                    st.session_state.handler.add_measurement(measurement)
                    st.success(f"✅ Measurement saved for {serial_number} at cycle {cycle_number}")
                    st.rerun()

        # Display existing measurements
        st.divider()
        st.subheader("Recorded Measurements")

        if st.session_state.handler.measurements:
            # Create DataFrame from measurements
            all_measurements = []
            for cycle_num, meas_list in st.session_state.handler.measurements.items():
                for meas in meas_list:
                    all_measurements.append({
                        "Serial Number": meas.serial_number,
                        "Cycle": meas.cycle_number,
                        "Pmax (W)": meas.pmax,
                        "Voc (V)": meas.voc,
                        "Isc (A)": meas.isc,
                        "Vmp (V)": meas.vmp,
                        "Imp (A)": meas.imp,
                        "FF (%)": meas.ff
                    })

            df = pd.DataFrame(all_measurements)
            st.dataframe(df, use_container_width=True)

            # Export measurements
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Measurements (CSV)",
                data=csv,
                file_name=f"thermal_cycling_measurements_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No measurements recorded yet")


# ==================== PAGE: ANALYSIS & RESULTS ====================

elif page == "Analysis & Results":
    st.header("Analysis & Results")

    if not st.session_state.handler.measurements:
        st.warning("⚠️ No measurement data available for analysis.")
    else:
        # Get list of serial numbers
        serial_numbers = list(set(
            meas.serial_number
            for meas_list in st.session_state.handler.measurements.values()
            for meas in meas_list
        ))

        # Degradation analysis
        st.subheader("Power Degradation Analysis")

        selected_module = st.selectbox("Select Module", serial_numbers)

        if selected_module:
            col1, col2 = st.columns(2)

            with col1:
                initial_cycle = st.number_input(
                    "Initial Cycle",
                    min_value=0,
                    value=0
                )

            with col2:
                final_cycle = st.number_input(
                    "Final Cycle",
                    min_value=1,
                    value=max(st.session_state.handler.measurements.keys())
                )

            if st.button("📊 Calculate Degradation", type="primary"):
                try:
                    analysis = st.session_state.handler.calculate_degradation(
                        selected_module,
                        initial_cycle,
                        final_cycle
                    )

                    # Display results
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Initial Power", f"{analysis.initial_power:.2f} W")

                    with col2:
                        st.metric("Final Power", f"{analysis.final_power:.2f} W")

                    with col3:
                        st.metric(
                            "Power Loss",
                            f"{analysis.percentage_loss:.2f}%",
                            delta=f"{analysis.absolute_loss:.2f} W",
                            delta_color="inverse"
                        )

                    with col4:
                        st.metric(
                            "Performance Retention",
                            f"{analysis.performance_retention:.2f}%"
                        )

                    # Degradation rate
                    st.info(
                        f"📈 Degradation Rate: {analysis.degradation_rate:.4f}% per cycle"
                    )

                    # Pass/Fail determination
                    st.divider()
                    st.subheader("Pass/Fail Determination")

                    pass_fail = st.session_state.handler.determine_pass_fail(
                        analysis,
                        max_power_loss=5.0
                    )

                    if pass_fail['result'] == "PASS":
                        st.success(f"✅ Module {selected_module}: **PASS**")
                    else:
                        st.error(f"❌ Module {selected_module}: **FAIL**")

                    st.write(f"**Justification:** {pass_fail['justification']}")

                except ValueError as e:
                    st.error(f"❌ Error: {e}")

        # Interactive comparison charts
        st.divider()
        st.subheader("Interactive Comparison Charts")

        tab1, tab2, tab3 = st.tabs([
            "Power Degradation Trend",
            "Parameter Evolution",
            "Initial vs Current Comparison"
        ])

        with tab1:
            # Power degradation trend
            trend_data = prepare_degradation_trend_data(
                st.session_state.handler,
                serial_numbers
            )

            fig = go.Figure()

            for sn, data in trend_data['modules'].items():
                fig.add_trace(go.Scatter(
                    x=data['cycle_numbers'],
                    y=data['retention_pct'],
                    mode='lines+markers',
                    name=sn,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))

            # Add acceptance criterion line
            fig.add_hline(
                y=95,
                line_dash="dash",
                line_color="red",
                annotation_text="Min Acceptable (95%)"
            )

            fig.update_layout(
                title="Power Retention vs Cycle Number",
                xaxis_title="Cycle Number",
                yaxis_title="Power Retention (%)",
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            # Parameter evolution
            selected_param = st.selectbox(
                "Select Parameter",
                ["pmax", "voc", "isc", "ff"]
            )

            fig = go.Figure()

            for sn in serial_numbers:
                trend = st.session_state.handler.get_measurement_trend(sn, selected_param)

                if trend:
                    cycles = [t['cycle_number'] for t in trend]
                    values = [t['value'] for t in trend]

                    # Normalize to percentage of initial value
                    if values:
                        initial = values[0]
                        normalized = [(v / initial) * 100 for v in values]

                        fig.add_trace(go.Scatter(
                            x=cycles,
                            y=normalized,
                            mode='lines+markers',
                            name=sn,
                            line=dict(width=3),
                            marker=dict(size=8)
                        ))

            fig.update_layout(
                title=f"{selected_param.upper()} Evolution (Normalized)",
                xaxis_title="Cycle Number",
                yaxis_title="Normalized Value (% of initial)",
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            # Initial vs Current comparison
            comparison_module = st.selectbox("Select Module for Comparison", serial_numbers, key="comp_module")

            if comparison_module:
                cycles = sorted(st.session_state.handler.measurements.keys())

                if len(cycles) >= 2:
                    col1, col2 = st.columns(2)

                    with col1:
                        cycle1 = st.selectbox("Initial Cycle", cycles, index=0)

                    with col2:
                        cycle2 = st.selectbox("Final Cycle", cycles, index=len(cycles)-1)

                    comparison = st.session_state.handler.compare_measurements(
                        comparison_module,
                        cycle1,
                        cycle2
                    )

                    if "error" not in comparison:
                        # Create comparison chart
                        parameters = list(comparison.keys())
                        initial_vals = [comparison[p][f'{p}_cycle_{cycle1}'] for p in parameters]
                        final_vals = [comparison[p][f'{p}_cycle_{cycle2}'] for p in parameters]

                        # Normalize to percentage
                        initial_pct = [100] * len(parameters)
                        final_pct = [(f / i) * 100 if i != 0 else 0
                                    for i, f in zip(initial_vals, final_vals)]

                        fig = go.Figure()

                        fig.add_trace(go.Bar(
                            name=f'Cycle {cycle1}',
                            x=parameters,
                            y=initial_pct,
                            marker_color='lightblue'
                        ))

                        fig.add_trace(go.Bar(
                            name=f'Cycle {cycle2}',
                            x=parameters,
                            y=final_pct,
                            marker_color='darkblue'
                        ))

                        fig.update_layout(
                            title=f"Parameter Comparison: {comparison_module}",
                            xaxis_title="Parameter",
                            yaxis_title="Normalized Value (% of initial)",
                            barmode='group',
                            height=400
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Show detailed comparison table
                        st.markdown("**Detailed Comparison**")
                        comp_df = pd.DataFrame(comparison).T
                        st.dataframe(comp_df, use_container_width=True)
                    else:
                        st.error(comparison["error"])
                else:
                    st.info("Need at least 2 measurement points for comparison")


# ==================== PAGE: DATA MANAGEMENT ====================

elif page == "Data Management":
    st.header("Data Management & Export")

    tab1, tab2 = st.tabs(["Save/Load Data", "Export Reports"])

    with tab1:
        st.subheader("Save Project Data")

        project_name = st.text_input(
            "Project Name",
            placeholder="e.g., TC200_SolarModuleA_2025"
        )

        if st.button("💾 Save Project", type="primary"):
            if project_name:
                filename = f"data/{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                Path("data").mkdir(exist_ok=True)

                st.session_state.handler.save_to_file(filename)
                st.success(f"✅ Project saved to {filename}")
            else:
                st.error("❌ Please enter a project name")

        st.divider()
        st.subheader("Load Project Data")

        uploaded_file = st.file_uploader("Upload project JSON file", type=['json'])

        if uploaded_file:
            if st.button("📂 Load Data"):
                # Save uploaded file temporarily
                temp_path = f"data/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                Path("data").mkdir(exist_ok=True)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                st.session_state.handler.load_from_file(temp_path)
                st.session_state.test_started = True
                st.success("✅ Data loaded successfully!")
                st.rerun()

    with tab2:
        st.subheader("Export Test Reports")

        export_format = st.radio("Select Format", ["Excel", "PDF", "JSON"])

        col1, col2 = st.columns(2)

        with col1:
            include_charts = st.checkbox("Include Charts", value=True)
            include_raw_data = st.checkbox("Include Raw Cycle Data", value=False)

        with col2:
            include_measurements = st.checkbox("Include All Measurements", value=True)
            include_analysis = st.checkbox("Include Analysis Results", value=True)

        if st.button("📥 Generate Report", type="primary"):
            if export_format == "JSON":
                # Export to JSON
                data = st.session_state.handler.export_to_dict()
                json_str = json.dumps(data, indent=2)

                st.download_button(
                    label="Download JSON Report",
                    data=json_str,
                    file_name=f"thermal_cycling_report_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.info(f"📄 {export_format} export functionality will generate comprehensive report with selected sections.")

        st.divider()
        st.subheader("Quick Data Export")

        # Export cycle data
        if st.session_state.handler.cycle_data:
            cycle_df = pd.DataFrame([
                {
                    "Cycle": cd.cycle_number,
                    "Timestamp": cd.timestamp.isoformat(),
                    "Chamber Temp (°C)": cd.chamber_temp,
                    "Humidity (%)": cd.humidity,
                    "Phase": cd.cycle_phase
                }
                for cd in st.session_state.handler.cycle_data
            ])

            csv_cycle = cycle_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Cycle Data (CSV)",
                data=csv_cycle,
                file_name=f"cycle_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
