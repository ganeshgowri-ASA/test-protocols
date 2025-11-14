"""
Pytest Configuration and Shared Fixtures

Provides common fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def protocols_dir(tmp_path):
    """Create a temporary protocols directory."""
    protocols_dir = tmp_path / "protocols" / "templates"
    protocols_dir.mkdir(parents=True)
    return protocols_dir


@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
