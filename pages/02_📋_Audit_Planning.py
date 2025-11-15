"""
Audit Planning Page
===================
Plan and schedule audits, manage audit programs.
"""

import streamlit as st
from datetime import datetime, timedelta
from config.database import get_db
from models.audit import AuditProgram, AuditType, AuditSchedule, AuditStatus
from models.entity import Entity
from models.user import User
from components.auth import check_authentication, render_user_info
from components.forms import render_audit_form
from components.tables import render_schedule_table
from config.settings import config


st.set_page_config(page_title="Audit Planning", page_icon="📋", layout="wide")


def main():
    """Main audit planning page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("📋 Audit Planning")
    st.markdown("Schedule and manage your audit programs")

    # Sidebar
    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    # Tabs
    tabs = st.tabs(["📅 Schedules", "📚 Programs", "📋 Audit Types", "➕ New Schedule"])

    with tabs[0]:  # Schedules
        st.subheader("Audit Schedules")

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All"] + [s.value for s in AuditStatus]
            )

        with col2:
            filter_year = st.selectbox(
                "Filter by Year",
                ["All"] + list(range(datetime.now().year - 2, datetime.now().year + 3))
            )

        with col3:
            with get_db() as db:
                entities = db.query(Entity).all()
                entity_options = ["All"] + [e.name for e in entities]
                filter_entity = st.selectbox("Filter by Entity", entity_options)

        # Fetch schedules with filters
        with get_db() as db:
            query = db.query(AuditSchedule)

            if filter_status != "All":
                query = query.filter(AuditSchedule.status == filter_status)

            if filter_year != "All":
                year_start = datetime(filter_year, 1, 1)
                year_end = datetime(filter_year, 12, 31)
                query = query.filter(
                    AuditSchedule.planned_date >= year_start,
                    AuditSchedule.planned_date <= year_end
                )

            if filter_entity != "All":
                entity_id = [e.id for e in entities if e.name == filter_entity][0]
                query = query.filter(AuditSchedule.auditee_entity_id == entity_id)

            schedules = query.order_by(AuditSchedule.planned_date).all()

        if schedules:
            render_schedule_table(schedules)
            st.info(f"Showing {len(schedules)} scheduled audit(s)")
        else:
            st.info("No scheduled audits found. Create one in the 'New Schedule' tab.")

    with tabs[1]:  # Programs
        st.subheader("Audit Programs")

        # Add new program
        with st.expander("➕ Create New Program"):
            with st.form("program_form"):
                col1, col2 = st.columns(2)

                with col1:
                    prog_name = st.text_input("Program Name *")
                    prog_year = st.number_input("Year *", min_value=2020, max_value=2030,
                                               value=datetime.now().year)

                with col2:
                    prog_standard = st.selectbox("Standard", config.SUPPORTED_STANDARDS)
                    prog_frequency = st.selectbox("Frequency", config.AUDIT_FREQUENCIES)

                prog_scope = st.text_area("Scope")

                if st.form_submit_button("Create Program"):
                    if prog_name:
                        try:
                            with get_db() as db:
                                new_program = AuditProgram(
                                    name=prog_name,
                                    year=prog_year,
                                    standard=prog_standard,
                                    frequency=prog_frequency,
                                    scope=prog_scope,
                                    is_active=True,
                                    created_at=datetime.utcnow()
                                )
                                db.add(new_program)
                                db.commit()
                            st.success(f"Program '{prog_name}' created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating program: {e}")
                    else:
                        st.error("Please provide a program name")

        # List existing programs
        with get_db() as db:
            programs = db.query(AuditProgram).order_by(AuditProgram.year.desc()).all()

        if programs:
            for program in programs:
                with st.expander(f"📋 {program.name} ({program.year})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Standard:** {program.standard}")
                        st.write(f"**Frequency:** {program.frequency}")
                        st.write(f"**Scope:** {program.scope or 'N/A'}")
                        st.write(f"**Status:** {'Active' if program.is_active else 'Inactive'}")

                        # Count schedules
                        schedule_count = len(program.schedules)
                        st.write(f"**Scheduled Audits:** {schedule_count}")

                    with col2:
                        if st.button("Toggle Status", key=f"toggle_{program.id}"):
                            with get_db() as db:
                                prog = db.query(AuditProgram).filter_by(id=program.id).first()
                                prog.is_active = not prog.is_active
                                db.commit()
                            st.rerun()
        else:
            st.info("No programs found.")

    with tabs[2]:  # Audit Types
        st.subheader("Audit Types")

        # Add new type
        with st.expander("➕ Create New Audit Type"):
            with st.form("type_form"):
                type_name = st.text_input("Audit Type Name *")
                type_desc = st.text_area("Description")
                type_duration = st.number_input("Default Duration (hours)", min_value=1.0, max_value=40.0,
                                               value=4.0, step=0.5)
                type_team_size = st.number_input("Default Team Size", min_value=1, max_value=10, value=1)

                if st.form_submit_button("Create Audit Type"):
                    if type_name:
                        try:
                            with get_db() as db:
                                new_type = AuditType(
                                    name=type_name,
                                    description=type_desc,
                                    default_duration_hours=type_duration,
                                    default_team_size=type_team_size
                                )
                                db.add(new_type)
                                db.commit()
                            st.success(f"Audit type '{type_name}' created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating audit type: {e}")
                    else:
                        st.error("Please provide a type name")

        # List existing types
        with get_db() as db:
            audit_types = db.query(AuditType).all()

        if audit_types:
            for atype in audit_types:
                with st.expander(f"📋 {atype.name}"):
                    st.write(f"**Description:** {atype.description or 'N/A'}")
                    st.write(f"**Default Duration:** {atype.default_duration_hours} hours")
                    st.write(f"**Default Team Size:** {atype.default_team_size} auditor(s)")
        else:
            st.info("No audit types found.")

    with tabs[3]:  # New Schedule
        st.subheader("Schedule New Audit")

        form_data = render_audit_form()

        if form_data:
            try:
                with get_db() as db:
                    # Generate schedule number
                    count = db.query(AuditSchedule).count()
                    schedule_number = f"AUD-{datetime.now().year}-{count + 1:04d}"

                    new_schedule = AuditSchedule(
                        schedule_number=schedule_number,
                        **form_data,
                        status=AuditStatus.SCHEDULED,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_schedule)
                    db.commit()

                st.success(f"Audit scheduled successfully! Schedule #: {schedule_number}")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"Error scheduling audit: {e}")


if __name__ == "__main__":
    main()
