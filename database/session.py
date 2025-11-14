"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path
import yaml
from typing import Optional

from .models.base import Base


# Global session factory
SessionFactory = None


def get_database_url(config_path: Optional[str] = None) -> str:
    """
    Get database URL from configuration.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Database URL string
    """
    if config_path:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Default configuration
        config = {
            "database": {
                "type": "sqlite",
                "sqlite": {
                    "path": "data/test_protocols.db"
                }
            }
        }

    db_config = config.get("database", {})
    db_type = db_config.get("type", "sqlite")

    if db_type == "sqlite":
        db_path = db_config.get("sqlite", {}).get("path", "data/test_protocols.db")
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    elif db_type == "postgresql":
        pg_config = db_config.get("postgresql", {})
        host = pg_config.get("host", "localhost")
        port = pg_config.get("port", 5432)
        database = pg_config.get("database", "test_protocols")
        username = pg_config.get("username", "postgres")
        password = pg_config.get("password", "")

        if password:
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{username}@{host}:{port}/{database}"

    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def init_database(config_path: Optional[str] = None, echo: bool = False) -> None:
    """
    Initialize the database and create all tables.

    Args:
        config_path: Path to config.yaml file
        echo: Whether to echo SQL statements
    """
    global SessionFactory

    database_url = get_database_url(config_path)
    engine = create_engine(database_url, echo=echo)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    session_factory = sessionmaker(bind=engine)
    SessionFactory = scoped_session(session_factory)

    print(f"Database initialized at: {database_url}")


def get_session():
    """
    Get a database session.

    Returns:
        Database session instance
    """
    global SessionFactory

    if SessionFactory is None:
        # Initialize with default configuration
        init_database()

    return SessionFactory()


def close_session():
    """Close the current session."""
    global SessionFactory
    if SessionFactory:
        SessionFactory.remove()
