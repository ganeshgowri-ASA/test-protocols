# PV Testing Protocol Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## 🎯 Overview

This framework provides a comprehensive, modular system for managing and executing photovoltaic (PV) module testing protocols with emphasis on:

- **Flexibility**: JSON-based protocol definitions allow easy customization
- **Automation**: Automated analysis, quality control, and reporting
- **Standards Compliance**: Built-in support for IEC 61853, IEC 60904, and other standards
- **Traceability**: Complete audit trail and version control
- **Integration**: Ready for LIMS, QMS, and project management system integration

## ✨ Features

### Core Capabilities

- 🔧 **Dynamic Protocol Management**: JSON-driven protocol definitions
- 📊 **Interactive UI**: Streamlit-based user interface for data collection
- 🧮 **Automated Analysis**: Real-time calculations and statistical analysis
- ✅ **Quality Control**: Comprehensive QC checks with configurable thresholds
- 📈 **Advanced Visualization**: Interactive Plotly charts and dashboards
- 📄 **Multi-Format Reports**: Generate PDF, HTML, JSON, and Excel reports
- 🗄️ **Database Integration**: SQLAlchemy-based data persistence
- 🔍 **Full Traceability**: Audit trails, version control, and digital signatures

### PERF-002 Protocol

The flagship implementation includes **PERF-002: Performance Testing at Different Irradiances**

- Tests at 7 irradiance levels: 100, 200, 400, 600, 800, 1000, 1100 W/m²
- Full I-V curve characterization (≥100 points per curve)
- Spatial uniformity analysis (5×5 measurement grid)
- Efficiency and fill factor calculations
- Linearity analysis with R² determination
- IEC 61853 compliant

## 📁 Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions (JSON)
│   └── PERF/
│       └── PERF-002/      # Performance testing protocol
│           ├── protocol.json
│           └── schema.json
├── src/                   # Core application code
│   ├── core/             # Protocol loading and validation
│   ├── database/         # Database models and connection
│   ├── analysis/         # Calculation and analysis modules
│   ├── visualization/    # Chart generation
│   ├── reports/          # Report generation
│   └── utils/            # Utilities and logging
├── ui/                   # Streamlit user interface
│   ├── app.py           # Main application
│   ├── pages/           # Multi-page UI
│   └── components/      # Reusable UI components
├── tests/               # Comprehensive test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test data
├── docs/               # Documentation
│   ├── protocols/     # Protocol documentation
│   └── api/          # API documentation
├── config/            # Configuration files
└── scripts/          # Utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/test-protocols.git
   cd test-protocols
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

4. **Launch the UI**
   ```bash
   streamlit run ui/app.py
   ```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

### Running a Test

1. **Select Protocol**: Choose PERF-002 from the sidebar
2. **Create Test Run**: Enter test run information (operator, module serial, etc.)
3. **Data Collection**: Enter or import measurement data
4. **Analysis**: View automated analysis results and charts
5. **QC Review**: Check quality control status
6. **Generate Report**: Export results in desired format

### Programmatic Usage

```python
from src.core.protocol_loader import get_protocol_loader
from src.analysis.calculations import PERF002Analyzer
from src.database.connection import get_db_manager

# Load protocol
loader = get_protocol_loader()
protocol = loader.load("PERF-002")

# Analyze data
analyzer = PERF002Analyzer(module_area=2.0)
results = analyzer.analyze_test_run(measurements)

# Access database
db_manager = get_db_manager()
with db_manager.session_scope() as session:
    test_runs = session.query(TestRun).all()
```

## 🔬 Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_protocols.py

# Specific test
pytest tests/unit/test_analysis.py::TestIVCurveAnalyzer::test_find_mpp
```

## 📊 Data Model

### Protocol

Defines test procedures, requirements, and configurations in JSON format.

### Test Run

Individual execution of a protocol with metadata (operator, module, conditions).

### Measurements

Raw measurement data points collected during testing.

### Analysis Results

Calculated parameters (Pmax, efficiency, fill factor, etc.).

### QC Checks

Quality control validation results with pass/fail status.

## 🔧 Configuration

### Database

Edit `config/database.yaml` to configure database connection:

```yaml
database:
  development:
    type: sqlite
    path: ./data/test_protocols.db
```

### Logging

Configure logging in `config/logging.yaml`:

```yaml
logging:
  level: INFO
  handlers: [console, file]
```

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
APP_ENV=development
LOG_LEVEL=INFO
DB_PATH=./data/test_protocols.db
```

## 📚 Documentation

- **Protocol Documentation**: `docs/protocols/PERF-002.md`
- **Architecture Guide**: `docs/architecture.md` (coming soon)
- **API Reference**: `docs/api/` (coming soon)
- **User Guide**: `docs/user_guide/` (coming soon)

## 🔌 Integration

### LIMS Integration

```json
{
  "lims": {
    "enabled": true,
    "api_url": "https://lims.example.com/api",
    "auto_upload": true
  }
}
```

### QMS Integration

Automatic NCR (Non-Conformance Report) creation on QC failures.

### Project Management

Test status updates and milestone tracking.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting: `black src/`
- Run linting: `flake8 src/`
- Type hints: `mypy src/`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **ganeshgowri-ASA** - Initial work and PERF-002 implementation

## 🙏 Acknowledgments

- IEC Technical Committee 82 for PV testing standards
- The Streamlit team for the excellent UI framework
- The Python scientific computing community

## 📞 Support

For questions or support:

- Open an issue on GitHub
- Check the documentation in `docs/`
- Review protocol specifications

## 🗺️ Roadmap

- [ ] Additional protocols (ELEC, MECH, ENV)
- [ ] Advanced statistical analysis
- [ ] Machine learning integration
- [ ] Cloud deployment
- [ ] Mobile app
- [ ] Real-time monitoring
- [ ] Multi-language support

## 📈 Status

**Current Version**: 1.0.0
**Status**: Production-ready with PERF-002 protocol
**Last Updated**: 2025-11-13

---

Made with ⚡ for the PV testing community
