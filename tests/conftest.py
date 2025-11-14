"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import sys
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database.connection import engine, Base
from src.database.models import Protocol, TestExecution, Equipment


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_protocol_data():
    """Provide sample protocol data for testing."""
    return {
        "protocol_id": "TEST-001",
        "version": "1.0",
        "title": "Test Protocol",
        "category": "Test",
        "description": "A test protocol",
        "test_steps": [
            {
                "step_number": 1,
                "name": "Step 1",
                "description": "First test step",
                "duration": 10,
                "duration_unit": "minutes",
                "inputs": [],
                "measurements": [
                    {
                        "name": "value1",
                        "type": "number",
                        "unit": "V",
                        "required": True,
                    }
                ],
                "acceptance_criteria": [
                    {"parameter": "value1", "condition": "less_than", "value": 100}
                ],
            }
        ],
        "qc_checks": [],
        "metadata": {},
    }


@pytest.fixture
def term001_protocol():
    """Create a TERM-001 protocol instance."""
    from src.protocols.term001 import TERM001Protocol

    protocol_file = Path(__file__).parent.parent / "src" / "protocols" / "templates" / "term-001.json"
    return TERM001Protocol(protocol_file)
