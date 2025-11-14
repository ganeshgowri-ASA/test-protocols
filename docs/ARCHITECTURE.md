# System Architecture

## Overview

The IEC 61730 Test Protocol Framework is a modular, extensible system for managing and executing photovoltaic module test protocols. It uses JSON-based dynamic templates to define test procedures and provides a user-friendly interface for test execution, data collection, and result analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                   (Streamlit/GenSpark UI)                   │
├─────────────────────────────────────────────────────────────┤
│  Home │ Run Test │ View Results │ Manage Samples │ Settings│
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                 Application Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Protocol Registry │ Test Execution │ Analysis Engine      │
│  Report Generator  │ Data Validation │ QC Checks           │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                   Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  Database (SQLAlchemy ORM)                                  │
│  ├── Test Protocols                                         │
│  ├── Test Runs                                              │
│  ├── Measurements                                           │
│  └── Results                                                │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              Integration Layer                              │
├─────────────────────────────────────────────────────────────┤
│  LIMS API │ QMS Integration │ Equipment Interface          │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Protocol System

#### Base Protocol (`protocols/base.py`)
- Abstract base class for all test protocols
- Defines standard interface: validate, run, analyze, report
- Manages measurement data collection
- Provides data export capabilities

#### Protocol Registry (`protocols/registry.py`)
- Singleton pattern for protocol management
- Dynamic protocol registration and instantiation
- Supports multiple protocol versions

#### WET-001 Protocol (`protocols/wet_leakage_current/`)
- Implements IEC 61730 MST 02 wet leakage current test
- JSON schema for parameter validation
- Custom analysis algorithms
- HTML report generation

### 2. Database Layer

#### Models (`database/models.py`)
- **TestProtocol**: Protocol definitions and schemas
- **SampleInformation**: Sample/module metadata
- **TestRun**: Test execution instances
- **Measurement**: Individual measurement points
- **TestResult**: Analysis results and conclusions

#### Session Management (`database/session.py`)
- Singleton session manager
- Support for SQLite (dev) and PostgreSQL (production)
- Automatic table creation and migration

### 3. Analysis Engine

#### WET Analyzer (`protocols/wet_leakage_current/analysis.py`)
- Statistical analysis of measurement data
- Acceptance criteria validation
- Anomaly detection using z-score
- Trending analysis using linear regression
- Pass/fail determination

### 4. User Interface

#### Streamlit Application (`ui/streamlit_app.py`)
- Main application entry point
- Navigation and routing
- Session state management

#### Pages (`ui/pages/`)
- **run_test.py**: Test configuration and execution
- **results.py**: Results viewing and analysis
- **samples.py**: Sample management
- **settings.py**: Configuration management

### 5. Utilities

#### Configuration (`utils/config.py`)
- YAML-based configuration
- Hierarchical key access
- Environment-specific settings

#### Logging (`utils/logging.py`)
- Structured logging with rotation
- Multiple output handlers
- Module-specific loggers

#### Validators (`utils/validators.py`)
- JSON schema validation
- Parameter validation
- Error handling and reporting

## Data Flow

### Test Execution Flow

```
1. User selects protocol → UI loads protocol schema
2. User enters parameters → Validation against schema
3. Test starts → TestRun created in database
4. Measurements collected → Stored in Measurement table
5. Test completes → Analysis engine processes data
6. Results generated → TestResult saved to database
7. Report created → HTML/PDF generated
```

### Measurement Collection Flow

```
Equipment → Measurement Point → Protocol → Database
                                    ↓
                              Validation
                                    ↓
                            Real-time Analysis
                                    ↓
                              UI Update
```

## Design Patterns

### 1. **Singleton Pattern**
- Configuration Manager
- Session Manager
- Protocol Registry

### 2. **Abstract Factory Pattern**
- BaseProtocol for creating protocol instances
- Standardized interface across all protocols

### 3. **Strategy Pattern**
- Different analysis strategies per protocol
- Pluggable report generators

### 4. **Observer Pattern**
- Real-time measurement updates to UI
- Event-driven test execution

## Extensibility

### Adding New Protocols

1. Create protocol directory: `protocols/new_protocol/`
2. Define JSON schema: `schema.json`
3. Implement protocol class extending `BaseProtocol`
4. Implement analysis logic
5. Create report template
6. Register in protocol registry
7. Add UI components if needed

### Adding New Analysis Methods

1. Extend analyzer class
2. Implement new statistical methods
3. Update acceptance criteria schema
4. Update report templates

## Security Considerations

- Input validation at all entry points
- SQL injection prevention via ORM
- Configurable authentication (future)
- Audit logging of all operations
- Data encryption for sensitive information (future)

## Performance Optimization

- Connection pooling for database
- Lazy loading of large datasets
- Caching of frequently accessed data
- Asynchronous measurement collection (future)
- Background report generation

## Scalability

- Horizontal scaling via load balancers
- Database sharding by test protocol
- Microservices architecture (future)
- Message queue for async tasks (future)

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Rapid UI development |
| Backend | Python 3.10+ | Application logic |
| ORM | SQLAlchemy | Database abstraction |
| Validation | Pydantic, JSONSchema | Data validation |
| Analysis | NumPy, Pandas | Statistical analysis |
| Visualization | Plotly | Interactive charts |
| Database | SQLite/PostgreSQL | Data persistence |
| Configuration | YAML | Settings management |
| Testing | PyTest | Unit/integration tests |

## Deployment Architecture

### Development
```
Local Machine
├── SQLite Database
├── Streamlit Dev Server
└── Python Virtual Environment
```

### Production
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Web    │
    │ Servers │
    └────┬────┘
         │
    ┌────┴────────┐
    │  PostgreSQL │
    │   Cluster   │
    └─────────────┘
```

## Future Enhancements

1. **REST API** for programmatic access
2. **WebSocket** support for real-time updates
3. **Docker** containerization
4. **Kubernetes** orchestration
5. **CI/CD** pipeline integration
6. **Multi-tenant** support
7. **Cloud storage** integration
8. **Mobile** application
9. **Advanced analytics** with ML
10. **Automated equipment** control
