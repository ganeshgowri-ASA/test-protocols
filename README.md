# PV Testing Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

A comprehensive framework for managing and executing photovoltaic (PV) module testing protocols with a focus on automation, validation, and integration. The first implemented protocol is **DELAM-001**: Delamination testing with electroluminescence (EL) image analysis per IEC 61215:2021.

## Features

### Core Capabilities
- **JSON-Based Protocol Definitions**: Flexible, version-controlled protocol configurations
- **Automated Validation**: Comprehensive data validation with configurable rules
- **EL Image Analysis**: Advanced defect detection and delamination quantification
- **Streamlit UI**: Interactive web interface for test management
- **Database Integration**: SQLAlchemy-based data persistence
- **Report Generation**: Automated test reports in multiple formats
- **LIMS/QMS Integration**: Ready for enterprise system integration

### DELAM-001 Protocol Features
- IEC 61215:2021 compliant delamination testing
- Environmental chamber monitoring (temperature, humidity, pressure)
- Automated EL image analysis with defect detection
- Configurable acceptance criteria
- Multi-interval inspection support (0h, 250h, 500h, 1000h)
- Severity classification (none, minor, moderate, severe, critical)
- Pass/fail determination based on multiple criteria

## Project Structure

```
test-protocols/
├── protocols/               # Protocol definitions
│   ├── schemas/            # JSON schemas
│   └── delam_001/          # DELAM-001 implementation
│       ├── definition.py   # Protocol configuration
│       ├── validation.py   # Validation rules
│       ├── analysis.py     # EL analysis
│       └── templates/      # Default configurations
├── models/                  # Database models
├── ui/                      # Streamlit UI
│   └── streamlit/
│       ├── app.py          # Main application
│       └── pages/          # UI pages
├── validation/              # Validation framework
├── analysis/                # Analysis modules
├── database/                # Database layer
├── config/                  # Configuration
├── tests/                   # Test suite
└── requirements.txt        # Dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) PostgreSQL for production database

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python -c "from database import init_db; init_db()"
```

## Usage

### Running the Streamlit UI

```bash
streamlit run ui/streamlit/app.py
```

Access the application at `http://localhost:8501`

### Using the Protocol Programmatically

```python
from protocols.delam_001 import DELAM001Protocol, DELAM001Analyzer, DELAM001Validator

# Load protocol
protocol = DELAM001Protocol()

# Analyze EL image
analyzer = DELAM001Analyzer()
results = analyzer.analyze_image('path/to/el_image.tiff')

print(f"Delamination detected: {results.delamination_detected}")
print(f"Affected area: {results.delamination_area_percent:.2f}%")
print(f"Severity: {results.severity_level}")

# Validate test data
validator = DELAM001Validator()
is_valid, errors = validator.validate_module_id("MOD-2025-001")

# Check acceptance criteria
passed, details = protocol.check_acceptance_criteria({
    'delamination_area_percent': 3.0,
    'power_degradation_percent': 2.0
})
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=models --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest tests/unit/test_delam_001_validation.py
```

## DELAM-001 Protocol Details

### Test Conditions
- **Temperature**: 85°C ± 2°C
- **Humidity**: 85% RH ± 5%
- **Duration**: 1000 hours
- **Inspection Intervals**: 0, 250, 500, 1000 hours

### Acceptance Criteria
- Maximum delamination area: 5% of module area
- Maximum power degradation: 5%
- No visual defects (bubbles, discoloration, broken cells)
- Minimum fill factor: 0.70

### Required Equipment
- Environmental chamber (0-100°C, 10-98% RH, ≥1m³)
- EL camera system (InGaAs or Si CCD, ≥2MP, ≥12-bit)
- IV curve tracer (0-100V, 0-20A, ±0.5% accuracy)
- Solar simulator or LED array (850nm, ±5% uniformity)

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=sqlite:///./test_protocols.db

# Analysis Parameters
DEFAULT_DEFECT_THRESHOLD=0.15
DEFAULT_MIN_DEFECT_AREA=10.0

# LIMS Integration
LIMS_ENABLED=False
LIMS_URL=https://your-lims-system.com
LIMS_API_KEY=your-api-key

# File Storage
DATA_DIR=./data
RESULTS_DIR=./results
IMAGES_DIR=./images
```

## Development

### Code Style

The project follows:
- PEP 8 style guide
- Black code formatting
- Type hints with mypy
- Docstrings for all public APIs

### Running Code Quality Tools

```bash
# Format code
black .

# Check formatting
flake8

# Type checking
mypy protocols models

# Sort imports
isort .
```

### Adding a New Protocol

1. Create protocol directory: `protocols/your_protocol/`
2. Define JSON schema in `protocols/schemas/`
3. Implement protocol class extending base
4. Add validation rules
5. Create analysis modules as needed
6. Add UI pages in `ui/streamlit/pages/`
7. Write comprehensive tests
8. Update documentation

## Database Schema

The framework uses SQLAlchemy with the following main models:
- **Protocol**: Protocol definitions and metadata
- **ProtocolVersion**: Version control for protocols
- **Module**: PV module information
- **Sample**: Test samples
- **TestExecution**: Test run records
- **TestMeasurement**: Measurement data points
- **TestResult**: Test outcomes and pass/fail
- **AnalysisResult**: EL analysis results
- **DefectRegion**: Individual defect details

## API Documentation

### Protocol API

```python
# Load default protocol
protocol = DELAM001Protocol()

# Load from file
protocol = DELAM001Protocol.load('config.json')

# Access configuration
env_conditions = protocol.environmental_conditions
test_duration = protocol.test_duration
acceptance_criteria = protocol.acceptance_criteria

# Validate test data
is_valid, errors = protocol.validate_test_data(test_data)

# Check acceptance
passed, details = protocol.check_acceptance_criteria(results)
```

### Analysis API

```python
# Single image analysis
analyzer = DELAM001Analyzer()
results = analyzer.analyze_image(image_path, metadata)

# Batch analysis
results = analyzer.analyze_batch(image_paths, metadata_list)

# Compare images
comparison = analyzer.compare_images(baseline_image, test_image)

# Get summary
summary = analyzer.get_analysis_summary()
```

### Validation API

```python
validator = DELAM001Validator(protocol_config)

# Validate different data types
is_valid, errors = validator.validate_module_id(module_id)
is_valid, errors = validator.validate_environmental_data(env_data)
is_valid, errors = validator.validate_el_image_metadata(metadata)
is_valid, errors = validator.validate_measurement_data(measurements)
is_valid, errors = validator.validate_analysis_results(results)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit changes (`git commit -am 'Add new protocol'`)
6. Push to branch (`git push origin feature/new-protocol`)
7. Create Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Standards Compliance

- IEC 61215:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
- IEC 61730 - Photovoltaic (PV) module safety qualification
- ISO 9001 - Quality management systems
- ISO/IEC 17025 - Testing and calibration laboratories

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Documentation: See `docs/` directory
- Email: testing@example.com

## Roadmap

### Planned Features
- [ ] Additional IEC 61215 protocols (thermal cycling, humidity-freeze, etc.)
- [ ] Advanced image processing algorithms
- [ ] Machine learning for defect classification
- [ ] Real-time dashboard for test monitoring
- [ ] Mobile app for data entry
- [ ] Cloud deployment option
- [ ] Multi-language support
- [ ] Advanced reporting with custom templates

### Future Protocols
- THERMAL-001: Thermal cycling test
- HUMID-001: Humidity-freeze test
- MECH-001: Mechanical load test
- UV-001: UV preconditioning test

## Acknowledgments

- IEC 61215 standard for protocol specifications
- OpenCV and scikit-image for image analysis
- Streamlit for the web interface
- SQLAlchemy for database management

---

**Version**: 1.0.0
**Last Updated**: January 2025
**Status**: Active Development
