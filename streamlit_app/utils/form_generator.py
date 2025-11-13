"""
Form Generator Module

Dynamically generates Streamlit form components based on field definitions.
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import pandas as pd


class FormGenerator:
    """
    Generates dynamic form fields based on protocol field definitions.
    """

    def __init__(self):
        """Initialize the form generator."""
        self.field_renderers = {
            "text": self._render_text_field,
            "number": self._render_number_field,
            "date": self._render_date_field,
            "datetime": self._render_datetime_field,
            "select": self._render_select_field,
            "multiselect": self._render_multiselect_field,
            "textarea": self._render_textarea_field,
            "checkbox": self._render_checkbox_field,
            "file_upload": self._render_file_upload_field,
            "calculated": self._render_calculated_field
        }

    def render_field(self, field_def: Dict[str, Any], field_key: str) -> Any:
        """
        Render a form field based on its definition.

        Args:
            field_def: Field definition dictionary
            field_key: Unique key for the field in session state

        Returns:
            The value entered/selected by the user
        """
        field_type = field_def.get("field_type", "text")
        renderer = self.field_renderers.get(field_type, self._render_text_field)

        # Check conditional display
        if not self._should_display_field(field_def):
            return None

        return renderer(field_def, field_key)

    def _should_display_field(self, field_def: Dict[str, Any]) -> bool:
        """
        Check if field should be displayed based on conditional logic.

        Args:
            field_def: Field definition dictionary

        Returns:
            True if field should be displayed
        """
        conditional = field_def.get("conditional_display")
        if not conditional:
            return True

        depends_on = conditional.get("depends_on")
        condition = conditional.get("condition")
        expected_value = conditional.get("value")

        # Check if dependency field has the expected value
        if depends_on in st.session_state.form_data:
            actual_value = st.session_state.form_data[depends_on]

            if condition == "equals":
                return actual_value == expected_value
            elif condition == "not_equals":
                return actual_value != expected_value
            elif condition == "greater_than":
                return actual_value > expected_value
            elif condition == "less_than":
                return actual_value < expected_value

        return False

    def _get_field_label(self, field_def: Dict[str, Any]) -> str:
        """Generate field label with optional unit."""
        label = field_def.get("field_name", "Field")
        unit = field_def.get("unit")

        if unit:
            label = f"{label} ({unit})"

        if field_def.get("required", False):
            label = f"{label} *"

        return label

    def _render_text_field(self, field_def: Dict[str, Any], field_key: str) -> str:
        """Render a text input field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")
        default_value = field_def.get("default_value", "")

        value = st.text_input(
            label,
            value=st.session_state.form_data.get(field_key, default_value),
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_number_field(self, field_def: Dict[str, Any], field_key: str) -> float:
        """Render a number input field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")
        default_value = field_def.get("default_value", 0.0)

        validation = field_def.get("validation", {})
        min_val = validation.get("min")
        max_val = validation.get("max")

        # Determine if field expects integer or float
        # Check for explicit type specification in validation
        field_type_spec = validation.get("type", "").lower()

        # Infer type from min/max values if not explicitly specified
        is_integer_field = False
        if field_type_spec in ["integer", "int"]:
            is_integer_field = True
        elif field_type_spec in ["float", "decimal", "number"]:
            is_integer_field = False
        else:
            # Infer from min/max values - if both are integers, treat as integer field
            if min_val is not None and max_val is not None:
                is_integer_field = isinstance(min_val, int) and isinstance(max_val, int)
            elif min_val is not None:
                is_integer_field = isinstance(min_val, int)
            elif max_val is not None:
                is_integer_field = isinstance(max_val, int)

        # Convert all numeric parameters to the same type for consistency
        if is_integer_field:
            # Convert to integers
            if default_value is not None:
                default_value = int(default_value)
            if min_val is not None:
                min_val = int(min_val)
            if max_val is not None:
                max_val = int(max_val)
            step = 1
        else:
            # Convert to floats
            if default_value is not None:
                default_value = float(default_value)
            if min_val is not None:
                min_val = float(min_val)
            if max_val is not None:
                max_val = float(max_val)
            step = None  # Let Streamlit determine appropriate step for floats

        # Get current value and ensure it matches the expected type
        current_value = st.session_state.form_data.get(field_key, default_value)
        if current_value is not None:
            if is_integer_field:
                current_value = int(current_value)
            else:
                current_value = float(current_value)

        value = st.number_input(
            label,
            value=current_value,
            min_value=min_val,
            max_value=max_val,
            step=step,
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_date_field(self, field_def: Dict[str, Any], field_key: str) -> date:
        """Render a date input field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")
        default_value = field_def.get("default_value", date.today())

        if isinstance(default_value, str):
            try:
                default_value = datetime.strptime(default_value, "%Y-%m-%d").date()
            except ValueError:
                default_value = date.today()

        value = st.date_input(
            label,
            value=st.session_state.form_data.get(field_key, default_value),
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_datetime_field(self, field_def: Dict[str, Any], field_key: str) -> datetime:
        """Render a datetime input field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")

        col1, col2 = st.columns(2)

        with col1:
            date_value = st.date_input(
                f"{label} - Date",
                value=date.today(),
                help=help_text,
                key=f"{field_key}_date"
            )

        with col2:
            time_value = st.time_input(
                f"{label} - Time",
                key=f"{field_key}_time"
            )

        datetime_value = datetime.combine(date_value, time_value)
        st.session_state.form_data[field_key] = datetime_value
        return datetime_value

    def _render_select_field(self, field_def: Dict[str, Any], field_key: str) -> str:
        """Render a select dropdown field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")

        validation = field_def.get("validation", {})
        options = validation.get("options", [])

        if not options:
            st.warning(f"No options defined for field: {field_def.get('field_name')}")
            return ""

        default_value = field_def.get("default_value", options[0] if options else "")

        value = st.selectbox(
            label,
            options=options,
            index=options.index(default_value) if default_value in options else 0,
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_multiselect_field(self, field_def: Dict[str, Any], field_key: str) -> List[str]:
        """Render a multi-select field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")

        validation = field_def.get("validation", {})
        options = validation.get("options", [])

        if not options:
            st.warning(f"No options defined for field: {field_def.get('field_name')}")
            return []

        default_value = field_def.get("default_value", [])

        value = st.multiselect(
            label,
            options=options,
            default=default_value,
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_textarea_field(self, field_def: Dict[str, Any], field_key: str) -> str:
        """Render a text area field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")
        default_value = field_def.get("default_value", "")

        value = st.text_area(
            label,
            value=st.session_state.form_data.get(field_key, default_value),
            help=help_text,
            key=field_key,
            height=150
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_checkbox_field(self, field_def: Dict[str, Any], field_key: str) -> bool:
        """Render a checkbox field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")
        default_value = field_def.get("default_value", False)

        value = st.checkbox(
            label,
            value=st.session_state.form_data.get(field_key, default_value),
            help=help_text,
            key=field_key
        )

        st.session_state.form_data[field_key] = value
        return value

    def _render_file_upload_field(self, field_def: Dict[str, Any], field_key: str):
        """Render a file upload field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")

        validation = field_def.get("validation", {})
        accepted_types = validation.get("accepted_types", None)

        uploaded_file = st.file_uploader(
            label,
            type=accepted_types,
            help=help_text,
            key=field_key
        )

        if uploaded_file:
            st.session_state.form_data[field_key] = uploaded_file
            return uploaded_file

        return None

    def _render_calculated_field(self, field_def: Dict[str, Any], field_key: str):
        """Render a calculated/read-only field."""
        label = self._get_field_label(field_def)
        help_text = field_def.get("description")

        # For now, just display as info
        calculation = field_def.get("calculation", {})
        formula = calculation.get("formula", "")

        st.text_input(
            label,
            value="[Calculated]",
            help=f"{help_text}\nFormula: {formula}",
            disabled=True,
            key=field_key
        )

        return None

    def render_data_table(self, table_def: Dict[str, Any], table_key: str):
        """
        Render an editable data table.

        Args:
            table_def: Table definition dictionary
            table_key: Unique key for the table
        """
        table_name = table_def.get("table_name", "Data Table")
        columns = table_def.get("columns", [])
        min_rows = table_def.get("min_rows", 1)
        editable = table_def.get("editable", True)

        # Initialize table data in session state
        if table_key not in st.session_state.form_data:
            # Create empty DataFrame with proper columns
            column_names = [col.get("column_name", f"Column {i}") for i, col in enumerate(columns)]
            st.session_state.form_data[table_key] = pd.DataFrame(
                columns=column_names,
                data=[[None] * len(column_names) for _ in range(min_rows)]
            )

        # Display data editor
        edited_df = st.data_editor(
            st.session_state.form_data[table_key],
            use_container_width=True,
            num_rows="dynamic" if editable else "fixed",
            key=f"{table_key}_editor"
        )

        st.session_state.form_data[table_key] = edited_df

        # Display column info
        with st.expander("ℹ️ Column Information"):
            for col in columns:
                col_name = col.get("column_name", "Column")
                col_type = col.get("data_type", "text")
                col_unit = col.get("unit", "")
                required = col.get("required", False)

                info_text = f"**{col_name}** - Type: {col_type}"
                if col_unit:
                    info_text += f", Unit: {col_unit}"
                if required:
                    info_text += " (Required)"

                st.markdown(info_text)
