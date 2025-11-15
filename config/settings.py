"""
Global Configuration Settings for Solar PV Testing LIMS-QMS System
===================================================================
Centralized configuration management for the entire application.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
from dataclasses import dataclass
from datetime import datetime


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
STATIC_DIR = PROJECT_ROOT / "static"
PROTOCOLS_DIR = PROJECT_ROOT / "protocols"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOAD_DIR, STATIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    """Application configuration class"""

    # Application metadata
    APP_NAME: str = "Solar PV Testing LIMS-QMS"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Unified testing protocol management system"

    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'solar_pv_lims.db'}"
    )
    DB_ECHO: bool = False  # Set to True for SQL debugging

    # Application settings
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: list = None
    SESSION_TIMEOUT_MINUTES: int = 120

    # UI Configuration
    THEME_PRIMARY_COLOR: str = "#FF6B35"  # Solar orange
    THEME_BACKGROUND_COLOR: str = "#FFFFFF"
    THEME_SECONDARY_BG: str = "#F0F2F6"
    THEME_TEXT_COLOR: str = "#262730"

    # Protocol configuration
    TOTAL_PROTOCOLS: int = 54
    PROTOCOL_CATEGORIES: Dict[str, tuple] = None

    # Date/Time formats
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE_FORMAT: str = "%d %b %Y"
    DISPLAY_DATETIME_FORMAT: str = "%d %b %Y, %I:%M %p"

    # Validation settings
    ENABLE_QA_VALIDATION: bool = True
    REQUIRE_SUPERVISOR_APPROVAL: bool = True
    AUTO_SAVE_INTERVAL_SECONDS: int = 60

    # Export settings
    EXPORT_FORMATS: list = None
    PDF_LOGO_PATH: Optional[Path] = STATIC_DIR / "images" / "logo.png"

    # Email configuration (for notifications)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    # Security
    ENABLE_AUTHENTICATION: bool = True
    PASSWORD_MIN_LENGTH: int = 8
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "change-me-in-production")

    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = [
                "csv", "xlsx", "xls", "json", "pdf", "png", "jpg", "jpeg"
            ]

        if self.EXPORT_FORMATS is None:
            self.EXPORT_FORMATS = ["PDF", "Excel", "CSV", "JSON"]

        if self.PROTOCOL_CATEGORIES is None:
            self.PROTOCOL_CATEGORIES = {
                "performance": ("P1", "P12"),
                "degradation": ("P13", "P27"),
                "environmental": ("P28", "P39"),
                "mechanical": ("P40", "P47"),
                "safety": ("P48", "P54")
            }


# Global configuration instance
config = AppConfig()


def setup_page_config(
    page_title: str = None,
    page_icon: str = "☀️",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded"
):
    """
    Configure Streamlit page settings

    Args:
        page_title: Title of the page (defaults to app name)
        page_icon: Icon for the page
        layout: Page layout ("wide" or "centered")
        initial_sidebar_state: Initial sidebar state
    """
    st.set_page_config(
        page_title=page_title or config.APP_NAME,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
        menu_items={
            'Get Help': 'https://github.com/ganeshgowri-ASA/test-protocols',
            'Report a bug': 'https://github.com/ganeshgowri-ASA/test-protocols/issues',
            'About': f"{config.APP_NAME} v{config.APP_VERSION}"
        }
    )


def apply_custom_css():
    """Apply custom CSS styling to the application"""
    custom_css = f"""
    <style>
        /* Main theme colors */
        :root {{
            --primary-color: {config.THEME_PRIMARY_COLOR};
            --background-color: {config.THEME_BACKGROUND_COLOR};
            --secondary-bg: {config.THEME_SECONDARY_BG};
            --text-color: {config.THEME_TEXT_COLOR};
        }}

        /* Header styling */
        .main-header {{
            background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .main-header h1 {{
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }}

        /* Card styling */
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border-left: 4px solid var(--primary-color);
        }}

        /* Button styling */
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }}

        /* Protocol category badges */
        .protocol-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            margin: 0.25rem;
        }}

        .badge-performance {{ background: #E3F2FD; color: #1976D2; }}
        .badge-degradation {{ background: #FFF3E0; color: #F57C00; }}
        .badge-environmental {{ background: #E8F5E9; color: #388E3C; }}
        .badge-mechanical {{ background: #F3E5F5; color: #7B1FA2; }}
        .badge-safety {{ background: #FFEBEE; color: #C62828; }}

        /* Table styling */
        .dataframe {{
            border-radius: 8px;
            overflow: hidden;
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
        }}

        /* Success/Error message styling */
        .stAlert {{
            border-radius: 8px;
            border-left-width: 4px;
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }}

        /* Progress bar styling */
        .stProgress > div > div {{
            background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
            border-radius: 10px;
        }}

        /* Footer styling */
        .app-footer {{
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            border-top: 2px solid #E0E0E0;
            color: #666;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def get_protocol_info(protocol_id: str) -> Dict[str, Any]:
    """
    Get information about a specific protocol

    Args:
        protocol_id: Protocol identifier (e.g., "P1", "P28")

    Returns:
        Dictionary containing protocol metadata
    """
    # Extract protocol number
    try:
        protocol_num = int(protocol_id.replace("P", ""))
    except ValueError:
        return None

    # Determine category
    category = None
    for cat, (start, end) in config.PROTOCOL_CATEGORIES.items():
        start_num = int(start.replace("P", ""))
        end_num = int(end.replace("P", ""))
        if start_num <= protocol_num <= end_num:
            category = cat
            break

    return {
        "id": protocol_id,
        "number": protocol_num,
        "category": category,
        "category_display": category.title() if category else "Unknown"
    }


def format_datetime(dt: datetime, format_type: str = "display") -> str:
    """
    Format datetime object to string

    Args:
        dt: datetime object
        format_type: Type of format ("display", "storage", "date_only")

    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""

    if format_type == "display":
        return dt.strftime(config.DISPLAY_DATETIME_FORMAT)
    elif format_type == "date_only":
        return dt.strftime(config.DISPLAY_DATE_FORMAT)
    elif format_type == "storage":
        return dt.strftime(config.DATETIME_FORMAT)
    else:
        return str(dt)


def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not uploaded_file:
        return False, "No file uploaded"

    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > config.MAX_UPLOAD_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({config.MAX_UPLOAD_SIZE_MB} MB)"

    # Check file type
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if file_ext not in config.ALLOWED_FILE_TYPES:
        return False, f"File type '.{file_ext}' not allowed. Allowed types: {', '.join(config.ALLOWED_FILE_TYPES)}"

    return True, ""


# Initialize session state helper
def init_session_state(key: str, default_value: Any):
    """Initialize session state variable if not exists"""
    if key not in st.session_state:
        st.session_state[key] = default_value


# Protocol status definitions
PROTOCOL_STATUS = {
    "NOT_STARTED": {"label": "Not Started", "color": "gray"},
    "IN_PROGRESS": {"label": "In Progress", "color": "blue"},
    "PENDING_REVIEW": {"label": "Pending Review", "color": "orange"},
    "COMPLETED": {"label": "Completed", "color": "green"},
    "FAILED": {"label": "Failed", "color": "red"},
    "CANCELLED": {"label": "Cancelled", "color": "gray"}
}

# Equipment status
EQUIPMENT_STATUS = {
    "AVAILABLE": {"label": "Available", "color": "green"},
    "IN_USE": {"label": "In Use", "color": "blue"},
    "MAINTENANCE": {"label": "Maintenance", "color": "orange"},
    "CALIBRATION": {"label": "Calibration Due", "color": "red"},
    "OUT_OF_SERVICE": {"label": "Out of Service", "color": "gray"}
}
