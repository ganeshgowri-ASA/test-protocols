"""
Application Settings and Configuration
"""

from pydantic import BaseSettings, Field
from typing import Optional, List
from pathlib import Path
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    app_name: str = "PV Testing Protocol Framework"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Database
    database_url: str = Field(
        default="sqlite:///./test_protocols.db",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # File Storage
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    temp_dir: Path = Field(default=Path("./temp"), env="TEMP_DIR")
    results_dir: Path = Field(default=Path("./results"), env="RESULTS_DIR")
    images_dir: Path = Field(default=Path("./images"), env="IMAGES_DIR")

    # Analysis
    max_image_size_mb: int = Field(default=50, env="MAX_IMAGE_SIZE_MB")
    default_defect_threshold: float = Field(default=0.15, env="DEFAULT_DEFECT_THRESHOLD")
    default_min_defect_area: float = Field(default=10.0, env="DEFAULT_MIN_DEFECT_AREA")

    # LIMS Integration
    lims_enabled: bool = Field(default=False, env="LIMS_ENABLED")
    lims_url: Optional[str] = Field(default=None, env="LIMS_URL")
    lims_api_key: Optional[str] = Field(default=None, env="LIMS_API_KEY")

    # QMS Integration
    qms_enabled: bool = Field(default=False, env="QMS_ENABLED")
    qms_url: Optional[str] = Field(default=None, env="QMS_URL")
    qms_api_key: Optional[str] = Field(default=None, env="QMS_API_KEY")

    # Security
    secret_key: str = Field(
        default="change-this-in-production",
        env="SECRET_KEY"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def create_directories(self):
        """Create required directories if they don't exist"""
        for directory in [self.data_dir, self.temp_dir, self.results_dir, self.images_dir]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None:
        _settings = Settings()
        _settings.create_directories()

    return _settings
