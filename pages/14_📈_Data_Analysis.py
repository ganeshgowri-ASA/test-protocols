"""
Data Analysis Module
====================
Advanced analytics, visualizations, and statistical insights from test results.
Provides interactive charts, statistical analysis, and data export capabilities.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Sample, TestExecution, TestData, ServiceRequest, TestProtocol,
    TestStatus, SampleStatus, AnalysisResult, DataExport, User
)
from sqlalchemy import select, desc, func, and_, or_

# Page configuration
setup_page_config(page_title="Data Analysis", page_icon="📊")

# Render navigation
render_header("Data Analysis", "Advanced analytics and statistical insights from test results")
render_sidebar_navigation()


def main():
    """Main data analysis page"""
    
    # Global filters
    st.sidebar.markdown("### 🎯 Global Filters")
    
    # Date range filter
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_start = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=90),
            key="global_date_start"
        )
    with col2:
        date_end = st.date_input(
            "End Date",
            value=datetime.now().date(),
            key="global_date_end"
        )
    
    # Protocol filter
    with get_db() as db:
        protocols = db.execute(
            select(TestProtocol)
            .where(TestProtocol.is_active == True)
            .order_by(TestProtocol.protocol_id)
        ).scalars().all()
        
        protocol_options = ["All"] + [f"{p.protocol_id} - {p.name}" for p in protocols]
    
    protocol_filter = st.sidebar.selectbox(
        "Protocol",
        options=protocol_options,
        key="global_protocol_filter"
    )
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Test Status",
        options=[s.value for s in TestStatus],
        default=[TestStatus.COMPLETED.value],
        key="global_status_filter"
    )
    
    # Tab structure
    tab1, tab2, tab3 = st.tabs([
        "📈 Analytics Dashboard",
        "📊 Statistical Analysis",
        "💾 Data Export"
    ])
    
    with tab1:
        render_analytics_dashboard(date_start, date_end, protocol_filter, status_filter)
    
    with tab2:
        render_statistical_analysis(date_start, date_end, protocol_filter, status_filter)
    
    with tab3:
        render_data_export(date_start, date_end, protocol_filter, status_filter)


def get_filtered_data(date_start, date_end, protocol_filter, status_filter):
    """Get filtered test execution data based on filters"""
    with get_db() as db:
        # Build query
        query = db.query(TestExecution).filter(
            and_(
                TestExecution.created_at >= datetime.combine(date_start, datetime.min.time()),
                TestExecution.created_at <= datetime.combine(date_end, datetime.max.time())
            )
        )
        
        # Apply protocol filter
        if protocol_filter != "All":
            protocol_id = protocol_filter.split(" - ")[0]
            protocol = db.execute(
                select(TestProtocol).where(TestProtocol.protocol_id == protocol_id)
            ).scalar_one_or_none()
            
            if protocol:
                query = query.filter(TestExecution.protocol_id == protocol.id)
        
        # Apply status filter
        if status_filter:
            status_enums = [TestStatus(s) for s in status_filter]
            query = query.filter(TestExecution.status.in_(status_enums))
        
        # Execute query and convert to DataFrame
        results = query.all()
        
        if not results:
            return pd.DataFrame()
        
        # Build DataFrame
        data = []
        for test in results:
            protocol = db.execute(
                select(TestProtocol).where(TestProtocol.id == test.protocol_id)
            ).scalar_one_or_none()
            
            technician = None
            if test.technician_id:
                technician = db.execute(
                    select(User).where(User.id == test.technician_id)
                ).scalar_one_or_none()
            
            data.append({
                'execution_number': test.execution_number,
                'protocol_id': protocol.protocol_id if protocol else 'Unknown',
                'protocol_name': protocol.name if protocol else 'Unknown',
                'protocol_category': protocol.category if protocol else 'Unknown',
                'sample_id': test.sample_id,
                'status': test.status.value,
                'test_passed': test.test_passed,
                'started_at': test.started_at,
                'completed_at': test.completed_at,
                'duration_hours': test.duration_hours,
                'technician': technician.full_name if technician else 'Unknown',
                'created_at': test.created_at,
                'failure_mode': test.failure_mode,
                'remarks': test.remarks
            })
        
        return pd.DataFrame(data)


def render_analytics_dashboard(date_start, date_end, protocol_filter, status_filter):
    """Render analytics dashboard with KPIs and interactive charts"""
    st.markdown("### 📈 Analytics Dashboard")
    
    # Get filtered data
    df = get_filtered_data(date_start, date_end, protocol_filter, status_filter)
    
    if df.empty:
        st.info("📊 No data available for the selected filters. Please adjust your filter criteria.")
        return
    
    # KPI Cards
    st.markdown("#### 📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = len(df)
    completed_tests = len(df[df['status'] == TestStatus.COMPLETED.value])
    passed_tests = len(df[df['test_passed'] == True])
    failed_tests = len(df[df['test_passed'] == False])
    pass_rate = (passed_tests / completed_tests * 100) if completed_tests > 0 else 0
    
    with col1:
        st.metric("Total Tests", total_tests)
    
    with col2:
        st.metric("Pass Rate", f"{pass_rate:.1f}%", 
                 delta=f"{passed_tests}/{completed_tests}" if completed_tests > 0 else "0/0")
    
    with col3:
        avg_duration = df[df['duration_hours'].notna()]['duration_hours'].mean()
        st.metric("Avg Duration", f"{avg_duration:.1f} hrs" if not pd.isna(avg_duration) else "N/A")
    
    with col4:
        active_samples = df['sample_id'].nunique()
        st.metric("Active Samples", active_samples)
    
    st.divider()
    
    # Time series chart - Test results over time
    st.markdown("#### 📉 Test Results Over Time")
    
    if 'completed_at' in df.columns and df['completed_at'].notna().any():
        df_completed = df[df['completed_at'].notna()].copy()
        df_completed['date'] = pd.to_datetime(df_completed['completed_at']).dt.date
        
        # Group by date and count
        daily_counts = df_completed.groupby(['date', 'test_passed']).size().reset_index(name='count')
        
        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            color='test_passed',
            title='Daily Test Results (Pass/Fail)',
            labels={'date': 'Date', 'count': 'Number of Tests', 'test_passed': 'Result'},
            color_discrete_map={True: 'green', False: 'red', None: 'gray'}
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Tests",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No completed tests with dates available for time series analysis.")
    
    st.divider()
    
    # Protocol performance comparison
    st.markdown("#### 🔬 Protocol Performance Comparison")
    
    protocol_stats = df.groupby('protocol_category').agg({
        'execution_number': 'count',
        'test_passed': lambda x: x.sum()
    }).reset_index()
    protocol_stats.columns = ['category', 'total', 'passed']
    protocol_stats['failed'] = protocol_stats['total'] - protocol_stats['passed']
    protocol_stats['pass_rate'] = (protocol_stats['passed'] / protocol_stats['total'] * 100).round(1)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Passed',
        x=protocol_stats['category'],
        y=protocol_stats['passed'],
        marker_color='green'
    ))
    fig.add_trace(go.Bar(
        name='Failed',
        x=protocol_stats['category'],
        y=protocol_stats['failed'],
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Pass/Fail by Protocol Category',
        xaxis_title='Protocol Category',
        yaxis_title='Number of Tests',
        barmode='group',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display stats table
    st.dataframe(
        protocol_stats[['category', 'total', 'passed', 'failed', 'pass_rate']],
        hide_index=True,
        use_container_width=True
    )
    
    st.divider()
    
    # Failure pattern heatmap
    st.markdown("#### 🔥 Failure Pattern Detection")
    
    failures = df[df['test_passed'] == False].copy()
    if not failures.empty and 'failure_mode' in failures.columns:
        failure_counts = failures.groupby(['protocol_category', 'failure_mode']).size().reset_index(name='count')
        
        # Create pivot table for heatmap
        heatmap_data = failure_counts.pivot(
            index='failure_mode',
            columns='protocol_category',
            values='count'
        ).fillna(0)
        
        if not heatmap_data.empty:
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Reds',
                hoverongaps=False
            ))
            fig.update_layout(
                title='Failure Mode Distribution by Category',
                xaxis_title='Protocol Category',
                yaxis_title='Failure Mode'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No failure mode data available for heatmap.")
    else:
        st.info("No test failures recorded in the selected period.")


def render_statistical_analysis(date_start, date_end, protocol_filter, status_filter):
    """Render statistical analysis with descriptive statistics and distributions"""
    st.markdown("### 📊 Statistical Analysis")
    
    # Get filtered data
    df = get_filtered_data(date_start, date_end, protocol_filter, status_filter)
    
    if df.empty:
        st.info("📊 No data available for the selected filters.")
        return
    
    # Descriptive Statistics
    st.markdown("#### 📈 Descriptive Statistics")
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        if 'duration_hours' in df.columns:
            mean_duration = df['duration_hours'].mean()
            st.metric("Mean Duration", f"{mean_duration:.2f} hrs" if not pd.isna(mean_duration) else "N/A")
    
    with col3:
        if 'duration_hours' in df.columns:
            median_duration = df['duration_hours'].median()
            st.metric("Median Duration", f"{median_duration:.2f} hrs" if not pd.isna(median_duration) else "N/A")
    
    with col4:
        if 'duration_hours' in df.columns:
            std_duration = df['duration_hours'].std()
            st.metric("Std Deviation", f"{std_duration:.2f} hrs" if not pd.isna(std_duration) else "N/A")
    
    st.divider()
    
    # Duration distribution
    if 'duration_hours' in df.columns and df['duration_hours'].notna().any():
        st.markdown("#### ⏱️ Duration Distribution")
        
        duration_data = df[df['duration_hours'].notna()]['duration_hours']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig = px.histogram(
                duration_data,
                nbins=30,
                title='Test Duration Histogram',
                labels={'value': 'Duration (hours)', 'count': 'Frequency'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot by category
            df_with_duration = df[df['duration_hours'].notna()]
            fig = px.box(
                df_with_duration,
                x='protocol_category',
                y='duration_hours',
                title='Duration Distribution by Protocol Category',
                labels={'protocol_category': 'Category', 'duration_hours': 'Duration (hours)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Correlation analysis
    st.markdown("#### 🔗 Correlation Analysis")
    
    # Create numeric columns for correlation
    df_numeric = df.copy()
    df_numeric['test_passed_numeric'] = df_numeric['test_passed'].map({True: 1, False: 0, None: 0.5})
    
    numeric_cols = ['duration_hours', 'test_passed_numeric']
    df_corr = df_numeric[numeric_cols].dropna()
    
    if len(df_corr) > 1:
        corr_matrix = df_corr.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 14}
        ))
        fig.update_layout(
            title='Correlation Matrix',
            width=600,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for correlation analysis.")
    
    st.divider()
    
    # Comparative analysis between batches
    st.markdown("#### 🔬 Comparative Analysis")
    
    # Compare pass rates by protocol
    protocol_comparison = df.groupby('protocol_name').agg({
        'execution_number': 'count',
        'test_passed': lambda x: (x == True).sum()
    }).reset_index()
    protocol_comparison.columns = ['protocol', 'total', 'passed']
    protocol_comparison['pass_rate'] = (protocol_comparison['passed'] / protocol_comparison['total'] * 100).round(1)
    protocol_comparison = protocol_comparison.sort_values('pass_rate', ascending=False)
    
    # Show top 10 protocols
    top_protocols = protocol_comparison.head(10)
    
    fig = px.bar(
        top_protocols,
        x='protocol',
        y='pass_rate',
        title='Top 10 Protocols by Pass Rate',
        labels={'protocol': 'Protocol', 'pass_rate': 'Pass Rate (%)'},
        color='pass_rate',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed statistics
    st.markdown("#### 📋 Detailed Statistics Table")
    st.dataframe(protocol_comparison, hide_index=True, use_container_width=True)
    
    # Outlier detection
    st.markdown("#### 🎯 Outlier Detection")
    
    if 'duration_hours' in df.columns and df['duration_hours'].notna().any():
        duration_data = df[df['duration_hours'].notna()]['duration_hours']
        
        Q1 = duration_data.quantile(0.25)
        Q3 = duration_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df['duration_hours'] < lower_bound) | (df['duration_hours'] > upper_bound)]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Outliers Detected", len(outliers))
        with col2:
            st.metric("Lower Bound", f"{lower_bound:.2f} hrs")
        with col3:
            st.metric("Upper Bound", f"{upper_bound:.2f} hrs")
        
        if not outliers.empty:
            st.markdown("**Outlier Records:**")
            st.dataframe(
                outliers[['execution_number', 'protocol_name', 'duration_hours', 'test_passed']],
                hide_index=True,
                use_container_width=True
            )


def render_data_export(date_start, date_end, protocol_filter, status_filter):
    """Render data export functionality"""
    st.markdown("### 💾 Data Export")
    
    # Get filtered data
    df = get_filtered_data(date_start, date_end, protocol_filter, status_filter)
    
    if df.empty:
        st.warning("📊 No data available to export. Please adjust your filter criteria.")
        return
    
    st.success(f"✅ {len(df)} records ready for export")
    
    # Export configuration
    st.markdown("#### ⚙️ Export Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            options=["Excel", "CSV"],
            help="Choose the export file format"
        )
    
    with col2:
        export_name = st.text_input(
            "Export Filename",
            value=f"test_data_{date_start}_{date_end}",
            help="Enter a filename (without extension)"
        )
    
    # Additional options
    include_charts = st.checkbox(
        "Include Charts in Excel Export",
        value=True,
        disabled=(export_format != "Excel"),
        help="Embed charts in the Excel file (Excel only)"
    )
    
    st.divider()
    
    # Export button
    if st.button("📥 Export Data", type="primary"):
        try:
            with st.spinner(f"Exporting data to {export_format}..."):
                if export_format == "Excel":
                    # Export to Excel
                    output = export_to_excel(df, export_name, include_charts)
                    file_extension = "xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                else:  # CSV
                    # Export to CSV
                    output = df.to_csv(index=False).encode('utf-8')
                    file_extension = "csv"
                    mime_type = "text/csv"
                
                # Provide download button
                st.download_button(
                    label=f"⬇️ Download {export_format} File",
                    data=output,
                    file_name=f"{export_name}.{file_extension}",
                    mime=mime_type
                )
                
                # Log the export
                log_export(export_format, export_name, date_start, date_end, 
                          protocol_filter, len(df))
                
                st.success(f"✅ Export successful! Click the download button above to save the file.")
                
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    st.divider()
    
    # Preview data
    st.markdown("#### 👀 Data Preview")
    st.dataframe(df.head(100), use_container_width=True, hide_index=True)
    
    # Export history
    st.markdown("#### 📜 Recent Exports")
    display_export_history()


def export_to_excel(df, filename, include_charts=True):
    """Export data to Excel with formatting and optional charts"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write main data
        df.to_excel(writer, sheet_name='Test Data', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Test Data']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(i, i, min(max_len, 50))
        
        # Add statistics sheet
        stats_df = df.describe()
        stats_df.to_excel(writer, sheet_name='Statistics')
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Tests', 'Passed Tests', 'Failed Tests', 'Pass Rate (%)', 'Avg Duration (hrs)'],
            'Value': [
                len(df),
                len(df[df['test_passed'] == True]),
                len(df[df['test_passed'] == False]),
                (len(df[df['test_passed'] == True]) / len(df) * 100) if len(df) > 0 else 0,
                df['duration_hours'].mean() if 'duration_hours' in df.columns else 0
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add charts if requested
        if include_charts:
            chart_sheet = workbook.add_worksheet('Charts')
            
            # Add a note about charts
            chart_sheet.write(0, 0, 'Interactive charts are available in the web interface.')
            chart_sheet.write(1, 0, 'This sheet contains chart data summaries.')
    
    output.seek(0)
    return output.getvalue()


def log_export(export_type, export_name, date_start, date_end, protocol_filter, records_count):
    """Log the export operation to the database"""
    try:
        with get_db() as db:
            export_id = f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            export_record = DataExport(
                export_id=export_id,
                export_type=export_type,
                export_name=export_name,
                file_path=f"exports/{export_name}.{export_type.lower()}",
                date_range=f"{date_start} to {date_end}",
                filters={"protocol": protocol_filter},
                records_count=records_count,
                exported_by=st.session_state.get('username', 'system')
            )
            
            db.add(export_record)
            db.commit()
    except Exception as e:
        st.warning(f"Could not log export: {str(e)}")


def display_export_history():
    """Display recent export history"""
    try:
        with get_db() as db:
            exports = db.execute(
                select(DataExport)
                .order_by(desc(DataExport.exported_at))
                .limit(10)
            ).scalars().all()
            
            if exports:
                export_data = []
                for export in exports:
                    export_data.append({
                        'Export ID': export.export_id,
                        'Type': export.export_type,
                        'Name': export.export_name,
                        'Records': export.records_count,
                        'Date Range': export.date_range,
                        'Exported By': export.exported_by,
                        'Exported At': export.exported_at.strftime('%Y-%m-%d %H:%M') if export.exported_at else 'N/A'
                    })
                
                st.dataframe(pd.DataFrame(export_data), hide_index=True, use_container_width=True)
            else:
                st.info("No export history available yet.")
    except Exception as e:
        st.info(f"Export history not available: {str(e)}")


if __name__ == "__main__":
    main()
