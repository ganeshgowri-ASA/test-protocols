"""Logging configuration for test protocols application."""

import logging
import sys
from pathlib import Path
from typing import Optional

from test_protocols.config import config


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """Set up logger with console and file handlers.

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Optional log level (defaults to config.log_level)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    log_level = getattr(logging, level or config.log_level)
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# Default application logger
app_logger = setup_logger("test_protocols", log_file=Path("logs/app.log"))
