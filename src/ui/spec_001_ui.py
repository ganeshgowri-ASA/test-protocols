"""
Streamlit UI for SPEC-001 Spectral Response Test
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..protocols import Protocol, SpectralResponseTest


def render_spec_001_ui():
    """
    Render the SPEC-001 Spectral Response Test UI
    """
    st.title("🌈 SPEC-001: Spectral Response Test")
    st.markdown("*IEC 60904-8 Standard*")

    # Load protocol
    protocol_path = Path(__file__).parent.parent.parent / "protocols" / "SPEC-001.json"
    protocol = Protocol(str(protocol_path))

    # Display protocol information
    with st.expander("ℹ️ Protocol Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Protocol ID", protocol.protocol_id)
            st.metric("Version", protocol.version)
        with col2:
            st.metric("Standard", protocol.standard)
            st.metric("Category", protocol.protocol_data.get("category"))

        st.markdown("**Description:**")
        st.info(protocol.protocol_data.get("description"))

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 Test Setup",
        "▶️ Run Test",
        "📊 Results",
        "📋 Reports"
    ])

    # Tab 1: Test Setup
    with tab1:
        render_test_setup(protocol)

    # Tab 2: Run Test
    with tab2:
        render_test_execution(protocol)

    # Tab 3: Results
    with tab3:
        render_results_viewer()

    # Tab 4: Reports
    with tab4:
        render_reports()


def render_test_setup(protocol: Protocol):
    """Render test setup interface"""
    st.header("Test Configuration")

    # Sample Information
    st.subheader("1. Sample Information")
    col1, col2 = st.columns(2)

    with col1:
        sample_id = st.text_input(
            "Sample ID *",
            help="Unique identifier for the sample",
            placeholder="e.g., SAMPLE-001"
        )
        sample_type = st.selectbox(
            "Sample Type *",
            options=["Solar Cell", "Solar Module", "Photodetector", "Other"]
        )

    with col2:
        technology = st.selectbox(
            "Technology Type *",
            options=["c-Si", "mc-Si", "CdTe", "CIGS", "Perovskite", "GaAs", "Organic", "Other"]
        )
        area = st.number_input(
            "Active Area (cm²) *",
            min_value=0.01,
            max_value=10000.0,
            value=1.0,
            step=0.1,
            format="%.2f"
        )

    # Test Parameters
    st.subheader("2. Test Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        wavelength_start = st.number_input(
            "Wavelength Start (nm)",
            min_value=300,
            max_value=1200,
            value=300,
            step=10
        )
        wavelength_end = st.number_input(
            "Wavelength End (nm)",
            min_value=300,
            max_value=1200,
            value=1200,
            step=10
        )
        step_size = st.number_input(
            "Step Size (nm)",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )

    with col2:
        temperature = st.number_input(
            "Temperature (°C)",
            min_value=-40,
            max_value=85,
            value=25,
            step=1
        )
        bias_voltage = st.number_input(
            "Bias Voltage (V)",
            min_value=-10.0,
            max_value=10.0,
            value=0.0,
            step=0.1,
            format="%.2f"
        )

    with col3:
        bias_light = st.number_input(
            "Bias Light Intensity (W/m²)",
            min_value=0,
            max_value=1000,
            value=0,
            step=10
        )
        integration_time = st.number_input(
            "Integration Time (ms)",
            min_value=10,
            max_value=10000,
            value=100,
            step=10
        )
        averaging = st.number_input(
            "Number of Averages",
            min_value=1,
            max_value=100,
            value=3,
            step=1
        )

    # Equipment Selection
    st.subheader("3. Equipment")
    equipment_list = protocol.get_equipment()

    for equipment in equipment_list:
        with st.expander(f"{equipment['name']} {'(Required)' if equipment['required'] else '(Optional)'}"):
            st.json(equipment['specifications'])

    # Operator Information
    st.subheader("4. Operator Information")
    operator = st.text_input("Operator Name", placeholder="Your name")
    notes = st.text_area("Test Notes", placeholder="Optional notes about this test...")

    # Save configuration
    if st.button("💾 Save Configuration", type="primary"):
        config = {
            "sample_info": {
                "sample_id": sample_id,
                "sample_type": sample_type,
                "technology": technology,
                "area": area
            },
            "test_parameters": {
                "wavelength": {
                    "start": wavelength_start,
                    "end": wavelength_end,
                    "step_size": step_size
                },
                "temperature": temperature,
                "bias_voltage": bias_voltage,
                "bias_light_intensity": bias_light,
                "integration_time": integration_time,
                "averaging": averaging
            },
            "operator": operator,
            "notes": notes
        }

        st.session_state["test_config"] = config
        st.success("✅ Configuration saved! Go to 'Run Test' tab to execute.")


def render_test_execution(protocol: Protocol):
    """Render test execution interface"""
    st.header("Execute Spectral Response Test")

    if "test_config" not in st.session_state:
        st.warning("⚠️ Please configure the test in the 'Test Setup' tab first.")
        return

    config = st.session_state["test_config"]

    # Display configuration summary
    st.subheader("Test Configuration Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Sample:** {config['sample_info']['sample_id']}")
        st.info(f"**Technology:** {config['sample_info']['technology']}")
        st.info(f"**Area:** {config['sample_info']['area']} cm²")

    with col2:
        st.info(f"**Wavelength Range:** {config['test_parameters']['wavelength']['start']}-{config['test_parameters']['wavelength']['end']} nm")
        st.info(f"**Temperature:** {config['test_parameters']['temperature']} °C")
        st.info(f"**Operator:** {config.get('operator', 'Not specified')}")

    # Pre-test checklist
    st.subheader("Pre-Test Checklist")
    checklist = st.empty()

    with checklist.container():
        check1 = st.checkbox("✓ Equipment is warmed up (30 min minimum)")
        check2 = st.checkbox("✓ Reference detector is calibrated")
        check3 = st.checkbox("✓ Sample is properly mounted and aligned")
        check4 = st.checkbox("✓ Temperature is stabilized")
        check5 = st.checkbox("✓ Monochromator is initialized")

    all_checked = all([check1, check2, check3, check4, check5])

    # Run test button
    col1, col2 = st.columns([1, 3])
    with col1:
        run_test = st.button(
            "▶️ Run Test",
            type="primary",
            disabled=not all_checked,
            help="Complete the checklist to enable"
        )

    if run_test:
        # Initialize test
        test = SpectralResponseTest(protocol=protocol)

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Initialize test
        status_text.text("Initializing test...")
        progress_bar.progress(10)

        test_id = test.initialize(
            test_params=config["test_parameters"],
            sample_info=config["sample_info"]
        )

        # Run measurement
        status_text.text("Running spectral response measurement...")
        progress_bar.progress(30)

        results = test.run()
        progress_bar.progress(60)

        # Analyze results
        status_text.text("Analyzing data...")
        test.analyze()
        progress_bar.progress(80)

        # Run QC
        status_text.text("Running quality control checks...")
        qc_results = test.run_qc()
        progress_bar.progress(90)

        # Export results
        status_text.text("Exporting results...")
        exported_files = test.export_results()
        progress_bar.progress(100)

        # Complete
        test.complete()
        status_text.text("✅ Test completed!")

        # Store results in session state
        st.session_state["current_test"] = {
            "test_id": test_id,
            "test": test,
            "results": results,
            "qc_results": qc_results,
            "exported_files": exported_files
        }

        st.success(f"Test completed successfully! Test ID: {test_id}")
        st.balloons()

        # Show quick summary
        st.subheader("Quick Results Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak EQE", f"{test.results['peak_eqe']:.1f}%")
        with col2:
            st.metric("Peak Wavelength", f"{test.results['peak_wavelength']:.0f} nm")
        with col3:
            st.metric("Integrated Jsc", f"{test.results['integrated_jsc']:.2f} mA/cm²")

        st.info("📊 View detailed results in the 'Results' tab")


def render_results_viewer():
    """Render results viewer interface"""
    st.header("Test Results")

    if "current_test" not in st.session_state:
        st.info("No test results available. Run a test first.")
        return

    test_data = st.session_state["current_test"]
    test = test_data["test"]

    # Results summary
    st.subheader("📈 Results Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Test ID", test_data["test_id"])
    with col2:
        st.metric("Peak EQE", f"{test.results['peak_eqe']:.1f}%")
    with col3:
        st.metric("Peak λ", f"{test.results['peak_wavelength']:.0f} nm")
    with col4:
        st.metric("Integrated Jsc", f"{test.results['integrated_jsc']:.2f} mA/cm²")

    # QC Results
    st.subheader("✅ Quality Control")
    qc_results = test_data["qc_results"]

    qc_cols = st.columns(len(qc_results))
    for i, (check_name, result) in enumerate(qc_results.items()):
        with qc_cols[i]:
            status = "✅" if result["passed"] else "❌"
            st.metric(
                f"{status} {check_name.replace('_', ' ').title()}",
                f"{result['value']:.3f} {result.get('unit', '')}",
                delta=f"Threshold: {result['threshold']}"
            )

    # Interactive Plots
    st.subheader("📊 Interactive Plots")

    # Plot 1: Spectral Response
    fig_sr = go.Figure()
    fig_sr.add_trace(go.Scatter(
        x=test.calculated_data["wavelength"],
        y=test.calculated_data["spectral_response"],
        mode='lines',
        name='Spectral Response',
        line=dict(color='blue', width=2)
    ))
    fig_sr.update_layout(
        title="Spectral Response vs Wavelength",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Spectral Response (A/W)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_sr, use_container_width=True)

    # Plot 2: External Quantum Efficiency
    fig_eqe = go.Figure()
    fig_eqe.add_trace(go.Scatter(
        x=test.calculated_data["wavelength"],
        y=test.calculated_data["external_quantum_efficiency"],
        mode='lines',
        name='EQE',
        line=dict(color='red', width=2)
    ))
    fig_eqe.add_hline(
        y=test.results['peak_eqe'],
        line_dash="dash",
        line_color="green",
        annotation_text=f"Peak: {test.results['peak_eqe']:.1f}%"
    )
    fig_eqe.update_layout(
        title="External Quantum Efficiency vs Wavelength",
        xaxis_title="Wavelength (nm)",
        yaxis_title="EQE (%)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_eqe, use_container_width=True)

    # Data Table
    st.subheader("📋 Data Table")
    st.dataframe(test.calculated_data, use_container_width=True)

    # Download buttons
    st.subheader("💾 Download Data")
    col1, col2, col3 = st.columns(3)

    with col1:
        csv_data = test.calculated_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{test_data['test_id']}_data.csv",
            mime="text/csv"
        )

    with col2:
        json_data = json.dumps(test.results, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{test_data['test_id']}_results.json",
            mime="application/json"
        )


def render_reports():
    """Render reports interface"""
    st.header("Test Reports")

    if "current_test" not in st.session_state:
        st.info("No test results available. Run a test first.")
        return

    test_data = st.session_state["current_test"]
    test = test_data["test"]

    st.subheader("📄 Test Report")

    # Report header
    st.markdown(f"### Test ID: {test_data['test_id']}")
    st.markdown(f"**Protocol:** {test.protocol.protocol_name} ({test.protocol.protocol_id})")
    st.markdown(f"**Standard:** {test.protocol.standard}")
    st.markdown(f"**Date:** {test.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test conditions
    st.markdown("#### Test Conditions")
    conditions_df = pd.DataFrame({
        "Parameter": [
            "Sample ID",
            "Technology",
            "Area",
            "Temperature",
            "Wavelength Range",
            "Bias Voltage",
            "Operator"
        ],
        "Value": [
            test.sample_info.get("sample_id"),
            test.sample_info.get("technology"),
            f"{test.sample_info.get('area')} cm²",
            f"{test.test_params.get('temperature')} °C",
            f"{test.test_params['wavelength']['start']}-{test.test_params['wavelength']['end']} nm",
            f"{test.test_params.get('bias_voltage', 0)} V",
            test.test_params.get('operator', 'Not specified')
        ]
    })
    st.table(conditions_df)

    # Results summary
    st.markdown("#### Results Summary")
    results_df = pd.DataFrame({
        "Metric": [
            "Peak Wavelength",
            "Peak EQE",
            "Integrated Jsc"
        ],
        "Value": [
            f"{test.results['peak_wavelength']:.0f} nm",
            f"{test.results['peak_eqe']:.1f} %",
            f"{test.results['integrated_jsc']:.2f} mA/cm²"
        ]
    })
    st.table(results_df)

    # QC Status
    st.markdown("#### Quality Control Status")
    qc_df = pd.DataFrame([
        {
            "Check": check_name.replace('_', ' ').title(),
            "Status": "✅ PASS" if result["passed"] else "❌ FAIL",
            "Value": f"{result['value']:.3f}",
            "Threshold": f"{result['threshold']:.3f}",
            "Unit": result.get('unit', ''),
            "Action": result.get('action', '')
        }
        for check_name, result in test_data["qc_results"].items()
    ])
    st.dataframe(qc_df, use_container_width=True)

    # Export report
    if st.button("📄 Generate PDF Report", type="primary"):
        st.info("PDF report generation would be implemented here using ReportLab or similar library")


# Main app entry point
if __name__ == "__main__":
    st.set_page_config(
        page_title="SPEC-001 Spectral Response Test",
        page_icon="🌈",
        layout="wide"
    )
    render_spec_001_ui()
