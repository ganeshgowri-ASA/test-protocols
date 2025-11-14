"""Data management page."""

import streamlit as st
import pandas as pd


def render():
    """Render data management page."""
    st.title("🗂️ Data Management")

    tab1, tab2, tab3 = st.tabs(["Samples", "Equipment", "Export"])

    with tab1:
        st.subheader("Sample Registry")

        # Mock sample data
        samples = pd.DataFrame({
            'Sample ID': ['SAMPLE-001', 'SAMPLE-002', 'SAMPLE-003'],
            'Manufacturer': ['SunPower', 'LG Solar', 'Hanwha Q-Cells'],
            'Cell Type': ['mono-PERC', 'mono-PERC', 'mono-TOPCon'],
            'Efficiency (%)': [22.0, 21.5, 22.8],
            'Area (cm²)': [243.36, 243.36, 244.30],
            'Pmax (W)': [5.0, 4.9, 5.2],
            'Status': ['Active', 'Tested', 'Active']
        })

        st.dataframe(samples, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("➕ Add Sample", type="primary")
        with col2:
            st.button("✏️ Edit Sample")
        with col3:
            st.button("🗑️ Delete Sample")

        st.markdown("---")

        # Sample details form
        with st.expander("Add New Sample"):
            col1, col2 = st.columns(2)

            with col1:
                st.text_input("Sample ID")
                st.text_input("Manufacturer")
                st.text_input("Cell Type")
                st.number_input("Efficiency (%)", min_value=0.0, max_value=30.0)
                st.number_input("Cell Area (cm²)", min_value=0.0)

            with col2:
                st.text_input("Manufacturing Date")
                st.number_input("Initial Pmax (W)", min_value=0.0)
                st.number_input("Initial Voc (V)", min_value=0.0)
                st.number_input("Initial Isc (A)", min_value=0.0)
                st.number_input("Initial Fill Factor", min_value=0.0, max_value=1.0)

            st.button("💾 Save Sample")

    with tab2:
        st.subheader("Equipment Management")

        # Mock equipment data
        equipment = pd.DataFrame({
            'Equipment ID': ['TC-001', 'EL-SYS-001', 'SIM-AAA-001', 'IV-001'],
            'Name': ['Thermal Chamber', 'EL Imaging System', 'Solar Simulator', 'IV Tracer'],
            'Type': ['thermal_chamber', 'el_system', 'solar_simulator', 'iv_tracer'],
            'Manufacturer': ['Espec', 'BT Imaging', 'Abet Technologies', 'Keithley'],
            'Last Calibration': ['2025-06-01', '2025-05-15', '2025-07-01', '2025-08-01'],
            'Next Calibration': ['2026-06-01', '2026-05-15', '2026-07-01', '2026-08-01'],
            'Status': ['✅ Operational', '✅ Operational', '✅ Operational', '✅ Operational']
        })

        st.dataframe(equipment, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("➕ Add Equipment", type="primary")
        with col2:
            st.button("📅 Update Calibration")
        with col3:
            st.button("📄 View Certificates")

        st.markdown("---")

        st.info("""
        **Calibration Reminders:**
        - Solar Simulator (SIM-AAA-001): Due in 234 days
        - All other equipment within calibration period
        """)

    with tab3:
        st.subheader("Data Export")

        st.write("Export test data in various formats for external analysis or archival.")

        export_type = st.selectbox(
            "Export Type",
            ["Test Results", "Sample Database", "Equipment Records", "Protocol Definitions"]
        )

        col1, col2 = st.columns(2)

        with col1:
            date_from = st.date_input("From Date")
        with col2:
            date_to = st.date_input("To Date")

        export_format = st.radio(
            "Export Format",
            ["CSV", "Excel", "JSON", "PDF Report"]
        )

        include_options = st.multiselect(
            "Include in Export",
            ["Raw Measurements", "Analysis Results", "EL Images", "IV Curves", "Metadata"],
            default=["Raw Measurements", "Analysis Results"]
        )

        st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            st.button("📊 Preview Export")

        with col3:
            st.button("📥 Download Export", type="primary")

        st.markdown("---")

        st.subheader("Backup & Archive")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Database Backup**")
            st.button("💾 Create Backup")
            st.caption("Last backup: 2025-11-14 02:00:00")

        with col2:
            st.write("**Data Archive**")
            st.button("📦 Archive Old Data")
            st.caption("Archive data older than 1 year")
