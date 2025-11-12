# PV Testing Protocol Framework - Master Workflow Orchestration System

🎯 **Complete end-to-end workflow orchestration for Photovoltaic testing protocols with full data traceability**

## 🌟 Overview

The PV Testing Protocol Framework is a comprehensive system for managing the complete lifecycle of photovoltaic testing protocols, from initial service request through final report generation. The system provides:

- **Complete Workflow Orchestration**: Service Request → Incoming Inspection → Equipment Planning → Protocol Execution → Analysis → Report Generation
- **Full Data Traceability**: Audit trails and data lineage tracking across all workflow stages
- **54+ Protocol Support**: Comprehensive coverage of IEC, UL, ASTM, and other PV testing standards
- **RESTful API Integration**: FastAPI-based endpoints for LIMS, QMS, and PM system integration
- **Interactive UI**: Streamlit-based web interface for all workflow operations
- **Real-time KPIs**: Live dashboards and analytics for workflow monitoring

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Workflow Stages](#workflow-stages)
- [API Documentation](#api-documentation)
- [Data Schemas](#data-schemas)
- [Traceability](#traceability)
- [Integration](#integration)
- [Development](#development)
- [Testing](#testing)

## ✨ Features

### Core Capabilities

1. **Service Request Management**
   - Create and submit service requests for testing
   - Multi-protocol support (select from 54+ protocols)
   - Priority management and scheduling
   - Approval workflow with audit trails

2. **Incoming Inspection Protocol** (LID/LIS Framework)
   - Sample receipt verification
   - Visual inspection with photo documentation
   - Documentation completeness check
   - Condition assessment and acceptance decisions
   - Chain of custody tracking

3. **Equipment Planning & Scheduling**
   - Equipment catalog management
   - Resource allocation optimization
   - Equipment calibration tracking
   - Conflict detection and resolution
   - Parallel execution optimization

4. **Protocol Dispatching**
   - Automatic protocol routing based on service requests
   - Equipment assignment
   - Technician allocation
   - Execution tracking and status monitoring

5. **Report Aggregation**
   - Comprehensive report generation
   - Data consolidation from all workflow stages
   - Protocol-specific and comprehensive reports
   - PDF export capability
   - QC approval workflow

6. **Complete Traceability**
   - Unique tracking IDs across all stages
   - Complete audit trail with timestamps
   - Data lineage tracking
   - Version control for all modifications
   - Integrity verification with checksums

### Technical Features

- **JSON Schema Validation**: All data validated against comprehensive JSON schemas
- **RESTful API**: Complete FastAPI implementation for external integrations
- **Real-time Dashboards**: Interactive Plotly visualizations
- **Bidirectional Linking**: Automatic data interlinking across workflow stages
- **Extensible Architecture**: Modular design for easy customization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                      │
│              (Dashboard, Service Request, Inspection,           │
│              Equipment Planning, Protocol Execution)             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                    FastAPI RESTful API                          │
│         (Integration with LIMS, QMS, PM Systems)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                 Workflow Orchestrator                           │
│              (Central coordination engine)                      │
└─────────┬────────────┬────────────┬────────────┬────────────────┘
          │            │            │            │
┌─────────┴───┐  ┌────┴────┐  ┌───┴─────┐  ┌──┴──────┐
│  Service    │  │Incoming │  │Equipment│  │Protocol │
│  Request    │  │Inspec.  │  │Planning │  │Dispatch │
│  Handler    │  │Handler  │  │Handler  │  │Handler  │
└─────────────┘  └─────────┘  └─────────┘  └─────────┘
          │            │            │            │
┌─────────┴────────────┴────────────┴────────────┴────────────────┐
│              Traceability Engine                                │
│         (Complete audit trail and data lineage)                 │
└─────────────────────────────────────────────────────────────────┘
          │
┌─────────┴─────────────────────────────────────────────────────┐
│                     Data Layer                                │
│  (JSON files / Database - Service Requests, Inspections,      │
│   Equipment Plans, Protocol Executions, Reports)              │
└───────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
test-protocols/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README_DETAILED.md             # This file
│
├── workflow/                       # Workflow orchestration modules
│   ├── orchestrator.py            # Master workflow coordinator
│   ├── protocol_dispatcher.py     # Protocol routing and execution
│   └── report_aggregator.py       # Report generation and consolidation
│
├── handlers/                       # Stage-specific handlers
│   ├── service_request_handler.py # Service request processing
│   ├── incoming_inspection_handler.py # Inspection workflow
│   └── equipment_scheduler.py     # Equipment allocation
│
├── traceability/                  # Traceability and audit trail
│   └── traceability_engine.py     # Complete audit system
│
├── api/                           # FastAPI integration
│   └── main.py                    # RESTful API endpoints
│
├── pages/                         # Streamlit pages
│   ├── 01_Service_Request.py      # Service request UI
│   ├── 02_Incoming_Inspection.py  # Inspection UI
│   └── 03_Equipment_Planning.py   # Equipment planning UI
│
├── schemas/                       # JSON schemas
│   ├── service_request/           # Service request schemas
│   ├── incoming_inspection/       # Inspection schemas
│   ├── equipment_planning/        # Equipment schemas
│   └── protocols/                 # Protocol templates
│
├── utils/                         # Utility modules
│   └── validators.py              # Schema validators
│
├── data/                          # Data storage (runtime)
│   ├── service_requests/          # Service request data
│   ├── inspections/              # Inspection records
│   ├── equipment/                # Equipment data
│   ├── protocols/                # Protocol executions
│   ├── reports/                  # Generated reports
│   ├── workflows/                # Workflow state
│   └── traceability/             # Audit trail
│
└── tests/                         # Test suite
    ├── unit/                      # Unit tests
    └── integration/               # Integration tests
```

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Initialize data directories:**
```bash
python -c "from pathlib import Path; [Path(f'data/{d}').mkdir(parents=True, exist_ok=True) for d in ['service_requests', 'inspections', 'equipment', 'protocols', 'reports', 'workflows', 'traceability', 'work_orders']]"
```

## 🎯 Quick Start

### Launch Streamlit UI

```bash
streamlit run app.py
```

Access the web interface at: `http://localhost:8501`

### Launch FastAPI Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation at: `http://localhost:8000/api/docs`

## 📊 Workflow Stages

### Stage 1: Service Request

**Purpose**: Initiate testing request with complete sample and protocol information

**Key Actions**:
- Create service request with requester and project information
- Select protocols from 54+ available protocols
- Specify sample details and special requirements
- Submit for approval

**Data Captured**:
- Requester information (name, email, department)
- Project/customer details
- Sample type, quantity, manufacturer
- Protocols requested (IEC, UL, ASTM, etc.)
- Priority level
- Special requirements

**Output**: Service Request ID (e.g., SR-2025-123456)

### Stage 2: Incoming Inspection

**Purpose**: Verify sample receipt, condition, and documentation completeness

**Key Actions**:
- Record sample receipt details
- Perform visual inspection with checklist
- Verify documentation completeness
- Assess condition and readiness for testing
- Make acceptance decision (Accept/Reject/Hold)

**LID/LIS Framework Components**:
- Sample receipt verification
- Visual inspection checklist
- Physical damage assessment
- Contamination check
- Labeling verification
- Documentation completeness
- Chain of custody
- Dimensional and electrical safety checks

**Output**: Inspection ID (e.g., II-2025-123456), Acceptance Decision

### Stage 3: Equipment Planning

**Purpose**: Allocate equipment resources and create execution schedule

**Key Actions**:
- Review protocol requirements
- Allocate equipment from catalog
- Check calibration status
- Create execution schedule
- Optimize resource utilization
- Assign technicians

**Equipment Management**:
- Equipment catalog with capabilities
- Calibration tracking
- Availability calendar
- Conflict detection
- Parallel execution optimization

**Output**: Equipment Planning ID (e.g., EP-2025-123456), Resource Allocation

### Stage 4: Protocol Execution

**Purpose**: Execute testing protocols with full data capture

**Key Actions**:
- Dispatch protocol to execution
- Record test configuration
- Capture measurements and observations
- Track procedure steps
- Record pass/fail results
- QC review and approval

**Data Captured**:
- Test conditions (temperature, humidity, irradiance)
- Sample information
- Technician details
- Step-by-step procedure execution
- Measurements with timestamps
- Test data (raw and processed)
- Pass/fail criteria evaluation
- QC approval

**Output**: Protocol Execution ID (e.g., PE-IEC61215-2025-123456), Test Results

### Stage 5: Report Generation

**Purpose**: Consolidate all workflow data into comprehensive reports

**Key Actions**:
- Aggregate data from all stages
- Generate executive summary
- Create protocol-specific reports
- Generate comprehensive workflow report
- Export to PDF
- Finalize and approve

**Report Types**:
- Comprehensive Workflow Report
- Protocol-Specific Reports
- Traceability Reports

**Output**: Report ID (e.g., RPT-2025-123456)

## 🔗 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
(Configure in production environment)

### Key Endpoints

#### Service Requests

```http
POST /api/service-requests
GET /api/service-requests
GET /api/service-requests/{request_id}
POST /api/service-requests/{request_id}/submit
POST /api/service-requests/{request_id}/approve
```

#### Inspections

```http
POST /api/inspections
GET /api/inspections
GET /api/inspections/{inspection_id}
POST /api/inspections/{inspection_id}/decision
```

#### Equipment

```http
POST /api/equipment/plans
GET /api/equipment
```

#### Protocols

```http
GET /api/protocols
GET /api/protocols/{protocol_id}
GET /api/protocols/executions
```

#### Workflows

```http
GET /api/workflows
GET /api/workflows/{workflow_id}
```

#### Traceability

```http
GET /api/traceability/audit-trail
GET /api/traceability/lineage/{entity_type}/{entity_id}
POST /api/traceability/report/{entity_type}/{entity_id}
GET /api/traceability/statistics
```

### Example API Usage

**Create Service Request:**

```python
import requests

service_request = {
    "requested_by": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "department": "R&D"
    },
    "project_customer": {
        "type": "Internal Project",
        "name": "New Module Development"
    },
    "sample_details": {
        "sample_type": "PV Module",
        "quantity": 5,
        "manufacturer": "ABC Solar"
    },
    "protocols_requested": [
        {
            "protocol_id": "IEC-61215-1",
            "protocol_name": "Crystalline Silicon PV Modules"
        }
    ],
    "priority": "High"
}

response = requests.post(
    "http://localhost:8000/api/service-requests",
    json=service_request
)

print(response.json())
```

## 📐 Data Schemas

All data structures are validated against JSON schemas located in `schemas/` directory.

### Service Request Schema
Path: `schemas/service_request/service_request_schema.json`

### Incoming Inspection Schema
Path: `schemas/incoming_inspection/incoming_inspection_schema.json`

### Equipment Planning Schema
Path: `schemas/equipment_planning/equipment_planning_schema.json`

### Protocol Template Schema
Path: `schemas/protocols/protocol_template_base.json`

## 🔍 Traceability

The traceability engine provides complete audit trail and data lineage tracking.

### Features

- **Unique Tracking IDs**: Every entity gets a unique, timestamped ID
- **Event Recording**: All actions recorded with timestamp, user, and data
- **Entity Relationships**: Bidirectional links between workflow stages
- **Data Integrity**: SHA-256 checksums for tamper detection
- **Lineage Tracking**: Complete chain from service request to final report
- **Audit Reports**: Comprehensive traceability reports for any entity

### Traceability Report Example

```python
from traceability.traceability_engine import TraceabilityEngine

engine = TraceabilityEngine()

# Generate traceability report for a service request
report = engine.generate_traceability_report(
    "service_request",
    "SR-2025-123456"
)

# Report contains:
# - Complete audit trail
# - All related entities (inspections, equipment plans, protocols)
# - Timestamps and user actions
# - Data lineage chain
# - Statistics
```

## 🔌 Integration

### LIMS Integration

The FastAPI endpoints can be integrated with Laboratory Information Management Systems:

```python
# Example LIMS integration
import requests

# Get protocol execution results
response = requests.get(
    "http://your-api-server/api/protocols/executions",
    params={"status_filter": "Completed"}
)

executions = response.json()["data"]

# Push to LIMS
for execution in executions:
    lims_client.push_results(execution)
```

### QMS Integration

Quality Management System integration for approval workflows and audit trails.

### Project Management Integration

Export workflow status and KPIs to project management systems.

## 👨‍💻 Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## 📧 Contact

For questions and support: [contact information]

## 🙏 Acknowledgments

- IEC Standards for PV testing protocols
- Streamlit and FastAPI communities
- All contributors

---

**Version**: 1.0.0
**Last Updated**: 2025-01-12
**Status**: Production Ready ✅
