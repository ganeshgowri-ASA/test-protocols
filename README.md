# PV Testing Protocol Framework

> Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

This framework provides a standardized, scalable approach to managing photovoltaic (PV) module testing protocols. It features:

- **Dynamic Protocol Configuration**: JSON-based protocol definitions
- **Interactive UI**: Streamlit/GenSpark web interface for test execution
- **Automated Analysis**: Built-in statistical analysis and trend detection
- **Quality Control**: Automated QC checks and validation
- **Report Generation**: PDF reports with visualizations
- **Database Integration**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **LIMS/QMS Integration**: Ready for enterprise system integration

## Features

### Implemented Protocols

#### SNAIL-001: Snail Trail Formation Test
- **Category**: Degradation
- **Standard**: IEC 61215-2:2021 MQT 13 (modified)
- **Duration**: 1000 hours
- **Purpose**: Assess snail trail formation under accelerated environmental exposure

### Core Capabilities

- **Protocol Management**
  - JSON-based protocol definitions
  - Version control and audit trail
  - Extensible architecture for new protocols

- **Data Collection**
  - Dynamic form generation from protocol schemas
  - Real-time validation
  - Image upload and management

- **Analysis Engine**
  - Automated degradation calculations
  - Statistical trend analysis
  - Correlation studies
  - QC check execution

- **Visualization**
  - Interactive Plotly charts
  - Time-series analysis
  - Correlation plots
  - Custom chart configurations per protocol

- **Reporting**
  - Automated PDF report generation
  - Configurable report sections
  - Include charts and images
  - Pass/fail assessment

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

### Running the Application

```bash
# Launch Streamlit UI
streamlit run ui/streamlit_app.py

# The application will open in your browser at http://localhost:8501
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=database --cov=ui

# Run specific test file
pytest tests/unit/test_snail_trail_formation.py -v
```

## Project Structure

```
test-protocols/
├── protocols/                  # Protocol implementations
│   ├── base_protocol.py       # Abstract base class
│   └── degradation/           # Degradation category
│       ├── snail_trail_formation.json
│       └── snail_trail_formation.py
├── ui/                        # Streamlit UI
│   ├── streamlit_app.py      # Main application
│   ├── components/           # Reusable UI components
│   └── pages/                # Multi-page sections
├── database/                  # Database layer
│   ├── models.py             # SQLAlchemy ORM models
│   └── db_config.py          # Database configuration
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── docs/                      # Documentation
│   └── protocols/            # Protocol documentation
└── requirements.txt          # Python dependencies
```

## Usage

### Via Web UI

1. **Start the Application**
   ```bash
   streamlit run ui/streamlit_app.py
   ```

2. **Select Protocol**
   - Choose SNAIL-001 from the protocol selector

3. **Enter Module Information**
   - Fill in module details in the Setup tab
   - All required fields marked with *

4. **Add Measurements**
   - Navigate to Data Entry tab
   - Select inspection interval
   - Enter visual and electrical measurements
   - Add measurements for all intervals

5. **Run Analysis**
   - Click "Run Protocol Analysis"
   - View results in Results tab

6. **Generate Report**
   - Click "Generate PDF Report"
   - Download comprehensive test report

### Via Python API

```python
from pathlib import Path
from protocols.degradation.snail_trail_formation import SnailTrailFormationProtocol

# Initialize protocol
protocol = SnailTrailFormationProtocol()

# Prepare test data
test_data = {
    'input_params': {
        'module_id': 'TEST-MODULE-001',
        'manufacturer': 'Solar Inc.',
        'model_number': 'SI-400',
        'cell_technology': 'mono-PERC',
        'nameplate_power_w': 400.0,
        'initial_isc_a': 10.5,
        'initial_voc_v': 48.2,
        'initial_pmax_w': 400.0,
        'initial_ff_percent': 79.2,
        'test_start_date': '2025-01-14',
        'operator_id': 'OP-001'
    },
    'measurements': [
        {
            'inspection_hour': 0,
            'visual_snail_trail_severity': 'none',
            'affected_cells_count': 0,
            'affected_area_percent': 0.0,
            'pmax_w': 400.0,
            'isc_a': 10.5,
            'voc_v': 48.2,
            'ff_percent': 79.2,
            'notes': 'Initial measurement'
        },
        # Add more measurements...
    ]
}

# Run protocol
result = protocol.run(test_data)

# Check results
if result.status == "completed":
    print(f"Test Result: {result.analysis_results['pass_fail']['overall']['result']}")
    print(f"Power Degradation: {result.analysis_results['power_degradation']['degradation_percent']:.2f}%")

# Generate report
report_path = protocol.generate_report(Path('./reports'))
print(f"Report saved to: {report_path}")
```

## Adding New Protocols

1. **Create Protocol JSON Definition**
   ```json
   {
     "protocol_id": "NEW-PROTOCOL-001",
     "name": "New Test Protocol",
     "category": "Category",
     "version": "1.0.0",
     "description": "Protocol description",
     "test_conditions": {},
     "input_parameters": [],
     "measurements": [],
     "qc_checks": [],
     "pass_fail_criteria": []
   }
   ```

2. **Implement Protocol Class**
   ```python
   from protocols.base_protocol import BaseProtocol

   class NewProtocol(BaseProtocol):
       def run(self, test_data):
           # Implementation
           pass

       def analyze_results(self):
           # Analysis logic
           pass

       def perform_qc_checks(self):
           # QC checks
           pass

       def generate_report(self, output_path):
           # Report generation
           pass
   ```

3. **Add Tests**
   - Create test file in `tests/unit/`
   - Implement comprehensive test coverage

4. **Update Documentation**
   - Create protocol documentation in `docs/protocols/`
   - Update this README

## Database Setup

### SQLite (Default)

SQLite is used by default - no configuration needed. Database file is created at `data/test_protocols.db`.

### PostgreSQL

For production use with PostgreSQL:

1. Create `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/test_protocols
   ```

2. Initialize database:
   ```python
   from database.db_config import init_db
   init_db()
   ```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///data/test_protocols.db

# Application
DEBUG=False
LOG_LEVEL=INFO

# LIMS Integration (optional)
LIMS_API_URL=https://lims.example.com/api
LIMS_API_KEY=your_api_key
```

## Testing

### Test Coverage

Current test coverage targets:
- **Protocols**: > 80%
- **Database**: > 70%
- **Overall**: > 70%

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest -m unit
pytest -m integration

# With coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Documentation

- [SNAIL-001 Protocol Documentation](docs/protocols/snail_trail_formation.md)
- [Protocol Development Guide](docs/protocol_development_guide.md) (Coming soon)
- [API Reference](docs/api_reference.md) (Coming soon)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Implement changes with tests
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contact

**Project Owner**: Quality Assurance Team
**Repository**: https://github.com/ganeshgowri-ASA/test-protocols

## Roadmap

### Upcoming Protocols
- Humidity-Freeze Test (HUMIDITY-FREEZE-001)
- Thermal Cycling (TC-200)
- UV Degradation (UV-001)
- Mechanical Load Test (ML-001)

### Planned Features
- Real-time LIMS integration
- Multi-user authentication
- Advanced analytics dashboard
- Machine learning degradation prediction
- Mobile app for field inspections

## Version History

- **1.0.0** (2025-01-14) - Initial release with SNAIL-001 protocol
