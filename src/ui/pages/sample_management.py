"""
Sample Management Page
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, Sample, SampleBatch


def render_sample_management():
    """Render the sample management page"""
    st.title("🔬 Sample Management")

    tab1, tab2 = st.tabs(["Samples", "Add New Sample"])

    with tab1:
        render_sample_list()

    with tab2:
        render_add_sample()


def render_sample_list():
    """Display list of samples"""
    st.header("Sample List")

    db = SessionLocal()

    try:
        samples = db.query(Sample).order_by(Sample.created_at.desc()).all()

        if samples:
            import pandas as pd

            data = []
            for sample in samples:
                data.append({
                    'Sample ID': sample.sample_id,
                    'Serial Number': sample.serial_number or 'N/A',
                    'Type': sample.module_type or 'N/A',
                    'Pmax (W)': sample.rated_power_pmax or 'N/A',
                    'Voc (V)': sample.open_circuit_voltage_voc or 'N/A',
                    'Isc (A)': sample.short_circuit_current_isc or 'N/A',
                    'Max OCP (A)': sample.max_overcurrent_protection or 'N/A',
                    'Status': '✅ Active' if sample.is_active else '❌ Inactive'
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No samples found. Add samples using the 'Add New Sample' tab.")

    finally:
        db.close()


def render_add_sample():
    """Form to add new sample"""
    st.header("Add New Sample")

    with st.form("add_sample_form"):
        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input("Sample ID*", help="Unique identifier for the sample")
            serial_number = st.text_input("Serial Number", help="Manufacturer serial number")
            module_type = st.text_input("Module Type", help="e.g., Monocrystalline, Polycrystalline")

        with col2:
            barcode = st.text_input("Barcode", help="Optional barcode")
            cell_technology = st.text_input("Cell Technology", help="e.g., PERC, TOPCon")
            frame_type = st.text_input("Frame Type", help="e.g., Aluminum, Frameless")

        st.subheader("Electrical Ratings")

        col1, col2, col3 = st.columns(3)

        with col1:
            rated_power = st.number_input("Rated Power Pmax (W)", min_value=0.0, step=1.0)
            rated_voltage = st.number_input("Rated Voltage Vmp (V)", min_value=0.0, step=0.1)

        with col2:
            rated_current = st.number_input("Rated Current Imp (A)", min_value=0.0, step=0.1)
            voc = st.number_input("Open Circuit Voltage Voc (V)", min_value=0.0, step=0.1)

        with col3:
            isc = st.number_input("Short Circuit Current Isc (A)", min_value=0.0, step=0.1)
            max_system_voltage = st.number_input("Max System Voltage (V)", min_value=0.0, step=1.0)

        max_ocp = st.number_input(
            "Max Overcurrent Protection (A)*",
            min_value=0.1,
            step=0.1,
            help="Required for ground continuity test"
        )

        st.subheader("Physical Characteristics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            length = st.number_input("Length (mm)", min_value=0.0, step=1.0)

        with col2:
            width = st.number_input("Width (mm)", min_value=0.0, step=1.0)

        with col3:
            thickness = st.number_input("Thickness (mm)", min_value=0.0, step=0.1)

        with col4:
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)

        notes = st.text_area("Notes", help="Additional information about the sample")

        submitted = st.form_submit_button("Add Sample", type="primary")

        if submitted:
            if not sample_id:
                st.error("Sample ID is required")
                return

            db = SessionLocal()

            try:
                # Check if sample_id already exists
                existing = db.query(Sample).filter(Sample.sample_id == sample_id).first()
                if existing:
                    st.error(f"Sample with ID '{sample_id}' already exists")
                    return

                # Create new sample
                sample = Sample(
                    sample_id=sample_id,
                    serial_number=serial_number or None,
                    module_type=module_type or None,
                    cell_technology=cell_technology or None,
                    frame_type=frame_type or None,
                    barcode=barcode or None,
                    rated_power_pmax=rated_power if rated_power > 0 else None,
                    rated_voltage_vmp=rated_voltage if rated_voltage > 0 else None,
                    rated_current_imp=rated_current if rated_current > 0 else None,
                    open_circuit_voltage_voc=voc if voc > 0 else None,
                    short_circuit_current_isc=isc if isc > 0 else None,
                    max_system_voltage=max_system_voltage if max_system_voltage > 0 else None,
                    max_overcurrent_protection=max_ocp if max_ocp > 0 else None,
                    dimensions_length=length if length > 0 else None,
                    dimensions_width=width if width > 0 else None,
                    dimensions_thickness=thickness if thickness > 0 else None,
                    weight=weight if weight > 0 else None,
                    notes=notes or None,
                    is_active=True
                )

                db.add(sample)
                db.commit()

                st.success(f"Sample '{sample_id}' added successfully!")

            except Exception as e:
                st.error(f"Error adding sample: {e}")

            finally:
                db.close()
