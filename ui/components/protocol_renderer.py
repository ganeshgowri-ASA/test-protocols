"""
Protocol Renderer Component

Dynamically renders protocol steps and data entry forms from JSON definitions.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime, date


def render_data_field(field: Dict[str, Any], value: Any = None) -> Any:
    """
    Render a single data field based on its type and configuration.

    Args:
        field: Field definition dictionary
        value: Current value (if any)

    Returns:
        User input value
    """
    field_id = field["field_id"]
    field_name = field["name"]
    field_type = field["type"]
    required = field.get("required", False)
    description = field.get("description", "")
    validation = field.get("validation", {})

    # Add required indicator
    label = f"{field_name} {'*' if required else ''}"

    # Add help text
    help_text = description
    if field.get("unit"):
        help_text += f" (Unit: {field['unit']})"

    # Render based on type
    if field_type == "number":
        min_val = validation.get("min", None)
        max_val = validation.get("max", None)
        return st.number_input(
            label,
            min_value=min_val,
            max_value=max_val,
            value=value if value is not None else (min_val if min_val is not None else 0.0),
            help=help_text,
            key=field_id
        )

    elif field_type == "text":
        return st.text_input(
            label,
            value=value if value is not None else "",
            help=help_text,
            key=field_id
        )

    elif field_type == "date":
        default_date = date.today() if value is None else value
        if isinstance(default_date, str):
            default_date = datetime.fromisoformat(default_date).date()
        return st.date_input(
            label,
            value=default_date,
            help=help_text,
            key=field_id
        )

    elif field_type == "datetime":
        default_datetime = datetime.now() if value is None else value
        if isinstance(default_datetime, str):
            default_datetime = datetime.fromisoformat(default_datetime)
        return st.text_input(
            label,
            value=default_datetime.isoformat() if isinstance(default_datetime, datetime) else default_datetime,
            help=help_text + " (ISO format: YYYY-MM-DDTHH:MM:SS)",
            key=field_id
        )

    elif field_type == "boolean":
        return st.checkbox(
            label,
            value=value if value is not None else False,
            help=help_text,
            key=field_id
        )

    elif field_type == "select":
        options = validation.get("options", [])
        default_index = 0
        if value and value in options:
            default_index = options.index(value)
        return st.selectbox(
            label,
            options=options,
            index=default_index,
            help=help_text,
            key=field_id
        )

    elif field_type == "multiselect":
        options = validation.get("options", [])
        default_values = value if isinstance(value, list) else []
        return st.multiselect(
            label,
            options=options,
            default=default_values,
            help=help_text,
            key=field_id
        )

    elif field_type == "file":
        return st.file_uploader(
            label,
            help=help_text,
            key=field_id
        )

    else:
        st.warning(f"Unknown field type: {field_type}")
        return st.text_input(label, value=value or "", help=help_text, key=field_id)


def render_step_form(step: Dict[str, Any], fields: List[Dict[str, Any]],
                    current_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render a form for a protocol step with its associated data fields.

    Args:
        step: Step definition dictionary
        fields: List of field definitions for this step
        current_data: Current test data

    Returns:
        Dictionary of collected form data
    """
    st.subheader(f"Step {step['step_number']}: {step['name']}")

    # Display step information
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**Type:** {step['type']}")
        st.markdown(f"**Description:** {step['description']}")

        if step.get("duration"):
            duration = step["duration"]
            st.markdown(f"**Duration:** {duration['value']} {duration['unit']}")

    with col2:
        if step.get("automated"):
            st.info("🤖 Automated")
        else:
            st.info("👤 Manual")

    # Quality checks
    if step.get("quality_checks"):
        with st.expander("Quality Checks"):
            for check in step["quality_checks"]:
                st.markdown(f"- {check}")

    st.markdown("---")

    # Render data fields
    form_data = {}

    if fields:
        st.markdown("### Data Entry")

        # Group fields into columns for better layout
        num_fields = len(fields)
        if num_fields <= 2:
            cols = st.columns(num_fields)
        else:
            # Create rows of 2 columns
            for i in range(0, num_fields, 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < num_fields:
                        field = fields[i + j]
                        with col:
                            value = current_data.get(field["field_id"])
                            form_data[field["field_id"]] = render_data_field(field, value)
    else:
        cols = [st.columns(1)[0]]  # Single column
        for field in fields:
            with cols[0] if len(cols) == 1 else st.container():
                value = current_data.get(field["field_id"])
                form_data[field["field_id"]] = render_data_field(field, value)

    return form_data


def render_step_summary(step: Dict[str, Any], data: Dict[str, Any],
                       fields: List[Dict[str, Any]]) -> None:
    """
    Render a summary view of completed step data.

    Args:
        step: Step definition dictionary
        data: Step data
        fields: Field definitions
    """
    with st.expander(f"Step {step['step_number']}: {step['name']} ✓", expanded=False):
        st.markdown(f"**Status:** Completed")

        if fields:
            st.markdown("**Data:**")
            for field in fields:
                field_id = field["field_id"]
                if field_id in data:
                    value = data[field_id]
                    unit = field.get("unit", "")
                    st.markdown(f"- **{field['name']}:** {value} {unit}")


def render_protocol_progress(protocol_definition: Dict[str, Any],
                            completed_steps: List[int],
                            current_step: int) -> None:
    """
    Render protocol progress indicator.

    Args:
        protocol_definition: Full protocol definition
        completed_steps: List of completed step numbers
        current_step: Current step number
    """
    total_steps = len(protocol_definition["steps"])
    progress = len(completed_steps) / total_steps

    st.progress(progress)
    st.markdown(f"**Progress:** {len(completed_steps)}/{total_steps} steps completed")

    # Step timeline
    cols = st.columns(min(total_steps, 10))
    for i, step in enumerate(protocol_definition["steps"][:10]):
        step_num = step["step_number"]
        with cols[i]:
            if step_num in completed_steps:
                st.markdown(f"✅ {step_num}")
            elif step_num == current_step:
                st.markdown(f"▶️ {step_num}")
            else:
                st.markdown(f"⭕ {step_num}")


def validate_step_data(fields: List[Dict[str, Any]],
                      data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate data for a step.

    Args:
        fields: Field definitions
        data: Data to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    for field in fields:
        field_id = field["field_id"]
        field_name = field["name"]

        # Check required fields
        if field.get("required", False):
            if field_id not in data or data[field_id] is None or data[field_id] == "":
                errors.append(f"Required field missing: {field_name}")
                continue

        # Skip validation if field not present
        if field_id not in data:
            continue

        value = data[field_id]

        # Type-specific validation
        if field["type"] == "number" and field.get("validation"):
            validation = field["validation"]
            if "min" in validation and value < validation["min"]:
                errors.append(f"{field_name} must be >= {validation['min']}")
            if "max" in validation and value > validation["max"]:
                errors.append(f"{field_name} must be <= {validation['max']}")

    return len(errors) == 0, errors
