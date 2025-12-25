"""
Training Management Module
==========================
Manage staff training, competencies, and certification tracking.
Implements ISO 17025 compliance for personnel competency tracking.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    StaffTraining, StaffTrainingRecord, User, TrainingStatus, TestProtocol
)
from sqlalchemy import select, desc, func, and_, or_
from sqlalchemy.orm import load_only

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


def save_certificate_file(uploaded_file, record_number):
    """Save uploaded certificate file"""
    if uploaded_file is not None:
        # Create directory if it doesn't exist
        cert_dir = project_root / "static" / "training_certificates"
        cert_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"{record_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        filepath = cert_dir / filename
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(filepath.relative_to(project_root))
    return None


def main():
    """Main training management page"""

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📚 Training Catalog",
        "📝 Training Records",
        "👥 Competency Matrix",
        "⏰ Expiring Certifications",
        "📊 Training Metrics",
        "📋 ISO 17025 Reports"
    ])

    with tab1:
        render_training_catalog()

    with tab2:
        render_training_records()

    with tab3:
        render_competency_matrix()

    with tab4:
        render_expiring_certifications()
    
    with tab5:
        render_training_metrics()
    
    with tab6:
        render_iso_compliance_reports()


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
            
            # Add protocol selection
            with get_db() as db:
                protocols = db.execute(
                    select(TestProtocol).where(TestProtocol.is_active == True)
                ).scalars().all()
                protocol_options = {f"{p.protocol_id} - {p.name}": p.id for p in protocols}
            
            required_for_protocols = st.multiselect(
                "Required for Protocols",
                options=list(protocol_options.keys()),
                help="Select protocols that require this training"
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
                                required_for_protocols=[protocol_options[p] for p in required_for_protocols] if required_for_protocols else None,
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

        # Extract data while session is open to avoid DetachedInstanceError
        trainings_data = []
        for training in trainings:
            trainings_data.append({
                'id': training.id,
                'training_id': training.training_id,
                'title': training.title,
                'category': training.category,
                'training_type': training.training_type,
                'duration_hours': training.duration_hours,
                'valid_months': training.valid_months,
                'passing_score': training.passing_score,
                'assessment_required': training.assessment_required,
                'description': training.description,
                'required_for_roles': training.required_for_roles
            })

    if trainings_data:
        for training_data in trainings_data:
            with st.expander(f"📖 {training_data['title']} ({training_data['training_id']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**ID:** {training_data['training_id']}")
                    st.markdown(f"**Category:** {training_data['category'].title() if training_data['category'] else 'N/A'}")
                    st.markdown(f"**Type:** {training_data['training_type'].title() if training_data['training_type'] else 'N/A'}")
                    st.markdown(f"**Duration:** {training_data['duration_hours']} hours")

                with col2:
                    st.markdown(f"**Valid for:** {training_data['valid_months']} months")
                    st.markdown(f"**Passing Score:** {training_data['passing_score']}%")
                    st.markdown(f"**Assessment:** {'Yes' if training_data['assessment_required'] else 'No'}")

                if training_data['description']:
                    st.markdown(f"**Description:** {training_data['description']}")

                if training_data['required_for_roles']:
                    st.markdown(f"**Required for:** {', '.join([r.title() for r in training_data['required_for_roles']])}")

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📝 Schedule Training", key=f"schedule_{training_data['id']}"):
                        st.session_state.schedule_training_id = training_data['id']

                with col2:
                    if st.button("✏️ Edit", key=f"edit_{training_data['id']}"):
                        st.info("Edit functionality")

                with col3:
                    if st.button("🗑️ Deactivate", key=f"deactivate_{training_data['id']}"):
                        with get_db() as db:
                            training_obj = db.execute(
                                select(StaffTraining).where(StaffTraining.id == training_data['id'])
                            ).scalar_one_or_none()
                            if training_obj:
                                training_obj.is_active = False
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
                # Use load_only to avoid loading password_hash column that may not exist
                with get_db() as db:
                    users = db.execute(
                        select(User)
                        .options(load_only(
                            User.id, User.username, User.email, User.full_name,
                            User.role, User.is_active
                        ))
                        .where(User.is_active == True)
                    ).scalars().all()
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
                    select(User)
                    .options(load_only(User.id, User.full_name, User.username))
                    .where(User.id == record.user_id)
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
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            score = st.number_input(
                                "Assessment Score (%)",
                                min_value=0,
                                max_value=100,
                                value=80,
                                key=f"score_{record.id}"
                            )
                            
                            assessment_notes = st.text_area(
                                "Assessment Notes",
                                placeholder="Skills demonstrated, areas for improvement...",
                                key=f"notes_{record.id}"
                            )
                        
                        with col2:
                            certificate_file = st.file_uploader(
                                "Upload Certificate",
                                type=["pdf", "jpg", "jpeg", "png"],
                                help="Upload training certificate (PDF or image)",
                                key=f"cert_{record.id}"
                            )
                            
                            cert_number = st.text_input(
                                "Certificate Number",
                                placeholder="CERT-2024-001",
                                key=f"cert_num_{record.id}"
                            )

                        if st.button("✅ Complete Training", key=f"complete_{record.id}"):
                            # Save certificate file if uploaded
                            cert_path = None
                            if certificate_file:
                                cert_path = save_certificate_file(certificate_file, record.record_number)
                            
                            record.status = TrainingStatus.COMPLETED
                            record.completion_date = datetime.utcnow()
                            record.assessment_score = score
                            record.assessment_passed = score >= (training.passing_score if training else 80)
                            record.assessment_date = datetime.utcnow()
                            record.assessment_notes = assessment_notes
                            record.is_current = True
                            record.certificate_path = cert_path
                            record.certificate_number = cert_number if cert_number else None
                            db.commit()
                            st.success("✅ Training completed and certificate uploaded!")
                            st.rerun()
                    
                    # Show certificate if available
                    elif record.status == TrainingStatus.COMPLETED and record.certificate_path:
                        st.markdown("**📜 Certificate:**")
                        if st.button("📥 Download Certificate", key=f"download_{record.id}"):
                            cert_full_path = project_root / record.certificate_path
                            if cert_full_path.exists():
                                with open(cert_full_path, "rb") as f:
                                    st.download_button(
                                        "Download",
                                        f,
                                        file_name=cert_full_path.name,
                                        key=f"dl_btn_{record.id}"
                                    )
                            else:
                                st.error("Certificate file not found")
        else:
            st.info("No training records found")


def render_competency_matrix():
    """Render enhanced competency matrix by role and protocol"""

    st.markdown("### 👥 Competency Matrix")
    
    # View selection
    view_type = st.radio(
        "View by:",
        ["By Staff Member", "By Protocol", "Heatmap View"],
        horizontal=True
    )

    with get_db() as db:
        # Use load_only to avoid loading password_hash column that may not exist
        users = db.execute(
            select(User)
            .options(load_only(
                User.id, User.username, User.email, User.full_name,
                User.role, User.is_active
            ))
            .where(User.is_active == True)
        ).scalars().all()
        trainings = db.execute(select(StaffTraining).where(StaffTraining.is_active == True)).scalars().all()
        protocols = db.execute(select(TestProtocol).where(TestProtocol.is_active == True)).scalars().all()

        if not users or not trainings:
            st.info("Add users and training courses first")
            return

        if view_type == "By Staff Member":
            # Original staff view with protocol requirements
            for user in users:
                with st.expander(f"👤 {user.full_name} ({user.role.value if user.role else 'N/A'})"):
                    # Get completed trainings
                    completed = db.execute(
                        select(StaffTrainingRecord)
                        .where(StaffTrainingRecord.user_id == user.id)
                        .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                        .where(StaffTrainingRecord.is_current == True)
                    ).scalars().all()

                    completed_training_ids = [r.training_id for r in completed]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**✅ Completed Trainings:**")
                        if completed:
                            for record in completed:
                                training = db.execute(
                                    select(StaffTraining).where(StaffTraining.id == record.training_id)
                                ).scalar()

                                if training:
                                    expiry = record.expiry_date
                                    is_expired = expiry and expiry < datetime.utcnow()
                                    days_to_expiry = (expiry - datetime.utcnow()).days if expiry else 0

                                    if is_expired:
                                        st.markdown(f"🔴 {training.title} (Expired)")
                                    elif days_to_expiry < 30:
                                        st.markdown(f"🟡 {training.title} (Expires in {days_to_expiry} days)")
                                    else:
                                        st.markdown(f"🟢 {training.title}")
                        else:
                            st.caption("No completed trainings")

                    with col2:
                        st.markdown("**⚠️ Required but Missing:**")
                        missing = []
                        
                        # Check role-based requirements
                        for training in trainings:
                            if training.required_for_roles:
                                if user.role and user.role.value in training.required_for_roles:
                                    if training.id not in completed_training_ids:
                                        missing.append(f"{training.title} (Role)")
                        
                        # Check protocol-based requirements
                        for training in trainings:
                            if training.required_for_protocols:
                                for protocol_id in training.required_for_protocols:
                                    protocol = db.execute(
                                        select(TestProtocol).where(TestProtocol.id == protocol_id)
                                    ).scalar()
                                    if protocol and training.id not in completed_training_ids:
                                        if f"{training.title}" not in str(missing):
                                            missing.append(f"{training.title} (Protocol: {protocol.protocol_id})")

                        if missing:
                            for m in missing:
                                st.markdown(f"⚠️ {m}")
                        else:
                            st.success("All required trainings completed!")
        
        elif view_type == "By Protocol":
            # Protocol-based competency view
            st.markdown("#### 🔬 Protocol Competency Requirements")
            
            for protocol in protocols:
                # Get required trainings for this protocol
                required_trainings = [t for t in trainings if t.required_for_protocols and protocol.id in t.required_for_protocols]
                
                if required_trainings:
                    with st.expander(f"🔬 {protocol.protocol_id} - {protocol.name}"):
                        st.markdown("**Required Trainings:**")
                        for training in required_trainings:
                            st.markdown(f"- {training.title}")
                        
                        st.divider()
                        st.markdown("**Qualified Staff:**")
                        
                        # Find staff who have completed all required trainings
                        qualified_users = []
                        for user in users:
                            user_trainings = db.execute(
                                select(StaffTrainingRecord)
                                .where(StaffTrainingRecord.user_id == user.id)
                                .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                                .where(StaffTrainingRecord.is_current == True)
                            ).scalars().all()
                            
                            user_training_ids = [r.training_id for r in user_trainings]
                            required_ids = [t.id for t in required_trainings]
                            
                            if all(req_id in user_training_ids for req_id in required_ids):
                                qualified_users.append(user)
                        
                        if qualified_users:
                            for user in qualified_users:
                                st.markdown(f"✅ {user.full_name} ({user.role.value if user.role else 'N/A'})")
                        else:
                            st.warning("No staff currently qualified for this protocol")
        
        else:  # Heatmap View
            st.markdown("#### 📊 Competency Heatmap")
            
            # Create competency matrix
            matrix_data = []
            for user in users:
                user_data = {"Staff": user.full_name}
                
                # Get user's completed trainings
                user_trainings = db.execute(
                    select(StaffTrainingRecord)
                    .where(StaffTrainingRecord.user_id == user.id)
                    .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                    .where(StaffTrainingRecord.is_current == True)
                ).scalars().all()
                
                user_training_ids = [r.training_id for r in user_trainings]
                
                # Check each training
                for training in trainings[:10]:  # Limit to 10 for readability
                    if training.id in user_training_ids:
                        # Check if expiring soon
                        record = next((r for r in user_trainings if r.training_id == training.id), None)
                        if record and record.expiry_date:
                            days_to_expiry = (record.expiry_date - datetime.utcnow()).days
                            if days_to_expiry < 0:
                                user_data[training.title[:20]] = 0  # Expired
                            elif days_to_expiry < 30:
                                user_data[training.title[:20]] = 1  # Expiring soon
                            else:
                                user_data[training.title[:20]] = 2  # Current
                        else:
                            user_data[training.title[:20]] = 2  # Current
                    else:
                        user_data[training.title[:20]] = -1  # Not completed
                
                matrix_data.append(user_data)
            
            if matrix_data:
                df = pd.DataFrame(matrix_data)
                
                # Create heatmap
                fig = px.imshow(
                    df.set_index("Staff").T,
                    labels=dict(x="Staff Member", y="Training", color="Status"),
                    color_continuous_scale=["red", "orange", "yellow", "green"],
                    aspect="auto"
                )
                fig.update_layout(
                    title="Training Competency Status",
                    xaxis_title="Staff Member",
                    yaxis_title="Training Course",
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.caption("🔴 Not Completed | 🟠 Expired | 🟡 Expiring Soon | 🟢 Current")


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
                    select(User)
                    .options(load_only(User.id, User.full_name, User.username))
                    .where(User.id == record.user_id)
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
                    select(User)
                    .options(load_only(User.id, User.full_name, User.username))
                    .where(User.id == record.user_id)
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


def render_training_metrics():
    """Render training effectiveness metrics dashboard"""
    
    st.markdown("### 📊 Training Effectiveness Metrics")
    
    with get_db() as db:
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_trainings = db.execute(
                select(func.count(StaffTraining.id)).where(StaffTraining.is_active == True)
            ).scalar() or 0
            st.metric("Active Training Courses", total_trainings)
        
        with col2:
            total_records = db.execute(
                select(func.count(StaffTrainingRecord.id))
            ).scalar() or 0
            st.metric("Total Training Sessions", total_records)
        
        with col3:
            completed_records = db.execute(
                select(func.count(StaffTrainingRecord.id))
                .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
            ).scalar() or 0
            st.metric("Completed Sessions", completed_records)
        
        with col4:
            avg_score = db.execute(
                select(func.avg(StaffTrainingRecord.assessment_score))
                .where(StaffTrainingRecord.assessment_score.isnot(None))
            ).scalar() or 0
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        st.divider()
        
        # Training completion rate by category
        st.markdown("#### 📈 Training Completion by Category")
        
        trainings = db.execute(
            select(StaffTraining).where(StaffTraining.is_active == True)
        ).scalars().all()
        
        category_data = {}
        for training in trainings:
            category = training.category or "general"
            if category not in category_data:
                category_data[category] = {"total": 0, "completed": 0}
            
            category_data[category]["total"] += 1
            
            completed = db.execute(
                select(func.count(StaffTrainingRecord.id))
                .where(StaffTrainingRecord.training_id == training.id)
                .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
            ).scalar() or 0
            
            category_data[category]["completed"] += completed
        
        if category_data:
            categories = list(category_data.keys())
            completed_counts = [category_data[cat]["completed"] for cat in categories]
            
            fig = px.bar(
                x=categories,
                y=completed_counts,
                labels={'x': 'Category', 'y': 'Completed Sessions'},
                title='Completed Training Sessions by Category'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Pass/Fail Rate
        st.markdown("#### ✅ Assessment Pass/Fail Rate")
        
        passed = db.execute(
            select(func.count(StaffTrainingRecord.id))
            .where(StaffTrainingRecord.assessment_passed == True)
        ).scalar() or 0
        
        failed = db.execute(
            select(func.count(StaffTrainingRecord.id))
            .where(StaffTrainingRecord.assessment_passed == False)
        ).scalar() or 0
        
        if passed + failed > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Passed', 'Failed'],
                values=[passed, failed],
                marker=dict(colors=['green', 'red'])
            )])
            fig.update_layout(title='Training Assessment Results')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assessment data available yet")
        
        st.divider()
        
        # Training trends over time
        st.markdown("#### 📅 Training Trends Over Time")
        
        # Get training records from last 6 months
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        records = db.execute(
            select(StaffTrainingRecord)
            .where(StaffTrainingRecord.completion_date >= six_months_ago)
            .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
            .order_by(StaffTrainingRecord.completion_date)
        ).scalars().all()
        
        if records:
            # Group by month
            monthly_data = {}
            for record in records:
                month = record.completion_date.strftime('%Y-%m')
                monthly_data[month] = monthly_data.get(month, 0) + 1
            
            months = sorted(monthly_data.keys())
            counts = [monthly_data[m] for m in months]
            
            fig = px.line(
                x=months,
                y=counts,
                labels={'x': 'Month', 'y': 'Completions'},
                title='Training Completions Over Time'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No training completion data in the last 6 months")
        
        st.divider()
        
        # Top performers
        st.markdown("#### 🏆 Top Performers")
        
        user_scores = db.execute(
            select(
                User.full_name,
                func.avg(StaffTrainingRecord.assessment_score).label('avg_score'),
                func.count(StaffTrainingRecord.id).label('count')
            )
            .join(StaffTrainingRecord, User.id == StaffTrainingRecord.user_id)
            .where(StaffTrainingRecord.assessment_score.isnot(None))
            .group_by(User.id, User.full_name)
            .order_by(desc('avg_score'))
            .limit(5)
        ).all()
        
        if user_scores:
            for idx, (name, avg_score, count) in enumerate(user_scores, 1):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(f"**{idx}. {name}**")
                col2.markdown(f"Avg Score: **{avg_score:.1f}%**")
                col3.markdown(f"Trainings: **{count}**")
        else:
            st.info("No assessment data available")


def render_iso_compliance_reports():
    """Render ISO 17025 compliance reports"""
    
    st.markdown("### 📋 ISO 17025 Compliance Reports")
    st.markdown("Personnel competency tracking for laboratory accreditation")
    
    with get_db() as db:
        # Compliance summary
        st.markdown("#### 📊 Compliance Summary")

        # Use load_only to avoid loading password_hash column that may not exist
        users = db.execute(
            select(User)
            .options(load_only(
                User.id, User.username, User.email, User.full_name,
                User.role, User.is_active
            ))
            .where(User.is_active == True)
        ).scalars().all()
        trainings = db.execute(select(StaffTraining).where(StaffTraining.is_active == True)).scalars().all()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Personnel", len(users))
        
        with col2:
            # Count staff with all required trainings
            fully_compliant = 0
            for user in users:
                user_trainings = db.execute(
                    select(StaffTrainingRecord)
                    .where(StaffTrainingRecord.user_id == user.id)
                    .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                    .where(StaffTrainingRecord.is_current == True)
                ).scalars().all()
                
                user_training_ids = [r.training_id for r in user_trainings]
                
                # Check role-based requirements
                required = [t for t in trainings if t.required_for_roles and user.role and user.role.value in t.required_for_roles]
                required_ids = [t.id for t in required]
                
                if required_ids and all(rid in user_training_ids for rid in required_ids):
                    fully_compliant += 1
            
            st.metric("Fully Compliant Staff", fully_compliant)
        
        with col3:
            # Count expiring certifications (30 days)
            expiring_soon = db.execute(
                select(func.count(StaffTrainingRecord.id))
                .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                .where(StaffTrainingRecord.expiry_date < datetime.utcnow() + timedelta(days=30))
                .where(StaffTrainingRecord.expiry_date > datetime.utcnow())
            ).scalar() or 0
            
            st.metric("Expiring Soon (30d)", expiring_soon, delta_color="inverse")
        
        st.divider()
        
        # Personnel competency records
        st.markdown("#### 👥 Personnel Competency Records")
        st.caption("ISO 17025 Section 6.2 - Personnel Competency")
        
        for user in users:
            with st.expander(f"👤 {user.full_name} - {user.role.value if user.role else 'N/A'}"):
                # Get all training records
                all_records = db.execute(
                    select(StaffTrainingRecord)
                    .where(StaffTrainingRecord.user_id == user.id)
                    .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                    .order_by(desc(StaffTrainingRecord.completion_date))
                ).scalars().all()
                
                if all_records:
                    # Create table
                    data = []
                    for record in all_records:
                        training = db.execute(
                            select(StaffTraining).where(StaffTraining.id == record.training_id)
                        ).scalar()
                        
                        if training:
                            is_current = record.is_current
                            is_expired = record.expiry_date and record.expiry_date < datetime.utcnow()
                            
                            status = "✅ Current" if is_current and not is_expired else ("🔴 Expired" if is_expired else "⚪ Superseded")
                            
                            data.append({
                                "Training": training.title,
                                "Category": training.category.title() if training.category else "N/A",
                                "Completed": record.completion_date.strftime('%Y-%m-%d') if record.completion_date else "N/A",
                                "Expires": record.expiry_date.strftime('%Y-%m-%d') if record.expiry_date else "N/A",
                                "Score": f"{record.assessment_score}%" if record.assessment_score else "N/A",
                                "Status": status,
                                "Certificate": record.certificate_number or "N/A"
                            })
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No training records found for this staff member")
        
        st.divider()
        
        # Generate compliance report
        st.markdown("#### 📄 Generate Compliance Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Full Personnel Records", "Current Certifications Only", "Expiring Certifications", "Non-Compliant Personnel"]
            )
        
        with col2:
            report_format = st.selectbox(
                "Format",
                ["PDF", "Excel", "CSV"]
            )
        
        if st.button("📥 Generate Report", type="primary"):
            st.info(f"Generating {report_type} report in {report_format} format...")
            st.success("✅ Report generation feature will be implemented with PDF/Excel export capabilities")
            
            # Show preview of what would be exported
            st.markdown("**Report Preview:**")
            
            # Collect data based on report type
            report_data = []
            
            for user in users:
                records = db.execute(
                    select(StaffTrainingRecord)
                    .where(StaffTrainingRecord.user_id == user.id)
                    .where(StaffTrainingRecord.status == TrainingStatus.COMPLETED)
                ).scalars().all()
                
                for record in records:
                    training = db.execute(
                        select(StaffTraining).where(StaffTraining.id == record.training_id)
                    ).scalar()
                    
                    if training:
                        include_record = False
                        
                        if report_type == "Full Personnel Records":
                            include_record = True
                        elif report_type == "Current Certifications Only":
                            include_record = record.is_current and (not record.expiry_date or record.expiry_date > datetime.utcnow())
                        elif report_type == "Expiring Certifications":
                            include_record = record.expiry_date and record.expiry_date < datetime.utcnow() + timedelta(days=30) and record.expiry_date > datetime.utcnow()
                        
                        if include_record:
                            report_data.append({
                                "Staff Name": user.full_name,
                                "Role": user.role.value if user.role else "N/A",
                                "Training": training.title,
                                "Category": training.category.title() if training.category else "N/A",
                                "Completion Date": record.completion_date.strftime('%Y-%m-%d') if record.completion_date else "N/A",
                                "Expiry Date": record.expiry_date.strftime('%Y-%m-%d') if record.expiry_date else "N/A",
                                "Score": f"{record.assessment_score}%" if record.assessment_score else "N/A",
                                "Certificate": record.certificate_number or "N/A"
                            })
            
            if report_data:
                preview_df = pd.DataFrame(report_data)
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
                
                # Download button for CSV
                csv = preview_df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV Preview",
                    csv,
                    f"iso_compliance_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.warning("No data available for selected report type")


if __name__ == "__main__":
    main()
