"""
Navigation Components - Unified navigation and header
====================================================
Provides consistent navigation across all pages.
"""

import streamlit as st
from datetime import datetime
from config.settings import config, apply_custom_css
from config.database import check_database_health


def render_header(title: str = None, subtitle: str = None):
    """
    Render the main page header

    Args:
        title: Page title
        subtitle: Page subtitle
    """
    apply_custom_css()

    if title:
        st.markdown(f"""
        <div class='main-header'>
            <h1>☀️ {title}</h1>
            {f'<p style="margin: 0; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)


def render_sidebar_navigation():
    """
    Render the unified sidebar navigation

    This provides:
    - Main menu navigation
    - User profile
    - Current context
    - Quick actions
    - System status
    """

    with st.sidebar:
        # Logo/Branding
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='margin: 0; color: #FF6B35;'>☀️ Solar PV LIMS</h2>
            <p style='margin: 0; color: #666; font-size: 0.875rem;'>v{config.APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # User Profile Section
        render_user_profile()

        st.divider()

        # Main Navigation
        st.markdown("### 📌 Main Menu")

        # Navigation buttons
        nav_items = [
            ("🏠 Home", "app.py"),
            ("📋 Service Request", "pages/2_📋_Service_Request.py"),
            ("📦 Incoming Inspection", "pages/3_📦_Incoming_Inspection.py"),
            ("⚙️ Equipment Booking", "pages/4_⚙️_Equipment_Booking.py"),
            ("🔬 Test Protocols", "pages/5_🔬_Test_Protocols.py"),
        ]

        for label, page in nav_items:
            if st.button(label, use_container_width=True, key=f"nav_{page}"):
                st.switch_page(page)

        st.divider()

        # Context Panel - shows current active service request
        render_context_panel()

        st.divider()

        # Quick Actions
        render_quick_actions()

        st.divider()

        # System Status
        render_system_status()


def render_user_profile():
    """Render user profile section in sidebar"""

    # Initialize session state for user
    if 'user' not in st.session_state:
        st.session_state.user = {
            'username': 'demo_user',
            'full_name': 'Demo User',
            'role': 'technician',
            'email': 'demo@solarpv.com'
        }

    user = st.session_state.user

    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("👤")

        with col2:
            st.markdown(f"""
            <div style='font-size: 0.875rem;'>
                <strong>{user['full_name']}</strong><br>
                <span style='color: #666;'>{user['role'].title()}</span>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_context_panel():
    """Render current context panel showing active service request"""

    st.markdown("### 📎 Current Context")

    if 'active_service_request' in st.session_state and st.session_state.active_service_request:
        sr = st.session_state.active_service_request

        st.info(f"""
        **Service Request:** {sr.get('request_number', 'N/A')}
        **Client:** {sr.get('client_name', 'N/A')}
        **Status:** {sr.get('status', 'N/A').upper()}
        """)

        if st.button("Clear Context", use_container_width=True):
            st.session_state.active_service_request = None
            st.rerun()
    else:
        st.caption("No active service request")


def render_quick_actions():
    """Render quick action buttons"""

    st.markdown("### ⚡ Quick Actions")

    quick_actions = [
        ("📝 New Request", "new_request"),
        ("🔍 Search", "search"),
        ("📊 Reports", "reports"),
        ("⚙️ Settings", "settings")
    ]

    for label, action_key in quick_actions:
        if st.button(label, use_container_width=True, key=f"qa_{action_key}"):
            handle_quick_action(action_key)


def handle_quick_action(action: str):
    """
    Handle quick action clicks

    Args:
        action: Action identifier
    """
    if action == "new_request":
        st.switch_page("pages/2_📋_Service_Request.py")
    elif action == "search":
        st.session_state.show_search = True
    elif action == "reports":
        st.info("Reports module - Coming soon!")
    elif action == "settings":
        st.info("Settings module - Coming soon!")


def render_system_status():
    """Render system status indicators"""

    st.markdown("### 🔧 System Status")

    # Check database health
    db_health = check_database_health()

    if db_health['connected']:
        st.success("✅ Database Connected")
    else:
        st.error("❌ Database Error")

    # Equipment status (placeholder)
    st.info("⚙️ Equipment: 12/15 Available")

    # Active users (placeholder)
    st.info("👥 Active Users: 8")


def render_breadcrumb(items: list):
    """
    Render breadcrumb navigation

    Args:
        items: List of (label, link) tuples
    """
    breadcrumb_html = " → ".join([
        f"<a href='{link}' style='text-decoration: none; color: #FF6B35;'>{label}</a>"
        if link else f"<span style='color: #666;'>{label}</span>"
        for label, link in items
    ])

    st.markdown(f"""
    <div style='padding: 0.5rem 0; font-size: 0.875rem;'>
        {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)


def render_page_actions(actions: list):
    """
    Render page-level action buttons

    Args:
        actions: List of (label, callback, variant) tuples
    """
    cols = st.columns(len(actions))

    for idx, (label, callback, variant) in enumerate(actions):
        with cols[idx]:
            button_type = "primary" if variant == "primary" else "secondary"
            if st.button(label, use_container_width=True, type=button_type):
                callback()


def show_notification(message: str, type: str = "info"):
    """
    Display a notification message

    Args:
        message: Notification message
        type: Type of notification (success, error, warning, info)
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def confirm_dialog(title: str, message: str, confirm_label: str = "Confirm", cancel_label: str = "Cancel") -> bool:
    """
    Show confirmation dialog

    Args:
        title: Dialog title
        message: Dialog message
        confirm_label: Confirm button label
        cancel_label: Cancel button label

    Returns:
        True if confirmed, False otherwise
    """
    with st.container():
        st.warning(f"**{title}**\n\n{message}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(confirm_label, use_container_width=True, type="primary"):
                return True

        with col2:
            if st.button(cancel_label, use_container_width=True):
                return False

    return False
