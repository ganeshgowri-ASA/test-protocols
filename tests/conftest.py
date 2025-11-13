"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_db_url():
    """Provide temporary test database URL."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    yield db_url

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(test_db_url):
    """Provide clean database session for each test."""
    # Temporarily set DATABASE_URL
    original_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_db_url

    from src.models.database import engine, Base, SessionLocal, init_db

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)

    # Restore original URL
    if original_url:
        os.environ["DATABASE_URL"] = original_url
    elif "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture
def pid001_schema():
    """Load PID-001 schema."""
    import json

    schema_path = Path(__file__).parent.parent / "protocols" / "pid-001" / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def pid001_template():
    """Load PID-001 template."""
    import json

    template_path = Path(__file__).parent.parent / "protocols" / "pid-001" / "template.json"
    with open(template_path) as f:
        return json.load(f)


@pytest.fixture
def sample_test_parameters():
    """Provide sample test parameters."""
    return {
        "test_name": "TEST-001",
        "module_id": "MOD-12345",
        "test_voltage": -1000,
        "test_duration": 96,
        "temperature": 85,
        "relative_humidity": 85,
        "sampling_interval": 60,
        "leakage_current_threshold": 10,
        "operator": "Test User",
        "notes": "Test run"
    }
