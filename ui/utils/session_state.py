"""
Session State Management

Utilities for managing Streamlit session state.
"""

import streamlit as st
from typing import Any, Dict


def initialize_session_state() -> None:
    """Initialize session state variables"""

    # Protocol selection
    if "selected_protocol" not in st.session_state:
        st.session_state.selected_protocol = None

    if "protocol_instance" not in st.session_state:
        st.session_state.protocol_instance = None

    # Test run management
    if "current_test_run" not in st.session_state:
        st.session_state.current_test_run = None

    if "test_data" not in st.session_state:
        st.session_state.test_data = {}

    if "current_step" not in st.session_state:
        st.session_state.current_step = 1

    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = []

    # Data validation
    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = []

    # QC results
    if "qc_results" not in st.session_state:
        st.session_state.qc_results = []

    # Analysis results
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}

    # UI state
    if "show_advanced_options" not in st.session_state:
        st.session_state.show_advanced_options = False


def reset_test_run() -> None:
    """Reset test run state"""
    st.session_state.current_test_run = None
    st.session_state.test_data = {}
    st.session_state.current_step = 1
    st.session_state.completed_steps = []
    st.session_state.validation_errors = []
    st.session_state.qc_results = []
    st.session_state.analysis_results = {}


def update_test_data(field_id: str, value: Any) -> None:
    """Update test data field"""
    if "test_data" not in st.session_state:
        st.session_state.test_data = {}
    st.session_state.test_data[field_id] = value


def get_test_data(field_id: str, default: Any = None) -> Any:
    """Get test data field value"""
    return st.session_state.test_data.get(field_id, default)


def mark_step_complete(step_number: int) -> None:
    """Mark a step as completed"""
    if step_number not in st.session_state.completed_steps:
        st.session_state.completed_steps.append(step_number)


def is_step_complete(step_number: int) -> bool:
    """Check if step is completed"""
    return step_number in st.session_state.completed_steps
