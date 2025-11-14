"""Database connection management."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and sessions."""

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize the DatabaseManager.

        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to echo SQL statements
        """
        self.database_url = database_url
        self.echo = echo

        # Special handling for SQLite in-memory databases
        if database_url == "sqlite:///:memory:" or ":memory:" in database_url:
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=echo,
            )
        else:
            self.engine = create_engine(database_url, echo=echo)

        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

        logger.info(f"DatabaseManager initialized with URL: {database_url}")

    def init_db(self):
        """Create all tables."""
        from .models import Base

        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def drop_all(self):
        """Drop all tables (use with caution!)."""
        from .models import Base

        Base.metadata.drop_all(self.engine)
        logger.warning("All database tables dropped")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Provide a database session context manager.

        Yields:
            SQLAlchemy session

        Example:
            with db_manager.get_session() as session:
                session.add(obj)
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """
        Get a database session directly (caller is responsible for closing).

        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

    def close(self):
        """Close the database engine."""
        self.engine.dispose()
        logger.info("Database connection closed")


# Singleton instance (optional)
_db_manager_instance = None


def get_db_manager(database_url: str = None, echo: bool = False) -> DatabaseManager:
    """
    Get or create DatabaseManager singleton instance.

    Args:
        database_url: SQLAlchemy database URL
        echo: Whether to echo SQL statements

    Returns:
        DatabaseManager instance
    """
    global _db_manager_instance

    if _db_manager_instance is None:
        if database_url is None:
            # Default to SQLite in-memory database
            database_url = "sqlite:///test_protocols.db"

        _db_manager_instance = DatabaseManager(database_url, echo)

    return _db_manager_instance


def reset_db_manager():
    """Reset the singleton instance (useful for testing)."""
    global _db_manager_instance
    if _db_manager_instance is not None:
        _db_manager_instance.close()
        _db_manager_instance = None
