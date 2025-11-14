"""
Database schema creation and management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and schema."""

    def __init__(self, database_url: str = "sqlite:///test_protocols.db"):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_all_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_all_tables(self):
        """Drop all tables in the database. Use with caution!"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

    def get_session(self):
        """
        Get a new database session.

        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()

    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


def init_database(database_url: str = "sqlite:///test_protocols.db"):
    """
    Initialize database with tables.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        DatabaseManager instance
    """
    db_manager = DatabaseManager(database_url)
    db_manager.create_all_tables()
    return db_manager
