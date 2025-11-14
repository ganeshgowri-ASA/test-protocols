"""QC dashboard component."""

import streamlit as st


def render_qc_dashboard():
    """Render quality control dashboard."""
    st.title("Quality Control Dashboard")

    protocol_id = st.session_state.current_protocol
    test_data = st.session_state.test_data
    validator = st.session_state.schema_validator
    data_processor = st.session_state.data_processor

    # Run QC validation
    validation_result = validator.validate_data(protocol_id, test_data)
    qc_result = validator.validate_qc_criteria(protocol_id, test_data)

    # Overall status
    st.subheader("Overall QC Status")

    if validation_result.get('valid') and qc_result.get('passed'):
        st.success("✓ All QC checks passed")
    elif validation_result.get('valid') and qc_result.get('overall_status') == 'WARNING':
        st.warning("⚠ QC checks passed with warnings")
    else:
        st.error("✗ QC checks failed")

    # Validation errors
    if validation_result.get('errors'):
        st.subheader("Validation Errors")
        for error in validation_result['errors']:
            st.error(f"• {error}")

    # Validation warnings
    if validation_result.get('warnings'):
        st.subheader("Validation Warnings")
        for warning in validation_result['warnings']:
            st.warning(f"• {warning}")

    # QC Criteria Results
    st.subheader("QC Criteria Evaluation")

    criteria_results = qc_result.get('criteria_results', [])

    if criteria_results:
        for criterion in criteria_results:
            status = criterion.get('status', 'UNKNOWN')
            name = criterion.get('name', 'Unknown')
            description = criterion.get('description', '')

            if status == 'PASS':
                st.success(f"✓ {name}: {description}")
            elif status == 'WARNING':
                st.warning(f"⚠ {name}: {description}")
            else:
                st.error(f"✗ {name}: {description}")

            message = criterion.get('message', '')
            if message:
                st.markdown(f"  *{message}*")
    else:
        st.info("No specific QC criteria results available.")

    # Data quality indicators
    st.subheader("Data Quality Indicators")

    df = data_processor.process_raw_data(protocol_id, test_data)

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Efficiency Outliers**")
            efficiency_outliers = data_processor.identify_outliers(df, 'efficiency', method='iqr')

            if efficiency_outliers:
                st.warning(f"Found {len(efficiency_outliers)} outlier(s) in efficiency data")
                st.markdown(f"Row indices: {efficiency_outliers}")
            else:
                st.success("No outliers detected in efficiency data")

        with col2:
            st.markdown("**Fill Factor Outliers**")
            ff_outliers = data_processor.identify_outliers(df, 'fill_factor', method='iqr')

            if ff_outliers:
                st.warning(f"Found {len(ff_outliers)} outlier(s) in fill factor data")
                st.markdown(f"Row indices: {ff_outliers}")
            else:
                st.success("No outliers detected in fill factor data")

    # Equipment calibration status
    st.subheader("Equipment Calibration Status")

    equipment_data = test_data.get('equipment', {})
    if equipment_data:
        from src.core.protocol_manager import ProtocolManager
        pm = ProtocolManager()
        cal_result = pm.validate_equipment_calibration(protocol_id, equipment_data)

        if cal_result.get('valid'):
            st.success("✓ Equipment calibration is current")
        else:
            st.error("✗ Equipment calibration issues detected")

        for error in cal_result.get('errors', []):
            st.error(f"• {error}")

        for warning in cal_result.get('warnings', []):
            st.warning(f"• {warning}")
    else:
        st.info("No equipment data available for calibration check.")

    # Recommendations
    st.subheader("Recommendations")

    recommendations = []

    if validation_result.get('warnings'):
        recommendations.append("Review and address validation warnings before finalizing report")

    if not validation_result.get('valid'):
        recommendations.append("Fix validation errors before proceeding")

    if efficiency_outliers if 'efficiency_outliers' in locals() else []:
        recommendations.append("Investigate outlier measurements for potential equipment or procedure issues")

    if recommendations:
        for rec in recommendations:
            st.info(f"• {rec}")
    else:
        st.success("No specific recommendations at this time.")
