# PV Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

The PV Test Protocols Framework is a flexible, extensible system for defining and executing standardized test protocols for photovoltaic modules. It combines the power of JSON-based protocol definitions with an intuitive web interface for test execution, data validation, and results reporting.

### Key Features

- **Dynamic Protocol Definition**: Define test protocols using JSON templates
- **Interactive Web UI**: Streamlit-based interface for guided test execution
- **Automatic Validation**: Real-time validation of measurements against acceptance criteria
- **Data Persistence**: SQLAlchemy-based database for storing test results and history
- **Visualization**: Automated chart and graph generation with Plotly
- **Standards Compliant**: Built to support IEC, UL, and other industry standards
- **Extensible**: Easy to add new protocols and customize existing ones
- **Integration Ready**: Designed for integration with LIMS, QMS, and project management systems

## Current Protocols

### TERM-001: Terminal Robustness Test

Comprehensive mechanical and electrical testing of PV module terminals including:
- Visual inspection
- Electrical continuity testing
- Pull force testing
- Torque testing
- Dielectric strength testing

**Standards**: IEC 61215-2:2021, IEC 61730-2:2016, UL 1703

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

# Initialize database
python -c "from src.database.connection import init_db; init_db()"
```

### Run the Application

```bash
streamlit run src/ui/streamlit_app.py
```

Open your browser to `http://localhost:8501`

## Project Structure

```
test-protocols/
├── src/
│   ├── protocols/           # Protocol definitions and implementations
│   │   ├── templates/       # JSON protocol templates
│   │   │   └── term-001.json
│   │   ├── base.py          # Base protocol classes
│   │   ├── models.py        # Pydantic data models
│   │   └── term001.py       # TERM-001 implementation
│   ├── database/            # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   └── connection.py    # Database connection
│   └── ui/                  # User interface
│       ├── streamlit_app.py # Main application
│       └── components/      # UI components
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── requirements.txt        # Dependencies
```

## Usage

### Starting a New Test

1. Navigate to **New Test** in the sidebar
2. Select a protocol (e.g., TERM-001)
3. Enter test information:
   - Module serial number
   - Operator name
   - Test conditions
4. Click **Start Test**

### Executing Test Steps

For each step:
1. Read the step description
2. Enter all required measurements
3. Click **Complete Step**

The system automatically:
- Validates measurements
- Checks acceptance criteria
- Calculates derived values
- Generates pass/fail results

### Viewing Results

- Navigate to **View Results**
- Filter by status, operator, or date
- Export reports to PDF or Excel

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Getting Started Guide](docs/getting-started.md)
- [Architecture Overview](docs/architecture.md)
- [TERM-001 Protocol Documentation](docs/term-001-protocol.md)
- [Protocol Format Specification](docs/README.md)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking
mypy src/
```

## Technology Stack

- **Backend**: Python 3.9+, SQLAlchemy, Pydantic
- **Frontend**: Streamlit, Plotly
- **Database**: SQLite (dev), PostgreSQL (production)
- **Testing**: pytest, pytest-cov

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Roadmap

- [ ] Additional test protocols (thermal, humidity, UV exposure)
- [ ] PDF report generation
- [ ] Excel export with formatting
- [ ] LIMS integration
- [ ] User authentication and role-based access
- [ ] Mobile-responsive design
- [ ] Statistical process control charts

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

Built for photovoltaic module testing and quality assurance teams.
