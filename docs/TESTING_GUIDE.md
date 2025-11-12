# Testing Guide

## Overview

The PV Testing Protocol Framework includes comprehensive test coverage using pytest.

## Running Tests

### All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=pv_testing --cov-report=html
```

### Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/

# Specific test file
pytest tests/test_protocols.py

# Specific test function
pytest tests/test_protocols.py::test_stc_power_measurement
```

## Test Structure

```
tests/
├── unit/
│   ├── test_protocols.py
│   ├── test_analysis.py
│   ├── test_reports.py
│   └── test_integrations.py
├── integration/
│   ├── test_workflow.py
│   ├── test_database.py
│   └── test_api_integration.py
├── api/
│   ├── test_service_requests.py
│   ├── test_protocols_api.py
│   └── test_auth.py
└── conftest.py  # Pytest fixtures
```

## Writing Tests

### Example Unit Test

```python
# tests/unit/test_protocols.py

import pytest
from pv_testing.protocols import STCPowerMeasurement

def test_stc_power_calculation():
    """Test STC power calculation"""
    protocol = STCPowerMeasurement()

    # Test data
    voc = 49.5
    isc = 10.2
    vmp = 41.8
    imp = 9.7

    # Calculate power
    pmax = protocol.calculate_power(vmp, imp)

    assert pmax == pytest.approx(405.46, rel=0.01)

def test_fill_factor_calculation():
    """Test fill factor calculation"""
    protocol = STCPowerMeasurement()

    voc = 49.5
    isc = 10.2
    pmax = 405.46

    ff = protocol.calculate_fill_factor(voc, isc, pmax)

    assert ff == pytest.approx(80.3, rel=0.1)
```

### Example Integration Test

```python
# tests/integration/test_workflow.py

import pytest
from pv_testing import ServiceRequest, ProtocolExecutor

@pytest.mark.integration
def test_complete_workflow(db_session):
    """Test complete workflow from SR to report"""

    # Create service request
    sr = ServiceRequest.create(
        customer="Test Corp",
        module_type="Test Module",
        protocols=["PVTP-001"]
    )

    assert sr.sr_number is not None

    # Execute protocol
    executor = ProtocolExecutor(protocol_id="PVTP-001")
    result = executor.execute(service_request=sr)

    assert result.status == "COMPLETE"

    # Generate report
    report = executor.generate_report(result)

    assert report.pdf_path is not None
```

### Example API Test

```python
# tests/api/test_service_requests.py

import pytest
from fastapi.testclient import TestClient
from pv_testing.api.main import app

client = TestClient(app)

def test_create_service_request():
    """Test creating service request via API"""

    response = client.post(
        "/api/v1/service-requests",
        json={
            "customer": {"name": "Test Corp"},
            "module": {"model": "Test-400W", "quantity": 5},
            "testing": {"standards": ["IEC 61215"]}
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "sr_number" in data
```

## Test Fixtures

Located in `tests/conftest.py`:

```python
import pytest
from pv_testing.db import engine, SessionLocal

@pytest.fixture(scope="session")
def db_engine():
    """Database engine fixture"""
    return engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Database session fixture"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_service_request():
    """Sample SR for testing"""
    return {
        "customer": {"name": "Test Corp"},
        "module": {"model": "Test-400W"},
        "testing": {"protocols": ["PVTP-001"]}
    }
```

## Test Coverage

### View Coverage Report

```bash
# Generate HTML report
pytest --cov=pv_testing --cov-report=html

# Open report
open htmlcov/index.html
```

### Coverage Goals

- Overall coverage: >80%
- Critical modules: >90%
- API endpoints: 100%

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Nightly scheduled builds

See `.github/workflows/ci.yml` for CI configuration.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
