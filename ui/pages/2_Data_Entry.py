"""Data Entry page."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.components.data_entry import DataEntryForm
from ui.components.protocol_selector import ProtocolSelector

st.set_page_config(page_title="Data Entry", page_icon="📊", layout="wide")

st.markdown("# 📊 Measurement Data Entry")
st.markdown("Enter or import measurement data for your test run")

# Initialize session state
if 'measurements' not in st.session_state:
    st.session_state.measurements = []

if 'selected_protocol_id' not in st.session_state:
    st.warning("⚠️ No protocol selected. Please go to Protocol Setup first.")
    st.stop()

# Load protocol
protocol_selector = ProtocolSelector()
protocol_data = protocol_selector.get_protocol_data(st.session_state.selected_protocol_id)

if not protocol_data:
    st.error("Could not load protocol data")
    st.stop()

# Create data entry form
data_entry_form = DataEntryForm(protocol_data)

# Tabs for different entry methods
tab1, tab2, tab3 = st.tabs(["Manual Entry", "Bulk Import", "Measurements Summary"])

with tab1:
    st.markdown("## Manual Data Entry")

    # Measurement type selection
    measurement_type = st.selectbox(
        "Measurement Type",
        ["initial", "during_exposure", "post_exposure"],
        format_func=lambda x: x.replace('_', ' ').title()
    )

    # Render form
    measurement_data = data_entry_form.render_measurement_form(
        measurement_type=measurement_type,
        key_prefix=f"entry_{len(st.session_state.measurements)}"
    )

    if measurement_data:
        # Add sequence number
        measurement_data['measurement_sequence'] = len(st.session_state.measurements) + 1

        # Add to session state
        st.session_state.measurements.append(measurement_data)

        st.success(f"✅ Measurement #{measurement_data['measurement_sequence']} saved!")
        st.rerun()

with tab2:
    st.markdown("## Bulk Import")

    imported_data = data_entry_form.render_bulk_import(key="data_entry_bulk")

    if imported_data:
        # Add sequence numbers
        for i, measurement in enumerate(imported_data):
            measurement['measurement_sequence'] = len(st.session_state.measurements) + i + 1

        # Add to session state
        st.session_state.measurements.extend(imported_data)
        st.rerun()

with tab3:
    st.markdown("## Measurements Summary")

    if st.session_state.measurements:
        data_entry_form.display_measurement_summary(st.session_state.measurements)

        # Actions
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear All Measurements", use_container_width=True):
                st.session_state.measurements = []
                st.rerun()

        with col2:
            if st.button("💾 Save to Database", use_container_width=True):
                st.success("Measurements saved!")
                # TODO: Save to database

        with col3:
            if st.button("📥 Export CSV", use_container_width=True):
                import pandas as pd
                df = pd.DataFrame(st.session_state.measurements)
                csv = df.to_csv(index=False)

                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="measurements.csv",
                    mime="text/csv"
                )
    else:
        st.info("No measurements entered yet. Use the 'Manual Entry' or 'Bulk Import' tabs to add data.")

# Sidebar
with st.sidebar:
    st.markdown("### Current Status")

    st.metric("Total Measurements", len(st.session_state.measurements))

    if st.session_state.measurements:
        import pandas as pd
        df = pd.DataFrame(st.session_state.measurements)

        if 'pmax' in df.columns:
            st.metric("Latest Pmax", f"{df['pmax'].iloc[-1]:.2f} W")

        # Measurement type breakdown
        if 'measurement_type' in df.columns:
            st.markdown("**By Type:**")
            type_counts = df['measurement_type'].value_counts()
            for mtype, count in type_counts.items():
                st.markdown(f"- {mtype.replace('_', ' ').title()}: {count}")

    st.markdown("---")
    st.info(f"Protocol: {st.session_state.selected_protocol_id}")
