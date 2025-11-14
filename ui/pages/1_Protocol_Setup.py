"""Protocol Setup page."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.components.protocol_selector import ProtocolSelector
from database import init_database, get_session, Sample, Protocol
import json

st.set_page_config(page_title="Protocol Setup", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Protocol Setup")
st.markdown("Configure test parameters and select samples for testing")

# Initialize session state
if 'selected_protocol_id' not in st.session_state:
    st.session_state.selected_protocol_id = None

if 'selected_sample_id' not in st.session_state:
    st.session_state.selected_sample_id = None

# Protocol Selection
st.markdown("## 1. Select Protocol")

protocol_selector = ProtocolSelector()
selected_protocol_id = protocol_selector.render(key="setup_protocol_selector")

if selected_protocol_id:
    st.session_state.selected_protocol_id = selected_protocol_id

    # Display protocol information
    with st.expander("📋 Protocol Details", expanded=False):
        protocol_selector.display_protocol_info(selected_protocol_id)

# Sample Selection/Creation
st.markdown("## 2. Select or Create Sample")

tab1, tab2 = st.tabs(["Select Existing Sample", "Create New Sample"])

with tab1:
    st.markdown("### Select from existing samples")

    # TODO: Load samples from database
    # For now, use dummy data
    sample_options = ["No samples in database"]
    selected_sample = st.selectbox("Sample", sample_options)

    if st.button("Load Sample"):
        st.info("Sample loading functionality will be implemented")

with tab2:
    st.markdown("### Create a new sample")

    with st.form("new_sample_form"):
        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input("Sample ID*", placeholder="e.g., PV-2025-001")
            manufacturer = st.text_input("Manufacturer*", placeholder="e.g., SolarTech")
            model = st.text_input("Model*", placeholder="e.g., ST-300W-Mono")
            serial_number = st.text_input("Serial Number", placeholder="e.g., SN123456")

        with col2:
            technology = st.selectbox(
                "Technology*",
                ["mono-Si", "poly-Si", "PERC", "n-type", "HJT", "TOPCon", "thin-film"]
            )
            rated_power = st.number_input("Rated Power (W)*", min_value=0.0, value=300.0)
            rated_voltage = st.number_input("Rated Voltage (V)*", min_value=0.0, value=40.0)
            rated_current = st.number_input("Rated Current (A)*", min_value=0.0, value=9.0)

        col3, col4 = st.columns(2)

        with col3:
            area = st.number_input("Module Area (m²)", min_value=0.0, value=1.6)
            num_cells = st.number_input("Number of Cells", min_value=1, value=60, step=1)

        with col4:
            location = st.text_input("Storage Location", placeholder="e.g., Lab A, Shelf 3")

        notes = st.text_area("Notes", placeholder="Additional information about the sample")

        submitted = st.form_submit_button("Create Sample")

        if submitted:
            if sample_id and manufacturer and model:
                st.success(f"Sample {sample_id} created successfully!")
                st.session_state.selected_sample_id = sample_id
                # TODO: Save to database
            else:
                st.error("Please fill in all required fields (marked with *)")

# Test Run Configuration
if st.session_state.selected_protocol_id and st.session_state.selected_sample_id:
    st.markdown("## 3. Configure Test Run")

    with st.form("test_run_config"):
        col1, col2 = st.columns(2)

        with col1:
            test_run_id = st.text_input(
                "Test Run ID*",
                placeholder=f"{st.session_state.selected_protocol_id}-{st.session_state.selected_sample_id}-001"
            )
            operator = st.text_input("Operator Name*", placeholder="Your name")

        with col2:
            import datetime
            start_date = st.date_input("Start Date", value=datetime.datetime.now())
            start_time = st.time_input("Start Time", value=datetime.datetime.now().time())

        test_notes = st.text_area("Test Notes", placeholder="Any special conditions or notes")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

        with col_btn1:
            start_test = st.form_submit_button("▶️ Start Test", use_container_width=True)

        with col_btn2:
            save_config = st.form_submit_button("💾 Save Configuration", use_container_width=True)

        if start_test:
            if test_run_id and operator:
                st.success(f"Test run {test_run_id} started!")
                st.balloons()
                # TODO: Create test run in database
            else:
                st.error("Please fill in Test Run ID and Operator Name")

        if save_config:
            st.info("Configuration saved for later")

else:
    st.info("👆 Please select a protocol and sample to configure test run")

# Sidebar
with st.sidebar:
    st.markdown("### Current Configuration")

    if st.session_state.selected_protocol_id:
        st.success(f"✅ Protocol: {st.session_state.selected_protocol_id}")
    else:
        st.warning("⚠️ No protocol selected")

    if st.session_state.selected_sample_id:
        st.success(f"✅ Sample: {st.session_state.selected_sample_id}")
    else:
        st.warning("⚠️ No sample selected")

    st.markdown("---")

    if st.button("🔄 Reset Configuration"):
        st.session_state.selected_protocol_id = None
        st.session_state.selected_sample_id = None
        st.rerun()
