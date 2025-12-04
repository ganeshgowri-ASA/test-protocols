"""
Training Management Module
==========================
Manage staff training, competencies, and certification tracking.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    StaffTraining, StaffTrainingRecord, User, TrainingStatus
)
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="Training Management", page_icon="🎓")

# Render navigation
render_header("Training Management", "Staff training and competency tracking")
render_sidebar_navigation()


def generate_training_id():
    """Generate unique training ID"""
    with get_db() as db:
        count = db.execute(
            select(func.count(StaffTraining.id))
        ).scalar() or 0
        return f"TRN-{datetime.now().year}-{count + 1:04d}"


def generate_record_number():
    """Generate unique training record number"""
    with get_db() as db:
        count = db.execute(
            select(func.count(StaffTrainingRecord.id))
        ).scalar() or 0
        return f"TR-{datetime.now().strftime('%Y%m%d')}-{count + 1:04d}"


def main():
    """Main training management page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Training Catalog",
        "📝 Training Records",
        "👥 Staff Competencies",
        "⏰ Expiring Certifications"
    ])

    with tab1:
        render_training_catalog()

    with tab2:
        render_training_records()

    with tab3:
        render_staff_competencies()

    with tab4:
        render_expiring_certifications()


def render_training_catalog():
    """Render training catalog management"""

    st.markdown("### 📚 Training Catalog")

    # Add new training
    with st.expander("➕ Add New Training Course"):
        with st.form("new_training"):
            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input("Training Title *", placeholder="e.g., Solar Module Safety")

                category = st.selectbox(
                    "Category *",
                    options=["Safety", "Equipment", "Protocol", "QMS", "General"]
                )

                training_type = st.selectbox(
                    "Training Type *",
                    options=["Initial", "Refresher", "Advanced", "Certification"]
                )

            with col2:
                duration = st.number_input("Duration (hours)", min_value=0.5, max_value=40.0, value=2.0, step=0.5)

                valid_months = st.number_input("Validity (months)", min_value=1, max_value=60, value=12)

                passing_score = st.number_input("Passing Score (%)", min_value=50, max_value=100, value=80)

            description = st.text_area("Description", placeholder="Training objectives and content...")

            assessment_required = st.checkbox("Assessment Required", value=True)

            required_for_roles = st.multiselect(
                "Required for Roles",
                options=["Admin", "Supervisor", "Technician", "Viewer"]
            )

            if st.form_submit_button("➕ Add Training", type="primary"):
                if not title:
                    st.error("Title is required")
                else:
                    try:
                        training_id = generate_training_id()

                        with get_db() as db:
                            new_training = StaffTraining(
                                training_id=training_id,
                                title=title,
                                description=description,
                                category=category.lower(),
                                training_type=training_type.lower(),
                                duration_hours=duration,
                                valid_months=valid_months,
                                passing_score=passing_score,
                                assessment_required=assessment_required,
                                required_for_roles=[r.lower() for r in required_for_roles] if required_for_roles else None,
                                created_by_id=1,
                                is_active=True
                            )
                            db.add(new_training)
                            db.commit()

                        st.success(f"✅ Training '{title}' added with ID: {training_id}")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    st.divider()

    # Training catalog list
    st.markdown("#### Available Training Courses")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All", "Safety", "Equipment", "Protocol", "QMS", "General"]
        )

    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            options=["All", "Initial", "Refresher", "Advanced", "Certification"]
        )

    with get_db() as db:
        query = select(StaffTraining).where(StaffTraining.is_active == True)

        if category_filter != "All":
            query = query.where(StaffTraining.category == category_filter.lower())

        if type_filter != "All":
            query = query.where(StaffTraining.training_type == type_filter.lower())

        trainings = db.execute(query.order_by(StaffTraining.title)).scalars().all()

        if trainings:
            for training in trainings:
                with st.expander(f"📖 {training.title} ({training.training_id})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**ID:** {training.training_id}")
                        st.markdown(f"**Category:** {training.category.title() if training.category else 'N/A'}")
                        st.markdown(f"**Type:** {training.training_type.title() if training.training_type else 'N/A'}")
                        st.markdown(f"**Duration:** {training.duration_hours} hours")

                    with col2:
                        st.markdown(f"**Valid for:** {training.valid_months} months")
                        st.markdown(f"**Passing Score:** {training.passing_score}%")
                        st.markdown(f"**Assessment:** {'Yes' if training.assessment_required else 'No'}")

                    if training.description:
                        st.markdown(f"**Description:** {training.description}")

                    if training.required_for_roles:
                        st.markdown(f"**Required for:** {', '.join([r.title() for r in training.required_for_roles])}")

                    # Action buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("📝 Schedule Training", key=f"schedule_{training.id}"):
                            st.session_state.schedule_training_id = training.id

                    with col2:
                        if st.button("✏️ Edit", key=f"edit_{training.id}"):
                            st.info("Edit functionality")

                    with col3:
                        if st.button("🗑️ Deactivate", key=f"deactivate_{training.id}"):
                            training.is_active = False
                            db.commit()
                            st.rerun()
        else:
            st.info("No training courses found")


def render_training_records():
    """Render training records management"""

    st.markdown("### 📝 Training Records")

    # Schedule new training
    with st.expander("📅 Schedule New Training Session"):
        with st.form("schedule_training"):
            col1, col2 = st.columns(2)

            with col1:
                # Select training
                with get_db() as db:
                    trainings = db.execute(
                        select(StaffTraining)
                        .where(StaffTraining.is_active == True)
                    ).scalars().all()

                    training_options = {f"{t.title} ({t.training_id})": t for t in trainings}

                selected_training = st.selectbox(
                    "Training Course *",
                    options=["-- Select --"] + list(training_options.keys())
                )

                # Select staff
                with get_db() as db:
                    users = db.execute(select(User).where(User.is_active == True)).scalars().all()
                    user_options = {f"{u.full_name} ({u.username})": u for u in users}

                selected_user = st.selectbox(
                    "Staff Member *",
                    options=["-- Select --"] + list(user_options.keys())
                )

            with col2:
                scheduled_date = st.date_input(
                    "Scheduled Date *",
                    value=datetime.now().date() + timedelta(days=7)
                )

                trainer_name = st.text_input("Trainer Name", placeholder="Trainer name")

            notes = st.text_area("Notes", placeholder="Additional notes...")

            if st.form_submit_button("📅 Schedule Training", type="primary"):
                if selected_training == "-- Select --" or selected_user == "-- Select --":
                    st.error("Please select training and staff member")
                else:
                    try:
                        training = training_options[selected_training]
                        user = user_options[selected_user]

                        record_number = generate_record_number()

                        # Calculate expiry date
                        expiry_date = datetime.combine(scheduled_date, datetime.min.time()) + timedelta(days=training.valid_months * 30)

                        with get_db() as db:
                            new_record = StaffTrainingRecord(
                                record_number=record_number,
                                training_id=training.id,
                                user_id=user.id,
                                scheduled_date=datetime.combine(scheduled_date, datetime.min.time()),
                                trainer_name=trainer_name,
                                status=TrainingStatus.SCHEDULED,
                                expiry_date=expiry_date,
                                notes=notes
                            )
                            db.add(new_record)
                            db.commit()

                        st.success(f"✅ Training scheduled! Record: {record_number}")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    st.divider()

    # Training records list
    st.markdown("#### Training Records")

    status_filter = st.selectbox(
        "Filter by Status",
        options=["All"] + [s.value.title() for s in TrainingStatus]
    )

    with get_db() as db:
        query = select(StaffTrainingRecord).order_by(desc(StaffTrainingRecord.scheduled_date))

        if status_filter != "All":
            query = query.where(StaffTrainingRecord.status == TrainingStatus(status_filter.lower()))

        records = db.execute(query.limit(50)).scalars().all()

        if records:
            for record in records:
                # Get training and user details
                training = db.execute(
                    select(StaffTraining).where(StaffTraining.id == record.training_id)
                ).scalar()

                user = db.execute(
                    select(User).where(User.id == record.user_id)
                ).scalar()

                status_colors = {
                    TrainingStatus.SCHEDULED: "🟡",
                    TrainingStatus.IN_PROGRESS: "🔵",
                    TrainingStatus.COMPLETED: "🟢",
                    TrainingStatus.EXPIRED: "🔴",
                    TrainingStatus.CANCELLED: "⚪"
                }
                status_icon = status_colors.get(record.status, "⚪")

                with st.expander(
                    f"{status_icon} {record.record_number} - {user.full_name if user else 'Unknown'} | {training.title if training else 'Unknown'}"
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Record:** {record.record_number}")
                        st.markdown(f"**Training:** {training.title if training else 'N/A'}")
                        st.markdown(f"**Staff:** {user.full_name if user else 'N/A'}")

                    with col2:
                        st.markdown(f"**Status:** {record.status.value.upper()}")
                        st.markdown(f"**Scheduled:** {record.scheduled_date.strftime('%Y-%m-%d') if record.scheduled_date else 'N/A'}")
                        st.markdown(f"**Trainer:** {record.trainer_name or 'N/A'}")

                    with col3:
                        if record.completion_date:
                            st.markdown(f"**Completed:** {record.completion_date.strftime('%Y-%m-%d')}")
                        if record.assessment_score is not None:
                            st.markdown(f"**Score:** {record.assessment_score}%")
                        st.markdown(f"**Expires:** {record.expiry_date.strftime('%Y-%m-%d') if record.expiry_date else 'N/A'}")

                    # Action buttons
                    if record.status == TrainingStatus.SCHEDULED:
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("▶️ Start Training", key=f"start_{record.id}"):
                                record.status = TrainingStatus.IN_PROGRESS
                                db.commit()
                                st.rerun()

                        with col2:
                            if st.button("❌ Cancel", key=f"cancel_{record.id}"):
                                record.status = TrainingStatus.CANCELLED
                                db.commit()
                                st.rerun()

                    elif record.status == TrainingStatus.IN_PROGRESS:
                        st.markdown("**Complete Training:**")
                        score = st.number_input(
                            "Assessment Score (%)",
                            min_value=0,
                            max_value=100,
                            value=80,
                            key=f"score_{record.id}"
                        )

                        if st.button("✅ Complete Training", key=f"complete_{record.id}"):
                            record.status = TrainingStatus.COMPLETED
                            record.completion_date = datetime.utcnow()
                            record.assessment_score = score
                            record.assessment_passed = score >= (training.passing_score if training else 80)
                            record.assessment_date = datetime.utcnow()
                            record.is_current = True
                            db.commit()
                            st.success("Training completed!")
                            st.rerun()
        else:
            st.info("No training records found")


def render_staff_competencies():
    """Render staff competency matrix"""

    st.markdown("### 👥 Staff Competency Matrix")

    with get_db() as db:
        users = db.execute(select(User).where(User.is_active == True)).scalars().all()
        trainings = db.execute(select(StaffTraining).where(StaffTraining.is_active == True)).scalars().all()

        if not users or not trainings:
            st.info("Add users and training courses first")
            return

        # Create competency matrix
        st.markdown("#### Competency Overview")

        for user in users:
            with st.expander(f"👤 {user.full_name} ({user.role.value if user.role else 'N/A'})"):
                # Get completed trainings
                completed = db.execute(
                    select(StaffTrainingRecord)
                    .where(StaffTrainingRecord.user_id == user.id)
                    .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                ).scalars().all()

                completed_training_ids = [r.training_id for r in completed]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Completed Trainings:**")
                    if completed:
                        for record in completed:
                            training = db.execute(
                                select(StaffTraining).where(StaffTraining.id == record.training_id)
                            ).scalar()

                            if training:
                                expiry = record.expiry_date
                                is_expired = expiry and expiry < datetime.utcnow()

                                if is_expired:
                                    st.markdown(f"🔴 {training.title} (Expired)")
                                else:
                                    st.markdown(f"✅ {training.title}")
                    else:
                        st.caption("No completed trainings")

                with col2:
                    st.markdown("**Required but Missing:**")
                    missing = []
                    for training in trainings:
                        if training.required_for_roles:
                            if user.role and user.role.value in training.required_for_roles:
                                if training.id not in completed_training_ids:
                                    missing.append(training.title)

                    if missing:
                        for m in missing:
                            st.markdown(f"⚠️ {m}")
                    else:
                        st.success("All required trainings completed!")


def render_expiring_certifications():
    """Render expiring certifications alerts"""

    st.markdown("### ⏰ Expiring Certifications")

    # Time range filter
    days_ahead = st.slider("Show expiring within (days)", 30, 180, 90)

    cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

    with get_db() as db:
        # Get expiring records
        expiring = db.execute(
            select(StaffTrainingRecord)
            .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
            .where(StaffTrainingRecord.expiry_date < cutoff_date)
            .where(StaffTrainingRecord.expiry_date > datetime.utcnow())
            .order_by(StaffTrainingRecord.expiry_date)
        ).scalars().all()

        # Get already expired
        expired = db.execute(
            select(StaffTrainingRecord)
            .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
            .where(StaffTrainingRecord.expiry_date < datetime.utcnow())
        ).scalars().all()

        if expired:
            st.error(f"🔴 {len(expired)} certification(s) EXPIRED")

            for record in expired:
                training = db.execute(
                    select(StaffTraining).where(StaffTraining.id == record.training_id)
                ).scalar()
                user = db.execute(
                    select(User).where(User.id == record.user_id)
                ).scalar()

                days_expired = (datetime.utcnow() - record.expiry_date).days

                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"**{user.full_name if user else 'Unknown'}**")
                col2.markdown(f"{training.title if training else 'Unknown'}")
                col3.error(f"{days_expired} days ago")
                with col4:
                    if st.button("🔄 Renew", key=f"renew_exp_{record.id}"):
                        st.info("Schedule renewal training")

        st.divider()

        if expiring:
            st.warning(f"⚠️ {len(expiring)} certification(s) expiring within {days_ahead} days")

            for record in expiring:
                training = db.execute(
                    select(StaffTraining).where(StaffTraining.id == record.training_id)
                ).scalar()
                user = db.execute(
                    select(User).where(User.id == record.user_id)
                ).scalar()

                days_until = (record.expiry_date - datetime.utcnow()).days

                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"**{user.full_name if user else 'Unknown'}**")
                col2.markdown(f"{training.title if training else 'Unknown'}")
                col3.warning(f"In {days_until} days")
                with col4:
                    if st.button("🔄 Renew", key=f"renew_{record.id}"):
                        st.info("Schedule renewal training")
        else:
            st.success("No certifications expiring soon!")


if __name__ == "__main__":
    main()
