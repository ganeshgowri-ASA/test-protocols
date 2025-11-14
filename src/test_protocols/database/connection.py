"""Database connection management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from test_protocols.config import config
from test_protocols.logger import setup_logger
from test_protocols.models.schema import Base

logger = setup_logger(__name__)


class DatabaseConnection:
    """Database connection manager.

    Manages SQLAlchemy engine and session creation with proper
    configuration and connection pooling.
    """

    def __init__(self, database_url: str | None = None):
        """Initialize database connection.

        Args:
            database_url: Database URL (defaults to config value)
        """
        self.database_url = database_url or config.database.url
        self.engine: Engine | None = None
        self.session_factory: sessionmaker | None = None

        logger.info(f"Initializing database connection: {self._safe_url()}")

    def _safe_url(self) -> str:
        """Get database URL with password masked.

        Returns:
            str: Safe URL for logging
        """
        if "://" in self.database_url:
            parts = self.database_url.split("://")
            protocol = parts[0]
            rest = parts[1]
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***:***@{host}"
        return self.database_url

    def connect(self) -> None:
        """Establish database connection and create tables if needed."""
        if self.engine is not None:
            logger.warning("Database connection already established")
            return

        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=config.database.echo,
            pool_size=config.database.pool_size,
            pool_recycle=config.database.pool_recycle,
        )

        # Enable foreign keys for SQLite
        if self.database_url.startswith("sqlite"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

        logger.info("Database connection established and tables created")

    def disconnect(self) -> None:
        """Close database connection and dispose of engine."""
        if self.engine is None:
            logger.warning("No active database connection")
            return

        self.engine.dispose()
        self.engine = None
        self.session_factory = None

        logger.info("Database connection closed")

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            Session: SQLAlchemy session

        Raises:
            RuntimeError: If connection not established
        """
        if self.session_factory is None:
            raise RuntimeError(
                "Database connection not established. Call connect() first."
            )

        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Yields:
            Session: Database session

        Example:
            with db.session_scope() as session:
                session.add(obj)
                session.commit()
        """
        if self.session_factory is None:
            raise RuntimeError(
                "Database connection not established. Call connect() first."
            )

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check if database connection is healthy.

        Returns:
            bool: True if connection is healthy
        """
        if self.engine is None:
            return False

        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Global database connection instance
db = DatabaseConnection()
