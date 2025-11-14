"""Snow Load Test UI Component

Streamlit UI for executing and monitoring Snow Load tests (SNOW-001).
"""

import streamlit as st
from datetime import datetime
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.mechanical.snow_load import (
    SnowLoadTestProtocol,
    SnowLoadTestConfig,
    ModuleSpecs
)
from protocols.mechanical.snow_load.analysis import (
    SnowLoadAnalyzer,
    plot_load_deflection_curve
)


def render_snow_load_test():
    """Render the Snow Load test interface"""

    st.markdown('<div class="main-header">SNOW-001: Snow Load Test</div>', unsafe_allow_html=True)

    st.markdown("""
    **Standard**: IEC 61215-1:2016, Part 1 - Mechanical Load Test
    **Category**: Mechanical Testing
    **Protocol Version**: 1.0.0
    """)

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Setup",
        "▶️ Execute",
        "📊 Results",
        "📄 Report"
    ])

    with tab1:
        render_setup_tab()

    with tab2:
        render_execute_tab()

    with tab3:
        render_results_tab()

    with tab4:
        render_report_tab()


def render_setup_tab():
    """Render test setup tab"""
    st.markdown('<div class="sub-header">Test Setup</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Module Specifications")

        module_id = st.text_input(
            "Module ID *",
            value="TEST-MOD-001",
            help="Unique module identifier"
        )

        manufacturer = st.text_input(
            "Manufacturer",
            value="Test Manufacturer",
            help="Module manufacturer name"
        )

        model = st.text_input(
            "Model",
            value="TEST-100W",
            help="Module model number"
        )

        serial_number = st.text_input(
            "Serial Number",
            help="Module serial number"
        )

        st.markdown("#### Dimensions")
        col_l, col_w, col_t = st.columns(3)

        with col_l:
            length_mm = st.number_input(
                "Length (mm) *",
                min_value=100.0,
                max_value=3000.0,
                value=1650.0,
                step=10.0
            )

        with col_w:
            width_mm = st.number_input(
                "Width (mm) *",
                min_value=100.0,
                max_value=2000.0,
                value=992.0,
                step=10.0
            )

        with col_t:
            thickness_mm = st.number_input(
                "Thickness (mm) *",
                min_value=1.0,
                max_value=100.0,
                value=35.0,
                step=1.0
            )

        mass_kg = st.number_input(
            "Mass (kg) *",
            min_value=1.0,
            max_value=50.0,
            value=18.5,
            step=0.1
        )

        frame_type = st.selectbox(
            "Frame Type",
            ["aluminum", "stainless_steel", "plastic", "frameless"],
            index=0
        )

        rated_power_w = st.number_input(
            "Rated Power (W)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=10.0
        )

    with col2:
        st.markdown("### Test Configuration")

        snow_load_pa = st.number_input(
            "Snow Load (Pa) *",
            min_value=100.0,
            max_value=10000.0,
            value=2400.0,
            step=100.0,
            help="Target snow load in Pascals (2400 Pa ≈ 245 kg/m²)"
        )

        st.info(f"≈ {snow_load_pa * 0.102:.1f} kg/m²")

        hold_duration_hours = st.number_input(
            "Hold Duration (hours) *",
            min_value=0.5,
            max_value=48.0,
            value=1.0,
            step=0.5
        )

        cycles = st.number_input(
            "Number of Cycles *",
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )

        test_temperature_c = st.number_input(
            "Test Temperature (°C)",
            min_value=-70.0,
            max_value=60.0,
            value=23.0,
            step=1.0
        )

        test_humidity_pct = st.number_input(
            "Test Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=5.0
        )

        load_application_rate = st.number_input(
            "Load Application Rate (kg/m²/min)",
            min_value=1.0,
            max_value=50.0,
            value=10.0,
            step=1.0
        )

        support_configuration = st.selectbox(
            "Support Configuration",
            ["4-point", "frame", "distributed"],
            index=0
        )

        st.markdown("### Acceptance Criteria")

        max_deflection_mm = st.number_input(
            "Max Deflection (mm) *",
            min_value=1.0,
            max_value=200.0,
            value=50.0,
            step=1.0
        )

        max_permanent_deflection_mm = st.number_input(
            "Max Permanent Deflection (mm) *",
            min_value=0.1,
            max_value=50.0,
            value=5.0,
            step=0.1
        )

        max_cracking = st.selectbox(
            "Max Cracking Level",
            ["none", "micro", "hairline", "visible"],
            index=0
        )

        min_performance_retention_pct = st.number_input(
            "Min Performance Retention (%)",
            min_value=80.0,
            max_value=100.0,
            value=95.0,
            step=0.5
        )

        visual_inspection_required = st.checkbox(
            "Visual Inspection Required",
            value=True
        )

        electrical_test_required = st.checkbox(
            "Electrical Test Required",
            value=False
        )

    # Save configuration to session state
    if st.button("💾 Save Configuration", type="primary"):
        try:
            module_specs = ModuleSpecs(
                module_id=module_id,
                length_mm=length_mm,
                width_mm=width_mm,
                thickness_mm=thickness_mm,
                mass_kg=mass_kg,
                manufacturer=manufacturer if manufacturer else None,
                model=model if model else None,
                serial_number=serial_number if serial_number else None,
                frame_type=frame_type,
                rated_power_w=rated_power_w if rated_power_w else None
            )

            test_config = SnowLoadTestConfig(
                snow_load_pa=snow_load_pa,
                hold_duration_hours=hold_duration_hours,
                cycles=cycles,
                test_temperature_c=test_temperature_c,
                test_humidity_pct=test_humidity_pct,
                load_application_rate=load_application_rate,
                support_configuration=support_configuration,
                max_deflection_mm=max_deflection_mm,
                max_permanent_deflection_mm=max_permanent_deflection_mm,
                max_cracking=max_cracking,
                min_performance_retention_pct=min_performance_retention_pct,
                visual_inspection_required=visual_inspection_required,
                electrical_test_required=electrical_test_required
            )

            # Validate
            module_specs.validate()
            test_config.validate()

            # Save to session state
            st.session_state['module_specs'] = module_specs
            st.session_state['test_config'] = test_config

            st.success("✅ Configuration saved successfully!")

        except Exception as e:
            st.error(f"❌ Configuration error: {str(e)}")


def render_execute_tab():
    """Render test execution tab"""
    st.markdown('<div class="sub-header">Test Execution</div>', unsafe_allow_html=True)

    # Check if configuration is saved
    if 'module_specs' not in st.session_state or 'test_config' not in st.session_state:
        st.warning("⚠️ Please configure the test in the Setup tab first.")
        return

    module_specs = st.session_state['module_specs']
    test_config = st.session_state['test_config']

    # Display current configuration
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Module")
        st.write(f"**ID**: {module_specs.module_id}")
        st.write(f"**Size**: {module_specs.length_mm} × {module_specs.width_mm} × {module_specs.thickness_mm} mm")
        st.write(f"**Mass**: {module_specs.mass_kg} kg")
        st.write(f"**Area**: {module_specs.area_m2:.2f} m²")

    with col2:
        st.markdown("#### Test Parameters")
        st.write(f"**Load**: {test_config.snow_load_pa} Pa ({test_config.snow_load_kg_m2:.1f} kg/m²)")
        st.write(f"**Duration**: {test_config.hold_duration_hours} hours")
        st.write(f"**Cycles**: {test_config.cycles}")
        st.write(f"**Temperature**: {test_config.test_temperature_c}°C")

    st.markdown("---")

    # Pre-test checklist
    st.markdown("### Pre-Test Checklist")

    checklist_items = [
        "Module is properly mounted on test frame",
        "Deflection sensors are calibrated and positioned",
        "Load application system is ready",
        "Data acquisition system is connected",
        "Safety equipment is in place",
        "Test area is clear"
    ]

    all_checked = True
    for item in checklist_items:
        checked = st.checkbox(item, key=f"check_{item}")
        all_checked = all_checked and checked

    st.markdown("---")

    # Execute button
    if st.button("▶️ Start Test", type="primary", disabled=not all_checked):
        if not all_checked:
            st.error("❌ Please complete all checklist items before starting the test.")
        else:
            execute_test(module_specs, test_config)


def execute_test(module_specs: ModuleSpecs, test_config: SnowLoadTestConfig):
    """Execute the snow load test"""

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Initialize protocol
        protocol = SnowLoadTestProtocol(test_config, module_specs)

        # Execute test
        status_text.text("🔄 Executing test...")
        result = protocol.execute()

        progress_bar.progress(100)

        # Save results to session state
        st.session_state['test_result'] = result
        st.session_state['protocol'] = protocol
        st.session_state['test_executed'] = True

        # Show results
        if result:
            st.success("✅ Test PASSED!")
        else:
            st.error("❌ Test FAILED!")

        st.info("📊 View detailed results in the Results tab.")

    except Exception as e:
        st.error(f"❌ Test execution error: {str(e)}")
        progress_bar.progress(0)


def render_results_tab():
    """Render results tab"""
    st.markdown('<div class="sub-header">Test Results</div>', unsafe_allow_html=True)

    if 'test_executed' not in st.session_state or not st.session_state['test_executed']:
        st.info("ℹ️ No test results available. Please execute a test first.")
        return

    protocol = st.session_state['protocol']
    test_result = st.session_state['test_result']

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    max_deflection = max((m.deflection_mm for m in protocol.measurements), default=0)
    permanent_deflection = (
        protocol.measurements[-1].deflection_mm - protocol.baseline_deflection
        if protocol.measurements else 0
    )

    with col1:
        st.metric(
            "Test Result",
            "PASS" if test_result else "FAIL",
            delta=None
        )

    with col2:
        st.metric(
            "Max Deflection",
            f"{max_deflection:.2f} mm",
            delta=f"Limit: {protocol.config.max_deflection_mm:.1f} mm"
        )

    with col3:
        st.metric(
            "Permanent Deflection",
            f"{permanent_deflection:.2f} mm",
            delta=f"Limit: {protocol.config.max_permanent_deflection_mm:.1f} mm"
        )

    with col4:
        st.metric(
            "Measurements",
            len(protocol.measurements),
            delta=None
        )

    st.markdown("---")

    # Detailed results
    st.markdown("### Measurement Data")

    # Convert measurements to display format
    measurements_data = []
    for m in protocol.measurements:
        measurements_data.append({
            "Timestamp": m.timestamp.strftime("%H:%M:%S"),
            "Phase": m.phase.value,
            "Load (Pa)": f"{m.load_applied_pa:.1f}",
            "Load (kg/m²)": f"{m.load_applied_pa * 0.102:.1f}",
            "Deflection (mm)": f"{m.deflection_mm:.2f}",
            "Temperature (°C)": f"{m.temperature_c:.1f}" if m.temperature_c else "N/A",
            "Visual": m.visual_condition.value
        })

    st.dataframe(measurements_data, use_container_width=True)

    # Analysis
    st.markdown("### Analysis")

    analyzer = SnowLoadAnalyzer(
        [m.to_dict() for m in protocol.measurements],
        baseline_deflection=protocol.baseline_deflection
    )
    analysis_results = analyzer.analyze()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Key Metrics")
        st.write(f"**Elastic Recovery**: {analysis_results.elastic_recovery_pct:.1f}%")
        if analysis_results.stiffness_n_mm:
            st.write(f"**Stiffness**: {analysis_results.stiffness_n_mm:.1f} Pa/mm")
        if analysis_results.failure_mode:
            st.write(f"**Failure Mode**: {analysis_results.failure_mode}")

    with col2:
        st.markdown("#### Test Steps")
        for step in protocol.steps:
            status_icon = "✅" if step.result and step.result.success else "❌"
            st.write(f"{status_icon} {step.name} ({step.duration_seconds:.1f}s)")


def render_report_tab():
    """Render report tab"""
    st.markdown('<div class="sub-header">Test Report</div>', unsafe_allow_html=True)

    if 'test_executed' not in st.session_state or not st.session_state['test_executed']:
        st.info("ℹ️ No test results available. Please execute a test first.")
        return

    protocol = st.session_state['protocol']

    # Generate report data
    report_data = protocol.get_report_data()

    st.markdown("### Report Summary")

    # Display report
    st.json(report_data)

    # Download buttons
    col1, col2 = st.columns(2)

    with col1:
        # Download JSON
        json_str = json.dumps(report_data, indent=2)
        st.download_button(
            label="📥 Download JSON Report",
            data=json_str,
            file_name=f"snow_load_test_{report_data['module_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    with col2:
        # Download CSV (measurements)
        import io
        csv_buffer = io.StringIO()
        csv_buffer.write("Timestamp,Phase,Load_Pa,Load_kg_m2,Deflection_mm,Temperature_C,Visual_Condition\n")
        for m in report_data['measurements']:
            csv_buffer.write(
                f"{m['timestamp']},{m['phase']},{m['load_applied_pa']},{m['load_applied_kg_m2']},"
                f"{m['deflection_mm']},{m['temperature_c']},{m['visual_condition']}\n"
            )

        st.download_button(
            label="📥 Download CSV Data",
            data=csv_buffer.getvalue(),
            file_name=f"snow_load_data_{report_data['module_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
