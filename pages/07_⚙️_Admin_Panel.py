"""
Admin Panel Page
================
System administration and user management.
"""

import streamlit as st
from datetime import datetime
import bcrypt
from config.database import get_db, check_database_health, reset_database
from config.settings import config
from models.user import User, UserRole
from models.base import AuditLog
from components.auth import check_authentication, render_user_info, require_role
from utils.validators import validate_email, validate_password_strength


st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")


def main():
    """Main admin panel page"""
    if not check_authentication():
        st.error("Please login to access this page.")
        st.stop()

    # Check if user is admin
    if st.session_state.get('role') != 'admin':
        st.error("Access denied. Admin privileges required.")
        st.stop()

    st.title("⚙️ Admin Panel")
    st.markdown("System administration and configuration")

    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    tabs = st.tabs(["👥 User Management", "📋 System Info", "🗄️ Database", "📊 Audit Logs"])

    with tabs[0]:  # User Management
        st.subheader("User Management")

        # Add new user
        with st.expander("➕ Create New User"):
            with st.form("create_user"):
                col1, col2 = st.columns(2)

                with col1:
                    username = st.text_input("Username *")
                    email = st.text_input("Email *")
                    full_name = st.text_input("Full Name *")

                with col2:
                    password = st.text_input("Password *", type="password")
                    confirm_password = st.text_input("Confirm Password *", type="password")
                    role = st.selectbox("Role *", ["admin", "auditor", "auditee", "viewer"])

                phone = st.text_input("Phone")
                department = st.text_input("Department")

                if st.form_submit_button("Create User"):
                    errors = []

                    if not username or not email or not full_name or not password:
                        errors.append("All required fields (*) must be filled")

                    if password != confirm_password:
                        errors.append("Passwords do not match")

                    if not validate_email(email):
                        errors.append("Invalid email format")

                    is_strong, msg = validate_password_strength(password)
                    if not is_strong:
                        errors.append(msg)

                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        try:
                            with get_db() as db:
                                # Check if username/email exists
                                existing = db.query(User).filter(
                                    (User.username == username) | (User.email == email)
                                ).first()

                                if existing:
                                    st.error("Username or email already exists")
                                else:
                                    # Hash password
                                    password_hash = bcrypt.hashpw(
                                        password.encode('utf-8'),
                                        bcrypt.gensalt()
                                    )

                                    new_user = User(
                                        username=username,
                                        email=email,
                                        password_hash=password_hash.decode('utf-8'),
                                        full_name=full_name,
                                        role=UserRole[role.upper()],
                                        phone=phone,
                                        department=department,
                                        is_active=True,
                                        created_at=datetime.utcnow()
                                    )
                                    db.add(new_user)
                                    db.commit()

                                    st.success(f"User '{username}' created successfully!")
                                    st.rerun()

                        except Exception as e:
                            st.error(f"Error creating user: {e}")

        # List users
        st.markdown("### Existing Users")

        with get_db() as db:
            users = db.query(User).order_by(User.created_at.desc()).all()

        if users:
            for user in users:
                with st.expander(f"👤 {user.full_name} ({user.username})"):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.write(f"**Email:** {user.email}")
                        st.write(f"**Role:** {user.role.value}")
                        st.write(f"**Department:** {user.department or 'N/A'}")

                    with col2:
                        st.write(f"**Phone:** {user.phone or 'N/A'}")
                        st.write(f"**Status:** {'Active' if user.is_active else 'Inactive'}")
                        st.write(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'}")

                    with col3:
                        if st.button("Toggle Status", key=f"toggle_{user.id}"):
                            with get_db() as db:
                                user_obj = db.query(User).filter_by(id=user.id).first()
                                user_obj.is_active = not user_obj.is_active
                                db.commit()
                            st.rerun()

            st.info(f"Total users: {len(users)}")
        else:
            st.info("No users found.")

    with tabs[1]:  # System Info
        st.subheader("System Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Application")
            st.write(f"**Name:** {config.APP_NAME}")
            st.write(f"**Version:** {config.APP_VERSION}")
            st.write(f"**Session ID:** {config.SESSION_ID}")

            st.markdown("### Database")
            db_health = check_database_health()
            if db_health['status'] == 'healthy':
                st.success(f"✅ Database: {db_health['status']}")
            else:
                st.error(f"❌ Database: {db_health.get('error', 'Unknown error')}")

        with col2:
            st.markdown("### Configuration")
            st.write(f"**Upload Max Size:** {config.MAX_FILE_SIZE_MB} MB")
            st.write(f"**Session Timeout:** {config.SESSION_TIMEOUT_MINUTES} minutes")
            st.write(f"**Bcrypt Rounds:** {config.BCRYPT_ROUNDS}")

            st.markdown("### Supported Standards")
            for standard in config.SUPPORTED_STANDARDS:
                st.write(f"- {standard}")

    with tabs[2]:  # Database
        st.subheader("Database Management")

        st.warning("⚠️ Database operations can affect system data. Use with caution!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Database Statistics")

            with get_db() as db:
                from models.entity import Entity
                from models.audit import Audit, AuditSchedule
                from models.nc_ofi import NC_OFI
                from models.car import CorrectiveAction

                stats = {
                    "Users": db.query(User).count(),
                    "Entities": db.query(Entity).count(),
                    "Audit Schedules": db.query(AuditSchedule).count(),
                    "Audits": db.query(Audit).count(),
                    "NC/OFI": db.query(NC_OFI).count(),
                    "CARs": db.query(CorrectiveAction).count(),
                    "Audit Logs": db.query(AuditLog).count()
                }

            for key, value in stats.items():
                st.metric(key, value)

        with col2:
            st.markdown("### Maintenance")

            if st.button("🔄 Check Database Health"):
                health = check_database_health()
                if health['status'] == 'healthy':
                    st.success("Database is healthy!")
                else:
                    st.error(f"Database issue: {health.get('error')}")

            st.markdown("---")
            st.error("**Danger Zone**")

            if st.button("🗑️ Reset Database (CAUTION!)"):
                st.warning("This will delete ALL data! This action cannot be undone.")
                if st.checkbox("I understand the consequences"):
                    if st.button("Confirm Reset"):
                        try:
                            reset_database()
                            st.success("Database reset successfully!")
                            st.info("Please logout and login again.")
                        except Exception as e:
                            st.error(f"Error resetting database: {e}")

    with tabs[3]:  # Audit Logs
        st.subheader("System Audit Logs")

        with get_db() as db:
            logs = db.query(AuditLog).order_by(
                AuditLog.created_at.desc()
            ).limit(100).all()

        if logs:
            for log in logs:
                timestamp = log.created_at.strftime('%Y-%m-%d %H:%M:%S')
                user_name = log.user.username if log.user else 'System'

                st.text(f"{timestamp} | {user_name} | {log.action} | {log.table_name} #{log.record_id or 'N/A'}")

            st.info(f"Showing {len(logs)} recent log entries")
        else:
            st.info("No audit logs found.")


if __name__ == "__main__":
    main()
