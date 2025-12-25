"""
Equipment Management Module
===========================
Manage laboratory equipment and calibration records.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import Equipment, CalibrationRecord, EquipmentStatus
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="Equipment Management", page_icon="🔧")

# Render navigation
render_header("Equipment Management", "Manage laboratory equipment and calibration records")
render_sidebar_navigation()


def generate_calibration_number() -> str:
    """Generate unique calibration number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"CAL-{timestamp[-10:]}"


def main():
    """Main equipment management page"""

    tabs = st.tabs(["📋 Equipment List", "📅 Calibration Tracker", "➕ Add Equipment"])

    with tabs[0]:
        render_equipment_list()

    with tabs[1]:
        render_calibration_tracker()

    with tabs[2]:
        render_add_equipment()


def render_equipment_list():
    """Render list of equipment with filtering"""

    st.subheader("Current Equipment Inventory")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "Testing Equipment", "Imaging Equipment", "Environmental Testing",
             "Measurement Device", "Calibration Standard", "chamber", "tester", "simulator"]
        )
    with col2:
        status_options = ["All"] + [s.value for s in EquipmentStatus]
        status_filter = st.selectbox("Status", status_options)
    with col3:
        search = st.text_input("Search Equipment", placeholder="Search by name or ID")

    try:
        with get_db() as db:
            # Build query with filters
            query = select(Equipment)

            if category_filter != "All":
                query = query.where(Equipment.category == category_filter)

            if status_filter != "All":
                query = query.where(Equipment.status == status_filter)

            if search:
                search_term = f"%{search}%"
                query = query.where(
                    (Equipment.name.ilike(search_term)) |
                    (Equipment.equipment_code.ilike(search_term))
                )

            query = query.order_by(Equipment.equipment_code)
            equipment_list = db.execute(query).scalars().all()

            if equipment_list:
                # Extract data while session is open
                equipment_data = []
                for eq in equipment_list:
                    equipment_data.append({
                        'id': eq.id,
                        'equipment_code': eq.equipment_code,
                        'name': eq.name,
                        'category': eq.category,
                        'manufacturer': eq.manufacturer,
                        'model': eq.model,
                        'status': eq.status.value if hasattr(eq.status, 'value') else str(eq.status),
                        'location': eq.location,
                        'last_calibration_date': eq.last_calibration_date,
                        'next_calibration_date': eq.next_calibration_date
                    })

                # Convert to DataFrame
                df = pd.DataFrame(equipment_data)

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Equipment", len(df))
                with col2:
                    available_count = len(df[df['status'] == 'available'])
                    st.metric("Available", available_count)
                with col3:
                    in_use_count = len(df[df['status'] == 'in_use'])
                    st.metric("In Use", in_use_count)
                with col4:
                    st.metric("Categories", df['category'].nunique() if 'category' in df.columns else 0)

                st.markdown("---")

                # Display equipment table
                display_cols = ['equipment_code', 'name', 'category', 'manufacturer', 'model', 'status']
                st.dataframe(
                    df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )

                # Equipment details
                st.markdown("### Equipment Details")
                equipment_options = {f"{eq['equipment_code']} - {eq['name']}": eq for eq in equipment_data}

                if equipment_options:
                    selected_key = st.selectbox(
                        "Select equipment for details",
                        options=list(equipment_options.keys())
                    )

                    if selected_key:
                        eq_data = equipment_options[selected_key]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Equipment Code:** {eq_data.get('equipment_code', 'N/A')}")
                            st.markdown(f"**Name:** {eq_data.get('name', 'N/A')}")
                            st.markdown(f"**Category:** {eq_data.get('category', 'N/A')}")
                            st.markdown(f"**Manufacturer:** {eq_data.get('manufacturer', 'N/A')}")

                        with col2:
                            st.markdown(f"**Model:** {eq_data.get('model', 'N/A')}")
                            st.markdown(f"**Status:** {eq_data.get('status', 'N/A')}")
                            st.markdown(f"**Location:** {eq_data.get('location', 'N/A')}")
                            if eq_data.get('next_calibration_date'):
                                st.markdown(f"**Next Calibration:** {eq_data['next_calibration_date'].strftime('%Y-%m-%d')}")
            else:
                st.info("No equipment found matching the filters.")

    except Exception as e:
        st.error(f"Error fetching equipment data: {str(e)}")


def render_calibration_tracker():
    """Render calibration schedule and records"""

    st.subheader("Calibration Schedule & Records")

    try:
        with get_db() as db:
            # Get calibration records with equipment details using join
            query = select(
                CalibrationRecord,
                Equipment.equipment_code,
                Equipment.name.label('equipment_name'),
                Equipment.category
            ).join(
                Equipment, CalibrationRecord.equipment_id == Equipment.id
            ).order_by(desc(CalibrationRecord.next_calibration_date))

            results = db.execute(query).all()

            # Extract data while session is open
            cal_data = []
            for row in results:
                record = row[0]  # CalibrationRecord object
                cal_data.append({
                    'equipment_code': row.equipment_code,
                    'equipment_name': row.equipment_name,
                    'category': row.category,
                    'calibration_date': record.calibration_date,
                    'next_calibration_date': record.next_calibration_date,
                    'calibration_passed': 'Pass' if record.calibration_passed else 'Fail' if record.calibration_passed is False else 'N/A',
                    'performed_by': record.performed_by,
                    'certificate_number': record.certificate_number
                })

            # Get equipment list for dropdown (extract data while session is open)
            equipment_query = select(Equipment).order_by(Equipment.equipment_code)
            equipment_list = db.execute(equipment_query).scalars().all()
            equipment_options = {f"{eq.equipment_code} - {eq.name}": eq.id for eq in equipment_list}

        if cal_data:
            df_cal = pd.DataFrame(cal_data)
            st.markdown("#### Complete Calibration Schedule")
            st.dataframe(df_cal, use_container_width=True, hide_index=True)
        else:
            st.info("No calibration records found.")

        # Add calibration record form
        st.markdown("---")
        st.markdown("#### Add Calibration Record")

        if not equipment_options:
            st.warning("No equipment available. Please add equipment first.")
            return

        with st.form("calibration_form"):
            col1, col2 = st.columns(2)

            with col1:
                selected_eq = st.selectbox("Equipment", options=list(equipment_options.keys()))
                cal_date = st.date_input("Calibration Date", value=datetime.now())
                cal_due_date = st.date_input("Next Calibration Due", value=datetime.now() + timedelta(days=365))
                calibrated_by = st.text_input("Calibrated By")

            with col2:
                cal_agency = st.text_input("Calibration Agency / Provider")
                certificate_num = st.text_input("Certificate Number")
                cal_result = st.selectbox("Calibration Result", ["Pass", "Fail", "Conditional Pass"])
                remarks = st.text_area("Notes/Remarks")

            submitted = st.form_submit_button("Add Calibration Record")

            if submitted:
                if not calibrated_by:
                    st.error("Please enter who performed the calibration")
                    return

                try:
                    equipment_id = equipment_options[selected_eq]
                    calibration_number = generate_calibration_number()

                    calibration_data = {
                        'calibration_number': calibration_number,
                        'equipment_id': equipment_id,
                        'calibration_date': datetime.combine(cal_date, datetime.min.time()),
                        'next_calibration_date': datetime.combine(cal_due_date, datetime.min.time()),
                        'performed_by': calibrated_by,
                        'provider_certificate': cal_agency,
                        'certificate_number': certificate_num,
                        'calibration_passed': cal_result == "Pass",
                        'deviation_found': cal_result == "Conditional Pass",
                        'notes': remarks,
                        'created_by_id': 1  # System user
                    }

                    with get_db() as db:
                        calibration_record = CalibrationRecord(**calibration_data)
                        db.add(calibration_record)

                        # Update equipment's calibration dates
                        equipment = db.execute(
                            select(Equipment).where(Equipment.id == equipment_id)
                        ).scalar_one_or_none()

                        if equipment:
                            equipment.last_calibration_date = datetime.combine(cal_date, datetime.min.time())
                            equipment.next_calibration_date = datetime.combine(cal_due_date, datetime.min.time())

                        db.commit()

                    st.success(f"Calibration record {calibration_number} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding calibration record: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def render_add_equipment():
    """Render add new equipment form"""

    st.subheader("Add New Equipment")

    with st.form("add_equipment_form"):
        col1, col2 = st.columns(2)

        with col1:
            equipment_code = st.text_input("Equipment Code *", placeholder="EQP-XXX")
            name = st.text_input("Equipment Name *")
            category = st.selectbox(
                "Category *",
                ["Testing Equipment", "Imaging Equipment", "Environmental Testing",
                 "Measurement Device", "Calibration Standard", "chamber", "tester", "simulator", "Other"]
            )
            manufacturer = st.text_input("Manufacturer")
            model_number = st.text_input("Model Number")

        with col2:
            serial_number = st.text_input("Serial Number")
            location = st.text_input("Location")
            notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Equipment")

        if submitted:
            if not equipment_code or not name or not category:
                st.error("Please fill all required fields marked with *")
            else:
                try:
                    with get_db() as db:
                        # Check if equipment code already exists
                        existing = db.execute(
                            select(Equipment).where(Equipment.equipment_code == equipment_code)
                        ).scalar_one_or_none()

                        if existing:
                            st.error(f"Equipment Code '{equipment_code}' already exists. Please use a unique code.")
                            return

                        equipment_data = {
                            'equipment_code': equipment_code,
                            'name': name,
                            'category': category,
                            'manufacturer': manufacturer,
                            'model': model_number,
                            'serial_number': serial_number,
                            'location': location,
                            'status': EquipmentStatus.AVAILABLE
                        }

                        equipment = Equipment(**equipment_data)
                        db.add(equipment)
                        db.commit()

                    st.success(f"Equipment {equipment_code} added successfully! Status set to AVAILABLE.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error adding equipment: {str(e)}")


if __name__ == "__main__":
    main()
