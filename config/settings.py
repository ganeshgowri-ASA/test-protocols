"""Application configuration and settings."""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "sqlite:///./test_protocols.db"

    # LIMS Integration
    lims_api_url: Optional[str] = None
    lims_api_key: Optional[str] = None

    # QMS Integration
    qms_api_url: Optional[str] = None
    qms_api_key: Optional[str] = None

    # Streamlit Configuration
    streamlit_theme: str = "light"
    streamlit_port: int = 8501

    # Application Settings
    debug: bool = True
    log_level: str = "INFO"

    # Protocol Settings
    protocol_base_path: Path = Path(__file__).parent.parent / "protocols"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
