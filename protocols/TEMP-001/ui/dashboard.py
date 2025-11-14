"""
Main Dashboard for TEMP-001 Temperature Coefficient Testing

Streamlit application for managing and analyzing temperature coefficient tests.

Author: ASA PV Testing
Date: 2025-11-14
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.analyzer import TemperatureCoefficientAnalyzer
from python.validator import TEMP001Validator, ValidationReport
from python.report_generator import TEMP001ReportGenerator


# Page configuration
st.set_page_config(
    page_title="TEMP-001 Temperature Coefficient Testing",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1976D2;
    }
    .status-pass {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-warning {
        color: #FF9800;
        font-weight: bold;
    }
    .status-fail {
        color: #F44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application"""

    # Header
    st.markdown('<div class="main-header">🌡️ TEMP-001: Temperature Coefficient Testing</div>',
                unsafe_allow_html=True)
    st.markdown("**IEC 60891:2021 - Photovoltaic Device Temperature Coefficient Analysis**")

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1976D2/FFFFFF?text=ASA+PV+Testing",
                use_column_width=True)
        st.markdown("---")

        st.subheader("Navigation")
        page = st.radio(
            "Select Page:",
            ["🏠 Home", "📊 New Test", "📈 Analysis", "📁 Test History", "⚙️ Settings"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.subheader("Protocol Information")
        st.info("""
        **Protocol:** TEMP-001
        **Version:** 1.0.0
        **Standard:** IEC 60891:2021
        **Category:** Performance Testing
        """)

    # Route to selected page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 New Test":
        show_new_test_page()
    elif page == "📈 Analysis":
        show_analysis_page()
    elif page == "📁 Test History":
        show_history_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display home page with overview"""

    st.markdown('<div class="sub-header">Welcome to TEMP-001 Dashboard</div>',
                unsafe_allow_html=True)

    # Quick stats (placeholder data)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tests", "0", "+0")

    with col2:
        st.metric("Tests This Month", "0", "0%")

    with col3:
        st.metric("Avg. Test Time", "N/A", "")

    with col4:
        st.metric("Success Rate", "N/A", "")

    st.markdown("---")

    # Protocol Overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Protocol Objectives")
        st.markdown("""
        - Measure temperature coefficient of maximum power (α_Pmp or γ)
        - Measure temperature coefficient of open circuit voltage (β_Voc)
        - Measure temperature coefficient of short circuit current (α_Isc)
        - Determine temperature-corrected performance at STC
        - Validate module performance under varying temperatures
        """)

        st.markdown("### 🔬 Equipment Required")
        st.markdown("""
        1. **Solar Simulator** - Class AAA, 1000 W/m²
        2. **Temperature Chamber** - Range: -20°C to +80°C
        3. **I-V Curve Tracer** - High accuracy
        4. **Temperature Sensors** - PT100/Thermocouple
        5. **Reference Cell** - Calibrated pyranometer
        """)

    with col2:
        st.markdown("### 📊 Test Requirements (IEC 60891)")
        st.markdown("""
        - **Minimum temperature range:** 30°C
        - **Minimum measurement points:** 5
        - **Irradiance stability:** ±2%
        - **Temperature stability:** ±1°C for 30 min
        - **Regression quality:** R² ≥ 0.95
        """)

        st.markdown("### 📈 Typical Coefficient Ranges")
        st.markdown("""
        For crystalline silicon modules:
        - **α_Pmp:** -0.65 to -0.25 %/°C
        - **β_Voc:** -0.50 to -0.20 %/°C
        - **α_Isc:** 0.00 to 0.10 %/°C
        """)

    st.markdown("---")

    # Quick Start Guide
    st.markdown("### 🚀 Quick Start")
    st.info("""
    **To start a new test:**
    1. Navigate to "📊 New Test" in the sidebar
    2. Enter test information and module details
    3. Record measurements at different temperatures
    4. Run analysis to calculate temperature coefficients
    5. Generate and download test report
    """)


def show_new_test_page():
    """Display new test creation page"""
    st.markdown('<div class="sub-header">Create New Test</div>', unsafe_allow_html=True)

    # Test Information Form
    with st.form("test_info_form"):
        st.markdown("#### Test Information")

        col1, col2 = st.columns(2)

        with col1:
            test_number = st.text_input(
                "Test Number",
                value=f"TEMP-001-{datetime.now().strftime('%Y-%m-%d')}",
                help="Unique identifier for this test"
            )
            operator = st.text_input("Operator Name", help="Person conducting the test")
            laboratory = st.text_input(
                "Laboratory",
                value="ASA PV Testing Lab",
                help="Testing facility name"
            )

        with col2:
            test_date = st.date_input("Test Date", value=datetime.now())
            module_id = st.text_input("Module ID", help="Unique module identifier")
            module_manufacturer = st.text_input("Manufacturer", help="Module manufacturer")

        module_model = st.text_input("Module Model", help="Module model number")
        module_serial = st.text_input("Serial Number", help="Module serial number")
        notes = st.text_area("Notes", help="Additional test notes")

        submitted = st.form_submit_button("Save Test Information")

        if submitted:
            test_info = {
                'test_number': test_number,
                'operator': operator,
                'laboratory': laboratory,
                'test_date': test_date.isoformat(),
                'module_id': module_id,
                'module_manufacturer': module_manufacturer,
                'module_model': module_model,
                'module_serial_number': module_serial,
                'notes': notes
            }
            st.session_state['test_info'] = test_info
            st.success("✅ Test information saved!")

    st.markdown("---")

    # Data Entry
    st.markdown("#### Measurement Data Entry")

    # Sample template for data entry
    if st.button("📥 Load Sample Data"):
        sample_data = pd.DataFrame({
            'module_temperature': [20, 30, 40, 50, 60, 70],
            'ambient_temperature': [18.5, 28.2, 38.1, 47.9, 57.8, 67.5],
            'irradiance': [1000, 1005, 998, 1002, 997, 1001],
            'voc': [38.50, 37.80, 37.10, 36.40, 35.70, 35.00],
            'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
            'vmp': [31.50, 30.85, 30.20, 29.55, 28.90, 28.25],
            'imp': [8.25, 8.17, 8.09, 8.01, 7.93, 7.85],
            'pmax': [259.88, 252.05, 244.32, 236.70, 229.18, 221.76]
        })
        st.session_state['measurement_data'] = sample_data
        st.success("✅ Sample data loaded!")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Measurement Data (CSV or Excel)",
        type=['csv', 'xlsx'],
        help="Upload a file with measurement data"
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state['measurement_data'] = df
        st.success(f"✅ Loaded {len(df)} measurements from file!")

    # Display and edit data
    if 'measurement_data' in st.session_state:
        st.markdown("##### Current Measurements")
        edited_df = st.data_editor(
            st.session_state['measurement_data'],
            num_rows="dynamic",
            use_container_width=True
        )
        st.session_state['measurement_data'] = edited_df

        # Quick statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Measurements", len(edited_df))
        with col2:
            temp_range = edited_df['module_temperature'].max() - edited_df['module_temperature'].min()
            st.metric("Temp Range (°C)", f"{temp_range:.1f}")
        with col3:
            avg_irrad = edited_df['irradiance'].mean()
            st.metric("Avg Irradiance", f"{avg_irrad:.1f} W/m²")
        with col4:
            irrad_std = edited_df['irradiance'].std()
            variation = (irrad_std / avg_irrad) * 100
            st.metric("Irrad Variation", f"{variation:.2f}%")


def show_analysis_page():
    """Display analysis page"""
    st.markdown('<div class="sub-header">Temperature Coefficient Analysis</div>',
                unsafe_allow_html=True)

    if 'measurement_data' not in st.session_state or st.session_state['measurement_data'] is None:
        st.warning("⚠️ No measurement data available. Please create a new test first.")
        return

    data = st.session_state['measurement_data']

    # Run Analysis Button
    if st.button("🔬 Run Analysis", type="primary"):
        with st.spinner("Analyzing data..."):
            try:
                # Initialize analyzer
                analyzer = TemperatureCoefficientAnalyzer()

                # Load data
                analyzer.load_data(data)

                # Calculate coefficients
                results = analyzer.calculate_temperature_coefficients()

                # Store results
                st.session_state['analysis_results'] = results

                # Validate data
                validator = TEMP001Validator()
                validation_report = validator.validate_dataset(data)

                # Validate coefficients
                coeff_validation = validator.validate_coefficients(
                    results.alpha_pmp_relative,
                    results.beta_voc_relative,
                    results.alpha_isc_relative,
                    results.r_squared_pmp,
                    results.r_squared_voc,
                    results.r_squared_isc
                )

                for result in coeff_validation:
                    validation_report.add_result(result)

                validation_report.update_overall_status()

                st.session_state['validation_report'] = validation_report

                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return

    # Display results if available
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']

        # Results Summary
        st.markdown("### 📊 Temperature Coefficients")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Power (α_Pmp)")
            st.metric(
                "Relative",
                f"{results.alpha_pmp_relative:.4f} %/°C",
                help="Temperature coefficient of maximum power"
            )
            st.metric(
                "Absolute",
                f"{results.alpha_pmp_absolute:.4f} W/°C"
            )
            st.metric("R²", f"{results.r_squared_pmp:.4f}")

        with col2:
            st.markdown("#### Voltage (β_Voc)")
            st.metric(
                "Relative",
                f"{results.beta_voc_relative:.4f} %/°C",
                help="Temperature coefficient of open circuit voltage"
            )
            st.metric(
                "Absolute",
                f"{results.beta_voc_absolute:.5f} V/°C"
            )
            st.metric("R²", f"{results.r_squared_voc:.4f}")

        with col3:
            st.markdown("#### Current (α_Isc)")
            st.metric(
                "Relative",
                f"{results.alpha_isc_relative:.4f} %/°C",
                help="Temperature coefficient of short circuit current"
            )
            st.metric(
                "Absolute",
                f"{results.alpha_isc_absolute:.5f} A/°C"
            )
            st.metric("R²", f"{results.r_squared_isc:.4f}")

        st.markdown("---")

        # STC Performance
        st.markdown("### 🎯 Performance at STC (25°C, 1000 W/m²)")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Maximum Power", f"{results.pmp_at_stc:.2f} W")
        with col2:
            st.metric("Voc at STC", f"{results.voc_at_stc:.3f} V")
        with col3:
            st.metric("Isc at STC", f"{results.isc_at_stc:.3f} A")

        st.markdown("---")

        # Regression Plots
        st.markdown("### 📈 Regression Analysis")

        # Create plots
        fig = create_regression_plots(data, results)
        st.plotly_chart(fig, use_container_width=True)

        # Validation Results
        if 'validation_report' in st.session_state:
            st.markdown("---")
            st.markdown("### ✅ Validation Report")

            report = st.session_state['validation_report']

            status_color = {
                'pass': 'green',
                'warning': 'orange',
                'fail': 'red'
            }.get(report.overall_status, 'gray')

            st.markdown(
                f'<p style="font-size: 1.5rem; color: {status_color}; font-weight: bold;">'
                f'Overall Status: {report.overall_status.upper()}</p>',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Checks", len(report.results))
            with col2:
                st.metric("Passed", report.num_passed)
            with col3:
                st.metric("Warnings", report.num_warnings)
            with col4:
                st.metric("Failures", report.num_critical_failures)

            # Detailed results
            with st.expander("View Detailed Validation Results"):
                for result in report.results:
                    status_emoji = {'pass': '✅', 'warning': '⚠️', 'fail': '❌'}.get(result.status, 'ℹ️')
                    st.markdown(f"{status_emoji} **{result.check_name}**: {result.message}")


def create_regression_plots(data, results):
    """Create interactive regression plots"""
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Power vs Temperature',
            'Voltage vs Temperature',
            'Current vs Temperature',
            'Normalized Power'
        )
    )

    temp = data['module_temperature'].values

    # Use normalized values if available
    pmax = data['pmax_normalized'].values if 'pmax_normalized' in data.columns else data['pmax'].values
    voc = data['voc_normalized'].values if 'voc_normalized' in data.columns else data['voc'].values
    isc = data['isc_normalized'].values if 'isc_normalized' in data.columns else data['isc'].values

    import numpy as np

    # Power plot
    fig.add_trace(
        go.Scatter(x=temp, y=pmax, mode='markers', name='Measured Pmax',
                  marker=dict(size=10, color='blue')),
        row=1, col=1
    )
    temp_fit = np.linspace(temp.min(), temp.max(), 100)
    pmax_fit = results.pmp_slope * temp_fit + results.pmp_intercept
    fig.add_trace(
        go.Scatter(x=temp_fit, y=pmax_fit, mode='lines', name='Linear Fit',
                  line=dict(color='red', width=2)),
        row=1, col=1
    )

    # Voltage plot
    fig.add_trace(
        go.Scatter(x=temp, y=voc, mode='markers', name='Measured Voc',
                  marker=dict(size=10, color='green')),
        row=1, col=2
    )
    voc_fit = results.voc_slope * temp_fit + results.voc_intercept
    fig.add_trace(
        go.Scatter(x=temp_fit, y=voc_fit, mode='lines', name='Linear Fit',
                  line=dict(color='red', width=2)),
        row=1, col=2
    )

    # Current plot
    fig.add_trace(
        go.Scatter(x=temp, y=isc, mode='markers', name='Measured Isc',
                  marker=dict(size=10, color='orange')),
        row=2, col=1
    )
    isc_fit = results.isc_slope * temp_fit + results.isc_intercept
    fig.add_trace(
        go.Scatter(x=temp_fit, y=isc_fit, mode='lines', name='Linear Fit',
                  line=dict(color='red', width=2)),
        row=2, col=1
    )

    # Normalized power
    pmax_normalized = (pmax / results.pmp_at_stc) * 100
    fig.add_trace(
        go.Scatter(x=temp, y=pmax_normalized, mode='lines+markers',
                  name='Normalized Power',
                  line=dict(color='purple', width=2),
                  marker=dict(size=8)),
        row=2, col=2
    )
    fig.add_hline(y=100, line_dash="dash", line_color="red", row=2, col=2)

    # Update layout
    fig.update_xaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_xaxes(title_text="Temperature (°C)", row=1, col=2)
    fig.update_xaxes(title_text="Temperature (°C)", row=2, col=1)
    fig.update_xaxes(title_text="Temperature (°C)", row=2, col=2)

    fig.update_yaxes(title_text="Power (W)", row=1, col=1)
    fig.update_yaxes(title_text="Voltage (V)", row=1, col=2)
    fig.update_yaxes(title_text="Current (A)", row=2, col=1)
    fig.update_yaxes(title_text="Normalized Power (%)", row=2, col=2)

    fig.update_layout(height=800, showlegend=False)

    return fig


def show_history_page():
    """Display test history"""
    st.markdown('<div class="sub-header">Test History</div>', unsafe_allow_html=True)
    st.info("📂 Test history feature coming soon!")


def show_settings_page():
    """Display settings page"""
    st.markdown('<div class="sub-header">Settings</div>', unsafe_allow_html=True)
    st.info("⚙️ Settings configuration coming soon!")


if __name__ == "__main__":
    main()
