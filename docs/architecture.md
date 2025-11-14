# Architecture Overview

## System Design

The PV Test Protocols Framework is designed as a modular, extensible system for defining and executing test protocols. The architecture follows a layered approach with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Streamlit Web Interface                     │   │
│  │  - Protocol Selector  - Test Execution              │   │
│  │  - Results Viewer     - Equipment Management        │   │
│  │  - Charting Components                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Protocol Engine                             │   │
│  │  - BaseProtocol (Abstract)                          │   │
│  │  - TERM001Protocol                                   │   │
│  │  - Step Execution & Validation                       │   │
│  │  - Acceptance Criteria Checking                      │   │
│  │  - Derived Value Calculations                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Data Models (Pydantic)                      │   │
│  │  - Protocol Models  - Test Execution Models         │   │
│  │  - Validation & Serialization                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Access Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Database Models (SQLAlchemy ORM)            │   │
│  │  - Protocol  - TestExecution  - TestStep            │   │
│  │  - Measurement  - QCCheck  - Equipment              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Database Connection Management              │   │
│  │  - Session Factory  - Transaction Management        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Storage Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     SQLite (Development) / PostgreSQL (Production)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Configuration Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          JSON Protocol Templates                     │   │
│  │  - TERM-001.json                                     │   │
│  │  - Protocol definitions, steps, acceptance criteria  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  External Integrations (Future)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LIMS    │    QMS    │    Project Management        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer

**Streamlit Web Interface**

The user interface is built with Streamlit, providing:
- Interactive protocol selection
- Step-by-step test execution
- Real-time data validation
- Results visualization with Plotly charts
- Equipment management

**Components:**
- `streamlit_app.py`: Main application entry point
- `protocol_selector.py`: Protocol selection interface
- `test_execution.py`: Test execution workflow
- `charting.py`: Chart and graph generation
- `results_viewer.py`: Historical results browsing

### 2. Business Logic Layer

**Protocol Engine**

The core of the system, implementing:

- **BaseProtocol**: Abstract base class defining protocol interface
  - Protocol initialization from JSON
  - Step management and execution
  - Measurement recording
  - Validation logic
  - Result generation

- **Concrete Protocols**: Specific implementations
  - `TERM001Protocol`: Terminal Robustness Test
  - Future protocols inherit from BaseProtocol

**Key Features:**
- Dynamic protocol loading from JSON templates
- Automatic validation of measurements
- Acceptance criteria evaluation
- Derived value calculation
- Step-by-step execution control

**Data Models (Pydantic)**

Type-safe data validation and serialization:
- Protocol definitions
- Test executions
- Measurements and results
- QC checks

### 3. Data Access Layer

**SQLAlchemy ORM Models**

Database schema definition using SQLAlchemy:

- **Protocol**: Protocol definitions and metadata
- **TestExecution**: Test execution instances
- **TestStep**: Individual step results
- **Measurement**: Individual measurement records
- **QCCheck**: Quality control check records
- **Equipment**: Test equipment and calibration tracking

**Relationships:**
- Protocol → TestExecution (one-to-many)
- TestExecution → TestStep (one-to-many)
- TestStep → Measurement (one-to-many)
- TestExecution → QCCheck (one-to-many)

**Connection Management:**
- Session factory pattern
- Context manager for automatic cleanup
- Transaction management

### 4. Data Storage Layer

**Database**

- **Development**: SQLite (file-based, no setup required)
- **Production**: PostgreSQL (recommended for multi-user)

**Features:**
- Full ACID compliance
- Automatic schema migration support
- Query optimization
- Connection pooling

### 5. Configuration Layer

**JSON Protocol Templates**

Protocol definitions stored as JSON:

```json
{
  "protocol_id": "TERM-001",
  "version": "1.0",
  "title": "Terminal Robustness Test",
  "test_steps": [...],
  "acceptance_criteria": [...],
  "qc_checks": [...]
}
```

**Benefits:**
- Human-readable and editable
- Version controlled
- Easy to create new protocols
- Validation against schema

## Data Flow

### Test Execution Flow

```
1. User selects protocol
   ↓
2. Protocol loaded from JSON template
   ↓
3. BaseProtocol subclass instantiated
   ↓
4. Test information entered (serial, operator)
   ↓
5. Test execution record created in DB
   ↓
6. For each step:
   a. Display step information
   b. User enters measurements
   c. System validates measurements
   d. Calculate derived values
   e. Check acceptance criteria
   f. Save step results to DB
   g. Move to next step
   ↓
7. All steps complete
   ↓
8. Generate final result
   ↓
9. Display summary and charts
   ↓
10. Export options (PDF, Excel)
```

### Data Validation Flow

```
User Input
   ↓
Pydantic Model Validation
   ↓
Business Logic Validation
   ↓
Acceptance Criteria Check
   ↓
Database Constraints
   ↓
Stored Data
```

## Design Patterns

### 1. Template Method Pattern

`BaseProtocol` defines the test execution algorithm with customizable steps:

```python
class BaseProtocol(ABC):
    def execute_test(self):
        self.start_test()
        for step in self.steps:
            self.execute_step(step)
            self.validate_step(step)
            self.calculate_derived_values(step)  # Customizable
        self.generate_result()
```

### 2. Factory Pattern

Protocol instantiation based on protocol ID:

```python
def create_protocol(protocol_id: str) -> BaseProtocol:
    if protocol_id == "TERM-001":
        return TERM001Protocol()
    # ... other protocols
```

### 3. Repository Pattern

Data access abstraction:

```python
class ProtocolRepository:
    def get_by_id(self, protocol_id: str) -> Protocol:
        ...
    def save(self, protocol: Protocol) -> None:
        ...
```

### 4. Session/Unit of Work Pattern

Database transaction management:

```python
with get_session() as session:
    # All operations in transaction
    session.add(entity)
    session.commit()  # Auto-commit on success
    # Auto-rollback on exception
```

## Extensibility Points

### Adding New Protocols

1. Create JSON template in `src/protocols/templates/`
2. Create protocol class inheriting from `BaseProtocol`
3. Implement `calculate_derived_values()` method
4. Add protocol to UI selector
5. Write tests

### Adding New Measurement Types

1. Add type to `MeasurementType` enum
2. Add UI component in `test_execution.py`
3. Add validation logic in `BaseProtocol`

### Adding Integrations

1. Create integration module in `src/integration/`
2. Implement interface (e.g., `LIMSIntegration`)
3. Add configuration to `.env`
4. Call from protocol execution hooks

## Performance Considerations

### Database

- Use connection pooling for production
- Index frequently queried columns
- Use eager loading for relationships
- Batch inserts for multiple measurements

### UI

- Cache protocol templates
- Use Streamlit caching decorators
- Lazy load historical data
- Paginate large result sets

### Memory

- Stream large report exports
- Clean up temporary data
- Use generators for bulk operations

## Security Considerations

### Data Protection

- Parameterized queries (SQLAlchemy ORM)
- Input validation (Pydantic)
- Authentication (future: integrate SSO)
- Role-based access control (future)

### Database

- Encrypted connections in production
- Separate read/write credentials
- Regular backups
- Audit logging

## Testing Strategy

### Unit Tests

- Protocol logic
- Validation functions
- Calculation methods
- Database models

### Integration Tests

- Database operations
- Complete test execution flow
- Report generation

### UI Tests

- Future: Selenium/Playwright tests

## Deployment Architecture

### Development

```
Developer Machine
  ├── Python venv
  ├── SQLite database
  └── Streamlit (port 8501)
```

### Production (Recommended)

```
Load Balancer
  │
  ├── App Server 1 (Docker container)
  │     ├── Streamlit app
  │     └── Python application
  │
  ├── App Server 2 (Docker container)
  │
  └── Database Server
        └── PostgreSQL
```

## Future Enhancements

1. **Authentication & Authorization**
   - User management
   - Role-based access
   - SSO integration

2. **Advanced Reporting**
   - PDF generation
   - Excel export with formatting
   - Email notifications

3. **Integration APIs**
   - LIMS integration
   - QMS integration
   - Project management tools

4. **Mobile Support**
   - Responsive design
   - Mobile app (React Native/Flutter)

5. **Advanced Analytics**
   - Statistical process control
   - Trend analysis
   - Predictive maintenance

## Technology Choices

### Why Python?

- Rich scientific computing ecosystem
- Easy to learn and maintain
- Strong typing with type hints
- Excellent database support

### Why Streamlit?

- Rapid development
- Built-in interactive widgets
- Easy deployment
- Good for data-heavy applications

### Why SQLAlchemy?

- Database agnostic
- Strong ORM capabilities
- Excellent documentation
- Migration support with Alembic

### Why Pydantic?

- Runtime validation
- Type safety
- JSON serialization
- FastAPI integration ready
