"""
Equipment Management Page
"""

import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, Equipment, EquipmentCalibration


def render_equipment_management():
    """Render the equipment management page"""
    st.title("🔧 Equipment Management")

    tab1, tab2 = st.tabs(["Equipment List", "Add New Equipment"])

    with tab1:
        render_equipment_list()

    with tab2:
        render_add_equipment()


def render_equipment_list():
    """Display list of equipment"""
    st.header("Equipment List")

    db = SessionLocal()

    try:
        equipment_list = db.query(Equipment).order_by(Equipment.created_at.desc()).all()

        if equipment_list:
            import pandas as pd

            data = []
            for eq in equipment_list:
                # Check calibration status
                cal_status = "N/A"
                if eq.calibration_required:
                    if eq.next_calibration_date:
                        if eq.next_calibration_date < datetime.utcnow():
                            cal_status = "🔴 Overdue"
                        elif eq.next_calibration_date < datetime.utcnow() + timedelta(days=30):
                            cal_status = "🟡 Due Soon"
                        else:
                            cal_status = "🟢 Valid"
                    else:
                        cal_status = "⚪ Not Calibrated"

                data.append({
                    'Equipment ID': eq.equipment_id,
                    'Name': eq.name,
                    'Type': eq.equipment_type,
                    'Manufacturer': eq.manufacturer or 'N/A',
                    'Model': eq.model or 'N/A',
                    'Serial Number': eq.serial_number or 'N/A',
                    'Calibration Status': cal_status,
                    'Next Calibration': eq.next_calibration_date.strftime('%Y-%m-%d') if eq.next_calibration_date else 'N/A',
                    'Status': '✅ Active' if eq.is_active else '❌ Inactive'
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No equipment found. Add equipment using the 'Add New Equipment' tab.")

    finally:
        db.close()


def render_add_equipment():
    """Form to add new equipment"""
    st.header("Add New Equipment")

    with st.form("add_equipment_form"):
        col1, col2 = st.columns(2)

        with col1:
            equipment_id = st.text_input("Equipment ID*", help="Unique identifier")
            name = st.text_input("Equipment Name*", help="Descriptive name")
            equipment_type = st.text_input("Type*", help="e.g., Ground Continuity Tester")

        with col2:
            manufacturer = st.text_input("Manufacturer")
            model = st.text_input("Model")
            serial_number = st.text_input("Serial Number")

        location = st.text_input("Location", help="Physical location of the equipment")

        st.subheader("Calibration")

        calibration_required = st.checkbox("Calibration Required", value=True)

        col1, col2 = st.columns(2)

        with col1:
            last_calibration = st.date_input(
                "Last Calibration Date",
                value=None,
                help="Leave empty if not yet calibrated"
            )

        with col2:
            calibration_interval = st.number_input(
                "Calibration Interval (days)",
                min_value=1,
                value=365,
                step=1
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Equipment", type="primary")

        if submitted:
            if not equipment_id or not name or not equipment_type:
                st.error("Equipment ID, Name, and Type are required")
                return

            db = SessionLocal()

            try:
                # Check if equipment_id already exists
                existing = db.query(Equipment).filter(Equipment.equipment_id == equipment_id).first()
                if existing:
                    st.error(f"Equipment with ID '{equipment_id}' already exists")
                    return

                # Calculate next calibration date
                next_calibration = None
                if calibration_required and last_calibration:
                    next_calibration = datetime.combine(
                        last_calibration,
                        datetime.min.time()
                    ) + timedelta(days=calibration_interval)

                # Create new equipment
                equipment = Equipment(
                    equipment_id=equipment_id,
                    name=name,
                    equipment_type=equipment_type,
                    manufacturer=manufacturer or None,
                    model=model or None,
                    serial_number=serial_number or None,
                    location=location or None,
                    calibration_required=calibration_required,
                    calibration_interval_days=calibration_interval if calibration_required else None,
                    last_calibration_date=datetime.combine(last_calibration, datetime.min.time()) if last_calibration else None,
                    next_calibration_date=next_calibration,
                    notes=notes or None,
                    is_active=True
                )

                db.add(equipment)
                db.commit()

                st.success(f"Equipment '{equipment_id}' added successfully!")

            except Exception as e:
                st.error(f"Error adding equipment: {e}")

            finally:
                db.close()
