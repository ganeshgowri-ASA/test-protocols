"""
State Manager Module
====================

Manages session state for Streamlit/GenSpark UI applications.
Handles persistence of form data, test progress, and user preferences.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Represents application session state"""
    session_id: str
    user_name: Optional[str] = None
    current_protocol_id: Optional[str] = None
    current_execution_id: Optional[int] = None
    form_data: Dict[str, Any] = field(default_factory=dict)
    test_progress: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Create from dictionary"""
        return cls(**data)


class StateManager:
    """
    State Manager for handling application state in Streamlit/GenSpark UI.

    Features:
    - Manage session state
    - Persist form data
    - Track test progress
    - Handle user preferences
    - Auto-save functionality
    """

    def __init__(self, storage_backend: str = "memory"):
        """
        Initialize State Manager.

        Args:
            storage_backend: Storage backend ('memory', 'file', 'database')
        """
        self.storage_backend = storage_backend
        self._memory_store: Dict[str, SessionState] = {}

    def create_session(
        self,
        session_id: str,
        user_name: Optional[str] = None
    ) -> SessionState:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier
            user_name: User name

        Returns:
            SessionState object
        """
        session = SessionState(
            session_id=session_id,
            user_name=user_name
        )

        self._memory_store[session_id] = session
        logger.info(f"Created new session: {session_id}")

        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Get existing session.

        Args:
            session_id: Session identifier

        Returns:
            SessionState or None
        """
        return self._memory_store.get(session_id)

    def update_session(self, session: SessionState):
        """
        Update session state.

        Args:
            session: SessionState object
        """
        session.last_updated = datetime.now().isoformat()
        self._memory_store[session.session_id] = session

    def set_form_data(
        self,
        session_id: str,
        form_id: str,
        data: Dict[str, Any]
    ):
        """
        Store form data in session.

        Args:
            session_id: Session identifier
            form_id: Form identifier
            data: Form data dictionary
        """
        session = self.get_session(session_id)
        if session:
            session.form_data[form_id] = data
            self.update_session(session)
            logger.debug(f"Stored form data: {form_id}")

    def get_form_data(
        self,
        session_id: str,
        form_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve form data from session.

        Args:
            session_id: Session identifier
            form_id: Form identifier

        Returns:
            Form data dictionary or None
        """
        session = self.get_session(session_id)
        if session:
            return session.form_data.get(form_id)
        return None

    def clear_form_data(self, session_id: str, form_id: Optional[str] = None):
        """
        Clear form data from session.

        Args:
            session_id: Session identifier
            form_id: Form identifier (clears all if None)
        """
        session = self.get_session(session_id)
        if session:
            if form_id:
                session.form_data.pop(form_id, None)
            else:
                session.form_data.clear()
            self.update_session(session)

    def set_test_progress(
        self,
        session_id: str,
        step_id: str,
        completed: bool = True,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Update test progress.

        Args:
            session_id: Session identifier
            step_id: Test step identifier
            completed: Whether step is completed
            data: Additional step data
        """
        session = self.get_session(session_id)
        if session:
            session.test_progress[step_id] = {
                'completed': completed,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
            self.update_session(session)

    def get_test_progress(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get test progress.

        Args:
            session_id: Session identifier

        Returns:
            Test progress dictionary
        """
        session = self.get_session(session_id)
        if session:
            return session.test_progress
        return {}

    def get_completed_steps(self, session_id: str) -> List[str]:
        """
        Get list of completed test steps.

        Args:
            session_id: Session identifier

        Returns:
            List of completed step IDs
        """
        progress = self.get_test_progress(session_id)
        return [
            step_id for step_id, step_data in progress.items()
            if step_data.get('completed', False)
        ]

    def set_preference(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """
        Set user preference.

        Args:
            session_id: Session identifier
            key: Preference key
            value: Preference value
        """
        session = self.get_session(session_id)
        if session:
            session.preferences[key] = value
            self.update_session(session)

    def get_preference(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get user preference.

        Args:
            session_id: Session identifier
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        session = self.get_session(session_id)
        if session:
            return session.preferences.get(key, default)
        return default

    def save_session_to_file(
        self,
        session_id: str,
        file_path: str
    ) -> bool:
        """
        Save session to file.

        Args:
            session_id: Session identifier
            file_path: Output file path

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if not session:
            return False

        try:
            with open(file_path, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.info(f"Session saved to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def load_session_from_file(
        self,
        session_id: str,
        file_path: str
    ) -> Optional[SessionState]:
        """
        Load session from file.

        Args:
            session_id: Session identifier
            file_path: Input file path

        Returns:
            SessionState or None
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            session = SessionState.from_dict(data)
            self._memory_store[session_id] = session
            logger.info(f"Session loaded from: {file_path}")
            return session
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return None

    def delete_session(self, session_id: str):
        """
        Delete session.

        Args:
            session_id: Session identifier
        """
        self._memory_store.pop(session_id, None)
        logger.info(f"Deleted session: {session_id}")

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Clean up old sessions.

        Args:
            max_age_hours: Maximum session age in hours
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_delete = []

        for session_id, session in self._memory_store.items():
            try:
                last_updated = datetime.fromisoformat(session.last_updated)
                if last_updated < cutoff_time:
                    sessions_to_delete.append(session_id)
            except ValueError:
                continue

        for session_id in sessions_to_delete:
            self.delete_session(session_id)

        if sessions_to_delete:
            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
