"""
Form Components
===============
Reusable form components for entities, audits, etc.
"""

import streamlit as st
from datetime import datetime, timedelta
from config.settings import config
from config.database import get_db
from models.entity import Entity
from models.user import User
from models.audit import AuditProgram, AuditType


def render_entity_form(entity=None):
    """
    Render entity creation/edit form

    Args:
        entity: Existing entity object for editing, None for new entity

    Returns:
        Dictionary with form data if submitted, None otherwise
    """
    with st.form("entity_form"):
        st.subheader("Entity Information")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Entity Name *",
                value=entity.name if entity else "",
                help="Name of the organization unit"
            )

            entity_type = st.selectbox(
                "Entity Type *",
                options=["Company", "Division", "Plant", "Department"],
                index=["Company", "Division", "Plant", "Department"].index(entity.type) if entity else 0
            )

            code = st.text_input(
                "Entity Code *",
                value=entity.code if entity else "",
                help="Unique identifier code"
            )

        with col2:
            # Get parent entities for hierarchical selection
            with get_db() as db:
                parent_entities = db.query(Entity).order_by(Entity.level, Entity.name).all()
                parent_options = ["None"] + [f"{e.name} ({e.type})" for e in parent_entities]
                parent_ids = [None] + [e.id for e in parent_entities]

                if entity and entity.parent_id:
                    default_idx = parent_ids.index(entity.parent_id)
                else:
                    default_idx = 0

            parent = st.selectbox(
                "Parent Entity",
                options=parent_options,
                index=default_idx,
                help="Select parent entity for hierarchy"
            )

            location = st.text_input(
                "Location",
                value=entity.location if entity else "",
                help="Physical location/address"
            )

        st.subheader("Contact Information")

        col3, col4 = st.columns(2)

        with col3:
            manager_name = st.text_input(
                "Manager Name",
                value=entity.manager_name if entity else ""
            )

        with col4:
            contact_email = st.text_input(
                "Contact Email",
                value=entity.contact_email if entity else ""
            )

        contact_phone = st.text_input(
            "Contact Phone",
            value=entity.contact_phone if entity else ""
        )

        submitted = st.form_submit_button(
            "Update Entity" if entity else "Create Entity",
            use_container_width=True
        )

        if submitted:
            if not name or not code:
                st.error("Please fill in all required fields (*)")
                return None

            # Determine level based on type
            level_map = {"Company": 1, "Division": 2, "Plant": 3, "Department": 4}
            level = level_map[entity_type]

            # Get parent_id
            parent_idx = parent_options.index(parent)
            parent_id = parent_ids[parent_idx]

            return {
                'name': name,
                'type': entity_type,
                'code': code,
                'level': level,
                'location': location,
                'parent_id': parent_id,
                'manager_name': manager_name,
                'contact_email': contact_email,
                'contact_phone': contact_phone
            }

    return None


def render_audit_form(schedule=None):
    """
    Render audit schedule creation/edit form

    Args:
        schedule: Existing schedule object for editing, None for new schedule

    Returns:
        Dictionary with form data if submitted, None otherwise
    """
    with st.form("audit_form"):
        st.subheader("Audit Schedule Details")

        # Get data for dropdowns
        with get_db() as db:
            programs = db.query(AuditProgram).filter_by(is_active=True).all()
            audit_types = db.query(AuditType).all()
            entities = db.query(Entity).order_by(Entity.level, Entity.name).all()
            auditors = db.query(User).filter(User.role.in_(['admin', 'auditor'])).all()

        col1, col2 = st.columns(2)

        with col1:
            program_options = [f"{p.name} ({p.year})" for p in programs]
            program_ids = [p.id for p in programs]
            program = st.selectbox("Audit Program *", options=program_options)

            audit_type_options = [at.name for at in audit_types]
            audit_type_ids = [at.id for at in audit_types]
            audit_type = st.selectbox("Audit Type *", options=audit_type_options)

        with col2:
            entity_options = [f"{e.name} ({e.type})" for e in entities]
            entity_ids = [e.id for e in entities]
            entity = st.selectbox("Auditee Entity *", options=entity_options)

            auditor_options = [f"{a.full_name} ({a.username})" for a in auditors]
            auditor_ids = [a.id for a in auditors]
            auditor = st.selectbox("Lead Auditor *", options=auditor_options)

        col3, col4 = st.columns(2)

        with col3:
            planned_date = st.date_input(
                "Planned Audit Date *",
                value=schedule.planned_date if schedule else datetime.now() + timedelta(days=7)
            )

        with col4:
            planned_duration = st.number_input(
                "Planned Duration (hours) *",
                min_value=0.5,
                max_value=40.0,
                value=float(schedule.planned_duration_hours) if schedule else 4.0,
                step=0.5
            )

        objectives = st.text_area(
            "Audit Objectives",
            value=schedule.objectives if schedule else "",
            help="What should this audit achieve?"
        )

        scope = st.text_area(
            "Audit Scope",
            value=schedule.scope if schedule else "",
            help="What areas/processes will be audited?"
        )

        submitted = st.form_submit_button(
            "Update Schedule" if schedule else "Create Schedule",
            use_container_width=True
        )

        if submitted:
            return {
                'program_id': program_ids[program_options.index(program)],
                'audit_type_id': audit_type_ids[audit_type_options.index(audit_type)],
                'auditee_entity_id': entity_ids[entity_options.index(entity)],
                'auditor_id': auditor_ids[auditor_options.index(auditor)],
                'planned_date': datetime.combine(planned_date, datetime.min.time()),
                'planned_duration_hours': planned_duration,
                'objectives': objectives,
                'scope': scope
            }

    return None
