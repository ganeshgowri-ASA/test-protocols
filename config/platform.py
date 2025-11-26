"""
Multi-Platform Detection and Configuration
==========================================
Automatically detects deployment platform and configures the application accordingly.
Supports: Railway, Replit, GenSpark, Streamlit Cloud, and Local Development.
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported deployment platforms"""
    RAILWAY = "railway"
    REPLIT = "replit"
    GENSPARK = "genspark"
    STREAMLIT_CLOUD = "streamlit_cloud"
    LOCAL = "local"


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: Platform
    database_type: DatabaseType
    database_url: str
    is_production: bool
    supports_persistent_storage: bool
    max_pool_size: int
    pool_overflow: int
    pool_pre_ping: bool
    features: Dict[str, bool]


def detect_platform() -> Platform:
    """
    Detect the current deployment platform based on environment variables.

    Returns:
        Platform enum indicating the detected platform
    """
    # Railway detection
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_SERVICE_NAME"):
        logger.info("Detected Railway platform")
        return Platform.RAILWAY

    # Replit detection
    if os.getenv("REPL_ID") or os.getenv("REPL_SLUG"):
        logger.info("Detected Replit platform")
        return Platform.REPLIT

    # GenSpark detection (custom env var)
    if os.getenv("GENSPARK_APP_ID") or os.getenv("GENSPARK_ENVIRONMENT"):
        logger.info("Detected GenSpark platform")
        return Platform.GENSPARK

    # Streamlit Cloud detection
    if os.getenv("STREAMLIT_SERVER_HEADLESS") == "true" or os.getenv("STREAMLIT_CLOUD"):
        # Additional check for cloud-specific paths
        home = os.getenv("HOME", "")
        if "/mount/src/" in home or "/app/" in home:
            logger.info("Detected Streamlit Cloud platform")
            return Platform.STREAMLIT_CLOUD

    # Default to local development
    logger.info("No platform detected, defaulting to local development")
    return Platform.LOCAL


def get_database_url(platform: Platform) -> tuple[DatabaseType, str]:
    """
    Get the appropriate database URL based on platform and environment.

    Supports rollback mechanism via environment variables:
    - FORCE_SQLITE=1: Force SQLite even if PostgreSQL is available
    - DATABASE_URL: Use provided PostgreSQL URL
    - POSTGRES_URL: Alternative PostgreSQL URL (Railway format)

    Args:
        platform: The detected deployment platform

    Returns:
        Tuple of (DatabaseType, database_url)
    """
    from pathlib import Path

    # Check for rollback/force SQLite flag (CRITICAL ROLLBACK MECHANISM)
    if os.getenv("FORCE_SQLITE", "").lower() in ("1", "true", "yes"):
        logger.warning("ROLLBACK MODE: FORCE_SQLITE is enabled, using SQLite database")
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return DatabaseType.SQLITE, f"sqlite:///{data_dir / 'solar_pv_lims.db'}"

    # Check for explicit DATABASE_URL (works on any platform)
    database_url = os.getenv("DATABASE_URL")

    # Railway uses POSTGRES_URL or DATABASE_URL
    if not database_url:
        database_url = os.getenv("POSTGRES_URL")

    # Railway also uses DATABASE_PRIVATE_URL for internal networking
    if not database_url:
        database_url = os.getenv("DATABASE_PRIVATE_URL")

    if database_url:
        # Handle Railway's postgres:// vs postgresql:// difference
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        if "postgresql" in database_url or "postgres" in database_url:
            logger.info(f"Using PostgreSQL database on {platform.value}")
            return DatabaseType.POSTGRESQL, database_url

    # Platform-specific fallbacks
    if platform == Platform.RAILWAY:
        # Railway should have DATABASE_URL set via the PostgreSQL plugin
        logger.warning("Railway detected but no DATABASE_URL found - using SQLite fallback")

    elif platform == Platform.REPLIT:
        # Replit has ephemeral storage - SQLite works but data may not persist
        logger.info("Replit detected - using SQLite (note: ephemeral storage)")

    elif platform == Platform.GENSPARK:
        # GenSpark configuration - check for their specific DB vars
        genspark_db = os.getenv("GENSPARK_DATABASE_URL")
        if genspark_db:
            if genspark_db.startswith("postgres://"):
                genspark_db = genspark_db.replace("postgres://", "postgresql://", 1)
            return DatabaseType.POSTGRESQL, genspark_db
        logger.info("GenSpark detected - using SQLite fallback")

    elif platform == Platform.STREAMLIT_CLOUD:
        # Streamlit Cloud uses secrets management
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'database' in st.secrets:
                db_url = st.secrets['database'].get('url', '')
                if db_url:
                    if db_url.startswith("postgres://"):
                        db_url = db_url.replace("postgres://", "postgresql://", 1)
                    if "postgresql" in db_url:
                        logger.info("Streamlit Cloud - using PostgreSQL from secrets")
                        return DatabaseType.POSTGRESQL, db_url
        except Exception as e:
            logger.debug(f"Streamlit secrets not available: {e}")

    # Default: SQLite database (universal fallback)
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{data_dir / 'solar_pv_lims.db'}"
    logger.info(f"Using SQLite database: {sqlite_url}")
    return DatabaseType.SQLITE, sqlite_url


def get_pool_config(platform: Platform, db_type: DatabaseType) -> Dict[str, Any]:
    """
    Get database pool configuration optimized for the platform.

    Args:
        platform: The deployment platform
        db_type: The database type

    Returns:
        Dictionary of pool configuration options
    """
    if db_type == DatabaseType.SQLITE:
        # SQLite doesn't need pooling in the traditional sense
        return {
            "poolclass": "StaticPool",
            "connect_args": {"check_same_thread": False}
        }

    # PostgreSQL pool configurations optimized per platform
    configs = {
        Platform.RAILWAY: {
            # Railway: Cost-optimized settings for $4.98 credits
            # Minimal connections to reduce memory usage
            "pool_size": 3,
            "max_overflow": 5,
            "pool_pre_ping": True,
            "pool_recycle": 1800,  # Recycle connections every 30 mins
            "pool_timeout": 30
        },
        Platform.REPLIT: {
            "pool_size": 2,
            "max_overflow": 3,
            "pool_pre_ping": True,
            "pool_recycle": 900
        },
        Platform.GENSPARK: {
            "pool_size": 3,
            "max_overflow": 5,
            "pool_pre_ping": True,
            "pool_recycle": 1800
        },
        Platform.STREAMLIT_CLOUD: {
            "pool_size": 3,
            "max_overflow": 7,
            "pool_pre_ping": True,
            "pool_recycle": 1800
        },
        Platform.LOCAL: {
            # Local development can use more resources
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600
        }
    }

    return configs.get(platform, configs[Platform.LOCAL])


def get_platform_config() -> PlatformConfig:
    """
    Get complete platform configuration.

    Returns:
        PlatformConfig with all settings for the current platform
    """
    platform = detect_platform()
    db_type, db_url = get_database_url(platform)
    pool_config = get_pool_config(platform, db_type)

    # Platform-specific features
    features = {
        Platform.RAILWAY: {
            "persistent_storage": True,
            "scheduled_tasks": True,
            "external_postgres": True,
            "custom_domains": True,
            "ssl_enabled": True,
            "environment_variables": True
        },
        Platform.REPLIT: {
            "persistent_storage": False,  # Ephemeral
            "scheduled_tasks": False,
            "external_postgres": True,
            "custom_domains": True,
            "ssl_enabled": True,
            "environment_variables": True
        },
        Platform.GENSPARK: {
            "persistent_storage": True,
            "scheduled_tasks": True,
            "external_postgres": True,
            "custom_domains": True,
            "ssl_enabled": True,
            "environment_variables": True
        },
        Platform.STREAMLIT_CLOUD: {
            "persistent_storage": False,  # Uses secrets only
            "scheduled_tasks": False,
            "external_postgres": True,
            "custom_domains": False,
            "ssl_enabled": True,
            "environment_variables": False  # Uses secrets
        },
        Platform.LOCAL: {
            "persistent_storage": True,
            "scheduled_tasks": True,
            "external_postgres": True,
            "custom_domains": False,
            "ssl_enabled": False,
            "environment_variables": True
        }
    }

    platform_features = features.get(platform, features[Platform.LOCAL])

    return PlatformConfig(
        platform=platform,
        database_type=db_type,
        database_url=db_url,
        is_production=platform not in (Platform.LOCAL,),
        supports_persistent_storage=platform_features["persistent_storage"],
        max_pool_size=pool_config.get("pool_size", 5),
        pool_overflow=pool_config.get("max_overflow", 10),
        pool_pre_ping=pool_config.get("pool_pre_ping", True),
        features=platform_features
    )


def get_platform_info() -> Dict[str, Any]:
    """
    Get human-readable platform information for debugging and display.

    Returns:
        Dictionary with platform details
    """
    config = get_platform_config()

    return {
        "platform": config.platform.value,
        "platform_display": config.platform.value.replace("_", " ").title(),
        "database_type": config.database_type.value,
        "is_production": config.is_production,
        "persistent_storage": config.supports_persistent_storage,
        "pool_size": config.max_pool_size,
        "features": config.features,
        # Mask the database URL for security
        "database_url_masked": _mask_db_url(config.database_url)
    }


def _mask_db_url(url: str) -> str:
    """Mask sensitive parts of database URL for display"""
    if "sqlite" in url:
        return url

    # Mask password in postgresql URLs
    import re
    masked = re.sub(r':([^:@]+)@', ':****@', url)
    return masked


# Rollback utilities
def enable_sqlite_fallback():
    """
    Enable SQLite fallback mode.
    Call this to force the application to use SQLite instead of PostgreSQL.
    """
    os.environ["FORCE_SQLITE"] = "1"
    logger.warning("SQLite fallback mode ENABLED - restart required")


def disable_sqlite_fallback():
    """
    Disable SQLite fallback mode.
    Returns to normal database detection.
    """
    if "FORCE_SQLITE" in os.environ:
        del os.environ["FORCE_SQLITE"]
    logger.info("SQLite fallback mode DISABLED - restart required")


def is_rollback_mode() -> bool:
    """Check if the application is in rollback (SQLite fallback) mode"""
    return os.getenv("FORCE_SQLITE", "").lower() in ("1", "true", "yes")


# Export key functions and classes
__all__ = [
    "Platform",
    "DatabaseType",
    "PlatformConfig",
    "detect_platform",
    "get_database_url",
    "get_platform_config",
    "get_platform_info",
    "enable_sqlite_fallback",
    "disable_sqlite_fallback",
    "is_rollback_mode"
]
