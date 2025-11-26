# System Architecture
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Last Updated:** November 2024

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [Component Architecture](#3-component-architecture)
4. [Data Architecture](#4-data-architecture)
5. [Infrastructure Architecture](#5-infrastructure-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Integration Architecture](#7-integration-architecture)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. System Overview

### 1.1 Purpose

The Solar PV Testing LIMS-QMS System is an enterprise-grade Laboratory Information Management System (LIMS) combined with Quality Management System (QMS) for comprehensive solar photovoltaic module testing.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Home    │  │ Service  │  │Equipment │  │  Test    │       │
│  │Dashboard │  │ Request  │  │ Booking  │  │Protocols │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────────┐
│                    APPLICATION LAYER                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │  Business   │ │  Workflow   │ │ Calculation │              │
│  │   Logic     │ │   Engine    │ │   Engine    │              │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘              │
└─────────┼───────────────┼───────────────┼──────────────────────┘
          │               │               │
┌─────────┴───────────────┴───────────────┴──────────────────────┐
│                   INFRASTRUCTURE LAYER                          │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │Database│ │Logging │ │Monitor │ │Security│ │ Cache  │       │
│  │Manager │ │        │ │        │ │        │ │        │       │
│  └────┬───┘ └────────┘ └────────┘ └────────┘ └────────┘       │
└───────┼────────────────────────────────────────────────────────┘
        │
┌───────┴────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                             │  │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐      │  │
│  │  │Users  │ │Service│ │Equip- │ │Test   │ │Audit  │      │  │
│  │  │       │ │Request│ │ment   │ │Data   │ │Logs   │      │  │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Streamlit | Interactive web UI |
| Backend | Python 3.11 | Business logic |
| Database | PostgreSQL 15 | Persistent storage |
| Cache | In-memory LRU | Performance optimization |
| Platform | Railway | Cloud hosting |
| CI/CD | GitHub Actions | Automated deployment |

---

## 2. Architecture Principles

### 2.1 Design Principles

1. **Modularity**: Components are loosely coupled and independently deployable
2. **Scalability**: Horizontal scaling through stateless design
3. **Security First**: Defense in depth, principle of least privilege
4. **Observability**: Comprehensive logging, metrics, and tracing
5. **Resilience**: Graceful degradation, automatic recovery

### 2.2 Code Organization

```
test-protocols/
├── app.py                    # Main entry point
├── config/
│   ├── settings.py          # Application configuration
│   ├── database.py          # Database setup
│   └── protocols_registry.py # Protocol definitions
├── database/
│   └── models.py            # SQLAlchemy models
├── infrastructure/
│   ├── database.py          # Advanced DB management
│   ├── logging_config.py    # Structured logging
│   ├── monitoring.py        # Health checks & metrics
│   ├── security.py          # Auth & rate limiting
│   ├── error_handling.py    # Error management
│   └── cache.py             # Caching layer
├── components/
│   ├── navigation.py        # UI navigation
│   ├── analytics_engine.py  # Analytics processing
│   └── visualizations.py    # Charts & graphs
├── pages/
│   ├── 2_Service_Request.py
│   ├── 3_Incoming_Inspection.py
│   ├── 4_Equipment_Booking.py
│   └── 5_Test_Protocols.py
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    └── ...
```

---

## 3. Component Architecture

### 3.1 User Interface Components

```
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT APPLICATION                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Header     │  │   Sidebar    │  │   Footer     │      │
│  │  Component   │  │  Navigation  │  │  Component   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    PAGE CONTENT                        │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│  │  │  Forms   │ │  Tables  │ │  Charts  │ │  Metrics │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Business Logic Components

```python
# Component responsibilities

class ServiceRequestManager:
    """Handles service request lifecycle"""
    - create_request()
    - submit_request()
    - approve_request()
    - cancel_request()

class InspectionManager:
    """Manages incoming inspections"""
    - create_inspection()
    - record_findings()
    - complete_inspection()

class EquipmentManager:
    """Equipment booking and availability"""
    - check_availability()
    - create_booking()
    - cancel_booking()

class TestExecutionManager:
    """Test execution workflow"""
    - start_test()
    - record_data()
    - calculate_results()
    - complete_test()

class ReportGenerator:
    """Report generation"""
    - generate_test_report()
    - export_data()
```

### 3.3 Infrastructure Components

```
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   Database    │  │   Logging     │  │  Monitoring   │  │
│  │   Manager     │  │   System      │  │   System      │  │
│  │               │  │               │  │               │  │
│  │ - Connection  │  │ - JSON Format │  │ - Health      │  │
│  │   Pooling     │  │ - Structured  │  │   Checks      │  │
│  │ - Retry Logic │  │ - Multiple    │  │ - Metrics     │  │
│  │ - Health      │  │   Handlers    │  │ - Alerts      │  │
│  │   Check       │  │               │  │               │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   Security    │  │    Error      │  │    Cache      │  │
│  │   Manager     │  │   Handler     │  │   Manager     │  │
│  │               │  │               │  │               │  │
│  │ - Auth        │  │ - Exception   │  │ - LRU Cache   │  │
│  │ - Rate Limit  │  │   Handling    │  │ - TTL Support │  │
│  │ - Sessions    │  │ - Recovery    │  │ - Stats       │  │
│  │ - Tokens      │  │ - Logging     │  │               │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Architecture

### 4.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │  ServiceRequest │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ username        │◄──────┤ created_by      │
│ email           │       │ request_number  │
│ password_hash   │       │ client_name     │
│ role            │       │ status          │
│ department      │       │ protocols[]     │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │                         │
         │     ┌───────────────────┼───────────────────┐
         │     │                   │                   │
         │     ▼                   ▼                   ▼
         │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
         │  │ Inspection  │  │TestExecution│  │  Equipment  │
         │  ├─────────────┤  ├─────────────┤  ├─────────────┤
         │  │ id          │  │ id          │  │ id          │
         │  │ sample_id   │  │ protocol_id │  │ name        │
         │  │ status      │  │ sample_id   │  │ status      │
         │  │ passed      │  │ results     │  │ location    │
         │  └─────────────┘  └──────┬──────┘  └──────┬──────┘
         │                          │                 │
         │                          ▼                 │
         │                   ┌─────────────┐         │
         │                   │  TestData   │         │
         │                   ├─────────────┤         │
         │                   │ id          │         │
         │                   │ value       │         │
         │                   │ timestamp   │         │
         │                   └─────────────┘         │
         │                                           │
         │                   ┌─────────────┐         │
         └──────────────────►│  AuditLog   │◄────────┘
                             ├─────────────┤
                             │ id          │
                             │ user_id     │
                             │ action      │
                             │ table_name  │
                             │ old_values  │
                             │ new_values  │
                             └─────────────┘
```

### 4.2 Data Flow

```
Service Request → Inspection → Equipment Booking → Test Execution → Report

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Service  │    │ Incoming │    │Equipment │    │   Test   │    │  Report  │
│ Request  │───►│Inspection│───►│ Booking  │───►│Execution │───►│Generation│
│ Created  │    │Completed │    │ Confirmed│    │Completed │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           AUDIT LOG                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Database Optimization

```sql
-- Indexes for performance
CREATE INDEX idx_service_request_status ON service_requests(status);
CREATE INDEX idx_test_execution_sample ON test_executions(sample_id);
CREATE INDEX idx_audit_log_created ON audit_logs(created_at);

-- Partitioning for large tables (future)
-- Partition audit_logs by month
-- Partition test_data by test_execution_id
```

---

## 5. Infrastructure Architecture

### 5.1 Database Manager Architecture

```python
class DatabaseManager:
    """
    Singleton database manager with:
    - Connection pooling (QueuePool)
    - Automatic retry with exponential backoff
    - Query performance metrics
    - Health checking
    """

    def __init__(self):
        self.config = DatabaseConfig()
        self.metrics = QueryMetrics()
        self._engine = None
        self._session_factory = None

    # Connection pool configuration
    pool_size = 10          # Base connections
    max_overflow = 20       # Additional connections
    pool_timeout = 30       # Wait time for connection
    pool_recycle = 1800     # Recycle connections after 30 min
```

### 5.2 Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STRUCTURED LOGGING                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Application Events                                         │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                       │
│  │ StructuredLogger│                                       │
│  │                 │                                       │
│  │ - JSON Formatter│                                       │
│  │ - Context       │                                       │
│  │ - Masking       │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│     ┌─────┴─────┐                                          │
│     ▼           ▼                                          │
│  ┌──────┐  ┌──────┐                                        │
│  │stdout│  │ file │                                        │
│  │(JSON)│  │(opt) │                                        │
│  └──┬───┘  └──────┘                                        │
│     │                                                       │
│     ▼                                                       │
│  Railway Log Aggregation                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Log Format:
{
  "timestamp": "2024-11-26T10:30:00.000Z",
  "level": "INFO",
  "logger": "solar_pv_lims",
  "message": "Test execution completed",
  "service": "solar-pv-lims",
  "environment": "production",
  "source": {"file": "app.py", "line": 45},
  "extra": {"test_id": 123, "duration_ms": 45.2}
}
```

### 5.3 Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │  HealthChecker  │    │ MetricsCollector│               │
│  │                 │    │                 │               │
│  │ - Liveness      │    │ - Counters      │               │
│  │ - Readiness     │    │ - Gauges        │               │
│  │ - Component     │    │ - Histograms    │               │
│  │   checks        │    │ - Time series   │               │
│  └────────┬────────┘    └────────┬────────┘               │
│           │                      │                         │
│           └──────────┬───────────┘                         │
│                      ▼                                      │
│           ┌─────────────────────┐                          │
│           │ PerformanceMonitor  │                          │
│           │                     │                          │
│           │ - Request tracking  │                          │
│           │ - DB query timing   │                          │
│           │ - Resource usage    │                          │
│           └─────────────────────┘                          │
│                      │                                      │
│                      ▼                                      │
│           ┌─────────────────────┐                          │
│           │      Endpoints      │                          │
│           │                     │                          │
│           │ GET /health         │                          │
│           │ GET /healthz        │                          │
│           │ GET /ready          │                          │
│           │ GET /metrics        │                          │
│           └─────────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐
│ Client  │────►│ Rate Limiter│────►│    Auth     │────►│   App   │
│         │     │             │     │   Manager   │     │         │
└─────────┘     └─────────────┘     └─────────────┘     └─────────┘
     │                                     │
     │                                     ▼
     │                           ┌─────────────────┐
     │                           │Password Manager │
     │                           │ - bcrypt hash   │
     │                           │ - validation    │
     │                           └─────────────────┘
     │                                     │
     │                                     ▼
     │                           ┌─────────────────┐
     │                           │ Token Manager   │
     │                           │ - JWT tokens    │
     │                           │ - Refresh       │
     │                           └─────────────────┘
     │                                     │
     │                                     ▼
     │                           ┌─────────────────┐
     └──────────────────────────►│Session Manager  │
                                 │ - Session store │
                                 │ - Expiry        │
                                 └─────────────────┘
```

### 6.2 Rate Limiting

```python
class RateLimiter:
    """
    Token bucket rate limiter:
    - 100 requests per minute (default)
    - Per-client tracking
    - Sliding window algorithm
    """

    # Limits by endpoint type
    limits = {
        "auth": (10, 60),      # 10 per minute
        "read": (100, 60),     # 100 per minute
        "write": (30, 60),     # 30 per minute
        "upload": (10, 60),    # 10 per minute
    }
```

### 6.3 Security Headers

```python
# Applied to all responses
security_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

---

## 7. Integration Architecture

### 7.1 External Integrations

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   Email       │  │  Equipment    │  │   Document    │  │
│  │   Service     │  │   APIs        │  │   Storage     │  │
│  │               │  │               │  │               │  │
│  │ - SMTP        │  │ - Data        │  │ - S3          │  │
│  │ - Templates   │  │   Collection  │  │ - Reports     │  │
│  │ - Notifications│ │   - Control   │  │ - Exports     │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   Webhook     │  │   Export      │  │   Import      │  │
│  │   System      │  │   Services    │  │   Services    │  │
│  │               │  │               │  │               │  │
│  │ - Event       │  │ - PDF         │  │ - CSV         │  │
│  │   Triggers    │  │ - Excel       │  │ - JSON        │  │
│  │ - Callbacks   │  │ - CSV         │  │ - XML         │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Data Export Formats

```python
# Supported export formats
export_formats = {
    "json": JSONExporter,      # Full data with metadata
    "csv": CSVExporter,        # Tabular data
    "xlsx": ExcelExporter,     # Excel with formatting
    "pdf": PDFExporter,        # Formatted reports
}
```

---

## 8. Deployment Architecture

### 8.1 Railway Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                        RAILWAY                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Project                           │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │             Environment: Production            │  │   │
│  │  │                                               │  │   │
│  │  │  ┌─────────────┐    ┌─────────────┐         │  │   │
│  │  │  │   Web       │    │  PostgreSQL │         │  │   │
│  │  │  │   Service   │◄──►│   Database  │         │  │   │
│  │  │  │             │    │             │         │  │   │
│  │  │  │ Streamlit   │    │ Managed DB  │         │  │   │
│  │  │  │ app.py      │    │ 15GB        │         │  │   │
│  │  │  └─────────────┘    └─────────────┘         │  │   │
│  │  │         │                                    │  │   │
│  │  │         ▼                                    │  │   │
│  │  │  ┌─────────────┐                            │  │   │
│  │  │  │   Domain    │                            │  │   │
│  │  │  │             │                            │  │   │
│  │  │  │ *.railway   │                            │  │   │
│  │  │  │   .app      │                            │  │   │
│  │  │  └─────────────┘                            │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 CI/CD Pipeline

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Push   │──►│  Lint   │──►│  Test   │──►│  Build  │──►│ Deploy  │
│         │   │         │   │         │   │         │   │         │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
                  │             │             │             │
                  ▼             ▼             ▼             ▼
              ┌───────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
              │Flake8 │   │ pytest  │   │ Verify  │   │ Railway │
              │Black  │   │Coverage │   │ Imports │   │ CLI     │
              │isort  │   │         │   │         │   │         │
              └───────┘   └─────────┘   └─────────┘   └─────────┘
```

### 8.3 Scaling Configuration

```
Resource Limits (Railway):
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Development:     Staging:          Production:              │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐           │
│  │ 0.5 vCPU   │   │ 1 vCPU     │   │ 2 vCPU     │           │
│  │ 512MB RAM  │   │ 1GB RAM    │   │ 4GB RAM    │           │
│  │ 1 replica  │   │ 1 replica  │   │ 2 replicas │           │
│  └────────────┘   └────────────┘   └────────────┘           │
│                                                              │
│  Database Pool:   Database Pool:   Database Pool:           │
│  pool_size=5      pool_size=10     pool_size=20             │
│  max_overflow=10  max_overflow=20  max_overflow=40          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Streamlit for UI

**Context**: Need a rapid development framework for data-centric application.

**Decision**: Use Streamlit for the user interface.

**Rationale**:
- Python-native, aligns with team skills
- Rapid prototyping and iteration
- Built-in data visualization
- Easy deployment

### ADR-002: PostgreSQL for Database

**Context**: Need reliable, scalable database for production.

**Decision**: Use PostgreSQL as primary database.

**Rationale**:
- ACID compliance for data integrity
- Native Railway support
- JSON support for flexible schemas
- Excellent performance with proper indexing

### ADR-003: Modular Infrastructure

**Context**: Need maintainable, testable infrastructure code.

**Decision**: Create separate infrastructure modules.

**Rationale**:
- Single responsibility principle
- Independent testing
- Reusability across projects
- Clear dependency management

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 2024 | System | Initial release |
