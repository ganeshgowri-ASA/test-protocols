"""
Configuration settings for Test Protocols Dashboard & Analytics Engine
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Dashboard settings
DASHBOARD_TITLE = "Test Protocols Master Dashboard & Analytics Engine"
DASHBOARD_ICON = "📊"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Protocol settings
TOTAL_PROTOCOLS = 54
PROTOCOL_CATEGORIES = [
    "Electrical Testing",
    "Mechanical Testing",
    "Environmental Testing",
    "Performance Testing",
    "Safety & Compliance",
    "Quality Control",
    "Calibration",
    "Material Analysis"
]

# KPI thresholds
TAT_TARGET_HOURS = 48
PASS_RATE_TARGET = 95.0
EQUIPMENT_UTILIZATION_TARGET = 80.0
FIRST_TIME_PASS_TARGET = 90.0

# Notification settings
ENABLE_NOTIFICATIONS = True
NOTIFICATION_CHANNELS = ["email", "dashboard", "webhook"]
CRITICAL_ALERT_THRESHOLD = 85  # percentage

# Visualization settings
CHART_THEME = "plotly"
COLOR_SCHEME = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#ff7f0e",
    "danger": "#d62728",
    "info": "#17a2b8"
}

# Export settings
EXPORT_FORMATS = ["PDF", "Excel", "CSV", "JSON"]
REPORT_TEMPLATES_DIR = BASE_DIR / "templates" / "reports"

# API settings
API_VERSION = "v1"
API_BASE_URL = "/api/v1"
API_RATE_LIMIT = 1000  # requests per hour

# Database settings (placeholder for future implementation)
DB_TYPE = "sqlite"  # Options: sqlite, postgresql, mysql
DB_PATH = DATA_DIR / "protocols.db"

# Cache settings
ENABLE_CACHE = True
CACHE_TTL = 300  # seconds

# Theme settings
THEMES = {
    "light": {
        "background": "#ffffff",
        "text": "#000000",
        "card_bg": "#f8f9fa"
    },
    "dark": {
        "background": "#1e1e1e",
        "text": "#ffffff",
        "card_bg": "#2d2d2d"
    }
}

# Mobile responsive breakpoints
BREAKPOINTS = {
    "mobile": 768,
    "tablet": 1024,
    "desktop": 1280
}

# Supported languages (for future i18n)
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de"]
DEFAULT_LANGUAGE = "en"
