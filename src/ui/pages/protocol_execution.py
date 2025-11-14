"""Protocol execution page."""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime


def render():
    """Render protocol execution page."""
    st.title("🔬 Protocol Execution")

    # Protocol selection
    st.subheader("1. Select Protocol")

    protocols_dir = Path(__file__).parent.parent.parent.parent / "protocols"

    # Find available protocols
    available_protocols = []
    if protocols_dir.exists():
        for protocol_file in protocols_dir.rglob("protocol.json"):
            with open(protocol_file, 'r') as f:
                protocol_def = json.load(f)
                available_protocols.append({
                    'id': protocol_def['protocol_id'],
                    'name': protocol_def['name'],
                    'category': protocol_def['category'],
                    'path': protocol_file
                })

    if not available_protocols:
        st.error("No protocols found. Please ensure protocol definitions are in the protocols directory.")
        return

    protocol_options = {p['id']: f"{p['id']} - {p['name']}" for p in available_protocols}
    selected_protocol_id = st.selectbox(
        "Protocol",
        options=list(protocol_options.keys()),
        format_func=lambda x: protocol_options[x]
    )

    # Load selected protocol
    selected_protocol = next(p for p in available_protocols if p['id'] == selected_protocol_id)
    with open(selected_protocol['path'], 'r') as f:
        protocol_def = json.load(f)

    # Display protocol information
    with st.expander("📋 Protocol Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Protocol ID:** {protocol_def['protocol_id']}")
            st.write(f"**Version:** {protocol_def['version']}")
            st.write(f"**Category:** {protocol_def['category']}")
        with col2:
            st.write(f"**Standard:** {protocol_def.get('reference_standard', 'N/A')}")
            st.write(f"**Created:** {protocol_def.get('created_date', 'N/A')}")

        st.write(f"**Description:** {protocol_def['description']}")

    st.markdown("---")

    # Test parameters configuration
    st.subheader("2. Configure Test Parameters")

    test_params = {}
    param_defs = protocol_def.get('test_parameters', {})

    col1, col2 = st.columns(2)

    for i, (param_name, param_config) in enumerate(param_defs.items()):
        param_type = param_config.get('type')
        default = param_config.get('default')
        description = param_config.get('description', '')
        unit = param_config.get('unit', '')

        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            label = f"{param_name.replace('_', ' ').title()}"
            if unit:
                label += f" ({unit})"

            if param_type == 'enum':
                options = param_config.get('options', [])
                test_params[param_name] = st.selectbox(
                    label,
                    options=options,
                    index=options.index(default) if default in options else 0,
                    help=description
                )
            elif param_type == 'integer':
                min_val = param_config.get('min', 0)
                max_val = param_config.get('max', 1000)
                test_params[param_name] = st.number_input(
                    label,
                    min_value=min_val,
                    max_value=max_val,
                    value=default if default is not None else min_val,
                    step=1,
                    help=description
                )
            elif param_type == 'float':
                min_val = param_config.get('min', 0.0)
                max_val = param_config.get('max', 1000.0)
                test_params[param_name] = st.number_input(
                    label,
                    min_value=min_val,
                    max_value=max_val,
                    value=default if default is not None else min_val,
                    step=0.1,
                    help=description
                )

    st.markdown("---")

    # Sample metadata upload
    st.subheader("3. Sample Information")

    metadata_fields = protocol_def.get('data_collection', {}).get('metadata', {}).get('required_fields', [])

    upload_method = st.radio(
        "Sample metadata input method",
        ["Manual Entry", "CSV Upload"]
    )

    samples = []

    if upload_method == "Manual Entry":
        num_samples = st.number_input(
            "Number of samples",
            min_value=1,
            max_value=20,
            value=1,
            step=1
        )

        for i in range(num_samples):
            with st.expander(f"Sample {i+1}", expanded=(i == 0)):
                sample = {}
                col1, col2 = st.columns(2)

                # Common fields in first column
                with col1:
                    sample['sample_id'] = st.text_input(
                        f"Sample ID",
                        value=f"SAMPLE-{i+1:03d}",
                        key=f"sample_id_{i}"
                    )
                    sample['manufacturer'] = st.text_input(
                        "Manufacturer",
                        key=f"manufacturer_{i}"
                    )
                    sample['cell_type'] = st.text_input(
                        "Cell Type",
                        value="mono-PERC",
                        key=f"cell_type_{i}"
                    )
                    sample['cell_efficiency'] = st.number_input(
                        "Cell Efficiency (%)",
                        min_value=0.0,
                        max_value=30.0,
                        value=22.0,
                        step=0.1,
                        key=f"efficiency_{i}"
                    )
                    sample['cell_area'] = st.number_input(
                        "Cell Area (cm²)",
                        min_value=0.0,
                        value=243.36,
                        step=0.01,
                        key=f"area_{i}"
                    )

                with col2:
                    sample['manufacturing_date'] = st.text_input(
                        "Manufacturing Date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        key=f"mfg_date_{i}"
                    )
                    sample['initial_pmax'] = st.number_input(
                        "Initial Pmax (W)",
                        min_value=0.0,
                        value=5.0,
                        step=0.01,
                        key=f"pmax_{i}"
                    )
                    sample['initial_voc'] = st.number_input(
                        "Initial Voc (V)",
                        min_value=0.0,
                        value=0.68,
                        step=0.001,
                        key=f"voc_{i}"
                    )
                    sample['initial_isc'] = st.number_input(
                        "Initial Isc (A)",
                        min_value=0.0,
                        value=9.5,
                        step=0.01,
                        key=f"isc_{i}"
                    )
                    sample['initial_ff'] = st.number_input(
                        "Initial Fill Factor",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.80,
                        step=0.001,
                        key=f"ff_{i}"
                    )

                samples.append(sample)

    else:  # CSV Upload
        st.write("Upload a CSV file with sample metadata. Required columns:")
        st.code(", ".join(metadata_fields))

        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df)

            samples = df.to_dict('records')

    st.markdown("---")

    # Execution controls
    st.subheader("4. Execute Protocol")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        run_id = st.text_input(
            "Test Run ID",
            value=f"{protocol_def['protocol_id']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")
        validate_button = st.button("✅ Validate Setup", type="secondary")

    with col3:
        st.write("")  # Spacing
        st.write("")
        execute_button = st.button("🚀 Start Execution", type="primary")

    if validate_button:
        # Validation logic
        st.info("Validating configuration...")

        errors = []

        # Check sample count
        min_samples = protocol_def.get('data_collection', {}).get('sample_size', {}).get('min', 1)
        if len(samples) < min_samples:
            errors.append(f"Minimum {min_samples} samples required, got {len(samples)}")

        # Check required fields
        for sample in samples:
            for field in metadata_fields:
                if field not in sample or not sample[field]:
                    errors.append(f"Sample {sample.get('sample_id', 'Unknown')}: Missing field '{field}'")

        if errors:
            st.error("Validation failed:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success("✅ Configuration is valid! Ready to execute.")

    if execute_button:
        st.success(f"🚀 Starting test execution: {run_id}")
        st.info("""
        In production, this would:
        1. Create test run in database
        2. Initialize measurement equipment
        3. Begin protocol execution
        4. Monitor progress in real-time

        For demonstration purposes, the execution flow is simulated.
        """)

        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        workflow_steps = protocol_def.get('workflow', {}).get('steps', [])

        for i, step in enumerate(workflow_steps):
            progress = (i + 1) / len(workflow_steps)
            progress_bar.progress(progress)
            status_text.text(f"Step {step['step']}: {step['name']}")

        st.success("✅ Protocol execution complete!")
        st.balloons()
