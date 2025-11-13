"""
PERF-001: Interactive Streamlit UI
Temperature Performance Testing Interface

Features:
- Dynamic form with conditional fields
- Real-time data validation
- Interactive Plotly visualizations
- Temperature-power curve analysis
- Export to JSON/PDF reports
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import date, datetime
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "python"))

from perf_001_engine import (
    PERF001Calculator, Measurement, PERF001Validator,
    create_sample_data
)

# Page configuration
st.set_page_config(
    page_title="PERF-001: Temperature Performance Testing",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .quality-pass {
        color: #28a745;
        font-weight: bold;
    }
    .quality-fail {
        color: #dc3545;
        font-weight: bold;
    }
    .warning {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'measurements' not in st.session_state:
        st.session_state.measurements = []
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {}
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False


def render_header():
    """Render application header"""
    st.markdown('<h1 class="main-header">PERF-001: Performance Testing at Different Temperatures</h1>',
                unsafe_allow_html=True)
    st.markdown("**IEC 61853 Compliant Temperature Coefficient Testing**")
    st.markdown("---")


def render_protocol_info():
    """Render protocol information section"""
    with st.expander("📋 Protocol Information", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text_input("Protocol ID", value="PERF-001", disabled=True)
        with col2:
            st.text_input("Standard", value="IEC 61853", disabled=True)
        with col3:
            st.text_input("Category", value="PERFORMANCE", disabled=True)
        with col4:
            st.text_input("Version", value="1.0.0", disabled=True)


def render_test_specimen_form():
    """Render test specimen information form"""
    st.subheader("🔬 Test Specimen Information")

    col1, col2 = st.columns(2)

    with col1:
        module_id = st.text_input(
            "Module ID *",
            help="Unique module identifier or serial number"
        )
        manufacturer = st.text_input(
            "Manufacturer *",
            help="Module manufacturer name"
        )
        model = st.text_input(
            "Model *",
            help="Module model number"
        )
        technology = st.selectbox(
            "Technology *",
            options=["mono-Si", "poly-Si", "CdTe", "CIGS", "a-Si", "HIT", "PERC", "TOPCon", "IBC", "other"],
            help="PV technology type"
        )

    with col2:
        rated_power = st.number_input(
            "Rated Power (STC) [W]",
            min_value=0.0,
            value=320.0,
            step=10.0,
            help="Nameplate power rating at Standard Test Conditions"
        )
        cell_count = st.number_input(
            "Cell Count",
            min_value=1,
            value=60,
            step=1,
            help="Number of cells in the module"
        )
        module_area = st.number_input(
            "Module Area [m²]",
            min_value=0.0,
            value=1.96,
            step=0.01,
            format="%.3f",
            help="Total module area"
        )
        specimen_notes = st.text_area(
            "Notes",
            help="Additional notes about the test specimen"
        )

    return {
        'module_id': module_id,
        'manufacturer': manufacturer,
        'model': model,
        'technology': technology,
        'rated_power_stc': rated_power,
        'cell_count': cell_count,
        'area': module_area,
        'notes': specimen_notes
    }


def render_test_conditions_form():
    """Render test conditions form"""
    st.subheader("⚙️ Test Conditions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.number_input(
            "Irradiance [W/m²]",
            value=1000.0,
            disabled=True,
            help="Fixed at 1000 W/m² for PERF-001"
        )

    with col2:
        spectrum = st.selectbox(
            "Spectrum",
            options=["AM1.5G", "AM1.5D", "AM0"],
            index=0,
            help="Solar spectrum reference"
        )

    with col3:
        reference_temp = st.number_input(
            "Reference Temperature [°C]",
            value=25.0,
            min_value=-40.0,
            max_value=100.0,
            step=1.0,
            help="Reference temperature for normalization"
        )

    # Temperature points
    st.markdown("**Temperature Test Points** (IEC 61853 requires minimum 4 points)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        temp1 = st.number_input("T1 [°C]", value=15.0, step=1.0)
    with col2:
        temp2 = st.number_input("T2 [°C]", value=25.0, step=1.0)
    with col3:
        temp3 = st.number_input("T3 [°C]", value=50.0, step=1.0)
    with col4:
        temp4 = st.number_input("T4 [°C]", value=75.0, step=1.0)

    temperature_points = [temp1, temp2, temp3, temp4]

    return {
        'temperature_points': temperature_points,
        'irradiance': 1000.0,
        'spectrum': spectrum,
        'reference_temperature': reference_temp
    }


def render_measurements_form(temperature_points, module_area):
    """Render measurements data entry form"""
    st.subheader("📊 Measurement Data Entry")

    measurements = []

    # Create tabs for each temperature point
    tabs = st.tabs([f"T = {t}°C" for t in temperature_points])

    for idx, (tab, temp) in enumerate(zip(tabs, temperature_points)):
        with tab:
            st.markdown(f"### Measurements at **{temp}°C**")

            col1, col2, col3 = st.columns(3)

            with col1:
                pmax = st.number_input(
                    f"Pmax [W]",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"pmax_{idx}",
                    help="Maximum power"
                )
                voc = st.number_input(
                    f"Voc [V]",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key=f"voc_{idx}",
                    help="Open circuit voltage"
                )

            with col2:
                isc = st.number_input(
                    f"Isc [A]",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    key=f"isc_{idx}",
                    help="Short circuit current"
                )
                vmp = st.number_input(
                    f"Vmp [V]",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key=f"vmp_{idx}",
                    help="Voltage at maximum power point"
                )

            with col3:
                imp = st.number_input(
                    f"Imp [A]",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    key=f"imp_{idx}",
                    help="Current at maximum power point"
                )

                # Calculated fill factor
                if voc > 0 and isc > 0 and pmax > 0:
                    ff = pmax / (voc * isc)
                    st.metric("Fill Factor", f"{ff:.3f}")

                # Calculated efficiency
                if module_area > 0 and pmax > 0:
                    efficiency = (pmax / (1000 * module_area)) * 100
                    st.metric("Efficiency", f"{efficiency:.2f}%")

            # Create measurement object if data is valid
            if pmax > 0 and voc > 0 and isc > 0:
                measurement = Measurement(
                    temperature=temp,
                    pmax=pmax,
                    voc=voc,
                    isc=isc,
                    vmp=vmp,
                    imp=imp
                )
                measurement.calculate_efficiency(module_area, 1000)
                measurements.append(measurement)

    return measurements


def render_metadata_form():
    """Render metadata and traceability form"""
    with st.expander("📝 Test Metadata & Traceability", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Test Information**")
            test_date = st.date_input("Test Date *", value=date.today())
            test_facility = st.text_input("Test Facility *", value="")
            operator = st.text_input("Operator *", value="")

            st.markdown("**Equipment**")
            solar_simulator = st.text_input("Solar Simulator")
            iv_tracer = st.text_input("IV Curve Tracer")
            temp_control = st.text_input("Temperature Control System")
            calibration_date = st.date_input("Last Calibration Date")

        with col2:
            st.markdown("**Environmental Conditions**")
            ambient_temp = st.number_input("Ambient Temperature [°C]", value=23.0)
            humidity = st.number_input("Relative Humidity [%]", value=45.0, min_value=0.0, max_value=100.0)
            pressure = st.number_input("Barometric Pressure [kPa]", value=101.3)

            st.markdown("**Project & Traceability**")
            project_id = st.text_input("Project ID")
            client = st.text_input("Client")
            lims_id = st.text_input("LIMS ID")
            parent_test = st.text_input("Parent Test ID (e.g., STC-001)")

    return {
        'test_date': test_date.isoformat(),
        'test_facility': test_facility,
        'operator': operator,
        'equipment': {
            'solar_simulator': solar_simulator,
            'iv_tracer': iv_tracer,
            'temperature_control': temp_control,
            'calibration_date': calibration_date.isoformat()
        },
        'environmental_conditions': {
            'ambient_temperature': ambient_temp,
            'relative_humidity': humidity,
            'barometric_pressure': pressure
        },
        'project_info': {
            'project_id': project_id,
            'client': client
        },
        'traceability': {
            'lims_id': lims_id,
            'parent_test_id': parent_test
        }
    }


def plot_temperature_power_curve(measurements):
    """Create interactive temperature vs power plot"""
    if not measurements:
        return None

    temps = [m.temperature for m in measurements]
    pmax = [m.pmax for m in measurements]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Scatter plot of actual measurements
    fig.add_trace(
        go.Scatter(
            x=temps,
            y=pmax,
            mode='markers+lines',
            name='Measured Pmax',
            marker=dict(size=12, color='#1f77b4', symbol='circle'),
            line=dict(width=2, dash='dot')
        ),
        secondary_y=False
    )

    # Add linear regression fit
    if len(temps) >= 2:
        z = np.polyfit(temps, pmax, 1)
        p = np.poly1d(z)
        temp_fit = np.linspace(min(temps), max(temps), 100)
        pmax_fit = p(temp_fit)

        fig.add_trace(
            go.Scatter(
                x=temp_fit,
                y=pmax_fit,
                mode='lines',
                name='Linear Fit',
                line=dict(width=2, color='#ff7f0e', dash='solid'),
                opacity=0.7
            ),
            secondary_y=False
        )

    fig.update_xaxes(title_text="Temperature [°C]", showgrid=True)
    fig.update_yaxes(title_text="Maximum Power [W]", secondary_y=False, showgrid=True)

    fig.update_layout(
        title="Temperature vs. Maximum Power",
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def plot_all_parameters(measurements):
    """Create comprehensive multi-parameter plot"""
    if not measurements:
        return None

    temps = [m.temperature for m in measurements]
    pmax = [m.pmax for m in measurements]
    voc = [m.voc for m in measurements]
    isc = [m.isc for m in measurements]
    ff = [m.fill_factor for m in measurements]

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Maximum Power', 'Open Circuit Voltage',
                        'Short Circuit Current', 'Fill Factor'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Pmax
    fig.add_trace(
        go.Scatter(x=temps, y=pmax, mode='markers+lines', name='Pmax',
                   marker=dict(size=10, color='#1f77b4'), showlegend=False),
        row=1, col=1
    )

    # Voc
    fig.add_trace(
        go.Scatter(x=temps, y=voc, mode='markers+lines', name='Voc',
                   marker=dict(size=10, color='#ff7f0e'), showlegend=False),
        row=1, col=2
    )

    # Isc
    fig.add_trace(
        go.Scatter(x=temps, y=isc, mode='markers+lines', name='Isc',
                   marker=dict(size=10, color='#2ca02c'), showlegend=False),
        row=2, col=1
    )

    # Fill Factor
    fig.add_trace(
        go.Scatter(x=temps, y=ff, mode='markers+lines', name='FF',
                   marker=dict(size=10, color='#d62728'), showlegend=False),
        row=2, col=2
    )

    # Update axes
    fig.update_xaxes(title_text="Temperature [°C]", row=1, col=1)
    fig.update_xaxes(title_text="Temperature [°C]", row=1, col=2)
    fig.update_xaxes(title_text="Temperature [°C]", row=2, col=1)
    fig.update_xaxes(title_text="Temperature [°C]", row=2, col=2)

    fig.update_yaxes(title_text="Power [W]", row=1, col=1)
    fig.update_yaxes(title_text="Voltage [V]", row=1, col=2)
    fig.update_yaxes(title_text="Current [A]", row=2, col=1)
    fig.update_yaxes(title_text="Fill Factor", row=2, col=2)

    fig.update_layout(
        title_text="Temperature Dependencies of PV Parameters",
        height=700,
        template='plotly_white'
    )

    return fig


def render_results(calculator, measurements):
    """Render calculation results and visualizations"""
    st.header("📈 Results & Analysis")

    # Calculate results
    try:
        results = calculator.calculate_all_coefficients()
        quality = calculator.validate_data_quality()

        # Display temperature coefficients
        st.subheader("Temperature Coefficients")

        col1, col2, col3 = st.columns(3)

        with col1:
            coef_pmax = results['temp_coefficient_pmax']
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Pmax Temperature Coefficient",
                f"{coef_pmax['value']:.4f} {coef_pmax['unit']}",
                delta=f"R² = {coef_pmax['r_squared']:.4f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            coef_voc = results['temp_coefficient_voc']
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Voc Temperature Coefficient",
                f"{coef_voc['value']:.4f} {coef_voc['unit']}",
                delta=f"R² = {coef_voc['r_squared']:.4f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            coef_isc = results['temp_coefficient_isc']
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Isc Temperature Coefficient",
                f"{coef_isc['value']:.4f} {coef_isc['unit']}",
                delta=f"R² = {coef_isc['r_squared']:.4f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Visualizations
        st.subheader("Interactive Visualizations")

        tab1, tab2, tab3 = st.tabs(["Temperature-Power Curve", "All Parameters", "Data Table"])

        with tab1:
            fig1 = plot_temperature_power_curve(measurements)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            fig2 = plot_all_parameters(measurements)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            df = pd.DataFrame([m.to_dict() for m in measurements])
            st.dataframe(df, use_container_width=True)

        # Quality checks
        st.subheader("Quality Assurance")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_class = "quality-pass" if quality['data_completeness'] else "quality-fail"
            st.markdown(f'<p class="{status_class}">{"✓" if quality["data_completeness"] else "✗"} Data Completeness</p>',
                        unsafe_allow_html=True)
        with col2:
            status_class = "quality-pass" if quality['linearity_check'] else "quality-fail"
            st.markdown(f'<p class="{status_class}">{"✓" if quality["linearity_check"] else "✗"} Linearity Check</p>',
                        unsafe_allow_html=True)
        with col3:
            status_class = "quality-pass" if quality['range_validation'] else "quality-fail"
            st.markdown(f'<p class="{status_class}">{"✓" if quality["range_validation"] else "✗"} Range Validation</p>',
                        unsafe_allow_html=True)
        with col4:
            status_class = "quality-pass" if quality['measurement_stability'] else "quality-fail"
            st.markdown(f'<p class="{status_class}">{"✓" if quality["measurement_stability"] else "✗"} Measurement Stability</p>',
                        unsafe_allow_html=True)

        # Warnings and errors
        if quality['warnings']:
            st.warning("⚠️ **Warnings:**")
            for warning in quality['warnings']:
                st.markdown(f"- {warning}")

        if quality['errors']:
            st.error("❌ **Errors:**")
            for error in quality['errors']:
                st.markdown(f"- {error}")

        return results, quality

    except Exception as e:
        st.error(f"Error calculating results: {str(e)}")
        return None, None


def main():
    """Main application"""
    initialize_session_state()
    render_header()
    render_protocol_info()

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Select Mode",
            ["New Test", "Load Sample Data", "View Documentation"]
        )

        st.markdown("---")
        st.markdown("### Quick Actions")

        if st.button("🔄 Reset Form"):
            st.session_state.clear()
            st.rerun()

    # Main content
    if mode == "Load Sample Data":
        st.info("Loading sample data for demonstration...")
        sample_data = create_sample_data()

        # Display sample data
        st.json(sample_data, expanded=False)

        # Create calculator from sample data
        calc = PERF001Calculator()
        measurements = [
            Measurement(**m) for m in sample_data['measurements']
        ]
        calc.add_measurements(measurements)

        # Show results
        render_results(calc, measurements)

    elif mode == "View Documentation":
        st.markdown("""
        ## PERF-001 Protocol Documentation

        ### Overview
        Performance testing at different temperatures according to IEC 61853 standard.

        ### Test Procedure
        1. **Setup**: Configure solar simulator at 1000 W/m² irradiance
        2. **Temperature Control**: Set module to test temperature and stabilize
        3. **Measurement**: Record IV curve and extract key parameters
        4. **Repeat**: Test at minimum 4 temperature points (15, 25, 50, 75°C)
        5. **Analysis**: Calculate temperature coefficients via linear regression

        ### Required Measurements
        - **Pmax**: Maximum power point
        - **Voc**: Open circuit voltage
        - **Isc**: Short circuit current
        - **Vmp**: Voltage at MPP
        - **Imp**: Current at MPP

        ### Quality Criteria
        - Minimum 4 temperature points
        - R² > 0.95 for linear fit
        - Fill factor within 0.50 - 0.90
        - Temperature range > 30°C recommended

        ### References
        - IEC 61853-1: PV module performance testing and energy rating
        - IEC 60904-1: Measurement of current-voltage characteristics
        """)

    else:  # New Test mode
        # Test specimen
        specimen_data = render_test_specimen_form()

        st.markdown("---")

        # Test conditions
        conditions_data = render_test_conditions_form()

        st.markdown("---")

        # Measurements
        measurements = render_measurements_form(
            conditions_data['temperature_points'],
            specimen_data['area']
        )

        st.markdown("---")

        # Metadata
        metadata = render_metadata_form()

        st.markdown("---")

        # Calculate button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            calculate_btn = st.button("🔬 Calculate Results", type="primary", use_container_width=True)

        if calculate_btn:
            if len(measurements) < 4:
                st.error("⚠️ IEC 61853 requires minimum 4 temperature measurements!")
            else:
                # Create calculator
                calc = PERF001Calculator(reference_temperature=conditions_data['reference_temperature'])
                calc.add_measurements(measurements)

                # Show results
                results, quality = render_results(calc, measurements)

                # Export functionality
                if results:
                    st.markdown("---")
                    st.subheader("📥 Export Data")

                    # Build complete test data
                    complete_data = {
                        'protocol_info': {
                            'protocol_id': 'PERF-001',
                            'protocol_name': 'Performance at Different Temperatures',
                            'standard': 'IEC 61853',
                            'version': '1.0.0',
                            'category': 'PERFORMANCE'
                        },
                        'test_specimen': specimen_data,
                        'test_conditions': conditions_data,
                        'measurements': [m.to_dict() for m in measurements],
                        'calculated_results': results,
                        'quality_checks': quality,
                        'metadata': metadata
                    }

                    col1, col2 = st.columns(2)
                    with col1:
                        json_str = json.dumps(complete_data, indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name=f"perf-001-{specimen_data['module_id']}-{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json"
                        )

                    with col2:
                        st.button("Generate PDF Report", disabled=True,
                                  help="PDF generation coming soon")


if __name__ == "__main__":
    main()
