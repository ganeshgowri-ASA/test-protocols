"""
Structured Logging Configuration for Railway Production Deployment
===================================================================
Enterprise-grade logging with structured output, multiple handlers,
and integration with Railway's logging infrastructure.
"""

import os
import sys
import json
import logging
import threading
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
from pathlib import Path
import uuid


# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class LogConfig:
    """Logging configuration from environment"""

    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv("LOG_FORMAT", "json")  # json or text
        self.log_file = os.getenv("LOG_FILE", None)
        self.enable_request_logging = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"
        self.enable_query_logging = os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true"
        self.service_name = os.getenv("RAILWAY_SERVICE_NAME", "solar-pv-lims")
        self.environment = os.getenv("RAILWAY_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
        self.deployment_id = os.getenv("RAILWAY_DEPLOYMENT_ID", "local")

        # Sensitive fields to mask in logs
        self.sensitive_fields = [
            "password", "token", "secret", "api_key", "apikey",
            "authorization", "auth", "credential", "private_key"
        ]


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def __init__(self, config: LogConfig):
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.config.service_name,
            "environment": self.config.environment,
            "deployment_id": self.config.deployment_id
        }

        # Add source location
        log_data["source"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName
        }

        # Add thread info
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self._format_traceback(record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data["extra"] = self._mask_sensitive(record.extra_data)

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id

        return json.dumps(log_data, default=str)

    def _format_traceback(self, exc_info) -> Optional[str]:
        if exc_info and exc_info[2]:
            return ''.join(traceback.format_exception(*exc_info))
        return None

    def _mask_sensitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in log data"""
        if not isinstance(data, dict):
            return data

        masked = {}
        for key, value in data.items():
            if any(field in key.lower() for field in self.config.sensitive_fields):
                masked[key] = "***REDACTED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive(value)
            else:
                masked[key] = value
        return masked


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development"""

    def __init__(self, config: LogConfig):
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.config = config


class StructuredLogger:
    """
    Enterprise-grade structured logger.

    Features:
    - JSON structured logging for production
    - Automatic sensitive data masking
    - Request context tracking
    - Performance metrics
    - Multiple output handlers
    """

    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()
    _config: Optional[LogConfig] = None
    _request_context = threading.local()

    @classmethod
    def get_config(cls) -> LogConfig:
        if cls._config is None:
            cls._config = LogConfig()
        return cls._config

    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name (default: root logger)

        Returns:
            Configured logger instance
        """
        name = name or "solar_pv_lims"

        with cls._lock:
            if name not in cls._loggers:
                cls._loggers[name] = cls._create_logger(name)
            return cls._loggers[name]

    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create and configure a new logger"""
        config = cls.get_config()

        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVELS.get(config.log_level, logging.INFO))
        logger.handlers.clear()

        # Console handler (stdout for Railway)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(config.log_level, logging.INFO))

        # Choose formatter based on config
        if config.log_format == "json":
            formatter = JSONFormatter(config)
        else:
            formatter = TextFormatter(config)

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if config.log_file:
            log_path = Path(config.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                config.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(LOG_LEVELS.get(config.log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False
        return logger

    @classmethod
    def set_request_context(cls, request_id: str = None, user_id: str = None, **kwargs):
        """Set request context for the current thread"""
        cls._request_context.request_id = request_id or str(uuid.uuid4())
        cls._request_context.user_id = user_id
        cls._request_context.extra = kwargs

    @classmethod
    def clear_request_context(cls):
        """Clear request context for the current thread"""
        if hasattr(cls._request_context, 'request_id'):
            del cls._request_context.request_id
        if hasattr(cls._request_context, 'user_id'):
            del cls._request_context.user_id
        if hasattr(cls._request_context, 'extra'):
            del cls._request_context.extra

    @classmethod
    def _add_context(cls, record: logging.LogRecord):
        """Add request context to log record"""
        if hasattr(cls._request_context, 'request_id'):
            record.request_id = cls._request_context.request_id
        if hasattr(cls._request_context, 'user_id'):
            record.user_id = cls._request_context.user_id


# Convenience functions
def get_logger(name: str = None) -> logging.Logger:
    """Get a configured logger instance"""
    return StructuredLogger.get_logger(name)


def log_request(method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """Log an HTTP request"""
    logger = get_logger("requests")

    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **kwargs
    }

    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "", 0,
        f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
        None, None
    )
    record.extra_data = log_data
    logger.handle(record)


def log_error(error: Exception, context: str = None, **kwargs):
    """Log an error with full context"""
    logger = get_logger("errors")

    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        **kwargs
    }

    logger.error(
        f"{context}: {error}" if context else str(error),
        exc_info=True,
        extra={"extra_data": log_data}
    )


def log_db_query(query: str, duration_ms: float, success: bool = True, **kwargs):
    """Log a database query"""
    logger = get_logger("database")

    log_data = {
        "query": query[:500],  # Truncate long queries
        "duration_ms": round(duration_ms, 2),
        "success": success,
        **kwargs
    }

    level = logging.DEBUG if success else logging.ERROR
    record = logger.makeRecord(
        logger.name,
        level,
        "", 0,
        f"Query executed in {duration_ms:.2f}ms",
        None, None
    )
    record.extra_data = log_data
    logger.handle(record)


def log_performance(operation: str, duration_ms: float, **kwargs):
    """Log performance metrics"""
    logger = get_logger("performance")

    log_data = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        **kwargs
    }

    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "", 0,
        f"{operation} completed in {duration_ms:.2f}ms",
        None, None
    )
    record.extra_data = log_data
    logger.handle(record)


def log_security_event(event_type: str, success: bool, **kwargs):
    """Log security-related events"""
    logger = get_logger("security")

    log_data = {
        "event_type": event_type,
        "success": success,
        **kwargs
    }

    level = logging.INFO if success else logging.WARNING
    record = logger.makeRecord(
        logger.name,
        level,
        "", 0,
        f"Security event: {event_type} - {'success' if success else 'failed'}",
        None, None
    )
    record.extra_data = log_data
    logger.handle(record)


# Decorators
def log_function_call(logger_name: str = None):
    """Decorator to log function calls with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start_time = datetime.utcnow()

            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                logger.debug(
                    f"{func.__name__} completed in {duration:.2f}ms",
                    extra={"extra_data": {
                        "function": func.__name__,
                        "duration_ms": round(duration, 2),
                        "success": True
                    }}
                )
                return result

            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                logger.error(
                    f"{func.__name__} failed after {duration:.2f}ms: {e}",
                    exc_info=True,
                    extra={"extra_data": {
                        "function": func.__name__,
                        "duration_ms": round(duration, 2),
                        "success": False,
                        "error": str(e)
                    }}
                )
                raise
        return wrapper
    return decorator


# Audit logging
class AuditLogger:
    """Specialized logger for audit trail"""

    def __init__(self):
        self.logger = get_logger("audit")

    def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: Any,
        user_id: str = None,
        old_values: Dict = None,
        new_values: Dict = None,
        **kwargs
    ):
        """Log an auditable action"""
        log_data = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "user_id": user_id,
            "old_values": old_values,
            "new_values": new_values,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }

        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "", 0,
            f"Audit: {action} on {entity_type}:{entity_id}",
            None, None
        )
        record.extra_data = log_data
        self.logger.handle(record)


# Global audit logger instance
audit_logger = AuditLogger()
