"""
Interactive visualization components using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from models.protocol import Protocol, ProtocolStatus, KPIMetrics
from utils.helpers import get_status_color


class ChartBuilder:
    """Build interactive charts for dashboard"""

    def __init__(self, theme: str = "plotly"):
        self.theme = theme

    def create_status_gauge(self, value: float, title: str, max_value: float = 100,
                           threshold: float = 80, unit: str = "%") -> go.Figure:
        """Create a gauge chart for KPI metrics"""
        color = "green" if value >= threshold else "orange" if value >= threshold * 0.8 else "red"

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 16}},
            number={'suffix': unit, 'font': {'size': 32}},
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, threshold * 0.8], 'color': '#ffebee'},
                    {'range': [threshold * 0.8, threshold], 'color': '#fff8e1'},
                    {'range': [threshold, max_value], 'color': '#e8f5e9'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold
                }
            }
        ))

        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'size': 12}
        )

        return fig

    def create_protocol_status_distribution(self, protocols: List[Protocol]) -> go.Figure:
        """Create pie chart for protocol status distribution"""
        status_counts = {}
        for protocol in protocols:
            status = protocol.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        labels = list(status_counts.keys())
        values = list(status_counts.values())
        colors = [get_status_color(label) for label in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent+value',
            textposition='auto'
        )])

        fig.update_layout(
            title="Protocol Status Distribution",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=50, b=20)
        )

        return fig

    def create_timeline_gantt(self, protocols: List[Protocol], max_items: int = 20) -> go.Figure:
        """Create Gantt chart for protocol timeline"""
        df_data = []

        for protocol in protocols[:max_items]:
            if protocol.start_time:
                start = protocol.start_time
                end = protocol.end_time if protocol.end_time else datetime.now()

                df_data.append({
                    'Task': f"{protocol.protocol_name[:30]}...",
                    'Start': start,
                    'Finish': end,
                    'Status': protocol.status.value,
                    'Resource': protocol.operator or "Unassigned"
                })

        if not df_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No protocol data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        df = pd.DataFrame(df_data)

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Status",
            color_discrete_map={
                'completed': '#2ca02c',
                'in_progress': '#1f77b4',
                'pending': '#ff7f0e',
                'failed': '#d62728'
            },
            hover_data=['Resource']
        )

        fig.update_yaxes(categoryorder="total ascending")
        fig.update_layout(
            title="Protocol Execution Timeline",
            height=600,
            xaxis_title="Time",
            yaxis_title="Protocol",
            showlegend=True,
            margin=dict(l=200, r=20, t=50, b=50)
        )

        return fig

    def create_kpi_trend_chart(self, metrics: List[KPIMetrics], metric_name: str) -> go.Figure:
        """Create line chart for KPI trends"""
        dates = [m.date for m in metrics]
        values = [getattr(m, metric_name) for m in metrics]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=metric_name.replace('_', ' ').title(),
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))

        # Add trend line
        if len(values) > 1:
            z = pd.Series(values).rolling(window=3, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=dates,
                y=z,
                mode='lines',
                name='Trend',
                line=dict(color='red', width=2, dash='dash')
            ))

        fig.update_layout(
            title=f"{metric_name.replace('_', ' ').title()} Trend",
            xaxis_title="Date",
            yaxis_title=metric_name.replace('_', ' ').title(),
            height=400,
            hovermode='x unified',
            showlegend=True
        )

        return fig

    def create_heatmap(self, data: pd.DataFrame, x_col: str, y_col: str, value_col: str) -> go.Figure:
        """Create heatmap for pattern analysis"""
        pivot_table = data.pivot_table(values=value_col, index=y_col, columns=x_col, aggfunc='sum', fill_value=0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale='Blues',
            text=pivot_table.values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title=value_col)
        ))

        fig.update_layout(
            title=f"{value_col} Heatmap",
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=500
        )

        return fig

    def create_sankey_diagram(self, protocols: List[Protocol]) -> go.Figure:
        """Create Sankey diagram for data flow"""
        # Map: Request -> Protocol Type -> Status
        nodes = []
        links = []

        # Create nodes
        unique_types = list(set([p.protocol_type.value for p in protocols]))
        unique_statuses = list(set([p.status.value for p in protocols]))

        node_labels = ["Service Requests"] + unique_types + unique_statuses
        node_dict = {label: idx for idx, label in enumerate(node_labels)}

        # Create links
        type_counts = {}
        status_counts = {}

        for protocol in protocols:
            # Request to Type
            type_key = ("Service Requests", protocol.protocol_type.value)
            type_counts[type_key] = type_counts.get(type_key, 0) + 1

            # Type to Status
            status_key = (protocol.protocol_type.value, protocol.status.value)
            status_counts[status_key] = status_counts.get(status_key, 0) + 1

        # Add type links
        for (source, target), value in type_counts.items():
            links.append({
                'source': node_dict[source],
                'target': node_dict[target],
                'value': value
            })

        # Add status links
        for (source, target), value in status_counts.items():
            links.append({
                'source': node_dict[source],
                'target': node_dict[target],
                'value': value
            })

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color="lightblue"
            ),
            link=dict(
                source=[link['source'] for link in links],
                target=[link['target'] for link in links],
                value=[link['value'] for link in links]
            )
        )])

        fig.update_layout(
            title="Protocol Data Flow",
            height=600,
            font=dict(size=10)
        )

        return fig

    def create_equipment_utilization_chart(self, equipment: List) -> go.Figure:
        """Create bar chart for equipment utilization"""
        equipment_names = [eq.equipment_name for eq in equipment]
        utilization_rates = [eq.utilization_rate for eq in equipment]
        colors = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in utilization_rates]

        fig = go.Figure(data=[
            go.Bar(
                x=equipment_names,
                y=utilization_rates,
                marker_color=colors,
                text=[f"{rate:.1f}%" for rate in utilization_rates],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title="Equipment Utilization Rates",
            xaxis_title="Equipment",
            yaxis_title="Utilization Rate (%)",
            height=400,
            yaxis=dict(range=[0, 110]),
            xaxis_tickangle=-45
        )

        return fig

    def create_multi_metric_chart(self, metrics: List[KPIMetrics]) -> go.Figure:
        """Create multi-line chart for multiple KPIs"""
        dates = [m.date for m in metrics]

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Pass Rate', 'Average TAT', 'Throughput', 'Equipment Utilization'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Pass Rate
        fig.add_trace(
            go.Scatter(x=dates, y=[m.pass_rate for m in metrics], name="Pass Rate", line=dict(color='green')),
            row=1, col=1
        )

        # Average TAT
        fig.add_trace(
            go.Scatter(x=dates, y=[m.average_tat for m in metrics], name="Avg TAT", line=dict(color='blue')),
            row=1, col=2
        )

        # Throughput
        fig.add_trace(
            go.Scatter(x=dates, y=[m.throughput_daily for m in metrics], name="Throughput", line=dict(color='purple')),
            row=2, col=1
        )

        # Equipment Utilization
        fig.add_trace(
            go.Scatter(x=dates, y=[m.equipment_utilization for m in metrics], name="Eq. Util.", line=dict(color='orange')),
            row=2, col=2
        )

        fig.update_layout(height=600, showlegend=False, title_text="Multi-Metric Dashboard")
        fig.update_xaxes(title_text="Date")

        return fig
