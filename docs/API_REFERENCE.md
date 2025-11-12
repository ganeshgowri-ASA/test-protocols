# API Reference

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Service Requests API](#service-requests-api)
4. [Protocols API](#protocols-api)
5. [Inspections API](#inspections-api)
6. [Executions API](#executions-api)
7. [Reports API](#reports-api)
8. [Integrations API](#integrations-api)
9. [Users & Permissions API](#users--permissions-api)
10. [Webhooks](#webhooks)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)

## Overview

The PV Testing Protocol Framework provides a RESTful API built with FastAPI, offering comprehensive access to all system functionality.

**Base URL**: `https://api.test-protocols.io/api/v1`

**API Version**: 1.0.0

**Content Type**: `application/json`

**Documentation**: `https://api.test-protocols.io/docs` (Swagger UI)

## Authentication

### JWT Token Authentication

All API endpoints (except `/auth/*`) require authentication using JWT Bearer tokens.

#### Obtain Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Using the Token

Include the token in the Authorization header:

```http
GET /api/v1/service-requests
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Service Requests API

### Create Service Request

```http
POST /api/v1/service-requests
Content-Type: application/json
Authorization: Bearer {token}

{
  "customer": {
    "name": "Solar Corporation",
    "contact_person": "John Doe",
    "email": "john@solarcorp.com",
    "phone": "+1-555-0123",
    "address": "123 Solar St, CA 90210"
  },
  "module": {
    "manufacturer": "ABC Solar",
    "model": "ASM-400M-72",
    "type": "Mono-Si",
    "power_rating": 400,
    "voltage": 48,
    "current": 10,
    "quantity": 12,
    "serial_numbers": ["SN001", "SN002", "..."]
  },
  "testing": {
    "standards": ["IEC 61215", "IEC 61730"],
    "protocols": ["PVTP-001", "PVTP-018", "PVTP-030"],
    "priority": "normal",
    "requested_delivery_date": "2025-12-31",
    "special_requirements": "Rush testing"
  }
}
```

**Response** (201 Created):
```json
{
  "id": 123,
  "sr_number": "SR-2025-0123",
  "status": "PENDING_INSPECTION",
  "created_at": "2025-11-12T10:00:00Z",
  "estimated_completion": "2025-12-15T17:00:00Z",
  "assigned_pm": {
    "id": 5,
    "name": "Jane Smith",
    "email": "jane.smith@company.com"
  }
}
```

### Get Service Request

```http
GET /api/v1/service-requests/{sr_id}
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "sr_number": "SR-2025-0123",
  "status": "TESTING_IN_PROGRESS",
  "customer": { /* customer details */ },
  "module": { /* module details */ },
  "testing": { /* testing details */ },
  "protocols": [
    {
      "protocol_id": "PVTP-001",
      "status": "COMPLETE",
      "completion_date": "2025-11-13T14:30:00Z"
    },
    {
      "protocol_id": "PVTP-018",
      "status": "IN_PROGRESS",
      "progress": 45.5,
      "estimated_completion": "2025-12-10T09:00:00Z"
    }
  ],
  "created_at": "2025-11-12T10:00:00Z",
  "updated_at": "2025-11-13T15:22:00Z"
}
```

### List Service Requests

```http
GET /api/v1/service-requests?status=IN_PROGRESS&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters**:
- `status`: Filter by status (optional)
- `customer`: Filter by customer name (optional)
- `from_date`: Start date (YYYY-MM-DD) (optional)
- `to_date`: End date (YYYY-MM-DD) (optional)
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "data": [
    { /* service request object */ },
    { /* service request object */ }
  ]
}
```

### Update Service Request

```http
PUT /api/v1/service-requests/{sr_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "PROTOCOLS_ASSIGNED",
  "testing": {
    "requested_delivery_date": "2026-01-15"
  }
}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "sr_number": "SR-2025-0123",
  "status": "PROTOCOLS_ASSIGNED",
  "updated_at": "2025-11-13T16:00:00Z"
}
```

### Delete Service Request

```http
DELETE /api/v1/service-requests/{sr_id}
Authorization: Bearer {token}
```

**Response** (204 No Content)

## Protocols API

### List All Protocols

```http
GET /api/v1/protocols
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "total": 54,
  "protocols": [
    {
      "protocol_id": "PVTP-001",
      "name": "STC Power Measurement",
      "category": "Module Performance",
      "standard": "IEC 61215-1:2021",
      "duration_hours": 2,
      "equipment_required": ["Solar Simulator", "I-V Tracer"]
    },
    { /* more protocols */ }
  ]
}
```

### Get Protocol Details

```http
GET /api/v1/protocols/{protocol_id}
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "protocol_id": "PVTP-001",
  "name": "STC Power Measurement",
  "description": "Standard Test Conditions power measurement...",
  "category": "Module Performance",
  "standard": "IEC 61215-1:2021",
  "duration_hours": 2,
  "parameters": {
    "irradiance": {
      "value": 1000,
      "unit": "W/m²",
      "tolerance": 2
    },
    "temperature": {
      "value": 25,
      "unit": "°C",
      "tolerance": 2
    },
    "spectrum": "AM1.5G"
  },
  "measurements": [
    {
      "name": "Pmax",
      "description": "Maximum power",
      "unit": "W",
      "required": true
    },
    {
      "name": "Voc",
      "description": "Open circuit voltage",
      "unit": "V",
      "required": true
    }
  ],
  "pass_fail_criteria": {
    "power_tolerance": {
      "min": -3,
      "max": 5,
      "unit": "%"
    }
  },
  "equipment_required": [
    {
      "type": "Solar Simulator",
      "calibration_required": true,
      "calibration_interval_months": 6
    }
  ]
}
```

### Get Protocol Template (JSON)

```http
GET /api/v1/protocols/{protocol_id}/template
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "protocol_id": "PVTP-001",
  "version": "1.0",
  "template": {
    /* Complete JSON template structure */
  }
}
```

## Executions API

### Execute Protocol

```http
POST /api/v1/protocols/{protocol_id}/execute
Content-Type: application/json
Authorization: Bearer {token}

{
  "sr_id": 123,
  "module_id": "SN001",
  "operator_id": 42,
  "equipment": {
    "simulator": "SIM-001",
    "iv_tracer": "IVT-001"
  },
  "parameters": {
    "irradiance": 1000,
    "temperature": 25
  }
}
```

**Response** (202 Accepted):
```json
{
  "execution_id": 5678,
  "protocol_id": "PVTP-001",
  "status": "RUNNING",
  "started_at": "2025-11-13T09:00:00Z",
  "estimated_completion": "2025-11-13T11:00:00Z"
}
```

### Get Execution Status

```http
GET /api/v1/executions/{execution_id}
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "execution_id": 5678,
  "protocol_id": "PVTP-001",
  "sr_id": 123,
  "status": "RUNNING",
  "progress": 67.5,
  "started_at": "2025-11-13T09:00:00Z",
  "current_step": "Measuring I-V curve",
  "measurements": [
    {
      "timestamp": "2025-11-13T09:15:00Z",
      "parameter": "Voc",
      "value": 48.2,
      "unit": "V"
    }
  ]
}
```

### Stop Execution

```http
POST /api/v1/executions/{execution_id}/stop
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "execution_id": 5678,
  "status": "STOPPED",
  "stopped_at": "2025-11-13T09:45:00Z"
}
```

### Get Execution Results

```http
GET /api/v1/executions/{execution_id}/results
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "execution_id": 5678,
  "protocol_id": "PVTP-001",
  "status": "COMPLETE",
  "completed_at": "2025-11-13T11:00:00Z",
  "results": {
    "measurements": {
      "Pmax": {
        "value": 398.5,
        "unit": "W",
        "uncertainty": 1.2
      },
      "Voc": {
        "value": 48.2,
        "unit": "V",
        "uncertainty": 0.1
      },
      "Isc": {
        "value": 10.5,
        "unit": "A",
        "uncertainty": 0.05
      }
    },
    "analysis": {
      "fill_factor": 78.5,
      "efficiency": 20.2
    },
    "qc_status": "PASS",
    "pass_fail": {
      "overall": "PASS",
      "criteria": [
        {
          "parameter": "Pmax",
          "expected": 400,
          "tolerance": 3,
          "measured": 398.5,
          "result": "PASS"
        }
      ]
    }
  }
}
```

## Reports API

### Generate Report

```http
POST /api/v1/reports/generate
Content-Type: application/json
Authorization: Bearer {token}

{
  "sr_id": 123,
  "report_type": "technical",
  "format": "pdf",
  "options": {
    "include_photos": true,
    "include_raw_data": true,
    "include_charts": true
  }
}
```

**Response** (202 Accepted):
```json
{
  "report_id": 999,
  "status": "GENERATING",
  "estimated_completion": "2025-11-13T12:05:00Z"
}
```

### Get Report Status

```http
GET /api/v1/reports/{report_id}
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "report_id": 999,
  "sr_id": 123,
  "report_type": "technical",
  "format": "pdf",
  "status": "COMPLETE",
  "file_size": 2458000,
  "pages": 45,
  "generated_at": "2025-11-13T12:03:00Z",
  "download_url": "/api/v1/reports/999/download",
  "expires_at": "2025-11-20T12:03:00Z"
}
```

### Download Report

```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer {token}
```

**Response** (200 OK):
- Content-Type: `application/pdf` (or appropriate MIME type)
- Content-Disposition: `attachment; filename="SR-2025-0123_Report.pdf"`
- Binary file content

### List Reports

```http
GET /api/v1/reports?sr_id=123
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "total": 3,
  "reports": [
    {
      "report_id": 999,
      "report_type": "technical",
      "format": "pdf",
      "status": "COMPLETE",
      "generated_at": "2025-11-13T12:03:00Z"
    }
  ]
}
```

## Integrations API

### Sync with LIMS

```http
POST /api/v1/integrations/lims/sync
Content-Type: application/json
Authorization: Bearer {token}

{
  "sr_id": 123,
  "sync_type": "results",
  "protocols": ["PVTP-001", "PVTP-018"]
}
```

**Response** (200 OK):
```json
{
  "sync_id": 456,
  "status": "SUCCESS",
  "synced_at": "2025-11-13T12:30:00Z",
  "lims_sample_ids": ["LIM-001", "LIM-002"],
  "records_synced": 2
}
```

### Create QMS NC Report

```http
POST /api/v1/integrations/qms/nc-report
Content-Type: application/json
Authorization: Bearer {token}

{
  "sr_id": 123,
  "protocol_id": "PVTP-018",
  "module_id": "SN001",
  "nc_description": "Module failed thermal cycling test",
  "root_cause": "Solder joint failure detected",
  "corrective_action": "Improve soldering process temperature control"
}
```

**Response** (201 Created):
```json
{
  "nc_report_id": "NC-2025-0089",
  "status": "CREATED",
  "created_at": "2025-11-13T13:00:00Z",
  "qms_url": "https://qms.company.com/nc/NC-2025-0089"
}
```

### Update PM System

```http
POST /api/v1/integrations/pm/update
Content-Type: application/json
Authorization: Bearer {token}

{
  "project_id": "PROJ-2025-001",
  "sr_id": 123,
  "update_type": "task_complete",
  "task_id": "TASK-456",
  "actual_hours": 8.5
}
```

**Response** (200 OK):
```json
{
  "sync_status": "SUCCESS",
  "pm_task_url": "https://pm.company.com/projects/PROJ-2025-001/tasks/TASK-456"
}
```

## Users & Permissions API

### List Users

```http
GET /api/v1/users?role=engineer&page=1&limit=20
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "total": 45,
  "users": [
    {
      "id": 42,
      "username": "john.smith",
      "email": "john.smith@company.com",
      "full_name": "John Smith",
      "role": "engineer",
      "active": true,
      "created_at": "2024-01-15T08:00:00Z"
    }
  ]
}
```

### Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": 42,
  "username": "john.smith",
  "email": "john.smith@company.com",
  "full_name": "John Smith",
  "role": "engineer",
  "permissions": [
    "execute_protocols",
    "view_reports",
    "create_service_requests"
  ],
  "active": true
}
```

## Webhooks

Subscribe to events for real-time notifications.

### Configure Webhook

```http
POST /api/v1/webhooks
Content-Type: application/json
Authorization: Bearer {token}

{
  "url": "https://your-system.com/webhook/endpoint",
  "events": [
    "service_request.created",
    "protocol.completed",
    "report.generated"
  ],
  "secret": "your_webhook_secret"
}
```

**Response** (201 Created):
```json
{
  "webhook_id": 789,
  "url": "https://your-system.com/webhook/endpoint",
  "events": ["service_request.created", "protocol.completed", "report.generated"],
  "active": true,
  "created_at": "2025-11-13T14:00:00Z"
}
```

### Webhook Event Example

When an event occurs, a POST request is sent to your webhook URL:

```json
{
  "event": "protocol.completed",
  "timestamp": "2025-11-13T15:30:00Z",
  "data": {
    "execution_id": 5678,
    "protocol_id": "PVTP-001",
    "sr_id": 123,
    "status": "COMPLETE",
    "qc_status": "PASS"
  },
  "signature": "sha256=abc123..."
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "module.power_rating",
        "message": "Must be a positive number"
      }
    ],
    "request_id": "req_abc123xyz"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Request accepted for processing |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `TOKEN_EXPIRED` | JWT token has expired |
| `VALIDATION_ERROR` | Input validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `EQUIPMENT_UNAVAILABLE` | Required equipment not available |
| `PROTOCOL_EXECUTION_FAILED` | Protocol execution error |

## Rate Limiting

API requests are rate-limited to ensure system stability.

**Limits**:
- **Free tier**: 100 requests/hour
- **Standard tier**: 1,000 requests/hour
- **Enterprise tier**: 10,000 requests/hour

**Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1699889123
```

When rate limit is exceeded:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after 2025-11-13T16:00:00Z",
    "retry_after": 3600
  }
}
```

## Python Client Example

```python
import requests

class PVTestingClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self._authenticate(username, password)

    def _authenticate(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        return response.json()["access_token"]

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_service_request(self, data):
        response = requests.post(
            f"{self.base_url}/service-requests",
            json=data,
            headers=self._headers()
        )
        return response.json()

    def execute_protocol(self, protocol_id, params):
        response = requests.post(
            f"{self.base_url}/protocols/{protocol_id}/execute",
            json=params,
            headers=self._headers()
        )
        return response.json()

    def get_execution_status(self, execution_id):
        response = requests.get(
            f"{self.base_url}/executions/{execution_id}",
            headers=self._headers()
        )
        return response.json()

# Usage
client = PVTestingClient(
    base_url="https://api.test-protocols.io/api/v1",
    username="user@example.com",
    password="password"
)

# Create service request
sr = client.create_service_request({
    "customer": {"name": "Solar Corp"},
    "module": {"model": "ASM-400M", "quantity": 10},
    "testing": {"standards": ["IEC 61215"]}
})

print(f"Created SR: {sr['sr_number']}")
```

---

**API Version**: 1.0.0
**Last Updated**: 2025-11-12
**OpenAPI Spec**: Available at `/api/v1/openapi.json`
