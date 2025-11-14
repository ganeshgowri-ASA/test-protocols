"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager singleton."""

    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file. If None, uses default path.
        """
        if config_path is None:
            config_path = os.path.join(
                Path(__file__).parent.parent, 'config', 'config.yaml'
            )

        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key (e.g., 'database.type')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()


def load_config(config_path: Optional[str] = None) -> None:
    """Load configuration from file.

    Args:
        config_path: Path to config file. If None, uses default path.
    """
    config = Config()
    config.load(config_path)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value.

    Args:
        key: Dot-separated configuration key
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    config = Config()
    if not config.all:
        load_config()
    return config.get(key, default)
