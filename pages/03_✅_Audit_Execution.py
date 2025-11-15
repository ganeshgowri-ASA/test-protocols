"""
Audit Execution Page
====================
Execute audits, complete checklists, record findings.
"""

import streamlit as st
from datetime import datetime
from config.database import get_db
from config.settings import config
from models.audit import Audit, AuditSchedule, AuditStatus
from models.checklist import Checklist, ChecklistItem, AuditResponse, ResponseStatus
from models.nc_ofi import NC_OFI, FindingType, Severity, NCStatus
from components.auth import check_authentication, render_user_info
from components.tables import render_audit_table


st.set_page_config(page_title="Audit Execution", page_icon="✅", layout="wide")


def main():
    """Main audit execution page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    st.title("✅ Audit Execution")
    st.markdown("Execute scheduled audits and record findings")

    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    tabs = st.tabs(["🔍 Active Audits", "▶️ Start Audit", "📋 Ongoing Audits"])

    with tabs[0]:  # Active Audits
        st.subheader("Scheduled Audits")

        with get_db() as db:
            schedules = db.query(AuditSchedule).filter(
                AuditSchedule.status == AuditStatus.SCHEDULED
            ).order_by(AuditSchedule.planned_date).all()

        if schedules:
            for schedule in schedules:
                with st.expander(f"📅 {schedule.schedule_number} - {schedule.auditee_entity.name}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Date:** {schedule.planned_date.strftime('%Y-%m-%d')}")
                        st.write(f"**Type:** {schedule.audit_type.name}")
                        st.write(f"**Auditor:** {schedule.auditor.full_name}")
                        st.write(f"**Duration:** {schedule.planned_duration_hours} hours")
                        st.write(f"**Objectives:** {schedule.objectives or 'N/A'}")

                    with col2:
                        if st.button("Start Audit", key=f"start_{schedule.id}"):
                            st.session_state.start_audit_schedule_id = schedule.id
                            st.rerun()
        else:
            st.info("No scheduled audits found.")

    with tabs[1]:  # Start Audit
        st.subheader("Start New Audit")

        if 'start_audit_schedule_id' in st.session_state:
            with get_db() as db:
                schedule = db.query(AuditSchedule).filter_by(
                    id=st.session_state.start_audit_schedule_id
                ).first()

            if schedule:
                st.info(f"Starting audit for: {schedule.auditee_entity.name}")

                with st.form("start_audit_form"):
                    actual_date = st.date_input("Actual Audit Date", value=datetime.now())
                    start_time = st.time_input("Start Time", value=datetime.now().time())

                    if st.form_submit_button("Begin Audit"):
                        try:
                            with get_db() as db:
                                # Generate audit number
                                count = db.query(Audit).count()
                                audit_number = f"AUD-EX-{datetime.now().year}-{count + 1:04d}"

                                # Create audit
                                new_audit = Audit(
                                    audit_number=audit_number,
                                    schedule_id=schedule.id,
                                    actual_date=datetime.combine(actual_date, start_time),
                                    start_time=datetime.combine(actual_date, start_time),
                                    status=AuditStatus.IN_PROGRESS,
                                    created_at=datetime.utcnow()
                                )
                                db.add(new_audit)

                                # Update schedule status
                                schedule.status = AuditStatus.IN_PROGRESS
                                db.commit()

                            st.success(f"Audit started! Audit #: {audit_number}")
                            del st.session_state.start_audit_schedule_id
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error starting audit: {e}")
        else:
            st.info("Select an audit to start from the 'Active Audits' tab.")

    with tabs[2]:  # Ongoing Audits
        st.subheader("Ongoing Audits")

        with get_db() as db:
            ongoing_audits = db.query(Audit).filter(
                Audit.status == AuditStatus.IN_PROGRESS
            ).all()

        if ongoing_audits:
            for audit in ongoing_audits:
                with st.expander(f"🔄 {audit.audit_number} - {audit.schedule.auditee_entity.name}"):
                    st.write(f"**Started:** {audit.start_time.strftime('%Y-%m-%d %H:%M') if audit.start_time else 'N/A'}")
                    st.write(f"**Progress:** {audit.completion_percentage:.0f}%")
                    st.write(f"**Findings:** {audit.findings_count}")

                    if st.button("Continue Audit", key=f"cont_{audit.id}"):
                        st.session_state.execute_audit_id = audit.id
                        st.rerun()

                    if st.button("Complete Audit", key=f"comp_{audit.id}"):
                        with get_db() as db:
                            audit_obj = db.query(Audit).filter_by(id=audit.id).first()
                            audit_obj.status = AuditStatus.COMPLETED
                            audit_obj.completed_at = datetime.utcnow()
                            audit_obj.completion_percentage = 100.0
                            db.commit()
                        st.success("Audit marked as completed!")
                        st.rerun()
        else:
            st.info("No ongoing audits.")

    # Audit execution interface
    if 'execute_audit_id' in st.session_state:
        st.markdown("---")
        st.subheader("🎯 Audit Execution")

        with get_db() as db:
            audit = db.query(Audit).filter_by(id=st.session_state.execute_audit_id).first()

        if audit:
            st.info(f"Executing: {audit.audit_number} - {audit.schedule.auditee_entity.name}")

            # Quick add NC/OFI
            with st.expander("⚠️ Add Finding (NC/OFI)"):
                with st.form("add_finding"):
                    col1, col2 = st.columns(2)

                    with col1:
                        finding_type = st.selectbox("Type", ["NC", "OFI", "Observation"])
                        severity = st.selectbox("Severity", ["Critical", "Major", "Minor", "Observation"])
                        category = st.selectbox("Category", config.NC_CATEGORIES)

                    with col2:
                        clause = st.text_input("Clause Reference")
                        assignee_id = st.number_input("Assignee User ID", min_value=1, value=1)

                    description = st.text_area("Description *")

                    if st.form_submit_button("Add Finding"):
                        if description:
                            try:
                                with get_db() as db:
                                    count = db.query(NC_OFI).count()
                                    nc_number = f"NC-{datetime.now().year}-{count + 1:04d}"

                                    new_nc = NC_OFI(
                                        nc_number=nc_number,
                                        audit_id=audit.id,
                                        type=FindingType[finding_type.upper()] if finding_type != "Observation" else FindingType.OFI,
                                        severity=Severity[severity.upper()],
                                        category=category,
                                        clause=clause,
                                        description=description,
                                        assignee_id=assignee_id,
                                        status=NCStatus.OPEN,
                                        created_at=datetime.utcnow()
                                    )
                                    db.add(new_nc)

                                    # Update audit counts
                                    audit_obj = db.query(Audit).filter_by(id=audit.id).first()
                                    audit_obj.findings_count += 1
                                    if finding_type == "NC":
                                        audit_obj.nc_count += 1
                                    elif finding_type == "OFI":
                                        audit_obj.ofi_count += 1
                                    else:
                                        audit_obj.observations_count += 1

                                    db.commit()

                                st.success(f"Finding {nc_number} added successfully!")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error adding finding: {e}")
                        else:
                            st.error("Please provide a description")

            # Summary
            st.markdown("### Current Findings")
            st.write(f"**Total Findings:** {audit.findings_count}")
            st.write(f"**NC:** {audit.nc_count} | **OFI:** {audit.ofi_count} | **Observations:** {audit.observations_count}")


if __name__ == "__main__":
    main()
