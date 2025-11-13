"""
Real-time Graphing Components

Provides interactive real-time graphs using Plotly:
- Temperature vs Time
- Power vs Temperature curves
- Efficiency plots
- Environmental condition monitoring
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import streamlit as st
from datetime import datetime


class RealTimeGraphs:
    """Real-time graphing utilities"""

    @staticmethod
    def temperature_vs_time(timestamps: List[datetime],
                           cell_temps: List[float],
                           ambient_temps: List[float],
                           title: str = "Cell Temperature vs Time") -> go.Figure:
        """
        Create temperature vs time line chart

        Args:
            timestamps: List of measurement timestamps
            cell_temps: List of cell temperatures
            ambient_temps: List of ambient temperatures
            title: Graph title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Cell temperature trace
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=cell_temps,
            mode='lines+markers',
            name='Cell Temperature',
            line=dict(color='red', width=2),
            marker=dict(size=4)
        ))

        # Ambient temperature trace
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=ambient_temps,
            mode='lines+markers',
            name='Ambient Temperature',
            line=dict(color='blue', width=2),
            marker=dict(size=4)
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            hovermode='x unified',
            showlegend=True,
            height=400
        )

        return fig

    @staticmethod
    def power_vs_temperature(temperatures: List[float],
                           powers: List[float],
                           title: str = "Power Output vs Cell Temperature") -> go.Figure:
        """
        Create power vs temperature scatter plot with trend line

        Args:
            temperatures: List of cell temperatures
            powers: List of power measurements
            title: Graph title

        Returns:
            Plotly figure
        """
        # Calculate trend line
        z = np.polyfit(temperatures, powers, 1)
        p = np.poly1d(z)
        trend_x = np.linspace(min(temperatures), max(temperatures), 100)
        trend_y = p(trend_x)

        fig = go.Figure()

        # Scatter plot
        fig.add_trace(go.Scatter(
            x=temperatures,
            y=powers,
            mode='markers',
            name='Measured Data',
            marker=dict(
                size=10,
                color=powers,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Power (W)")
            )
        ))

        # Trend line
        fig.add_trace(go.Scatter(
            x=trend_x,
            y=trend_y,
            mode='lines',
            name=f'Trend (slope={z[0]:.3f} W/°C)',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Cell Temperature (°C)",
            yaxis_title="Power Output (W)",
            hovermode='closest',
            showlegend=True,
            height=450
        )

        return fig

    @staticmethod
    def efficiency_vs_temperature(temperatures: List[float],
                                 efficiencies: List[float],
                                 title: str = "Efficiency vs Cell Temperature") -> go.Figure:
        """
        Create efficiency vs temperature plot

        Args:
            temperatures: List of cell temperatures
            efficiencies: List of efficiency values (%)
            title: Graph title

        Returns:
            Plotly figure
        """
        # Calculate trend line
        z = np.polyfit(temperatures, efficiencies, 1)
        p = np.poly1d(z)
        trend_x = np.linspace(min(temperatures), max(temperatures), 100)
        trend_y = p(trend_x)

        fig = go.Figure()

        # Scatter plot
        fig.add_trace(go.Scatter(
            x=temperatures,
            y=efficiencies,
            mode='markers',
            name='Measured Data',
            marker=dict(size=10, color='green')
        ))

        # Trend line
        fig.add_trace(go.Scatter(
            x=trend_x,
            y=trend_y,
            mode='lines',
            name=f'Trend (slope={z[0]:.4f} %/°C)',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Cell Temperature (°C)",
            yaxis_title="Efficiency (%)",
            hovermode='closest',
            showlegend=True,
            height=450
        )

        return fig

    @staticmethod
    def environmental_conditions(timestamps: List[datetime],
                                irradiances: List[float],
                                wind_speeds: List[float],
                                title: str = "Environmental Conditions") -> go.Figure:
        """
        Create dual-axis plot for environmental conditions

        Args:
            timestamps: List of timestamps
            irradiances: List of irradiance values (W/m²)
            wind_speeds: List of wind speed values (m/s)
            title: Graph title

        Returns:
            Plotly figure with dual y-axes
        """
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Irradiance trace (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=irradiances,
                name="Irradiance",
                line=dict(color='orange', width=2),
                mode='lines+markers'
            ),
            secondary_y=False
        )

        # Wind speed trace (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=wind_speeds,
                name="Wind Speed",
                line=dict(color='cyan', width=2),
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update axes titles
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Irradiance (W/m²)", secondary_y=False)
        fig.update_yaxes(title_text="Wind Speed (m/s)", secondary_y=True)

        fig.update_layout(
            title=title,
            hovermode='x unified',
            height=400
        )

        return fig

    @staticmethod
    def iv_curve(voltages: List[float],
                currents: List[float],
                title: str = "I-V Curve") -> go.Figure:
        """
        Create I-V curve plot

        Args:
            voltages: List of voltage values (V)
            currents: List of current values (A)
            title: Graph title

        Returns:
            Plotly figure
        """
        # Calculate power
        powers = [v * i for v, i in zip(voltages, currents)]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # I-V curve (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=voltages,
                y=currents,
                name="I-V Curve",
                line=dict(color='blue', width=3),
                mode='lines'
            ),
            secondary_y=False
        )

        # P-V curve (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=voltages,
                y=powers,
                name="P-V Curve",
                line=dict(color='red', width=3),
                mode='lines'
            ),
            secondary_y=True
        )

        # Mark Pmax
        max_power_idx = powers.index(max(powers))
        fig.add_trace(
            go.Scatter(
                x=[voltages[max_power_idx]],
                y=[powers[max_power_idx]],
                name=f"Pmax ({max(powers):.2f}W)",
                mode='markers',
                marker=dict(size=15, color='green', symbol='star')
            ),
            secondary_y=True
        )

        fig.update_xaxes(title_text="Voltage (V)")
        fig.update_yaxes(title_text="Current (A)", secondary_y=False)
        fig.update_yaxes(title_text="Power (W)", secondary_y=True)

        fig.update_layout(
            title=title,
            hovermode='x unified',
            height=500
        )

        return fig

    @staticmethod
    def noct_summary_dashboard(protocol_results: Dict[str, Any]) -> None:
        """
        Create comprehensive NOCT results dashboard

        Args:
            protocol_results: Protocol results dictionary
        """
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            noct = protocol_results.get('noct_value')
            st.metric("NOCT", f"{noct:.2f}°C" if noct else "N/A")

        with col2:
            pmax = protocol_results.get('pmax_at_noct')
            st.metric("Pmax @ NOCT", f"{pmax:.2f}W" if pmax else "N/A")

        with col3:
            efficiency = protocol_results.get('efficiency_at_noct')
            st.metric("Efficiency @ NOCT", f"{efficiency:.2f}%" if efficiency else "N/A")

        with col4:
            temp_coeff = protocol_results.get('temperature_coefficients', {})
            alpha_p = temp_coeff.get('power', {}).get('alpha_p') if temp_coeff else None
            st.metric("Temp Coeff (Power)", f"{alpha_p:.3f}%/°C" if alpha_p else "N/A")

        # Temperature vs time graph
        if protocol_results.get('timestamps'):
            st.subheader("Temperature Monitoring")
            fig_temp = RealTimeGraphs.temperature_vs_time(
                protocol_results.get('timestamps', []),
                protocol_results.get('cell_temperatures', []),
                protocol_results.get('ambient_temperatures', [])
            )
            st.plotly_chart(fig_temp, use_container_width=True)

        # Power vs temperature (if available)
        if protocol_results.get('tc_temperatures') and protocol_results.get('tc_powers'):
            st.subheader("Temperature Coefficient Analysis")
            fig_power = RealTimeGraphs.power_vs_temperature(
                protocol_results['tc_temperatures'],
                protocol_results['tc_powers']
            )
            st.plotly_chart(fig_power, use_container_width=True)

        # Environmental conditions
        if protocol_results.get('timestamps'):
            st.subheader("Environmental Conditions")
            fig_env = RealTimeGraphs.environmental_conditions(
                protocol_results.get('timestamps', []),
                protocol_results.get('irradiances', []),
                protocol_results.get('wind_speeds', [])
            )
            st.plotly_chart(fig_env, use_container_width=True)


class LivePlotter:
    """Live plotting during test execution"""

    def __init__(self):
        self.placeholder = st.empty()

    def update(self, data: Dict[str, List]):
        """
        Update live plot with new data

        Args:
            data: Dictionary with lists of measurement data
        """
        with self.placeholder.container():
            if 'timestamps' in data and len(data['timestamps']) > 0:
                fig = RealTimeGraphs.temperature_vs_time(
                    data['timestamps'],
                    data.get('cell_temperatures', []),
                    data.get('ambient_temperatures', []),
                    title="Live Temperature Monitoring"
                )
                st.plotly_chart(fig, use_container_width=True)
