"""
Incoming Inspection Page
Log and inspect samples upon arrival
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(page_title="Incoming Inspection", page_icon="🔍", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

st.title("🔍 Incoming Inspection")
st.markdown("### Sample Receiving and Inspection Workflow")

tab1, tab2 = st.tabs(["📝 New Inspection", "📋 Inspection History"])

# ============================================
# TAB 1: NEW INSPECTION
# ============================================

with tab1:
    # Link to service request
    st.subheader("Link to Service Request")

    requests = st.session_state.db.get_service_requests(status='approved')
    if not requests:
        requests = st.session_state.db.get_service_requests(status='pending')

    request_options = {f"{r['request_id']} - {r['project_name']}": r['request_id'] for r in requests}

    # Pre-select if coming from service request page
    default_request = None
    if st.session_state.get('current_request_id'):
        for key, val in request_options.items():
            if val == st.session_state.current_request_id:
                default_request = list(request_options.keys()).index(key)
                break

    selected_request_key = st.selectbox(
        "Select Service Request *",
        options=list(request_options.keys()),
        index=default_request if default_request is not None else 0
    )

    selected_request_id = request_options[selected_request_key] if selected_request_key else None

    st.markdown("---")

    with st.form("inspection_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Sample Identification")

            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., SAMPLE-2024-001",
                value=f"SAMPLE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )

            sample_type = st.selectbox(
                "Sample Type *",
                options=["Monocrystalline", "Polycrystalline", "Thin Film", "Bifacial", "Other"]
            )

            manufacturer = st.text_input("Manufacturer", placeholder="e.g., Company Name")

            model_number = st.text_input("Model Number", placeholder="e.g., XYZ-300W")

            serial_number = st.text_input("Serial Number", placeholder="If available")

            quantity = st.number_input("Quantity", min_value=1, value=1)

        with col2:
            st.markdown("#### Physical Inspection")

            condition = st.selectbox(
                "Overall Condition *",
                options=["excellent", "good", "fair", "poor", "damaged"]
            )

            st.markdown("**Dimensions (mm)**")
            dim_col1, dim_col2, dim_col3 = st.columns(3)
            with dim_col1:
                length_mm = st.number_input("Length", min_value=0.0, value=1650.0, step=0.1)
            with dim_col2:
                width_mm = st.number_input("Width", min_value=0.0, value=990.0, step=0.1)
            with dim_col3:
                thickness_mm = st.number_input("Thickness", min_value=0.0, value=40.0, step=0.1)

            weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=18.5, step=0.1)

        st.markdown("#### Inspection Notes")

        visual_inspection_notes = st.text_area(
            "Visual Inspection Findings",
            placeholder="Document any visible defects, damage, or observations...",
            height=150
        )

        # Photos/attachments
        st.markdown("**Photos/Documentation**")
        uploaded_files = st.file_uploader(
            "Upload inspection photos",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'pdf']
        )

        # Submit
        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            submitted = st.form_submit_button("✅ Complete Inspection", use_container_width=True)

    if submitted:
        if not sample_id or not sample_type:
            st.error("❌ Please fill all required fields")
        else:
            try:
                # Save photos
                photo_paths = []
                if uploaded_files:
                    for file in uploaded_files:
                        photo_paths.append(f"data/photos/{file.name}")

                inspection_data = {
                    'request_id': selected_request_id,
                    'sample_id': sample_id,
                    'sample_type': sample_type,
                    'manufacturer': manufacturer,
                    'model_number': model_number,
                    'serial_number': serial_number,
                    'quantity': quantity,
                    'condition': condition,
                    'visual_inspection_notes': visual_inspection_notes,
                    'dimensions': {
                        'length_mm': length_mm,
                        'width_mm': width_mm,
                        'thickness_mm': thickness_mm
                    },
                    'weight_kg': weight_kg,
                    'photos': photo_paths,
                    'inspected_by': 1
                }

                inspection_id = st.session_state.db.create_inspection(inspection_data)

                st.success(f"✅ Inspection Completed Successfully!")
                st.info(f"**Inspection ID:** {inspection_id}")

                st.session_state.current_inspection_id = inspection_id

                st.markdown("### 🎯 Next Steps")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➡️ Equipment Planning", use_container_width=True):
                        st.switch_page("pages/03_Equipment_Planning.py")
                with col2:
                    if st.button("🎯 Select Protocol", use_container_width=True):
                        st.switch_page("pages/04_Protocol_Selector.py")

            except Exception as e:
                st.error(f"❌ Error creating inspection: {e}")

# ============================================
# TAB 2: INSPECTION HISTORY
# ============================================

with tab2:
    st.subheader("Inspection History")

    try:
        inspections = st.session_state.db.get_inspections()

        if inspections:
            for insp in inspections:
                with st.expander(f"🔍 {insp['inspection_id']} - {insp['sample_id']}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample Type:** {insp['sample_type']}")
                        st.markdown(f"**Manufacturer:** {insp.get('manufacturer', 'N/A')}")
                        st.markdown(f"**Model:** {insp.get('model_number', 'N/A')}")

                    with col2:
                        st.markdown(f"**Condition:** {insp['condition']}")
                        st.markdown(f"**Quantity:** {insp.get('quantity', 1)}")
                        st.markdown(f"**Weight:** {insp.get('weight_kg', 'N/A')} kg")

                    with col3:
                        st.markdown(f"**Inspection Date:** {insp['inspection_date'][:10]}")
                        st.markdown(f"**Status:** {insp.get('status', 'N/A')}")

                    if insp.get('visual_inspection_notes'):
                        st.markdown("**Notes:**")
                        st.caption(insp['visual_inspection_notes'])
        else:
            st.info("📭 No inspection records found")

    except Exception as e:
        st.error(f"Error loading inspections: {e}")

with st.sidebar:
    st.markdown("---")
    st.info("""
    **Incoming Inspection**

    Document sample details:
    - Physical characteristics
    - Condition assessment
    - Visual defects
    - Photos/documentation

    Links to Service Request for complete traceability.
    """)

    if st.session_state.get('current_inspection_id'):
        st.success(f"**Active Inspection:**\n{st.session_state.current_inspection_id}")
