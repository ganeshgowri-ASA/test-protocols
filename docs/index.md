# Test Protocols Framework Documentation

## Overview

The Test Protocols Framework is a modular, JSON-based system for defining and executing standardized test protocols for photovoltaic (PV) modules and components. It provides:

- **Dynamic Protocol Definitions**: JSON-based protocol templates that drive the entire testing workflow
- **Streamlit UI**: Interactive web interface for test execution and data entry
- **Automated Analysis**: Built-in QC checks, calculations, and visualizations
- **Database Integration**: SQLAlchemy models for persistent data storage
- **Report Generation**: Automated report generation in multiple formats
- **System Integration**: Ready for LIMS, QMS, and Project Management system integration

## Architecture

```
test-protocols/
├── protocols/              # Core protocol definitions and implementations
│   ├── definitions/        # JSON protocol templates
│   ├── implementations/    # Python protocol classes
│   ├── analysis/          # Analysis modules
│   └── visualization/     # Charting and reporting
├── ui/                    # Streamlit web interface
│   ├── app.py            # Main application
│   ├── pages/            # UI pages
│   └── components/       # Reusable UI components
├── database/             # Database schemas and models
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
└── config/               # Configuration files
```

## Key Components

### 1. Protocol Definitions (JSON)

Protocols are defined in JSON format following a standardized schema. Each protocol includes:

- Metadata (ID, name, version, category)
- Standards compliance information
- Equipment requirements
- Step-by-step procedures
- Data fields to collect
- QC criteria
- Analysis and reporting specifications

**Example:**
```json
{
  "protocol_id": "CORR-001",
  "name": "Corrosion Testing",
  "category": "degradation",
  "version": "1.0.0",
  "steps": [...],
  "data_fields": [...],
  "qc_criteria": [...]
}
```

### 2. Protocol Implementations (Python)

Each protocol has a Python implementation that:

- Extends the `BaseProtocol` abstract class
- Implements step execution logic
- Performs data validation
- Runs QC checks
- Generates reports

### 3. Streamlit UI

The web interface provides:

- Protocol selection and browsing
- Test run creation and management
- Step-by-step data entry with validation
- Real-time QC checking
- Interactive visualizations
- Report generation and download

### 4. Database Layer

SQLAlchemy models provide:

- Protocol storage
- Test run tracking
- Measurement data storage
- Visual inspection records
- QC results
- Equipment and sample tracking

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Running the UI

```bash
streamlit run ui/app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=ui --cov-report=html

# Run specific test file
pytest tests/unit/test_protocols/test_corrosion_protocol.py
```

### Initialize Database

```bash
# Create SQLite database
sqlite3 test_protocols.db < database/schema.sql
```

## Available Protocols

### CORR-001: Corrosion Testing

Comprehensive corrosion testing protocol for PV modules using salt spray and humidity exposure.

**Standards:**
- IEC 61701: Salt Mist Corrosion Testing
- ASTM B117: Salt Spray (Fog) Apparatus
- IEC 61215: Design Qualification

**Key Features:**
- Multi-cycle salt spray and humidity exposure
- Electrical performance tracking
- Visual corrosion inspection
- Automated QC checks
- Degradation analysis

[See detailed CORR-001 documentation →](corr-001.md)

## Creating New Protocols

### 1. Create JSON Definition

Create a new JSON file in `protocols/definitions/<category>/`:

```json
{
  "protocol_id": "YOUR-001",
  "name": "Your Protocol Name",
  "category": "electrical",
  "version": "1.0.0",
  "steps": [
    {
      "step_number": 1,
      "name": "Step Name",
      "type": "measurement",
      "description": "Step description"
    }
  ],
  "data_fields": [
    {
      "field_id": "your_field",
      "name": "Your Field",
      "type": "number",
      "required": true
    }
  ]
}
```

### 2. Create Python Implementation

Create a Python class in `protocols/implementations/<category>/`:

```python
from protocols.implementations.base_protocol import BaseProtocol

class YourProtocol(BaseProtocol):
    def execute_step(self, step_number, **kwargs):
        # Implement step logic
        pass

    def generate_report(self, output_path=None):
        # Implement report generation
        pass
```

### 3. Write Tests

Create tests in `tests/unit/test_protocols/`:

```python
def test_your_protocol():
    protocol = YourProtocol(definition_path=path)
    assert protocol.definition.protocol_id == "YOUR-001"
```

## API Reference

### BaseProtocol

Abstract base class for all protocols.

**Key Methods:**
- `create_test_run(run_id, operator, initial_data)`: Create new test run
- `validate_data(data)`: Validate data against protocol schema
- `run_qc_checks(data)`: Execute quality control checks
- `calculate_results(data)`: Calculate derived results
- `execute_step(step_number, **kwargs)`: Execute protocol step (abstract)
- `generate_report(output_path)`: Generate test report (abstract)

### CorrosionProtocol

CORR-001 implementation extending BaseProtocol.

**Additional Methods:**
- `get_degradation_curve()`: Get power degradation data over cycles

**Step Execution:**
- Step 1-13: Implements complete corrosion testing workflow

## Configuration

### Development Configuration

Edit `config/dev.yaml`:

```yaml
environment: development
database:
  type: sqlite
  path: ./data/test_protocols_dev.db
ui:
  debug: true
```

### Production Configuration

Edit `config/prod.yaml`:

```yaml
environment: production
database:
  type: postgresql
  host: ${DB_HOST}
security:
  require_auth: true
```

## Integration

### LIMS Integration

The framework is designed to integrate with Laboratory Information Management Systems (LIMS):

```python
from protocols.integrations.lims import LIMSConnector

lims = LIMSConnector(url=LIMS_URL, api_key=API_KEY)
lims.submit_test_results(test_run_data)
```

### QMS Integration

Quality Management System integration for compliance tracking:

```python
from protocols.integrations.qms import QMSConnector

qms = QMSConnector(url=QMS_URL, api_key=API_KEY)
qms.submit_qc_results(qc_results)
```

## Troubleshooting

### Common Issues

**Protocol not loading:**
- Verify JSON syntax is valid
- Check protocol definition against schema
- Ensure all required fields are present

**Data validation errors:**
- Check field types match expectations
- Verify required fields are provided
- Ensure values are within validation ranges

**QC checks failing:**
- Review QC criteria in protocol definition
- Check measured values against thresholds
- Verify baseline measurements are recorded

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Email: support@example.com

## Changelog

### Version 0.1.0 (2025-01-15)
- Initial release
- CORR-001 corrosion testing protocol
- Streamlit UI
- Database models
- Core framework implementation
