"""
Configuration Management for PV Testing Protocol Framework
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "PV Testing Protocol Framework"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./pv_testing.db"
    DATABASE_ECHO: bool = False

    # Streamlit
    STREAMLIT_PORT: int = 8501
    STREAMLIT_SERVER_ADDRESS: str = "0.0.0.0"

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    PROTOCOLS_DIR: Path = BASE_DIR / "protocols" / "templates"
    REPORTS_DIR: Path = BASE_DIR / "reports" / "generated"
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Protocol Settings
    MAX_PROTOCOL_VERSION: int = 100
    PROTOCOL_RETENTION_DAYS: int = 365

    # Measurement Settings
    DEFAULT_UNCERTAINTY_LEVEL: float = 0.95  # 95% confidence
    TEMPERATURE_STC: float = 25.0  # °C
    IRRADIANCE_STC: float = 1000.0  # W/m²
    SPECTRUM_STC: str = "AM1.5G"

    # Report Settings
    REPORT_FORMAT: str = "PDF"
    REPORT_LOGO_PATH: Optional[str] = None
    REPORT_COMPANY_NAME: str = "PV Testing Laboratory"

    # Integration Settings
    LIMS_API_URL: Optional[str] = None
    LIMS_API_KEY: Optional[str] = None
    QMS_API_URL: Optional[str] = None
    QMS_API_KEY: Optional[str] = None
    PM_DASHBOARD_URL: Optional[str] = None
    PM_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.PROTOCOLS_DIR, self.REPORTS_DIR, self.DATA_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
