"""
Authentication Component
========================
User authentication and session management with bcrypt.
"""

import streamlit as st
import bcrypt
from datetime import datetime
from functools import wraps
from config.database import get_db
from models.user import User, UserRole


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with username and password

    Args:
        username: User's username
        password: User's plain text password

    Returns:
        True if authentication successful, False otherwise
    """
    try:
        with get_db() as db:
            user = db.query(User).filter_by(username=username, is_active=True).first()

            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                # Update last login
                user.last_login = datetime.utcnow()
                db.commit()

                # Store user info in session
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.full_name = user.full_name
                st.session_state.role = user.role.value
                st.session_state.email = user.email

                return True

            return False

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False


def check_authentication() -> bool:
    """
    Check if user is authenticated

    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def logout():
    """Logout current user"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def require_role(allowed_roles: list):
    """
    Decorator to require specific roles for a function

    Args:
        allowed_roles: List of allowed role strings

    Usage:
        @require_role(['admin', 'auditor'])
        def admin_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not check_authentication():
                st.error("You must be logged in to access this page.")
                st.stop()

            user_role = st.session_state.get('role')
            if user_role not in allowed_roles:
                st.error(f"Access denied. Required roles: {', '.join(allowed_roles)}")
                st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorator


def render_login_page():
    """Render login page"""
    st.title("🔐 Audit Pro Enterprise")
    st.markdown("### Login")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if authenticate_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        st.info("**Default Login**\n\nUsername: `admin`\nPassword: `admin123`")


def get_current_user() -> User:
    """
    Get current logged-in user object

    Returns:
        User object or None
    """
    if not check_authentication():
        return None

    user_id = st.session_state.get('user_id')
    if not user_id:
        return None

    try:
        with get_db() as db:
            return db.query(User).filter_by(id=user_id).first()
    except Exception as e:
        st.error(f"Error fetching user: {e}")
        return None


def render_user_info():
    """Render current user information in sidebar"""
    if check_authentication():
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Current User")
        st.sidebar.write(f"**Name:** {st.session_state.full_name}")
        st.sidebar.write(f"**Role:** {st.session_state.role.upper()}")
        st.sidebar.write(f"**Email:** {st.session_state.email}")

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
