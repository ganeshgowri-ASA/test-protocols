"""Logging configuration for the test protocols framework."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import yaml


def setup_logging(
    config_path: Optional[str] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        config_path: Path to config.yaml file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    # Load configuration if provided
    if config_path:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logging_config = config.get('logging', {})
            log_level = logging_config.get('level', log_level)
            log_file = logging_config.get('file_path', log_file)
            log_format = logging_config.get(
                'format',
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            max_bytes = logging_config.get('max_bytes', 10485760)
            backup_count = logging_config.get('backup_count', 5)
    else:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        max_bytes = 10485760
        backup_count = 5

    # Create logger
    logger = logging.getLogger('test_protocols')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logging()
