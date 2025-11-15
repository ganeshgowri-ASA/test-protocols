"""
Incoming Inspection Module
==========================
Perform incoming inspection of samples before testing.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from components.qr_generator import render_qr_code_generator_ui, get_qr_generator
from database.models import IncomingInspection, ServiceRequest, InspectionStatus

# Page configuration
setup_page_config(page_title="Incoming Inspection", page_icon="📦")

# Render navigation
render_header("Incoming Inspection", "Visual inspection and sample identification")
render_sidebar_navigation()


def main():
    """Main incoming inspection page"""

    tabs = st.tabs(["➕ New Inspection", "📋 View Inspections", "📱 QR Code"])

    with tabs[0]:
        render_new_inspection_form()

    with tabs[1]:
        render_inspections_list()

    with tabs[2]:
        render_qr_code_section()


def render_new_inspection_form():
    """Render form for new incoming inspection"""

    st.markdown("### New Incoming Inspection")

    # Link to service request
    with get_db() as db:
        service_requests = db.query(ServiceRequest).filter(
            ServiceRequest.status.in_(['approved', 'in_progress'])
        ).all()

    if not service_requests:
        st.warning("⚠️ No approved service requests available")
        return

    sr_options = {
        f"{sr.request_number} - {sr.client_name}": sr.id
        for sr in service_requests
    }

    selected_sr = st.selectbox("Link to Service Request *", options=list(sr_options.keys()))
    sr_id = sr_options[selected_sr]

    with st.form("incoming_inspection"):
        # Sample Identification
        st.markdown("#### 📝 Sample Identification")

        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input("Sample ID *", placeholder="e.g., SAMPLE-001")

        with col2:
            inspection_number = st.text_input(
                "Inspection Number",
                value=generate_inspection_number(),
                disabled=True
            )

        st.divider()

        # Visual Inspection Checklist
        st.markdown("#### ✅ Visual Inspection Checklist")

        col1, col2 = st.columns(2)

        with col1:
            physical_damage = st.checkbox("Physical Damage Detected", value=False)
            if physical_damage:
                damage_notes = st.text_area("Damage Notes", height=100)
            else:
                damage_notes = ""

            label_readable = st.checkbox("Label Readable", value=True)
            connectors_intact = st.checkbox("Connectors Intact", value=True)

        with col2:
            frame_condition = st.selectbox(
                "Frame Condition",
                ["Excellent", "Good", "Fair", "Poor"]
            )

            glass_condition = st.selectbox(
                "Glass Condition",
                ["Excellent", "Good", "Fair", "Poor"]
            )

            backsheet_condition = st.selectbox(
                "Backsheet Condition",
                ["Excellent", "Good", "Fair", "Poor"]
            )

        st.divider()

        # Physical Measurements
        st.markdown("#### 📏 Physical Measurements")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            length_mm = st.number_input("Length (mm)", min_value=0.0, value=0.0, step=0.1)

        with col2:
            width_mm = st.number_input("Width (mm)", min_value=0.0, value=0.0, step=0.1)

        with col3:
            thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=0.0, step=0.1)

        with col4:
            weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.01)

        st.divider()

        # Photos
        st.markdown("#### 📸 Photos")
        photos = st.file_uploader(
            "Upload Photos",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png']
        )

        # Inspection Result
        st.markdown("#### ✅ Inspection Result")

        col1, col2 = st.columns(2)

        with col1:
            passed = st.selectbox("Inspection Result", ["Passed", "Failed", "Conditional"])

        with col2:
            remarks = st.text_area("Remarks", height=100)

        # Submit
        col1, col2 = st.columns([3, 1])

        with col2:
            submitted = st.form_submit_button("✅ Complete Inspection", use_container_width=True, type="primary")

        if submitted:
            if not sample_id:
                st.error("❌ Please enter Sample ID")
                return

            try:
                # Determine status
                if passed == "Passed":
                    status = InspectionStatus.PASSED
                elif passed == "Failed":
                    status = InspectionStatus.FAILED
                else:
                    status = InspectionStatus.CONDITIONAL

                # Generate QR code
                qr_generator = get_qr_generator()
                qr_string, qr_img = qr_generator.generate_sample_qr_code(
                    sample_id=sample_id,
                    service_request_number=selected_sr.split(' - ')[0]
                )

                # Create inspection record
                inspection_data = {
                    'inspection_number': inspection_number,
                    'service_request_id': sr_id,
                    'sample_id': sample_id,
                    'qr_code': qr_string,
                    'physical_damage': physical_damage,
                    'physical_damage_notes': damage_notes if physical_damage else None,
                    'label_readable': label_readable,
                    'connectors_intact': connectors_intact,
                    'frame_condition': frame_condition.lower(),
                    'glass_condition': glass_condition.lower(),
                    'backsheet_condition': backsheet_condition.lower(),
                    'length_mm': length_mm if length_mm > 0 else None,
                    'width_mm': width_mm if width_mm > 0 else None,
                    'thickness_mm': thickness_mm if thickness_mm > 0 else None,
                    'weight_kg': weight_kg if weight_kg > 0 else None,
                    'status': status,
                    'passed': (passed == "Passed"),
                    'remarks': remarks,
                    'inspector_id': 1,  # Demo user
                    'inspection_date': datetime.utcnow()
                }

                with get_db() as db:
                    inspection = IncomingInspection(**inspection_data)
                    db.add(inspection)
                    db.commit()

                    st.success(f"✅ Inspection {inspection_number} completed successfully!")
                    st.info(f"📱 QR Code generated for sample {sample_id}")

                    # Store QR in session for display
                    st.session_state.last_generated_qr = {
                        'sample_id': sample_id,
                        'qr_string': qr_string,
                        'qr_image': qr_img
                    }

            except Exception as e:
                st.error(f"❌ Error creating inspection: {str(e)}")


def render_inspections_list():
    """Render list of inspections"""

    st.markdown("### 📋 Inspection History")

    try:
        with get_db() as db:
            inspections = db.query(IncomingInspection).order_by(
                IncomingInspection.inspection_date.desc()
            ).limit(20).all()

            if not inspections:
                st.info("No inspections found")
                return

            for insp in inspections:
                status_emoji = "✅" if insp.passed else "❌"

                with st.expander(
                    f"{status_emoji} {insp.inspection_number} - {insp.sample_id} ({insp.status.value.upper()})",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample ID:** {insp.sample_id}")
                        st.markdown(f"**Date:** {insp.inspection_date.strftime('%Y-%m-%d %H:%M')}")

                    with col2:
                        st.markdown(f"**Status:** {insp.status.value.upper()}")
                        st.markdown(f"**Passed:** {'Yes' if insp.passed else 'No'}")

                    with col3:
                        st.markdown(f"**Frame:** {insp.frame_condition.title() if insp.frame_condition else 'N/A'}")
                        st.markdown(f"**Glass:** {insp.glass_condition.title() if insp.glass_condition else 'N/A'}")

                    if insp.remarks:
                        st.markdown(f"**Remarks:** {insp.remarks}")

    except Exception as e:
        st.error(f"Error loading inspections: {str(e)}")


def render_qr_code_section():
    """Render QR code generation section"""

    st.markdown("### 📱 QR Code Management")

    if 'last_generated_qr' in st.session_state:
        qr_data = st.session_state.last_generated_qr

        st.success(f"Last generated QR code for sample: {qr_data['sample_id']}")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(qr_data['qr_image'], caption=f"QR Code - {qr_data['sample_id']}", width=300)

            st.download_button(
                "📥 Download QR Code",
                data=qr_data['qr_image'],
                file_name=f"{qr_data['sample_id']}_qr.png",
                mime="image/png",
                use_container_width=True
            )

        with col2:
            st.code(qr_data['qr_string'], language='json')

    else:
        st.info("Complete an inspection to generate a QR code")


def generate_inspection_number() -> str:
    """Generate unique inspection number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INSP-{timestamp[-10:]}"


if __name__ == "__main__":
    main()
