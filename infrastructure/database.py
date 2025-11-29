"""
Advanced Database Layer for Railway Production Deployment
==========================================================
Enterprise-grade database management with connection pooling,
query optimization, and horizontal scaling support.
"""

import os
import time
import threading
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any, List
from functools import wraps
from datetime import datetime, timedelta

from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Import Base from config to avoid duplicate table definitions
from config.database import Base


class DatabaseConfig:
    """Database configuration with Railway environment support"""

    def __init__(self):
        # Railway-specific environment variables
        self.database_url = os.getenv(
            "DATABASE_URL",
            os.getenv("DATABASE_PRIVATE_URL", "sqlite:///./data/solar_pv_lims.db")
        )

        # Fix for Railway PostgreSQL URL format
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace(
                "postgres://", "postgresql://", 1
            )

        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

        # Query settings
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.slow_query_threshold = float(os.getenv("DB_SLOW_QUERY_MS", "1000"))

        # Retry settings
        self.max_retries = int(os.getenv("DB_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("DB_RETRY_DELAY", "1.0"))

    @property
    def is_postgres(self) -> bool:
        return "postgresql" in self.database_url

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


class QueryMetrics:
    """Thread-safe query performance metrics collector"""

    def __init__(self):
        self._lock = threading.Lock()
        self._query_count = 0
        self._total_time = 0.0
        self._slow_queries: List[Dict] = []
        self._errors: List[Dict] = []
        self._start_time = datetime.utcnow()

    def record_query(self, duration_ms: float, statement: str = None):
        """Record a query execution"""
        with self._lock:
            self._query_count += 1
            self._total_time += duration_ms

            # Track slow queries (> 1000ms)
            if duration_ms > 1000 and statement:
                self._slow_queries.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "statement": statement[:500]  # Truncate for safety
                })
                # Keep only last 100 slow queries
                if len(self._slow_queries) > 100:
                    self._slow_queries.pop(0)

    def record_error(self, error: str, statement: str = None):
        """Record a query error"""
        with self._lock:
            self._errors.append({
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(error)[:500],
                "statement": statement[:200] if statement else None
            })
            # Keep only last 50 errors
            if len(self._errors) > 50:
                self._errors.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self._lock:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()
            avg_time = self._total_time / self._query_count if self._query_count > 0 else 0

            return {
                "total_queries": self._query_count,
                "avg_query_time_ms": round(avg_time, 2),
                "queries_per_second": round(self._query_count / uptime, 2) if uptime > 0 else 0,
                "slow_query_count": len(self._slow_queries),
                "error_count": len(self._errors),
                "uptime_seconds": round(uptime, 2)
            }

    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self._query_count = 0
            self._total_time = 0.0
            self._slow_queries.clear()
            self._errors.clear()
            self._start_time = datetime.utcnow()


class DatabaseManager:
    """
    Enterprise Database Manager

    Features:
    - Connection pooling with automatic recycling
    - Query performance monitoring
    - Automatic retry with exponential backoff
    - Health checking and connection validation
    - Thread-safe session management
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for database manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config = DatabaseConfig()
        self.metrics = QueryMetrics()
        self._engine: Optional[Engine] = None
        self._session_factory = None
        self._scoped_session = None
        self._initialized = True

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with production settings"""

        if self.config.is_sqlite:
            # SQLite configuration (for development/testing)
            engine = create_engine(
                self.config.database_url,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,  # SQLite doesn't support connection pooling
                echo=self.config.echo
            )

            # Enable foreign keys and WAL mode for SQLite
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
                cursor.close()
        else:
            # PostgreSQL configuration (production)
            engine = create_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                echo=self.config.echo,
                # PostgreSQL-specific settings
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "solar_pv_lims",
                    "options": "-c statement_timeout=30000"  # 30 second query timeout
                } if self.config.is_postgres else {}
            )

        # Query timing event listener
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            start_time = conn.info['query_start_time'].pop()
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_query(duration_ms, statement)

        @event.listens_for(engine, "handle_error")
        def handle_error(exception_context):
            self.metrics.record_error(
                str(exception_context.original_exception),
                str(exception_context.statement)[:200] if exception_context.statement else None
            )

        return engine

    @property
    def engine(self) -> Engine:
        """Get or create database engine"""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self):
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False
            )
        return self._session_factory

    @property
    def scoped_session(self):
        """Get or create thread-local scoped session"""
        if self._scoped_session is None:
            self._scoped_session = scoped_session(self.session_factory)
        return self._scoped_session

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic commit/rollback.

        Usage:
            with db_manager.get_session() as session:
                session.query(Model).all()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_with_retry(
        self,
        func,
        *args,
        max_retries: int = None,
        retry_delay: float = None,
        **kwargs
    ):
        """
        Execute a database operation with automatic retry.

        Args:
            func: Function to execute
            max_retries: Maximum retry attempts (default from config)
            retry_delay: Delay between retries in seconds

        Returns:
            Result of the function

        Raises:
            Last exception if all retries fail
        """
        max_retries = max_retries or self.config.max_retries
        retry_delay = retry_delay or self.config.retry_delay

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                last_exception = e
                if attempt < max_retries:
                    # Exponential backoff
                    sleep_time = retry_delay * (2 ** attempt)
                    time.sleep(sleep_time)

                    # Try to reconnect
                    self._engine.dispose()
                    self._engine = None
            except SQLAlchemyError:
                raise

        raise last_exception

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.

        Returns:
            Dictionary with health status and metrics
        """
        try:
            start_time = time.time()

            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            latency_ms = (time.time() - start_time) * 1000

            # Get connection pool stats
            pool_status = {}
            if hasattr(self.engine.pool, 'status'):
                pool_status = {
                    "pool_size": self.engine.pool.size(),
                    "checked_in": self.engine.pool.checkedin(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                    "invalidated": self.engine.pool.invalidated()
                }

            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "database_type": "postgresql" if self.config.is_postgres else "sqlite",
                "pool": pool_status,
                "metrics": self.metrics.get_stats()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self.metrics.get_stats()
            }

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not hasattr(self.engine.pool, 'status'):
            return {"type": "sqlite", "pooling": False}

        return {
            "type": "postgresql",
            "pooling": True,
            "size": self.engine.pool.size(),
            "checked_in": self.engine.pool.checkedin(),
            "checked_out": self.engine.pool.checkedout(),
            "overflow": self.engine.pool.overflow(),
            "invalidated": self.engine.pool.invalidated()
        }

    def dispose(self):
        """Dispose of the connection pool"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
        if self._scoped_session:
            self._scoped_session.remove()
            self._scoped_session = None
        self._session_factory = None


# Convenience functions
def get_db_manager() -> DatabaseManager:
    """Get the singleton database manager instance"""
    return DatabaseManager()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Convenience context manager for database sessions"""
    with get_db_manager().get_session() as session:
        yield session


def connection_health_check() -> Dict[str, Any]:
    """Convenience function for health checks"""
    return get_db_manager().health_check()


def with_db_retry(max_retries: int = 3, retry_delay: float = 1.0):
    """
    Decorator for database operations with automatic retry.

    Usage:
        @with_db_retry(max_retries=3)
        def my_db_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return get_db_manager().execute_with_retry(
                func, *args,
                max_retries=max_retries,
                retry_delay=retry_delay,
                **kwargs
            )
        return wrapper
    return decorator


# Query optimization utilities
class QueryOptimizer:
    """Query optimization utilities for large datasets"""

    @staticmethod
    def paginate(query, page: int = 1, per_page: int = 50):
        """Add pagination to a query"""
        return query.offset((page - 1) * per_page).limit(per_page)

    @staticmethod
    def batch_insert(session: Session, objects: list, batch_size: int = 1000):
        """Insert objects in batches for better performance"""
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            session.bulk_save_objects(batch)
            session.flush()

    @staticmethod
    def stream_results(query, batch_size: int = 1000):
        """Stream large result sets to avoid memory issues"""
        return query.yield_per(batch_size)
