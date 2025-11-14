"""Logging utilities for test protocols framework."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(config_path: Optional[str] = None) -> None:
    """Setup logging configuration.

    Args:
        config_path: Path to logging config file. If None, uses default path.
    """
    if config_path is None:
        config_path = os.path.join(
            Path(__file__).parent.parent, 'config', 'logging.yaml'
        )

    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Load logging configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
