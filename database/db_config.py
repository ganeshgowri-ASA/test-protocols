"""
Database Configuration
Handles database connection and configuration settings
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

from .models import Base

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database configuration class"""

    def __init__(self, database_url: str = None):
        """
        Initialize database configuration.

        Args:
            database_url: Database connection URL. If None, uses environment variable.
        """
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.session_factory = None
        self.Session = None

    def _get_database_url(self) -> str:
        """Get database URL from environment or use default SQLite."""
        # Check for environment variable
        db_url = os.getenv('DATABASE_URL')

        if db_url:
            return db_url

        # Default to SQLite in project directory
        project_root = Path(__file__).parent.parent
        db_path = project_root / 'data' / 'test_protocols.db'
        db_path.parent.mkdir(exist_ok=True)

        return f"sqlite:///{db_path}"

    def initialize(self, echo: bool = False) -> None:
        """
        Initialize database engine and session factory.

        Args:
            echo: If True, SQLAlchemy will log all SQL statements
        """
        # Create engine
        if self.database_url.startswith('sqlite'):
            # SQLite-specific configuration
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
                pool_size=10,
                max_overflow=20
            )

        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """Drop all tables from the database. USE WITH CAUTION!"""
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        Base.metadata.drop_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        if self.Session is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        return self.Session()

    def close(self) -> None:
        """Close database connections."""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()


# Global database instance
db_config = DatabaseConfig()


def init_db(database_url: str = None, echo: bool = False) -> DatabaseConfig:
    """
    Initialize the database with the given configuration.

    Args:
        database_url: Database connection URL
        echo: If True, log SQL statements

    Returns:
        DatabaseConfig instance
    """
    global db_config

    if database_url:
        db_config = DatabaseConfig(database_url)

    db_config.initialize(echo=echo)
    db_config.create_tables()

    return db_config


def get_db_session():
    """
    Get a database session.

    Returns:
        SQLAlchemy session
    """
    return db_config.get_session()
