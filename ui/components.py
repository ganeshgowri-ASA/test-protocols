"""
Reusable UI components
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Callable
import pandas as pd


class UIComponents:
    """
    Reusable UI components for test protocols
    """

    @staticmethod
    def render_header(title: str, description: str):
        """Render page header"""
        st.title(title)
        st.markdown(f"*{description}*")
        st.markdown("---")

    @staticmethod
    def render_protocol_info(protocol_id: str, version: str, standard: str):
        """Render protocol information card"""
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protocol", protocol_id)
        with col2:
            st.metric("Version", version)
        with col3:
            st.metric("Standard", standard)

    @staticmethod
    def render_sample_info_form() -> Dict[str, Any]:
        """
        Render sample information form

        Returns:
            Dictionary of sample information
        """
        st.subheader("Sample Information")

        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input(
                "Sample ID *",
                help="Unique identifier for the sample",
                key="sample_id"
            )

            module_type = st.text_input(
                "Module Type *",
                help="PV module type/model",
                key="module_type"
            )

            manufacturer = st.text_input(
                "Manufacturer",
                help="Module manufacturer",
                key="manufacturer"
            )

            serial_number = st.text_input(
                "Serial Number",
                help="Module serial number",
                key="serial_number"
            )

        with col2:
            batch_id = st.text_input(
                "Batch ID",
                help="Production batch identifier",
                key="batch_id"
            )

            cell_technology = st.selectbox(
                "Cell Technology",
                options=["", "mono-Si", "poly-Si", "CdTe", "CIGS", "a-Si", "HIT", "PERC", "TOPCon", "other"],
                help="Solar cell technology type",
                key="cell_technology"
            )

            rated_power = st.number_input(
                "Rated Power (W)",
                min_value=0.0,
                help="Rated power at STC",
                key="rated_power"
            )

            module_area = st.number_input(
                "Module Area (m²) *",
                min_value=0.0,
                max_value=10.0,
                value=1.6,
                step=0.01,
                help="Module area in square meters",
                key="module_area"
            )

            num_cells = st.number_input(
                "Number of Cells",
                min_value=1,
                value=60,
                step=1,
                help="Number of cells in module",
                key="num_cells"
            )

        return {
            "sample_id": sample_id,
            "module_type": module_type,
            "manufacturer": manufacturer,
            "serial_number": serial_number,
            "batch_id": batch_id,
            "cell_technology": cell_technology if cell_technology else None,
            "rated_power": rated_power if rated_power > 0 else None,
            "module_area": module_area,
            "num_cells": int(num_cells)
        }

    @staticmethod
    def render_test_conditions_form(
        target_temp: float = 25.0,
        irradiance_levels: List[int] = [200, 400, 600, 800]
    ) -> Dict[str, Any]:
        """
        Render test conditions form

        Args:
            target_temp: Target temperature
            irradiance_levels: Required irradiance levels

        Returns:
            Dictionary of test conditions
        """
        st.subheader("Test Conditions")

        col1, col2 = st.columns(2)

        with col1:
            temperature = st.number_input(
                f"Temperature (°C) *",
                value=target_temp,
                help=f"Target: {target_temp}°C ± 2°C",
                key="temperature"
            )

            spectrum = st.selectbox(
                "Solar Spectrum",
                options=["AM1.5G", "AM1.5D"],
                help="Solar spectrum standard",
                key="spectrum"
            )

            operator = st.text_input(
                "Operator",
                help="Test operator name/ID",
                key="operator"
            )

        with col2:
            st.markdown("**Required Irradiance Levels (W/m²)**")
            st.write(", ".join([f"{irr}" for irr in irradiance_levels]))

            equipment_id = st.text_input(
                "Equipment ID",
                help="Test equipment identifier",
                key="equipment_id"
            )

            lab_location = st.text_input(
                "Lab Location",
                help="Laboratory location",
                key="lab_location"
            )

        # Ambient conditions (optional, expandable)
        with st.expander("Ambient Conditions (Optional)"):
            humidity = st.number_input(
                "Relative Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                key="humidity"
            )

            pressure = st.number_input(
                "Atmospheric Pressure (kPa)",
                value=101.325,
                key="pressure"
            )

        return {
            "temperature": temperature,
            "temperature_tolerance": 2.0,
            "spectrum": spectrum,
            "irradiance_levels": irradiance_levels,
            "irradiance_tolerance": 10.0,
            "operator": operator if operator else None,
            "equipment_id": equipment_id if equipment_id else None,
            "lab_location": lab_location if lab_location else None,
            "ambient_conditions": {
                "humidity": humidity,
                "pressure": pressure
            }
        }

    @staticmethod
    def render_measurement_input(
        irradiance: int,
        key_prefix: str
    ) -> Optional[Dict[str, Any]]:
        """
        Render measurement input form for a single irradiance level

        Args:
            irradiance: Target irradiance level (W/m²)
            key_prefix: Unique key prefix for widgets

        Returns:
            Measurement data dictionary or None
        """
        st.markdown(f"#### {irradiance} W/m²")

        col1, col2 = st.columns(2)

        with col1:
            actual_irradiance = st.number_input(
                f"Actual Irradiance (W/m²)",
                value=float(irradiance),
                min_value=0.0,
                key=f"{key_prefix}_actual_irradiance"
            )

            actual_temp = st.number_input(
                f"Actual Temperature (°C)",
                value=25.0,
                key=f"{key_prefix}_actual_temp"
            )

        with col2:
            voc = st.number_input(
                "Voc (V)",
                min_value=0.0,
                key=f"{key_prefix}_voc"
            )

            isc = st.number_input(
                "Isc (A)",
                min_value=0.0,
                key=f"{key_prefix}_isc"
            )

        # I-V curve data input
        st.markdown("**I-V Curve Data**")

        upload_method = st.radio(
            "Input Method",
            options=["Upload CSV", "Manual Entry"],
            key=f"{key_prefix}_method",
            horizontal=True
        )

        voltage = []
        current = []

        if upload_method == "Upload CSV":
            uploaded_file = st.file_uploader(
                "Upload I-V curve data (CSV with 'voltage' and 'current' columns)",
                type=['csv'],
                key=f"{key_prefix}_upload"
            )

            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'voltage' in df.columns and 'current' in df.columns:
                        voltage = df['voltage'].tolist()
                        current = df['current'].tolist()
                        st.success(f"Loaded {len(voltage)} data points")

                        # Show preview
                        with st.expander("Data Preview"):
                            st.dataframe(df.head(10))
                    else:
                        st.error("CSV must contain 'voltage' and 'current' columns")
                except Exception as e:
                    st.error(f"Error reading CSV: {str(e)}")
        else:
            # Manual entry using text area
            st.info("Enter voltage and current values (one pair per line, comma-separated)")

            col_v, col_i = st.columns(2)

            with col_v:
                voltage_text = st.text_area(
                    "Voltage (V)",
                    height=200,
                    key=f"{key_prefix}_voltage_text",
                    help="One value per line"
                )

            with col_i:
                current_text = st.text_area(
                    "Current (A)",
                    height=200,
                    key=f"{key_prefix}_current_text",
                    help="One value per line"
                )

            if voltage_text and current_text:
                try:
                    voltage = [float(v.strip()) for v in voltage_text.split('\n') if v.strip()]
                    current = [float(i.strip()) for i in current_text.split('\n') if i.strip()]

                    if len(voltage) != len(current):
                        st.warning(f"Voltage ({len(voltage)} points) and current ({len(current)} points) must have same length")
                    else:
                        st.success(f"Entered {len(voltage)} data points")
                except ValueError:
                    st.error("Invalid number format. Please enter numeric values only.")

        if not voltage or not current:
            return None

        return {
            "actual_irradiance": actual_irradiance,
            "actual_temperature": actual_temp,
            "iv_curve": {
                "voltage": voltage,
                "current": current,
                "num_points": len(voltage)
            },
            "raw_measurements": {
                "voc": voc if voc > 0 else None,
                "isc": isc if isc > 0 else None
            },
            "timestamp": pd.Timestamp.now().isoformat()
        }

    @staticmethod
    def render_validation_results(is_valid: bool, errors: List[str]):
        """
        Render validation results

        Args:
            is_valid: Whether validation passed
            errors: List of error messages
        """
        if is_valid:
            st.success("✓ All validations passed")
        else:
            st.error("✗ Validation failed")
            for error in errors:
                st.error(f"• {error}")

    @staticmethod
    def render_results_table(results: Dict[str, Any]):
        """
        Render results as a table

        Args:
            results: Results dictionary
        """
        by_irradiance = results.get("by_irradiance", {})

        if not by_irradiance:
            st.warning("No results available")
            return

        # Create DataFrame
        rows = []
        for irr_key in sorted(by_irradiance.keys(), key=lambda x: int(x)):
            level_results = by_irradiance[irr_key]
            rows.append({
                "Irradiance (W/m²)": int(irr_key),
                "Pmax (W)": f"{level_results['pmax']:.3f}",
                "Vmp (V)": f"{level_results['vmp']:.2f}",
                "Imp (A)": f"{level_results['imp']:.3f}",
                "Voc (V)": f"{level_results['voc']:.2f}",
                "Isc (A)": f"{level_results['isc']:.3f}",
                "Fill Factor": f"{level_results['fill_factor']:.4f}",
                "Efficiency (%)": f"{level_results['efficiency']:.2f}",
                "Quality": level_results.get("quality_indicators", {}).get("curve_quality", "N/A")
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def render_download_buttons(data: Dict[str, Any], prefix: str = "lic001"):
        """
        Render download buttons for different formats

        Args:
            data: Data to download
            prefix: Filename prefix
        """
        import json

        st.subheader("Download Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            json_str = json.dumps(data, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"{prefix}_results.json",
                mime="application/json"
            )

        with col2:
            # Convert to CSV
            if "results" in data and "by_irradiance" in data["results"]:
                results = data["results"]["by_irradiance"]
                rows = []
                for irr_key, level_results in results.items():
                    rows.append({
                        "irradiance": int(irr_key),
                        **level_results
                    })
                df = pd.DataFrame(rows)
                csv_str = df.to_csv(index=False)

                st.download_button(
                    label="📊 Download CSV",
                    data=csv_str,
                    file_name=f"{prefix}_results.csv",
                    mime="text/csv"
                )

        with col3:
            # Report
            from datetime import datetime
            report = f"""
LIC-001 Low Irradiance Conditions Test Report
==============================================

Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Protocol: LIC-001
Standard: IEC 61215-1:2021

Sample Information:
-------------------
Sample ID: {data.get('sample_info', {}).get('sample_id', 'N/A')}
Module Type: {data.get('sample_info', {}).get('module_type', 'N/A')}

Test Summary:
-------------
"""
            if "results" in data and "summary" in data["results"]:
                summary = data["results"]["summary"]
                report += f"Test Passed: {summary.get('test_passed', 'N/A')}\n"
                report += f"Quality Score: {summary.get('quality_score', 0):.1f}/100\n"

            st.download_button(
                label="📝 Download Report",
                data=report,
                file_name=f"{prefix}_report.txt",
                mime="text/plain"
            )
