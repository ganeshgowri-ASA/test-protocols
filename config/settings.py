"""
Application Configuration Settings
===================================
Central configuration for Audit Pro Enterprise system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Application
    APP_NAME = "Audit Pro Enterprise"
    APP_VERSION = "1.0.0"
    SESSION_ID = "SESSION-APE-001"

    # Database
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR}/auditpro.db"
    )
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "audit-pro-enterprise-secret-key-change-in-production")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    # File Upload
    UPLOAD_DIR = BASE_DIR / "uploads"
    UPLOAD_DIR.mkdir(exist_ok=True)
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx'}

    # Reports
    REPORTS_DIR = BASE_DIR / "reports"
    REPORTS_DIR.mkdir(exist_ok=True)

    # Audit Standards
    SUPPORTED_STANDARDS = [
        "ISO 9001:2015",
        "ISO 14001:2015",
        "ISO 45001:2018",
        "ISO 27001:2022",
        "IATF 16949:2016",
        "AS9100D",
        "ISO 13485:2016",
        "ISO 22000:2018"
    ]

    # Entity Hierarchy Levels
    ENTITY_LEVELS = {
        1: "Company",
        2: "Division",
        3: "Plant",
        4: "Department"
    }

    # Audit Frequencies
    AUDIT_FREQUENCIES = [
        "Annual",
        "Semi-Annual",
        "Quarterly",
        "Monthly",
        "Ad-hoc"
    ]

    # NC/OFI Categories
    NC_CATEGORIES = [
        "Documentation",
        "Process",
        "Product/Service",
        "Management System",
        "Resource Management",
        "Infrastructure",
        "Competence",
        "Customer Focus"
    ]

    # Severity Levels
    SEVERITY_LEVELS = {
        "Critical": 4,
        "Major": 3,
        "Minor": 2,
        "Observation": 1
    }


# Create singleton config instance
config = Config()
