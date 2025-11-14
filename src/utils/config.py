"""Configuration management utilities."""

import os
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file based on environment.

    Args:
        env: Environment name (dev, test, prod). If None, reads from APP_ENV or defaults to 'dev'

    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    load_dotenv()

    # Determine environment
    if env is None:
        env = os.getenv('APP_ENV', 'dev')

    # Load configuration file
    config_file = f'config/{env}.yaml'

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        # Fall back to development config
        with open('config/dev.yaml', 'r') as f:
            config = yaml.safe_load(f)

    # Override with environment variables
    if 'DATABASE_URL' in os.environ:
        config.setdefault('database', {})['url'] = os.environ['DATABASE_URL']

    if 'LOG_LEVEL' in os.environ:
        config.setdefault('logging', {})['level'] = os.environ['LOG_LEVEL']

    return config


# Global configuration cache
_config_cache: Optional[Dict[str, Any]] = None


def get_config() -> Dict[str, Any]:
    """Get cached configuration.

    Returns:
        Configuration dictionary
    """
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config()
    return _config_cache


def reload_config(env: Optional[str] = None) -> Dict[str, Any]:
    """Reload configuration from file.

    Args:
        env: Environment name

    Returns:
        New configuration dictionary
    """
    global _config_cache
    _config_cache = load_config(env)
    return _config_cache
