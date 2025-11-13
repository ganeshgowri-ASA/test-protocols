"""
Database package initialization
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# This will be initialized by the Flask app
db_engine = None
db_session = None


def init_db(database_url, echo=False):
    """Initialize database connection"""
    global db_engine, db_session

    db_engine = create_engine(database_url, echo=echo)
    session_factory = sessionmaker(bind=db_engine)
    db_session = scoped_session(session_factory)

    # Set query property on Base
    Base.query = db_session.query_property()

    return db_engine, db_session


def create_all_tables():
    """Create all tables in the database"""
    if db_engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.create_all(db_engine)


def drop_all_tables():
    """Drop all tables in the database (use with caution!)"""
    if db_engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.drop_all(db_engine)


def get_session():
    """Get database session"""
    if db_session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db_session()
