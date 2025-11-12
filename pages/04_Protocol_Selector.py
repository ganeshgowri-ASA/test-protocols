"""
Protocol Selector Page
Browse and select from all 54 protocols
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Protocol Selector", page_icon="🎯", layout="wide")

st.title("🎯 Protocol Selector")
st.markdown("### Select Testing Protocol to Execute")

# All 54 protocols
PROTOCOLS = [
    {"id": "PVTP-001", "name": "LID/LIS Testing", "category": "Electrical", "page": "05", "status": "active"},
    {"id": "PVTP-002", "name": "Thermal Cycling", "category": "Reliability", "page": "06", "status": "active"},
    {"id": "PVTP-003", "name": "Damp Heat Testing", "category": "Environmental", "page": "07", "status": "active"},
    {"id": "PVTP-004", "name": "Humidity Freeze", "category": "Environmental", "page": "08", "status": "active"},
    {"id": "PVTP-005", "name": "UV Preconditioning", "category": "Environmental", "page": "09", "status": "active"},
    {"id": "PVTP-006", "name": "Outdoor Exposure", "category": "Environmental", "page": "10", "status": "template"},
    {"id": "PVTP-007", "name": "Hot Spot Endurance", "category": "Reliability", "page": "11", "status": "template"},
    {"id": "PVTP-008", "name": "UV Test", "category": "Environmental", "page": "12", "status": "template"},
    {"id": "PVTP-009", "name": "Thermal Cycling Extended", "category": "Reliability", "page": "13", "status": "template"},
    {"id": "PVTP-010", "name": "Damp Heat Extended", "category": "Environmental", "page": "14", "status": "template"},
    {"id": "PVTP-011", "name": "Mechanical Load Test", "category": "Mechanical", "page": "15", "status": "template"},
    {"id": "PVTP-012", "name": "Hail Impact Test", "category": "Mechanical", "page": "16", "status": "template"},
    {"id": "PVTP-013", "name": "Robustness of Terminations", "category": "Mechanical", "page": "17", "status": "template"},
    {"id": "PVTP-014", "name": "Twist Test", "category": "Mechanical", "page": "18", "status": "template"},
    {"id": "PVTP-015", "name": "Bypass Diode Thermal Test", "category": "Thermal", "page": "19", "status": "template"},
    {"id": "PVTP-016", "name": "Fire Test", "category": "Safety", "page": "20", "status": "template"},
    {"id": "PVTP-017", "name": "Wet Leakage Current", "category": "Safety", "page": "21", "status": "template"},
    {"id": "PVTP-018", "name": "Dielectric Voltage Test", "category": "Safety", "page": "22", "status": "template"},
    {"id": "PVTP-019", "name": "Ground Continuity", "category": "Safety", "page": "23", "status": "template"},
    {"id": "PVTP-020", "name": "Cut Susceptibility", "category": "Safety", "page": "24", "status": "template"},
    {"id": "PVTP-021", "name": "Spectral Response", "category": "Optical", "page": "25", "status": "template"},
    {"id": "PVTP-022", "name": "Temperature Coefficients", "category": "Electrical", "page": "26", "status": "template"},
    {"id": "PVTP-023", "name": "Irradiance & Temperature", "category": "Environmental", "page": "27", "status": "template"},
    {"id": "PVTP-024", "name": "Low Irradiance Performance", "category": "Electrical", "page": "28", "status": "template"},
    {"id": "PVTP-025", "name": "Incidence Angle Response", "category": "Optical", "page": "29", "status": "template"},
    {"id": "PVTP-026", "name": "I-V Curve Measurement", "category": "Electrical", "page": "30", "status": "template"},
    {"id": "PVTP-027", "name": "STC Power Rating", "category": "Electrical", "page": "31", "status": "template"},
    {"id": "PVTP-028", "name": "NOCT Measurement", "category": "Thermal", "page": "32", "status": "template"},
    {"id": "PVTP-029", "name": "Maximum Power Tracking", "category": "Electrical", "page": "33", "status": "template"},
    {"id": "PVTP-030", "name": "PID Testing", "category": "Reliability", "page": "34", "status": "template"},
    {"id": "PVTP-031", "name": "PID Recovery Test", "category": "Reliability", "page": "35", "status": "template"},
    {"id": "PVTP-032", "name": "Bifacial Power Measurement", "category": "Electrical", "page": "36", "status": "template"},
    {"id": "PVTP-033", "name": "Bifaciality Factor", "category": "Electrical", "page": "37", "status": "template"},
    {"id": "PVTP-034", "name": "Electroluminescence Imaging", "category": "Quality Control", "page": "38", "status": "template"},
    {"id": "PVTP-035", "name": "Thermography Analysis", "category": "Quality Control", "page": "39", "status": "template"},
    {"id": "PVTP-036", "name": "Visual Inspection", "category": "Quality Control", "page": "40", "status": "template"},
    {"id": "PVTP-037", "name": "Insulation Resistance", "category": "Safety", "page": "41", "status": "template"},
    {"id": "PVTP-038", "name": "Grounding Verification", "category": "Safety", "page": "42", "status": "template"},
    {"id": "PVTP-039", "name": "Long-term Stability", "category": "Reliability", "page": "43", "status": "template"},
    {"id": "PVTP-040", "name": "Performance Degradation", "category": "Reliability", "page": "44", "status": "template"},
    {"id": "PVTP-041", "name": "Field Performance Ratio", "category": "Performance", "page": "45", "status": "template"},
    {"id": "PVTP-042", "name": "Solderability Test", "category": "Quality Control", "page": "46", "status": "template"},
    {"id": "PVTP-043", "name": "Peel Test", "category": "Quality Control", "page": "47", "status": "template"},
    {"id": "PVTP-044", "name": "Thermal Shock", "category": "Reliability", "page": "48", "status": "template"},
    {"id": "PVTP-045", "name": "Salt Mist Corrosion", "category": "Environmental", "page": "49", "status": "template"},
    {"id": "PVTP-046", "name": "Ammonia Corrosion", "category": "Environmental", "page": "50", "status": "template"},
    {"id": "PVTP-047", "name": "Sand & Dust Test", "category": "Environmental", "page": "51", "status": "template"},
    {"id": "PVTP-048", "name": "Dynamic Mechanical Load", "category": "Mechanical", "page": "52", "status": "template"},
    {"id": "PVTP-049", "name": "Cell Interconnect Fatigue", "category": "Reliability", "page": "53", "status": "template"},
    {"id": "PVTP-050", "name": "Bypass Diode Functionality", "category": "Electrical", "page": "54", "status": "template"},
    {"id": "PVTP-051", "name": "Flash Testing", "category": "Quality Control", "page": "55", "status": "template"},
    {"id": "PVTP-052", "name": "Power Tolerance Verification", "category": "Quality Control", "page": "56", "status": "template"},
    {"id": "PVTP-053", "name": "Nameplate Verification", "category": "Quality Control", "page": "57", "status": "template"},
    {"id": "PVTP-054", "name": "Compliance Documentation", "category": "Documentation", "page": "58", "status": "template"},
]

# Group by category
categories = {}
for protocol in PROTOCOLS:
    cat = protocol['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(protocol)

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    selected_category = st.selectbox(
        "Filter by Category",
        options=["All"] + list(categories.keys())
    )

with col2:
    search_term = st.text_input("🔍 Search Protocol")

with col3:
    view_mode = st.selectbox("View Mode", options=["Grid", "Table"])

st.markdown("---")
st.markdown(f"### Found {len(PROTOCOLS)} protocols")

# Display protocols
if view_mode == "Grid":
    # Grid view
    if selected_category == "All":
        filtered = PROTOCOLS
    else:
        filtered = categories[selected_category]

    if search_term:
        filtered = [p for p in filtered if search_term.lower() in p['name'].lower() or search_term.lower() in p['id'].lower()]

    # Display in grid (3 columns)
    cols = st.columns(3)
    for idx, protocol in enumerate(filtered):
        with cols[idx % 3]:
            with st.container():
                status_icon = "✅" if protocol['status'] == 'active' else "📋"
                st.markdown(f"#### {status_icon} {protocol['id']}")
                st.markdown(f"**{protocol['name']}**")
                st.caption(f"Category: {protocol['category']}")

                # Navigate to protocol page
                if protocol['status'] == 'active':
                    if st.button(f"🚀 Execute", key=f"exec_{protocol['id']}", use_container_width=True):
                        try:
                            st.switch_page(f"pages/{protocol['page']}_{protocol['id']}.py")
                        except:
                            st.warning(f"Protocol page {protocol['id']} under development")
                else:
                    st.button(f"📋 Template", key=f"temp_{protocol['id']}", use_container_width=True, disabled=True)

                st.markdown("---")

else:
    # Table view
    if selected_category == "All":
        filtered = PROTOCOLS
    else:
        filtered = categories[selected_category]

    if search_term:
        filtered = [p for p in filtered if search_term.lower() in p['name'].lower()]

    # Display as table
    table_data = []
    for protocol in filtered:
        table_data.append({
            "ID": protocol['id'],
            "Protocol Name": protocol['name'],
            "Category": protocol['category'],
            "Status": "🟢 Active" if protocol['status'] == 'active' else "🔵 Template"
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    # Action buttons
    st.markdown("### Quick Actions")
    selected_protocol = st.selectbox(
        "Select Protocol to Execute",
        options=[f"{p['id']} - {p['name']}" for p in filtered if p['status'] == 'active']
    )

    if st.button("🚀 Execute Selected Protocol", type="primary", use_container_width=True):
        protocol_id = selected_protocol.split(' - ')[0]
        protocol = next((p for p in PROTOCOLS if p['id'] == protocol_id), None)
        if protocol:
            try:
                st.switch_page(f"pages/{protocol['page']}_{protocol['id']}.py")
            except:
                st.info(f"Navigating to {protocol['name']} protocol...")

with st.sidebar:
    st.markdown("---")
    st.info("""
    **Protocol Selector**

    Browse all 54 testing protocols:
    - Filter by category
    - Search by name/ID
    - View as grid or table
    - Launch protocol execution

    **Categories:**
    - Electrical
    - Reliability
    - Environmental
    - Mechanical
    - Safety
    - Optical
    - Quality Control
    """)
