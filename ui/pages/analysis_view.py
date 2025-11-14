"""Data Analysis View Component"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_analysis_view():
    """Render data analysis view"""

    st.markdown("### Data Analysis Dashboard")

    # Check if we have results in session state
    if 'test_protocol' not in st.session_state or st.session_state['test_protocol'] is None:
        st.info("No test data available. Please execute a test first.")
        return

    protocol = st.session_state['test_protocol']

    if not protocol.calculated_results:
        st.warning("No calculated results available. Please complete the test execution.")
        return

    # Summary metrics
    st.markdown("#### Summary Metrics")

    calc_results = protocol.calculated_results

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Average Chalking",
            f"{calc_results['average_chalking_rating']:.2f}",
            delta=None
        )

    with col2:
        st.metric(
            "Uniformity Index",
            f"{calc_results.get('chalking_uniformity_index', 0):.1f}%"
        )

    with col3:
        st.metric(
            "Coefficient of Variation",
            f"{calc_results.get('coefficient_of_variation', 0):.1f}%"
        )

    # Charts
    st.markdown("#### Visualizations")

    # Prepare data
    if protocol.measurements:
        df = pd.DataFrame(protocol.measurements)

        # Histogram
        st.markdown("**Chalking Rating Distribution**")
        fig_hist = px.histogram(
            df,
            x="chalking_rating",
            nbins=20,
            title="Distribution of Chalking Ratings",
            labels={"chalking_rating": "Chalking Rating", "count": "Frequency"}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # Box plot
        st.markdown("**Box Plot**")
        fig_box = px.box(
            df,
            y="chalking_rating",
            title="Chalking Rating Statistics",
            labels={"chalking_rating": "Chalking Rating"}
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Spatial heatmap (if coordinates available)
        if 'location_x' in df.columns and 'location_y' in df.columns:
            st.markdown("**Spatial Distribution Heatmap**")

            # Filter out zero coordinates
            df_spatial = df[(df['location_x'] > 0) | (df['location_y'] > 0)]

            if not df_spatial.empty:
                fig_scatter = px.scatter(
                    df_spatial,
                    x="location_x",
                    y="location_y",
                    size="chalking_rating",
                    color="chalking_rating",
                    title="Spatial Chalking Distribution",
                    labels={
                        "location_x": "X Position (mm)",
                        "location_y": "Y Position (mm)",
                        "chalking_rating": "Chalking Rating"
                    },
                    color_continuous_scale="Reds"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

        # Data table
        st.markdown("**Detailed Measurements**")
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    render_analysis_view()
