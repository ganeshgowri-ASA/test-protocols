# PV Test Protocol System Documentation

## Overview

The PV Test Protocol System is a comprehensive framework for executing, analyzing, and reporting photovoltaic module test protocols. The system provides JSON-based dynamic protocol templates with automated analysis, charting, quality control, and report generation capabilities.

## Features

- **JSON-Based Protocol Definitions:** Flexible, schema-driven protocol specifications
- **Dynamic UI Generation:** Streamlit/GenSpark interface auto-generated from protocol definitions
- **Automated Analysis:** Built-in statistical analysis and pass/fail evaluation
- **Quality Control:** Comprehensive QC checks with configurable rules
- **Report Generation:** Multi-format reports (PDF, HTML, Excel, JSON)
- **Database Integration:** PostgreSQL-backed data persistence with SQLAlchemy
- **LIMS/QMS Integration:** Ready for enterprise system integration
- **Extensible Architecture:** Easy to add new protocols and test types

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│              (Streamlit/GenSpark Web UI)                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────────────────┐
│                  Application Logic Layer                     │
├──────────────────────────────────────────────────────────────┤
│  Protocol Registry  │  Test Analyzer  │  QC Checker         │
│  Report Generator   │  Data Validator │  Integration Mgr    │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────────────────┐
│                    Data Layer                                │
├──────────────────────────────────────────────────────────────┤
│  PostgreSQL Database  │  Protocol JSON Files  │  Reports     │
└──────────────────────────────────────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────────────────┐
│               External Systems Integration                   │
├──────────────────────────────────────────────────────────────┤
│  LIMS  │  QMS Document Control  │  Project Management       │
└──────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   ├── base/              # Base protocol classes
│   ├── degradation/       # Degradation test protocols (UVID-001)
│   └── [other categories]
├── database/              # Database models and migrations
│   └── models/           # SQLAlchemy models
├── analysis/              # Data analysis modules
│   ├── degradation/      # Degradation-specific analysis
│   └── qc/              # Quality control modules
├── ui/                    # User interface
│   ├── pages/           # Streamlit pages
│   └── components/      # Reusable UI components
├── reports/               # Report generation
│   ├── templates/       # HTML report templates
│   └── generators/      # Report generators
├── tests/                 # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
├── docs/                  # Documentation
├── config/               # Configuration files
└── scripts/              # Utility scripts
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the UI

```bash
# Start Streamlit application
streamlit run ui/streamlit_app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_protocol.py
```

## Implemented Protocols

### UVID-001: UV-Induced Degradation

**Category:** Degradation
**Standard:** IEC 61215-2:2021 MQT 10
**Status:** ✅ Implemented

Evaluates PV module degradation under accelerated UV exposure. Measures electrical performance retention after 1000 hours of UV-A irradiance at 60°C.

**Key Features:**
- Automated I-V curve analysis
- Real-time degradation tracking
- Environmental condition monitoring
- Comprehensive pass/fail evaluation
- Visual defect inspection

**Documentation:** [UVID-001 Protocol](UVID-001_PROTOCOL.md)

## Core Components

### Protocol System

#### Protocol Definition (JSON)

Protocols are defined in JSON format with complete specification:

```json
{
  "protocol_id": "UVID-001",
  "name": "UV-Induced Degradation Protocol",
  "test_parameters": { ... },
  "measurement_points": [ ... ],
  "pass_fail_criteria": { ... },
  "qc_rules": { ... }
}
```

#### Protocol Class (Python)

```python
from protocols.base import Protocol

# Load protocol
protocol = Protocol('protocols/degradation/uvid_001.json')

# Validate parameters
is_valid, errors = protocol.validate_parameters(params)

# Evaluate results
results = protocol.evaluate_pass_fail(initial, final)
```

### Analysis Engine

```python
from analysis.analyzer import TestAnalyzer

analyzer = TestAnalyzer(protocol)

# Analyze test results
results = analyzer.evaluate_test_results(measurements_by_point)

# Generate trends
trends = analyzer.generate_degradation_trends(all_measurements)

# Calculate statistics
stats = analyzer.analyze_measurement_series(measurements, 'pmax')
```

### Quality Control

```python
from analysis.qc_checker import QCChecker

qc_checker = QCChecker(protocol.definition)

# Run all QC checks
qc_results = qc_checker.run_all_checks(test_data)

# Individual checks
repeatability = qc_checker.check_measurement_repeatability(values, 'pmax')
temp_stability = qc_checker.check_temperature_stability(temp_readings)
```

### Report Generation

```python
from reports.generator import ReportGenerator

generator = ReportGenerator(protocol.definition)

# Generate summary report
html_report = generator.generate_summary_report(test_execution, results)

# Save report
generator.save_report(html_report, output_path, format='html')

# Export data
generator.export_to_json(test_execution, results, measurements, json_path)
```

### Database Models

```python
from database.models import TestExecution, Measurement, TestResult

# Create test execution
test = TestExecution(
    test_number='UVID-001-2025-001',
    protocol_id='UVID-001',
    specimen_id=specimen.id,
    status=TestStatus.RUNNING
)

# Add measurements
measurement = Measurement(
    test_execution_id=test.id,
    measurement_point_id='initial',
    parameter_name='pmax',
    value=250.5,
    unit='W'
)

# Store results
result = TestResult(
    test_execution_id=test.id,
    pass_fail=PassFailStatus.PASS,
    criteria_evaluations=criteria_results
)
```

## Creating a New Protocol

### 1. Create JSON Definition

Create a new JSON file in the appropriate category directory:

```bash
touch protocols/[category]/[protocol_id].json
```

### 2. Define Protocol Structure

Follow the standard protocol schema:

```json
{
  "protocol_id": "YOUR-PROTOCOL-ID",
  "name": "Your Protocol Name",
  "version": "1.0.0",
  "category": "Category Name",
  "test_parameters": { ... },
  "measurement_points": [ ... ],
  "pass_fail_criteria": { ... },
  "qc_rules": { ... }
}
```

### 3. Register Protocol

```python
from protocols.base import ProtocolRegistry

registry = ProtocolRegistry()
registry.register_from_file('protocols/[category]/[protocol_id].json')
```

### 4. Create Tests

Add unit and integration tests in `tests/` directory.

### 5. Document Protocol

Create protocol documentation in `docs/[PROTOCOL_ID]_PROTOCOL.md`.

## API Reference

### Protocol Class

**Methods:**
- `validate_parameters(params)` - Validate test parameters
- `evaluate_pass_fail(initial, final)` - Evaluate pass/fail criteria
- `get_required_measurements()` - Get required measurement points
- `to_dict()` - Export protocol as dictionary

### TestAnalyzer Class

**Methods:**
- `calculate_retention(initial, final)` - Calculate retention percentage
- `calculate_degradation_rate(measurements, param)` - Calculate degradation rate
- `evaluate_test_results(measurements_by_point)` - Full test evaluation
- `generate_degradation_trends(measurements)` - Generate trend data

### QCChecker Class

**Methods:**
- `check_measurement_repeatability(values, param)` - Check repeatability
- `check_temperature_stability(readings)` - Check temp stability
- `check_irradiance_stability(readings)` - Check irradiance stability
- `check_data_completeness(expected, actual)` - Check data completeness
- `run_all_checks(test_data)` - Run all QC checks

### ReportGenerator Class

**Methods:**
- `generate_summary_report(test_exec, results)` - Generate summary HTML
- `generate_detailed_report(test_exec, results, measurements)` - Detailed HTML
- `export_to_json(test_exec, results, measurements, path)` - Export to JSON
- `save_report(content, path, format)` - Save report to file

## Testing

### Unit Tests

Test individual components in isolation:

```bash
pytest tests/unit/
```

### Integration Tests

Test complete workflows:

```bash
pytest tests/integration/
```

### Test Coverage

Generate coverage report:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Configuration

### Database Configuration

Edit `config/database.yaml`:

```yaml
database:
  host: localhost
  port: 5432
  name: test_protocols
  user: postgres
  password: your_password
```

### Application Configuration

Edit `config/settings.py`:

```python
DATABASE_URL = "postgresql://user:pass@localhost/test_protocols"
REPORT_OUTPUT_DIR = "reports/output"
LOG_LEVEL = "INFO"
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t test-protocols:latest .

# Run container
docker-compose up -d
```

### Production Considerations

1. **Database:** Use managed PostgreSQL service
2. **File Storage:** Configure S3 or similar for report storage
3. **Authentication:** Integrate with enterprise SSO
4. **Monitoring:** Set up application monitoring and alerts
5. **Backup:** Configure automated database backups

## Integration

### LIMS Integration

Synchronize specimen data and export results:

```python
from integrations.lims import LIMSClient

lims = LIMSClient(api_url, api_key)
specimen = lims.get_specimen(specimen_code)
lims.upload_results(test_execution_id, results)
```

### QMS Integration

Link to document control system:

```python
from integrations.qms import QMSClient

qms = QMSClient(qms_url, credentials)
qms.link_protocol(protocol_id, document_number)
```

## Troubleshooting

### Common Issues

**Issue:** Protocol not loading
**Solution:** Check JSON syntax and file path

**Issue:** Database connection error
**Solution:** Verify database configuration in config/database.yaml

**Issue:** Tests failing
**Solution:** Ensure all dependencies installed: `pip install -r requirements-dev.txt`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](../LICENSE) file

## Support

- **Documentation:** [docs/](.)
- **Issues:** GitHub Issues
- **Email:** support@pvtestlab.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Last Updated:** 2025-11-14
**Version:** 1.0.0
