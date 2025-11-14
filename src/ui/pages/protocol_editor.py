"""Protocol Editor page for creating and editing test protocols."""

import streamlit as st
import json
from pathlib import Path

from src.core.validator import ProtocolValidator


def render_protocol_editor() -> None:
    """Render the protocol editor page."""
    st.markdown('<p class="main-header">Protocol Editor</p>', unsafe_allow_html=True)
    st.markdown("Create and edit test protocol configurations")

    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["📝 Edit Existing", "➕ Create New", "📤 Import JSON"],
        horizontal=True
    )

    if mode == "📝 Edit Existing":
        render_edit_protocol()
    elif mode == "➕ Create New":
        render_create_protocol()
    elif mode == "📤 Import JSON":
        render_import_protocol()


def render_edit_protocol() -> None:
    """Render interface for editing existing protocols."""
    st.markdown("---")
    st.markdown("### Edit Existing Protocol")

    # List available protocols
    schema_dir = Path("schemas/examples")
    if schema_dir.exists():
        protocol_files = list(schema_dir.glob("*.json"))

        if protocol_files:
            selected_file = st.selectbox(
                "Select Protocol",
                protocol_files,
                format_func=lambda x: x.name
            )

            if selected_file:
                with open(selected_file, 'r') as f:
                    protocol_data = json.load(f)

                # Display editor
                st.markdown("#### Protocol Configuration")
                edited_json = st.text_area(
                    "JSON Configuration",
                    value=json.dumps(protocol_data, indent=2),
                    height=400
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Save Changes", type="primary"):
                        try:
                            new_data = json.loads(edited_json)
                            validator = ProtocolValidator()

                            if validator.validate_protocol(new_data):
                                with open(selected_file, 'w') as f:
                                    json.dump(new_data, f, indent=2)
                                st.success("✅ Protocol saved successfully!")
                            else:
                                st.error("❌ Validation failed!")
                                for error in validator.get_errors():
                                    st.error(error)
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")

                with col2:
                    if st.button("🔍 Validate"):
                        try:
                            data = json.loads(edited_json)
                            validator = ProtocolValidator()

                            if validator.validate_protocol(data):
                                st.success("✅ Protocol is valid!")
                            else:
                                st.error("❌ Validation failed!")
                                for error in validator.get_errors():
                                    st.error(error)
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {str(e)}")
        else:
            st.info("No protocol files found in schemas/examples directory")
    else:
        st.error("Schemas directory not found")


def render_create_protocol() -> None:
    """Render interface for creating new protocols."""
    st.markdown("---")
    st.markdown("### Create New Protocol")

    st.info("Protocol creation wizard - Coming soon!")

    # Basic fields
    col1, col2 = st.columns(2)

    with col1:
        protocol_id = st.text_input("Protocol ID", placeholder="e.g., TRACK-002")
        name = st.text_input("Protocol Name", placeholder="e.g., New Test Protocol")
        version = st.text_input("Version", value="1.0.0")

    with col2:
        category = st.selectbox(
            "Category",
            ["Performance", "Reliability", "Safety", "Environmental", "Functional"]
        )
        description = st.text_area("Description", placeholder="Enter protocol description")

    st.markdown("#### Test Parameters")
    st.text_area("Test Parameters (JSON)", height=200, placeholder='{"duration": {...}, "metrics": [...]}')

    if st.button("Create Protocol", type="primary"):
        st.warning("Protocol creation - Coming soon!")


def render_import_protocol() -> None:
    """Render interface for importing protocols from JSON."""
    st.markdown("---")
    st.markdown("### Import Protocol from JSON")

    uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

    if uploaded_file is not None:
        try:
            protocol_data = json.load(uploaded_file)

            st.markdown("#### Preview")
            st.json(protocol_data)

            # Validate
            validator = ProtocolValidator()
            is_valid = validator.validate_protocol(protocol_data)

            if is_valid:
                st.success("✅ Protocol is valid!")

                if st.button("💾 Import Protocol", type="primary"):
                    # Save to schemas/examples
                    schema_dir = Path("schemas/examples")
                    schema_dir.mkdir(parents=True, exist_ok=True)

                    output_file = schema_dir / uploaded_file.name

                    with open(output_file, 'w') as f:
                        json.dump(protocol_data, f, indent=2)

                    st.success(f"✅ Protocol imported successfully to {output_file}")
            else:
                st.error("❌ Validation failed!")
                for error in validator.get_errors():
                    st.error(error)

        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON file: {str(e)}")
