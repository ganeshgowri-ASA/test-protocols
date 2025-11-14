# ML-002 Mechanical Load Dynamic Test - Design Document

## Overview

The ML-002 protocol implements a 1000Pa cyclic mechanical load test for photovoltaic modules according to IEC 61215-2:2021 MQT 16. This document describes the complete design and implementation.

## Table of Contents

1. [Protocol Specification](#protocol-specification)
2. [Implementation Architecture](#implementation-architecture)
3. [Data Flow](#data-flow)
4. [Quality Control](#quality-control)
5. [User Interface](#user-interface)
6. [Database Schema](#database-schema)
7. [Testing Strategy](#testing-strategy)

## Protocol Specification

### Test Parameters

- **Protocol ID**: ML-002
- **Test Load**: 1000 Pa (cyclic)
- **Cycle Count**: 1000 cycles (configurable: 100-10,000)
- **Cycle Duration**: 10 seconds (configurable: 5-60s)
- **Load Rate**: 100 Pa/sec (configurable)
- **Standard**: IEC 61215-2:2021 MQT 16

### Test Objectives

1. Evaluate module structural integrity under cyclic mechanical loading
2. Simulate wind and snow loads experienced in field conditions
3. Assess module resistance to fatigue and permanent deformation
4. Verify load-deflection linearity
5. Ensure module meets safety and reliability standards

### Environmental Conditions

- **Temperature**: 15-35°C (target: 25°C)
- **Humidity**: 45-75% RH (target: 50%)
- **Atmospheric Pressure**: 86-106 kPa

## Implementation Architecture

### Component Structure

```
protocols/ml_002/
├── protocol.json          # Protocol definition
├── schema.json            # JSON Schema validation
├── implementation.py      # Test execution logic
├── analyzer.py            # Data analysis
├── ui/
│   ├── components.py      # UI components
│   └── streamlit_app.py   # Streamlit application
└── tests/
    ├── test_protocol.py
    ├── test_implementation.py
    └── test_analyzer.py
```

### Key Classes

#### Implementation Layer

1. **ML002MechanicalLoadTest**: Main test orchestration
   - Equipment control
   - Cycle execution
   - Data collection
   - Real-time monitoring

2. **LoadController**: Load application system interface
   - Connect/disconnect
   - Calibration
   - Load application with rate control
   - Emergency stop

3. **SensorArray**: Multi-sensor management
   - Sensor connection
   - Data acquisition
   - Synchronized reading

#### Data Layer

4. **TestSample**: Module information
5. **SensorReading**: Individual sensor data point
6. **CycleData**: Complete cycle dataset
7. **TestResults**: Complete test results

#### Analysis Layer

8. **ML002Analyzer**: Comprehensive data analysis
   - Statistical analysis
   - Linearity assessment
   - Cyclic behavior evaluation
   - QC criteria verification

## Data Flow

### Test Execution Flow

```
1. Initialize Equipment
   ↓
2. Start Test Loop (for each cycle):
   ├─→ Apply Load (ramp to target)
   ├─→ Hold at Peak
   ├─→ Read Sensors
   ├─→ Unload (ramp to zero)
   ├─→ Read Sensors
   ├─→ Check Failure Conditions
   └─→ Record Cycle Data
   ↓
3. Complete Test
   ↓
4. Perform Analysis
   ↓
5. Evaluate QC Criteria
   ↓
6. Generate Report
```

### Data Collection Points

**Per Cycle**:
- Load cell readings (10 Hz)
- LVDT deflection measurements (10 Hz)
- Strain gauge data (10 Hz, optional)

**Periodic** (every 10 cycles):
- Temperature
- Humidity
- Atmospheric pressure

**Inspection Points**:
- Pre-test visual inspection
- Mid-test inspection (cycle 500)
- Post-test visual inspection

## Quality Control

### Acceptance Criteria

| Criterion | Description | Pass Condition |
|-----------|-------------|----------------|
| No Visible Defects | No cracks, delamination, or damage | Visual inspection |
| Deflection Linearity | Load vs deflection R² | R² ≥ 0.95 |
| Max Deflection Limit | Maximum deflection at 1000Pa | ≤ 30 mm |
| Deflection Consistency | Cycle-to-cycle variation | CV ≤ 10% |
| Load Accuracy | Applied load accuracy | Within ±5% |
| Environmental Stability | Conditions within range | Temperature & humidity |
| No Permanent Deformation | Residual deflection after unload | ≤ 0.5 mm |

### Failure Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Module Cracking | Visual detection | Stop immediately |
| Excessive Deflection | > 50 mm | Stop immediately |
| Load Overshoot | > 5400 Pa | Stop immediately |
| Sensor Failure | Critical sensor offline | Stop with retry |
| Environmental Deviation | Outside range > 5 min | Warning |

## User Interface

### GenSpark UI Components

#### 1. Sample Input Form
- Module identification
- Physical specifications
- Manufacturing details

#### 2. Test Configuration
- Load parameters
- Cycle settings
- Environmental targets

#### 3. Live Monitoring Dashboard
- Real-time load display
- Deflection tracking
- Progress indicators
- Environmental conditions
- Interactive charts

#### 4. Results Visualization
- Statistical summaries
- Load-deflection plots
- Cyclic behavior charts
- QC assessment table
- Pass/fail determination

#### 5. Report Generation
- Summary reports
- Detailed analysis
- Data export (PDF, JSON, CSV)

### Streamlit Application

**Pages**:
1. **Home**: Overview and quick stats
2. **Configure Test**: Sample and parameter setup
3. **Run Test**: Live monitoring and control
4. **View Results**: Analysis and reporting
5. **Protocol Info**: Protocol details

## Database Schema

### Tables

#### test_runs
Primary test execution records with sample info, timestamps, and results summary.

#### sensor_data
Raw sensor readings with timestamps and cycle numbers.

#### cycle_data
Aggregated data per cycle including load and deflection metrics.

#### analysis_results
Processed analysis including statistics, linearity, and cyclic behavior.

#### quality_control
QC assessment results with pass/fail for each criterion.

#### test_reports
Generated reports in various formats.

#### calibration_records
Equipment calibration tracking.

### Relationships

```
test_runs (1) ──→ (many) sensor_data
test_runs (1) ──→ (many) cycle_data
test_runs (1) ──→ (1) analysis_results
test_runs (1) ──→ (1) quality_control
test_runs (1) ──→ (many) test_reports
```

## Testing Strategy

### Unit Tests

1. **Protocol Tests** (`test_protocol.py`)
   - JSON structure validation
   - Schema compliance
   - Parameter verification

2. **Implementation Tests** (`test_implementation.py`)
   - Equipment control
   - Cycle execution
   - Data collection
   - Failure handling

3. **Analyzer Tests** (`test_analyzer.py`)
   - Statistical calculations
   - Regression analysis
   - QC evaluation
   - Report generation

### Integration Tests

- End-to-end test execution (reduced cycles)
- Equipment communication
- Data persistence
- UI workflow

### Test Coverage Goals

- Unit test coverage: > 80%
- Critical path coverage: 100%
- Edge case handling: Comprehensive

## API Reference

### Main Test Execution

```python
from protocols.ml_002 import ML002MechanicalLoadTest, TestSample

# Create test instance
test = ML002MechanicalLoadTest("protocol.json")

# Define sample
sample = TestSample(
    sample_id="MODULE-001",
    module_type="Crystalline Silicon",
    serial_number="SN123456"
)

# Execute test
results = test.execute_test(sample)

# Check results
if results.passed:
    print("Test PASSED")
else:
    print(f"Test FAILED: {results.failure_reason}")
```

### Data Analysis

```python
from protocols.ml_002 import ML002Analyzer

# Create analyzer
analyzer = ML002Analyzer(test_results, protocol)

# Perform full analysis
analysis = analyzer.perform_full_analysis()

# Generate report
report = analyzer.generate_summary_report()
print(report)
```

### UI Components

```python
from protocols.ml_002.ui.components import ML002UIComponents

# Create UI components
ui = ML002UIComponents(protocol)

# Render forms
sample_data = ui.render_sample_input_form()
test_params = ui.render_test_parameters_form()

# Display results
ui.render_test_results(results)
```

## Configuration

### Protocol Customization

Modify `protocol.json` to customize:
- Load levels and rates
- Cycle counts and durations
- Acceptance criteria thresholds
- Sensor configurations
- Report formats

### Equipment Integration

Implement equipment-specific interfaces by extending:
- `LoadController`: Custom load control systems
- `SensorArray`: Specific sensor hardware

## Deployment

### Requirements

```
python >= 3.8
numpy >= 1.21.0
scipy >= 1.7.0
pandas >= 1.3.0
streamlit >= 1.25.0
plotly >= 5.0.0
sqlalchemy >= 1.4.0
jsonschema >= 4.0.0
pytest >= 7.0.0
```

### Installation

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest protocols/ml_002/tests/

# Run with coverage
pytest --cov=protocols.ml_002 protocols/ml_002/tests/

# Run specific test file
pytest protocols/ml_002/tests/test_protocol.py -v
```

### Running Streamlit App

```bash
streamlit run protocols/ml_002/ui/streamlit_app.py
```

## Maintenance and Support

### Version History

- **v1.0.0** (2025-11-14): Initial implementation
  - Core test execution
  - Data analysis
  - UI components
  - Database integration

### Future Enhancements

1. Multi-module parallel testing
2. Advanced fatigue modeling
3. Machine learning-based defect detection
4. Cloud data storage
5. Mobile app interface

## References

1. IEC 61215-2:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
2. IEC 61730 - Photovoltaic (PV) module safety qualification
3. ISO 17025 - General requirements for the competence of testing and calibration laboratories

## Authors

- ganeshgowri-ASA
- Date: 2025-11-14
- Version: 1.0.0

## License

MIT License - See LICENSE file for details
