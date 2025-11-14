# PV Test Protocol Framework - Architecture Documentation

## Overview

The PV Test Protocol Framework is a comprehensive system for managing, executing, and analyzing standardized tests for photovoltaic modules. The framework provides a flexible, JSON-driven approach to test protocol definition and execution.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Streamlit Web Application                  │  │
│  │  - Protocol Selection                                │  │
│  │  - Test Execution Interface                          │  │
│  │  - Results Visualization                             │  │
│  │  - Report Generation                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Core Components                                     │  │
│  │  - ProtocolLoader: Load and validate protocols      │  │
│  │  - TestExecutor: Execute test sessions              │  │
│  │  - DataCollector: Collect measurement data          │  │
│  │  - ResultEvaluator: Evaluate pass/fail criteria     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Analysis Components                                 │  │
│  │  - Statistical Analysis                              │  │
│  │  - Charting and Visualization                        │  │
│  │  - Report Generation                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Protocol Definitions (JSON)                         │  │
│  │  - Test protocols with full specifications          │  │
│  │  - JSON schemas for validation                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database (PostgreSQL)                               │  │
│  │  - Test sessions                                     │  │
│  │  - Measurements and results                          │  │
│  │  - Samples and metadata                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Protocol Definition System

#### JSON Protocol Format

Protocols are defined in JSON format with the following structure:

- **Metadata**: Description, applicable products, requirements
- **Parameters**: Configurable test parameters with validation rules
- **Sample Requirements**: Sample size, conditioning, mounting
- **Test Sequence**: Step-by-step procedure
- **Measurements**: Pre-test, during-test, and post-test measurements
- **Pass Criteria**: Rules for determining pass/fail status
- **Reporting**: Required charts and report sections
- **Quality Controls**: QC checks to perform

#### JSON Schema Validation

All protocols are validated against JSON schemas to ensure:
- Structural correctness
- Required fields presence
- Data type compliance
- Value range validation

### 2. Core Components

#### ProtocolLoader

**Responsibilities:**
- Load protocol JSON files from filesystem
- Validate protocols against JSON schema
- Parse JSON into Pydantic models
- Provide protocol querying capabilities

**Key Methods:**
```python
- list_protocols(category: Optional[str]) -> List[Dict]
- load_protocol(protocol_id: str) -> Protocol
- validate_protocol_file(file_path: Path) -> Tuple[bool, Optional[str]]
```

#### TestExecutor

**Responsibilities:**
- Manage test session lifecycle
- Collect measurement data
- Record QC checks
- Evaluate pass/fail criteria

**Key Methods:**
```python
- start_session(operator_id, parameters, samples) -> TestSession
- add_measurement(measurement_id, data) -> MeasurementData
- add_qc_check(check_id, result) -> QCCheckResult
- complete_session() -> TestSession
- evaluate_results() -> TestResult
```

### 3. Data Models

#### Using Pydantic for Type Safety

All data structures use Pydantic models for:
- Type validation
- Serialization/deserialization
- Data integrity
- IDE support

**Key Models:**
- `Protocol`: Complete protocol definition
- `TestSession`: Active test session
- `MeasurementData`: Individual measurements
- `TestResult`: Evaluated test results
- `Sample`: Specimen information

### 4. Analysis Components

#### Statistical Analysis

Provides functions for:
- Degradation calculation
- Statistical summaries (mean, std, etc.)
- Confidence intervals
- Hypothesis testing (t-tests)
- PSD analysis for vibration data

#### Visualization

Uses Plotly for interactive charts:
- I-V curves
- Power comparisons
- Degradation charts
- PSD plots
- Time series plots

### 5. Database Schema

PostgreSQL database with tables for:
- **test_protocols**: Protocol definitions
- **test_sessions**: Test session records
- **samples**: Sample/specimen tracking
- **test_measurements**: Measurement data
- **qc_checks**: Quality control results
- **test_results**: Evaluated results
- **criterion_evaluations**: Individual criterion results
- **reports**: Generated report metadata

## Data Flow

### Test Execution Flow

```
1. User selects protocol
   ↓
2. ProtocolLoader loads protocol definition
   ↓
3. User configures test parameters and samples
   ↓
4. TestExecutor creates new session
   ↓
5. User collects measurements (pre, during, post)
   ↓
6. Data is validated and stored
   ↓
7. User completes test
   ↓
8. TestExecutor evaluates pass/fail criteria
   ↓
9. Results are displayed/exported
   ↓
10. Reports are generated
```

### Data Validation Flow

```
Protocol JSON
   ↓
JSON Schema Validation
   ↓
Pydantic Model Parsing
   ↓
Business Logic Validation
   ↓
Database Constraints
```

## Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **Pydantic**: Data validation and serialization
- **NumPy/SciPy**: Scientific computing and statistics
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualization
- **JSONSchema**: Protocol validation

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive charts in UI

### Database
- **PostgreSQL**: Primary data storage
- **SQLAlchemy**: ORM (future implementation)

### Testing
- **pytest**: Unit and integration testing
- **pytest-cov**: Code coverage analysis

## Design Patterns

### 1. Strategy Pattern
The framework uses the Strategy pattern for:
- Different test execution strategies per protocol type
- Multiple chart types for different data
- Various report formats (PDF, Excel, JSON)

### 2. Factory Pattern
Used for creating:
- Protocol instances from JSON
- Measurement objects based on type
- Chart objects based on configuration

### 3. Observer Pattern
For real-time updates during test execution:
- Progress monitoring
- Data collection events
- Status changes

## Extensibility

### Adding New Protocols

1. Create JSON file in appropriate category directory
2. Follow JSON schema specification
3. Define all required sections
4. Validate using `ProtocolLoader.validate_protocol_file()`

### Adding New Test Types

1. Extend `TestCategory` enum if needed
2. Create protocol JSON with new test type
3. Implement custom evaluation logic if needed
4. Add specific analysis functions

### Adding New Measurements

1. Define measurement in protocol JSON
2. Specify type: qualitative, quantitative, or time_series
3. TestExecutor automatically handles data collection
4. Add custom visualization if needed

## Security Considerations

### Data Integrity
- JSON schema validation prevents malformed protocols
- Pydantic models ensure type safety
- Database constraints prevent invalid data

### Access Control
- Operator identification for all operations
- Audit logging for data changes
- Session tracking

### Data Privacy
- No sensitive data in protocol definitions
- Secure sample identification
- Configurable data retention policies

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Protocols loaded only when needed
2. **Caching**: Protocol definitions cached after first load
3. **Batch Operations**: Bulk inserts for measurements
4. **Indexing**: Database indexes on frequently queried fields
5. **Async Operations**: Background processing for reports

### Scalability

- Stateless design allows horizontal scaling
- Database can be scaled independently
- Session data stored in database, not memory
- File-based protocol definitions for easy distribution

## Monitoring and Logging

### Logging Strategy

- Application logs for debugging
- Audit logs for compliance
- Performance logs for optimization
- Error logs for troubleshooting

### Metrics to Monitor

- Test session duration
- Protocol usage statistics
- Pass/fail rates
- System performance metrics

## Future Enhancements

### Planned Features

1. **Real-time Data Streaming**: Live data collection from test equipment
2. **Machine Learning**: Predictive failure analysis
3. **Multi-user Collaboration**: Shared test sessions
4. **API Development**: REST API for external integrations
5. **Mobile Application**: Mobile interface for data entry
6. **Cloud Integration**: Cloud storage and processing
7. **Advanced Analytics**: Trend analysis across tests
8. **Report Templates**: Customizable report templates

## Conclusion

The PV Test Protocol Framework provides a robust, flexible, and extensible platform for standardized photovoltaic module testing. Its modular architecture, comprehensive data models, and powerful analysis capabilities make it suitable for both research and production environments.
