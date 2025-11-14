"""
Data Entry Page

Interface for entering test data step by step.
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.components.protocol_renderer import (
    render_step_form,
    render_step_summary,
    render_protocol_progress,
    validate_step_data
)
from ui.utils.session_state import mark_step_complete, is_step_complete


def render():
    """Render data entry page"""

    st.header("Data Entry")

    # Check if protocol and test run are selected
    if not st.session_state.get("selected_protocol"):
        st.warning("Please select a protocol first.")
        st.info("Go to 'Protocol Selection' to choose a protocol.")
        return

    if not st.session_state.get("current_test_run"):
        st.warning("No active test run.")
        st.info("Go to 'Protocol Selection' to start a new test run.")
        return

    # Get protocol definition
    protocol_instance = st.session_state.protocol_instance
    protocol_def = protocol_instance.definition

    # Display test run info
    test_run = st.session_state.current_test_run
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Run ID", test_run["run_id"])
    with col2:
        st.metric("Sample ID", test_run["sample_id"])
    with col3:
        st.metric("Operator", test_run["operator"])

    st.markdown("---")

    # Progress indicator
    render_protocol_progress(
        protocol_def.dict(),
        st.session_state.completed_steps,
        st.session_state.current_step
    )

    st.markdown("---")

    # Get current step
    current_step_num = st.session_state.current_step
    current_step_def = None

    for step in protocol_def.steps:
        if step.step_number == current_step_num:
            current_step_def = step
            break

    if not current_step_def:
        st.success("All steps completed!")
        if st.button("Go to Analysis"):
            st.session_state.page_navigation = "Analysis & Results"
            st.rerun()
        return

    # Display completed steps summary
    if st.session_state.completed_steps:
        with st.expander("View Completed Steps", expanded=False):
            for step in protocol_def.steps:
                if is_step_complete(step.step_number):
                    # Get fields for this step
                    step_fields = [
                        f for f in protocol_def.data_fields
                        if f.step_number == step.step_number
                    ]
                    render_step_summary(
                        step.dict(),
                        st.session_state.test_data,
                        [f.dict() for f in step_fields]
                    )

    st.markdown("---")

    # Current step form
    st.markdown("## Current Step")

    # Get fields for current step
    current_fields = [
        f for f in protocol_def.data_fields
        if f.step_number == current_step_num
    ]

    # Render step form
    with st.form(f"step_{current_step_num}_form"):
        form_data = render_step_form(
            current_step_def.dict(),
            [f.dict() for f in current_fields],
            st.session_state.test_data
        )

        st.markdown("---")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            submit = st.form_submit_button("Save & Continue", type="primary", use_container_width=True)
        with col2:
            save = st.form_submit_button("Save Progress", use_container_width=True)
        with col3:
            skip = st.form_submit_button("Skip", use_container_width=True)

        if submit or save:
            # Validate data
            is_valid, errors = validate_step_data([f.dict() for f in current_fields], form_data)

            if not is_valid and submit:
                st.error("Please fix the following errors:")
                for error in errors:
                    st.error(f"- {error}")
            else:
                # Save data
                st.session_state.test_data.update(form_data)

                # Execute step in protocol
                try:
                    result = protocol_instance.execute_step(current_step_num, **form_data)

                    if result.get("success"):
                        st.success(f"Step {current_step_num} completed successfully!")

                        if submit:
                            # Mark step complete and move to next
                            mark_step_complete(current_step_num)
                            st.session_state.current_step = current_step_num + 1
                            st.rerun()
                    else:
                        st.error(f"Error executing step: {result.get('error')}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if skip:
            st.warning("Step skipped. Data not saved.")
            mark_step_complete(current_step_num)
            st.session_state.current_step = current_step_num + 1
            st.rerun()

    # Step navigation
    st.markdown("---")
    st.markdown("### Step Navigation")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_step_num > 1:
            if st.button("⬅️ Previous Step"):
                st.session_state.current_step = current_step_num - 1
                st.rerun()

    with col2:
        # Step selector
        step_options = [f"Step {s.step_number}: {s.name}" for s in protocol_def.steps]
        selected_step_idx = st.selectbox(
            "Jump to step:",
            range(len(step_options)),
            index=current_step_num - 1,
            format_func=lambda i: step_options[i],
            key="step_selector"
        )

        if selected_step_idx + 1 != current_step_num:
            if st.button("Go to Selected Step"):
                st.session_state.current_step = selected_step_idx + 1
                st.rerun()

    with col3:
        if current_step_num < len(protocol_def.steps):
            if st.button("Next Step ➡️"):
                st.session_state.current_step = current_step_num + 1
                st.rerun()
