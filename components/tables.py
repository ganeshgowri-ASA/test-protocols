"""
Table Components
================
Reusable data table components.
"""

import streamlit as st
import pandas as pd
from config.database import get_db
from models.entity import Entity
from models.audit import Audit, AuditSchedule


def render_entity_table(entities=None, selectable=False):
    """
    Render entities in a table format

    Args:
        entities: List of entities to display, None to fetch all
        selectable: If True, add selection column

    Returns:
        Selected entities if selectable=True
    """
    if entities is None:
        with get_db() as db:
            entities = db.query(Entity).order_by(Entity.level, Entity.name).all()

    if not entities:
        st.info("No entities found.")
        return None

    # Create dataframe
    data = []
    for entity in entities:
        data.append({
            'ID': entity.id,
            'Code': entity.code,
            'Name': entity.name,
            'Type': entity.type,
            'Level': entity.level,
            'Location': entity.location or '-',
            'Manager': entity.manager_name or '-',
            'Parent': entity.parent.name if entity.parent else '-'
        })

    df = pd.DataFrame(data)

    if selectable:
        # Display with checkboxes
        selected = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            disabled=['ID', 'Code', 'Name', 'Type', 'Level', 'Location', 'Manager', 'Parent']
        )
        return selected
    else:
        # Display read-only
        st.dataframe(df, hide_index=True, use_container_width=True)
        return None


def render_audit_table(audits=None, show_actions=False):
    """
    Render audits in a table format

    Args:
        audits: List of audits to display, None to fetch all
        show_actions: If True, add action buttons

    Returns:
        Selected audit ID if action clicked
    """
    if audits is None:
        with get_db() as db:
            audits = db.query(Audit).order_by(Audit.created_at.desc()).all()

    if not audits:
        st.info("No audits found.")
        return None

    # Create dataframe
    data = []
    for audit in audits:
        data.append({
            'Audit #': audit.audit_number,
            'Date': audit.actual_date.strftime('%Y-%m-%d') if audit.actual_date else '-',
            'Entity': audit.schedule.auditee_entity.name if audit.schedule else '-',
            'Auditor': audit.schedule.auditor.full_name if audit.schedule else '-',
            'Status': audit.status.value,
            'NC Count': audit.nc_count,
            'OFI Count': audit.ofi_count,
            'Score': f"{audit.score:.1f}" if audit.score else '-',
            'ID': audit.id
        })

    df = pd.DataFrame(data)

    # Display table
    st.dataframe(
        df.drop('ID', axis=1),
        hide_index=True,
        use_container_width=True
    )

    return None


def render_schedule_table(schedules=None):
    """
    Render audit schedules in a table format

    Args:
        schedules: List of schedules to display, None to fetch all
    """
    if schedules is None:
        with get_db() as db:
            schedules = db.query(AuditSchedule).order_by(AuditSchedule.planned_date).all()

    if not schedules:
        st.info("No scheduled audits found.")
        return

    # Create dataframe
    data = []
    for schedule in schedules:
        data.append({
            'Schedule #': schedule.schedule_number,
            'Planned Date': schedule.planned_date.strftime('%Y-%m-%d'),
            'Entity': schedule.auditee_entity.name,
            'Audit Type': schedule.audit_type.name,
            'Auditor': schedule.auditor.full_name,
            'Duration (hrs)': schedule.planned_duration_hours,
            'Status': schedule.status.value
        })

    df = pd.DataFrame(data)

    # Display table
    st.dataframe(df, hide_index=True, use_container_width=True)


def render_nc_ofi_table(nc_ofis=None):
    """
    Render NC/OFI in a table format

    Args:
        nc_ofis: List of NC/OFIs to display, None to fetch all
    """
    if nc_ofis is None:
        from models.nc_ofi import NC_OFI
        with get_db() as db:
            nc_ofis = db.query(NC_OFI).order_by(NC_OFI.created_at.desc()).all()

    if not nc_ofis:
        st.info("No NC/OFI records found.")
        return

    # Create dataframe
    data = []
    for nc in nc_ofis:
        data.append({
            'NC #': nc.nc_number,
            'Type': nc.type.value.upper(),
            'Severity': nc.severity.value,
            'Category': nc.category,
            'Clause': nc.clause,
            'Description': nc.description[:50] + '...' if len(nc.description) > 50 else nc.description,
            'Assignee': nc.assignee.full_name if nc.assignee else '-',
            'Status': nc.status.value,
            'Created': nc.created_at.strftime('%Y-%m-%d')
        })

    df = pd.DataFrame(data)

    # Color-code by severity
    def highlight_severity(row):
        if row['Severity'] == 'critical':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Severity'] == 'major':
            return ['background-color: #ffe6cc'] * len(row)
        elif row['Severity'] == 'minor':
            return ['background-color: #ffffcc'] * len(row)
        return [''] * len(row)

    st.dataframe(df, hide_index=True, use_container_width=True)
