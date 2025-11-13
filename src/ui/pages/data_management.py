"""Data management page."""

import streamlit as st
from pathlib import Path
import json
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render() -> None:
    """Render the data management page."""

    st.markdown('<div class="main-header">📁 Data Management</div>', unsafe_allow_html=True)

    # Data directory
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📂 Browse Files", "📤 Import/Export", "🗑️ Cleanup"])

    with tab1:
        st.markdown("### Test Protocol Files")

        json_files = list(data_dir.glob("*.json"))

        if not json_files:
            st.info("No protocol files found.")
        else:
            st.markdown(f"Found **{len(json_files)}** protocol files")

            # List files with details
            file_data = []

            for file_path in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(file_path, "r") as f:
                        protocol_data = json.load(f)

                    file_info = {
                        "Filename": file_path.name,
                        "Sample ID": protocol_data.get("sample_info", {}).get("sample_id", "N/A"),
                        "Protocol": protocol_data.get("protocol_info", {}).get("protocol_id", "N/A"),
                        "Test Date": protocol_data.get("protocol_info", {}).get("test_date", "N/A")[:10],
                        "Size (KB)": f"{file_path.stat().st_size / 1024:.1f}",
                        "Modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    }
                    file_data.append(file_info)

                except Exception as e:
                    file_info = {
                        "Filename": file_path.name,
                        "Sample ID": "Error",
                        "Protocol": "Error",
                        "Test Date": "Error",
                        "Size (KB)": f"{file_path.stat().st_size / 1024:.1f}",
                        "Modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    }
                    file_data.append(file_info)

            if file_data:
                import pandas as pd
                df = pd.DataFrame(file_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # File operations
                selected_file = st.selectbox(
                    "Select file for operations",
                    options=[f["Filename"] for f in file_data]
                )

                if selected_file:
                    file_path = data_dir / selected_file

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("👁️ View", use_container_width=True):
                            try:
                                with open(file_path, "r") as f:
                                    protocol_data = json.load(f)
                                st.json(protocol_data)
                            except Exception as e:
                                st.error(f"Error viewing file: {e}")

                    with col2:
                        if st.button("📥 Download", use_container_width=True):
                            try:
                                with open(file_path, "r") as f:
                                    content = f.read()
                                st.download_button(
                                    label="Download File",
                                    data=content,
                                    file_name=selected_file,
                                    mime="application/json",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error downloading file: {e}")

                    with col3:
                        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                            if "confirm_delete" not in st.session_state:
                                st.session_state.confirm_delete = selected_file
                            elif st.session_state.confirm_delete == selected_file:
                                try:
                                    file_path.unlink()
                                    st.success(f"Deleted {selected_file}")
                                    del st.session_state.confirm_delete
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting file: {e}")

                    if hasattr(st.session_state, "confirm_delete") and st.session_state.confirm_delete == selected_file:
                        st.warning(f"⚠️ Click 'Delete' again to confirm deletion of {selected_file}")

    with tab2:
        st.markdown("### Import Protocol")

        uploaded_file = st.file_uploader(
            "Upload protocol JSON file",
            type=["json"],
            help="Select a protocol JSON file to import"
        )

        if uploaded_file is not None:
            try:
                protocol_data = json.loads(uploaded_file.read().decode("utf-8"))

                st.success("✅ File loaded successfully")

                # Display protocol info
                protocol_info = protocol_data.get("protocol_info", {})
                sample_info = protocol_data.get("sample_info", {})

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Protocol:** {protocol_info.get('protocol_id', 'N/A')}")
                    st.markdown(f"**Sample:** {sample_info.get('sample_id', 'N/A')}")

                with col2:
                    st.markdown(f"**Test Date:** {protocol_info.get('test_date', 'N/A')[:10]}")
                    st.markdown(f"**Module:** {sample_info.get('module_type', 'N/A')}")

                # Import button
                if st.button("📤 Import to Database", type="primary"):
                    # Save to data directory
                    filename = f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    save_path = data_dir / filename

                    with open(save_path, "w") as f:
                        json.dump(protocol_data, f, indent=2)

                    st.success(f"✅ Imported as {filename}")

            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON file: {e}")
            except Exception as e:
                st.error(f"❌ Error importing file: {e}")

        st.markdown("---")

        st.markdown("### Export Multiple Files")

        if json_files:
            export_files = st.multiselect(
                "Select files to export",
                options=[f.name for f in json_files]
            )

            if export_files and st.button("📥 Download Selected", type="primary"):
                st.info("Batch download feature coming soon!")
        else:
            st.info("No files available for export.")

    with tab3:
        st.markdown("### Database Cleanup")

        st.markdown("""
        Use these tools to manage and clean up the protocol database.
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Statistics")

            if json_files:
                total_size = sum(f.stat().st_size for f in json_files)
                st.metric("Total Files", len(json_files))
                st.metric("Total Size", f"{total_size / 1024 / 1024:.2f} MB")

                # Count by protocol
                protocol_counts = {}
                for file_path in json_files:
                    try:
                        with open(file_path, "r") as f:
                            protocol_data = json.load(f)
                        protocol_id = protocol_data.get("protocol_info", {}).get("protocol_id", "Unknown")
                        protocol_counts[protocol_id] = protocol_counts.get(protocol_id, 0) + 1
                    except:
                        pass

                if protocol_counts:
                    st.markdown("**By Protocol:**")
                    for protocol_id, count in protocol_counts.items():
                        st.markdown(f"- {protocol_id}: {count} files")

        with col2:
            st.markdown("#### Cleanup Operations")

            st.warning("⚠️ Cleanup operations cannot be undone!")

            if st.button("🧹 Remove Duplicate Files", use_container_width=True):
                st.info("Duplicate detection feature coming soon!")

            if st.button("📦 Archive Old Files", use_container_width=True):
                st.info("Archiving feature coming soon!")

            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
                if "confirm_clear_all" not in st.session_state:
                    st.session_state.confirm_clear_all = True
                elif st.session_state.confirm_clear_all:
                    try:
                        for file_path in json_files:
                            file_path.unlink()
                        st.success("✅ All files deleted")
                        del st.session_state.confirm_clear_all
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error clearing data: {e}")

            if hasattr(st.session_state, "confirm_clear_all") and st.session_state.confirm_clear_all:
                st.error("⚠️ Click 'Clear All Data' again to confirm deletion of ALL files!")
