"""Database session management."""

import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base
from utils.config import get_config
from utils.logging import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Database session manager singleton."""

    _instance: Optional['SessionManager'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None

    def __new__(cls) -> 'SessionManager':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, database_url: Optional[str] = None) -> None:
        """Initialize database connection.

        Args:
            database_url: Database URL. If None, reads from config.
        """
        if self._engine is not None:
            logger.warning("Database already initialized")
            return

        if database_url is None:
            database_url = self._get_database_url_from_config()

        # Create engine
        echo = get_config('database.echo', False)
        pool_size = get_config('database.pool_size', 5)
        max_overflow = get_config('database.max_overflow', 10)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)

        logger.info(f"Database initialized: {database_url.split('://')[0]}://...")

    def _get_database_url_from_config(self) -> str:
        """Get database URL from configuration.

        Returns:
            Database URL string
        """
        db_type = get_config('database.type', 'sqlite')

        if db_type == 'sqlite':
            db_path = get_config('database.path', 'test_protocols.db')
            # Ensure absolute path
            if not os.path.isabs(db_path):
                project_root = Path(__file__).parent.parent
                db_path = os.path.join(project_root, db_path)
            return f"sqlite:///{db_path}"

        elif db_type == 'postgresql':
            host = get_config('database.host', 'localhost')
            port = get_config('database.port', 5432)
            database = get_config('database.database', 'test_protocols')
            username = get_config('database.username', 'postgres')
            password = get_config('database.password', '')

            return f"postgresql://{username}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def create_tables(self) -> None:
        """Create all database tables."""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        Base.metadata.create_all(self._engine)
        logger.info("Database tables created")

    def drop_tables(self) -> None:
        """Drop all database tables."""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        Base.metadata.drop_all(self._engine)
        logger.warning("Database tables dropped")

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy Session object

        Raises:
            RuntimeError: If database not initialized
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        return self._session_factory()

    @property
    def engine(self) -> Engine:
        """Get database engine.

        Returns:
            SQLAlchemy Engine

        Raises:
            RuntimeError: If database not initialized
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine


# Global session manager
_manager = SessionManager()


def init_database(database_url: Optional[str] = None, create_tables: bool = True) -> None:
    """Initialize database.

    Args:
        database_url: Database URL. If None, reads from config.
        create_tables: Whether to create tables
    """
    _manager.initialize(database_url)
    if create_tables:
        _manager.create_tables()


def get_session() -> Session:
    """Get a database session.

    Returns:
        SQLAlchemy Session
    """
    return _manager.get_session()


def get_engine() -> Engine:
    """Get database engine.

    Returns:
        SQLAlchemy Engine
    """
    return _manager.engine
