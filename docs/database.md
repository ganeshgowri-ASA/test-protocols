# Database Schema Documentation

## Overview

The Test Protocols Framework uses a relational database to store protocol definitions, test runs, measurements, results, and QC data. The schema is designed to support multiple protocols, concurrent test execution, and comprehensive data analysis.

## Supported Databases

- **SQLite** (development and testing)
- **PostgreSQL** (production recommended)

## Schema Diagram

```
protocols
    ↓
test_runs ← measurements
    ↓
results
    ↓
qa_flags
    ↓
reports
```

## Tables

### protocols

Stores protocol definitions and configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| protocol_id | VARCHAR(50) | UNIQUE, NOT NULL | Protocol identifier (e.g., TRACK-001) |
| name | VARCHAR(255) | NOT NULL | Protocol name |
| version | VARCHAR(20) | NOT NULL | Version number |
| category | VARCHAR(50) | NOT NULL | Protocol category |
| description | TEXT | | Protocol description |
| config | JSON | NOT NULL | Full protocol configuration |
| created_at | TIMESTAMP | DEFAULT NOW | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update timestamp |
| created_by | VARCHAR(100) | | Creator username |
| status | VARCHAR(20) | DEFAULT 'active' | Protocol status |

**Constraints**:
- UNIQUE (protocol_id, version)

**Indexes**:
- idx_protocols_status ON status

### test_runs

Stores individual test execution records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| run_id | VARCHAR(100) | UNIQUE, NOT NULL | Unique run identifier |
| protocol_id | VARCHAR(50) | FOREIGN KEY | Protocol used |
| protocol_version | VARCHAR(20) | | Protocol version |
| status | VARCHAR(20) | DEFAULT 'pending' | Run status |
| start_time | TIMESTAMP | | Test start time |
| end_time | TIMESTAMP | | Test end time |
| duration_seconds | INTEGER | | Test duration |
| operator | VARCHAR(100) | | Operator name |
| sample_id | VARCHAR(100) | | Sample/device ID |
| device_id | VARCHAR(100) | | Test device ID |
| location | VARCHAR(100) | | Test location |
| environmental_conditions | JSON | | Environmental data |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP | DEFAULT NOW | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW | Update timestamp |

**Status Values**:
- `pending`: Created but not started
- `running`: Currently executing
- `completed`: Successfully completed
- `failed`: Failed with errors
- `cancelled`: Manually cancelled

**Indexes**:
- idx_test_runs_status ON status
- idx_test_runs_protocol ON protocol_id

### measurements

Stores raw measurement data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| run_id | VARCHAR(100) | FOREIGN KEY, NOT NULL | Test run ID |
| timestamp | TIMESTAMP | NOT NULL | Measurement timestamp |
| metric_name | VARCHAR(100) | NOT NULL | Metric identifier |
| metric_value | REAL | NOT NULL | Measured value |
| metric_unit | VARCHAR(20) | | Unit of measurement |
| quality_flag | VARCHAR(20) | DEFAULT 'good' | Quality indicator |
| sensor_id | VARCHAR(50) | | Sensor identifier |
| metadata | JSON | | Additional metadata |
| created_at | TIMESTAMP | DEFAULT NOW | Creation timestamp |

**Quality Flags**:
- `good`: Valid measurement
- `questionable`: Possible issue
- `bad`: Invalid measurement

**Indexes**:
- idx_run_metric ON (run_id, metric_name)
- idx_timestamp ON timestamp

### results

Stores analyzed results and calculated values.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| run_id | VARCHAR(100) | FOREIGN KEY, NOT NULL | Test run ID |
| result_type | VARCHAR(50) | NOT NULL | Type of result |
| metric_name | VARCHAR(100) | | Associated metric |
| calculated_value | REAL | | Calculated value |
| unit | VARCHAR(20) | | Unit of value |
| pass_fail | VARCHAR(10) | | Pass/fail status |
| threshold | REAL | | Acceptance threshold |
| deviation | REAL | | Deviation from threshold |
| calculation_method | VARCHAR(100) | | Method used |
| result_data | JSON | | Additional result data |
| created_at | TIMESTAMP | DEFAULT NOW | Creation timestamp |

**Result Types**:
- `statistical`: Statistical analysis
- `validation`: Validation rule check
- `qc`: Quality control check
- `performance_index`: Performance metric

**Indexes**:
- idx_run_result ON (run_id, result_type)

### qa_flags

Stores quality assurance flags and anomalies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| run_id | VARCHAR(100) | FOREIGN KEY, NOT NULL | Test run ID |
| measurement_id | INTEGER | FOREIGN KEY | Associated measurement |
| flag_type | VARCHAR(50) | NOT NULL | Type of flag |
| severity | VARCHAR(20) | NOT NULL | Severity level |
| description | TEXT | | Flag description |
| flagged_at | TIMESTAMP | DEFAULT NOW | When flagged |
| flagged_by | VARCHAR(100) | | Who flagged |
| resolved | BOOLEAN | DEFAULT FALSE | Resolution status |
| resolved_at | TIMESTAMP | | When resolved |
| resolved_by | VARCHAR(100) | | Who resolved |
| resolution_notes | TEXT | | Resolution notes |

**Flag Types**:
- `data_gap`: Missing data
- `outlier`: Statistical outlier
- `out_of_range`: Value out of acceptable range
- `anomaly`: Unexpected behavior
- `validation_failure`: Failed validation rule

**Severity Levels**:
- `info`: Informational only
- `warning`: Minor issue
- `major`: Significant issue
- `critical`: Critical issue

**Indexes**:
- idx_run_flags ON run_id
- idx_qa_flags_unresolved ON resolved WHERE resolved = FALSE

### reports

Stores generated report metadata and references.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| report_id | VARCHAR(100) | UNIQUE, NOT NULL | Report identifier |
| run_id | VARCHAR(100) | FOREIGN KEY, NOT NULL | Test run ID |
| report_type | VARCHAR(50) | NOT NULL | Type of report |
| format | VARCHAR(20) | NOT NULL | Report format |
| file_path | VARCHAR(500) | | Path to report file |
| generated_at | TIMESTAMP | DEFAULT NOW | Generation timestamp |
| generated_by | VARCHAR(100) | | Generator |
| report_data | JSON | | Report metadata |

**Report Types**:
- `comprehensive`: Full detailed report
- `summary`: Executive summary
- `charts`: Visualization package
- `compliance`: Compliance certificate

**Formats**:
- `html`: HTML document
- `pdf`: PDF document
- `json`: JSON data
- `csv`: CSV data export

### audit_log

Tracks all system activities for compliance and debugging.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| timestamp | TIMESTAMP | DEFAULT NOW | Activity timestamp |
| user | VARCHAR(100) | | User identifier |
| action | VARCHAR(100) | NOT NULL | Action performed |
| entity_type | VARCHAR(50) | | Entity affected |
| entity_id | VARCHAR(100) | | Entity identifier |
| details | JSON | | Action details |
| ip_address | VARCHAR(45) | | Client IP address |

## Views

### v_active_protocols

Lists all active protocols.

```sql
CREATE VIEW v_active_protocols AS
SELECT
    protocol_id,
    name,
    version,
    category,
    description,
    created_at,
    updated_at
FROM protocols
WHERE status = 'active'
ORDER BY protocol_id, version DESC;
```

### v_test_run_summary

Provides comprehensive test run summaries.

```sql
CREATE VIEW v_test_run_summary AS
SELECT
    tr.run_id,
    tr.protocol_id,
    p.name AS protocol_name,
    tr.status,
    tr.start_time,
    tr.end_time,
    tr.duration_seconds,
    tr.operator,
    tr.sample_id,
    COUNT(DISTINCT m.id) AS measurement_count,
    COUNT(DISTINCT CASE WHEN qf.resolved = FALSE THEN qf.id END) AS open_flags,
    COUNT(DISTINCT r.id) AS result_count
FROM test_runs tr
LEFT JOIN protocols p ON tr.protocol_id = p.protocol_id
LEFT JOIN measurements m ON tr.run_id = m.run_id
LEFT JOIN qa_flags qf ON tr.run_id = qf.run_id
LEFT JOIN results r ON tr.run_id = r.run_id
GROUP BY tr.run_id, tr.protocol_id, p.name, tr.status,
         tr.start_time, tr.end_time, tr.duration_seconds,
         tr.operator, tr.sample_id;
```

## Common Queries

### Get Test Run with Results

```sql
SELECT
    tr.*,
    COUNT(m.id) as measurement_count,
    COUNT(r.id) as result_count,
    COUNT(CASE WHEN qf.resolved = FALSE THEN 1 END) as open_flags
FROM test_runs tr
LEFT JOIN measurements m ON tr.run_id = m.run_id
LEFT JOIN results r ON tr.run_id = r.run_id
LEFT JOIN qa_flags qf ON tr.run_id = qf.run_id
WHERE tr.run_id = ?
GROUP BY tr.id;
```

### Get Measurements for Metric

```sql
SELECT
    timestamp,
    metric_value,
    quality_flag
FROM measurements
WHERE run_id = ?
  AND metric_name = ?
ORDER BY timestamp;
```

### Get Validation Results

```sql
SELECT
    result_type,
    metric_name,
    calculated_value,
    pass_fail,
    threshold
FROM results
WHERE run_id = ?
  AND result_type = 'validation'
ORDER BY metric_name;
```

## Maintenance

### Vacuum and Analyze (PostgreSQL)

```sql
VACUUM ANALYZE measurements;
VACUUM ANALYZE results;
```

### Archive Old Data

```sql
-- Archive test runs older than 1 year
INSERT INTO archive.test_runs
SELECT * FROM test_runs
WHERE start_time < NOW() - INTERVAL '1 year';

DELETE FROM test_runs
WHERE start_time < NOW() - INTERVAL '1 year';
```

### Rebuild Indexes

```sql
REINDEX TABLE measurements;
REINDEX TABLE results;
```

## Backup and Recovery

### Backup (SQLite)

```bash
sqlite3 test_protocols.db ".backup test_protocols_backup.db"
```

### Backup (PostgreSQL)

```bash
pg_dump -Fc test_protocols > test_protocols_backup.dump
```

### Restore (PostgreSQL)

```bash
pg_restore -d test_protocols test_protocols_backup.dump
```

## Migration

Schema migrations should be managed using a migration tool. Version history is tracked in the `schema_migrations` table (not shown but recommended to add).

## Performance Tuning

### Recommended Indexes

All critical indexes are defined in the schema. Additional indexes may be added based on query patterns.

### Connection Pooling

For production deployments:
- Pool size: 20-40 connections
- Max overflow: 40
- Pool timeout: 30 seconds

### Query Optimization

- Use prepared statements
- Batch insert operations
- Use transactions appropriately
- Limit result sets

## Security

### Access Control

Implement role-based access control:
- `admin`: Full access
- `engineer`: Read/write test data
- `operator`: Execute tests only
- `viewer`: Read-only access

### Data Encryption

- Enable encryption at rest
- Use SSL/TLS for connections
- Encrypt sensitive fields (if any)

## Monitoring

Key metrics to monitor:
- Connection pool usage
- Query performance
- Database size growth
- Slow query log
- Lock contention
