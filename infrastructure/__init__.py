"""
Enterprise Infrastructure Module
================================
Production-ready infrastructure components for Railway deployment.

Modules:
    - database: Advanced database layer with connection pooling
    - logging_config: Structured logging with multiple outputs
    - monitoring: Health checks, metrics, and performance monitoring
    - security: Authentication, authorization, and rate limiting
    - error_handling: Centralized error handling and recovery
    - cache: Caching layer for performance optimization
"""

from infrastructure.database import (
    DatabaseManager,
    get_db_manager,
    db_session,
    connection_health_check
)

from infrastructure.logging_config import (
    StructuredLogger,
    get_logger,
    log_request,
    log_error
)

from infrastructure.monitoring import (
    HealthChecker,
    MetricsCollector,
    PerformanceMonitor
)

from infrastructure.security import (
    RateLimiter,
    AuthenticationManager,
    SecureSession
)

from infrastructure.error_handling import (
    ErrorHandler,
    handle_exception,
    ApplicationError
)

__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'db_session',
    'connection_health_check',
    'StructuredLogger',
    'get_logger',
    'log_request',
    'log_error',
    'HealthChecker',
    'MetricsCollector',
    'PerformanceMonitor',
    'RateLimiter',
    'AuthenticationManager',
    'SecureSession',
    'ErrorHandler',
    'handle_exception',
    'ApplicationError'
]

__version__ = '1.0.0'
