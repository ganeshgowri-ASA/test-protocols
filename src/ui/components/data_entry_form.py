"""
Data Entry Form Component

Dynamic form generation from protocol definitions.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime


class DataEntryForm:
    """Dynamic data entry form component."""

    def __init__(self):
        """Initialize the DataEntryForm."""
        pass

    def render_step_form(
        self,
        substep: Dict[str, Any],
        step_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Render a data entry form for a substep.

        Args:
            substep: Substep definition
            step_key: Unique key for this step (e.g., "1.1")

        Returns:
            Dictionary of collected data or None if not submitted
        """
        st.subheader(f"Step {step_key}: {substep['name']}")

        if substep.get('description'):
            st.info(substep['description'])

        # Display instructions if present
        if 'instructions' in substep:
            with st.expander("Instructions", expanded=True):
                for instruction in substep['instructions']:
                    st.write(f"- {instruction}")

        # Display test conditions if present
        if 'conditions' in substep:
            with st.expander("Test Conditions", expanded=True):
                conditions = substep['conditions']
                for key, value in conditions.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        # Render data fields
        data_fields = substep.get('data_fields', [])

        if not data_fields:
            st.info("No data collection required for this step.")
            if st.button("Mark as Complete", key=f"complete_{step_key}"):
                return {}
            return None

        # Create form
        with st.form(key=f"form_{step_key}"):
            data = {}

            for field_def in data_fields:
                field_value = self._render_field(field_def, step_key)
                if field_value is not None:
                    data[field_def['field_id']] = field_value

            # Submit button
            submitted = st.form_submit_button("Submit Data")

            if submitted:
                # Validate required fields
                missing_fields = []
                for field_def in data_fields:
                    if field_def.get('required', False):
                        if field_def['field_id'] not in data or data[field_def['field_id']] is None:
                            missing_fields.append(field_def.get('label', field_def['field_id']))

                if missing_fields:
                    st.error(f"Missing required fields: {', '.join(missing_fields)}")
                    return None

                return data

        return None

    def _render_field(
        self,
        field_def: Dict[str, Any],
        step_key: str
    ) -> Any:
        """
        Render a single form field.

        Args:
            field_def: Field definition
            step_key: Step key for unique widget keys

        Returns:
            Field value
        """
        field_id = field_def['field_id']
        field_type = field_def['type']
        label = field_def.get('label', field_id.replace('_', ' ').title())
        required = field_def.get('required', False)
        unit = field_def.get('unit', '')

        # Add asterisk for required fields
        if required:
            label = f"{label} *"

        # Add unit to label if present
        if unit:
            label = f"{label} ({unit})"

        key = f"{step_key}_{field_id}"

        # Render based on field type
        if field_type == 'number':
            min_val = field_def.get('min')
            max_val = field_def.get('max')
            decimal_places = field_def.get('decimal_places', 2)
            step = 10 ** (-decimal_places) if decimal_places > 0 else 1

            value = st.number_input(
                label,
                min_value=min_val,
                max_value=max_val,
                step=step,
                format=f"%.{decimal_places}f",
                key=key,
                help=field_def.get('description')
            )
            return value if value != 0 or not required else None

        elif field_type == 'text':
            value = st.text_area(
                label,
                key=key,
                help=field_def.get('description')
            )
            return value if value else None

        elif field_type == 'boolean':
            return st.checkbox(
                label,
                key=key,
                help=field_def.get('description')
            )

        elif field_type == 'datetime':
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input(
                    f"{label} - Date",
                    key=f"{key}_date",
                    help=field_def.get('description')
                )
            with col2:
                time = st.time_input(
                    f"{label} - Time",
                    key=f"{key}_time"
                )

            if date and time:
                return datetime.combine(date, time).isoformat()
            return None

        elif field_type == 'multiselect':
            options = field_def.get('options', [])
            return st.multiselect(
                label,
                options=options,
                key=key,
                help=field_def.get('description')
            )

        elif field_type == 'select':
            options = field_def.get('options', [])
            return st.selectbox(
                label,
                options=options,
                key=key,
                help=field_def.get('description')
            )

        elif field_type == 'file':
            file_types = field_def.get('file_types', [])
            uploaded_file = st.file_uploader(
                label,
                type=file_types if file_types else None,
                key=key,
                help=field_def.get('description')
            )

            if uploaded_file:
                # In production, save file and return path
                return uploaded_file.name

            return None

        else:
            st.warning(f"Unknown field type: {field_type}")
            return None

    def render_measurements_table(
        self,
        measurements: List[Dict[str, Any]],
        title: str = "Measurements"
    ):
        """
        Render a table of measurements.

        Args:
            measurements: List of measurement dictionaries
            title: Table title
        """
        st.subheader(title)

        if not measurements:
            st.info("No measurements recorded yet.")
            return

        # Convert to display format
        import pandas as pd

        df_data = []
        for m in measurements:
            df_data.append({
                'Step': f"{m.get('step_id', '')}.{m.get('substep_id', '')}",
                'Field': m.get('field_id', ''),
                'Value': m.get('value', ''),
                'Unit': m.get('unit', ''),
                'Time': m.get('timestamp', '')
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

    def render_progress(
        self,
        total_steps: int,
        completed_steps: int,
        current_step: Optional[int] = None
    ):
        """
        Render test progress.

        Args:
            total_steps: Total number of steps
            completed_steps: Number of completed steps
            current_step: Current step number
        """
        progress = completed_steps / total_steps if total_steps > 0 else 0

        st.subheader("Test Progress")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Completed Steps", f"{completed_steps}/{total_steps}")

        with col2:
            st.metric("Progress", f"{progress * 100:.1f}%")

        with col3:
            if current_step:
                st.metric("Current Step", current_step)

        st.progress(progress)
