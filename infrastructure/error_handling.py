"""
Centralized Error Handling for Railway Production Deployment
=============================================================
Enterprise-grade error handling with recovery, logging, and alerting.
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Type, Callable, List
from functools import wraps
from enum import Enum
import json


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, auto-recoverable
    MEDIUM = "medium"     # Noticeable issues, may need attention
    HIGH = "high"         # Significant issues, requires attention
    CRITICAL = "critical" # System-breaking issues, immediate action needed


class ErrorCategory(Enum):
    """Error categories for classification"""
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class ApplicationError(Exception):
    """
    Base application error with enhanced metadata.

    All custom errors should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        code: str = None,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
        recoverable: bool = True,
        user_message: str = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "INTERNAL_ERROR"
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.user_message = user_message or "An error occurred. Please try again."
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/response"""
        return {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "user_message": self.user_message,
            "timestamp": self.timestamp.isoformat()
        }

    def to_response(self) -> Dict[str, Any]:
        """Convert to safe response for clients"""
        return {
            "error": {
                "code": self.code,
                "message": self.user_message,
                "recoverable": self.recoverable
            }
        }


# Specific error types
class DatabaseError(ApplicationError):
    """Database-related errors"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code=kwargs.pop("code", "DATABASE_ERROR"),
            category=ErrorCategory.DATABASE,
            severity=kwargs.pop("severity", ErrorSeverity.HIGH),
            user_message=kwargs.pop("user_message", "A database error occurred."),
            **kwargs
        )


class ValidationError(ApplicationError):
    """Input validation errors"""

    def __init__(self, message: str, field: str = None, **kwargs):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field

        super().__init__(
            message=message,
            code=kwargs.pop("code", "VALIDATION_ERROR"),
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            user_message=kwargs.pop("user_message", message),
            **kwargs
        )


class AuthenticationError(ApplicationError):
    """Authentication failures"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            code=kwargs.pop("code", "AUTH_ERROR"),
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            user_message=kwargs.pop("user_message", "Invalid credentials."),
            **kwargs
        )


class AuthorizationError(ApplicationError):
    """Authorization/permission errors"""

    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            code=kwargs.pop("code", "FORBIDDEN"),
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            user_message=kwargs.pop("user_message", "You don't have permission to perform this action."),
            **kwargs
        )


class NotFoundError(ApplicationError):
    """Resource not found errors"""

    def __init__(self, resource: str, identifier: Any = None, **kwargs):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"

        super().__init__(
            message=message,
            code=kwargs.pop("code", "NOT_FOUND"),
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.LOW,
            details={"resource": resource, "identifier": str(identifier) if identifier else None},
            user_message=kwargs.pop("user_message", message),
            **kwargs
        )


class ExternalServiceError(ApplicationError):
    """External service/API errors"""

    def __init__(self, service: str, message: str = None, **kwargs):
        super().__init__(
            message=message or f"Error communicating with {service}",
            code=kwargs.pop("code", "EXTERNAL_SERVICE_ERROR"),
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=kwargs.pop("severity", ErrorSeverity.HIGH),
            details={"service": service, **kwargs.pop("details", {})},
            user_message=kwargs.pop("user_message", "A service is temporarily unavailable. Please try again later."),
            **kwargs
        )


class RateLimitError(ApplicationError):
    """Rate limit exceeded errors"""

    def __init__(self, retry_after: int = None, **kwargs):
        details = kwargs.pop("details", {})
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMIT_EXCEEDED",
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.LOW,
            details=details,
            user_message=f"Too many requests. Please wait {retry_after} seconds." if retry_after else "Too many requests. Please try again later.",
            **kwargs
        )


class ConfigurationError(ApplicationError):
    """Configuration/setup errors"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code=kwargs.pop("code", "CONFIGURATION_ERROR"),
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            recoverable=False,
            user_message=kwargs.pop("user_message", "The system is misconfigured. Please contact support."),
            **kwargs
        )


class ErrorHandler:
    """
    Centralized error handler with logging and recovery.

    Features:
    - Error classification and logging
    - Recovery strategy registration
    - Error aggregation for alerting
    - Safe error responses
    """

    def __init__(self):
        self._recovery_strategies: Dict[str, Callable] = {}
        self._error_hooks: List[Callable] = []
        self._error_counts: Dict[str, int] = {}
        self._recent_errors: List[Dict] = []
        self._max_recent_errors = 100

    def register_recovery(self, error_code: str, strategy: Callable):
        """Register a recovery strategy for an error code"""
        self._recovery_strategies[error_code] = strategy

    def register_hook(self, hook: Callable):
        """Register an error hook (for alerting, logging, etc.)"""
        self._error_hooks.append(hook)

    def handle(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        attempt_recovery: bool = True
    ) -> Dict[str, Any]:
        """
        Handle an error with logging and optional recovery.

        Args:
            error: The exception to handle
            context: Additional context about the error
            attempt_recovery: Whether to attempt recovery

        Returns:
            Response dictionary safe for clients
        """
        # Convert to ApplicationError if needed
        if isinstance(error, ApplicationError):
            app_error = error
        else:
            app_error = ApplicationError(
                message=str(error),
                category=self._classify_error(error),
                details={"original_type": type(error).__name__}
            )

        # Log the error
        self._log_error(app_error, context)

        # Track error counts
        self._error_counts[app_error.code] = self._error_counts.get(app_error.code, 0) + 1

        # Store in recent errors
        self._recent_errors.append({
            **app_error.to_dict(),
            "context": context
        })
        if len(self._recent_errors) > self._max_recent_errors:
            self._recent_errors.pop(0)

        # Call error hooks
        for hook in self._error_hooks:
            try:
                hook(app_error, context)
            except Exception:
                pass  # Don't let hook failures cause more errors

        # Attempt recovery if applicable
        if attempt_recovery and app_error.recoverable:
            recovery_result = self._attempt_recovery(app_error, context)
            if recovery_result:
                return recovery_result

        return app_error.to_response()

    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify a generic exception into a category"""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()

        if "database" in error_type or "sql" in error_type:
            return ErrorCategory.DATABASE
        elif "auth" in error_type:
            return ErrorCategory.AUTHENTICATION
        elif "permission" in error_type or "forbidden" in error_type:
            return ErrorCategory.AUTHORIZATION
        elif "validation" in error_type or "invalid" in error_message:
            return ErrorCategory.VALIDATION
        elif "connection" in error_type or "timeout" in error_type:
            return ErrorCategory.NETWORK
        elif "config" in error_type:
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.UNKNOWN

    def _log_error(self, error: ApplicationError, context: Dict = None):
        """Log error with full details"""
        from infrastructure.logging_config import get_logger, log_error

        logger = get_logger("errors")

        log_data = {
            **error.to_dict(),
            "context": context,
            "traceback": error.traceback
        }

        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"[{error.code}] {error.message}", extra={"extra_data": log_data})
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"[{error.code}] {error.message}", extra={"extra_data": log_data})
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"[{error.code}] {error.message}", extra={"extra_data": log_data})
        else:
            logger.info(f"[{error.code}] {error.message}", extra={"extra_data": log_data})

    def _attempt_recovery(
        self,
        error: ApplicationError,
        context: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """Attempt to recover from an error"""
        strategy = self._recovery_strategies.get(error.code)

        if strategy:
            try:
                result = strategy(error, context)
                if result:
                    return {"recovered": True, "result": result}
            except Exception as recovery_error:
                # Recovery failed, log it
                from infrastructure.logging_config import get_logger
                logger = get_logger("errors")
                logger.error(f"Recovery failed for {error.code}: {recovery_error}")

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": sum(self._error_counts.values()),
            "errors_by_code": dict(self._error_counts),
            "recent_error_count": len(self._recent_errors)
        }

    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Get recent errors"""
        return self._recent_errors[-limit:]

    def reset_stats(self):
        """Reset error statistics"""
        self._error_counts.clear()
        self._recent_errors.clear()


# Global error handler instance
error_handler = ErrorHandler()


# Exception handling decorator
def handle_exception(
    default_message: str = "An error occurred",
    reraise: bool = False,
    error_type: Type[ApplicationError] = ApplicationError
):
    """
    Decorator for exception handling.

    Args:
        default_message: Message if exception doesn't have one
        reraise: Whether to reraise after handling
        error_type: Type of ApplicationError to convert to
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                if reraise:
                    raise
                return error_handler.handle(sys.exc_info()[1])
            except Exception as e:
                app_error = error_type(
                    message=str(e) or default_message,
                    details={"function": func.__name__}
                )
                if reraise:
                    raise app_error from e
                return error_handler.handle(app_error)
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, **kwargs):
    """
    Safely execute a function, returning default on error.

    Args:
        func: Function to execute
        *args: Function arguments
        default: Default value on error
        **kwargs: Function keyword arguments

    Returns:
        Function result or default on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle(e, {"function": func.__name__})
        return default


# Context manager for error handling
class ErrorContext:
    """Context manager for error handling with cleanup"""

    def __init__(
        self,
        context_name: str,
        cleanup_func: Callable = None,
        suppress: bool = False
    ):
        self.context_name = context_name
        self.cleanup_func = cleanup_func
        self.suppress = suppress
        self.error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.error = exc_val
            error_handler.handle(
                exc_val,
                context={"context_name": self.context_name}
            )

        if self.cleanup_func:
            try:
                self.cleanup_func()
            except Exception as cleanup_error:
                error_handler.handle(
                    cleanup_error,
                    context={"cleanup_for": self.context_name}
                )

        return self.suppress


# Error response utilities
def create_error_response(
    message: str,
    code: str = "ERROR",
    status: int = 500,
    details: Dict = None
) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        },
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }


def format_error_for_user(error: Exception) -> str:
    """Format an error message suitable for display to users"""
    if isinstance(error, ApplicationError):
        return error.user_message

    # Generic error messages for common exceptions
    error_type = type(error).__name__

    friendly_messages = {
        "ConnectionError": "Unable to connect to the server. Please check your internet connection.",
        "TimeoutError": "The request timed out. Please try again.",
        "ValueError": "Invalid input provided. Please check your data.",
        "KeyError": "Required data is missing. Please try again.",
        "FileNotFoundError": "The requested file could not be found.",
        "PermissionError": "You don't have permission to perform this action.",
    }

    return friendly_messages.get(
        error_type,
        "An unexpected error occurred. Please try again or contact support."
    )


# Streamlit error display
def display_error_streamlit(error: Exception, show_details: bool = False):
    """Display error in Streamlit"""
    import streamlit as st

    user_message = format_error_for_user(error)
    st.error(user_message)

    if show_details and isinstance(error, ApplicationError):
        with st.expander("Error Details"):
            st.json(error.to_dict())
