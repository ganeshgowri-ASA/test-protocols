# PV Test Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

The PV Test Protocol Framework provides a comprehensive, modular system for managing and executing photovoltaic module testing protocols. Built with flexibility and extensibility in mind, it uses JSON-based protocol definitions to drive interactive test execution, real-time monitoring, and automated analysis.

## Features

- **JSON-Driven Protocol Definitions**: Define test protocols using structured JSON
- **Interactive UI**: Streamlit-based interface for test execution and monitoring
- **Real-Time Monitoring**: Live tracking of chamber conditions and test progress
- **Automated Analysis**: Statistical analysis, trend detection, and outlier identification
- **Data Visualization**: Interactive charts and dashboards
- **Database Persistence**: SQLite database for reliable data storage
- **Standards Compliance**: IEC 61215 compliant test protocols
- **Extensible Architecture**: Easy to add new protocols and test types
- **Integration Ready**: Designed for LIMS, QMS, and project management integration

## Implemented Protocols

### TROP-001 - Tropical Climate Test

Combined high temperature and humidity exposure test per IEC 61215-2:2021 MQT 24.

**Test Conditions**:
- Temperature: 85°C ± 2°C
- Relative Humidity: 85% ± 5%
- Duration: 2400 hours (100 cycles × 24 hours)

**Acceptance Criteria**:
- Visual: No major defects
- Electrical: ≤5% power degradation
- Insulation: ≥40 MΩ resistance

## Project Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   ├── climate/           # Climate/environmental tests
│   │   └── trop-001.json
│   ├── mechanical/        # Mechanical tests
│   └── electrical/        # Electrical tests
├── src/                   # Python source code
│   ├── core/             # Core protocol engine
│   │   ├── protocol_loader.py
│   │   ├── test_engine.py
│   │   └── models.py
│   ├── ui/               # Streamlit UI components
│   │   ├── app.py
│   │   └── tropical_climate_ui.py
│   ├── analysis/         # Data analysis modules
│   │   ├── data_analyzer.py
│   │   └── chart_generator.py
│   └── integrations/     # LIMS, QMS integrations
├── tests/                # Unit/integration tests
│   ├── unit/
│   └── integration/
├── docs/                 # Documentation
│   ├── TROP-001_USER_GUIDE.md
│   └── TECHNICAL_DOCUMENTATION.md
├── database/             # Database schemas/migrations
│   ├── schema.sql
│   └── db_manager.py
└── examples/             # Example protocols
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python -c "from database.db_manager import DatabaseManager; DatabaseManager().initialize_database()"
```

### Running the Application

**Main Application** (protocol browser):
```bash
streamlit run src/ui/app.py
```

**TROP-001 Interface** (tropical climate test):
```bash
streamlit run src/ui/tropical_climate_ui.py
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run unit tests only
python -m unittest discover tests/unit

# Run integration tests only
python -m unittest discover tests/integration
```

## Usage Example

### Load a Protocol

```python
from src.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("TROP-001")
print(f"Protocol: {protocol['name']}")
print(f"Duration: {protocol['test_sequence']['total_test_duration']} hours")
```

### Execute a Test

```python
from src.core.test_engine import TestEngine

# Initialize test engine
engine = TestEngine(protocol, "TEST-001")

# Start test with modules
modules = ["MOD001", "MOD002", "MOD003"]
result = engine.start_test(modules, operator="John Doe")

# Record measurements
engine.record_measurement("temperature", 85.0, "°C")
engine.record_measurement("relative_humidity", 85.0, "%")

# Check status
status = engine.get_status()
print(f"Progress: {status['progress_percent']}%")
```

### Analyze Data

```python
from src.analysis.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()

# Calculate statistics
stats = analyzer.calculate_statistics(temperature_values)
print(f"Mean: {stats['mean']:.2f}°C")
print(f"Std Dev: {stats['std_dev']:.2f}°C")

# Detect outliers
outliers = analyzer.detect_outliers(temperature_values, threshold=3.0)
print(f"Found {len(outliers)} outliers")
```

## Documentation

- **User Guide**: [TROP-001 User Guide](docs/TROP-001_USER_GUIDE.md)
- **Technical Documentation**: [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)
- **API Reference**: See docstrings in source code

## Testing

The framework includes comprehensive unit and integration tests:

- **Protocol Loader Tests**: Validate protocol loading and parsing
- **Test Engine Tests**: Test execution logic and state management
- **Database Tests**: Database operations and data persistence
- **Analysis Tests**: Statistical analysis and calculations

Test coverage aims for >80% of critical code paths.

## Development

### Adding a New Protocol

1. Create JSON definition in `protocols/category/`
2. Follow the protocol schema (see existing protocols)
3. Include all required fields:
   - `protocol_id`, `version`, `name`, `category`
   - `test_sequence` with steps
   - `acceptance_criteria`
4. Test with protocol loader
5. Document in `docs/`

### Creating a Custom UI

1. Create new file in `src/ui/`
2. Import required modules:
   ```python
   import streamlit as st
   from core.protocol_loader import ProtocolLoader
   from core.test_engine import TestEngine
   ```
3. Implement UI tabs for setup, execution, monitoring, analysis
4. Add to main app navigation

### Extending Analysis

1. Add methods to `DataAnalyzer` class
2. Implement custom calculations
3. Integrate with `ChartGenerator` for visualizations
4. Add to UI analysis tab

## Integration

The framework supports integration with:

- **LIMS** (Laboratory Information Management System)
- **QMS** (Quality Management System)
- **Project Management** tools

Integration configuration in protocol JSON:
```json
"integrations": {
  "lims": {
    "enabled": true,
    "endpoints": ["/api/v1/test-results"]
  },
  "qms": {
    "enabled": true,
    "document_references": ["SOP-ENV-001"]
  }
}
```

## Standards Compliance

The framework implements protocols compliant with:

- **IEC 61215-2:2021**: PV modules - Design qualification and type approval
- **IEC 61215-1:2021**: Testing of crystalline silicon PV modules
- **IEC 60904-9**: Solar simulator classification

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Contact the development team

## Acknowledgments

Built for photovoltaic module testing laboratories to streamline test execution, improve data quality, and ensure standards compliance.

## Version

Current Version: 1.0.0 (Initial Release)

## Changelog

### Version 1.0.0 (2025-11-14)
- Initial release
- TROP-001 Tropical Climate Test protocol
- Core test execution engine
- Streamlit UI interface
- SQLite database integration
- Data analysis and visualization
- Comprehensive documentation
- Unit and integration tests
