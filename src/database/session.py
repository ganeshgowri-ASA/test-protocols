"""Database session management."""

from typing import Optional, Generator
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseSession:
    """Database session manager."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        """Initialize database session manager.

        Args:
            database_url: SQLAlchemy database URL. If None, uses SQLite in-memory.
        """
        if database_url is None:
            # Default to SQLite in data directory
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///{data_dir}/protocols.db"

        # Create engine
        if database_url.startswith("sqlite"):
            # SQLite-specific settings
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(database_url, pool_pre_ping=True)

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy session

        Note:
            The caller is responsible for closing the session.
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Yields:
            SQLAlchemy session

        Example:
            with db.session_scope() as session:
                protocol = Protocol(...)
                session.add(protocol)
                # Automatically commits on success, rolls back on error
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database session instance
_db_session: Optional[DatabaseSession] = None


def initialize_database(database_url: Optional[str] = None) -> DatabaseSession:
    """Initialize the global database session.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        DatabaseSession instance
    """
    global _db_session
    _db_session = DatabaseSession(database_url)
    _db_session.create_tables()
    return _db_session


def get_session() -> Session:
    """Get a database session from the global instance.

    Returns:
        SQLAlchemy session

    Raises:
        RuntimeError: If database not initialized
    """
    if _db_session is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    return _db_session.get_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope using the global database instance.

    Yields:
        SQLAlchemy session

    Raises:
        RuntimeError: If database not initialized
    """
    if _db_session is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )

    with _db_session.session_scope() as session:
        yield session
