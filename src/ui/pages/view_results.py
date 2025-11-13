"""View test results page."""

import streamlit as st
from pathlib import Path
import json
import sys
import plotly.graph_objects as go
import plotly.express as px

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render() -> None:
    """Render the view results page."""

    st.markdown('<div class="main-header">📊 View Test Results</div>', unsafe_allow_html=True)

    # File selection
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        st.info("No test results found. Create a new test to get started.")
        if st.button("➕ Create New Test"):
            st.session_state.page = "➕ New Test"
            st.rerun()
        return

    # File selector
    file_options = {f.name: f for f in json_files}
    selected_file = st.selectbox(
        "Select test result file",
        options=list(file_options.keys())
    )

    if selected_file:
        file_path = file_options[selected_file]

        try:
            with open(file_path, "r") as f:
                protocol_data = json.load(f)

            # Display protocol information
            st.markdown("### Test Information")

            col1, col2, col3 = st.columns(3)

            protocol_info = protocol_data.get("protocol_info", {})
            sample_info = protocol_data.get("sample_info", {})

            with col1:
                st.markdown(f"**Protocol ID:** {protocol_info.get('protocol_id', 'N/A')}")
                st.markdown(f"**Sample ID:** {sample_info.get('sample_id', 'N/A')}")
                st.markdown(f"**Module Type:** {sample_info.get('module_type', 'N/A')}")

            with col2:
                st.markdown(f"**Manufacturer:** {sample_info.get('manufacturer', 'N/A')}")
                st.markdown(f"**Technology:** {sample_info.get('technology', 'N/A')}")
                st.markdown(f"**Rated Power:** {sample_info.get('rated_power', 'N/A')} W")

            with col3:
                st.markdown(f"**Test Date:** {protocol_info.get('test_date', 'N/A')}")
                st.markdown(f"**Operator:** {protocol_info.get('operator', 'N/A')}")
                st.markdown(f"**Facility:** {protocol_info.get('facility', 'N/A')}")

            st.markdown("---")

            # Measurements
            st.markdown("### Measurements")

            measurements = protocol_data.get("measurements", [])
            if measurements:
                import pandas as pd
                df_meas = pd.DataFrame(measurements)

                # Display as table
                st.dataframe(df_meas, use_container_width=True)

                # Plot measurements
                fig = go.Figure()

                angles = [m["angle"] for m in measurements]
                powers = [m["pmax"] for m in measurements]

                fig.add_trace(go.Scatter(
                    x=angles,
                    y=powers,
                    mode='markers+lines',
                    name='Pmax',
                    marker=dict(size=10, color='blue'),
                    line=dict(width=2)
                ))

                fig.update_layout(
                    title="Power vs Angle of Incidence",
                    xaxis_title="Angle of Incidence (°)",
                    yaxis_title="Maximum Power (W)",
                    template="plotly_white",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Analysis Results
            if "analysis_results" in protocol_data:
                st.markdown("### Analysis Results")

                analysis = protocol_data["analysis_results"]

                # Quality metrics
                col1, col2, col3, col4 = st.columns(4)

                quality_metrics = analysis.get("quality_metrics", {})
                fitting_params = analysis.get("fitting_parameters", {})

                with col1:
                    fit_quality = quality_metrics.get("fit_quality", "N/A")
                    if fit_quality == "excellent":
                        st.success(f"**Fit Quality**\n\n{fit_quality.upper()}")
                    elif fit_quality == "good":
                        st.info(f"**Fit Quality**\n\n{fit_quality.upper()}")
                    else:
                        st.warning(f"**Fit Quality**\n\n{fit_quality.upper()}")

                with col2:
                    r_squared = fitting_params.get("r_squared", 0)
                    st.metric("R² Value", f"{r_squared:.4f}")

                with col3:
                    rmse = fitting_params.get("rmse", 0)
                    st.metric("RMSE", f"{rmse:.4f}")

                with col4:
                    model = fitting_params.get("model", "N/A")
                    st.metric("Model", model.upper())

                # Data completeness
                completeness = quality_metrics.get("data_completeness", 0)
                st.progress(completeness / 100, text=f"Data Completeness: {completeness:.1f}%")

                # IAM Curve
                iam_curve = analysis.get("iam_curve", [])
                if iam_curve:
                    st.markdown("#### IAM Curve")

                    fig = go.Figure()

                    iam_angles = [point["angle"] for point in iam_curve]
                    iam_values = [point["iam"] for point in iam_curve]

                    fig.add_trace(go.Scatter(
                        x=iam_angles,
                        y=iam_values,
                        mode='markers+lines',
                        name='IAM',
                        marker=dict(size=10, color='green'),
                        line=dict(width=2)
                    ))

                    # Add reference line at IAM = 1
                    fig.add_hline(y=1.0, line_dash="dash", line_color="red",
                                annotation_text="IAM = 1.0")

                    fig.update_layout(
                        title="Incidence Angle Modifier Curve",
                        xaxis_title="Angle of Incidence (°)",
                        yaxis_title="IAM (normalized)",
                        template="plotly_white",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Display IAM values at key angles
                    st.markdown("#### IAM Values at Key Angles")

                    col1, col2, col3, col4, col5 = st.columns(5)

                    key_angles = [0, 30, 50, 60, 70]
                    cols = [col1, col2, col3, col4, col5]

                    for angle, col in zip(key_angles, cols):
                        # Find closest angle in data
                        closest = min(iam_curve, key=lambda x: abs(x["angle"] - angle))
                        with col:
                            st.metric(f"{angle}°", f"{closest['iam']:.3f}")

                # Model parameters
                if "parameters" in fitting_params:
                    st.markdown("#### Model Parameters")

                    params = fitting_params["parameters"]
                    param_data = []

                    for param_name, param_info in params.items():
                        if isinstance(param_info, dict):
                            param_data.append({
                                "Parameter": param_name,
                                "Value": f"{param_info.get('value', 0):.6f}",
                                "Error": f"±{param_info.get('error', 0):.6f}"
                            })

                    if param_data:
                        import pandas as pd
                        df_params = pd.DataFrame(param_data)
                        st.table(df_params)

                # Warnings
                warnings = quality_metrics.get("validation_warnings", [])
                if warnings:
                    st.markdown("#### Validation Warnings")
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")

            # Export options
            st.markdown("---")
            st.markdown("### Export")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Download JSON", use_container_width=True):
                    st.download_button(
                        label="Download Protocol Data",
                        data=json.dumps(protocol_data, indent=2),
                        file_name=f"protocol_{selected_file}",
                        mime="application/json",
                        use_container_width=True
                    )

            with col2:
                if st.button("📄 Generate Report", use_container_width=True):
                    st.info("Report generation feature coming soon!")

        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.exception(e)
