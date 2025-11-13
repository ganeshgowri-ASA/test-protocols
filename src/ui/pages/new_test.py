"""New test creation page."""

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocol_engine import ProtocolLoader, ProtocolExecutor
from analysis import create_analyzer


def render() -> None:
    """Render the new test page."""

    st.markdown('<div class="main-header">➕ Create New Test</div>', unsafe_allow_html=True)

    # Initialize session state
    if "protocol_executor" not in st.session_state:
        st.session_state.protocol_executor = None
    if "measurements" not in st.session_state:
        st.session_state.measurements = []

    # Test setup section
    st.markdown("### 1. Test Information")

    col1, col2 = st.columns(2)

    with col1:
        sample_id = st.text_input(
            "Sample ID *",
            placeholder="e.g., PV-2025-001",
            help="Unique identifier for the test sample"
        )

        module_type = st.text_input(
            "Module Type *",
            placeholder="e.g., Mono-Si 400W",
            help="PV module type or model"
        )

        manufacturer = st.text_input(
            "Manufacturer",
            placeholder="e.g., SolarTech Inc."
        )

        serial_number = st.text_input(
            "Serial Number",
            placeholder="Module serial number"
        )

    with col2:
        technology = st.selectbox(
            "Technology *",
            ["mono-Si", "poly-Si", "CdTe", "CIGS", "a-Si", "HIT", "perovskite", "other"],
            help="PV cell technology"
        )

        rated_power = st.number_input(
            "Rated Power (W)",
            min_value=0.0,
            value=400.0,
            step=10.0
        )

        area = st.number_input(
            "Module Area (m²)",
            min_value=0.0,
            value=2.0,
            step=0.1,
            format="%.2f"
        )

        operator = st.text_input(
            "Operator",
            placeholder="Test operator name"
        )

    st.markdown("---")

    # Test configuration
    st.markdown("### 2. Test Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            min_value=0.0,
            value=1000.0,
            step=10.0
        )

    with col2:
        temperature = st.number_input(
            "Temperature (°C)",
            min_value=-50.0,
            max_value=100.0,
            value=25.0,
            step=1.0
        )

    with col3:
        spectrum = st.selectbox(
            "Spectrum",
            ["AM1.5G", "AM1.5D", "AM0"]
        )

    # Angle selection
    st.markdown("### 3. Test Angles")

    use_recommended = st.checkbox(
        "Use recommended angles (0°, 10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°)",
        value=True
    )

    if use_recommended:
        test_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    else:
        angle_input = st.text_input(
            "Custom angles (comma-separated)",
            placeholder="e.g., 0, 15, 30, 45, 60, 75, 90"
        )
        try:
            test_angles = [float(x.strip()) for x in angle_input.split(",") if x.strip()]
        except ValueError:
            st.error("Invalid angle format. Use comma-separated numbers.")
            test_angles = []

    if test_angles:
        st.info(f"📐 Testing at {len(test_angles)} angles: {', '.join(f'{a}°' for a in test_angles)}")

    st.markdown("---")

    # Measurements section
    st.markdown("### 4. Measurements")

    if not sample_id or not module_type:
        st.warning("⚠️ Please fill in required fields (Sample ID, Module Type, Technology) to continue.")
    else:
        # Initialize protocol if needed
        if st.session_state.protocol_executor is None and st.button("Initialize Protocol", type="primary"):
            try:
                executor = ProtocolExecutor("iam-001")
                executor.create_protocol(
                    **{
                        "sample_info.sample_id": sample_id,
                        "sample_info.module_type": module_type,
                        "sample_info.manufacturer": manufacturer,
                        "sample_info.serial_number": serial_number,
                        "sample_info.technology": technology,
                        "sample_info.rated_power": rated_power,
                        "sample_info.area": area,
                        "protocol_info.operator": operator,
                        "test_configuration.irradiance": irradiance,
                        "test_configuration.temperature": temperature,
                        "test_configuration.spectrum": spectrum,
                        "test_configuration.angle_range.min": 0,
                        "test_configuration.angle_range.max": max(test_angles) if test_angles else 90,
                    }
                )
                st.session_state.protocol_executor = executor
                st.session_state.measurements = []
                st.success("✅ Protocol initialized!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error initializing protocol: {e}")

        # Add measurements
        if st.session_state.protocol_executor is not None:
            st.markdown("#### Add Measurement")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                angle = st.number_input(
                    "Angle (°)",
                    min_value=0.0,
                    max_value=90.0,
                    value=0.0,
                    step=10.0,
                    key="meas_angle"
                )

            with col2:
                isc = st.number_input(
                    "Isc (A)",
                    min_value=0.0,
                    value=10.0,
                    step=0.1,
                    format="%.3f",
                    key="meas_isc"
                )

            with col3:
                voc = st.number_input(
                    "Voc (V)",
                    min_value=0.0,
                    value=48.0,
                    step=0.1,
                    format="%.2f",
                    key="meas_voc"
                )

            with col4:
                pmax = st.number_input(
                    "Pmax (W)",
                    min_value=0.0,
                    value=400.0,
                    step=1.0,
                    format="%.2f",
                    key="meas_pmax"
                )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("➕ Add Measurement", use_container_width=True):
                    try:
                        st.session_state.protocol_executor.add_measurement(
                            angle=angle,
                            isc=isc,
                            voc=voc,
                            pmax=pmax,
                            irradiance_actual=irradiance,
                            temperature_actual=temperature
                        )
                        st.session_state.measurements.append({
                            "angle": angle,
                            "isc": isc,
                            "voc": voc,
                            "pmax": pmax
                        })
                        st.success(f"✅ Added measurement at {angle}°")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding measurement: {e}")

            # Display current measurements
            if st.session_state.measurements:
                st.markdown(f"#### Current Measurements ({len(st.session_state.measurements)} points)")

                import pandas as pd
                df = pd.DataFrame(st.session_state.measurements)
                st.dataframe(df, use_container_width=True)

                # Validate and analyze
                col1, col2, col3 = st.columns([1, 1, 3])

                with col1:
                    if st.button("🔍 Validate", use_container_width=True):
                        try:
                            validation_results = st.session_state.protocol_executor.validate_protocol()

                            if validation_results["overall_status"] == "pass":
                                st.success("✅ Validation passed!")
                            elif validation_results["overall_status"] == "pass_with_warnings":
                                st.warning(f"⚠️ Validation passed with {len(validation_results['warnings'])} warnings")
                                for warning in validation_results["warnings"]:
                                    st.warning(f"• {warning}")
                            else:
                                st.error(f"❌ Validation failed with {len(validation_results['errors'])} errors")
                                for error in validation_results["errors"]:
                                    st.error(f"• {error}")

                        except Exception as e:
                            st.error(f"❌ Validation error: {e}")

                with col2:
                    if st.button("📊 Analyze", type="primary", use_container_width=True):
                        try:
                            # Run analysis
                            st.session_state.protocol_executor.execute_analysis(create_analyzer)

                            results = st.session_state.protocol_executor.get_analysis_results()

                            st.success("✅ Analysis completed!")

                            # Display results
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    "Fit Quality",
                                    results.get("quality_metrics", {}).get("fit_quality", "N/A").upper()
                                )

                            with col2:
                                st.metric(
                                    "R² Value",
                                    f"{results.get('fitting_parameters', {}).get('r_squared', 0):.4f}"
                                )

                            with col3:
                                st.metric(
                                    "Model",
                                    results.get("fitting_parameters", {}).get("model", "N/A").upper()
                                )

                            # Save option
                            save_path = st.text_input(
                                "Save path",
                                value=f"data/iam-001_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                key="save_path"
                            )

                            if st.button("💾 Save Protocol", use_container_width=True):
                                try:
                                    st.session_state.protocol_executor.save_protocol(Path(save_path))
                                    st.success(f"✅ Protocol saved to {save_path}")
                                except Exception as e:
                                    st.error(f"❌ Error saving: {e}")

                        except Exception as e:
                            st.error(f"❌ Analysis error: {e}")
                            st.exception(e)

                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.protocol_executor = None
                    st.session_state.measurements = []
                    st.rerun()
