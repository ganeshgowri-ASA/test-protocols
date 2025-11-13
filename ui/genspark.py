"""
GenSpark Interactive UI for PV Testing Protocols
"""

import streamlit as st
from typing import Dict, Any
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.lic_001 import LIC001Protocol
from ui.components import UIComponents


class GenSparkApp:
    """
    Main GenSpark application for PV testing protocols
    """

    def __init__(self):
        self.components = UIComponents()
        self._setup_page_config()

    def _setup_page_config(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="PV Testing Protocols",
            page_icon="☀️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def run(self):
        """Run the application"""
        # Sidebar for protocol selection
        with st.sidebar:
            st.title("☀️ PV Testing")
            st.markdown("---")

            protocol_choice = st.selectbox(
                "Select Protocol",
                options=["LIC-001 - Low Irradiance Conditions"],
                key="protocol_choice"
            )

            st.markdown("---")

            st.markdown("### About")
            st.info("""
            **Modular PV Testing Framework**

            JSON-based dynamic templates for automated
            testing, analysis, and reporting.

            **Standards Compliance:**
            - IEC 61215-1:2021
            - IEC 61730

            **Features:**
            - Real-time validation
            - Interactive visualizations
            - Data traceability
            - LIMS/QMS integration
            """)

        # Main content based on selection
        if "LIC-001" in protocol_choice:
            self.render_lic001()

    def render_lic001(self):
        """Render LIC-001 protocol interface"""
        protocol = LIC001Protocol()

        # Header
        self.components.render_header(
            "LIC-001: Low Irradiance Conditions Test",
            "Performance testing at 200, 400, 600, and 800 W/m² at 25°C (IEC 61215-1:2021)"
        )

        # Protocol info
        self.components.render_protocol_info(
            protocol.PROTOCOL_ID,
            protocol.VERSION,
            protocol.STANDARD
        )

        st.markdown("---")

        # Use tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Test Setup",
            "📊 Measurements",
            "📈 Analysis & Results",
            "💾 Export"
        ])

        # Initialize session state
        if 'test_data' not in st.session_state:
            st.session_state.test_data = {}
        if 'measurements' not in st.session_state:
            st.session_state.measurements = {}
        if 'results' not in st.session_state:
            st.session_state.results = None

        # Tab 1: Test Setup
        with tab1:
            self._render_test_setup_tab(protocol)

        # Tab 2: Measurements
        with tab2:
            self._render_measurements_tab(protocol)

        # Tab 3: Analysis & Results
        with tab3:
            self._render_analysis_tab(protocol)

        # Tab 4: Export
        with tab4:
            self._render_export_tab(protocol)

    def _render_test_setup_tab(self, protocol: LIC001Protocol):
        """Render test setup tab"""
        st.markdown("### Sample Information")
        sample_info = self.components.render_sample_info_form()

        st.markdown("---")

        st.markdown("### Test Conditions")
        test_conditions = self.components.render_test_conditions_form(
            target_temp=protocol.TARGET_TEMPERATURE,
            irradiance_levels=protocol.REQUIRED_IRRADIANCE_LEVELS
        )

        st.markdown("---")

        # Save button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Save Setup", type="primary", use_container_width=True):
                # Validate sample info
                if not sample_info.get("sample_id"):
                    st.error("Sample ID is required")
                    return
                if not sample_info.get("module_type"):
                    st.error("Module Type is required")
                    return

                # Create test run
                test_run = protocol.create_test_run(
                    sample_id=sample_info["sample_id"],
                    sample_info=sample_info,
                    operator=test_conditions.get("operator")
                )

                # Update test conditions
                test_run["test_conditions"] = test_conditions

                # Save to session state
                st.session_state.test_data = test_run
                st.success("✓ Test setup saved successfully!")

        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.test_data = {}
                st.session_state.measurements = {}
                st.session_state.results = None
                st.rerun()

        # Show current setup
        if st.session_state.test_data:
            with st.expander("📋 Current Test Setup", expanded=False):
                st.json(st.session_state.test_data.get("sample_info", {}))

    def _render_measurements_tab(self, protocol: LIC001Protocol):
        """Render measurements tab"""
        if not st.session_state.test_data:
            st.warning("⚠️ Please complete Test Setup first")
            return

        st.markdown("### I-V Curve Measurements")
        st.info("Enter I-V curve data for each irradiance level. You can upload CSV files or enter data manually.")

        # Create tabs for each irradiance level
        irr_tabs = st.tabs([f"{irr} W/m²" for irr in protocol.REQUIRED_IRRADIANCE_LEVELS])

        for idx, irradiance in enumerate(protocol.REQUIRED_IRRADIANCE_LEVELS):
            with irr_tabs[idx]:
                measurement = self.components.render_measurement_input(
                    irradiance=irradiance,
                    key_prefix=f"measure_{irradiance}"
                )

                if measurement:
                    # Validate measurement
                    is_valid, errors = protocol.validator._validate_single_measurement(
                        measurement, irradiance
                    )

                    if errors:
                        st.warning("⚠️ Validation warnings:")
                        for error in errors:
                            st.warning(f"• {error}")

                    # Save button for this measurement
                    if st.button(f"💾 Save {irradiance} W/m² Measurement", key=f"save_{irradiance}"):
                        st.session_state.measurements[str(irradiance)] = measurement
                        st.success(f"✓ Measurement saved for {irradiance} W/m²")

                # Show if already saved
                if str(irradiance) in st.session_state.measurements:
                    st.success(f"✓ Measurement for {irradiance} W/m² is saved")
                    num_points = st.session_state.measurements[str(irradiance)]["iv_curve"]["num_points"]
                    st.info(f"📊 {num_points} data points recorded")

        st.markdown("---")

        # Summary
        col1, col2 = st.columns(2)
        with col1:
            completed = len(st.session_state.measurements)
            total = len(protocol.REQUIRED_IRRADIANCE_LEVELS)
            st.metric("Measurements Completed", f"{completed}/{total}")

            if completed == total:
                st.success("✓ All measurements completed!")

        with col2:
            if st.button("🔄 Clear All Measurements", use_container_width=True):
                st.session_state.measurements = {}
                st.rerun()

    def _render_analysis_tab(self, protocol: LIC001Protocol):
        """Render analysis and results tab"""
        if not st.session_state.test_data:
            st.warning("⚠️ Please complete Test Setup first")
            return

        if len(st.session_state.measurements) < len(protocol.REQUIRED_IRRADIANCE_LEVELS):
            st.warning(f"⚠️ Please complete all measurements ({len(st.session_state.measurements)}/{len(protocol.REQUIRED_IRRADIANCE_LEVELS)} done)")
            return

        st.markdown("### Analysis & Results")

        # Calculate results button
        if st.button("🔬 Calculate Results", type="primary"):
            with st.spinner("Analyzing data..."):
                # Prepare data for analysis
                analysis_data = {
                    "sample_info": st.session_state.test_data.get("sample_info", {}),
                    "test_conditions": st.session_state.test_data.get("test_conditions", {}),
                    "measurements": st.session_state.measurements
                }

                # Calculate results
                results = protocol.calculate_results(analysis_data)
                st.session_state.results = results

                # Validate results
                is_valid, errors = protocol.validator.validate_results(results)

                if is_valid:
                    st.success("✓ Analysis completed successfully!")
                else:
                    st.warning("⚠️ Analysis completed with warnings:")
                    for error in errors:
                        st.warning(f"• {error}")

        # Display results
        if st.session_state.results:
            st.markdown("---")

            # Summary metrics
            summary = st.session_state.results.get("summary", {})
            col1, col2 = st.columns(2)

            with col1:
                test_passed = summary.get("test_passed", False)
                st.metric(
                    "Test Status",
                    "PASSED" if test_passed else "FAILED",
                    delta=None,
                    delta_color="normal"
                )

            with col2:
                quality_score = summary.get("quality_score", 0)
                st.metric(
                    "Quality Score",
                    f"{quality_score:.1f}/100",
                    delta=None
                )

            st.markdown("---")

            # Results table
            st.markdown("### Detailed Results")
            self.components.render_results_table(st.session_state.results)

            st.markdown("---")

            # Visualizations
            st.markdown("### Visualizations")

            # Prepare full data for visualization
            viz_data = {
                **st.session_state.test_data,
                "measurements": st.session_state.measurements,
                "results": st.session_state.results
            }

            # Generate plots
            plots = protocol.generate_visualizations(viz_data)

            # I-V Curves (200, 400, 600 W/m² as per requirements)
            st.markdown("#### I-V Curves (200, 400, 600 W/m²)")
            st.plotly_chart(plots["iv_curves"], use_container_width=True)

            # Power Curves
            st.markdown("#### Power-Voltage Curves")
            st.plotly_chart(plots["power_curves"], use_container_width=True)

            # Create two columns for additional plots
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Performance Summary")
                st.plotly_chart(plots["performance_summary"], use_container_width=True)

            with col2:
                st.markdown("#### Irradiance Response")
                st.plotly_chart(plots["irradiance_response"], use_container_width=True)

            # Fill Factor Comparison
            st.markdown("#### Fill Factor vs Irradiance")
            st.plotly_chart(plots["fill_factor_comparison"], use_container_width=True)

    def _render_export_tab(self, protocol: LIC001Protocol):
        """Render export tab"""
        if not st.session_state.results:
            st.warning("⚠️ Please complete analysis first")
            return

        st.markdown("### Export Results")

        # Prepare complete data package
        export_data = {
            **st.session_state.test_data,
            "measurements": st.session_state.measurements,
            "results": st.session_state.results
        }

        # Finalize with hash
        export_data = protocol.finalize_test_run(export_data)

        # Show data hash for traceability
        st.info(f"🔐 Data Hash: `{export_data['metadata']['data_hash']}`")

        # Download buttons
        sample_id = export_data.get("sample_info", {}).get("sample_id", "unknown")
        run_id = export_data.get("metadata", {}).get("run_id", "test")

        self.components.render_download_buttons(
            export_data,
            prefix=f"{protocol.PROTOCOL_ID}_{sample_id}_{run_id}"
        )

        st.markdown("---")

        # Integration section
        st.markdown("### System Integration")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### LIMS Integration")
            lims_id = st.text_input("LIMS ID", key="lims_id")
            if st.button("📤 Upload to LIMS"):
                if lims_id:
                    export_data["metadata"]["lims_id"] = lims_id
                    st.success(f"✓ Linked to LIMS: {lims_id}")
                    st.info("Note: Actual LIMS integration requires configuration")
                else:
                    st.error("Please enter LIMS ID")

        with col2:
            st.markdown("#### QMS Integration")
            qms_id = st.text_input("QMS ID", key="qms_id")
            if st.button("📤 Upload to QMS"):
                if qms_id:
                    export_data["metadata"]["qms_id"] = qms_id
                    st.success(f"✓ Linked to QMS: {qms_id}")
                    st.info("Note: Actual QMS integration requires configuration")
                else:
                    st.error("Please enter QMS ID")

        with col3:
            st.markdown("#### Project Management")
            project_id = st.text_input("Project ID", key="project_id")
            if st.button("📤 Link to Project"):
                if project_id:
                    export_data["metadata"]["project_id"] = project_id
                    st.success(f"✓ Linked to Project: {project_id}")
                    st.info("Note: Actual PM integration requires configuration")
                else:
                    st.error("Please enter Project ID")

        st.markdown("---")

        # Complete data view
        with st.expander("📋 View Complete Data Package"):
            st.json(export_data)


def main():
    """Main entry point"""
    app = GenSparkApp()
    app.run()


if __name__ == "__main__":
    main()
