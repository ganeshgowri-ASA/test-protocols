"""
Chart Generation Module
Create visualizations for test data using matplotlib and plotly
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class ChartGenerator:
    """Generate charts and visualizations for test data"""

    @staticmethod
    def plot_temperature_humidity(
        measurements: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        interactive: bool = False
    ):
        """
        Plot temperature and humidity over time

        Args:
            measurements: List of environmental measurements
            output_path: Path to save the plot
            interactive: Use plotly for interactive charts
        """
        # Convert to DataFrame
        df = pd.DataFrame(measurements)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        if interactive:
            # Create plotly figure with secondary y-axis
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                name='Temperature',
                line=dict(color='red', width=2),
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['relative_humidity'],
                name='Humidity',
                line=dict(color='blue', width=2),
                yaxis='y2'
            ))

            # Add target lines if available
            if 'target_temperature' in df.columns:
                target_temp = df['target_temperature'].iloc[0]
                fig.add_hline(
                    y=target_temp,
                    line_dash="dash",
                    line_color="red",
                    opacity=0.5,
                    yref='y1'
                )

            if 'target_humidity' in df.columns:
                target_hum = df['target_humidity'].iloc[0]
                fig.add_hline(
                    y=target_hum,
                    line_dash="dash",
                    line_color="blue",
                    opacity=0.5,
                    yref='y2'
                )

            fig.update_layout(
                title='Temperature and Humidity Monitoring',
                xaxis=dict(title='Time'),
                yaxis=dict(
                    title='Temperature (°C)',
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red')
                ),
                yaxis2=dict(
                    title='Relative Humidity (%)',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified'
            )

            if output_path:
                fig.write_html(output_path)

            return fig

        else:
            # Matplotlib version
            fig, ax1 = plt.subplots(figsize=(12, 6))

            ax1.set_xlabel('Time')
            ax1.set_ylabel('Temperature (°C)', color='red')
            ax1.plot(df['timestamp'], df['temperature'], color='red', label='Temperature')
            ax1.tick_params(axis='y', labelcolor='red')
            ax1.grid(True, alpha=0.3)

            # Add target line
            if 'target_temperature' in df.columns:
                target_temp = df['target_temperature'].iloc[0]
                ax1.axhline(y=target_temp, color='red', linestyle='--', alpha=0.5, label='Target')

            ax2 = ax1.twinx()
            ax2.set_ylabel('Relative Humidity (%)', color='blue')
            ax2.plot(df['timestamp'], df['relative_humidity'], color='blue', label='Humidity')
            ax2.tick_params(axis='y', labelcolor='blue')

            # Add target line
            if 'target_humidity' in df.columns:
                target_hum = df['target_humidity'].iloc[0]
                ax2.axhline(y=target_hum, color='blue', linestyle='--', alpha=0.5, label='Target')

            plt.title('Temperature and Humidity Monitoring')
            fig.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')

            return fig

    @staticmethod
    def plot_power_degradation(
        measurements: List[Dict[str, Any]],
        initial_power: float,
        output_path: Optional[str] = None,
        interactive: bool = False
    ):
        """
        Plot power degradation over time

        Args:
            measurements: List of electrical measurements
            initial_power: Initial Pmax value
            output_path: Path to save the plot
            interactive: Use plotly for interactive charts
        """
        df = pd.DataFrame(measurements)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calculate degradation percentage
        df['degradation'] = ((initial_power - df['pmax']) / initial_power) * 100

        if interactive:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['degradation'],
                mode='lines+markers',
                name='Power Degradation',
                line=dict(color='orange', width=2),
                marker=dict(size=6)
            ))

            # Add acceptance limit line
            fig.add_hline(
                y=5.0,
                line_dash="dash",
                line_color="red",
                annotation_text="Acceptance Limit (5%)"
            )

            fig.update_layout(
                title='Power Degradation Over Time',
                xaxis_title='Time',
                yaxis_title='Degradation (%)',
                hovermode='x unified'
            )

            if output_path:
                fig.write_html(output_path)

            return fig

        else:
            plt.figure(figsize=(12, 6))
            plt.plot(df['timestamp'], df['degradation'], 'o-', color='orange', linewidth=2, markersize=6)
            plt.axhline(y=5.0, color='red', linestyle='--', label='Acceptance Limit (5%)')
            plt.xlabel('Time')
            plt.ylabel('Degradation (%)')
            plt.title('Power Degradation Over Time')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')

            return plt.gcf()

    @staticmethod
    def plot_iv_curves(
        pre_test: Dict[str, Any],
        post_test: Dict[str, Any],
        output_path: Optional[str] = None,
        interactive: bool = False
    ):
        """
        Plot I-V curves comparison

        Args:
            pre_test: Pre-test I-V data
            post_test: Post-test I-V data
            output_path: Path to save the plot
            interactive: Use plotly for interactive charts
        """
        if interactive:
            fig = go.Figure()

            # Pre-test curve (simplified - showing key points)
            fig.add_trace(go.Scatter(
                x=[0, pre_test['vmpp'], pre_test['voc']],
                y=[pre_test['isc'], pre_test['impp'], 0],
                mode='lines+markers',
                name='Pre-test',
                line=dict(color='blue', width=2)
            ))

            # Post-test curve
            fig.add_trace(go.Scatter(
                x=[0, post_test['vmpp'], post_test['voc']],
                y=[post_test['isc'], post_test['impp'], 0],
                mode='lines+markers',
                name='Post-test',
                line=dict(color='red', width=2, dash='dash')
            ))

            fig.update_layout(
                title='I-V Curve Comparison',
                xaxis_title='Voltage (V)',
                yaxis_title='Current (A)',
                hovermode='x unified'
            )

            if output_path:
                fig.write_html(output_path)

            return fig

        else:
            plt.figure(figsize=(10, 6))

            # Simplified I-V curves using key points
            plt.plot(
                [0, pre_test['vmpp'], pre_test['voc']],
                [pre_test['isc'], pre_test['impp'], 0],
                'b-o',
                linewidth=2,
                label='Pre-test'
            )

            plt.plot(
                [0, post_test['vmpp'], post_test['voc']],
                [post_test['isc'], post_test['impp'], 0],
                'r--o',
                linewidth=2,
                label='Post-test'
            )

            plt.xlabel('Voltage (V)')
            plt.ylabel('Current (A)')
            plt.title('I-V Curve Comparison')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')

            return plt.gcf()

    @staticmethod
    def create_summary_dashboard(
        test_data: Dict[str, Any],
        output_path: Optional[str] = None
    ):
        """
        Create comprehensive test summary dashboard

        Args:
            test_data: Complete test data
            output_path: Path to save HTML dashboard
        """
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature Monitoring',
                'Humidity Monitoring',
                'Power Degradation',
                'Test Progress'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "indicator"}]
            ]
        )

        # Temperature plot
        if 'environmental_data' in test_data:
            df_env = pd.DataFrame(test_data['environmental_data'])
            df_env['timestamp'] = pd.to_datetime(df_env['timestamp'])

            fig.add_trace(
                go.Scatter(
                    x=df_env['timestamp'],
                    y=df_env['temperature'],
                    name='Temperature'
                ),
                row=1, col=1
            )

            # Humidity plot
            fig.add_trace(
                go.Scatter(
                    x=df_env['timestamp'],
                    y=df_env['relative_humidity'],
                    name='Humidity'
                ),
                row=1, col=2
            )

        # Power degradation
        if 'electrical_data' in test_data:
            df_elec = pd.DataFrame(test_data['electrical_data'])
            if not df_elec.empty:
                initial_power = df_elec['pmax'].iloc[0]
                df_elec['degradation'] = (
                    (initial_power - df_elec['pmax']) / initial_power * 100
                )

                fig.add_trace(
                    go.Scatter(
                        x=range(len(df_elec)),
                        y=df_elec['degradation'],
                        name='Degradation'
                    ),
                    row=2, col=1
                )

        # Test progress gauge
        progress = test_data.get('progress_percent', 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=progress,
                title={'text': "Progress"},
                gauge={'axis': {'range': [None, 100]}}
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Test Summary Dashboard"
        )

        if output_path:
            fig.write_html(output_path)

        return fig
