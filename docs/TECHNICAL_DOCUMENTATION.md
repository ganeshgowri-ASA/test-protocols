# Technical Documentation - Test Protocol Framework

## Architecture Overview

The PV Test Protocol Framework is a modular, JSON-driven system for managing and executing photovoltaic module testing protocols. The architecture consists of four main layers:

### 1. Protocol Definition Layer (JSON)
- JSON-based protocol definitions
- Schema-validated structure
- Version control and metadata
- Location: `protocols/`

### 2. Core Engine Layer (Python)
- Protocol loader and validator
- Test execution engine
- Data models and validation
- Location: `src/core/`

### 3. Data Layer (Database)
- SQLite database for data persistence
- Structured schema for test data
- Audit trail and history
- Location: `database/`

### 4. Presentation Layer (UI)
- Streamlit-based user interface
- Interactive test execution
- Real-time monitoring
- Data visualization
- Location: `src/ui/`

### 5. Analysis Layer (Python)
- Statistical analysis
- Trend detection
- Anomaly identification
- Chart generation
- Location: `src/analysis/`

## Module Descriptions

### Core Modules

#### `protocol_loader.py`
Loads and validates JSON protocol definitions.

**Key Classes**:
- `ProtocolLoader`: Main class for protocol operations

**Key Methods**:
- `load_protocol(protocol_id)`: Load a protocol by ID
- `list_protocols(category)`: List available protocols
- `get_protocol_info(protocol_id)`: Get protocol summary

**Usage**:
```python
from core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("TROP-001")
```

#### `test_engine.py`
Manages test execution, monitoring, and data collection.

**Key Classes**:
- `TestEngine`: Main test execution engine
- `TestStatus`: Enumeration of test statuses

**Key Methods**:
- `start_test(modules, operator)`: Initialize test
- `record_measurement(parameter, value, unit)`: Record data
- `advance_step()`: Progress to next step
- `complete_test()`: Mark test as complete
- `abort_test(reason)`: Abort test execution

**Usage**:
```python
from core.test_engine import TestEngine

engine = TestEngine(protocol, "TEST-001")
engine.start_test(["MOD1", "MOD2", "MOD3"], "John Doe")
engine.record_measurement("temperature", 85.0, "°C")
```

#### `models.py`
Data models for the framework.

**Key Classes**:
- `Module`: PV module information
- `ElectricalMeasurement`: Electrical test data
- `EnvironmentalMeasurement`: Chamber conditions
- `VisualInspection`: Visual inspection records
- `TestSession`: Complete test session
- `TestResult`: Test result summary

**Usage**:
```python
from core.models import Module, ModuleType

module = Module(
    serial_number="MOD001",
    manufacturer="Test Co",
    model="TEST-300",
    module_type=ModuleType.CRYSTALLINE_SILICON,
    rated_power=300.0,
    technology="PERC"
)
```

### Analysis Modules

#### `data_analyzer.py`
Statistical analysis and trend detection.

**Key Classes**:
- `DataAnalyzer`: Main analysis class

**Key Methods**:
- `calculate_statistics(values)`: Compute statistical measures
- `detect_outliers(values, threshold)`: Z-score outlier detection
- `calculate_trend(values, timestamps)`: Linear regression trend
- `analyze_chamber_uniformity(measurements)`: Uniformity analysis
- `calculate_degradation_rate(measurements, parameter)`: Degradation analysis

**Usage**:
```python
from analysis.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
stats = analyzer.calculate_statistics(temperature_values)
outliers = analyzer.detect_outliers(temperature_values, threshold=3.0)
```

#### `chart_generator.py`
Visualization and chart generation.

**Key Classes**:
- `ChartGenerator`: Chart generation utilities

**Key Methods**:
- `plot_temperature_humidity(measurements)`: T/H time series
- `plot_power_degradation(measurements, initial_power)`: Degradation chart
- `plot_iv_curves(pre_test, post_test)`: I-V curve comparison
- `create_summary_dashboard(test_data)`: Multi-panel dashboard

**Usage**:
```python
from analysis.chart_generator import ChartGenerator

generator = ChartGenerator()
fig = generator.plot_temperature_humidity(
    measurements,
    output_path="temp_humidity.png"
)
```

### Database Module

#### `db_manager.py`
Database connection and operations.

**Key Classes**:
- `DatabaseManager`: Database interface

**Key Methods**:
- `initialize_database()`: Create schema
- `create_test_session(...)`: Create test
- `add_module(...)`: Add module
- `record_electrical_measurement(...)`: Store electrical data
- `record_environmental_measurement(...)`: Store chamber data
- `get_test_session(test_id)`: Retrieve test
- `update_test_status(...)`: Update status

**Usage**:
```python
from database.db_manager import DatabaseManager

with DatabaseManager() as db:
    db.initialize_database()
    session_id = db.create_test_session(
        "TEST-001",
        "TROP-001",
        "1.0.0",
        "John Doe"
    )
```

### UI Modules

#### `app.py`
Main application entry point.

**Features**:
- Protocol browser
- Category filtering
- Navigation to test execution
- Settings management

**Launch**:
```bash
streamlit run src/ui/app.py
```

#### `tropical_climate_ui.py`
TROP-001 specific interface.

**Features**:
- Test setup and configuration
- Test execution control
- Real-time monitoring
- Data analysis views
- Report generation

**Launch**:
```bash
streamlit run src/ui/tropical_climate_ui.py
```

## Database Schema

### Key Tables

**test_sessions**
- Core test information
- Links to protocol
- Status tracking
- Equipment information

**modules**
- Module master data
- Manufacturer information
- Specifications

**test_session_modules**
- Many-to-many relationship
- Links modules to tests

**electrical_measurements**
- I-V curve data
- All electrical parameters
- Pre/in/post test phases

**environmental_measurements**
- Temperature data
- Humidity data
- Chamber sensor readings

**visual_inspections**
- Defect tracking
- Inspector notes
- Photo references

**alerts**
- Out-of-tolerance conditions
- Severity levels
- Acknowledgment tracking

**deviations**
- Test deviations
- Corrective actions
- Review workflow

**test_results**
- Summary results
- Pass/fail determination
- Degradation calculations

### Indexes

Performance-optimized indexes on:
- Test session lookup (test_id, protocol_id, status)
- Measurement queries (test_session_id, timestamp)
- Module lookups (serial_number)
- Alert and deviation queries

## JSON Protocol Schema

### Required Fields

```json
{
  "protocol_id": "string",
  "version": "string",
  "name": "string",
  "category": "string",
  "test_sequence": {
    "steps": [...],
    "total_cycles": integer,
    "total_test_duration": number
  },
  "acceptance_criteria": {...}
}
```

### Optional Fields

- `subcategory`: Protocol subcategory
- `standard`: Reference standard
- `description`: Protocol description
- `test_requirements`: Detailed requirements
- `pre_test_requirements`: Pre-test checks
- `post_test_requirements`: Post-test procedures
- `monitoring_parameters`: Real-time monitoring
- `equipment_requirements`: Required equipment
- `safety_requirements`: Safety precautions
- `integrations`: External system integration

## Data Flow

### Test Execution Flow

1. **Initialization**
   - Load protocol JSON
   - Validate protocol structure
   - Create database session
   - Initialize test engine

2. **Pre-Test**
   - Record module information
   - Perform pre-test measurements
   - Store baseline data
   - Perform visual inspection

3. **Test Execution**
   - Start test sequence
   - Record environmental data (automated)
   - Perform interim measurements
   - Monitor for alerts
   - Track deviations
   - Progress through steps/cycles

4. **Post-Test**
   - Complete test sequence
   - Perform final measurements
   - Evaluate acceptance criteria
   - Generate results
   - Create report

5. **Archival**
   - Store all test data
   - Generate audit trail
   - Export data for external systems

## API Design

### Protocol Loader API

```python
# List protocols
protocols = loader.list_protocols(category="Environmental")

# Load specific protocol
protocol = loader.load_protocol("TROP-001")

# Get protocol info
info = loader.get_protocol_info("TROP-001")
```

### Test Engine API

```python
# Initialize
engine = TestEngine(protocol, test_id)

# Start test
result = engine.start_test(modules, operator)

# Record data
engine.record_measurement("temperature", 85.0, "°C")
engine.record_deviation("Power failure", "MAJOR", "Restored")

# Progress
engine.advance_step()

# Complete
engine.complete_test()

# Status
status = engine.get_status()

# Evaluate
result = engine.evaluate_acceptance_criteria(pre_test, post_test)
```

### Database API

```python
# Context manager pattern
with DatabaseManager() as db:
    # Create test
    session_id = db.create_test_session(...)

    # Add data
    db.record_electrical_measurement(...)
    db.record_environmental_measurement(...)

    # Query
    session = db.get_test_session(test_id)
    measurements = db.get_test_measurements(session_id)

    # Update
    db.update_test_status(session_id, "completed")
```

## Extension Points

### Adding New Protocols

1. Create JSON definition in `protocols/category/`
2. Follow schema requirements
3. Include all necessary test steps
4. Define acceptance criteria
5. Test with protocol loader

### Adding New Test Types

1. Create protocol JSON
2. Optionally create dedicated UI in `src/ui/`
3. Add any custom analysis in `src/analysis/`
4. Document in `docs/`

### Custom Analysis

1. Extend `DataAnalyzer` class
2. Add methods for custom calculations
3. Integrate with chart generator
4. Add to UI analysis tab

### External Integrations

Implement in protocol JSON:
```json
"integrations": {
  "lims": {
    "enabled": true,
    "endpoints": ["/api/v1/results"]
  },
  "qms": {
    "enabled": true,
    "document_references": ["SOP-001"]
  }
}
```

## Testing

### Unit Tests

Located in `tests/unit/`:
- `test_protocol_loader.py`: Protocol loading tests
- `test_test_engine.py`: Engine functionality tests

Run with:
```bash
python -m unittest discover tests/unit
```

### Integration Tests

Located in `tests/integration/`:
- `test_database_integration.py`: Database operations

Run with:
```bash
python -m unittest discover tests/integration
```

### Test Coverage

Aim for:
- Unit tests: >80% coverage
- Integration tests: Critical paths
- End-to-end: Manual test scenarios

## Performance Considerations

### Database Optimization

- Indexed queries for fast lookups
- Batch inserts for measurements
- Connection pooling for concurrent access
- Periodic vacuum/analyze

### UI Performance

- Lazy loading for large datasets
- Pagination for measurement tables
- Cached protocol loading
- Async operations where possible

### Data Storage

- Compress historical data
- Archive completed tests
- Implement data retention policies
- Regular database maintenance

## Security

### Data Protection

- No sensitive data in JSON files
- Database access control
- Audit logging for changes
- Backup procedures

### Input Validation

- JSON schema validation
- SQL injection prevention (parameterized queries)
- Type checking
- Range validation

## Deployment

### Requirements

See `requirements.txt`:
- Python 3.8+
- streamlit
- pandas
- numpy
- matplotlib
- plotly
- sqlite3 (built-in)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Edit `database/db_manager.py` for database path
Edit UI files for custom branding/settings

### Running

```bash
# Main UI
streamlit run src/ui/app.py

# TROP-001 UI
streamlit run src/ui/tropical_climate_ui.py
```

## Troubleshooting

### Common Issues

**Protocol not found**
- Check file location in `protocols/`
- Verify JSON is valid
- Check protocol_id matches

**Database errors**
- Initialize database first
- Check file permissions
- Verify schema version

**UI connection issues**
- Check streamlit installation
- Verify Python path
- Check port availability

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-14 | Initial implementation |

## Future Enhancements

1. **Multi-chamber support**: Parallel test execution
2. **Advanced reporting**: PDF generation with charts
3. **Real-time notifications**: Email/SMS alerts
4. **Cloud sync**: Remote monitoring capability
5. **AI analysis**: Predictive failure detection
6. **Mobile app**: Field inspection tools
7. **API server**: RESTful API for integrations
