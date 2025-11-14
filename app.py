"""
GenSpark - Test Protocols UI

Main Streamlit application for the test protocols framework.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.protocol_loader import ProtocolLoader


def main():
    """Main application entry point."""

    st.set_page_config(
        page_title="GenSpark - Test Protocols",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .status-pass {
            color: #28a745;
            font-weight: bold;
        }
        .status-fail {
            color: #dc3545;
            font-weight: bold;
        }
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=GenSpark", use_container_width=True)
        st.markdown("---")

        page = st.selectbox(
            "Navigation",
            ["Home", "Protocols", "Test Execution", "Results", "Reports"],
            key="navigation"
        )

        st.markdown("---")
        st.markdown("### Quick Info")
        st.info("**Framework Version:** 1.0.0")
        st.info("**Active Protocols:** 1")

    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Protocols":
        show_protocols_page()
    elif page == "Test Execution":
        show_test_execution_page()
    elif page == "Results":
        show_results_page()
    elif page == "Reports":
        show_reports_page()


def show_home_page():
    """Display home page."""
    st.markdown('<div class="main-header">🔬 GenSpark Test Protocols</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Modular PV Testing Protocol Framework</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📋 Total Protocols")
        st.markdown('<div class="metric-card"><h1>1</h1><p>Active Protocols</p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🧪 Active Tests")
        st.markdown('<div class="metric-card"><h1>0</h1><p>Tests Running</p></div>', unsafe_allow_html=True)

    with col3:
        st.markdown("### ✅ Completed Tests")
        st.markdown('<div class="metric-card"><h1>0</h1><p>Total Tests</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📌 Available Protocols")

    # Load and display protocols
    loader = ProtocolLoader()
    protocols = loader.list_protocols()

    if protocols:
        for protocol in protocols:
            with st.expander(f"**{protocol['protocol_id']}** - {protocol['protocol_name']}", expanded=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Description:** {protocol.get('description', 'N/A')}")
                    st.markdown(f"**Category:** {protocol.get('category', 'N/A')}")
                    st.markdown(f"**Version:** {protocol.get('version', 'N/A')}")

                with col2:
                    if st.button("Run Test", key=f"run_{protocol['protocol_id']}"):
                        st.session_state['selected_protocol'] = protocol['protocol_id']
                        st.session_state['navigation'] = 'Test Execution'
                        st.rerun()
    else:
        st.warning("No protocols found. Please add protocol definitions to the protocols/ directory.")

    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. **Select a Protocol** from the list above or navigate to the Protocols page
    2. **Configure Test Parameters** in the Test Execution page
    3. **Add Samples** to be tested
    4. **Run the Test** and monitor progress
    5. **View Results** and generate reports
    """)


def show_protocols_page():
    """Display protocols management page."""
    st.markdown('<div class="main-header">📋 Protocol Management</div>', unsafe_allow_html=True)

    loader = ProtocolLoader()
    protocols = loader.list_protocols()

    if not protocols:
        st.warning("No protocols available.")
        return

    # Protocol selector
    protocol_ids = [p['protocol_id'] for p in protocols]
    selected_id = st.selectbox("Select Protocol", protocol_ids)

    if selected_id:
        protocol_data = loader.load_protocol(selected_id)

        # Display protocol details
        st.markdown(f"## {protocol_data['protocol_name']}")
        st.markdown(f"**Version:** {protocol_data['version']}")
        st.markdown(f"**Category:** {protocol_data['category']}")
        st.markdown(f"**Description:** {protocol_data['description']}")

        st.markdown("---")

        # Test parameters
        st.markdown("### Test Parameters")
        params = protocol_data.get('test_parameters', {})

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Duration", f"{params.get('duration_hours', 'N/A')} hours")
            st.metric("Temperature", f"{params.get('temperature_celsius', 'N/A')}°C")

        with col2:
            st.metric("Humidity", f"{params.get('humidity_percent', 'N/A')}%")
            st.metric("UV Intensity", f"{params.get('light_intensity_mw_cm2', 'N/A')} mW/cm²")

        # Measurements
        st.markdown("### Measurements")
        measurements = protocol_data.get('measurements', [])

        for measurement in measurements:
            with st.expander(measurement.get('name', 'Unnamed')):
                st.markdown(f"**Type:** {measurement.get('measurement_type', 'N/A')}")
                st.markdown(f"**Unit:** {measurement.get('unit', 'N/A')}")
                st.markdown(f"**Description:** {measurement.get('description', 'N/A')}")
                st.markdown(f"**Interval:** Every {measurement.get('measurement_interval_hours', 'N/A')} hours")

                thresholds = measurement.get('critical_thresholds', {})
                if thresholds:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.warning(f"⚠️ Warning: {thresholds.get('warning', 'N/A')}")
                    with col2:
                        st.error(f"❌ Fail: {thresholds.get('fail', 'N/A')}")

        # Pass/Fail Criteria
        st.markdown("### Pass/Fail Criteria")
        criteria = protocol_data.get('pass_fail_criteria', [])

        for criterion in criteria:
            severity = criterion.get('severity', 'INFO')
            icon = "❌" if severity == "FAIL" else "⚠️"
            st.markdown(f"{icon} **{criterion.get('description', 'N/A')}**")


def show_test_execution_page():
    """Display test execution page."""
    st.markdown('<div class="main-header">🧪 Test Execution</div>', unsafe_allow_html=True)

    from protocols.yellow.yellow_001 import Yellow001Protocol, Sample
    import json

    # Protocol selection
    loader = ProtocolLoader()
    protocols = loader.list_protocols()
    protocol_ids = [p['protocol_id'] for p in protocols]

    selected_protocol = st.selectbox("Select Protocol", protocol_ids, key="exec_protocol")

    if selected_protocol == "YELLOW-001":
        st.markdown("### EVA Yellowing Test - YELLOW-001")

        # Sample input
        st.markdown("#### Sample Configuration")

        num_samples = st.number_input("Number of samples", min_value=1, max_value=10, value=3)

        samples = []

        for i in range(num_samples):
            with st.expander(f"Sample {i+1}", expanded=(i == 0)):
                col1, col2 = st.columns(2)

                with col1:
                    sample_id = st.text_input(f"Sample ID", value=f"EVA_SAMPLE_{i+1:03d}", key=f"id_{i}")
                    batch_code = st.text_input(f"Batch Code", value=f"BATCH_{i+1}", key=f"batch_{i}")

                with col2:
                    length = st.number_input(f"Length (mm)", value=100.0, key=f"len_{i}")
                    width = st.number_input(f"Width (mm)", value=100.0, key=f"wid_{i}")
                    thickness = st.number_input(f"Thickness (mm)", value=3.0, key=f"thick_{i}")

                sample = Sample(
                    sample_id=sample_id,
                    material_type="EVA",
                    dimensions={'length_mm': length, 'width_mm': width, 'thickness_mm': thickness},
                    batch_code=batch_code
                )
                samples.append(sample)

        # Test execution
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("🚀 Start Test", type="primary", use_container_width=True):
                with st.spinner("Executing YELLOW-001 protocol..."):
                    protocol = Yellow001Protocol()
                    results = protocol.execute_test(samples)
                    analysis = protocol.analyze_results()

                    # Store in session state
                    st.session_state['test_results'] = results
                    st.session_state['test_analysis'] = analysis

                st.success("✅ Test completed successfully!")
                st.balloons()

        with col2:
            if st.button("📊 View Results", use_container_width=True):
                st.session_state['navigation'] = 'Results'
                st.rerun()

        # Display results if available
        if 'test_results' in st.session_state:
            st.markdown("---")
            st.markdown("### Test Results")

            results = st.session_state['test_results']
            analysis = st.session_state.get('test_analysis', {})

            # Summary
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Test Session", results['session_id'][-12:])

            with col2:
                st.metric("Samples Tested", results['total_samples'])

            with col3:
                status = analysis.get('overall_status', 'UNKNOWN')
                status_class = f"status-{status.lower()}"
                st.markdown(f"**Overall Status:** <span class='{status_class}'>{status}</span>", unsafe_allow_html=True)

            # Sample summaries
            st.markdown("#### Sample Results")

            sample_summaries = analysis.get('sample_summaries', {})

            for sample_id, summary in sample_summaries.items():
                with st.expander(f"**{sample_id}** - {summary['status']}"):
                    final_vals = summary.get('final_values', {})

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Yellow Index", f"{final_vals.get('yellow_index', 'N/A'):.2f}")

                    with col2:
                        st.metric("Color Shift (ΔE)", f"{final_vals.get('color_shift', 'N/A'):.2f}")

                    with col3:
                        st.metric("Transmittance", f"{final_vals.get('light_transmittance', 'N/A'):.2f}%")

            # Option to download results
            st.markdown("---")
            st.download_button(
                "📥 Download Results (JSON)",
                data=json.dumps(results, indent=2),
                file_name=f"test_results_{results['session_id']}.json",
                mime="application/json"
            )


def show_results_page():
    """Display results page."""
    st.markdown('<div class="main-header">📊 Test Results</div>', unsafe_allow_html=True)

    if 'test_results' not in st.session_state:
        st.info("No test results available. Run a test first.")
        return

    results = st.session_state['test_results']
    analysis = st.session_state.get('test_analysis', {})

    st.markdown(f"### Test Session: {results['session_id']}")

    # Overall summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Protocol", results['protocol_id'])

    with col2:
        st.metric("Version", results['protocol_version'])

    with col3:
        st.metric("Samples", results['total_samples'])

    with col4:
        status = analysis.get('overall_status', 'UNKNOWN')
        st.metric("Status", status)

    st.markdown("---")

    # Detailed results for each sample
    for sample_data in results.get('samples', []):
        sample_id = sample_data['sample_id']
        st.markdown(f"### {sample_id}")

        time_points = sample_data['time_points']

        # Create data for plotting
        import pandas as pd

        df = pd.DataFrame(time_points)

        # Plot YI over time
        st.markdown("#### Yellowness Index Over Time")
        st.line_chart(df.set_index('time_point_hours')['yellow_index'])

        # Plot Delta E over time
        st.markdown("#### Color Shift (ΔE) Over Time")
        st.line_chart(df.set_index('time_point_hours')['color_shift'])

        # Plot Transmittance over time
        st.markdown("#### Light Transmittance Over Time")
        st.line_chart(df.set_index('time_point_hours')['light_transmittance'])

        # Show data table
        with st.expander("View Raw Data"):
            st.dataframe(df)

        st.markdown("---")


def show_reports_page():
    """Display reports page."""
    st.markdown('<div class="main-header">📄 Reports</div>', unsafe_allow_html=True)

    st.info("Report generation feature coming soon!")

    if 'test_results' in st.session_state:
        st.markdown("### Generate Report")

        report_format = st.selectbox("Report Format", ["PDF", "Excel", "HTML", "JSON"])

        if st.button("Generate Report"):
            st.success(f"Report generation in {report_format} format would start here!")


if __name__ == "__main__":
    main()
