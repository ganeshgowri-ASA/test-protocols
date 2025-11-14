"""Logging configuration for the test protocols framework."""

import logging
import os
from typing import Optional
from src.utils.config import get_config


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration.

    Args:
        name: Logger name. If None, returns root logger.

    Returns:
        Configured logger
    """
    config = get_config()
    log_config = config.get('logging', {})

    # Get or create logger
    logger = logging.getLogger(name)

    # Set logging level
    level_str = log_config.get('level', 'INFO')
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formatter
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (if configured)
    log_file = log_config.get('file')
    if log_file:
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return setup_logging(name)
