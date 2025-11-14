# ML-002: Mechanical Load Dynamic Test (1000Pa Cyclic)

## Overview

ML-002 is a comprehensive test protocol for evaluating photovoltaic module structural integrity under cyclic mechanical loading. This protocol implements IEC 61215-2:2021 MQT 16 requirements with 1000Pa cyclic loading.

## Features

- ✅ **Standards-Compliant**: IEC 61215-2:2021 MQT 16
- ✅ **Automated Testing**: Fully automated test execution
- ✅ **Real-Time Monitoring**: Live data visualization
- ✅ **Comprehensive Analysis**: Statistical and quality control analysis
- ✅ **Interactive UI**: Streamlit-based user interface
- ✅ **Database Integration**: Complete data persistence
- ✅ **Report Generation**: Automated PDF/HTML/JSON reports

## Quick Start

### Installation

```bash
# Install dependencies
pip install numpy scipy pandas streamlit plotly sqlalchemy jsonschema pytest

# Or use requirements.txt
pip install -r requirements.txt
```

### Running a Test

```python
from protocols.ml_002 import ML002MechanicalLoadTest, TestSample

# Initialize test
test = ML002MechanicalLoadTest("protocols/ml_002/protocol.json")

# Create sample
sample = TestSample(
    sample_id="PV-MODULE-001",
    module_type="Crystalline Silicon",
    serial_number="SN123456789",
    manufacturer="Example Solar Inc."
)

# Execute test
results = test.execute_test(sample)

# Check results
print(f"Test Status: {results.status.value}")
print(f"Result: {'PASS' if results.passed else 'FAIL'}")
print(f"Cycles Completed: {results.completed_cycles}/{results.total_cycles}")
```

### Using the Web Interface

```bash
# Launch Streamlit app
streamlit run protocols/ml_002/ui/streamlit_app.py
```

Then navigate to:
1. **Configure Test** - Register module and set parameters
2. **Run Test** - Execute test with live monitoring
3. **View Results** - Analyze results and generate reports

## Test Specification

### Parameters

| Parameter | Default Value | Range |
|-----------|--------------|-------|
| Test Load | 1000 Pa | 100 - 5400 Pa |
| Cycle Count | 1000 | 100 - 10,000 |
| Cycle Duration | 10 sec | 5 - 60 sec |
| Load Rate | 100 Pa/sec | 10 - 500 Pa/sec |
| Hold Time | 2 sec | 0 - 10 sec |
| Rest Time | 1 sec | 0 - 5 sec |

### Environmental Conditions

- **Temperature**: 15-35°C (target: 25°C)
- **Humidity**: 45-75% RH (target: 50%)
- **Pressure**: 86-106 kPa

### Acceptance Criteria

1. **No Visible Defects**: No cracks, delamination, or damage
2. **Deflection Linearity**: R² ≥ 0.95
3. **Max Deflection**: ≤ 30 mm at 1000 Pa
4. **Deflection Consistency**: CV ≤ 10%
5. **Load Accuracy**: Within ±5% of target
6. **Environmental Stability**: Conditions within spec
7. **No Permanent Deformation**: ≤ 0.5 mm residual

## Architecture

```
ml_002/
├── protocol.json          # Protocol definition
├── schema.json            # JSON Schema validation
├── implementation.py      # Core test logic
├── analyzer.py            # Data analysis
├── ui/
│   ├── components.py      # UI components
│   └── streamlit_app.py   # Web application
├── tests/
│   ├── test_protocol.py
│   ├── test_implementation.py
│   └── test_analyzer.py
└── README.md
```

## Data Analysis

The ML-002 analyzer provides:

### Statistical Analysis
- Mean, std deviation, min/max
- Quartiles and IQR
- Coefficient of variation

### Linearity Analysis
- Linear regression (load vs deflection)
- R² calculation
- Residual analysis

### Cyclic Behavior
- Cycle-to-cycle variation
- Trend analysis
- Fatigue indicators
- Outlier detection

### Quality Control
- Automated criteria evaluation
- Pass/fail determination
- Failure cause identification

## Example Analysis

```python
from protocols.ml_002 import ML002Analyzer

# Create analyzer
analyzer = ML002Analyzer(test_results, protocol)

# Perform full analysis
analysis = analyzer.perform_full_analysis()

# Access results
print(f"R² = {analysis['load_deflection_linearity']['regression']['r_squared']:.4f}")
print(f"Max Deflection = {analysis['deflection_statistics']['overall_deflection_range']['absolute_max']:.3f} mm")

# Generate report
report = analyzer.generate_summary_report()
print(report)
```

## Database Integration

The protocol integrates with SQLAlchemy for data persistence:

```python
from sqlalchemy import create_engine
from integrations.database import Base, TestRun, CycleData, AnalysisResults

# Create database
engine = create_engine('sqlite:///ml002_tests.db')
Base.metadata.create_all(engine)

# Store test results
# (Implementation handles this automatically)
```

### Database Tables

- **test_runs**: Test execution records
- **sensor_data**: Raw sensor readings
- **cycle_data**: Per-cycle aggregated data
- **analysis_results**: Processed analysis
- **quality_control**: QC assessment
- **test_reports**: Generated reports
- **calibration_records**: Equipment calibration

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest protocols/ml_002/tests/ -v

# Run specific test file
pytest protocols/ml_002/tests/test_protocol.py -v

# Run with coverage
pytest --cov=protocols.ml_002 protocols/ml_002/tests/
```

### Test Coverage

- Protocol structure validation
- Implementation logic
- Data analysis algorithms
- QC criteria evaluation
- Edge cases and error handling

## Configuration

### Customizing Protocol

Edit `protocol.json` to modify:

```json
{
  "parameters": {
    "load_configuration": {
      "test_load_pa": {
        "value": 1000
      }
    },
    "cycle_parameters": {
      "cycle_count": {
        "value": 1000
      }
    }
  }
}
```

### Equipment Integration

Extend base classes for custom equipment:

```python
from protocols.ml_002.implementation import LoadController

class CustomLoadController(LoadController):
    def connect(self):
        # Your equipment connection code
        pass

    def set_load(self, load_pa, rate_pa_per_sec):
        # Your load control code
        pass
```

## API Reference

### Main Classes

- **ML002MechanicalLoadTest**: Test orchestration
- **ML002Analyzer**: Data analysis
- **TestSample**: Sample information
- **TestResults**: Test results container
- **ML002UIComponents**: UI components

### Key Methods

```python
# Test execution
test.execute_test(sample) -> TestResults
test.initialize_equipment() -> bool
test.abort_test() -> None

# Analysis
analyzer.perform_full_analysis() -> Dict
analyzer.evaluate_acceptance_criteria() -> Dict
analyzer.generate_summary_report() -> str

# UI
ui.render_sample_input_form() -> Dict
ui.render_test_parameters_form() -> Dict
ui.render_test_results(results) -> None
```

## Troubleshooting

### Common Issues

**Equipment Connection Failed**
- Check equipment is powered on
- Verify connection settings
- Review calibration status

**Test Stopped Unexpectedly**
- Check failure conditions in logs
- Verify environmental conditions
- Review sensor readings for anomalies

**Analysis Errors**
- Ensure test completed successfully
- Verify sufficient data points
- Check for sensor data quality

## Best Practices

1. **Calibration**: Calibrate equipment before each test session
2. **Environmental Control**: Maintain stable test environment
3. **Visual Inspection**: Perform thorough pre/post-test inspections
4. **Data Backup**: Enable automatic data backup
5. **Documentation**: Record all test parameters and observations

## Standards Compliance

This protocol implements:
- **IEC 61215-2:2021** MQT 16: Mechanical load test
- **IEC 61730**: Module safety qualification
- **ISO 17025**: Testing laboratory competence

## Contributing

To contribute to this protocol:

1. Review design documentation
2. Follow coding standards
3. Add unit tests for new features
4. Update documentation
5. Submit pull request

## Support

For issues or questions:
- Review documentation in `docs/ml-002-design.md`
- Check test examples in `tests/`
- Consult protocol specification in `protocol.json`

## Version History

- **v1.0.0** (2025-11-14): Initial release
  - Core implementation
  - UI components
  - Database integration
  - Comprehensive testing

## License

MIT License

## Author

ganeshgowri-ASA

## References

1. IEC 61215-2:2021 - Terrestrial PV modules - Design qualification and type approval
2. IEC 61730 - PV module safety qualification
3. ISO 17025 - Testing and calibration laboratory competence
