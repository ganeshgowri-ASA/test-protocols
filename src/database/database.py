"""
Database Connection and Session Management

Provides database connection setup and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Optional

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the DatabaseManager.

        Args:
            database_url: SQLAlchemy database URL.
                         If None, uses SQLite in project root.
        """
        if database_url is None:
            # Default to SQLite in project root
            db_path = Path(__file__).parent.parent.parent / "data" / "test_protocols.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{db_path}"

        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.scoped_session_factory = None

    def initialize(self, echo: bool = False):
        """
        Initialize the database engine and session factory.

        Args:
            echo: If True, log all SQL statements
        """
        logger.info(f"Initializing database connection: {self.database_url}")

        # Create engine
        if self.database_url.startswith("sqlite"):
            # SQLite specific settings
            self.engine = create_engine(
                self.database_url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(
                self.database_url,
                echo=echo,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )

        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.scoped_session_factory = scoped_session(self.session_factory)

        logger.info("Database connection initialized")

    def create_tables(self):
        """Create all tables in the database."""
        logger.info("Creating database tables")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Drop all tables from the database."""
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(self.engine)
        logger.info("Database tables dropped")

    def get_session(self):
        """
        Get a new database session.

        Returns:
            SQLAlchemy session
        """
        if self.session_factory is None:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        return self.session_factory()

    def get_scoped_session(self):
        """
        Get a scoped session (thread-local).

        Returns:
            Scoped SQLAlchemy session
        """
        if self.scoped_session_factory is None:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        return self.scoped_session_factory()

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for database operations.

        Usage:
            with db_manager.session_scope() as session:
                session.add(obj)
                # Changes are committed automatically
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """Close database connections."""
        if self.scoped_session_factory:
            self.scoped_session_factory.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """
    Get the global database manager instance.

    Args:
        database_url: Database URL (only used on first call)

    Returns:
        DatabaseManager instance
    """
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)

    return _db_manager


def init_database(database_url: Optional[str] = None, echo: bool = False):
    """
    Initialize the database.

    Args:
        database_url: Database URL
        echo: If True, log SQL statements
    """
    db_manager = get_db_manager(database_url)
    db_manager.initialize(echo=echo)
    db_manager.create_tables()
    return db_manager
