"""
Parameter Input Component
UI for inputting test parameters
"""

import streamlit as st
from typing import Dict, Any


def render_parameter_input(protocol: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render parameter input form

    Args:
        protocol: Protocol definition

    Returns:
        Dictionary of parameter values
    """
    test_parameters = protocol.get('test_parameters', {})

    if not test_parameters:
        st.info("This protocol has no configurable parameters.")
        return {}

    parameters = {}

    # Group parameters by type/category if needed
    st.markdown("Configure the test parameters below:")

    # Create input fields for each parameter
    for param_name, param_def in test_parameters.items():
        param_type = param_def.get('type', 'number')
        description = param_def.get('description', '')
        default = param_def.get('default')
        unit = param_def.get('unit', '')
        min_val = param_def.get('min')
        max_val = param_def.get('max')
        required = param_def.get('validation') == 'required'

        # Create label with unit
        label = param_name.replace('_', ' ').title()
        if unit:
            label += f" ({unit})"
        if required:
            label += " *"

        # Help text
        help_text = description
        if min_val is not None or max_val is not None:
            range_text = f"Range: {min_val if min_val is not None else '∞'} - {max_val if max_val is not None else '∞'}"
            help_text += f"\n{range_text}"

        # Render appropriate input widget
        if param_type == 'integer':
            value = st.number_input(
                label,
                min_value=int(min_val) if min_val is not None else None,
                max_value=int(max_val) if max_val is not None else None,
                value=int(default) if default is not None else 0,
                step=1,
                help=help_text,
                key=f"param_{param_name}"
            )
        elif param_type == 'number':
            value = st.number_input(
                label,
                min_value=float(min_val) if min_val is not None else None,
                max_value=float(max_val) if max_val is not None else None,
                value=float(default) if default is not None else 0.0,
                step=0.1,
                help=help_text,
                key=f"param_{param_name}"
            )
        elif param_type == 'string':
            value = st.text_input(
                label,
                value=str(default) if default is not None else "",
                help=help_text,
                key=f"param_{param_name}"
            )
        elif param_type == 'boolean':
            value = st.checkbox(
                label,
                value=bool(default) if default is not None else False,
                help=help_text,
                key=f"param_{param_name}"
            )
        else:
            # Default to text input
            value = st.text_input(
                label,
                value=str(default) if default is not None else "",
                help=help_text,
                key=f"param_{param_name}"
            )

        parameters[param_name] = value

    # Validation summary
    st.markdown("---")

    # Show parameter summary
    with st.expander("Parameter Summary"):
        for param_name, value in parameters.items():
            unit = test_parameters[param_name].get('unit', '')
            st.write(f"**{param_name}:** {value} {unit}")

    return parameters


def validate_parameters(parameters: Dict[str, Any], test_parameters: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate parameter values

    Args:
        parameters: Parameter values to validate
        test_parameters: Parameter definitions from protocol

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    for param_name, param_def in test_parameters.items():
        value = parameters.get(param_name)

        # Check required
        if param_def.get('validation') == 'required' and value is None:
            errors.append(f"{param_name} is required")
            continue

        if value is None:
            continue

        # Check range
        min_val = param_def.get('min')
        max_val = param_def.get('max')

        if min_val is not None and value < min_val:
            errors.append(f"{param_name} must be >= {min_val}")

        if max_val is not None and value > max_val:
            errors.append(f"{param_name} must be <= {max_val}")

    return len(errors) == 0, errors
