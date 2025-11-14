"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
import logging

from .models import Base

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""

    def __init__(self, database_url: str = None, echo: bool = False):
        """
        Initialize database connection

        Args:
            database_url: SQLAlchemy database URL (default: SQLite in project root)
            echo: Enable SQL query logging
        """
        if database_url is None:
            db_path = Path(__file__).parent.parent.parent / "test_protocols.db"
            database_url = f"sqlite:///{db_path}"

        # Configure engine
        connect_args = {}
        poolclass = None

        if database_url.startswith("sqlite"):
            # SQLite-specific configuration
            connect_args = {"check_same_thread": False}
            poolclass = StaticPool

        self.engine = create_engine(
            database_url,
            echo=echo,
            connect_args=connect_args,
            poolclass=poolclass
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(f"Database initialized: {database_url}")

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")

    def get_session(self) -> Session:
        """
        Get a new database session

        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations

        Usage:
            with db.session_scope() as session:
                session.add(object)
                # session.commit() called automatically on success
                # session.rollback() called automatically on exception
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


# Global database instance
_db_instance = None


def get_database(database_url: str = None, echo: bool = False) -> Database:
    """
    Get or create global database instance

    Args:
        database_url: SQLAlchemy database URL
        echo: Enable SQL query logging

    Returns:
        Database instance
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = Database(database_url=database_url, echo=echo)

    return _db_instance


def init_database(database_url: str = None, echo: bool = False):
    """
    Initialize database and create tables

    Args:
        database_url: SQLAlchemy database URL
        echo: Enable SQL query logging
    """
    db = get_database(database_url=database_url, echo=echo)
    db.create_tables()
    logger.info("Database initialized and tables created")


if __name__ == "__main__":
    # Initialize database when run directly
    logging.basicConfig(level=logging.INFO)
    init_database(echo=True)
