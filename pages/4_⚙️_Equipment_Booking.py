"""
Equipment Booking Module
========================
Book and manage equipment for testing.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from sqlalchemy.orm import joinedload
from components.navigation import render_header, render_sidebar_navigation
from database.models import Equipment, EquipmentBooking, EquipmentStatus

# Page configuration
setup_page_config(page_title="Equipment Booking", page_icon="⚙️")

# Render navigation
render_header("Equipment Booking", "Reserve equipment for testing protocols")
render_sidebar_navigation()


def main():
    """Main equipment booking page"""

    tabs = st.tabs(["⚙️ Available Equipment", "📅 Make Booking", "📋 My Bookings"])

    with tabs[0]:
        render_equipment_list()

    with tabs[1]:
        render_booking_form()

    with tabs[2]:
        render_bookings_list()


def render_equipment_list():
    """Render list of available equipment"""

    st.markdown("### ⚙️ Equipment Inventory")

    try:
        with get_db() as db:
            equipment = db.query(Equipment).all()

            if not equipment:
                # Add sample equipment
                sample_equipment = [
                    {
                        'equipment_code': 'SIM-001',
                        'name': 'Solar Simulator',
                        'category': 'simulator',
                        'manufacturer': 'Halm',
                        'model': 'LS-1000',
                        'status': EquipmentStatus.AVAILABLE,
                        'location': 'Test Lab 1',
                        'specifications': {'irradiance': '1000 W/m²', 'class': 'AAA'}
                    },
                    {
                        'equipment_code': 'CHAM-001',
                        'name': 'Climate Chamber',
                        'category': 'chamber',
                        'manufacturer': 'Espec',
                        'model': 'EC-5000',
                        'status': EquipmentStatus.AVAILABLE,
                        'location': 'Test Lab 2',
                        'specifications': {'temp_range': '-40 to +85°C', 'humidity': '10-98% RH'}
                    },
                    {
                        'equipment_code': 'EL-001',
                        'name': 'EL Imaging System',
                        'category': 'tester',
                        'manufacturer': 'BT Imaging',
                        'model': 'LIS-R3',
                        'status': EquipmentStatus.AVAILABLE,
                        'location': 'Test Lab 1',
                        'specifications': {'resolution': '1024x1024', 'camera': 'InGaAs'}
                    }
                ]

                for eq_data in sample_equipment:
                    eq = Equipment(**eq_data)
                    db.add(eq)

                db.commit()
                equipment = db.query(Equipment).all()

            # Display equipment cards
            for eq in equipment:
                status_color = {
                    EquipmentStatus.AVAILABLE: "🟢",
                    EquipmentStatus.IN_USE: "🔵",
                    EquipmentStatus.MAINTENANCE: "🟡",
                    EquipmentStatus.CALIBRATION_DUE: "🔴",
                    EquipmentStatus.OUT_OF_SERVICE: "⚫"
                }.get(eq.status, "⚪")

                with st.expander(
                    f"{status_color} {eq.name} ({eq.equipment_code}) - {eq.status.value.upper().replace('_', ' ')}",
                    expanded=(eq.status == EquipmentStatus.AVAILABLE)
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Code:** {eq.equipment_code}")
                        st.markdown(f"**Category:** {eq.category.title() if eq.category else 'N/A'}")
                        st.markdown(f"**Status:** {eq.status.value.upper().replace('_', ' ')}")

                    with col2:
                        st.markdown(f"**Manufacturer:** {eq.manufacturer or 'N/A'}")
                        st.markdown(f"**Model:** {eq.model or 'N/A'}")
                        st.markdown(f"**Location:** {eq.location or 'N/A'}")

                    with col3:
                        if eq.last_calibration_date:
                            st.markdown(f"**Last Calibration:** {eq.last_calibration_date.strftime('%Y-%m-%d')}")
                        if eq.next_calibration_date:
                            st.markdown(f"**Next Calibration:** {eq.next_calibration_date.strftime('%Y-%m-%d')}")

                    if eq.specifications:
                        st.markdown("**Specifications:**")
                        st.json(eq.specifications)

                    # Book button
                    if eq.status == EquipmentStatus.AVAILABLE:
                        if st.button(f"📅 Book {eq.equipment_code}", key=f"book_{eq.id}"):
                            st.session_state.booking_equipment_id = eq.id
                            st.info(f"Go to 'Make Booking' tab to complete booking for {eq.name}")

    except Exception as e:
        st.error(f"Error loading equipment: {str(e)}")


def render_booking_form():
    """Render equipment booking form"""

    st.markdown("### 📅 Create Equipment Booking")

    try:
        # Query and extract equipment data before session closes to avoid DetachedInstanceError
        with get_db() as db:
            available_equipment = db.query(Equipment).filter(
                Equipment.status == EquipmentStatus.AVAILABLE
            ).all()
            # Extract needed data while session is still open
            eq_options = {
                f"{eq.equipment_code} - {eq.name}": eq.id
                for eq in available_equipment
            }

        if not eq_options:
            st.warning("⚠️ No equipment currently available for booking")
            return

        with st.form("equipment_booking"):
            # Equipment selection
            selected_eq = st.selectbox("Select Equipment *", options=list(eq_options.keys()))
            equipment_id = eq_options[selected_eq]

            # Booking period
            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input(
                    "Start Date *",
                    value=datetime.now(),
                    min_value=datetime.now()
                )
                start_time = st.time_input("Start Time *", value=datetime.now().time())

            with col2:
                end_date = st.date_input(
                    "End Date *",
                    value=datetime.now() + timedelta(days=1),
                    min_value=datetime.now()
                )
                end_time = st.time_input("End Time *", value=datetime.now().time())

            # Combine date and time
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            # Purpose
            purpose = st.text_area(
                "Purpose *",
                placeholder="e.g., P1 - I-V Performance Testing for SR-2024-0001",
                height=100
            )

            notes = st.text_area("Notes", placeholder="Any special requirements...", height=80)

            # Submit
            submitted = st.form_submit_button("✅ Create Booking", type="primary", use_container_width=True)

            if submitted:
                if not purpose:
                    st.error("❌ Please enter booking purpose")
                    return

                if end_datetime <= start_datetime:
                    st.error("❌ End time must be after start time")
                    return

                try:
                    booking_number = generate_booking_number()

                    booking_data = {
                        'booking_number': booking_number,
                        'equipment_id': equipment_id,
                        'booked_by_id': 1,  # Demo user
                        'start_time': start_datetime,
                        'end_time': end_datetime,
                        'purpose': purpose,
                        'notes': notes,
                        'is_active': True
                    }

                    # Use new session for database operations
                    with get_db() as db:
                        booking = EquipmentBooking(**booking_data)
                        db.add(booking)

                        # Update equipment status
                        equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
                        equipment.status = EquipmentStatus.IN_USE

                        db.commit()

                    st.success(f"✅ Booking {booking_number} created successfully!")
                    st.info(f"""
                    **Booking Details:**
                    - Equipment: {selected_eq}
                    - Period: {start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%Y-%m-%d %H:%M')}
                    - Duration: {(end_datetime - start_datetime).total_seconds() / 3600:.1f} hours
                    """)

                except Exception as e:
                    st.error(f"❌ Error creating booking: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def render_bookings_list():
    """Render list of bookings"""

    st.markdown("### 📋 Equipment Bookings")

    try:
        # Query bookings with eager loading and extract data to avoid DetachedInstanceError
        with get_db() as db:
            bookings = db.query(EquipmentBooking).options(
                joinedload(EquipmentBooking.equipment)
            ).filter(
                EquipmentBooking.is_active == True
            ).order_by(EquipmentBooking.start_time.desc()).limit(20).all()

            # Extract all needed data while session is open
            bookings_data = []
            for booking in bookings:
                bookings_data.append({
                    'id': booking.id,
                    'booking_number': booking.booking_number,
                    'start_time': booking.start_time,
                    'end_time': booking.end_time,
                    'purpose': booking.purpose,
                    'notes': booking.notes,
                    'equipment_id': booking.equipment_id,
                    'equipment_name': booking.equipment.name if booking.equipment else 'N/A',
                    'equipment_code': booking.equipment.equipment_code if booking.equipment else 'N/A',
                })

        if not bookings_data:
            st.info("No active bookings found")
            return

        for booking_info in bookings_data:
            is_current = (
                booking_info['start_time'] <= datetime.now() <= booking_info['end_time']
            )

            status_emoji = "🔵" if is_current else "📅"

            with st.expander(
                f"{status_emoji} {booking_info['booking_number']} - {booking_info['equipment_name']}",
                expanded=is_current
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Equipment:** {booking_info['equipment_name']}")
                    st.markdown(f"**Code:** {booking_info['equipment_code']}")

                with col2:
                    st.markdown(f"**Start:** {booking_info['start_time'].strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(f"**End:** {booking_info['end_time'].strftime('%Y-%m-%d %H:%M')}")

                with col3:
                    duration = (booking_info['end_time'] - booking_info['start_time']).total_seconds() / 3600
                    st.markdown(f"**Duration:** {duration:.1f} hours")
                    st.markdown(f"**Status:** {'In Progress' if is_current else 'Scheduled'}")

                st.markdown(f"**Purpose:** {booking_info['purpose']}")

                if booking_info['notes']:
                    st.markdown(f"**Notes:** {booking_info['notes']}")

                # Action buttons
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✅ Complete Booking", key=f"complete_{booking_info['id']}"):
                        with get_db() as db:
                            booking = db.query(EquipmentBooking).filter(
                                EquipmentBooking.id == booking_info['id']
                            ).first()
                            if booking:
                                booking.is_active = False
                                booking.actual_end_time = datetime.now()
                                equipment = db.query(Equipment).filter(
                                    Equipment.id == booking_info['equipment_id']
                                ).first()
                                if equipment:
                                    equipment.status = EquipmentStatus.AVAILABLE
                                db.commit()
                        st.success("Booking completed!")
                        st.rerun()

                with col2:
                    if st.button("❌ Cancel Booking", key=f"cancel_{booking_info['id']}"):
                        with get_db() as db:
                            booking = db.query(EquipmentBooking).filter(
                                EquipmentBooking.id == booking_info['id']
                            ).first()
                            if booking:
                                booking.is_cancelled = True
                                booking.is_active = False
                                equipment = db.query(Equipment).filter(
                                    Equipment.id == booking_info['equipment_id']
                                ).first()
                                if equipment:
                                    equipment.status = EquipmentStatus.AVAILABLE
                                db.commit()
                        st.success("Booking cancelled!")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading bookings: {str(e)}")


def generate_booking_number() -> str:
    """Generate unique booking number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"BK-{timestamp[-10:]}"


if __name__ == "__main__":
    main()
