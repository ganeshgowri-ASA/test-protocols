"""
Configuration Settings for PV Testing Protocol Framework
"""

from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Protocol definitions directory
PROTOCOLS_DIR = BASE_DIR / "protocols" / "definitions"
SCHEMAS_DIR = BASE_DIR / "protocols" / "schemas"

# Data storage
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
SESSIONS_DIR = BASE_DIR / "sessions"

# Database
DATABASE_URL = "sqlite:///test_protocols.db"

# Safety settings
SAFETY_INTERLOCKS_ENABLED = True
EMERGENCY_STOP_ENABLED = True
REQUIRE_EQUIPMENT_CALIBRATION = True

# Traceability settings
AUDIT_LOG_ENABLED = True
DATA_LINEAGE_ENABLED = True
CRYPTOGRAPHIC_INTEGRITY = True

# Report settings
AUTO_GENERATE_REPORTS = True
DEFAULT_REPORT_FORMATS = ["pdf", "json"]
INCLUDE_AUDIT_TRAIL = True
INCLUDE_CHARTS = True

# Integration settings
LIMS_INTEGRATION_ENABLED = False
QMS_INTEGRATION_ENABLED = False
PM_INTEGRATION_ENABLED = False

# Compliance
CFR_PART_11_COMPLIANT = True
IEC_61730_COMPLIANT = True
