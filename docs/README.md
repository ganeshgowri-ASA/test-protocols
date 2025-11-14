# PV Test Protocols Framework - Documentation

Welcome to the documentation for the Modular PV Testing Protocol Framework.

## Table of Contents

1. [Getting Started](getting-started.md)
2. [Architecture Overview](architecture.md)
3. [Protocol Format](protocol-format.md)
4. [TERM-001 Protocol](term-001-protocol.md)
5. [API Reference](api-reference.md)
6. [Database Schema](database-schema.md)
7. [Creating Custom Protocols](creating-protocols.md)
8. [Deployment Guide](deployment.md)

## Quick Links

- **Installation**: See [Getting Started](getting-started.md)
- **Running Tests**: `pytest tests/`
- **Starting UI**: `streamlit run src/ui/streamlit_app.py`
- **Protocol Templates**: `src/protocols/templates/`

## Overview

The PV Test Protocols Framework is a modular, JSON-based system for defining and executing test protocols for photovoltaic modules. It provides:

- **Dynamic Protocol Definition**: Define test protocols using JSON templates
- **Automated Execution**: Step-by-step guided test execution through web UI
- **Data Validation**: Automatic validation of measurements against acceptance criteria
- **Database Storage**: Persistent storage of test results and history
- **Reporting**: Automated report generation with charts and analysis
- **Integration Ready**: Built for integration with LIMS, QMS, and project management systems

## Supported Protocols

### TERM-001: Terminal Robustness Test

The Terminal Robustness Test evaluates the mechanical strength and electrical integrity of PV module terminals under various stress conditions.

**Test Steps:**
1. Initial Visual Inspection
2. Initial Electrical Continuity Test
3. Pull Force Test
4. Torque Test
5. Post-Stress Electrical Continuity Test
6. Dielectric Strength Test
7. Final Visual Inspection

**Applicable Standards:**
- IEC 61215-2:2021
- IEC 61730-2:2016
- UL 1703

See [TERM-001 Protocol Documentation](term-001-protocol.md) for details.

## Technology Stack

- **Backend**: Python 3.9+, SQLAlchemy, Pydantic
- **Frontend**: Streamlit, Plotly
- **Database**: SQLite (dev), PostgreSQL (production)
- **Testing**: pytest, pytest-cov

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) for details.
