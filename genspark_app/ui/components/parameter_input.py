"""
Smart Parameter Input Components

Provides interactive, validated input components with:
- Conditional fields
- Smart dropdowns
- Auto-validation
- Real-time feedback
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import re


class ParameterInput:
    """Smart parameter input component with validation"""

    @staticmethod
    def render_input(param_spec: Dict[str, Any], current_value: Any = None) -> Any:
        """
        Render appropriate input component based on parameter specification

        Args:
            param_spec: Parameter specification from protocol template
            current_value: Current parameter value (for pre-filling)

        Returns:
            User input value
        """
        param_name = param_spec['name']
        param_type = param_spec['type']
        label = param_spec.get('label', param_name)
        description = param_spec.get('description', '')
        required = param_spec.get('required', False)
        ui_config = param_spec.get('ui', {})

        # Add required indicator
        if required:
            label = f"{label} *"

        # Render based on UI component type
        component_type = ui_config.get('component', 'text_input')

        if component_type == 'text_input':
            value = st.text_input(
                label,
                value=current_value or '',
                placeholder=ui_config.get('placeholder', ''),
                help=description
            )

        elif component_type == 'number_input':
            step = ui_config.get('step', 0.1 if param_type == 'float' else 1)
            min_val = param_spec.get('validation', {}).get('min')
            max_val = param_spec.get('validation', {}).get('max')

            value = st.number_input(
                label,
                value=float(current_value) if current_value else (param_spec.get('default') or 0.0),
                step=step,
                min_value=min_val,
                max_value=max_val,
                help=description
            )

        elif component_type == 'select':
            options = param_spec.get('options', [])
            default_val = param_spec.get('default')
            index = options.index(default_val) if default_val in options else 0

            value = st.selectbox(
                label,
                options=options,
                index=index,
                help=description
            )

        elif component_type == 'smart_dropdown':
            # Smart dropdown with autocomplete
            options = param_spec.get('options', [])
            if not options:
                # Would load from database in production
                options = ['Option 1', 'Option 2', 'Option 3']

            allow_custom = ui_config.get('allow_custom', False)

            if allow_custom:
                value = st.text_input(
                    label,
                    value=current_value or '',
                    help=description + " (You can enter a custom value)"
                )
                # Show suggestions
                if options:
                    st.caption(f"Suggestions: {', '.join(options[:5])}")
            else:
                value = st.selectbox(label, options=options, help=description)

        elif component_type == 'checkbox':
            default_val = param_spec.get('default', False)
            value = st.checkbox(
                label,
                value=current_value if current_value is not None else default_val,
                help=description
            )

        else:
            # Fallback to text input
            value = st.text_input(label, value=current_value or '', help=description)

        # Validate input
        if value:
            is_valid, error_msg = ParameterInput.validate_input(value, param_spec)
            if not is_valid:
                st.error(f"❌ {error_msg}")
            elif is_valid and error_msg is None:
                st.success("✓ Valid")

        return value

    @staticmethod
    def validate_input(value: Any, param_spec: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input value against parameter specification

        Returns:
            (is_valid, error_message)
        """
        param_type = param_spec.get('type')
        validation = param_spec.get('validation', {})

        # Type validation
        if param_type == 'float':
            try:
                value = float(value)
            except (TypeError, ValueError):
                return False, "Must be a number"

            # Range validation
            if 'min' in validation and value < validation['min']:
                return False, validation.get('message', f"Must be >= {validation['min']}")
            if 'max' in validation and value > validation['max']:
                return False, validation.get('message', f"Must be <= {validation['max']}")

        elif param_type == 'integer':
            try:
                value = int(value)
            except (TypeError, ValueError):
                return False, "Must be an integer"

            if 'min' in validation and value < validation['min']:
                return False, validation.get('message', f"Must be >= {validation['min']}")
            if 'max' in validation and value > validation['max']:
                return False, validation.get('message', f"Must be <= {validation['max']}")

        elif param_type == 'string':
            if 'pattern' in validation:
                pattern = validation['pattern']
                if not re.match(pattern, str(value)):
                    return False, validation.get('message', f"Invalid format")

        return True, None

    @staticmethod
    def render_conditional_parameters(param_specs: List[Dict[str, Any]],
                                     current_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render all parameters with conditional logic

        Args:
            param_specs: List of parameter specifications
            current_values: Current parameter values

        Returns:
            Dictionary of parameter values
        """
        values = {}

        for param_spec in param_specs:
            param_name = param_spec['name']

            # Check conditional display
            if 'conditional' in param_spec:
                conditional = param_spec['conditional']
                depends_on = conditional.get('depends_on')
                show_when = conditional.get('show_when')

                if depends_on in current_values:
                    if current_values[depends_on] != show_when:
                        # Don't show this parameter
                        continue

            # Render the parameter input
            current_val = current_values.get(param_name)
            value = ParameterInput.render_input(param_spec, current_val)
            values[param_name] = value

        return values


class ParameterForm:
    """Complete parameter input form with sections"""

    @staticmethod
    def render_form(protocol_template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render complete parameter input form

        Args:
            protocol_template: Protocol template with parameter specifications

        Returns:
            Dictionary of all parameter values
        """
        st.header("Test Parameters")
        st.markdown("Fill in the required test parameters below.")

        param_specs = protocol_template.get('input_parameters', [])

        # Sort by UI order if specified
        param_specs_sorted = sorted(
            param_specs,
            key=lambda x: x.get('ui', {}).get('order', 999)
        )

        # Track values for conditional rendering
        if 'param_values' not in st.session_state:
            st.session_state.param_values = {}

        # Render parameters
        for param_spec in param_specs_sorted:
            param_name = param_spec['name']

            # Check conditional display
            should_display = True
            if 'conditional' in param_spec:
                conditional = param_spec['conditional']
                depends_on = conditional.get('depends_on')
                show_when = conditional.get('show_when')

                if depends_on in st.session_state.param_values:
                    if st.session_state.param_values[depends_on] != show_when:
                        should_display = False

            if should_display:
                current_val = st.session_state.param_values.get(param_name)
                value = ParameterInput.render_input(param_spec, current_val)
                st.session_state.param_values[param_name] = value

        return st.session_state.param_values
