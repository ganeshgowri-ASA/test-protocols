"""
Chart Components
================
Analytics and visualization components using Plotly.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from config.database import get_db
from models.audit import Audit, AuditStatus
from models.nc_ofi import NC_OFI, Severity, FindingType
from sqlalchemy import func


def render_audit_dashboard():
    """Render audit analytics dashboard"""

    with get_db() as db:
        # Total audits by status
        audit_counts = db.query(
            Audit.status,
            func.count(Audit.id).label('count')
        ).group_by(Audit.status).all()

        # NC/OFI counts
        nc_count = db.query(func.count(NC_OFI.id)).filter(NC_OFI.type == FindingType.NC).scalar()
        ofi_count = db.query(func.count(NC_OFI.id)).filter(NC_OFI.type == FindingType.OFI).scalar()

        # Open vs Closed NC/OFIs
        open_nc = db.query(func.count(NC_OFI.id)).filter(
            NC_OFI.type == FindingType.NC,
            NC_OFI.status.in_(['open', 'in_progress'])
        ).scalar()

        # Severity breakdown
        severity_counts = db.query(
            NC_OFI.severity,
            func.count(NC_OFI.id).label('count')
        ).group_by(NC_OFI.severity).all()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_audits = sum([c.count for c in audit_counts])
        st.metric("Total Audits", total_audits)

    with col2:
        st.metric("Non-Conformances", nc_count, delta=f"{open_nc} open")

    with col3:
        st.metric("Opportunities", ofi_count)

    with col4:
        completed_audits = sum([c.count for c in audit_counts if c.status == AuditStatus.COMPLETED])
        st.metric("Completed Audits", completed_audits)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Audit Status Distribution
        if audit_counts:
            status_df = pd.DataFrame([(str(c.status.value), c.count) for c in audit_counts],
                                    columns=['Status', 'Count'])
            fig = px.pie(status_df, values='Count', names='Status',
                        title='Audit Status Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # NC/OFI Severity Breakdown
        if severity_counts:
            severity_df = pd.DataFrame([(str(c.severity.value), c.count) for c in severity_counts],
                                       columns=['Severity', 'Count'])
            severity_df['Severity'] = pd.Categorical(
                severity_df['Severity'],
                categories=['critical', 'major', 'minor', 'observation'],
                ordered=True
            )
            severity_df = severity_df.sort_values('Severity')

            fig = px.bar(severity_df, x='Severity', y='Count',
                        title='NC/OFI by Severity',
                        color='Severity',
                        color_discrete_map={
                            'critical': '#dc3545',
                            'major': '#fd7e14',
                            'minor': '#ffc107',
                            'observation': '#28a745'
                        })
            st.plotly_chart(fig, use_container_width=True)


def render_nc_trends(months=6):
    """
    Render NC/OFI trends over time

    Args:
        months: Number of months to show
    """
    with get_db() as db:
        start_date = datetime.now() - timedelta(days=months*30)

        # Get NC/OFI data with dates
        nc_ofis = db.query(NC_OFI).filter(NC_OFI.created_at >= start_date).all()

        if not nc_ofis:
            st.info("No NC/OFI data available for the selected period.")
            return

        # Create dataframe
        data = []
        for nc in nc_ofis:
            data.append({
                'Date': nc.created_at.date(),
                'Type': nc.type.value,
                'Severity': nc.severity.value
            })

        df = pd.DataFrame(data)

        # Group by month and type
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M').astype(str)

        trend_df = df.groupby(['Month', 'Type']).size().reset_index(name='Count')

        # Create trend chart
        fig = px.line(trend_df, x='Month', y='Count', color='Type',
                     title='NC/OFI Trends Over Time',
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)


def render_entity_audit_heatmap():
    """Render heatmap of audits by entity"""
    with get_db() as db:
        from models.entity import Entity
        from models.audit import AuditSchedule

        # Get audit counts by entity
        entity_audits = db.query(
            Entity.name,
            func.count(AuditSchedule.id).label('audit_count')
        ).join(AuditSchedule).group_by(Entity.name).all()

        if not entity_audits:
            st.info("No audit data available.")
            return

        df = pd.DataFrame([(e.name, e.audit_count) for e in entity_audits],
                         columns=['Entity', 'Audit Count'])

        fig = px.bar(df, x='Entity', y='Audit Count',
                    title='Audits by Entity',
                    color='Audit Count',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
