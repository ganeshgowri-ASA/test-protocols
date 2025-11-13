# Test Protocols - IAM-001 Implementation

Modular PV Testing Protocol Framework with complete IAM-001 (Incidence Angle Modifier) implementation following IEC 61853 standards.

## Features

### ✨ Core Capabilities

- **📋 Protocol Management**: JSON-based protocol definitions with schema validation
- **📊 IAM Analysis**: Automated calculation of incidence angle modifier curves (0-90°)
- **📈 AOI Curves**: Multiple fitting models (ASHRAE, Physical, Polynomial)
- **✅ Validation & QC**: Comprehensive quality control checks and validation
- **💾 Traceability**: SQLAlchemy ORM with complete audit trail
- **🖥️ GenSpark UI**: Interactive Streamlit interface for test management
- **🧪 Testing**: Comprehensive test suite with >90% coverage

### 🎯 IAM-001 Protocol

The IAM-001 protocol implements the Incidence Angle Modifier test according to IEC 61853:

- **Test Range**: 0° to 90° angle of incidence
- **Recommended Angles**: 0°, 10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°
- **Test Conditions**: 1000 W/m², 25°C, AM1.5G spectrum
- **Measurements**: Isc, Voc, Pmax, I-V curve parameters
- **Analysis Models**: ASHRAE, Physical (Fresnel-based), 4th-order Polynomial

## Project Structure

```
test-protocols/
├── protocols/
│   └── iam-001/
│       ├── schema.json           # JSON schema for validation
│       ├── template.json         # Protocol template
│       └── config.json           # Configuration parameters
├── src/
│   ├── protocol_engine/
│   │   ├── loader.py             # Protocol loading and parsing
│   │   ├── validator.py          # Schema and data validation
│   │   └── executor.py           # Protocol execution engine
│   ├── analysis/
│   │   ├── iam_calculator.py     # IAM calculations
│   │   ├── curve_fitting.py      # Model fitting (ASHRAE, Physical, Polynomial)
│   │   └── analyzer.py           # Main analysis orchestrator
│   ├── database/
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   ├── session.py            # Database session management
│   │   └── repository.py         # Data access layer
│   └── ui/
│       ├── app.py                # Main Streamlit application
│       └── pages/
│           ├── new_test.py       # New test creation
│           ├── view_results.py   # Results visualization
│           └── data_management.py # Data management
├── tests/
│   ├── unit/                     # Unit tests
│   │   ├── test_protocol_loader.py
│   │   ├── test_validator.py
│   │   ├── test_iam_calculator.py
│   │   └── test_curve_fitting.py
│   └── integration/              # Integration tests
│       └── test_full_workflow.py
├── data/                         # Protocol data storage
├── config/                       # Configuration files
└── pyproject.toml               # Project configuration
```

## Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Usage

### 1. Run the Streamlit UI

```bash
streamlit run src/ui/app.py
```

Navigate to http://localhost:8501 to access the web interface.

### 2. Programmatic API

```python
from protocol_engine import ProtocolExecutor
from analysis import create_analyzer

# Create protocol
executor = ProtocolExecutor("iam-001")
executor.create_protocol(
    **{
        "sample_info.sample_id": "PV-2025-001",
        "sample_info.module_type": "400W Mono-Si",
        "sample_info.technology": "mono-Si"
    }
)

# Add measurements (0-90° range)
for angle in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
    executor.add_measurement(
        angle=angle,
        isc=10.0 - angle * 0.05,  # Example values
        voc=48.0,
        pmax=400.0 - angle * 3,
        irradiance_actual=1000.0,
        temperature_actual=25.0
    )

# Validate
validation_results = executor.validate_protocol()
print(f"Validation: {validation_results['overall_status']}")

# Analyze
executor.execute_analysis(create_analyzer)
results = executor.get_analysis_results()

print(f"Model: {results['fitting_parameters']['model']}")
print(f"R²: {results['fitting_parameters']['r_squared']:.4f}")

# Save
executor.save_protocol("data/my_test.json")
```

### 3. Command Line Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_iam_calculator.py

# Run integration tests
pytest tests/integration/
```

## IAM Analysis Models

### ASHRAE Model

Simple single-parameter model:

```
IAM(θ) = 1 - b₀ * (1/cos(θ) - 1)
```

### Physical Model

Based on Fresnel reflections:

```
IAM(θ) = (1 - exp(-cos(θ)/aᵣ)) / (1 - exp(-1/aᵣ))
```

### Polynomial Model

Flexible 4th-order polynomial:

```
IAM(θ) = 1 + a₁(θ/90) + a₂(θ/90)² + a₃(θ/90)³ + a₄(θ/90)⁴
```

## Database Schema

The system uses SQLAlchemy ORM with the following main models:

- **Protocol**: Test protocol instances
- **Measurement**: Individual angle measurements
- **AnalysisResult**: IAM curve and fitting results
- **AuditLog**: Complete traceability and audit trail
- **Equipment**: Test equipment and calibration tracking

## Testing

The test suite includes:

- **Unit Tests**: Test individual components
  - Protocol loader and validator
  - IAM calculator
  - Curve fitting models

- **Integration Tests**: Test complete workflows
  - Full 0-90° angle coverage
  - End-to-end protocol execution
  - Database operations

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test
pytest tests/unit/test_iam_calculator.py::test_iam_full_range_0_to_90

# Coverage report
pytest --cov=src --cov-report=term-missing
```

## Configuration

### Protocol Configuration

Edit `protocols/iam-001/config.json`:

```json
{
  "default_settings": {
    "recommended_angles": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
    "irradiance": 1000,
    "temperature": 25
  },
  "validation_rules": {
    "min_data_points": 5,
    "irradiance_tolerance": 50,
    "temperature_tolerance": 5
  },
  "analysis_settings": {
    "default_model": "ashrae",
    "fit_quality_thresholds": {
      "excellent": 0.99,
      "good": 0.95,
      "acceptable": 0.90
    }
  }
}
```

## Development

### Code Style

The project uses:

- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Adding New Protocols

1. Create protocol directory: `protocols/<protocol-id>/`
2. Define JSON schema: `schema.json`
3. Create template: `template.json`
4. Add configuration: `config.json`
5. Implement analysis function
6. Add tests

## API Reference

### ProtocolExecutor

Main class for protocol execution:

```python
executor = ProtocolExecutor(protocol_id: str)
executor.create_protocol(**overrides)
executor.add_measurement(angle, isc, voc, pmax, **kwargs)
executor.validate_protocol() -> Dict
executor.execute_analysis(analysis_function)
executor.save_protocol(file_path)
```

### IAMCalculator

IAM calculations:

```python
calculator = IAMCalculator(measurements)
iam_curve = calculator.calculate_iam(metric="pmax")
stats = calculator.get_statistics(iam_curve)
is_valid, warnings = calculator.validate_iam_curve(iam_curve)
```

### CurveFitter

Model fitting:

```python
fitter = CurveFitter(iam_curve)
results = fitter.fit_all_models()
best_name, best_result = fitter.select_best_model(results)
smooth_curve = fitter.generate_smooth_curve(model, parameters)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Standards

- **IEC 61853**: PV module performance testing and energy rating
- **JSON Schema**: Draft-07 specification
- **SQLAlchemy**: 2.0+ ORM

## Support

For issues and questions:

- GitHub Issues: [repository issues]
- Documentation: See `docs/` directory
- Email: test-protocols@example.com

## Version

Current version: **0.1.0**

Protocol version: **1.0.0**

---

© 2025 Test Protocols Team
