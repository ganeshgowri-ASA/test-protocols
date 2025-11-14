"""Test execution page."""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from ...protocols.ener_001 import ENER001Protocol
from ...core.test_runner import TestRunner
from ...models import init_database, get_session, TestSession, Protocol


def show_test_execution_page():
    """Display test execution page."""
    st.title("Test Execution")

    # Check if protocol is selected
    selected_protocol = st.session_state.get("selected_protocol", None)

    if not selected_protocol:
        st.warning("No protocol selected. Please go to 'Protocol Selection' page first.")

        # Allow manual selection
        protocol_id = st.selectbox(
            "Or select protocol here:",
            ["ENER-001"],
            help="Select a protocol to execute",
        )

        if st.button("Use Selected Protocol"):
            st.session_state["selected_protocol"] = protocol_id
            st.rerun()

        return

    st.info(f"Selected Protocol: **{selected_protocol}**")

    # Protocol-specific execution
    if selected_protocol == "ENER-001":
        execute_ener001_test()
    else:
        st.error(f"Protocol {selected_protocol} not yet implemented in UI.")


def execute_ener001_test():
    """Execute ENER-001 Energy Rating Test."""
    st.header("ENER-001: Energy Rating Test")

    # Test metadata
    with st.expander("Test Metadata", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            test_name = st.text_input("Test Name", value=f"Energy Rating Test {datetime.now().strftime('%Y%m%d')}")
            operator = st.text_input("Operator Name")
            device_id = st.text_input("Module Serial Number / Device ID")

        with col2:
            location = st.text_input("Test Location", value="Laboratory")
            module_area = st.number_input("Module Area (m²)", value=1.65, min_value=0.1, max_value=10.0, step=0.01)
            rated_power = st.number_input("Rated Power STC (W)", value=300.0, min_value=1.0, max_value=1000.0, step=1.0)

    # Data input
    st.subheader("Test Data Input")

    data_input_method = st.radio(
        "Select data input method:",
        ["Upload CSV File", "Upload Excel File", "Use Sample Data"],
    )

    test_data = None

    if data_input_method == "Upload CSV File":
        uploaded_file = st.file_uploader(
            "Upload test data CSV",
            type=["csv"],
            help="CSV file should contain columns: irradiance, module_temp, voltage, current",
        )

        if uploaded_file:
            try:
                test_data = pd.read_csv(uploaded_file)
                st.success(f"Loaded {len(test_data)} data points")
            except Exception as e:
                st.error(f"Error loading CSV: {e}")

    elif data_input_method == "Upload Excel File":
        uploaded_file = st.file_uploader(
            "Upload test data Excel",
            type=["xlsx", "xls"],
            help="Excel file should contain columns: irradiance, module_temp, voltage, current",
        )

        if uploaded_file:
            try:
                test_data = pd.read_excel(uploaded_file)
                st.success(f"Loaded {len(test_data)} data points")
            except Exception as e:
                st.error(f"Error loading Excel: {e}")

    elif data_input_method == "Use Sample Data":
        if st.button("Generate Sample Data"):
            test_data = generate_sample_data()
            st.success(f"Generated {len(test_data)} sample data points")

    # Display data preview
    if test_data is not None:
        # Add module area and rated power to data
        test_data["module_area"] = module_area
        test_data["rated_power"] = rated_power

        with st.expander("Data Preview", expanded=True):
            st.dataframe(test_data.head(20))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Points", len(test_data))
            with col2:
                if "irradiance" in test_data.columns:
                    unique_irr = test_data["irradiance"].nunique()
                    st.metric("Irradiance Levels", unique_irr)
            with col3:
                if "module_temp" in test_data.columns:
                    unique_temp = test_data["module_temp"].nunique()
                    st.metric("Temperature Levels", unique_temp)

        # Run test
        st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            climate = st.selectbox(
                "Climate Zone (for energy rating)",
                ["moderate", "hot", "cold"],
                help="Select climate zone for energy rating calculation",
            )

        with col2:
            validate_inputs = st.checkbox("Validate Inputs", value=True)

        with col3:
            run_qc = st.checkbox("Run Quality Checks", value=True)

        if st.button("🚀 Run Test", type="primary"):
            run_test(test_data, test_name, operator, device_id, location, climate, validate_inputs, run_qc)


def generate_sample_data() -> pd.DataFrame:
    """Generate sample test data for ENER-001."""
    import numpy as np

    # Test matrix: irradiance levels × temperature levels
    irradiances = [100, 200, 400, 600, 800, 1000]
    temperatures = [15, 25, 50, 75]

    data_points = []

    for irr in irradiances:
        for temp in temperatures:
            # Generate IV curve points (30 points per condition)
            # Simplified model: linear approximation
            voc = 45 - (temp - 25) * 0.15  # Voc decreases with temperature
            isc = irr / 1000 * 10  # Isc proportional to irradiance

            voltages = np.linspace(0, voc, 30)

            for v in voltages:
                # Simplified IV curve model
                i = isc * (1 - (v / voc) ** 1.2)

                data_points.append(
                    {
                        "irradiance": irr,
                        "module_temp": temp,
                        "ambient_temp": temp - 20,
                        "voltage": round(v, 2),
                        "current": round(max(0, i), 3),
                    }
                )

    return pd.DataFrame(data_points)


def run_test(
    data: pd.DataFrame,
    test_name: str,
    operator: str,
    device_id: str,
    location: str,
    climate: str,
    validate_inputs: bool,
    run_qc: bool,
):
    """Run the ENER-001 test."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Initialize protocol
        status_text.text("Initializing protocol...")
        progress_bar.progress(10)

        protocol = ENER001Protocol()

        # Create test runner
        status_text.text("Creating test runner...")
        progress_bar.progress(20)

        runner = TestRunner(protocol)

        # Run test
        status_text.text("Executing test...")
        progress_bar.progress(40)

        results = runner.run(data, validate_inputs=validate_inputs, run_qc=run_qc)

        progress_bar.progress(80)

        # Save to database
        status_text.text("Saving results to database...")

        try:
            init_database()

            with get_session() as session:
                # Create test session record
                test_session = TestSession(
                    session_id=results["session_id"],
                    test_name=test_name,
                    operator=operator,
                    device_under_test=device_id,
                    location=location,
                    status=results["status"],
                    started_at=datetime.fromisoformat(results["start_time"]),
                    completed_at=datetime.fromisoformat(results["end_time"]),
                    duration_seconds=results["duration_seconds"],
                    test_data=data.to_dict(orient="records"),
                    results=results,
                    qc_results=results.get("qc_results"),
                )

                # Get or create protocol record
                protocol_record = session.query(Protocol).filter_by(protocol_id="ENER-001").first()

                if not protocol_record:
                    protocol_record = Protocol.from_config(protocol.config)
                    session.add(protocol_record)
                    session.commit()

                test_session.protocol_id = protocol_record.id
                session.add(test_session)
                session.commit()

                st.session_state["last_test_session_id"] = test_session.id

        except Exception as e:
            st.warning(f"Could not save to database: {e}")

        progress_bar.progress(100)
        status_text.text("Test completed!")

        # Display results
        st.success(f"✅ Test completed with status: **{results['status']}**")

        # Store results in session state
        st.session_state["test_results"] = results

        # Display results
        display_results(results, climate)

    except Exception as e:
        st.error(f"❌ Test execution failed: {e}")
        st.exception(e)

    finally:
        progress_bar.empty()
        status_text.empty()


def display_results(results: dict, climate: str):
    """Display test results."""
    st.markdown("---")
    st.header("Test Results")

    # Tabs for different result sections
    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Analysis", "Quality Checks", "Charts"])

    with tab1:
        st.subheader("Test Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Session ID", results["session_id"])
            st.metric("Status", results["status"])

        with col2:
            st.metric("Duration", f"{results['duration_seconds']:.1f}s")
            iv_curves = results.get("iv_curves", {})
            st.metric("Test Conditions", len(iv_curves))

        with col3:
            if "analysis" in results and "energy_rating" in results["analysis"]:
                energy_rating = results["analysis"]["energy_rating"]["energy_rating_kWh_per_kWp"]
                st.metric("Energy Rating", f"{energy_rating:.0f} kWh/kWp")

    with tab2:
        st.subheader("Performance Analysis")

        if "analysis" in results:
            analysis = results["analysis"]

            # STC Performance
            if "stc_performance" in analysis:
                st.markdown("### Performance at STC (1000 W/m², 25°C)")
                stc = analysis["stc_performance"]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pmax", f"{stc.get('pmpp', 0):.2f} W")
                with col2:
                    st.metric("Voc", f"{stc.get('voc', 0):.2f} V")
                with col3:
                    st.metric("Isc", f"{stc.get('isc', 0):.2f} A")
                with col4:
                    st.metric("Fill Factor", f"{stc.get('fill_factor', 0):.1f}%")

            # Temperature Coefficients
            if "temperature_coefficients" in analysis:
                st.markdown("### Temperature Coefficients")
                tc = analysis["temperature_coefficients"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    if "alpha_isc" in tc:
                        st.metric("α (Isc)", f"{tc['alpha_isc']:.3f} %/°C")
                with col2:
                    if "beta_voc" in tc:
                        st.metric("β (Voc)", f"{tc['beta_voc']:.3f} %/°C")
                with col3:
                    if "gamma_pmax" in tc:
                        st.metric("γ (Pmax)", f"{tc['gamma_pmax']:.3f} %/°C")

            # Energy Rating
            if "energy_rating" in analysis:
                st.markdown("### Energy Rating")
                er = analysis["energy_rating"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Energy Rating", f"{er['energy_rating_kWh_per_kWp']:.0f} kWh/kWp")
                with col2:
                    st.metric("Climate Zone", er["climate_zone"].capitalize())
                with col3:
                    st.metric("Performance Ratio", f"{er['performance_ratio']:.1f}%")

    with tab3:
        st.subheader("Quality Control Results")

        if "qc_results" in results:
            qc_results = results["qc_results"]

            # Summary metrics
            total = len(qc_results)
            passed = sum(1 for qc in qc_results if qc.get("passed"))
            failed = sum(1 for qc in qc_results if qc.get("passed") == False)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Checks", total)
            with col2:
                st.metric("Passed", passed, delta=None if passed == total else f"-{total - passed}")
            with col3:
                st.metric("Failed", failed, delta=None if failed == 0 else f"+{failed}")

            # Detailed QC results
            for qc in qc_results:
                severity = qc.get("severity", "info")
                passed = qc.get("passed")

                if passed is True:
                    icon = "✅"
                    color = "green"
                elif passed is False:
                    icon = "❌" if severity == "error" else "⚠️"
                    color = "red" if severity == "error" else "orange"
                else:
                    icon = "ℹ️"
                    color = "blue"

                with st.expander(f"{icon} {qc['name']}"):
                    st.write(f"**Status**: {qc.get('message', 'No message')}")
                    st.write(f"**Severity**: {severity}")
                    st.write(f"**Type**: {qc['type']}")

    with tab4:
        st.subheader("Charts and Visualizations")

        if "charts" in results:
            charts = results["charts"]

            # Display each chart
            for chart_name, fig in charts.items():
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)

    # Download buttons
    st.markdown("---")
    st.subheader("Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export as JSON
        import json

        json_str = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"{results['session_id']}_results.json",
            mime="application/json",
        )

    with col2:
        # Export measurements as CSV
        if "measurements" in results:
            measurements_df = pd.DataFrame(results["measurements"])
            csv = measurements_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{results['session_id']}_measurements.csv",
                mime="text/csv",
            )

    with col3:
        st.button("📄 Generate PDF Report", disabled=True, help="PDF report generation coming soon")
