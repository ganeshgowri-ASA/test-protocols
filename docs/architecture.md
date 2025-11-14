# System Architecture

## Overview

The Test Protocols Framework is designed as a modular, extensible system for managing and executing PV testing protocols.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Streamlit   │  │   GenSpark   │  │   REST API   │          │
│  │     UI       │  │      UI      │  │   (Future)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         │    Application / Business Logic Layer                 │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │          Protocol Management                      │           │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │           │
│  │  │ Protocol │  │ Parameter│  │   Test   │       │           │
│  │  │  Loader  │  │Validation│  │ Executor │       │           │
│  │  └──────────┘  └──────────┘  └──────────┘       │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │     Data Collection & Analysis                    │           │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │           │
│  │  │   Data   │  │    QC    │  │  Report  │       │           │
│  │  │Collector │  │  Checks  │  │Generator │       │           │
│  │  └──────────┘  └──────────┘  └──────────┘       │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │          Integration Layer                        │           │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │           │
│  │  │   LIMS   │  │   QMS    │  │    PM    │       │           │
│  │  │Interface │  │Interface │  │Interface │       │           │
│  │  └──────────┘  └──────────┘  └──────────┘       │           │
│  └──────────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                   Data Layer                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │              Database (PostgreSQL/SQLite)         │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │          │
│  │  │Protocols │  │ Test     │  │   Data   │       │          │
│  │  │          │  │ Runs     │  │  Points  │       │          │
│  │  └──────────┘  └──────────┘  └──────────┘       │          │
│  │  ┌──────────┐  ┌──────────┐                     │          │
│  │  │    QC    │  │ Interim  │                     │          │
│  │  │ Results  │  │  Tests   │                     │          │
│  │  └──────────┘  └──────────┘                     │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │           File Storage (JSON Protocols)           │          │
│  │           protocols/environmental/*.json          │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Description

### 1. User Interface Layer

#### Streamlit UI (`ui/`)
- Protocol selection interface
- Parameter configuration forms
- Real-time test monitoring
- Results visualization
- Report generation and download

#### Future: REST API
- Programmatic access to protocols
- Test execution control
- Data query endpoints

### 2. Application Layer

#### Protocol Management (`protocols/`)
- **Base Protocol (`base.py`)**: Abstract base class for all protocols
- **Protocol Validator (`schema.py`)**: JSON schema validation
- **Environmental Protocols (`environmental/`)**: Specialized implementations
  - `DesertClimateProtocol`
  - Future: `HumidityFreezeProtocol`, `DampHeatProtocol`, etc.

#### Data Collection & Analysis
- Continuous data collection
- Real-time QC checks
- Statistical analysis
- Report generation

#### Integration Layer (`integrations/`)
- LIMS (Laboratory Information Management System)
- QMS (Quality Management System)
- Project Management tools

### 3. Data Layer

#### Database (`database/`)
- **Models (`models.py`)**: SQLAlchemy ORM models
  - `Protocol`: Protocol definitions
  - `TestRun`: Test execution records
  - `DataPoint`: Time-series measurements
  - `QCResult`: Quality control results
  - `InterimTest`: Periodic test measurements

- **Session (`session.py`)**: Database connection management

#### File Storage
- Protocol definitions stored as JSON files
- Easy version control with Git
- Human-readable and editable

## Data Flow

### Protocol Execution Flow

```
1. User selects protocol
   ↓
2. System loads JSON definition
   ↓
3. Protocol validated against schema
   ↓
4. User configures parameters
   ↓
5. Parameters validated
   ↓
6. Test run created in database
   ↓
7. Test execution begins
   ↓
8. Continuous data collection
   │  ├─> Store to database
   │  └─> Run QC checks
   ↓
9. Periodic interim tests
   │  ├─> Measure I-V curves
   │  ├─> Check insulation
   │  └─> Visual inspection
   ↓
10. Post-test measurements
    ↓
11. Generate report
    ↓
12. Export results
```

### Data Collection Flow

```
Equipment/Sensors
      ↓
Data Collector
      ├─> Real-time display
      ├─> Database storage
      └─> QC validator
            ├─> Pass → Continue
            └─> Fail → Alert/Abort
```

## Design Patterns

### 1. Template Method Pattern
- `BaseProtocol` defines the test execution template
- Specific protocols override steps as needed
- Ensures consistent test flow

### 2. Strategy Pattern
- Different QC check strategies
- Pluggable report generators
- Flexible integration adapters

### 3. Repository Pattern
- Database access abstracted through repositories
- Clean separation of data access logic
- Easy to test and mock

### 4. Factory Pattern
- Protocol factory for creating protocol instances
- Integration factory for external system connections

## Technology Stack

### Backend
- **Python 3.9+**: Core language
- **SQLAlchemy**: ORM and database abstraction
- **Pydantic**: Data validation
- **NumPy/Pandas**: Data analysis

### Frontend
- **Streamlit**: Web UI framework
- **Plotly**: Interactive charts
- **Pandas**: Data tables

### Database
- **PostgreSQL**: Production database
- **SQLite**: Development/testing

### Testing
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **hypothesis**: Property-based testing

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Database connection pooling
- Async operations for long-running tests

### Data Volume
- Efficient indexing on time-series data
- Partitioning by test run
- Archive old test runs

### Performance
- Lazy loading of protocol definitions
- Caching frequently accessed data
- Batch inserts for data points

## Security

### Data Protection
- Database encryption at rest
- Secure credential storage
- Role-based access control (future)

### Validation
- Input validation at all layers
- SQL injection prevention (parameterized queries)
- JSON schema validation

## Extensibility

### Adding New Protocols
1. Create JSON definition in `protocols/`
2. Optionally extend `BaseProtocol` for custom behavior
3. Add tests
4. Update documentation

### Adding New Integrations
1. Create adapter in `integrations/`
2. Implement standard interface
3. Configure in settings
4. Add integration tests

### Custom QC Checks
1. Define check in protocol JSON
2. Implement check logic in protocol class
3. Configure alert actions

## Monitoring and Logging

### Logging
- Structured logging with levels
- Separate logs for:
  - Application events
  - Test execution
  - QC checks
  - Integration calls

### Metrics
- Test execution duration
- QC check pass rates
- Data collection completeness
- System performance metrics
