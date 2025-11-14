"""Chart generation module for visualization."""

import logging
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate charts for test data visualization."""

    def __init__(self, protocol: Dict[str, Any] = None):
        """
        Initialize ChartGenerator.

        Args:
            protocol: Optional protocol definition
        """
        self.protocol = protocol
        self.default_config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        }
        logger.info("ChartGenerator initialized")

    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        title: str = "Line Chart",
        x_label: str = None,
        y_label: str = None,
    ) -> go.Figure:
        """
        Create a line chart.

        Args:
            df: DataFrame with data
            x_column: Column name for x-axis
            y_columns: List of column names for y-axis
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        for y_col in y_columns:
            if y_col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df[x_column],
                        y=df[y_col],
                        mode="lines+markers",
                        name=y_col.replace("_", " ").title(),
                        line=dict(width=2),
                        marker=dict(size=6),
                    )
                )

        fig.update_layout(
            title=title,
            xaxis_title=x_label or x_column.replace("_", " ").title(),
            yaxis_title=y_label or "Value",
            hovermode="x unified",
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created line chart: {title}")
        return fig

    def create_scatter_chart(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str = "Scatter Plot",
        color_column: str = None,
    ) -> go.Figure:
        """
        Create a scatter plot.

        Args:
            df: DataFrame with data
            x_column: Column name for x-axis
            y_column: Column name for y-axis
            title: Chart title
            color_column: Optional column for color coding

        Returns:
            Plotly Figure object
        """
        if color_column and color_column in df.columns:
            fig = px.scatter(
                df,
                x=x_column,
                y=y_column,
                color=color_column,
                title=title,
                template="plotly_white",
            )
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=df[y_column],
                    mode="markers",
                    marker=dict(size=8, color="blue", opacity=0.6),
                    name=y_column,
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title=x_column.replace("_", " ").title(),
            yaxis_title=y_column.replace("_", " ").title(),
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created scatter chart: {title}")
        return fig

    def create_bar_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str = "Bar Chart",
        x_label: str = "Category",
        y_label: str = "Value",
    ) -> go.Figure:
        """
        Create a bar chart.

        Args:
            categories: List of category names
            values: List of values
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                marker=dict(
                    color=values,
                    colorscale="Viridis",
                    showscale=True,
                ),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created bar chart: {title}")
        return fig

    def create_box_plot(
        self,
        df: pd.DataFrame,
        value_column: str,
        group_column: str = None,
        title: str = "Box Plot",
    ) -> go.Figure:
        """
        Create a box plot.

        Args:
            df: DataFrame with data
            value_column: Column with values
            group_column: Optional column for grouping
            title: Chart title

        Returns:
            Plotly Figure object
        """
        if group_column and group_column in df.columns:
            fig = px.box(
                df,
                x=group_column,
                y=value_column,
                title=title,
                template="plotly_white",
            )
        else:
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[value_column], name=value_column))

        fig.update_layout(
            title=title,
            yaxis_title=value_column.replace("_", " ").title(),
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created box plot: {title}")
        return fig

    def create_histogram(
        self,
        values: List[float],
        title: str = "Histogram",
        x_label: str = "Value",
        bins: int = None,
    ) -> go.Figure:
        """
        Create a histogram.

        Args:
            values: List of values
            title: Chart title
            x_label: X-axis label
            bins: Number of bins (auto if None)

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=values,
                nbinsx=bins,
                marker=dict(color="steelblue", line=dict(color="white", width=1)),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title="Frequency",
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created histogram: {title}")
        return fig

    def create_heatmap(
        self,
        df: pd.DataFrame,
        title: str = "Heatmap",
        x_label: str = None,
        y_label: str = None,
    ) -> go.Figure:
        """
        Create a heatmap.

        Args:
            df: DataFrame with data (will use as matrix)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Heatmap(
                z=df.values,
                x=df.columns,
                y=df.index,
                colorscale="Viridis",
                hoverongaps=False,
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title=x_label or "Columns",
            yaxis_title=y_label or "Rows",
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created heatmap: {title}")
        return fig

    def create_comparison_chart(
        self,
        initial_values: List[float],
        final_values: List[float],
        labels: List[str],
        title: str = "Initial vs Final Comparison",
    ) -> go.Figure:
        """
        Create a grouped bar chart for initial vs final comparison.

        Args:
            initial_values: List of initial values
            final_values: List of final values
            labels: List of labels for each pair
            title: Chart title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Initial",
                x=labels,
                y=initial_values,
                marker=dict(color="steelblue"),
            )
        )

        fig.add_trace(
            go.Bar(
                name="Final",
                x=labels,
                y=final_values,
                marker=dict(color="coral"),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Measurement",
            yaxis_title="Value",
            barmode="group",
            template="plotly_white",
            height=500,
        )

        logger.debug(f"Created comparison chart: {title}")
        return fig

    def create_protocol_charts(
        self, df: pd.DataFrame, phase_id: str = None
    ) -> Dict[str, go.Figure]:
        """
        Create all charts defined in protocol.

        Args:
            df: DataFrame with measurements
            phase_id: Optional filter by phase

        Returns:
            Dictionary mapping chart IDs to Figure objects
        """
        if not self.protocol:
            logger.warning("No protocol defined, cannot create protocol charts")
            return {}

        charts = {}
        chart_defs = self.protocol["protocol"]["analysis"].get("default_charts", [])

        for chart_def in chart_defs:
            # Filter by phase if specified
            if chart_def.get("phase_id"):
                if phase_id and chart_def["phase_id"] != phase_id:
                    continue

                chart_df = df[df["phase_id"] == chart_def["phase_id"]]
            else:
                chart_df = df

            if chart_df.empty:
                continue

            chart_id = chart_def["chart_id"]
            chart_type = chart_def["type"]
            title = chart_def["title"]

            try:
                if chart_type == "line":
                    x_col = chart_def["x_axis"]
                    y_cols = chart_def["y_axis"]
                    if isinstance(y_cols, str):
                        y_cols = [y_cols]

                    charts[chart_id] = self.create_line_chart(
                        chart_df, x_col, y_cols, title
                    )

                elif chart_type == "scatter":
                    x_col = chart_def["x_axis"]
                    y_col = chart_def["y_axis"]
                    charts[chart_id] = self.create_scatter_chart(
                        chart_df, x_col, y_col, title
                    )

                elif chart_type == "bar":
                    # This would need more specific handling
                    pass

            except Exception as e:
                logger.error(f"Failed to create chart {chart_id}: {e}")

        logger.info(f"Created {len(charts)} protocol charts")
        return charts
