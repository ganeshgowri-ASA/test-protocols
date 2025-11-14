"""Charting components for test results visualization."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Any


def render_resistance_chart(protocol):
    """Render resistance measurements chart for TERM-001."""
    data = protocol.get_resistance_data()

    if not data:
        st.info("No resistance data available yet")
        return

    # Create bar chart
    categories = ["Initial Positive", "Initial Negative", "Post Positive", "Post Negative"]
    values = [
        data.get("initial_positive", 0),
        data.get("initial_negative", 0),
        data.get("post_positive", 0),
        data.get("post_negative", 0),
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=["blue", "blue", "orange", "orange"],
                text=[f"{v:.2f} mΩ" if v else "N/A" for v in values],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Terminal Resistance Measurements",
        xaxis_title="Measurement Point",
        yaxis_title="Resistance (mΩ)",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Resistance change chart if available
    if data.get("change_positive") is not None and data.get("change_negative") is not None:
        fig2 = go.Figure(
            data=[
                go.Bar(
                    x=["Positive Terminal", "Negative Terminal"],
                    y=[data["change_positive"], data["change_negative"]],
                    marker_color=["green" if abs(data["change_positive"]) < 10 else "red",
                                  "green" if abs(data["change_negative"]) < 10 else "red"],
                    text=[f"{data['change_positive']:.2f}%", f"{data['change_negative']:.2f}%"],
                    textposition="auto",
                )
            ]
        )

        fig2.update_layout(
            title="Resistance Change After Stress",
            xaxis_title="Terminal",
            yaxis_title="Change (%)",
            height=400,
        )

        # Add acceptance line at 10%
        fig2.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="Max Acceptable (10%)")
        fig2.add_hline(y=-10, line_dash="dash", line_color="red")

        st.plotly_chart(fig2, use_container_width=True)


def render_mechanical_chart(protocol):
    """Render mechanical test results chart for TERM-001."""
    data = protocol.get_mechanical_data()

    if not data:
        st.info("No mechanical test data available yet")
        return

    # Create gauge chart for pull force
    if data.get("pull_force"):
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=data["pull_force"],
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Pull Force Applied (N)"},
                delta={"reference": 200, "increasing": {"color": "green"}},
                gauge={
                    "axis": {"range": [None, 500]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 200], "color": "lightgray"},
                        {"range": [200, 500], "color": "lightgreen"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 200,
                    },
                },
            )
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Torque and integrity display
    if data.get("torque_applied"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Torque Applied", f"{data['torque_applied']} Nm")
        with col2:
            integrity = data.get("terminal_integrity", "Unknown")
            color = "green" if integrity == "No damage" else "red"
            st.metric("Terminal Integrity", integrity)


def render_dielectric_chart(protocol):
    """Render dielectric test results for TERM-001."""
    data = protocol.get_dielectric_data()

    if not data:
        st.info("No dielectric test data available yet")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Test Voltage", f"{data.get('test_voltage', 0)} V")

    with col2:
        leakage = data.get("leakage_current", 0)
        st.metric("Leakage Current", f"{leakage:.2f} mA", delta=None if leakage < 10 else "High")

    with col3:
        breakdown = data.get("breakdown_occurred", False)
        status = "❌ Breakdown" if breakdown else "✅ Pass"
        st.metric("Breakdown Status", status)
