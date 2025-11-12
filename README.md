# PV Testing Protocol Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](./docs/)

## Overview

The **PV Testing Protocol Framework** is a comprehensive, modular system for managing photovoltaic (PV) testing protocols with JSON-based dynamic templates for Streamlit/GenSpark UI integration. The framework includes automated analysis, charting, quality control, and report generation capabilities, fully integrated with LIMS, QMS, and Project Management systems.

### Key Features

- **54 Complete Testing Protocols**: Comprehensive coverage of IEC/ISO standards for PV testing
- **Dynamic JSON Templates**: Flexible, data-driven protocol definitions
- **Workflow Orchestration**: Service Request → Inspection → Protocol Execution → Report Generation
- **Automated Analysis**: Built-in data analysis, statistical calculations, and QC checks
- **Interactive Dashboards**: Streamlit-based UI for protocol execution and monitoring
- **System Integration**: LIMS, QMS, and PM system connectivity
- **Traceability**: Complete data lineage from service request to final report
- **Compliance**: IEC 61215, IEC 61730, IEC 62804, ISO 17025 standards

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Run automated setup
./deploy/setup.sh

# Start the application
./deploy/start_services.sh

# Access the dashboard
# Open browser to http://localhost:8501
```

For detailed installation instructions, see [INSTALLATION.md](./docs/INSTALLATION.md)

## Documentation

### User Documentation
- **[User Manual](./docs/USER_MANUAL.md)**: Complete end-user guide
- **[Workflow Guide](./docs/WORKFLOW_GUIDE.md)**: Step-by-step workflow documentation
- **[Protocol Catalog](./docs/PROTOCOL_CATALOG.md)**: All 54 protocols with descriptions

### Technical Documentation
- **[Architecture](./docs/ARCHITECTURE.md)**: System architecture and design
- **[API Reference](./docs/API_REFERENCE.md)**: REST API documentation
- **[Integration Guide](./docs/INTEGRATION_GUIDE.md)**: LIMS, QMS, PM integration
- **[Traceability Matrix](./docs/TRACEABILITY_MATRIX.md)**: Data lineage documentation

### Deployment & Administration
- **[Installation Guide](./docs/INSTALLATION.md)**: Step-by-step installation
- **[Configuration Guide](./docs/CONFIGURATION.md)**: Configuration options
- **[Admin Guide](./docs/ADMIN_GUIDE.md)**: System administration
- **[Docker Deployment](./docs/DOCKER_DEPLOYMENT.md)**: Container deployment
- **[Cloud Deployment](./docs/CLOUD_DEPLOYMENT.md)**: AWS/Azure/GCP deployment

### Developer Documentation
- **[Development Setup](./docs/DEVELOPMENT_SETUP.md)**: Local development environment
- **[Contributing](./docs/CONTRIBUTING.md)**: Contribution guidelines
- **[Code Standards](./docs/CODE_STANDARDS.md)**: Coding conventions
- **[Testing Guide](./docs/TESTING_GUIDE.md)**: Testing procedures

## Protocol Categories

The framework includes 54 protocols across 8 categories:

1. **Module Performance** (9 protocols): STC power, NOCT, low irradiance, temperature coefficients
2. **Electrical Safety** (8 protocols): Insulation, wet leakage, bypass diode, ground continuity
3. **Environmental Testing** (12 protocols): Thermal cycling, humidity freeze, damp heat, UV exposure
4. **Mechanical Testing** (8 protocols): Mechanical load, hail impact, twist test, robustness
5. **Degradation Analysis** (6 protocols): PID, LID, LeTID, UV degradation
6. **Quality Control** (5 protocols): Visual inspection, EL imaging, IR thermography, cell inspection
7. **Specialty Testing** (4 protocols): Spectral response, bifacial performance, durability
8. **Advanced Diagnostics** (2 protocols): Comprehensive module analysis, certification testing

See [PROTOCOL_CATALOG.md](./docs/PROTOCOL_CATALOG.md) for complete protocol listing.

## System Architecture

```
┌─────────────────┐
│ Service Request │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   Inspection    │────▶│ Test Planning│
└────────┬────────┘     └──────┬───────┘
         │                     │
         ▼                     ▼
┌─────────────────┐     ┌──────────────┐
│  Protocol Exec  │◀────│ JSON Template│
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  Data Analysis  │────▶│   Reporting  │
└────────┬────────┘     └──────┬───────┘
         │                     │
         ▼                     ▼
┌─────────────────┐     ┌──────────────┐
│  LIMS/QMS/PM    │◀────│  Dashboard   │
└─────────────────┘     └──────────────┘
```

## Technology Stack

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy
- **Frontend**: Streamlit, Plotly, Pandas
- **Database**: PostgreSQL, SQLite (dev)
- **API**: RESTful API, OpenAPI/Swagger
- **Deployment**: Docker, Kubernetes, AWS/Azure/GCP
- **CI/CD**: GitHub Actions, pytest, pylint

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (or SQLite for development)
- Node.js 14+ (for documentation generation)
- Docker (optional, for containerized deployment)

### Installation

See detailed instructions in [INSTALLATION.md](./docs/INSTALLATION.md)

### Basic Usage

```python
from pv_testing import ProtocolExecutor, ServiceRequest

# Create service request
sr = ServiceRequest.create(
    customer="Solar Corp",
    module_type="Mono-Si 400W",
    protocols=["PVTP-001", "PVTP-015", "PVTP-030"]
)

# Execute protocol
executor = ProtocolExecutor(protocol_id="PVTP-001")
results = executor.execute(service_request=sr)

# Generate report
report = executor.generate_report(results)
```

## Integration

The framework integrates with:

- **LIMS**: Bidirectional data sync, sample tracking
- **QMS**: NC reporting, CAPA tracking, audit trails
- **PM Systems**: Project tracking, resource allocation
- **ERP**: Invoicing, customer management

See [INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md) for details.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pv_testing --cov-report=html

# Run specific test category
pytest tests/test_protocols.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://docs.test-protocols.io](./docs/)
- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Email**: support@test-protocols.io

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and release notes.

## Roadmap

- **v1.1**: Machine learning-based QC predictions
- **v1.2**: Mobile app for field testing
- **v1.3**: Real-time collaboration features
- **v2.0**: AI-powered anomaly detection

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Maintainer**: ganeshgowri-ASA
