"""Test results display component."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_test_results():
    """Render test results visualization."""
    st.title("Test Results")

    protocol_id = st.session_state.current_protocol
    test_data = st.session_state.test_data
    data_processor = st.session_state.data_processor

    # Process data
    df = data_processor.process_raw_data(protocol_id, test_data)

    if df.empty:
        st.warning("No measurement data available.")
        return

    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Measurements",
            len(df)
        )

    with col2:
        if 'efficiency' in df.columns:
            st.metric(
                "Avg Efficiency",
                f"{df['efficiency'].mean():.2f}%",
                f"{df['efficiency'].std():.2f}% std"
            )

    with col3:
        if 'fill_factor' in df.columns:
            st.metric(
                "Avg Fill Factor",
                f"{df['fill_factor'].mean():.3f}",
                f"{df['fill_factor'].std():.3f} std"
            )

    with col4:
        if 'concentration_suns' in df.columns:
            st.metric(
                "Concentration Range",
                f"{df['concentration_suns'].min():.1f} - {df['concentration_suns'].max():.1f} suns"
            )

    # Data table
    st.subheader("Measurement Data")

    display_columns = [
        col for col in [
            'concentration_suns', 'temperature_c', 'voc', 'isc',
            'vmp', 'imp', 'fill_factor', 'efficiency'
        ] if col in df.columns
    ]

    st.dataframe(
        df[display_columns].style.format({
            'concentration_suns': '{:.1f}',
            'temperature_c': '{:.1f}',
            'voc': '{:.3f}',
            'isc': '{:.3f}',
            'vmp': '{:.3f}',
            'imp': '{:.3f}',
            'fill_factor': '{:.3f}',
            'efficiency': '{:.2f}'
        }),
        use_container_width=True
    )

    # Charts
    st.subheader("Performance Plots")

    if 'concentration_suns' in df.columns and 'efficiency' in df.columns:
        # Efficiency vs Concentration
        fig1 = px.line(
            df,
            x='concentration_suns',
            y='efficiency',
            title='Efficiency vs Concentration',
            markers=True
        )
        fig1.update_layout(
            xaxis_title='Concentration (suns)',
            yaxis_title='Efficiency (%)',
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)

    if 'concentration_suns' in df.columns and 'fill_factor' in df.columns:
        # Fill Factor vs Concentration
        fig2 = px.line(
            df,
            x='concentration_suns',
            y='fill_factor',
            title='Fill Factor vs Concentration',
            markers=True
        )
        fig2.update_layout(
            xaxis_title='Concentration (suns)',
            yaxis_title='Fill Factor',
            hovermode='x unified'
        )
        st.plotly_chart(fig2, use_container_width=True)

    if 'concentration_suns' in df.columns and 'power_w' in df.columns:
        # Power Output vs Concentration
        fig3 = px.scatter(
            df,
            x='concentration_suns',
            y='power_w',
            title='Power Output vs Concentration',
            trendline='ols'
        )
        fig3.update_layout(
            xaxis_title='Concentration (suns)',
            yaxis_title='Power Output (W)',
            hovermode='closest'
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Statistical Analysis
    st.subheader("Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Temperature coefficient
        temp_coeff_eff = data_processor.calculate_temperature_coefficient(df, 'efficiency')
        temp_coeff_voc = data_processor.calculate_temperature_coefficient(df, 'voc')

        st.markdown("**Temperature Coefficients**")
        if temp_coeff_eff is not None:
            st.markdown(f"- Efficiency: {temp_coeff_eff:.4f} %/°C")
        if temp_coeff_voc is not None:
            st.markdown(f"- Voc: {temp_coeff_voc:.4f} %/°C")

    with col2:
        # Concentration coefficient
        conc_coeff_eff = data_processor.calculate_concentration_coefficient(df, 'efficiency')

        st.markdown("**Concentration Coefficient**")
        if conc_coeff_eff is not None:
            st.markdown(f"- Efficiency: {conc_coeff_eff:.4f} %/sun")

    # Export options
    st.subheader("Export Data")

    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{test_data.get('test_run_id', 'test')}_data.csv",
            mime="text/csv"
        )

    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{test_data.get('test_run_id', 'test')}_data.json",
            mime="application/json"
        )
