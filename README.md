# Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Features

- **JSON-Based Protocol Definitions**: Flexible, schema-validated protocol configurations
- **Automated Test Execution**: Simulated, hardware, and file-based data acquisition
- **Real-Time Analysis**: Statistical analysis, QC checks, and performance metrics
- **Interactive UI**: Streamlit-based web interface for test management
- **Comprehensive Reporting**: Automated report generation with visualizations
- **Database Integration**: SQLite/PostgreSQL support for data persistence
- **Extensible Architecture**: Easy to add new test protocols and analysis methods

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
```

### Initialize Database

```bash
python scripts/init_db.py
```

### Run the UI

```bash
streamlit run src/ui/app.py
```

Open http://localhost:8501 in your browser.

## Available Protocols

### TRACK-001: Tracker Performance Test

Comprehensive performance evaluation of solar tracker systems including:
- Tracking accuracy measurement
- Response time analysis
- Power consumption monitoring
- Performance under various environmental conditions

**Documentation**: [TRACK-001 Overview](docs/track_001/overview.md)

## Project Structure

```
test-protocols/
├── src/                       # Source code
│   ├── core/                 # Core protocol engine
│   │   ├── protocol.py       # Base protocol implementation
│   │   ├── validator.py      # JSON schema validation
│   │   ├── analyzer.py       # Analysis and QC
│   │   └── report_generator.py
│   ├── tests/                # Test protocol implementations
│   │   └── track/
│   │       └── track_001/    # TRACK-001 implementation
│   ├── ui/                   # Streamlit UI
│   │   ├── app.py           # Main application
│   │   └── pages/           # UI pages
│   ├── integrations/         # External system integrations
│   └── utils/               # Utilities
├── schemas/                  # JSON schemas
│   ├── protocol-schema.json
│   ├── tracker-schema.json
│   └── examples/            # Example configurations
├── data/                     # Data and database
│   ├── db/                  # Database files
│   ├── fixtures/            # Test fixtures
│   └── reports/             # Generated reports
├── docs/                     # Documentation
│   ├── getting_started.md
│   ├── track_001/           # TRACK-001 docs
│   └── database.md
├── tests/                    # Unit and integration tests
│   ├── unit/
│   └── integration/
└── config/                   # Configuration files
    ├── dev.yaml
    ├── test.yaml
    └── prod.yaml
```

## Usage Example

```python
from src.tests.track.track_001.protocol import TRACK001Protocol
from src.tests.track.track_001.test_runner import TRACK001TestRunner
from src.core.protocol import ProtocolEngine

# Load protocol from JSON
protocol = ProtocolEngine.from_json('schemas/examples/track_001_example.json')

# Create test runner
runner = TRACK001TestRunner(protocol)

# Run test
run_id = runner.run_test(
    data_source="simulated",
    operator="Engineer Name",
    sample_id="TRACKER-001",
    latitude=40.0,
    longitude=-105.0
)

# Analyze results
results = protocol.analyze_results()

# Get summary
summary = protocol.get_test_summary()
print(f"Test {run_id}: {summary['status']}")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/integration/test_track_001.py
```

## Documentation

- [Getting Started Guide](docs/getting_started.md)
- [TRACK-001 Protocol](docs/track_001/overview.md)
- [Implementation Guide](docs/track_001/implementation.md)
- [Analysis Methods](docs/track_001/analysis_methods.md)
- [QC Criteria](docs/track_001/qc_criteria.md)
- [Database Schema](docs/database.md)

## Configuration

The framework supports three environments:

- **Development** (`config/dev.yaml`) - For local development
- **Test** (`config/test.yaml`) - For automated testing
- **Production** (`config/prod.yaml`) - For production deployment

Set the environment:
```bash
export APP_ENV=production
```

## Technology Stack

- **Python 3.9+**: Core language
- **Streamlit**: Web UI framework
- **SQLAlchemy**: Database ORM
- **Pandas & NumPy**: Data analysis
- **Plotly**: Interactive visualizations
- **Pytest**: Testing framework
- **JSON Schema**: Protocol validation

## Contributing

1. Follow the existing code structure
2. Write tests for new features
3. Update documentation
4. Use type hints
5. Follow PEP 8 style guide

## Extending the Framework

### Adding a New Protocol

1. Create a new directory in `src/tests/`
2. Define JSON schema in `schemas/`
3. Implement protocol class extending `ProtocolEngine`
4. Create test runner and analyzer
5. Add documentation
6. Write tests

See [TRACK-001 implementation](src/tests/track/track_001/) as a reference.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please contact the development team.

## Version

Current Version: 0.1.0

## Authors

Test Protocols Team
