# Testing Guide

## Overview

This guide provides comprehensive documentation for the QA testing framework for the PV Testing Protocol system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Data Generation](#test-data-generation)
6. [Validation Testing](#validation-testing)
7. [Performance Testing](#performance-testing)
8. [Continuous Integration](#continuous-integration)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage
pytest --cov=protocols --cov=validators --cov=test_data --cov=monitoring

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only
```

## Test Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_handler.py
│   └── test_generators.py
├── integration/        # Integration tests for component interactions
│   └── test_protocol_workflow.py
├── e2e/               # End-to-end tests for complete workflows
│   └── test_complete_flow.py
└── performance/       # Performance and load tests
```

## Running Tests

### By Category

```bash
# Unit tests (fast)
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# End-to-end tests
pytest tests/e2e -v

# Performance tests
pytest tests/performance -v
```

### By Module

```bash
# Test specific module
pytest tests/unit/test_validators.py -v

# Test specific test class
pytest tests/unit/test_validators.py::TestSchemaValidator -v

# Test specific test function
pytest tests/unit/test_validators.py::TestSchemaValidator::test_validate_valid_protocol -v
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=protocols --cov=validators --cov-report=html

# View report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Run tests in parallel (uses pytest-xdist)
pytest -n auto

# Specify number of workers
pytest -n 4
```

## Writing Tests

### Unit Test Example

```python
import pytest
from protocols.models import Protocol, ProtocolType

@pytest.mark.unit
class TestProtocol:
    def test_valid_protocol(self):
        """Test creating a valid protocol."""
        protocol = Protocol(
            protocol_id="TEST-001",
            protocol_name="Test Protocol",
            protocol_type=ProtocolType.ELECTRICAL,
            version="1.0",
            parameters={"module_id": "MOD-001"},
        )

        assert protocol.protocol_id == "TEST-001"
        assert protocol.status == "pending"
```

### Integration Test Example

```python
@pytest.mark.integration
def test_protocol_workflow():
    """Test complete protocol workflow."""
    # Load protocol
    loader = ProtocolLoader()
    template = loader.load_template("IEC61215-10-1")

    # Validate
    validator = SchemaValidator()
    result = validator.validate_protocol(template)
    assert result["is_valid"]

    # Execute
    handler = ProtocolHandler()
    protocol = handler.load_protocol(template)
    execution_result = handler.execute_protocol(protocol)

    assert execution_result.status == "completed"
```

### Using Fixtures

```python
@pytest.fixture
def sample_protocol():
    """Provide sample protocol for testing."""
    return {
        "protocol_id": "TEST-001",
        "protocol_name": "Test",
        "protocol_type": "electrical",
        "version": "1.0",
        "parameters": {},
    }

def test_with_fixture(sample_protocol):
    """Test using fixture."""
    assert sample_protocol["protocol_id"] == "TEST-001"
```

## Test Data Generation

### Using Protocol Generator

```python
from test_data import ProtocolGenerator

# Create generator
generator = ProtocolGenerator(seed=42)  # Use seed for reproducibility

# Generate single protocol
protocol = generator.generate_protocol(protocol_type="electrical")

# Generate batch
protocols = generator.generate_batch(count=10)
```

### Using Measurement Generator

```python
from test_data import MeasurementGenerator

# Create generator
generator = MeasurementGenerator(seed=42)

# Generate measurement
measurement = generator.generate_measurement(parameter="voltage")

# Generate I-V curve
iv_curve = generator.generate_iv_curve(num_points=100)

# Generate time series
time_series = generator.generate_time_series(
    parameter="temperature",
    duration_seconds=3600,
    interval_seconds=60
)
```

### Edge Case Testing

```python
from test_data import EdgeCaseGenerator

generator = EdgeCaseGenerator()

# Generate boundary values
boundary_cases = generator.generate_boundary_values("temperature")

# Generate null/empty cases
null_cases = generator.generate_null_empty_cases()

# Generate all edge cases
all_cases = generator.generate_all_edge_cases()
```

## Validation Testing

### Schema Validation

```python
from validators import SchemaValidator

validator = SchemaValidator()

# Validate protocol
result = validator.validate_protocol(protocol_data)

if result["is_valid"]:
    print("✓ Protocol is valid")
else:
    print(f"✗ Errors: {result['errors']}")
```

### Range Validation

```python
from validators import RangeValidator

validator = RangeValidator()

# Validate single value
result = validator.validate_value("temperature", 25.0)

# Validate multiple values
measurements = {
    "temperature": 25.0,
    "irradiance": 1000.0,
    "voltage": 45.0,
}
result = validator.validate_multiple_values(measurements)
```

### Compliance Validation

```python
from validators import ComplianceValidator

validator = ComplianceValidator()

# Check IEC 61215 compliance
result = validator.validate_protocol_compliance(
    protocol_data,
    standard="IEC61215"
)

if result["compliant"]:
    print("✓ Protocol is compliant")
```

## Performance Testing

### Load Testing

```python
@pytest.mark.performance
@pytest.mark.slow
def test_large_batch_processing():
    """Test processing large batch of protocols."""
    import time

    generator = ProtocolGenerator(seed=42)
    protocols = generator.generate_batch(count=1000)

    start_time = time.time()

    handler = ProtocolHandler()
    for protocol_data in protocols:
        protocol = handler.load_protocol(protocol_data)
        handler.execute_protocol(protocol)

    elapsed = time.time() - start_time

    # Performance assertion
    assert elapsed < 300  # Should complete in 5 minutes
```

### Benchmarking

```python
def test_validation_performance(benchmark):
    """Benchmark validation performance."""
    validator = SchemaValidator()
    generator = ProtocolGenerator(seed=42)
    protocol = generator.generate_protocol()

    # Benchmark the validation
    result = benchmark(validator.validate_protocol, protocol)

    assert result["is_valid"]
```

## Continuous Integration

### GitHub Actions

The CI/CD pipeline automatically runs on:
- Push to main, develop, or claude/** branches
- Pull requests to main or develop
- Daily at 2 AM UTC

### Pipeline Stages

1. **Test** - Run unit, integration, and e2e tests
2. **Validation** - Validate JSON schemas and protocol templates
3. **Quality Checks** - Run linting and code quality tools
4. **Performance** - Run performance tests
5. **Security** - Security scanning with Bandit

### Local CI Simulation

```bash
# Run all checks locally
./scripts/run_ci_checks.sh

# Or run individual checks
pytest
flake8 protocols validators test_data monitoring
black --check protocols validators test_data monitoring
mypy protocols validators test_data monitoring
```

## Best Practices

1. **Use descriptive test names** - Test names should clearly describe what is being tested
2. **One assertion per test** - Keep tests focused and easy to debug
3. **Use fixtures** - Share common setup code using pytest fixtures
4. **Test edge cases** - Use EdgeCaseGenerator for comprehensive testing
5. **Mock external dependencies** - Use pytest-mock for isolating tests
6. **Maintain test data** - Keep test data generators up to date
7. **Run tests frequently** - Run tests before commits
8. **Review coverage** - Aim for >80% code coverage
9. **Document test requirements** - Document special setup or dependencies
10. **Keep tests fast** - Use markers for slow tests

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Show full traceback
pytest --tb=long

# Run specific failing test
pytest tests/unit/test_models.py::TestProtocol::test_valid_protocol -vv
```

### Coverage Issues

```bash
# Check which lines are not covered
pytest --cov=protocols --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=protocols --cov-report=html
open htmlcov/index.html
```

### Performance Issues

```bash
# Profile test execution
pytest --durations=10  # Show 10 slowest tests

# Run only fast tests
pytest -m "not slow"
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [JSON Schema Documentation](https://json-schema.org/)

## Support

For questions or issues:
1. Check existing issues on GitHub
2. Review this testing guide
3. Contact the development team
