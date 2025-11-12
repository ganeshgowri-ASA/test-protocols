# Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [LIMS Integration](#lims-integration)
3. [QMS Integration](#qms-integration)
4. [Project Management Integration](#project-management-integration)
5. [ERP Integration](#erp-integration)
6. [Custom Integrations](#custom-integrations)
7. [Security & Authentication](#security--authentication)
8. [Data Mapping](#data-mapping)
9. [Troubleshooting](#troubleshooting)

## Overview

The PV Testing Protocol Framework supports integration with Laboratory Information Management Systems (LIMS), Quality Management Systems (QMS), Project Management (PM) systems, and ERP systems through RESTful APIs, webhooks, and data synchronization services.

### Integration Architecture

```
┌──────────────────────────────────────────────────┐
│         PV Testing Protocol Framework            │
│                                                   │
│  ┌─────────────────────────────────────────┐   │
│  │       Integration Layer                  │   │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌────┐ │   │
│  │  │ LIMS │  │ QMS  │  │  PM  │  │ERP │ │   │
│  │  │Client│  │Client│  │Client│  │API │ │   │
│  │  └───┬──┘  └───┬──┘  └───┬──┘  └─┬──┘ │   │
│  └──────┼─────────┼─────────┼────────┼────┘   │
└─────────┼─────────┼─────────┼────────┼────────┘
          │         │         │        │
     ─────┴─────────┴─────────┴────────┴────
          │         │         │        │
     ┌────▼──┐  ┌───▼──┐  ┌──▼───┐  ┌▼────┐
     │ LIMS  │  │ QMS  │  │  PM  │  │ ERP │
     │System │  │System│  │System│  │Sys  │
     └───────┘  └──────┘  └──────┘  └─────┘
```

### Supported Integration Methods

1. **REST API** - Bidirectional data exchange
2. **Webhooks** - Real-time event notifications
3. **File Export/Import** - CSV, Excel, XML, JSON
4. **Database Direct** - SQL connector (optional)
5. **SOAP** - Legacy system support

## LIMS Integration

### Overview

Integrate with Laboratory Information Management Systems for sample tracking, test results management, and certificate generation.

### Configuration

```python
# config/integrations.yaml
lims:
  enabled: true
  provider: "LabWare"  # or "StarLIMS", "LabVantage", "Custom"
  base_url: "https://lims.company.com/api/v2"
  auth_type: "api_key"  # or "oauth2", "basic"
  api_key: "${LIMS_API_KEY}"
  sync_interval: 300  # seconds
  bidirectional: true
  mappings:
    sample_id_field: "LabSampleID"
    status_field: "TestStatus"
```

### Sample Creation Workflow

```python
from pv_testing.integrations import LIMSClient

# Initialize LIMS client
lims = LIMSClient(
    base_url="https://lims.company.com/api/v2",
    api_key="YOUR_API_KEY"
)

# Create sample in LIMS when SR is created
def on_service_request_created(sr):
    for module in sr.modules:
        lims_sample = lims.create_sample(
            external_id=module.serial_number,
            sample_type="PV Module",
            project_id=sr.sr_number,
            customer=sr.customer.name,
            metadata={
                "manufacturer": module.manufacturer,
                "model": module.model,
                "power_rating": module.power_rating
            }
        )

        # Store LIMS sample ID for future reference
        module.lims_sample_id = lims_sample["id"]
        module.save()
```

### Results Upload

```python
# Upload test results to LIMS
def sync_results_to_lims(execution):
    lims_sample_id = execution.module.lims_sample_id

    # Prepare results data
    results_data = {
        "test_id": execution.protocol_id,
        "test_name": execution.protocol.name,
        "test_date": execution.completed_at.isoformat(),
        "operator": execution.operator.name,
        "results": []
    }

    # Map measurements to LIMS format
    for measurement in execution.results["measurements"]:
        results_data["results"].append({
            "analyte": measurement["parameter"],
            "value": measurement["value"],
            "unit": measurement["unit"],
            "uncertainty": measurement.get("uncertainty"),
            "status": measurement.get("qc_status", "PASS")
        })

    # Upload to LIMS
    response = lims.upload_results(
        sample_id=lims_sample_id,
        results=results_data
    )

    return response
```

### Status Synchronization

```python
# Bidirectional status sync
class LIMSSync:
    def __init__(self):
        self.lims = LIMSClient()

    def sync_status_to_lims(self, sr):
        """Update LIMS when SR status changes"""
        status_mapping = {
            "TESTING_IN_PROGRESS": "In Testing",
            "TESTING_COMPLETE": "Testing Complete",
            "REPORTS_APPROVED": "Approved"
        }

        lims_status = status_mapping.get(sr.status)
        if lims_status:
            self.lims.update_sample_status(
                sample_id=sr.lims_sample_id,
                status=lims_status,
                notes=f"Updated from PV Testing Framework"
            )

    def sync_status_from_lims(self):
        """Poll LIMS for status updates"""
        pending_samples = self.lims.get_samples_by_status("Pending Receipt")

        for lims_sample in pending_samples:
            # Find corresponding SR
            sr = ServiceRequest.find_by_lims_id(lims_sample["id"])
            if sr and lims_sample["status"] == "Received":
                sr.update_status("PENDING_INSPECTION")
```

## QMS Integration

### Overview

Integrate with Quality Management Systems for non-conformance reporting, CAPA tracking, and audit trail management.

### Non-Conformance (NC) Reporting

```python
from pv_testing.integrations import QMSClient

qms = QMSClient(
    base_url="https://qms.company.com/api",
    username="integration_user",
    password="${QMS_PASSWORD}"
)

# Automatic NC creation on test failure
def handle_test_failure(execution):
    if execution.qc_status == "FAIL":
        nc_report = qms.create_nc_report(
            title=f"Module Failed {execution.protocol.name}",
            description=generate_nc_description(execution),
            severity="Major" if is_critical_test(execution) else "Minor",
            source="Testing",
            detection_date=execution.completed_at,
            related_documents=[
                execution.sr.sr_number,
                f"Protocol: {execution.protocol_id}"
            ],
            affected_items=[
                {
                    "type": "Module",
                    "id": execution.module.serial_number,
                    "quantity": 1
                }
            ],
            root_cause_analysis={
                "immediate_cause": extract_failure_mode(execution),
                "contributing_factors": analyze_conditions(execution)
            },
            proposed_corrective_action": generate_ca_recommendations(execution)
        )

        # Link NC report to execution
        execution.qms_nc_id = nc_report["nc_id"]
        execution.save()

        return nc_report
```

### CAPA Integration

```python
# Create CAPA from recurring failures
def analyze_recurring_failures():
    # Find patterns of failures
    failures = Execution.objects.filter(
        qc_status="FAIL",
        protocol_id="PVTP-018"  # Thermal cycling
    ).last_n_days(30)

    if len(failures) > 5:  # Threshold for CAPA
        capa = qms.create_capa(
            title="Recurring Thermal Cycling Failures",
            problem_statement=f"{len(failures)} modules failed thermal cycling in last 30 days",
            root_cause="Solder joint quality issues identified",
            corrective_action={
                "description": "Improve soldering process control",
                "responsible": "Process Engineering",
                "target_date": "2025-12-31"
            },
            preventive_action={
                "description": "Implement statistical process control for soldering",
                "responsible": "Quality Engineering",
                "target_date": "2026-01-31"
            },
            effectiveness_criteria="< 1 failure per month for 6 months"
        )
```

### Audit Trail Sync

```python
# Sync audit events to QMS
class AuditTrailSync:
    def __init__(self):
        self.qms = QMSClient()

    def sync_audit_event(self, event):
        """Send audit events to QMS"""
        qms_event = {
            "timestamp": event.timestamp.isoformat(),
            "user": event.user.username,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "changes": event.changes,
            "ip_address": event.ip_address,
            "session_id": event.session_id
        }

        self.qms.log_audit_event(qms_event)
```

## Project Management Integration

### Overview

Integrate with PM systems (Jira, Asana, Microsoft Project, etc.) for task management, resource allocation, and project tracking.

### Task Synchronization

```python
from pv_testing.integrations import PMClient

pm = PMClient(
    base_url="https://pm.company.com/api",
    api_token="${PM_API_TOKEN}"
)

# Create PM tasks when SR is created
def create_pm_tasks(sr):
    # Create main project task
    project_task = pm.create_task(
        project_id=sr.pm_project_id,
        title=f"PV Testing - {sr.sr_number}",
        description=f"Testing for {sr.customer.name}",
        start_date=sr.created_at,
        due_date=sr.requested_delivery_date,
        assignee=sr.assigned_pm.email
    )

    # Create subtasks for each protocol
    for protocol in sr.assigned_protocols:
        subtask = pm.create_subtask(
            parent_task_id=project_task["id"],
            title=f"{protocol.protocol_id}: {protocol.name}",
            estimated_hours=protocol.duration_hours,
            assignee=find_available_operator(protocol)
        )

        # Store PM task ID for tracking
        protocol.pm_task_id = subtask["id"]
        protocol.save()
```

### Status Updates

```python
# Auto-update PM system on execution completion
def on_execution_complete(execution):
    pm.update_task(
        task_id=execution.protocol.pm_task_id,
        status="COMPLETE",
        completion_date=execution.completed_at,
        actual_hours=calculate_actual_hours(execution),
        notes=f"QC Status: {execution.qc_status}"
    )

    # Update project progress
    sr = execution.service_request
    progress = calculate_sr_progress(sr)

    pm.update_project_progress(
        project_id=sr.pm_project_id,
        progress_percent=progress
    )
```

### Resource Tracking

```python
# Track resource utilization
def log_resource_usage(execution):
    pm.log_time_entry(
        task_id=execution.protocol.pm_task_id,
        user=execution.operator.email,
        date=execution.start_time.date(),
        hours=calculate_duration_hours(execution),
        description=f"Executed {execution.protocol.name}"
    )

    # Log equipment usage
    for equipment_id in execution.equipment_used:
        pm.log_resource_usage(
            task_id=execution.protocol.pm_task_id,
            resource_type="Equipment",
            resource_id=equipment_id,
            usage_hours=calculate_duration_hours(execution)
        )
```

## ERP Integration

### Overview

Integration with ERP systems for invoicing, inventory management, and customer relationship management.

### Invoice Generation

```python
from pv_testing.integrations import ERPClient

erp = ERPClient(
    base_url="https://erp.company.com/api",
    client_id="${ERP_CLIENT_ID}",
    client_secret="${ERP_CLIENT_SECRET}"
)

# Generate invoice when testing is complete
def generate_invoice(sr):
    if sr.status == "REPORTS_APPROVED":
        # Calculate charges
        line_items = []
        for protocol in sr.protocols:
            line_items.append({
                "description": f"{protocol.protocol_id}: {protocol.name}",
                "quantity": sr.module.quantity,
                "unit_price": protocol.price_per_module,
                "total": sr.module.quantity * protocol.price_per_module
            })

        # Create invoice in ERP
        invoice = erp.create_invoice(
            customer_id=sr.customer.erp_customer_id,
            invoice_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            reference=sr.sr_number,
            line_items=line_items,
            notes=f"PV Module Testing - {sr.module.model}"
        )

        sr.erp_invoice_id = invoice["invoice_id"]
        sr.save()
```

## Custom Integrations

### Webhook-Based Integration

```python
# Register webhook for custom integration
from pv_testing.webhooks import WebhookManager

webhook_mgr = WebhookManager()

# Register webhook endpoint
webhook_mgr.register(
    url="https://your-system.com/webhook",
    events=[
        "service_request.created",
        "protocol.completed",
        "report.generated"
    ],
    secret="your_webhook_secret"
)

# Webhook payload example
{
    "event": "protocol.completed",
    "timestamp": "2025-11-13T15:30:00Z",
    "data": {
        "execution_id": 5678,
        "protocol_id": "PVTP-001",
        "sr_number": "SR-2025-0123",
        "status": "COMPLETE",
        "qc_status": "PASS",
        "results_url": "https://api.test-protocols.io/api/v1/executions/5678/results"
    },
    "signature": "sha256=abc123..."
}
```

### File-Based Integration

```python
# Export data for file-based integration
from pv_testing.exporters import DataExporter

exporter = DataExporter()

# Export to CSV
exporter.export_csv(
    sr_id=123,
    output_path="/exports/SR-2025-0123_results.csv",
    include_raw_data=True
)

# Export to Excel with multiple sheets
exporter.export_excel(
    sr_id=123,
    output_path="/exports/SR-2025-0123_results.xlsx",
    sheets={
        "Summary": "summary_data",
        "Measurements": "measurement_data",
        "QC Results": "qc_data"
    }
)

# Export to XML for legacy systems
exporter.export_xml(
    sr_id=123,
    output_path="/exports/SR-2025-0123_results.xml",
    schema="lims_v2"
)
```

## Security & Authentication

### API Key Authentication

```python
# Configuration
integrations:
  lims:
    auth_type: "api_key"
    api_key_header: "X-API-Key"
    api_key: "${LIMS_API_KEY}"
```

### OAuth 2.0

```python
# OAuth 2.0 configuration
integrations:
  qms:
    auth_type: "oauth2"
    client_id: "${QMS_CLIENT_ID}"
    client_secret: "${QMS_CLIENT_SECRET}"
    token_url: "https://qms.company.com/oauth/token"
    scopes: ["read:nc", "write:nc", "read:capa"]
```

### Mutual TLS (mTLS)

```python
# mTLS for secure integration
integrations:
  erp:
    auth_type: "mtls"
    client_cert: "/certs/client.crt"
    client_key: "/certs/client.key"
    ca_cert: "/certs/ca.crt"
```

## Data Mapping

### Field Mapping Configuration

```yaml
# config/field_mappings.yaml
lims_mapping:
  service_request:
    sr_number: "ProjectID"
    customer_name: "ClientName"
    module_model: "ProductCode"

  measurements:
    Pmax: "MaxPower_W"
    Voc: "OpenCircuitVoltage_V"
    Isc: "ShortCircuitCurrent_A"
    Fill_Factor: "FillFactor_Percent"
```

### Custom Transformations

```python
# Custom data transformations
class DataTransformer:
    @staticmethod
    def transform_for_lims(internal_data):
        """Transform internal data format to LIMS format"""
        return {
            "LabSampleID": internal_data["module"]["serial_number"],
            "TestMethod": internal_data["protocol"]["standard"],
            "Results": [
                {
                    "Analyte": key,
                    "Value": value["value"],
                    "Units": value["unit"],
                    "Status": "Pass" if value.get("qc_status") == "PASS" else "Fail"
                }
                for key, value in internal_data["measurements"].items()
            ]
        }
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   ```python
   # Debug authentication
   try:
       client.authenticate()
   except AuthenticationError as e:
       logger.error(f"Auth failed: {e}")
       # Check credentials, token expiry, network connectivity
   ```

2. **Data Sync Errors**
   ```python
   # Implement retry logic
   @retry(max_attempts=3, backoff=2)
   def sync_with_retry(data):
       try:
           return lims.upload_results(data)
       except NetworkError:
           logger.warning("Network error, retrying...")
           raise
   ```

3. **Field Mapping Issues**
   ```python
   # Validate field mappings
   def validate_mapping(data, mapping):
       for internal_field, external_field in mapping.items():
           if internal_field not in data:
               raise MappingError(f"Missing field: {internal_field}")
   ```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-12
