# API Documentation
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Base URL:** `https://your-app.railway.app/api/v1`

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Health & Monitoring](#2-health--monitoring)
3. [Service Requests](#3-service-requests)
4. [Incoming Inspections](#4-incoming-inspections)
5. [Equipment Management](#5-equipment-management)
6. [Test Protocols](#6-test-protocols)
7. [Test Executions](#7-test-executions)
8. [Reporting](#8-reporting)
9. [Error Handling](#9-error-handling)
10. [Rate Limiting](#10-rate-limiting)

---

## 1. Authentication

### 1.1 Login

Authenticate user and receive access token.

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "usr_12345",
    "session_id": "sess_abcdef",
    "access_token": "eyJ...",
    "refresh_token": "rf_xyz...",
    "expires_in": 86400
  }
}
```

### 1.2 Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "refresh_token": "rf_xyz..."
}
```

### 1.3 Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

### 1.4 API Key Authentication

For programmatic access:

```http
GET /api/v1/resource
X-API-Key: sk_your_api_key_here
```

---

## 2. Health & Monitoring

### 2.1 Liveness Check

Basic check that service is running.

```http
GET /healthz
```

**Response (200 OK):**
```json
{
  "status": "alive",
  "timestamp": "2024-11-26T10:30:00Z",
  "uptime_seconds": 86400
}
```

### 2.2 Readiness Check

Full health check including dependencies.

```http
GET /ready
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "database",
      "status": "healthy",
      "latency_ms": 5.2
    },
    {
      "name": "cache",
      "status": "healthy",
      "latency_ms": 0.5
    }
  ],
  "timestamp": "2024-11-26T10:30:00Z"
}
```

### 2.3 Full Status

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": [...],
  "system": {
    "cpu_percent": 25.5,
    "memory": {
      "used_percent": 45.2,
      "available_mb": 2048
    }
  },
  "service": {
    "name": "solar-pv-lims",
    "environment": "production",
    "version": "1.0.0"
  }
}
```

### 2.4 Metrics (Prometheus Format)

```http
GET /metrics
```

**Response (text/plain):**
```
http_requests_total{method="GET",status="200"} 1234
http_request_duration_ms{path="/api/v1/protocols"} 45.2
db_queries_total{success="true"} 5678
```

---

## 3. Service Requests

### 3.1 List Service Requests

```http
GET /api/v1/service-requests
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| per_page | int | Items per page (default: 20, max: 100) |
| status | string | Filter by status |
| client_name | string | Filter by client |
| from_date | string | Start date (ISO 8601) |
| to_date | string | End date (ISO 8601) |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "request_number": "SR-2024-0001",
        "client_name": "Solar Corp",
        "status": "in_progress",
        "sample_type": "module",
        "sample_count": 5,
        "requested_protocols": ["P1", "P28", "P48"],
        "created_at": "2024-11-20T09:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### 3.2 Create Service Request

```http
POST /api/v1/service-requests
Authorization: Bearer <token>
Content-Type: application/json

{
  "client_name": "Solar Corp",
  "client_email": "contact@solarcorp.com",
  "client_phone": "+1-555-0123",
  "sample_type": "module",
  "sample_count": 5,
  "manufacturer": "SunPower",
  "model_number": "SPR-MAX3-400",
  "serial_numbers": ["SN001", "SN002", "SN003", "SN004", "SN005"],
  "requested_protocols": ["P1", "P28", "P48"],
  "priority": "normal",
  "notes": "Expedited testing requested"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 156,
    "request_number": "SR-2024-0156",
    "status": "draft",
    "created_at": "2024-11-26T10:30:00Z"
  }
}
```

### 3.3 Get Service Request

```http
GET /api/v1/service-requests/{id}
Authorization: Bearer <token>
```

### 3.4 Update Service Request

```http
PATCH /api/v1/service-requests/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "priority": "high",
  "notes": "Updated notes"
}
```

### 3.5 Submit Service Request

```http
POST /api/v1/service-requests/{id}/submit
Authorization: Bearer <token>
```

### 3.6 Approve Service Request

```http
POST /api/v1/service-requests/{id}/approve
Authorization: Bearer <token>
```

---

## 4. Incoming Inspections

### 4.1 List Inspections

```http
GET /api/v1/inspections
Authorization: Bearer <token>
```

### 4.2 Create Inspection

```http
POST /api/v1/inspections
Authorization: Bearer <token>
Content-Type: application/json

{
  "service_request_id": 156,
  "sample_id": "SAMPLE-001",
  "physical_damage": false,
  "label_readable": true,
  "connectors_intact": true,
  "frame_condition": "excellent",
  "glass_condition": "good",
  "backsheet_condition": "good",
  "length_mm": 2108,
  "width_mm": 1048,
  "thickness_mm": 35,
  "weight_kg": 22.5,
  "remarks": "Sample in good condition"
}
```

### 4.3 Upload Inspection Photo

```http
POST /api/v1/inspections/{id}/photos
Authorization: Bearer <token>
Content-Type: multipart/form-data

photo: <file>
description: "Front view of module"
```

### 4.4 Complete Inspection

```http
POST /api/v1/inspections/{id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "passed": true,
  "remarks": "Inspection passed, sample ready for testing"
}
```

---

## 5. Equipment Management

### 5.1 List Equipment

```http
GET /api/v1/equipment
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | available, in_use, maintenance |
| category | string | simulator, chamber, tester |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "equipment_code": "EQ-SIM-001",
        "name": "Solar Simulator AAA",
        "category": "simulator",
        "status": "available",
        "location": "Lab A",
        "next_calibration_date": "2025-01-15"
      }
    ]
  }
}
```

### 5.2 Get Equipment Availability

```http
GET /api/v1/equipment/{id}/availability
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| from_date | string | Start date (ISO 8601) |
| to_date | string | End date (ISO 8601) |

**Response:**
```json
{
  "success": true,
  "data": {
    "equipment_id": 1,
    "available_slots": [
      {
        "start": "2024-11-27T09:00:00Z",
        "end": "2024-11-27T12:00:00Z"
      },
      {
        "start": "2024-11-27T14:00:00Z",
        "end": "2024-11-27T17:00:00Z"
      }
    ]
  }
}
```

### 5.3 Book Equipment

```http
POST /api/v1/equipment/{id}/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "start_time": "2024-11-27T09:00:00Z",
  "end_time": "2024-11-27T12:00:00Z",
  "test_execution_id": 45,
  "purpose": "P1 - I-V Performance Testing"
}
```

### 5.4 Cancel Booking

```http
DELETE /api/v1/equipment/bookings/{booking_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "cancellation_reason": "Test postponed"
}
```

---

## 6. Test Protocols

### 6.1 List All Protocols

```http
GET /api/v1/protocols
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "protocol_id": "P1",
        "name": "I-V Performance at STC",
        "category": "performance",
        "standard_reference": "IEC 61215-1-1",
        "estimated_duration_hours": 2,
        "required_equipment": ["EQ-SIM-001"]
      }
    ],
    "categories": {
      "performance": 12,
      "degradation": 15,
      "environmental": 12,
      "mechanical": 8,
      "safety": 7
    }
  }
}
```

### 6.2 Get Protocol Details

```http
GET /api/v1/protocols/{protocol_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "protocol_id": "P1",
    "name": "I-V Performance at STC",
    "description": "Measures I-V characteristics at Standard Test Conditions",
    "category": "performance",
    "standard_reference": "IEC 61215-1-1",
    "input_parameters": [
      {
        "name": "irradiance",
        "type": "float",
        "unit": "W/m²",
        "default": 1000
      },
      {
        "name": "temperature",
        "type": "float",
        "unit": "°C",
        "default": 25
      }
    ],
    "calculation_formulas": {
      "pmax": "vmp * imp",
      "fill_factor": "pmax / (voc * isc)"
    },
    "acceptance_criteria": {
      "power_deviation": "≤ ±3%"
    }
  }
}
```

### 6.3 Get Protocol Template

```http
GET /api/v1/protocols/{protocol_id}/template
Authorization: Bearer <token>
```

---

## 7. Test Executions

### 7.1 List Test Executions

```http
GET /api/v1/test-executions
Authorization: Bearer <token>
```

### 7.2 Start Test Execution

```http
POST /api/v1/test-executions
Authorization: Bearer <token>
Content-Type: application/json

{
  "service_request_id": 156,
  "protocol_id": "P1",
  "sample_id": "SAMPLE-001",
  "equipment_booking_id": 78
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 45,
    "execution_number": "TE-2024-0045",
    "status": "in_progress",
    "started_at": "2024-11-26T10:30:00Z"
  }
}
```

### 7.3 Submit Test Data

```http
POST /api/v1/test-executions/{id}/data
Authorization: Bearer <token>
Content-Type: application/json

{
  "input_data": {
    "irradiance": 1000,
    "temperature": 25,
    "humidity": 50
  },
  "measurements": [
    {
      "measurement_type": "voltage",
      "value": 48.5,
      "unit": "V"
    },
    {
      "measurement_type": "current",
      "value": 8.25,
      "unit": "A"
    }
  ]
}
```

### 7.4 Complete Test Execution

```http
POST /api/v1/test-executions/{id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "results": {
    "pmax": 400.125,
    "voc": 52.3,
    "isc": 9.12,
    "vmp": 48.5,
    "imp": 8.25,
    "fill_factor": 0.839
  },
  "test_passed": true,
  "remarks": "All parameters within specification"
}
```

### 7.5 Upload Test Data File

```http
POST /api/v1/test-executions/{id}/files
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <csv_file>
file_type: "raw_data"
description: "I-V curve data points"
```

---

## 8. Reporting

### 8.1 Generate Test Report

```http
POST /api/v1/reports/test-report
Authorization: Bearer <token>
Content-Type: application/json

{
  "test_execution_ids": [45, 46, 47],
  "format": "pdf",
  "include_charts": true,
  "include_raw_data": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_id": "RPT-2024-0089",
    "download_url": "/api/v1/reports/RPT-2024-0089/download",
    "expires_at": "2024-11-27T10:30:00Z"
  }
}
```

### 8.2 Download Report

```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer <token>
```

### 8.3 Export Data

```http
GET /api/v1/export/test-executions
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| format | string | csv, json, xlsx |
| from_date | string | Start date |
| to_date | string | End date |
| protocol_id | string | Filter by protocol |

---

## 9. Error Handling

### 9.1 Error Response Format

All errors follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "sample_count",
      "issue": "Must be a positive integer"
    }
  },
  "timestamp": "2024-11-26T10:30:00Z"
}
```

### 9.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input data |
| AUTH_ERROR | 401 | Authentication failed |
| FORBIDDEN | 403 | Access denied |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
| DATABASE_ERROR | 500 | Database operation failed |
| EXTERNAL_SERVICE_ERROR | 502 | Third-party service error |

---

## 10. Rate Limiting

### 10.1 Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Read operations | 100 requests | 1 minute |
| Write operations | 30 requests | 1 minute |
| File uploads | 10 requests | 1 minute |
| Reports | 5 requests | 1 minute |

### 10.2 Rate Limit Headers

All responses include rate limit information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1732617600
```

### 10.3 Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please wait 45 seconds.",
    "details": {
      "retry_after": 45
    }
  }
}
```

---

## SDK Examples

### Python

```python
import requests

class SolarPVAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def list_protocols(self):
        response = requests.get(
            f"{self.base_url}/api/v1/protocols",
            headers=self.headers
        )
        return response.json()

    def create_service_request(self, data):
        response = requests.post(
            f"{self.base_url}/api/v1/service-requests",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
api = SolarPVAPI("https://your-app.railway.app", "sk_your_api_key")
protocols = api.list_protocols()
```

### JavaScript

```javascript
const api = {
  baseUrl: 'https://your-app.railway.app',
  apiKey: 'sk_your_api_key',

  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    return response.json();
  },

  listProtocols() {
    return this.request('/api/v1/protocols');
  },

  createServiceRequest(data) {
    return this.request('/api/v1/service-requests', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
};
```

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 2024 | System | Initial release |
