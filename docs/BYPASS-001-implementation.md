# BYPASS-001 Implementation Guide

## Implementation Overview

This document describes the complete implementation of the BYPASS-001 (Bypass Diode Testing) protocol for the Test Protocols Framework.

## Components Implemented

### 1. JSON Protocol Definition

**File**: `src/protocols/bypass-diode-testing/protocol.json`

The protocol definition includes:
- 6 test phases covering the complete bypass diode test sequence
- 20+ configurable parameters
- 15+ measurement types
- 7 QC rules for automated quality control
- 6 default charts for data visualization
- Comprehensive report template

**Key Features**:
- Fully compliant with IEC 61215 MQT 18 standard
- Configurable temperature ranges and cycle counts
- Per-diode measurements support
- Automated degradation calculations

### 2. JSON Schema Validation

**File**: `src/protocols/bypass-diode-testing/schema.json`

JSON Schema ensures:
- Protocol structure validation
- Type safety for all parameters
- Required field enforcement
- Pattern matching for IDs and codes
- Equipment specification validation

### 3. Protocol Metadata

**File**: `src/protocols/bypass-diode-testing/metadata.json`

Metadata includes:
- Protocol identification and versioning
- Category and standard compliance
- Estimated duration (33 hours)
- Equipment requirements count
- Prerequisites and related protocols
- Revision history

### 4. Python Core Framework

#### Protocol Loader (`src/core/protocol_loader.py`)
- Loads and validates JSON protocol definitions
- Lists available protocols
- Provides metadata access
- Schema validation integration

#### Data Processor (`src/core/data_processor.py`)
- Measurement data collection
- DataFrame conversion for analysis
- Aggregation by phase and measurement type
- Statistical summary calculations
- Time-series filtering

#### Validators (`src/core/validators.py`)
- Parameter validation against protocol definitions
- Type checking and range validation
- Pattern matching for strings
- QC rule validation
- Outlier detection (IQR and Z-score methods)

### 5. Database Models

**File**: `src/database/models.py`

Seven database tables:
1. **protocols** - Protocol definitions
2. **test_runs** - Test execution records
3. **measurements** - Individual measurements
4. **qc_flags** - Quality control flags
5. **test_reports** - Generated reports
6. **equipment** - Equipment inventory
7. **equipment_calibrations** - Calibration records

**Features**:
- SQLAlchemy ORM models
- Relationships between entities
- JSON fields for flexible metadata
- Automatic timestamps
- Support for SQLite and PostgreSQL

### 6. Analysis Modules

#### QC Checker (`src/analysis/qc_checks.py`)
- Real-time quality control checking
- Range validation
- Outlier detection (IQR, Z-score)
- Trend analysis
- QC summary generation

#### Statistical Analyzer (`src/analysis/statistical_analysis.py`)
- Basic statistics (mean, median, std, quartiles)
- Confidence intervals
- Outlier detection
- Degradation calculation
- Normality testing (Shapiro-Wilk)
- Distribution comparison (t-test)

#### Chart Generator (`src/analysis/charting.py`)
- Line charts for time-series data
- Scatter plots for correlations
- Bar charts for comparisons
- Box plots for distributions
- Histograms for frequency
- Heatmaps for matrices
- Protocol-driven chart generation

### 7. Streamlit UI

**File**: `src/ui/app.py`

Web application with pages:
1. **Home** - Protocol overview and quick start
2. **Protocol Runner** - Interactive protocol execution
3. **Data Viewer** - Measurement data exploration
4. **Analysis & Results** - Statistical analysis and visualization
5. **Reports** - Report generation and export
6. **Database Management** - Schema verification and maintenance

**Features**:
- Dynamic form generation from protocol JSON
- Parameter validation in real-time
- Protocol selection interface
- Database statistics dashboard
- Expandable phase information

### 8. Test Suite

#### Unit Tests
- `test_protocol_loader.py` - Protocol loading and validation
- `test_data_processor.py` - Data processing operations
- `test_validators.py` - Validation logic

#### Integration Tests
- `test_database_operations.py` - Database CRUD operations

**Features**:
- Pytest framework
- Fixtures for common test data
- In-memory database for testing
- 95%+ code coverage target

### 9. Documentation

**Files**:
- `src/protocols/bypass-diode-testing/README.md` - Protocol specification
- `docs/BYPASS-001-implementation.md` - This implementation guide

**Content**:
- Detailed test procedure
- Equipment requirements
- Safety requirements
- QC rules documentation
- Acceptance criteria
- Failure mode analysis

## Usage Examples

### Loading the Protocol

```python
from src.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("bypass-diode-testing")

# Access protocol information
protocol_info = protocol["protocol"]
print(f"Protocol: {protocol_info['name']}")
print(f"Version: {protocol_info['version']}")
print(f"Phases: {len(protocol_info['test_phases'])}")
```

### Collecting Measurements

```python
from src.core.data_processor import DataProcessor, Measurement
from datetime import datetime

processor = DataProcessor(protocol)

# Add a measurement
measurement = Measurement(
    measurement_id="diode_forward_voltage",
    phase_id="p2_initial_electrical",
    timestamp=datetime.now(),
    value=0.65,
    unit="V",
    metadata={"diode_number": 1}
)

processor.add_measurement(measurement)

# Get statistics
stats = processor.get_statistics()
print(f"Mean: {stats['mean']:.3f}V")
print(f"Std Dev: {stats['std']:.3f}V")
```

### Running QC Checks

```python
from src.analysis.qc_checks import QCChecker

qc_checker = QCChecker(protocol)

# Check a measurement
measurement_dict = {
    "measurement_id": "diode_forward_voltage",
    "phase_id": "p2_initial_electrical",
    "value": 0.95  # Out of range value
}

flags = qc_checker.check_measurement(measurement_dict)

for flag in flags:
    print(f"QC Flag: {flag['description']}")
    print(f"Type: {flag['flag_type']}")
```

### Generating Charts

```python
from src.analysis.charting import ChartGenerator
import pandas as pd

chart_gen = ChartGenerator(protocol)

# Create line chart
df = processor.get_dataframe()
fig = chart_gen.create_line_chart(
    df,
    x_column="timestamp",
    y_columns=["value"],
    title="Diode Voltage Over Time"
)

fig.show()
```

### Database Operations

```python
from src.database.connection import DatabaseManager
from src.database.models import Protocol, TestRun

db_manager = DatabaseManager("sqlite:///test_protocols.db")
db_manager.init_db()

# Create protocol record
protocol_record = Protocol(
    id="bypass-diode-testing-v1",
    name="Bypass Diode Testing Protocol",
    code="BYPASS-001",
    version="1.0.0",
    category="Safety",
    standard="IEC 61215 MQT 18",
    definition=protocol
)

with db_manager.get_session() as session:
    session.add(protocol_record)
    session.commit()
```

### Running the Streamlit UI

```bash
cd test-protocols
streamlit run src/ui/app.py
```

## Configuration

### Database Configuration

Edit `config/development.yaml`:

```yaml
database:
  url: "sqlite:///test_protocols.db"
  echo: false
  pool_size: 5
```

For production with PostgreSQL:

```yaml
database:
  url: "postgresql://user:password@localhost/test_protocols"
  echo: false
  pool_size: 20
```

### Protocol Path Configuration

```yaml
protocols:
  base_path: "src/protocols"
  schema_validation: true
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/unit/test_protocol_loader.py -v
```

## Development Workflow

### Adding a New Protocol

1. Create protocol directory: `src/protocols/your-protocol/`
2. Create `protocol.json` with protocol definition
3. Create `schema.json` for validation
4. Create `metadata.json` with protocol info
5. Write `README.md` with documentation
6. Add tests in `tests/unit/`

### Extending the Framework

1. **New Analysis Method**:
   - Add to `src/analysis/statistical_analysis.py`
   - Write unit tests
   - Update documentation

2. **New Chart Type**:
   - Add to `src/analysis/charting.py`
   - Add to protocol analysis section
   - Test with sample data

3. **New QC Rule Type**:
   - Extend `src/analysis/qc_checks.py`
   - Update schema validation
   - Add tests

## Deployment

### Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.connection import DatabaseManager; db = DatabaseManager(); db.init_db()"

# Run Streamlit app
streamlit run src/ui/app.py
```

### Production Environment

1. Use PostgreSQL database
2. Configure environment variables
3. Set up proper logging
4. Enable HTTPS for Streamlit
5. Configure backup strategy

## Integration Points

### LIMS Integration

Configure in `config/production.yaml`:

```yaml
integrations:
  lims:
    enabled: true
    api_url: "https://lims.example.com/api"
    timeout: 30
```

### QMS Integration

```yaml
integrations:
  qms:
    enabled: true
    api_url: "https://qms.example.com/api"
    timeout: 30
```

## Troubleshooting

### Common Issues

1. **Protocol Not Loading**
   - Check JSON syntax validity
   - Verify schema compliance
   - Check file permissions

2. **Database Errors**
   - Verify database URL is correct
   - Check database permissions
   - Run `init_db()` to create tables

3. **UI Not Starting**
   - Verify Streamlit is installed
   - Check port 8501 is available
   - Review logs for errors

## Performance Considerations

- Database queries are optimized with indexes
- Large datasets use chunked processing
- Charts use Plotly for interactive performance
- Session state manages UI state efficiently

## Security Considerations

- Parameterized database queries prevent SQL injection
- Input validation on all user inputs
- File path validation prevents directory traversal
- Equipment calibration verification enforced

## Future Enhancements

Planned features:
- Real-time data acquisition from instruments
- Automated report generation in PDF format
- Email notifications for QC failures
- Multi-user authentication and authorization
- API for external system integration
- Advanced statistical analysis (SPC charts)
- Machine learning for failure prediction

## Support

For issues or questions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Documentation: See `docs/` directory
- Protocol Specs: See individual protocol README files
