"""Database connection and session management."""

import os
from typing import Generator
from contextlib import contextmanager
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.database.models import Base


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, config_path: str = "config/database.yaml", env: str = None):
        """Initialize database manager.

        Args:
            config_path: Path to database configuration file
            env: Environment name (development, production, test)
        """
        self.config = self._load_config(config_path)
        self.env = env or self.config.get('default_env', 'development')
        self.engine = None
        self.SessionLocal = None

    def _load_config(self, config_path: str) -> dict:
        """Load database configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration if file not found
            return {
                'database': {
                    'development': {
                        'type': 'sqlite',
                        'path': './data/test_protocols.db'
                    }
                },
                'default_env': 'development'
            }

    def _get_connection_string(self) -> str:
        """Generate database connection string based on configuration."""
        db_config = self.config['database'][self.env]
        db_type = db_config['type']

        if db_type == 'sqlite':
            db_path = db_config['path']
            if db_path == ":memory:":
                return "sqlite:///:memory:"
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return f"sqlite:///{db_path}"

        elif db_type == 'postgresql':
            username = os.getenv('DB_USER', db_config.get('username'))
            password = os.getenv('DB_PASSWORD', db_config.get('password'))
            host = db_config['host']
            port = db_config['port']
            database = db_config['database']
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def initialize(self) -> None:
        """Initialize database connection and create tables."""
        connection_string = self._get_connection_string()
        db_config = self.config['database'][self.env]

        # Engine kwargs
        engine_kwargs = {
            'echo': db_config.get('echo', False)
        }

        # Special handling for in-memory SQLite (for testing)
        if connection_string == "sqlite:///:memory:":
            engine_kwargs['connect_args'] = {'check_same_thread': False}
            engine_kwargs['poolclass'] = StaticPool

        self.engine = create_engine(connection_string, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Create all tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy Session object
        """
        if self.SessionLocal is None:
            self.initialize()
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Yields:
            SQLAlchemy Session object

        Example:
            with db_manager.session_scope() as session:
                protocol = session.query(Protocol).first()
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

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()


# Global database manager instance
_db_manager = None


def get_db_manager(env: str = None) -> DatabaseManager:
    """Get global database manager instance.

    Args:
        env: Environment name (optional)

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(env=env)
        _db_manager.initialize()
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection.

    Yields:
        SQLAlchemy Session object

    Example:
        def some_function(db: Session = next(get_db())):
            protocols = db.query(Protocol).all()
    """
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def init_db(env: str = None) -> None:
    """Initialize database and create tables.

    Args:
        env: Environment name (optional)
    """
    db_manager = get_db_manager(env=env)
    db_manager.initialize()
    print(f"Database initialized successfully for environment: {db_manager.env}")
