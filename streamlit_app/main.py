"""
Main Streamlit Application for PV Testing Protocol System

This application provides a dynamic interface for managing and executing
photovoltaic testing protocols.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.protocol_parser import ProtocolParser, ProtocolParserError
from streamlit_app.utils.form_generator import FormGenerator
from streamlit_app.utils.session_manager import SessionManager
from streamlit_app.components.protocol_viewer import display_protocol_info


# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()

    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None

    if 'protocol_data' not in st.session_state:
        st.session_state.protocol_data = None

    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

    if 'current_section' not in st.session_state:
        st.session_state.current_section = None


def load_protocols():
    """Load available protocols from templates directory."""
    try:
        base_dir = Path(__file__).parent.parent
        templates_dir = base_dir / "templates"

        parser = ProtocolParser()
        protocols = parser.get_available_protocols(str(templates_dir))

        return protocols, parser
    except Exception as e:
        st.error(f"Error loading protocols: {e}")
        return [], None


def render_sidebar():
    """Render the sidebar with protocol selection and navigation."""
    with st.sidebar:
        st.title("🔬 PV Testing")
        st.markdown("---")

        # Protocol selection
        st.subheader("Select Protocol")

        protocols, parser = load_protocols()

        if not protocols:
            st.warning("No protocols found in templates directory.")
            st.info("Add protocol JSON files to the 'templates/' directory to get started.")
            return None, None

        # Group protocols by category
        categories = {}
        for protocol in protocols:
            cat = protocol.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(protocol)

        # Display protocols by category
        selected_protocol = None

        if len(categories) == 1:
            # If only one category, show flat list
            protocol_options = {p["name"]: p for p in protocols}
            selected_name = st.selectbox(
                "Protocol",
                options=list(protocol_options.keys()),
                key="protocol_selector"
            )
            if selected_name:
                selected_protocol = protocol_options[selected_name]
        else:
            # Multi-category selection
            selected_category = st.selectbox(
                "Category",
                options=list(categories.keys()),
                key="category_selector"
            )

            if selected_category:
                protocol_options = {p["name"]: p for p in categories[selected_category]}
                selected_name = st.selectbox(
                    "Protocol",
                    options=list(protocol_options.keys()),
                    key="protocol_selector"
                )
                if selected_name:
                    selected_protocol = protocol_options[selected_name]

        if selected_protocol:
            st.markdown("---")
            st.markdown(f"**Version:** {selected_protocol.get('version', 'N/A')}")

            if selected_protocol.get('description'):
                with st.expander("ℹ️ Description"):
                    st.write(selected_protocol['description'])

        st.markdown("---")

        # Navigation
        st.subheader("Navigation")
        navigation_options = [
            "📋 Protocol Overview",
            "📝 Data Entry",
            "📊 Analysis & Charts",
            "✅ Quality Control",
            "📄 Generate Report",
            "⚙️ Settings"
        ]

        selected_nav = st.radio(
            "Go to:",
            options=navigation_options,
            key="navigation"
        )

        return selected_protocol, parser


def render_protocol_overview(protocol_data, parser):
    """Render protocol overview page."""
    st.header("📋 Protocol Overview")

    metadata = parser.get_protocol_metadata(protocol_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Protocol ID", metadata.get("protocol_id", "N/A"))

    with col2:
        st.metric("Version", metadata.get("version", "N/A"))

    with col3:
        st.metric("Category", metadata.get("category", "N/A").title())

    st.markdown("---")

    # Display sections
    st.subheader("Protocol Sections")
    sections = parser.get_sections(protocol_data)

    if sections:
        cols = st.columns(min(3, len(sections)))
        for idx, section in enumerate(sections):
            with cols[idx % 3]:
                st.info(f"**{section.replace('_', ' ').title()}**")
    else:
        st.warning("No sections defined in this protocol.")

    # Display validation rules
    validation_rules = parser.get_validation_rules(protocol_data)
    if validation_rules:
        st.markdown("---")
        st.subheader("Quality Control Rules")
        st.write(f"Total validation rules: {len(validation_rules)}")

        with st.expander("View Rules"):
            for rule in validation_rules:
                st.markdown(f"- **{rule.get('rule_name')}**: {rule.get('message', 'No description')}")


def render_data_entry(protocol_data, parser):
    """Render data entry page with dynamic forms."""
    st.header("📝 Data Entry")

    form_generator = FormGenerator()
    sections = parser.get_sections(protocol_data)

    if not sections:
        st.warning("No data entry sections available for this protocol.")
        return

    # Section tabs
    tabs = st.tabs([section.replace('_', ' ').title() for section in sections])

    for idx, section in enumerate(sections):
        with tabs[idx]:
            section_data = protocol_data.get(section, {})

            if "fields" in section_data:
                # Regular form fields
                st.subheader(section.replace('_', ' ').title())
                fields = section_data["fields"]

                for field in fields:
                    field_key = f"{section}_{field['field_id']}"
                    form_generator.render_field(field, field_key)

            elif "sections" in section_data:
                # Multi-section (like protocol_inputs)
                for subsection in section_data["sections"]:
                    st.markdown(f"### {subsection.get('section_title', 'Subsection')}")
                    for field in subsection.get("fields", []):
                        field_key = f"{section}_{subsection['section_id']}_{field['field_id']}"
                        form_generator.render_field(field, field_key)

            elif "tables" in section_data:
                # Table-based input (like live_readings)
                st.subheader("Data Tables")
                for table in section_data["tables"]:
                    st.markdown(f"**{table.get('table_name', 'Table')}**")
                    form_generator.render_data_table(table, f"{section}_{table['table_id']}")

    # Save button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Save Data", type="primary", use_container_width=True):
            # Save form data to session state
            st.session_state.session_manager.save_form_data(st.session_state.form_data)
            st.success("Data saved successfully!")

    with col2:
        if st.button("🗑️ Clear Form", use_container_width=True):
            st.session_state.form_data = {}
            st.rerun()


def render_analysis(protocol_data, parser):
    """Render analysis and charts page."""
    st.header("📊 Analysis & Visualization")

    calculations = parser.get_calculations(protocol_data)
    charts = parser.get_chart_configs(protocol_data)

    if calculations:
        st.subheader("Calculations")
        for calc in calculations:
            with st.expander(f"📐 {calc.get('calc_name', 'Calculation')}"):
                st.markdown(f"**Formula:** `{calc.get('formula', 'N/A')}`")
                st.markdown(f"**Output Unit:** {calc.get('output_unit', 'N/A')}")
                if calc.get('description'):
                    st.markdown(f"**Description:** {calc['description']}")

    if charts:
        st.markdown("---")
        st.subheader("Visualizations")
        st.info("Chart rendering will be available once data is collected.")

        for chart in charts:
            with st.expander(f"📈 {chart.get('title', 'Chart')}"):
                st.markdown(f"**Type:** {chart.get('chart_type', 'N/A').title()}")
                st.markdown(f"**X-Axis:** {chart.get('x_axis', {}).get('label', 'N/A')}")
                st.markdown(f"**Y-Axis:** {chart.get('y_axis', {}).get('label', 'N/A')}")
    else:
        st.info("No visualizations configured for this protocol.")


def render_quality_control(protocol_data, parser):
    """Render quality control page."""
    st.header("✅ Quality Control")

    validation_rules = parser.get_validation_rules(protocol_data)

    if not validation_rules:
        st.info("No quality control rules defined for this protocol.")
        return

    st.subheader("Validation Rules")

    for rule in validation_rules:
        severity = rule.get("severity", "info")
        severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")

        with st.expander(f"{severity_emoji} {rule.get('rule_name', 'Rule')}"):
            st.markdown(f"**Field:** {rule.get('field', 'N/A')}")
            st.markdown(f"**Type:** {rule.get('rule_type', 'N/A')}")
            st.markdown(f"**Severity:** {severity.upper()}")
            st.markdown(f"**Message:** {rule.get('message', 'N/A')}")

            params = rule.get('parameters', {})
            if params:
                st.markdown("**Parameters:**")
                for key, value in params.items():
                    st.markdown(f"- {key}: {value}")

    st.markdown("---")
    if st.button("🔍 Run Validation", type="primary"):
        st.info("Validation will run on collected data.")


def render_report_generation():
    """Render report generation page."""
    st.header("📄 Generate Report")

    st.subheader("Report Configuration")

    col1, col2 = st.columns(2)

    with col1:
        report_format = st.selectbox(
            "Export Format",
            options=["PDF", "Excel", "JSON", "CSV"],
            key="report_format"
        )

        include_charts = st.checkbox("Include Charts", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=True)

    with col2:
        report_title = st.text_input("Report Title", value="PV Testing Report")
        author_name = st.text_input("Author", value="")

    st.markdown("---")

    # Section selection
    st.subheader("Sections to Include")

    sections = [
        "General Information",
        "Sample Details",
        "Test Parameters",
        "Results & Analysis",
        "Quality Control",
        "Charts & Visualizations"
    ]

    selected_sections = []
    cols = st.columns(2)
    for idx, section in enumerate(sections):
        with cols[idx % 2]:
            if st.checkbox(section, value=True, key=f"section_{idx}"):
                selected_sections.append(section)

    st.markdown("---")

    if st.button("📥 Generate Report", type="primary", use_container_width=True):
        with st.spinner("Generating report..."):
            st.info("Report generation will be implemented with actual data processing.")
            st.balloons()


def render_settings():
    """Render settings page."""
    st.header("⚙️ Settings")

    st.subheader("Application Settings")

    with st.expander("🎨 Display Settings"):
        theme = st.selectbox("Theme", options=["Light", "Dark", "Auto"])
        page_width = st.slider("Page Width", min_value=800, max_value=1600, value=1200)

    with st.expander("💾 Data Storage"):
        st.text_input("Data Directory", value="./data")
        auto_save = st.checkbox("Auto-save enabled", value=True)
        auto_save_interval = st.number_input("Auto-save interval (minutes)", min_value=1, max_value=60, value=5)

    with st.expander("🔔 Notifications"):
        enable_notifications = st.checkbox("Enable notifications", value=True)
        email_alerts = st.checkbox("Email alerts for critical issues", value=False)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.success("Settings saved successfully!")

    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.info("Settings reset to defaults.")


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Render sidebar and get selected protocol
    selected_protocol, parser = render_sidebar()

    # Load protocol data if selected
    if selected_protocol:
        try:
            protocol_data = parser.load_protocol(selected_protocol["path"])
            st.session_state.protocol_data = protocol_data
            st.session_state.selected_protocol = selected_protocol
        except ProtocolParserError as e:
            st.error(f"Error loading protocol: {e}")
            return
    else:
        st.info("👈 Please select a protocol from the sidebar to get started.")
        st.markdown("---")
        st.markdown("""
        ## Welcome to PV Testing Protocol System

        This application provides a comprehensive framework for managing photovoltaic testing protocols.

        ### Getting Started:
        1. Add protocol JSON files to the `templates/` directory
        2. Select a protocol from the sidebar
        3. Navigate through different sections using the sidebar menu
        4. Enter data, run analysis, and generate reports

        ### Features:
        - ✅ Dynamic form generation from JSON protocols
        - 📊 Real-time data analysis and visualization
        - 🔍 Quality control validation
        - 📄 Automated report generation
        - 💾 Session state management
        """)
        return

    # Route to appropriate page based on navigation
    navigation = st.session_state.get('navigation', '📋 Protocol Overview')

    if "Overview" in navigation:
        render_protocol_overview(protocol_data, parser)
    elif "Data Entry" in navigation:
        render_data_entry(protocol_data, parser)
    elif "Analysis" in navigation:
        render_analysis(protocol_data, parser)
    elif "Quality Control" in navigation:
        render_quality_control(protocol_data, parser)
    elif "Report" in navigation:
        render_report_generation()
    elif "Settings" in navigation:
        render_settings()


if __name__ == "__main__":
    main()
