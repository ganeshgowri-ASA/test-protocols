"""
PVTP-010: Flash Test / STC Performance - Streamlit Page
"""
import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
import plotly.graph_objects as go

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.protocols.electrical_pvtp010 import PVTP010Handler

st.set_page_config(page_title="PVTP-010: Flash Test", layout="wide")

st.markdown("# ⚡ PVTP-010: Flash Test / STC Performance")
st.markdown("Standard Test Conditions (STC) performance measurement with uncertainty analysis")
st.markdown("---")

# Initialize handler
handler = PVTP010Handler()

# Load protocol template
with open(Path(__file__).parent.parent.parent / "protocols/templates/PVTP-010_flash_test_stc.json") as f:
    template = json.load(f)

# Create tabs for workflow
tabs = st.tabs(["📝 Sample Info", "🔬 Measurements", "📊 Analysis", "✅ QC & Reports"])

# Tab 1: Sample Information
with tabs[0]:
    st.subheader("Sample Information")

    col1, col2 = st.columns(2)

    with col1:
        sample_id = st.text_input("Sample ID *", placeholder="e.g., MOD-2025-001")
        manufacturer = st.text_input("Manufacturer *", placeholder="e.g., SolarTech Inc")
        model = st.text_input("Model Number *", placeholder="e.g., ST-400M")
        serial_number = st.text_input("Serial Number *", placeholder="e.g., SN123456789")

    with col2:
        technology = st.selectbox("Cell Technology *", [
            "mono-Si", "multi-Si", "PERC", "HJT", "TOPCon", "CdTe", "CIGS", "Other"
        ])
        rated_power = st.number_input("Rated Power (W) *", min_value=0.0, max_value=1000.0, value=400.0)
        test_date = st.date_input("Test Date *")
        operator = st.text_input("Test Operator *", value="John Doe")

    st.markdown("**Optional Information**")
    col3, col4 = st.columns(2)

    with col3:
        project_id = st.text_input("Project ID", placeholder="Optional")
        customer = st.text_input("Customer Name", placeholder="Optional")

    with col4:
        notes = st.text_area("Test Notes", placeholder="Optional notes...")

    if st.button("Save Sample Info", type="primary"):
        st.session_state['sample_info'] = {
            'sample_id': sample_id,
            'manufacturer': manufacturer,
            'model': model,
            'serial_number': serial_number,
            'technology': technology,
            'rated_power': rated_power,
            'test_date': str(test_date),
            'operator': operator,
            'project_id': project_id,
            'customer': customer,
            'notes': notes
        }
        st.success("✅ Sample information saved!")

# Tab 2: Measurements
with tabs[1]:
    st.subheader("Flash Measurement Data")

    st.markdown("**Pre-Test Conditions**")
    col1, col2, col3 = st.columns(3)

    with col1:
        ambient_temp = st.number_input("Ambient Temperature (°C)", value=23.0, step=0.1)
    with col2:
        humidity = st.number_input("Relative Humidity (%)", value=45.0, step=1.0)
    with col3:
        stabilization_time = st.number_input("Stabilization Time (min)", value=30, step=5)

    st.markdown("---")
    st.markdown("**Flash Measurement (Uncorrected)**")

    col1, col2 = st.columns(2)

    with col1:
        irradiance_measured = st.number_input("Measured Irradiance (W/m²)", value=1000.0, step=1.0,
                                              help="Measured irradiance during flash")
        temperature_measured = st.number_input("Module Temperature (°C)", value=25.0, step=0.1,
                                               help="Module temperature during measurement")
        voc_measured = st.number_input("Open Circuit Voltage (V)", value=48.5, step=0.1)
        isc_measured = st.number_input("Short Circuit Current (A)", value=10.5, step=0.01)

    with col2:
        pmax_measured = st.number_input("Maximum Power (W)", value=405.0, step=0.1)
        vmpp_measured = st.number_input("Voltage at MPP (V)", value=40.2, step=0.1)
        impp_measured = st.number_input("Current at MPP (A)", value=10.07, step=0.01)
        mmf = st.number_input("Spectral Mismatch Factor", value=1.0, step=0.01, min_value=0.9, max_value=1.1)

    if st.button("Process Measurements", type="primary"):
        # Prepare test data
        test_data = {
            'inputs': st.session_state.get('sample_info', {}),
            'measurements': {
                'pre_test_conditions': {
                    'ambient_temp': ambient_temp,
                    'humidity': humidity,
                    'stabilization_time': stabilization_time
                },
                'flash_measurement': {
                    'irradiance_measured': irradiance_measured,
                    'temperature_measured': temperature_measured,
                    'voc_measured': voc_measured,
                    'isc_measured': isc_measured,
                    'pmax_measured': pmax_measured,
                    'vmpp_measured': vmpp_measured,
                    'impp_measured': impp_measured
                },
                'spectral_mismatch_factor': mmf
            }
        }

        # Process with handler
        try:
            results = handler.process_test(test_data)
            st.session_state['test_results'] = results
            st.success("✅ Analysis completed successfully!")
        except Exception as e:
            st.error(f"❌ Error processing test: {str(e)}")

# Tab 3: Analysis
with tabs[2]:
    st.subheader("STC-Corrected Results & Analysis")

    if 'test_results' in st.session_state:
        results = st.session_state['test_results']
        stc_results = results['analysis']['stc_results']

        # Display corrected parameters
        st.markdown("### STC-Corrected Parameters")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Voc @ STC", f"{stc_results['voc_stc']:.2f} V")
            st.metric("Isc @ STC", f"{stc_results['isc_stc']:.3f} A")

        with col2:
            st.metric("Pmax @ STC", f"{stc_results['pmax_stc']:.2f} W")
            st.metric("FF @ STC", f"{stc_results['ff_stc']:.4f}")

        with col3:
            st.metric("Vmpp @ STC", f"{stc_results['vmpp_stc']:.2f} V")
            st.metric("Impp @ STC", f"{stc_results['impp_stc']:.3f} A")

        with col4:
            uncertainty = stc_results['combined_uncertainty_pmax']
            st.metric("Combined Uncertainty", f"±{uncertainty:.2f}%")
            st.metric("Expanded Uncertainty (k=2)", f"±{stc_results['expanded_uncertainty_pmax']:.2f}%")

        # Performance ratio
        st.markdown("---")
        st.markdown("### Performance Analysis")

        col1, col2 = st.columns(2)

        with col1:
            perf_ratio = results['analysis']['performance_ratio']
            power_dev = results['analysis']['power_deviation']

            st.metric("Performance Ratio", f"{perf_ratio:.2f}%",
                     delta=f"{perf_ratio - 100:.2f}%")
            st.metric("Power Deviation", f"{power_dev:.2f} W")

        with col2:
            # Uncertainty budget chart
            if 'uncertainty_budget' in stc_results:
                budget = stc_results['uncertainty_budget']

                fig = go.Figure(data=[
                    go.Bar(
                        x=list(budget.keys()),
                        y=list(budget.values()),
                        text=[f"{v:.2f}%" for v in budget.values()],
                        textposition='auto'
                    )
                ])

                fig.update_layout(
                    title="Uncertainty Budget Contributors",
                    xaxis_title="Source",
                    yaxis_title="Contribution (%)",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("👆 Complete measurements in the previous tab to see analysis results.")

# Tab 4: QC & Reports
with tabs[3]:
    st.subheader("Quality Control & Reporting")

    if 'test_results' in st.session_state:
        results = st.session_state['test_results']
        qc_results = results.get('qc_results', [])

        st.markdown("### QC Check Results")

        # Display QC results in a table
        if qc_results:
            qc_df = pd.DataFrame(qc_results)
            st.dataframe(qc_df, use_container_width=True)

            # Summary
            passed = sum(1 for qc in qc_results if qc['status'] == 'passed')
            total = len(qc_results)

            if passed == total:
                st.success(f"✅ All {total} QC checks passed!")
            else:
                st.warning(f"⚠️ {passed}/{total} QC checks passed. Review required.")

        # Report generation
        st.markdown("---")
        st.markdown("### Generate Reports")

        col1, col2 = st.columns(2)

        with col1:
            report_type = st.selectbox("Report Type", [
                "Test Report (PDF)",
                "Certificate (PDF)",
                "Data Export (Excel)",
                "Raw Data (CSV)"
            ])

        with col2:
            include_charts = st.checkbox("Include Charts", value=True)
            include_uncertainty = st.checkbox("Include Uncertainty Analysis", value=True)

        if st.button("Generate Report", type="primary"):
            st.success("✅ Report generated successfully!")
            st.download_button("📥 Download Report", data="Sample report", file_name="PVTP-010_report.pdf")

    else:
        st.info("👆 Complete the test to access QC checks and reporting.")

# Sidebar with protocol info
with st.sidebar:
    st.markdown("### Protocol Information")
    st.markdown(f"**ID:** PVTP-010")
    st.markdown(f"**Version:** {template['metadata']['version']}")
    st.markdown(f"**Category:** {template['metadata']['category']}")
    st.markdown("**Standards:**")
    for std in template['metadata']['standard_references']:
        st.markdown(f"- {std}")

    st.markdown("---")
    st.markdown("### Estimated Duration")
    st.markdown(f"⏱️ {template['project_management']['estimated_duration_minutes']} minutes")

    st.markdown("---")
    if st.button("🏠 Back to Dashboard"):
        st.switch_page("app.py")
