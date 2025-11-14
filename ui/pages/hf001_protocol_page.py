"""HF-001 Protocol Execution Page

Interactive Streamlit page for running HF-001 Humidity Freeze tests.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd

from protocols.environmental.hf_001 import HumidityFreezeProtocol
from ui.components.hf001_visualizations import (
    plot_cycle_profile,
    plot_all_cycles_overview,
    plot_iv_curve_comparison,
    plot_degradation_metrics,
    create_qr_code_display,
    display_cycle_progress
)


def render_hf001_page():
    """Render HF-001 protocol execution page"""

    st.set_page_config(
        page_title="HF-001 Humidity Freeze Test",
        page_icon="❄️",
        layout="wide"
    )

    st.title("❄️ HF-001 - Humidity Freeze Test Protocol")
    st.markdown("**IEC 61215 MQT 12** | Environmental Testing")

    # Initialize protocol
    if 'protocol' not in st.session_state:
        st.session_state.protocol = HumidityFreezeProtocol()
        st.session_state.test_started = False
        st.session_state.test_completed = False

    protocol = st.session_state.protocol

    # Sidebar - Test Configuration
    with st.sidebar:
        st.header("⚙️ Test Configuration")

        # Module information
        st.subheader("Module Information")
        module_serial = st.text_input(
            "Module Serial Number *",
            value="PV-TEST-001",
            help="Enter unique module serial number"
        )

        module_manufacturer = st.text_input(
            "Manufacturer",
            value="SolarTech Inc."
        )

        module_model = st.text_input(
            "Model",
            value="ST-300-60"
        )

        # Operator information
        st.subheader("Operator Information")
        operator_id = st.text_input(
            "Operator ID *",
            value="OP001",
            help="Enter operator identification"
        )

        # Equipment selection
        st.subheader("Equipment")
        chamber_id = st.selectbox(
            "Environmental Chamber",
            ["CHAMBER-01", "CHAMBER-02", "CHAMBER-03"],
            help="Select calibrated environmental chamber"
        )

        iv_tracer_id = st.selectbox(
            "I-V Curve Tracer",
            ["IV-TRACER-01", "IV-TRACER-02"]
        )

        # Test parameters (from template, can be overridden)
        st.subheader("Test Parameters")
        num_cycles = st.number_input(
            "Number of Cycles",
            min_value=1,
            max_value=20,
            value=protocol.get_parameter('total_cycles')['value'],
            help="Standard: 10 cycles"
        )

        # Start test button
        st.divider()
        if not st.session_state.test_started:
            if st.button("▶️ Start Test", type="primary", use_container_width=True):
                if module_serial and operator_id:
                    st.session_state.test_started = True
                    st.session_state.start_time = datetime.now()
                    st.rerun()
                else:
                    st.error("Please fill all required fields (*)")
        else:
            st.success(f"Test Running...")
            if st.button("⏹️ Abort Test", type="secondary"):
                st.session_state.test_started = False
                st.session_state.test_completed = False
                st.rerun()

    # Main content area
    if not st.session_state.test_started:
        # Pre-test information display
        render_protocol_info(protocol)

    else:
        # Test execution interface
        render_test_execution(
            protocol,
            module_serial,
            operator_id,
            num_cycles
        )


def render_protocol_info(protocol):
    """Render protocol information before test starts"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Overview",
        "🔬 Equipment",
        "📝 Test Steps",
        "✅ QC Criteria"
    ])

    with tab1:
        st.header("Protocol Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Protocol ID", protocol.metadata.protocol_id)
            st.metric("Version", protocol.metadata.version)

        with col2:
            st.metric("Standard", protocol.metadata.standard)
            st.metric("Category", protocol.metadata.category)

        with col3:
            st.metric("Total Cycles", protocol.get_parameter('total_cycles')['value'])
            st.metric("Test Duration", "~60 hours")

        st.divider()

        st.subheader("Description")
        st.write(protocol.metadata.description)

        st.subheader("Test Parameters")
        params = protocol.template['parameters']

        params_df = pd.DataFrame([
            {
                'Parameter': key,
                'Value': f"{val['value']} {val['unit']}",
                'Description': val['description']
            }
            for key, val in params.items()
            if 'value' in val
        ])

        st.dataframe(params_df, use_container_width=True, hide_index=True)

    with tab2:
        st.header("Required Equipment")

        equipment = protocol.template['equipment']

        for eq_name, specs in equipment.items():
            with st.expander(f"{'✓' if specs['required'] else '○'} {eq_name.replace('_', ' ').title()}", expanded=specs['required']):
                st.write(f"**Required:** {'Yes' if specs['required'] else 'No'}")

                if 'specifications' in specs:
                    st.write("**Specifications:**")
                    for spec_name, spec_val in specs['specifications'].items():
                        st.write(f"- {spec_name.replace('_', ' ').title()}: {spec_val}")

                if specs.get('calibration_required'):
                    st.warning(f"⚠️ Calibration required every {specs.get('calibration_interval', 'N/A')}")

    with tab3:
        st.header("Test Steps")

        for step in protocol.get_test_steps():
            with st.expander(f"Step {step['step']}: {step['name']}", expanded=False):
                st.write(f"**Description:** {step['description']}")

                if 'actions' in step:
                    st.write("**Actions:**")
                    for action in step['actions']:
                        st.write(f"- {action}")

                if 'measurements' in step:
                    st.write("**Measurements:**")
                    st.write(", ".join(step['measurements']))

    with tab4:
        st.header("QC Pass/Fail Criteria")

        qc = protocol.get_qc_criteria()

        # Power degradation
        st.subheader("🔋 Power Degradation")
        st.error(f"**CRITICAL:** Maximum allowed degradation: {qc['power_degradation']['limit']}%")
        st.write(qc['power_degradation']['requirement'])

        # Insulation resistance
        st.subheader("⚡ Insulation Resistance")
        st.error(f"**CRITICAL:** Minimum resistance: {qc['insulation_resistance']['final_min']} MΩ")
        st.write(qc['insulation_resistance']['requirement'])

        # Visual defects
        st.subheader("👁️ Visual Inspection")
        st.write("**Major Defects (FAIL):**")
        for defect, criteria in qc['visual_defects']['major_defects'].items():
            st.write(f"- {defect.replace('_', ' ').title()}: {criteria['description']}")

        st.write("**Minor Defects (WARNING):**")
        for defect, criteria in qc['visual_defects']['minor_defects'].items():
            st.write(f"- {defect.replace('_', ' ').title()}: {criteria['description']}")


def render_test_execution(protocol, module_serial, operator_id, num_cycles):
    """Render test execution interface"""

    st.header("🔬 Test Execution")

    # Progress indicator
    st.subheader("Test Progress")

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
        st.session_state.current_cycle = 0

    # Simplified execution for demo - in real implementation, this would be event-driven
    if st.button("▶️ Execute Test (Demo)", type="primary"):
        with st.spinner("Executing test protocol..."):
            # Run the test
            result = protocol.run_test(
                sample_id=module_serial,
                operator_id=operator_id
            )

            st.session_state.test_result = result
            st.session_state.test_completed = True
            st.rerun()

    # Display results if test is completed
    if st.session_state.get('test_completed', False):
        render_test_results(protocol)


def render_test_results(protocol):
    """Render test results and analysis"""

    st.success("✅ Test Completed!")

    test_data = protocol.test_data
    analysis = protocol.analyze_results(st.session_state.test_result)

    # Summary metrics
    st.header("📊 Test Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_color = "normal" if analysis['pass_fail'] else "inverse"
        st.metric(
            "Result",
            "PASS ✅" if analysis['pass_fail'] else "FAIL ❌"
        )

    with col2:
        st.metric(
            "Power Degradation",
            f"{analysis['power_degradation']:.2f}%",
            delta=f"{analysis['power_degradation'] - 5:.2f}% vs limit",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "Cycles Completed",
            f"{analysis['cycles_completed']}/10"
        )

    with col4:
        st.metric(
            "Test Duration",
            f"{analysis['test_duration_hours']:.1f} hrs"
        )

    # Tabs for detailed results
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Performance Analysis",
        "🌡️ Cycle Data",
        "👁️ Visual Inspection",
        "📄 Report & QR Code"
    ])

    with tab1:
        st.subheader("I-V Curve Comparison")

        if test_data.initial_iv_curve and test_data.final_iv_curve:
            fig = plot_iv_curve_comparison(
                test_data.initial_iv_curve.model_dump(),
                test_data.final_iv_curve.model_dump()
            )
            st.plotly_chart(fig, use_container_width=True)

            # Degradation metrics
            st.subheader("Degradation Metrics")
            fig_deg = plot_degradation_metrics(analysis)
            st.plotly_chart(fig_deg, use_container_width=True)

            # Detailed comparison table
            st.subheader("Detailed Comparison")

            comparison_df = pd.DataFrame({
                'Parameter': ['Pmax (W)', 'Voc (V)', 'Isc (A)', 'FF', 'Insulation (MΩ)'],
                'Initial': [
                    f"{test_data.initial_iv_curve.Pmax:.2f}",
                    f"{test_data.initial_iv_curve.Voc:.2f}",
                    f"{test_data.initial_iv_curve.Isc:.2f}",
                    f"{test_data.initial_iv_curve.FF:.3f}",
                    f"{test_data.initial_insulation_resistance:.1f}"
                ],
                'Final': [
                    f"{test_data.final_iv_curve.Pmax:.2f}",
                    f"{test_data.final_iv_curve.Voc:.2f}",
                    f"{test_data.final_iv_curve.Isc:.2f}",
                    f"{test_data.final_iv_curve.FF:.3f}",
                    f"{test_data.final_insulation_resistance:.1f}"
                ],
                'Change (%)': [
                    f"{((test_data.initial_iv_curve.Pmax - test_data.final_iv_curve.Pmax) / test_data.initial_iv_curve.Pmax * 100):.2f}",
                    f"{((test_data.initial_iv_curve.Voc - test_data.final_iv_curve.Voc) / test_data.initial_iv_curve.Voc * 100):.2f}",
                    f"{((test_data.initial_iv_curve.Isc - test_data.final_iv_curve.Isc) / test_data.initial_iv_curve.Isc * 100):.2f}",
                    f"{((test_data.initial_iv_curve.FF - test_data.final_iv_curve.FF) / test_data.initial_iv_curve.FF * 100):.2f}",
                    "N/A"
                ]
            })

            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Temperature & Humidity Cycles")

        if test_data.cycles:
            # All cycles overview
            cycles_for_plot = [
                {
                    'cycle_number': c.cycle_number,
                    'temperature_log': c.temperature_log
                }
                for c in test_data.cycles
            ]

            fig_overview = plot_all_cycles_overview(cycles_for_plot)
            st.plotly_chart(fig_overview, use_container_width=True)

            # Individual cycle selector
            st.subheader("Individual Cycle Details")
            selected_cycle = st.selectbox(
                "Select Cycle",
                range(1, len(test_data.cycles) + 1)
            )

            cycle_data = test_data.cycles[selected_cycle - 1]

            fig_cycle = plot_cycle_profile(
                cycle_data.cycle_number,
                cycle_data.temperature_log,
                cycle_data.humidity_log
            )
            st.plotly_chart(fig_cycle, use_container_width=True)

            # Cycle statistics
            col1, col2, col3 = st.columns(3)

            temps = [t[1] for t in cycle_data.temperature_log]
            humids = [h[1] for h in cycle_data.humidity_log] if cycle_data.humidity_log else []

            with col1:
                st.metric("Temp Min", f"{min(temps):.1f}°C")
                st.metric("Temp Max", f"{max(temps):.1f}°C")

            with col2:
                if humids:
                    st.metric("Humidity Min", f"{min(humids):.1f}%")
                    st.metric("Humidity Max", f"{max(humids):.1f}%")

            with col3:
                st.metric("Duration", f"{(cycle_data.end_time - cycle_data.start_time).total_seconds() / 3600:.1f} hrs")
                st.metric("Status", cycle_data.status.upper())

    with tab3:
        st.subheader("Visual Inspection Results")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Initial Inspection**")
            for key, value in test_data.initial_visual_inspection.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value}")

        with col2:
            st.write("**Final Inspection**")
            for key, value in test_data.final_visual_inspection.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value}")

        if analysis.get('failure_modes'):
            st.error("**Failure Modes Detected:**")
            for mode in analysis['failure_modes']:
                st.write(f"- {mode}")

    with tab4:
        st.subheader("Traceability & Reporting")

        # QR Code
        qr_content = protocol.generate_qr_code()
        create_qr_code_display(qr_content)

        # Export options
        st.subheader("Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export Cycle Data (CSV)"):
                try:
                    output_path = Path("./reports")
                    output_path.mkdir(exist_ok=True)
                    csv_file = protocol.export_cycle_data(output_path)
                    st.success(f"Exported to: {csv_file}")
                except Exception as e:
                    st.error(f"Export failed: {e}")

        with col2:
            if st.button("📄 Generate PDF Report"):
                st.info("PDF report generation - implement with WeasyPrint")

        with col3:
            if st.button("💾 Save to Database"):
                st.info("Database save - implement with SQLAlchemy session")

        # Test metadata
        st.subheader("Test Metadata")
        metadata = {
            'Test ID': test_data.test_id,
            'Module Serial': test_data.module_serial,
            'Operator': test_data.operator_id,
            'Start Time': test_data.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'End Time': test_data.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Protocol': f"{protocol.metadata.protocol_id} v{protocol.metadata.version}",
            'Standard': protocol.metadata.standard
        }

        st.json(metadata)


if __name__ == "__main__":
    render_hf001_page()
