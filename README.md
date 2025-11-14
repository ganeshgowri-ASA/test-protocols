# Test Protocols Framework

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Features

- 🔬 **JSON-Based Protocol Definitions** - Define test protocols as structured JSON templates
- 🖥️ **Dynamic Streamlit UI** - Automatically generated forms from protocol definitions
- ✅ **Automated QC Checks** - Built-in quality control validation
- 📊 **Real-Time Analysis** - Automated calculations and visualizations
- 📄 **Report Generation** - Multi-format report export (Markdown, PDF, JSON, CSV)
- 🗄️ **Database Integration** - SQLAlchemy models for persistent storage
- 🔌 **System Integration** - Ready for LIMS, QMS, and PM system connections
- 🧪 **Comprehensive Testing** - Full unit test coverage with pytest

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

### Run the Application

```bash
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=ui --cov-report=html
```

## Project Structure

```
test-protocols/
├── protocols/              # Core protocol system
│   ├── definitions/        # JSON protocol templates
│   │   └── corrosion/
│   │       └── corr-001.json
│   ├── implementations/    # Python protocol classes
│   │   ├── base_protocol.py
│   │   └── corrosion/
│   │       └── corrosion_protocol.py
│   ├── analysis/          # Analysis modules
│   ├── visualization/     # Charting and plotting
│   └── integrations/      # External system integrations
│
├── ui/                    # Streamlit web interface
│   ├── app.py            # Main application
│   ├── pages/            # UI pages (selector, entry, analysis, reports)
│   ├── components/       # Reusable UI components
│   └── utils/            # Session state management
│
├── database/             # Database layer
│   ├── models.py         # SQLAlchemy models
│   ├── schema.sql        # Database schema
│   └── migrations/       # Database migrations
│
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── conftest.py      # Pytest fixtures
│
├── docs/                 # Documentation
│   ├── index.md         # Main documentation
│   └── corr-001.md      # CORR-001 protocol guide
│
├── config/               # Configuration files
│   ├── dev.yaml         # Development config
│   ├── prod.yaml        # Production config
│   └── protocol_schema.json  # JSON schema
│
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Package configuration
└── README.md            # This file
```

## Available Protocols

### CORR-001: Corrosion Testing

Comprehensive corrosion testing protocol for PV modules using salt spray and humidity exposure.

**Standards Compliance:**
- IEC 61701:2020 - Salt Mist Corrosion Testing
- ASTM B117:2019 - Salt Spray Apparatus
- IEC 61215:2021 - Design Qualification

**Key Features:**
- Multi-cycle salt spray and humidity exposure
- Electrical performance tracking (IV curves)
- Visual corrosion inspection
- Automated QC checks and degradation analysis
- Comprehensive reporting

[View detailed documentation →](docs/corr-001.md)

## Usage Example

### Python API

```python
from protocols.implementations.corrosion.corrosion_protocol import CorrosionProtocol

# Load protocol
protocol = CorrosionProtocol()

# Create test run
test_run = protocol.create_test_run(
    run_id="CORR-001-2025-001",
    operator="John Doe"
)

# Execute step
result = protocol.execute_step(
    1,
    sample_id="MODULE-12345",
    serial_number="SN-67890",
    operator="John Doe"
)

# Run QC checks
qc_results = protocol.run_qc_checks(protocol.test_run.data)

# Generate report
report = protocol.generate_report()
print(report)
```

### Streamlit UI Workflow

1. **Select Protocol** - Browse and select from available protocols
2. **Create Test Run** - Enter sample information and start new test
3. **Data Entry** - Follow step-by-step workflow with validation
4. **Analysis** - View real-time QC checks and visualizations
5. **Reports** - Download comprehensive test reports

## Creating New Protocols

### 1. Define Protocol (JSON)

Create `protocols/definitions/category/your-protocol.json`:

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
      "required": true,
      "validation": {"min": 0, "max": 100}
    }
  ],
  "qc_criteria": [
    {
      "criterion_id": "qc_1",
      "name": "QC Check Name",
      "type": "range",
      "field_id": "your_field",
      "condition": {"min": 10, "max": 90},
      "severity": "critical"
    }
  ]
}
```

### 2. Implement Protocol (Python)

Create `protocols/implementations/category/your_protocol.py`:

```python
from protocols.implementations.base_protocol import BaseProtocol

class YourProtocol(BaseProtocol):
    def execute_step(self, step_number, **kwargs):
        # Implement step logic
        return {
            "success": True,
            "result": {}
        }

    def generate_report(self, output_path=None):
        # Generate report
        return "Report content"
```

### 3. Write Tests

Create `tests/unit/test_protocols/test_your_protocol.py`:

```python
def test_your_protocol(your_protocol_path):
    protocol = YourProtocol(definition_path=your_protocol_path)
    assert protocol.definition.protocol_id == "YOUR-001"
```

## Configuration

### Development Setup

Edit `config/dev.yaml`:

```yaml
environment: development
database:
  type: sqlite
  path: ./data/test_protocols_dev.db
ui:
  debug: true
```

### Production Setup

Edit `config/prod.yaml` and set environment variables:

```bash
export DB_HOST=your-db-host
export DB_NAME=test_protocols
export DB_USER=your-user
export DB_PASSWORD=your-password
```

## Database Setup

### SQLite (Development)

```bash
sqlite3 data/test_protocols.db < database/schema.sql
```

### PostgreSQL (Production)

```bash
psql -h localhost -U postgres -d test_protocols -f database/schema.sql
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_protocols/test_corrosion_protocol.py

# Run with coverage
pytest --cov=protocols --cov=ui --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Documentation

Full documentation is available in the `docs/` directory:

- [Main Documentation](docs/index.md) - Framework overview and API reference
- [CORR-001 Protocol](docs/corr-001.md) - Detailed corrosion testing guide

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IEC and ASTM for test standards
- Streamlit team for the excellent UI framework
- SQLAlchemy team for the robust ORM
- The PV testing community for guidance and best practices

## Contact

- **Issues:** [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Email:** support@example.com
- **Documentation:** [docs/](docs/)

## Roadmap

### Version 0.2.0 (Planned)
- [ ] PDF report generation
- [ ] Additional test protocols (thermal cycling, mechanical load)
- [ ] LIMS integration implementation
- [ ] Advanced statistical analysis
- [ ] Multi-user authentication

### Version 0.3.0 (Planned)
- [ ] Real-time equipment monitoring
- [ ] Automated test scheduling
- [ ] Data import/export improvements
- [ ] Custom report templates
- [ ] Mobile-responsive UI
