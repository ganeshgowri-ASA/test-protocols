"""
Database Session Management
Handles database connections and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .models import Base

# Default database path
DEFAULT_DB_PATH = Path.home() / ".test_protocols" / "test_protocols.db"


class DatabaseManager:
    """Manages database connections and sessions"""

    def __init__(self, db_url: str = None):
        """
        Initialize database manager

        Args:
            db_url: Database URL (default: SQLite in user home)
        """
        if db_url is None:
            # Create directory if it doesn't exist
            db_path = DEFAULT_DB_PATH
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        """Initialize database (create all tables)"""
        Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations

        Usage:
            with db_manager.session_scope() as session:
                # perform operations
                session.add(obj)
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


# Global database manager instance
_db_manager: DatabaseManager = None


def init_db(db_url: str = None):
    """
    Initialize the database

    Args:
        db_url: Database URL (default: SQLite in user home)
    """
    global _db_manager
    _db_manager = DatabaseManager(db_url)
    _db_manager.init_db()
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = init_db()
    return _db_manager


def get_session() -> Session:
    """Get a new database session"""
    return get_db_manager().get_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for database operations

    Usage:
        with session_scope() as session:
            # perform operations
            session.add(obj)
    """
    db_manager = get_db_manager()
    with db_manager.session_scope() as session:
        yield session
