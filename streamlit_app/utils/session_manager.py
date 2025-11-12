"""
Session Manager Module

Handles session state management, data persistence, and user session tracking.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st


class SessionManager:
    """
    Manages user session data and persistence.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the session manager.

        Args:
            data_dir: Directory for storing session data. If None, uses default.
        """
        if data_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            data_dir = base_dir / "data" / "sessions"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize session ID
        if 'session_id' not in st.session_state:
            st.session_state.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"

    def save_form_data(self, form_data: Dict[str, Any], protocol_id: Optional[str] = None) -> bool:
        """
        Save form data to file.

        Args:
            form_data: Dictionary containing form data
            protocol_id: Optional protocol identifier

        Returns:
            True if save successful, False otherwise
        """
        try:
            session_id = st.session_state.session_id
            timestamp = datetime.now().isoformat()

            # Prepare data structure
            save_data = {
                "session_id": session_id,
                "timestamp": timestamp,
                "protocol_id": protocol_id,
                "form_data": self._serialize_form_data(form_data)
            }

            # Create filename
            filename = f"{session_id}_{protocol_id or 'data'}.json"
            filepath = self.data_dir / filename

            # Save to file
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True

        except Exception as e:
            st.error(f"Error saving session data: {e}")
            return False

    def load_form_data(self, session_id: Optional[str] = None, protocol_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load form data from file.

        Args:
            session_id: Session ID to load. If None, uses current session.
            protocol_id: Protocol ID to load

        Returns:
            Dictionary containing form data, or None if not found
        """
        try:
            if session_id is None:
                session_id = st.session_state.session_id

            filename = f"{session_id}_{protocol_id or 'data'}.json"
            filepath = self.data_dir / filename

            if not filepath.exists():
                return None

            with open(filepath, 'r') as f:
                save_data = json.load(f)

            return save_data.get("form_data", {})

        except Exception as e:
            st.error(f"Error loading session data: {e}")
            return None

    def _serialize_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize form data to JSON-compatible format.

        Args:
            form_data: Raw form data dictionary

        Returns:
            Serialized form data
        """
        serialized = {}

        for key, value in form_data.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                # For pandas DataFrames
                serialized[key] = value.to_dict()
            elif hasattr(value, '__dict__'):
                # For custom objects
                serialized[key] = str(value)
            else:
                serialized[key] = value

        return serialized

    def get_session_history(self) -> list:
        """
        Get list of available session files.

        Returns:
            List of session file information
        """
        sessions = []

        for filepath in self.data_dir.glob("session_*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                sessions.append({
                    "filename": filepath.name,
                    "session_id": data.get("session_id"),
                    "timestamp": data.get("timestamp"),
                    "protocol_id": data.get("protocol_id")
                })
            except Exception as e:
                continue

        return sorted(sessions, key=lambda x: x.get("timestamp", ""), reverse=True)

    def delete_session_data(self, session_id: str, protocol_id: Optional[str] = None) -> bool:
        """
        Delete session data file.

        Args:
            session_id: Session ID to delete
            protocol_id: Optional protocol ID

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            filename = f"{session_id}_{protocol_id or 'data'}.json"
            filepath = self.data_dir / filename

            if filepath.exists():
                filepath.unlink()
                return True

            return False

        except Exception as e:
            st.error(f"Error deleting session data: {e}")
            return False

    def export_session_data(self, session_id: Optional[str] = None, output_path: Optional[str] = None) -> bool:
        """
        Export session data to a specific location.

        Args:
            session_id: Session ID to export. If None, uses current session.
            output_path: Output file path

        Returns:
            True if export successful, False otherwise
        """
        try:
            if session_id is None:
                session_id = st.session_state.session_id

            # Find all files for this session
            session_files = list(self.data_dir.glob(f"{session_id}_*.json"))

            if not session_files:
                st.warning(f"No data found for session {session_id}")
                return False

            # If output path not specified, use data/outputs
            if output_path is None:
                base_dir = Path(__file__).parent.parent.parent
                output_dir = base_dir / "data" / "outputs"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{session_id}_export.json"

            # Combine all session data
            combined_data = {
                "session_id": session_id,
                "export_timestamp": datetime.now().isoformat(),
                "protocols": []
            }

            for filepath in session_files:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    combined_data["protocols"].append(data)

            # Write combined data
            with open(output_path, 'w') as f:
                json.dump(combined_data, f, indent=2)

            return True

        except Exception as e:
            st.error(f"Error exporting session data: {e}")
            return False

    def clear_current_session(self):
        """Clear current session data from memory (not from disk)."""
        keys_to_clear = ['form_data', 'protocol_data', 'selected_protocol']

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current session.

        Returns:
            Dictionary containing session statistics
        """
        stats = {
            "session_id": st.session_state.session_id,
            "form_data_size": len(st.session_state.get('form_data', {})),
            "has_protocol_loaded": st.session_state.get('protocol_data') is not None,
            "current_protocol": None
        }

        if st.session_state.get('selected_protocol'):
            stats["current_protocol"] = st.session_state.selected_protocol.get('name')

        return stats
