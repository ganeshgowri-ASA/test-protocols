# PV Test Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

The PV Test Protocol Framework is a comprehensive system for managing, executing, and analyzing standardized tests for photovoltaic modules. It provides a flexible, JSON-driven approach to test protocol definition and execution with an intuitive web-based interface.

### Key Features

- **JSON-Based Protocol Definitions**: Define test protocols declaratively in JSON
- **Dynamic UI Generation**: Streamlit interface automatically adapts to protocol requirements
- **Automated Analysis**: Built-in statistical analysis and degradation calculations
- **Interactive Visualization**: Plotly-based charts and dashboards
- **Pass/Fail Evaluation**: Automatic evaluation against defined criteria
- **Quality Control Tracking**: Integrated QC checks throughout testing
- **Report Generation**: Export results in JSON, PDF, and Excel formats
- **Database Integration**: PostgreSQL backend for data persistence
- **Type Safety**: Pydantic models for robust data validation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run src/ui/app.py
```

The application will open in your browser at `http://localhost:8501`.

### Running Your First Test

1. Select the **VIBR-001** protocol from the main page
2. Review the protocol details and requirements
3. Click on the "Start Test" tab
4. Enter operator information and sample details
5. Configure test parameters
6. Click "Start Test Session"
7. Follow the guided workflow to collect measurements
8. Complete the test and view results

## Implemented Protocol: VIBR-001

### Transportation Vibration Test

The VIBR-001 protocol implements the **IEC 62759-1:2022** transportation vibration test for PV modules.

#### Test Overview

- **Purpose**: Evaluate module resistance to vibration during transportation
- **Standard**: IEC 62759-1:2022
- **Category**: Mechanical Testing
- **Duration**: ~3.5 hours
- **Sample Size**: Minimum 2 modules

#### Test Parameters

| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| Frequency Range | 5-200 | Hz | Random vibration frequency range |
| Vibration Severity | ≥ 0.49 | g RMS | Root mean square acceleration |
| Test Duration | ≥ 180 | minutes | Minimum exposure time |
| Test Axis | Vertical | - | Primary test orientation |

#### Test Sequence

1. **Sample Conditioning** (24 hours)
   - Temperature: 23°C ± 5°C
   - Humidity: 50% ± 10% RH

2. **Pre-Test Measurements**
   - Visual inspection
   - Electrical performance (Pmax, Voc, Isc, Vmp, Imp, FF)

3. **Vibration Test** (180 minutes)
   - Random vibration per IEC 62759-1
   - Continuous monitoring
   - Real-time data collection

4. **Post-Test Measurements**
   - Visual inspection
   - Electrical performance
   - Insulation resistance

#### Pass/Fail Criteria

| Criterion | Limit | Description |
|-----------|-------|-------------|
| Power Degradation | ≤ 5% | (Pre_Pmax - Post_Pmax) / Pre_Pmax |
| Visual Defects | 0 critical | No cracks, delamination, breakage |
| Insulation Resistance | ≥ 40 MΩ | At 1000V DC |
| Voc Degradation | ≤ 2% | Open circuit voltage |
| Isc Degradation | ≤ 2% | Short circuit current |
| FF Degradation | ≤ 3% | Fill factor |

## Project Structure

```
test-protocols/
├── protocols/                  # Protocol definitions (JSON)
│   ├── schemas/               # JSON validation schemas
│   ├── mechanical/
│   │   └── VIBR-001.json     # Transportation vibration test
│   ├── environmental/
│   └── electrical/
│
├── src/                       # Python source code
│   ├── core/                  # Core framework components
│   │   ├── protocol_loader.py
│   │   └── test_executor.py
│   ├── models/                # Pydantic data models
│   │   ├── protocol.py
│   │   └── test_result.py
│   ├── analysis/              # Analysis modules
│   │   ├── statistical.py
│   │   └── charting.py
│   └── ui/                    # Streamlit UI
│       └── app.py
│
├── database/                  # Database schemas
│   ├── schema.sql
│   └── migrations/
│
├── tests/                     # Unit and integration tests
│   ├── test_protocol_loader.py
│   ├── test_executor.py
│   └── test_analysis.py
│
├── docs/                      # Documentation
│   ├── architecture.md
│   └── user_guide.md
│
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
└── README.md
```

## Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **Pydantic**: Data validation and serialization
- **NumPy/SciPy**: Scientific computing
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualization
- **JSONSchema**: Protocol validation

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive charts

### Database
- **PostgreSQL**: Data persistence
- **SQLAlchemy**: ORM (planned)

### Testing
- **pytest**: Unit and integration testing
- **pytest-cov**: Code coverage

## Architecture

The framework follows a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│         UI Layer (Streamlit)            │
├─────────────────────────────────────────┤
│      Application Layer                  │
│  - Protocol Loader                      │
│  - Test Executor                        │
│  - Analysis Engine                      │
├─────────────────────────────────────────┤
│         Data Layer                      │
│  - Protocol JSON                        │
│  - PostgreSQL Database                  │
└─────────────────────────────────────────┘
```

### Core Components

#### ProtocolLoader
Loads and validates JSON protocol definitions, provides querying capabilities.

#### TestExecutor
Manages test session lifecycle, collects measurements, evaluates pass/fail criteria.

#### Statistical Analysis
Provides degradation calculations, statistical summaries, PSD analysis.

#### Charting Engine
Generates interactive Plotly charts: I-V curves, power comparisons, degradation plots.

## Usage Examples

### Loading a Protocol

```python
from src.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol('VIBR-001')

print(f"Protocol: {protocol.name}")
print(f"Standard: {protocol.standard}")
print(f"Sample Size: {protocol.sample_requirements.sample_size.min}")
```

### Executing a Test

```python
from src.core.test_executor import TestExecutor
from src.models.test_result import Sample

# Create executor
executor = TestExecutor(protocol)

# Start session
session = executor.start_session(
    operator_name='John Doe',
    parameters={'vibration_severity': 0.5, 'test_duration': 180},
    samples=[Sample(sample_id='TEST-001', manufacturer='TestCorp')]
)

# Add measurements
executor.add_measurement(
    measurement_id='electrical_performance_pre',
    data={'Pmax': 300.5, 'Voc': 45.6, 'Isc': 8.9}
)

# Complete and evaluate
executor.complete_session()
result = executor.evaluate_results()

print(f"Overall Status: {result.overall_status}")
```

### Statistical Analysis

```python
from src.analysis.statistical import calculate_degradation

pre_power = 300.0
post_power = 285.0

degradation = calculate_degradation(pre_power, post_power, percentage=True)
print(f"Power degradation: {degradation:.2f}%")
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_protocol_loader.py -v
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Architecture Documentation](docs/architecture.md): System design and components
- [User Guide](docs/user_guide.md): Complete usage instructions
- API Reference: Detailed API documentation (coming soon)

## Database Setup (Optional)

To enable database persistence:

1. Install PostgreSQL 12+
2. Create database:
   ```bash
   createdb pv_test_protocols
   ```
3. Run schema:
   ```bash
   psql -d pv_test_protocols -f database/schema.sql
   ```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
```

### Creating New Protocols

1. Create JSON file in appropriate category directory
2. Follow the protocol schema structure (see `protocols/schemas/base_protocol.schema.json`)
3. Validate:
   ```python
   from src.core.protocol_loader import ProtocolLoader
   loader = ProtocolLoader()
   is_valid, error = loader.validate_protocol_file('path/to/protocol.json')
   ```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Ensure all tests pass
6. Submit a pull request

## Roadmap

### Upcoming Features

- [ ] PDF report generation
- [ ] Excel export with charts
- [ ] Real-time data acquisition from test equipment
- [ ] Additional test protocols (thermal cycling, humidity-freeze, etc.)
- [ ] REST API for external integrations
- [ ] Multi-user support with authentication
- [ ] Cloud deployment option
- [ ] Machine learning for predictive analysis
- [ ] Mobile application

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on IEC 62759-1:2022 and IEC 61215-1:2021 standards
- Built with Streamlit, Pydantic, and Plotly
- Inspired by best practices in PV module quality testing

## Support

For questions, issues, or feature requests:

- GitHub Issues: [https://github.com/ganeshgowri-ASA/test-protocols/issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- Documentation: [docs/](docs/)
- Email: info@test-protocols.com

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{pv_test_protocols,
  title = {PV Test Protocol Framework},
  author = {Test Protocols Team},
  year = {2024},
  url = {https://github.com/ganeshgowri-ASA/test-protocols}
}
```

---

**Note**: This framework is designed for professional testing environments. Ensure proper training and equipment calibration before conducting actual qualification testing.
