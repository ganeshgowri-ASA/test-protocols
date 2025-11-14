# Test Protocols Framework

**Modular PV Testing Protocol Framework** - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

This repository contains a comprehensive framework for managing photovoltaic (PV) module testing protocols. Each protocol is defined using JSON specifications and implemented with Python analysis modules, Streamlit UI components, and database integration.

## Features

- 📋 **JSON Protocol Specifications** - Standardized protocol definitions
- 🐍 **Python Analysis Modules** - Automated data analysis and calculations
- 🖥️ **Streamlit UI** - Interactive test configuration and monitoring
- 💾 **Database Integration** - PostgreSQL/SQLite data storage
- 📊 **Automated Reporting** - PDF, HTML, CSV, and JSON export
- ✅ **Quality Control** - Built-in validation and acceptance criteria
- 🔗 **System Integration** - LIMS, QMS, and project management interfaces

## Repository Structure

```
test-protocols/
├── README.md                          # This file
├── LICENSE                            # License information
├── protocols/                         # Protocol implementations
│   ├── sponge-effect/                # SPONGE-001: Sponge Effect Testing
│   │   ├── spec.json                 # Protocol specification
│   │   ├── implementation.py         # Python implementation
│   │   ├── ui_components.py          # Streamlit UI
│   │   ├── tests/                    # Unit tests
│   │   │   ├── __init__.py
│   │   │   └── test_sponge_protocol.py
│   │   └── data/                     # Test data (gitignored)
│   └── degradation/                  # Other degradation protocols
├── database/                          # Database schemas and models
│   ├── schema.sql                    # SQL schema definitions
│   └── models.py                     # SQLAlchemy ORM models
├── ui/                               # Shared UI components
│   └── components/                   # Reusable UI widgets
├── docs/                             # Documentation
│   └── SPONGE-001-Protocol-Guide.md # Protocol documentation
└── tests/                            # Integration tests
```

## Implemented Protocols

### SPONGE-001: Sponge Effect Testing

**Category:** Degradation
**Status:** ✅ Implemented

Evaluates reversible and irreversible effects of moisture absorption/desorption cycles on PV module performance.

**Key Features:**
- Automated moisture absorption/desorption tracking
- Reversible vs. irreversible degradation analysis
- Sponge coefficient calculation
- Real-time environmental monitoring
- Comprehensive quality control

**Documentation:** [SPONGE-001 Protocol Guide](docs/SPONGE-001-Protocol-Guide.md)

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Required packages:
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `streamlit>=1.28.0`
- `plotly>=5.17.0`
- `sqlalchemy>=2.0.0`
- `psycopg2-binary>=2.9.0` (for PostgreSQL)
- `openpyxl>=3.1.0` (for Excel export)

### Running SPONGE-001 Protocol

#### Method 1: Python API

```python
from protocols.sponge_effect.implementation import SpongeProtocol, TestParameters, TestPhase

# Initialize protocol
protocol = SpongeProtocol()

# Configure parameters
params = TestParameters(
    humidity_cycles=10,
    humid_phase_temperature=85.0,
    humid_phase_rh=85.0,
    humid_phase_duration=24
)

# Create test plan
sample_ids = ['MODULE-001', 'MODULE-002', 'MODULE-003']
test_plan = protocol.create_test_plan(params, sample_ids)

# Record measurements
protocol.record_measurement(
    sample_id='MODULE-001',
    cycle=0,
    phase=TestPhase.INITIAL,
    weight_g=18000.0,
    pmax_w=300.0,
    voc_v=38.5,
    isc_a=9.0,
    ff_percent=76.5
)

# Analyze and report
analysis = protocol.analyze_sample('MODULE-001')
report = protocol.generate_report('./reports/report.json')
```

#### Method 2: Streamlit UI

```bash
streamlit run protocols/sponge-effect/ui_components.py
```

Access the UI at http://localhost:8501

### Running Tests

```bash
# Run protocol tests
python protocols/sponge-effect/tests/test_sponge_protocol.py

# Or use pytest
pytest protocols/sponge-effect/tests/
```

## Database Setup

### PostgreSQL (Production)

1. **Create database:**
```sql
CREATE DATABASE testprotocols;
CREATE USER testuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE testprotocols TO testuser;
```

2. **Initialize schema:**
```bash
psql -U testuser -d testprotocols -f database/schema.sql
```

3. **Configure connection:**
```python
from database.models import DatabaseManager

db = DatabaseManager('postgresql://testuser:password@localhost/testprotocols')
db.create_tables()
```

### SQLite (Development)

```python
from database.models import DatabaseManager

# In-memory database
db = DatabaseManager('sqlite:///:memory:')

# File-based database
db = DatabaseManager('sqlite:///./test_data.db')

db.create_tables()
```

## Support

- **Documentation:** [Protocol Guides](docs/)
- **Issues:** [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated:** 2025-11-14
**Version:** 1.0.0
