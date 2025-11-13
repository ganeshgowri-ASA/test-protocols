# Test-Protocols Repository Structure Analysis

## Current State
- **Repository**: test-protocols (Brand new, initial commit only)
- **Current Branch**: claude/iam-001-incidence-angle-modifier-011CV5qwu5rkit15bYd6PN2X
- **Other Branch**: claude/genspark-54-protocols-lims-011CV5nhriFffbrsK7FZ1KiF
- **Status**: Only contains initial files (README.md, LICENSE, .gitignore)

## Project Description (from README)
"Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems."

## Key Framework Components
1. **Protocols**: JSON-based protocol templates for PV (Photovoltaic) testing
2. **UI**: Streamlit/GenSpark interface for protocol execution
3. **Analysis**: Automated data analysis and charting
4. **QC**: Quality control functionality
5. **Reporting**: Automated report generation
6. **Integration**: LIMS, QMS, and Project Management systems

---

## RECOMMENDED REPOSITORY STRUCTURE

### Root Level
```
test-protocols/
├── protocols/                    # Protocol definitions (JSON-based)
│   ├── iam-001/                 # IAM-001 Incidence Angle Modifier Protocol
│   │   ├── schema.json          # Protocol schema definition
│   │   ├── template.json        # Default protocol template
│   │   ├── config.json          # Protocol configuration
│   │   └── README.md            # Protocol documentation
│   ├── other-protocols/         # Future protocol implementations
│   └── _templates/              # Shared protocol templates
│
├── src/                         # Source code
│   ├── genspark/                # GenSpark UI integration
│   │   ├── __init__.py
│   │   ├── app.py               # Main Streamlit app entry point
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── protocol_selector.py
│   │   │   ├── data_input.py
│   │   │   ├── analysis_view.py
│   │   │   ├── charts.py
│   │   │   └── report_generator.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── protocol_setup.py
│   │   │   ├── data_entry.py
│   │   │   ├── analysis.py
│   │   │   ├── qc_review.py
│   │   │   └── reports.py
│   │   ├── config.py            # UI configuration
│   │   └── styles.css           # Styling
│   │
│   ├── protocols/               # Protocol execution engine
│   │   ├── __init__.py
│   │   ├── engine.py            # Protocol execution engine
│   │   ├── loader.py            # Protocol schema/template loader
│   │   ├── validator.py         # Data validation
│   │   └── executor.py          # Task execution
│   │
│   ├── analysis/                # Data analysis modules
│   │   ├── __init__.py
│   │   ├── analyzer.py          # Main analysis logic
│   │   ├── statistics.py        # Statistical calculations
│   │   ├── charts.py            # Chart generation
│   │   └── export.py            # Data export utilities
│   │
│   ├── qc/                      # QC/QA functionality
│   │   ├── __init__.py
│   │   ├── validator.py         # QC validation rules
│   │   ├── checks.py            # QC check implementations
│   │   └── reports.py           # QC reporting
│   │
│   ├── reporting/               # Report generation
│   │   ├── __init__.py
│   │   ├── generator.py         # Report generation engine
│   │   ├── templates/           # Report templates (Jinja2, etc.)
│   │   │   ├── html_report.html
│   │   │   ├── pdf_report.html
│   │   │   └── excel_report.py
│   │   └── exporters.py         # Export formats (PDF, Excel, etc.)
│   │
│   ├── database/                # Database models and ORM
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schema.py            # Database schema definitions
│   │   ├── migrations/          # Alembic migrations
│   │   └── repository.py        # Data access layer
│   │
│   ├── integrations/            # External system integrations
│   │   ├── __init__.py
│   │   ├── lims/                # LIMS integration
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   ├── qms/                 # QMS integration
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   └── project_mgmt/        # Project Management integration
│   │       ├── __init__.py
│   │       └── client.py
│   │
│   └── common/                  # Shared utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── exceptions.py
│       ├── decorators.py
│       ├── validators.py
│       └── constants.py
│
├── tests/                       # Test suites
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── fixtures/                # Test fixtures
│   │   ├── __init__.py
│   │   ├── sample_protocols.py
│   │   ├── sample_data.py
│   │   └── mock_integrations.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_protocol_loader.py
│   │   ├── test_validator.py
│   │   ├── test_analyzer.py
│   │   ├── test_qc.py
│   │   └── test_reporting.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_protocol_execution.py
│   │   ├── test_lims_integration.py
│   │   └── test_end_to_end.py
│   └── e2e/
│       ├── __init__.py
│       └── test_genspark_workflow.py
│
├── docs/                        # Documentation
│   ├── architecture.md          # System architecture
│   ├── api.md                   # API documentation
│   ├── protocols.md             # Protocol format specification
│   ├── installation.md          # Installation guide
│   ├── user_guide.md            # User guide
│   ├── developer_guide.md       # Developer documentation
│   └── examples/
│       ├── sample_protocol.json
│       └── sample_data.json
│
├── config/                      # Configuration files
│   ├── development.yaml         # Development config
│   ├── production.yaml          # Production config
│   ├── test.yaml                # Test config
│   ├── logging.yaml             # Logging configuration
│   └── database.yaml            # Database configuration
│
├── requirements/                # Python dependencies
│   ├── base.txt                 # Core dependencies
│   ├── dev.txt                  # Development dependencies
│   ├── test.txt                 # Testing dependencies
│   └── prod.txt                 # Production dependencies
│
├── scripts/                     # Utility scripts
│   ├── init_db.py              # Database initialization
│   ├── migrate_db.py           # Database migrations
│   ├── run_tests.sh            # Test runner
│   └── docker_build.sh         # Docker build script
│
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── .github/                     # GitHub workflows
│   ├── workflows/
│   │   ├── tests.yml            # Run tests on push
│   │   ├── lint.yml             # Code linting
│   │   └── deploy.yml           # Deployment pipeline
│   └── ISSUE_TEMPLATE/
│
├── main.py                      # Application entry point
├── setup.py                     # Package setup
├── pyproject.toml              # Project metadata
├── pytest.ini                  # Pytest configuration
├── .env.example                # Example environment variables
├── .pre-commit-config.yaml     # Pre-commit hooks
├── tox.ini                     # Tox configuration
├── Makefile                    # Make targets
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## IAM-001 Protocol Implementation Guide

### 1. Protocol Definition (JSON-based)

**Location**: `/home/user/test-protocols/protocols/iam-001/`

#### Required Files:

##### schema.json
Defines the structure and validation rules for the IAM-001 protocol:
```json
{
  "protocol_id": "IAM-001",
  "name": "Incidence Angle Modifier Measurement",
  "version": "1.0.0",
  "description": "Protocol for measuring and analyzing Incidence Angle Modifier effects",
  "parameters": {
    "angle_range": { "type": "number", "min": 0, "max": 90 },
    "measurement_intervals": { "type": "integer", "min": 1 },
    "temperature_compensation": { "type": "boolean" }
  },
  "data_fields": [
    { "name": "timestamp", "type": "datetime" },
    { "name": "angle", "type": "number" },
    { "name": "measurement", "type": "number" }
  ],
  "qc_rules": [...],
  "report_sections": [...]
}
```

##### template.json
Default template for executing the protocol

##### config.json
Protocol-specific configuration (paths, thresholds, etc.)

##### README.md
Protocol documentation

### 2. Test File Locations and Patterns

**Location**: `/home/user/test-protocols/tests/`

#### Test Patterns:
- `test_iam_001_*.py` - Protocol-specific tests
- `test_*_unit.py` - Unit tests
- `test_*_integration.py` - Integration tests
- Use pytest fixtures for sample data
- Mock external integrations (LIMS, QMS)

### 3. Database Models

**Location**: `/home/user/test-protocols/src/database/models.py`

Expected models for IAM-001:
- Protocol instance records
- Measurement data records
- QC results
- Report artifacts
- Integration audit logs

### 4. Configuration Files

**Locations**:
- `/home/user/test-protocols/config/` - YAML configs
- `/home/user/test-protocols/protocols/iam-001/config.json` - Protocol config
- `.env` - Environment variables

### 5. GenSpark Integration

**Location**: `/home/user/test-protocols/src/genspark/`

- Pages for protocol selection, data entry, analysis, QC review
- Components for data input, visualization, reporting
- Dynamic form generation from protocol schema

---

## Key Files to Create for IAM-001

1. **Protocol Definition**:
   - `/home/user/test-protocols/protocols/iam-001/schema.json`
   - `/home/user/test-protocols/protocols/iam-001/template.json`
   - `/home/user/test-protocols/protocols/iam-001/config.json`

2. **Source Code**:
   - Protocol engine and loader
   - Analysis module with IAM-specific calculations
   - QC validation rules

3. **Tests**:
   - Unit tests for protocol execution
   - Integration tests with sample data
   - E2E tests with GenSpark UI

4. **Database**:
   - SQLAlchemy models for IAM-001 data
   - Migration scripts

5. **Documentation**:
   - Protocol specification
   - API documentation
   - User guide

---

## Technology Stack (Inferred)

- **Backend**: Python 3.8+
- **UI Framework**: Streamlit or GenSpark (custom framework)
- **Database**: SQLite/PostgreSQL (via SQLAlchemy)
- **Testing**: pytest
- **Data Analysis**: pandas, numpy, scipy
- **Visualization**: matplotlib, plotly
- **Reporting**: jinja2, reportlab (PDF), openpyxl (Excel)
- **API**: FastAPI (likely, for LIMS/QMS integration)
- **Deployment**: Docker

