"""Configuration management for test protocols application."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""

    url: str
    echo: bool = False
    pool_size: int = 10
    pool_recycle: int = 3600


@dataclass
class AppConfig:
    """Application configuration."""

    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig
    report_output_dir: Path
    image_storage_dir: Path
    lims_api_url: Optional[str] = None
    lims_api_key: Optional[str] = None
    qms_api_url: Optional[str] = None
    qms_api_key: Optional[str] = None
    chamber_ip: Optional[str] = None
    chamber_port: Optional[int] = None
    chamber_protocol: str = "modbus"
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    notification_email: Optional[str] = None


def load_config() -> AppConfig:
    """Load configuration from environment variables.

    Returns:
        AppConfig: Application configuration object
    """
    database_url = os.getenv("DATABASE_URL", "sqlite:///test_protocols.db")
    report_dir = Path(os.getenv("REPORT_OUTPUT_DIR", "./reports"))
    image_dir = Path(os.getenv("IMAGE_STORAGE_DIR", "./images"))

    # Create directories if they don't exist
    report_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        debug=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database=DatabaseConfig(
            url=database_url,
            echo=os.getenv("DB_ECHO", "False").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        ),
        report_output_dir=report_dir,
        image_storage_dir=image_dir,
        lims_api_url=os.getenv("LIMS_API_URL"),
        lims_api_key=os.getenv("LIMS_API_KEY"),
        qms_api_url=os.getenv("QMS_API_URL"),
        qms_api_key=os.getenv("QMS_API_KEY"),
        chamber_ip=os.getenv("CHAMBER_IP"),
        chamber_port=int(os.getenv("CHAMBER_PORT", "502")),
        chamber_protocol=os.getenv("CHAMBER_PROTOCOL", "modbus"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        notification_email=os.getenv("NOTIFICATION_EMAIL"),
    )


# Global configuration instance
config = load_config()
