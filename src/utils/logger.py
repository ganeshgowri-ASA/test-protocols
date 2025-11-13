"""Logging configuration and utilities."""

import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional


def setup_logging(config_path: str = "config/logging.yaml", default_level: int = logging.INFO) -> None:
    """Setup logging configuration.

    Args:
        config_path: Path to logging configuration file
        default_level: Default logging level if config file not found
    """
    config_file = Path(config_path)

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            # Create logs directory if it doesn't exist
            Path('logs').mkdir(exist_ok=True)

            logging.config.dictConfig(config['logging'])
        except Exception as e:
            print(f"Error loading logging config: {e}")
            logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
