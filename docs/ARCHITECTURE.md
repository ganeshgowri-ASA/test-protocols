# System Architecture

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Architecture Diagrams](#architecture-diagrams)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Scalability & Performance](#scalability--performance)
7. [Security Architecture](#security-architecture)

## Overview

The PV Testing Protocol Framework follows a modular, microservices-inspired architecture with clear separation of concerns. The system is designed for scalability, maintainability, and extensibility.

### Design Principles

- **Modularity**: Each protocol is self-contained and independently executable
- **Data-Driven**: JSON templates define protocol structure and behavior
- **API-First**: RESTful API for all operations
- **Event-Driven**: Asynchronous processing for long-running tests
- **Cloud-Native**: Container-ready with stateless services

## System Components

### 1. Frontend Layer

#### Streamlit Dashboard
- **Purpose**: Interactive UI for protocol execution and monitoring
- **Technology**: Streamlit, Plotly, Pandas
- **Features**:
  - Protocol selection and configuration
  - Real-time test monitoring
  - Data visualization and charting
  - Report generation interface
  - Admin configuration panel

#### GenSpark UI Integration
- **Purpose**: Alternative UI framework
- **Technology**: React, Material-UI
- **Features**:
  - Responsive design
  - Mobile support
  - Advanced analytics

### 2. Application Layer

#### Protocol Executor
```python
class ProtocolExecutor:
    """
    Core execution engine for test protocols
    """
    - load_protocol(protocol_id)
    - validate_inputs(data)
    - execute_test(parameters)
    - analyze_results(raw_data)
    - generate_report(results)
```

#### Workflow Orchestrator
```python
class WorkflowOrchestrator:
    """
    Manages end-to-end workflow
    """
    - create_service_request()
    - schedule_inspection()
    - assign_protocols()
    - track_progress()
    - finalize_reports()
```

#### Analysis Engine
```python
class AnalysisEngine:
    """
    Data analysis and QC checks
    """
    - statistical_analysis()
    - quality_control()
    - pass_fail_criteria()
    - anomaly_detection()
    - trend_analysis()
```

### 3. API Layer

#### REST API (FastAPI)
```
/api/v1/
├── service-requests/
│   ├── POST   /create
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── protocols/
│   ├── GET    /list
│   ├── GET    /{id}
│   ├── POST   /{id}/execute
│   └── GET    /{id}/status
├── inspections/
│   ├── POST   /create
│   ├── GET    /{id}
│   └── PUT    /{id}/complete
├── reports/
│   ├── GET    /{id}
│   ├── POST   /{id}/generate
│   └── GET    /{id}/download
└── integrations/
    ├── POST   /lims/sync
    ├── POST   /qms/nc-report
    └── POST   /pm/update-status
```

### 4. Data Layer

#### Database Schema

**service_requests**
```sql
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    sr_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    module_type VARCHAR(100),
    sample_quantity INTEGER,
    requested_protocols TEXT[], -- Array of protocol IDs
    status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**inspections**
```sql
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    sr_id INTEGER REFERENCES service_requests(id),
    inspector_id INTEGER REFERENCES users(id),
    inspection_date TIMESTAMP,
    findings JSONB,
    images TEXT[],
    status VARCHAR(50),
    created_at TIMESTAMP
);
```

**protocol_executions**
```sql
CREATE TABLE protocol_executions (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(50),
    sr_id INTEGER REFERENCES service_requests(id),
    operator_id INTEGER REFERENCES users(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    input_data JSONB,
    results JSONB,
    status VARCHAR(50),
    qc_status VARCHAR(50)
);
```

**test_results**
```sql
CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER REFERENCES protocol_executions(id),
    measurement_type VARCHAR(100),
    measured_value NUMERIC,
    unit VARCHAR(20),
    timestamp TIMESTAMP,
    equipment_id VARCHAR(50),
    operator_id INTEGER REFERENCES users(id)
);
```

### 5. Integration Layer

#### LIMS Integration
- **Protocol**: REST API / SOAP
- **Sync**: Bidirectional
- **Data Flow**:
  - Sample IDs → Framework
  - Test results → LIMS
  - Status updates → Both

#### QMS Integration
- **Protocol**: REST API
- **Features**:
  - NC (Non-Conformance) reporting
  - CAPA tracking
  - Audit trail sync
  - Document control

#### Project Management Integration
- **Protocol**: Webhook / REST API
- **Features**:
  - Task creation
  - Status updates
  - Resource tracking
  - Timeline sync

### 6. Storage Layer

#### File Storage
- **Raw Data**: Time-series measurements, images
- **Reports**: PDF, Excel, CSV formats
- **Templates**: JSON protocol definitions
- **Attachments**: Supporting documents

#### Object Storage (S3/Azure Blob)
```
/storage/
├── raw-data/
│   └── {sr_id}/{protocol_id}/{timestamp}/
├── reports/
│   └── {sr_id}/{report_type}/{timestamp}/
├── templates/
│   └── protocols/{protocol_id}.json
└── attachments/
    └── {sr_id}/{filename}
```

## Architecture Diagrams

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Streamlit UI    │              │  GenSpark UI     │    │
│  └────────┬─────────┘              └────────┬─────────┘    │
└───────────┼────────────────────────────────┼───────────────┘
            │                                │
            └────────────────┬───────────────┘
                             │
┌────────────────────────────┼───────────────────────────────┐
│                  Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Workflow    │  │  Protocol    │  │   Analysis   │    │
│  │ Orchestrator │  │  Executor    │  │    Engine    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────┐
│                       API Layer (FastAPI)                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints / OpenAPI / Authentication     │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────┐
│                       Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │  File Store  │  │    Cache     │    │
│  │   Database   │  │  (S3/Azure)  │  │   (Redis)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────┬───────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────┐
│                   Integration Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     LIMS     │  │     QMS      │  │      PM      │    │
│  │  Integration │  │  Integration │  │  Integration │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Architecture

```
Service Request Creation
         │
         ▼
    ┌────────┐
    │ SR-001 │
    └───┬────┘
        │
        ▼
  Initial Inspection
        │
        ├─ Visual Check
        ├─ Documentation
        └─ Protocol Selection
        │
        ▼
  Protocol Assignment
        │
        ├─ PVTP-001 (STC Power)
        ├─ PVTP-015 (Thermal Cycling)
        └─ PVTP-030 (PID Testing)
        │
        ▼
  Parallel Execution
        │
        ├─────────┬─────────┐
        ▼         ▼         ▼
    Protocol  Protocol  Protocol
       #1        #2        #3
        │         │         │
        └─────────┼─────────┘
                  │
                  ▼
           Data Analysis
                  │
                  ├─ Statistical Analysis
                  ├─ QC Checks
                  └─ Pass/Fail Determination
                  │
                  ▼
           Report Generation
                  │
                  ├─ PDF Report
                  ├─ Excel Data Export
                  └─ Certificate (if passed)
                  │
                  ▼
            Integration Sync
                  │
                  ├─ LIMS Update
                  ├─ QMS NC (if failed)
                  └─ PM Status Update
                  │
                  ▼
              Complete
```

### Data Flow Diagram

```
┌──────────────┐
│    User      │
└──────┬───────┘
       │ 1. Submit SR
       ▼
┌──────────────┐     2. Validate    ┌──────────────┐
│   API Layer  │◀──────────────────▶│   Validator  │
└──────┬───────┘                     └──────────────┘
       │ 3. Create Record
       ▼
┌──────────────┐     4. Store       ┌──────────────┐
│   Database   │◀──────────────────▶│    Cache     │
└──────┬───────┘                     └──────────────┘
       │ 5. Trigger Workflow
       ▼
┌──────────────┐     6. Load        ┌──────────────┐
│  Orchestrator│◀──────────────────▶│    JSON      │
└──────┬───────┘                     │   Template   │
       │ 7. Execute                  └──────────────┘
       ▼
┌──────────────┐     8. Analyze     ┌──────────────┐
│   Protocol   │────────────────────▶│   Analysis   │
│   Executor   │                     │    Engine    │
└──────┬───────┘                     └──────┬───────┘
       │                                     │
       │ 9. Save Results                     │
       ▼                                     │
┌──────────────┐                             │
│   Database   │◀────────────────────────────┘
└──────┬───────┘     10. QC Results
       │
       │ 11. Generate Report
       ▼
┌──────────────┐     12. Store      ┌──────────────┐
│    Report    │────────────────────▶│  File Store  │
│   Generator  │                     │    (S3)      │
└──────┬───────┘                     └──────────────┘
       │
       │ 13. Sync External Systems
       ▼
┌──────────────┐     14. Update     ┌──────────────┐
│  Integration │◀──────────────────▶│ LIMS/QMS/PM  │
│    Layer     │                     └──────────────┘
└──────┬───────┘
       │ 15. Complete
       ▼
┌──────────────┐
│     User     │
│ Notification │
└──────────────┘
```

## Technology Stack

### Backend
- **Python 3.8+**: Core language
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for database access
- **Celery**: Asynchronous task queue
- **Pandas/NumPy**: Data analysis
- **SciPy/Statsmodels**: Statistical analysis

### Frontend
- **Streamlit**: Primary UI framework
- **Plotly**: Interactive charting
- **Altair**: Statistical visualizations
- **React** (optional): GenSpark UI

### Database
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **SQLite**: Development/testing

### Storage
- **AWS S3**: Cloud object storage
- **Azure Blob**: Alternative cloud storage
- **MinIO**: Self-hosted S3-compatible storage

### DevOps
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **GitHub Actions**: CI/CD
- **Terraform**: Infrastructure as code

## Scalability & Performance

### Horizontal Scaling
- **API Layer**: Stateless, easily replicated
- **Protocol Executors**: Distributed workers
- **Database**: Read replicas for queries

### Performance Optimization
- **Caching**: Redis for frequently accessed data
- **Database Indexing**: Optimized queries
- **Async Processing**: Celery for long-running tasks
- **CDN**: Static assets delivery

### Load Balancing
```
Internet
   │
   ▼
┌─────────────┐
│   Nginx     │
│Load Balancer│
└──────┬──────┘
       │
       ├────────┬────────┬────────┐
       ▼        ▼        ▼        ▼
    API-1    API-2    API-3    API-N
       │        │        │        │
       └────────┴────────┴────────┘
                  │
                  ▼
            ┌──────────┐
            │ Database │
            │  Cluster │
            └──────────┘
```

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Role-Based Access Control (RBAC)**:
  - Admin: Full access
  - Engineer: Execute protocols, view reports
  - Operator: Execute assigned protocols
  - Viewer: Read-only access

### Data Security
- **Encryption at Rest**: AES-256
- **Encryption in Transit**: TLS 1.3
- **Database Encryption**: PostgreSQL pgcrypto
- **Secrets Management**: AWS Secrets Manager / HashiCorp Vault

### Audit Trail
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Network Security
- **Firewall Rules**: Restricted access
- **VPC**: Isolated network
- **WAF**: Web Application Firewall
- **DDoS Protection**: CloudFlare / AWS Shield

## Deployment Architecture

### Production Environment
```
┌─────────────────────────────────────────────────────────┐
│                    AWS/Azure Cloud                       │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Load Balancer (ELB/ALB)             │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────┴─────────────────────────────┐  │
│  │         Kubernetes Cluster (EKS/AKS)             │  │
│  │                                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐               │  │
│  │  │  API Pods   │  │  UI Pods    │               │  │
│  │  └─────────────┘  └─────────────┘               │  │
│  │                                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐               │  │
│  │  │ Worker Pods │  │ Cache Pods  │               │  │
│  │  └─────────────┘  └─────────────┘               │  │
│  └───────────────────────────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────┴─────────────────────────────┐  │
│  │         RDS PostgreSQL (Multi-AZ)                │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────┴─────────────────────────────┐  │
│  │         S3 Bucket / Azure Blob Storage           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-12
**Author**: System Architecture Team
