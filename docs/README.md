# Test Protocols Framework Documentation

Welcome to the Test Protocols Framework documentation.

## Overview

The Test Protocols Framework is a modular, JSON-based system for managing and executing PV (photovoltaic) testing protocols with automated analysis, charting, QC checks, and report generation.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .[dev]
```

### Database Setup

```bash
# Initialize the database
python -c "from database import init_db; init_db()"
```

### Running the UI

```bash
# Start the Streamlit application
streamlit run ui/app.py
```

## Documentation

- [Architecture](architecture.md) - System architecture and design
- [Protocol Schema](protocol_schema.md) - JSON protocol schema specification
- [Environmental Protocols](environmental_protocols.md) - Environmental testing protocols guide
- [Database Schema](database.md) - Database schema and models
- [API Documentation](api.md) - API reference

## Protocol Examples

- [DESERT-001: Desert Climate Test](examples/desert_climate.md)
- More examples coming soon...

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test markers
pytest -m desert
pytest -m environmental
```

## Contributing

Please see CONTRIBUTING.md for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
