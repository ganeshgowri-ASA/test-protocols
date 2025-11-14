"""Data entry form component."""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional


class DataEntryForm:
    """Component for entering measurement data."""

    def __init__(self, protocol_data: Dict[str, Any]):
        """
        Initialize data entry form.

        Args:
            protocol_data: Protocol definition data
        """
        self.protocol_data = protocol_data
        self.measurements_spec = protocol_data.get('measurements', {})
        self.required_fields = self.measurements_spec.get('required_fields', [])
        self.optional_fields = self.measurements_spec.get('optional_fields', [])
        self.field_definitions = self.measurements_spec.get('field_definitions', {})

    def render_measurement_form(
        self,
        measurement_type: str = "during_exposure",
        key_prefix: str = "measurement"
    ) -> Optional[Dict[str, Any]]:
        """
        Render measurement entry form.

        Args:
            measurement_type: Type of measurement (initial, during_exposure, post_exposure)
            key_prefix: Prefix for form field keys

        Returns:
            Measurement data dictionary or None if not submitted
        """
        st.markdown(f"### Enter Measurement Data ({measurement_type.replace('_', ' ').title()})")

        measurement_data = {}

        # Use form for better UX
        with st.form(key=f"{key_prefix}_form"):
            # Timestamp
            col1, col2 = st.columns(2)
            with col1:
                measurement_date = st.date_input(
                    "Measurement Date",
                    value=datetime.now().date(),
                    key=f"{key_prefix}_date"
                )
            with col2:
                measurement_time = st.time_input(
                    "Measurement Time",
                    value=datetime.now().time(),
                    key=f"{key_prefix}_time"
                )

            timestamp = datetime.combine(measurement_date, measurement_time)
            measurement_data['timestamp'] = timestamp

            # Electrical parameters
            st.markdown("#### Electrical Parameters")
            elec_col1, elec_col2, elec_col3 = st.columns(3)

            with elec_col1:
                voc = st.number_input(
                    "Voc (V)",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=0.001,
                    format="%.3f",
                    key=f"{key_prefix}_voc"
                )
                measurement_data['voc'] = voc

                isc = st.number_input(
                    "Isc (A)",
                    min_value=0.0,
                    max_value=20.0,
                    value=9.0,
                    step=0.001,
                    format="%.3f",
                    key=f"{key_prefix}_isc"
                )
                measurement_data['isc'] = isc

            with elec_col2:
                pmax = st.number_input(
                    "Pmax (W)",
                    min_value=0.0,
                    max_value=500.0,
                    value=300.0,
                    step=0.01,
                    format="%.2f",
                    key=f"{key_prefix}_pmax"
                )
                measurement_data['pmax'] = pmax

                vmp = st.number_input(
                    "Vmp (V)",
                    min_value=0.0,
                    max_value=100.0,
                    value=33.0,
                    step=0.001,
                    format="%.3f",
                    key=f"{key_prefix}_vmp"
                )
                measurement_data['vmp'] = vmp

            with elec_col3:
                imp = st.number_input(
                    "Imp (A)",
                    min_value=0.0,
                    max_value=20.0,
                    value=9.0,
                    step=0.001,
                    format="%.3f",
                    key=f"{key_prefix}_imp"
                )
                measurement_data['imp'] = imp

                # Calculate fill factor
                if voc > 0 and isc > 0:
                    ff = pmax / (voc * isc)
                else:
                    ff = 0.0

                st.number_input(
                    "Fill Factor",
                    value=ff,
                    disabled=True,
                    format="%.4f",
                    key=f"{key_prefix}_ff"
                )
                measurement_data['fill_factor'] = ff

            # Environmental conditions
            st.markdown("#### Environmental Conditions")
            env_col1, env_col2, env_col3 = st.columns(3)

            with env_col1:
                irradiance = st.number_input(
                    "Irradiance (W/m²)",
                    min_value=0.0,
                    max_value=1500.0,
                    value=1000.0,
                    step=0.1,
                    format="%.1f",
                    key=f"{key_prefix}_irradiance"
                )
                measurement_data['irradiance'] = irradiance

            with env_col2:
                temperature = st.number_input(
                    "Temperature (°C)",
                    min_value=-40.0,
                    max_value=85.0,
                    value=25.0,
                    step=0.1,
                    format="%.1f",
                    key=f"{key_prefix}_temperature"
                )
                measurement_data['temperature'] = temperature

            with env_col3:
                humidity = st.number_input(
                    "Humidity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=50.0,
                    step=0.1,
                    format="%.1f",
                    key=f"{key_prefix}_humidity",
                    help="Optional field"
                )
                measurement_data['humidity'] = humidity

            # Optional fields
            with st.expander("Optional Fields"):
                opt_col1, opt_col2 = st.columns(2)

                with opt_col1:
                    efficiency = st.number_input(
                        "Efficiency (%)",
                        min_value=0.0,
                        max_value=30.0,
                        value=0.0,
                        step=0.01,
                        format="%.2f",
                        key=f"{key_prefix}_efficiency"
                    )
                    if efficiency > 0:
                        measurement_data['efficiency'] = efficiency

                    rs = st.number_input(
                        "Series Resistance (Ω)",
                        min_value=0.0,
                        max_value=10.0,
                        value=0.0,
                        step=0.001,
                        format="%.3f",
                        key=f"{key_prefix}_rs"
                    )
                    if rs > 0:
                        measurement_data['rs'] = rs

                with opt_col2:
                    rsh = st.number_input(
                        "Shunt Resistance (Ω)",
                        min_value=0.0,
                        max_value=10000.0,
                        value=0.0,
                        step=0.1,
                        format="%.1f",
                        key=f"{key_prefix}_rsh"
                    )
                    if rsh > 0:
                        measurement_data['rsh'] = rsh

            # Notes
            notes = st.text_area(
                "Notes (Optional)",
                key=f"{key_prefix}_notes",
                help="Add any additional observations or notes"
            )
            if notes:
                measurement_data['notes'] = notes

            # Operator
            operator = st.text_input(
                "Operator Name",
                key=f"{key_prefix}_operator"
            )
            if operator:
                measurement_data['operator'] = operator

            # Submit button
            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
            with col_submit1:
                submitted = st.form_submit_button("💾 Save Measurement", use_container_width=True)
            with col_submit2:
                st.form_submit_button("🗑️ Clear", use_container_width=True)

            if submitted:
                measurement_data['measurement_type'] = measurement_type
                return measurement_data

        return None

    def render_bulk_import(self, key: str = "bulk_import") -> Optional[List[Dict[str, Any]]]:
        """
        Render bulk data import interface.

        Args:
            key: Unique key for this component

        Returns:
            List of imported measurements or None
        """
        st.markdown("### Bulk Import")

        st.info("""
        **Upload a CSV file** with the following columns:
        - timestamp, voc, isc, pmax, vmp, imp, fill_factor, irradiance, temperature
        - Optional: humidity, efficiency, rs, rsh, operator, notes
        """)

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            key=key
        )

        if uploaded_file is not None:
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_file)

                st.markdown("**Preview:**")
                st.dataframe(df.head())

                st.markdown(f"**Total rows:** {len(df)}")

                if st.button("Import Data", key=f"{key}_import"):
                    # Convert DataFrame to list of dicts
                    measurements = df.to_dict('records')
                    st.success(f"Successfully imported {len(measurements)} measurements!")
                    return measurements

            except Exception as e:
                st.error(f"Error reading file: {e}")

        return None

    def display_measurement_summary(self, measurements: List[Dict[str, Any]]) -> None:
        """
        Display summary of entered measurements.

        Args:
            measurements: List of measurement dictionaries
        """
        if not measurements:
            st.info("No measurements entered yet")
            return

        st.markdown(f"### Measurement Summary ({len(measurements)} measurements)")

        import pandas as pd

        # Create DataFrame
        df = pd.DataFrame(measurements)

        # Display statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Avg Power",
                f"{df['pmax'].mean():.2f} W" if 'pmax' in df else "N/A"
            )

        with col2:
            st.metric(
                "Avg Voc",
                f"{df['voc'].mean():.3f} V" if 'voc' in df else "N/A"
            )

        with col3:
            st.metric(
                "Avg Isc",
                f"{df['isc'].mean():.3f} A" if 'isc' in df else "N/A"
            )

        with col4:
            st.metric(
                "Avg FF",
                f"{df['fill_factor'].mean():.4f}" if 'fill_factor' in df else "N/A"
            )

        # Display table
        st.dataframe(df, use_container_width=True)
