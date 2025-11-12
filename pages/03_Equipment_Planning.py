"""
Equipment Planning Page
Resource allocation and scheduling
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(page_title="Equipment Planning", page_icon="⚙️", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

st.title("⚙️ Equipment Planning")
st.markdown("### Resource Allocation and Scheduling")

# Equipment definitions
EQUIPMENT_LIST = [
    {"id": "EQ-001", "name": "Solar Simulator (Class AAA)", "type": "electrical"},
    {"id": "EQ-002", "name": "I-V Curve Tracer", "type": "electrical"},
    {"id": "EQ-003", "name": "EL Imaging System", "type": "optical"},
    {"id": "EQ-004", "name": "Thermal Chamber", "type": "environmental"},
    {"id": "EQ-005", "name": "Climate Chamber (Damp Heat)", "type": "environmental"},
    {"id": "EQ-006", "name": "Mechanical Load Tester", "type": "mechanical"},
    {"id": "EQ-007", "name": "Hail Impact Tester", "type": "mechanical"},
    {"id": "EQ-008", "name": "Thermography Camera", "type": "optical"},
    {"id": "EQ-009", "name": "Insulation Tester", "type": "safety"},
    {"id": "EQ-010", "name": "Flash Test System", "type": "electrical"},
]

tab1, tab2, tab3 = st.tabs(["📅 Schedule Equipment", "📊 Equipment Status", "🔧 Maintenance"])

# ============================================
# TAB 1: SCHEDULE EQUIPMENT
# ============================================

with tab1:
    st.subheader("Schedule Equipment for Testing")

    # Link to inspection
    inspections = st.session_state.db.get_inspections()
    insp_options = {f"{i['inspection_id']} - {i['sample_id']}": i['inspection_id'] for i in inspections}

    if insp_options:
        selected_insp_key = st.selectbox("Select Inspection/Sample", options=list(insp_options.keys()))
        selected_insp_id = insp_options[selected_insp_key]

        st.markdown("---")

        with st.form("equipment_form"):
            # Equipment selection
            equipment_options = [f"{e['id']} - {e['name']}" for e in EQUIPMENT_LIST]
            selected_equipment = st.multiselect(
                "Select Equipment *",
                options=equipment_options,
                help="Select one or more equipment items needed for testing"
            )

            col1, col2 = st.columns(2)

            with col1:
                scheduled_start = st.date_input(
                    "Scheduled Start Date *",
                    value=date.today(),
                    min_value=date.today()
                )

                scheduled_start_time = st.time_input("Start Time", value=datetime.now().time())

            with col2:
                scheduled_end = st.date_input(
                    "Scheduled End Date *",
                    value=date.today() + timedelta(days=7),
                    min_value=date.today()
                )

                scheduled_end_time = st.time_input("End Time", value=datetime.now().time())

            # Operator assignment
            operator = st.selectbox(
                "Assign Operator",
                options=["Engineer 1", "Engineer 2", "Technician 1", "Technician 2"]
            )

            notes = st.text_area("Planning Notes", height=100)

            submitted = st.form_submit_button("📅 Schedule Equipment", use_container_width=True)

        if submitted:
            if not selected_equipment:
                st.error("❌ Please select at least one equipment item")
            else:
                st.success(f"✅ Equipment scheduled successfully!")
                st.info(f"**{len(selected_equipment)}** equipment item(s) scheduled")

                # Show scheduled items
                for eq in selected_equipment:
                    st.markdown(f"- {eq}")

                st.markdown("### 🎯 Next Steps")
                if st.button("🎯 Proceed to Protocol Selection", use_container_width=True):
                    st.switch_page("pages/04_Protocol_Selector.py")

    else:
        st.warning("⚠️ No inspection records available. Please complete inspection first.")
        if st.button("🔍 Go to Incoming Inspection"):
            st.switch_page("pages/02_Incoming_Inspection.py")

# ============================================
# TAB 2: EQUIPMENT STATUS
# ============================================

with tab2:
    st.subheader("Equipment Availability Status")

    # Display equipment status
    for eq in EQUIPMENT_LIST:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.markdown(f"**{eq['name']}**")
                st.caption(f"ID: {eq['id']} | Type: {eq['type']}")

            with col2:
                # Random status for demo
                import random
                status = random.choice(['available', 'in_use', 'maintenance'])
                if status == 'available':
                    st.success("✅ Available")
                elif status == 'in_use':
                    st.warning("⏳ In Use")
                else:
                    st.error("🔧 Maintenance")

            with col3:
                # Calibration status
                cal_status = random.choice(['valid', 'due_soon', 'overdue'])
                if cal_status == 'valid':
                    st.info("✓ Cal Valid")
                elif cal_status == 'due_soon':
                    st.warning("⚠ Cal Due Soon")
                else:
                    st.error("❌ Cal Overdue")

            with col4:
                if st.button("📅 Schedule", key=f"sched_{eq['id']}"):
                    st.info(f"Schedule {eq['name']}")

            st.markdown("---")

# ============================================
# TAB 3: MAINTENANCE
# ============================================

with tab3:
    st.subheader("Equipment Maintenance Log")

    st.info("""
    **Maintenance Schedule:**
    - Preventive maintenance: Quarterly
    - Calibration: Annually or per standard requirements
    - Inspection: Monthly

    Use this section to log maintenance activities and track equipment health.
    """)

    with st.form("maintenance_form"):
        equipment_id = st.selectbox(
            "Equipment",
            options=[f"{e['id']} - {e['name']}" for e in EQUIPMENT_LIST]
        )

        maintenance_type = st.selectbox(
            "Maintenance Type",
            options=["preventive", "corrective", "calibration", "inspection"]
        )

        description = st.text_area("Description of Work Performed")

        performed_date = st.date_input("Date Performed", value=date.today())

        next_maintenance = st.date_input(
            "Next Maintenance Due",
            value=date.today() + timedelta(days=90)
        )

        if st.form_submit_button("💾 Log Maintenance"):
            st.success("✅ Maintenance log recorded")

with st.sidebar:
    st.markdown("---")
    st.info("""
    **Equipment Planning**

    - Schedule equipment
    - Check availability
    - Track calibration
    - Log maintenance

    Ensures resources are allocated efficiently for testing protocols.
    """)
