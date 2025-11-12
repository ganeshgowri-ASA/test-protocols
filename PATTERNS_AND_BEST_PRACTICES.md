# PV Testing Protocol Framework - Patterns and Best Practices

## Overview
This document describes the common patterns and best practices for creating and maintaining protocols in the PV Testing Protocol Framework.

## 1. Directory Structure Patterns

### Organization by Test Type
```
protocols/
├── environmental/          # Environmental stress tests
│   ├── temperature-humidity-cycling.json
│   ├── salt-fog-corrosion.json
│   ├── uv-exposure.json
│   └── thermal-stress.json
├── electrical/            # Electrical performance tests
│   ├── iv-curve-measurement.json
│   └── insulation-resistance.json
├── mechanical/            # Mechanical stress tests
│   └── wind-load.json
└── templates/             # Reusable base templates
    ├── base-protocol-template.json
    ├── environmental-template.json
    └── electrical-template.json
```

### Protocol Naming Convention
- Format: `{test-type}-protocol.json`
- Examples:
  - `temperature-humidity-cycling-protocol.json`
  - `salt-fog-corrosion-protocol.json`
  - `uv-exposure-protocol.json`

### Configuration Structure
```
configs/
├── test-chambers.json              # All available chambers and their specs
├── data-loggers.json               # Logger configurations
├── analysis-templates.json         # Reusable analysis specs
└── integration/
    ├── lims-integration.json       # LIMS configuration
    ├── qms-integration.json        # QMS configuration
    └── pms-integration.json        # Project Management config
```

## 2. JSON Structure Patterns

### Pattern 1: Hierarchical Metadata
Every protocol contains complete metadata for identification and version control:

```json
{
  "metadata": {
    "protocol_id": "THC-2024-001",          // Unique ID: {TYPE}-{YEAR}-{SEQ}
    "name": "Temperature-Humidity Cycling Test",
    "version": "1.0.0",                     // Semantic versioning
    "created_date": "2024-11-12",           // ISO8601 format
    "created_by": "Engineering Team",
    "last_modified": "2024-11-12",
    "description": "Long description",
    "compliance_standards": [
      {
        "standard": "IEC 61215",
        "section": "10.2.1",
        "requirement": "Thermal Cycling"
      }
    ]
  }
}
```

**Key Patterns:**
- Protocol ID uses format: `{TYPE}-{YEAR}-{SEQUENCE}`
- Types: `THC` (Temperature-Humidity), `SFCORR` (Salt Fog Corrosion), `UV`, etc.
- Compliance standards always include standard code, section, and requirement
- Dates are ISO8601 format (YYYY-MM-DD)

### Pattern 2: Modular Test Sequence
Test sequences are defined as ordered arrays with support for nested steps and repetition:

```json
{
  "test_sequence": [
    {
      "step_id": 1,
      "name": "Initial Conditioning",
      "duration_minutes": 120,
      "conditions": {
        "temperature_celsius": 23,
        "humidity_rh_percent": 50
      },
      "logging_interval_seconds": 300,
      "qc_checks": [ /* ... */ ]
    },
    {
      "step_id": 2,
      "name": "Thermal Cycling Loop",
      "repeat_count": 200,           // Repeat entire sub-sequence
      "sub_steps": [
        {
          "sub_step_id": "2a",
          "name": "Heat Phase",
          "duration_minutes": 60,
          "conditions": { /* ... */ }
        },
        {
          "sub_step_id": "2b",
          "name": "Cool Phase",
          "duration_minutes": 60,
          "conditions": { /* ... */ }
        }
      ]
    }
  ]
}
```

**Key Patterns:**
- Use numeric step_id (1, 2, 3...) for main steps
- Use hierarchical sub_step_id (2a, 2b, 2c) for nested steps
- Duration can be specified in minutes or hours
- Conditions are parameter-specific objects
- Logging intervals are in seconds

### Pattern 3: Data Logging Specification
Data logging defines comprehensive time-series collection with quality checks:

```json
{
  "data_logging": {
    "parameters": [
      {
        "parameter_id": "temp_internal",
        "parameter_name": "Chamber Internal Temperature",
        "source": "chamber_sensor_1",           // Which device measures this
        "unit": "Celsius",                       // Always specify units
        "data_type": "float",                    // float, integer, string, boolean
        "sampling_interval_seconds": 60,         // Measurement frequency
        "aggregation_methods": [
          {
            "method": "raw",
            "description": "Individual measurements"
          },
          {
            "method": "mean",
            "window_minutes": 10                 // Sliding window
          },
          {
            "method": "min_max",
            "window_minutes": 10
          }
        ],
        "quality_checks": [
          {
            "check": "range_validation",
            "valid_range": [-50, 100]            // Physically valid range
          },
          {
            "check": "rate_of_change",
            "max_change_per_minute": 20          // Detect sensor failures
          }
        ]
      }
    ],
    "storage": {
      "format": "CSV with ISO8601 timestamps",
      "location": "/data/test_results/{protocol_id}/{test_run_id}/raw_data.csv",
      "retention_years": 5,
      "backup": "Daily to archive storage"
    }
  }
}
```

**Key Patterns:**
- Every parameter has ID, name, unit, and data type
- Sampling intervals are in seconds
- Aggregation methods enable multi-scale analysis
- Quality checks detect sensor failures and data anomalies
- Storage paths use template variables: {protocol_id}, {test_run_id}

### Pattern 4: Chamber Integration Specification
Chambers are fully specified with sensors, safety interlocks, and requirements:

```json
{
  "test_chamber_integration": {
    "chamber_type": "Temperature-Humidity Cycling Chamber",
    "chamber_id": "THC-001",
    "chamber_model": "Cincinnati Sub-Zero Tenney",
    "specifications": {
      "temperature_range": {
        "min_celsius": -40,
        "max_celsius": 85,
        "ramp_rate_celsius_per_minute": 15,
        "stability_celsius": 2
      },
      "humidity_range": {
        "min_rh_percent": 10,
        "max_rh_percent": 95,
        "stability_rh_percent": 3
      }
    },
    "sensors": {
      "temperature": {
        "sensor_id": "TEMP-001",
        "type": "PT100 RTD",
        "accuracy_celsius": 0.5,
        "calibration_due": "2025-05-12",
        "calibration_status": "valid"
      }
    },
    "safety_interlocks": [
      {
        "name": "Temperature overshoot protection",
        "trigger": "Temperature exceeds max by 5°C",
        "action": "Emergency stop"
      }
    ],
    "pre_test_requirements": [
      "Chamber humidity must be between 50-70%",
      "All sensors must pass calibration check"
    ]
  }
}
```

**Key Patterns:**
- Chamber ID format: `{ABBREV}-{SEQUENCE}` (e.g., THC-001, SFOG-001)
- All sensor ranges have both nominal and tolerance specifications
- Calibration status must be tracked
- Safety interlocks are explicit and documented
- Pre-test requirements are checkable items

### Pattern 5: Quality Control Framework
QC checks are organized by test phase:

```json
{
  "quality_control": {
    "pre_test_checks": [
      {
        "check_id": "QC-Pre-1",
        "description": "Verify chamber calibration is current",
        "requirement": "Calibration not older than 12 months",
        "pass_fail": true                   // Binary pass/fail
      }
    ],
    "in_test_checks": [
      {
        "check_id": "QC-In-1",
        "description": "Temperature ramp rate compliance",
        "parameter": "temperature_ramp_rate",
        "min": 14,
        "max": 16,
        "unit": "°C/min",
        "check_frequency_hours": 1
      }
    ],
    "post_test_checks": [
      {
        "check_id": "QC-Post-1",
        "description": "Visual inspection",
        "pass_criteria": "No cracks, delamination"
      }
    ]
  }
}
```

**Key Patterns:**
- Check IDs follow format: `QC-{PHASE}-{SEQUENCE}` (QC-Pre-1, QC-In-1, etc.)
- Pre-test checks are boolean pass/fail
- In-test checks have numeric ranges and check frequencies
- Post-test checks may reference subjective criteria

### Pattern 6: Analysis and Visualization
Analysis specifications are separate from data to support multiple analysis approaches:

```json
{
  "analysis": {
    "charts": [
      {
        "chart_id": "thc_temp_profile",
        "title": "Temperature Profile Over Test Duration",
        "type": "line",
        "x_axis": {
          "parameter": "elapsed_time",
          "unit": "Hours"
        },
        "y_axis": {
          "parameter": "temp_internal",
          "unit": "Celsius"
        },
        "series": [
          {
            "name": "Chamber Temperature",
            "data_source": "temp_internal",
            "color": "red"
          }
        ],
        "reference_lines": [
          {
            "value": 85,
            "label": "Max Spec"
          }
        ]
      }
    ],
    "statistics": [
      {
        "stat_id": "temperature_stats",
        "title": "Temperature Statistics",
        "parameters": ["temp_internal"],
        "calculations": [
          "mean", "std_dev", "min", "max", "range"
        ]
      }
    ]
  }
}
```

**Key Patterns:**
- Chart ID format: `{protocol_abbrev}_{parameter}_{type}` (thc_temp_profile)
- Chart types: line, scatter, histogram, heatmap, bar
- Series data_source references parameter_id from data_logging
- Reference lines show specification limits
- Statistics specify which calculations to perform

### Pattern 7: Traceability and Compliance Mapping
Traceability connects test evidence to compliance standards:

```json
{
  "traceability": {
    "audit_trail": {
      "track_operator": true,
      "track_chamber_id": true,
      "track_sensor_calibration_status": true,
      "timestamp_format": "ISO8601",
      "timezone": "UTC"
    },
    "sample_tracking": {
      "sample_id_format": "PV-{project}-{batch}-{sequence}",
      "identification_requirements": [
        "Sample ID label on module",
        "Barcode for automated tracking",
        "Photographic documentation"
      ]
    },
    "compliance_mapping": [
      {
        "standard": "IEC 61215",
        "requirement": "Thermal Cycling -40°C to 85°C, 200 cycles",
        "test_sequence_step": 2,
        "evidence_location": "raw_data.csv, chamber_logs.log"
      }
    ]
  }
}
```

**Key Patterns:**
- Audit trail explicitly lists what to track
- Sample ID uses template variables
- Compliance mapping connects each requirement to specific test steps
- Evidence locations reference generated data files

## 3. Common Parameters by Test Type

### Temperature Cycling Tests
```json
{
  "temperature_celsius": 23,
  "humidity_rh_percent": 50,
  "ramp_rate_celsius_per_minute": 15,
  "dwell_time_minutes": 30,
  "thermal_stress_cycles": 200
}
```

### Corrosion Tests
```json
{
  "temperature_celsius": 35,
  "humidity_rh_percent": 95,
  "salt_concentration_percent": 5,
  "fog_collection_rate_ml_per_80cm2_per_day": 1.5
}
```

### Electrical Tests
```json
{
  "voltage_v": 600,
  "current_a": 10,
  "temperature_celsius": 25,
  "illumination_w_m2": 1000
}
```

## 4. Time-Series Data Analysis Patterns

### Aggregation Levels
1. **Raw**: Individual measurements (highest frequency)
2. **Summarized**: Statistical aggregates (mean, min, max, std_dev) over time windows
3. **Metrics**: Derived metrics (ramp rates, compliance percentages, degradation rates)

### Typical Time Windows
- Sensors: 30-60 seconds (real-time monitoring)
- Aggregation: 10-60 minutes (trend analysis)
- Summaries: Daily (compliance reporting)

### Quality Metrics
- **Specification Compliance**: % time within spec
- **Stability**: Standard deviation during hold phases
- **Ramp Rate Accuracy**: Measured vs. specified rate
- **Data Completeness**: % valid measurements vs. total expected

## 5. Integration Patterns

### LIMS Integration Fields
```json
{
  "lims_integration": {
    "fields_to_export": [
      "protocol_id",
      "test_run_id",
      "sample_ids",
      "test_start_date",
      "test_end_date",
      "chamber_id",
      "pass_fail_status"
    ]
  }
}
```

### QMS Integration Fields
- Document Type: "Test Report"
- Review Chain: Technician → Quality Engineer → Manager
- Retention: As specified in compliance_standards

### Project Management Integration
- Status Updates: test_status, completion_percentage
- Notifications: On test start, completion, failure
- Result Integration: Pass/fail status, key metrics

## 6. Best Practices

### 1. Version Control
- Always increment version when making changes
- Include change summary in commit messages
- Maintain changelog.md for each protocol

### 2. Parameterization
- Use consistent parameter naming across protocols
- Always specify units explicitly
- Include valid ranges and tolerances

### 3. Compliance Mapping
- Map EVERY requirement to specific test steps
- Include evidence locations in your protocol
- Keep standards documentation current

### 4. Data Quality
- Define quality checks for every measured parameter
- Include range validation and rate-of-change checks
- Document acceptable data gap tolerances

### 5. Documentation
- Include clear descriptions for all non-obvious parameters
- Provide examples of expected values
- Document any specialized procedures or preparations

### 6. Reusability
- Create base templates for common test types
- Use references to avoid duplication
- Parameterize chamber and sensor configurations

### 7. Safety
- Always include safety interlocks
- Document all emergency stop conditions
- Include operator alert specifications

### 8. Traceability
- Track all relevant metadata (operator, chamber, date)
- Use ISO8601 timestamps throughout
- Map sample IDs to batch information

## 7. Protocol Creation Workflow

### Step 1: Start with Template
1. Choose appropriate base template (environmental, electrical, mechanical)
2. Copy and rename with your protocol_id
3. Update metadata section

### Step 2: Define Objectives and Scope
1. Specify primary and secondary objectives
2. List success criteria
3. Map to compliance standards

### Step 3: Specify Chamber and Sensors
1. Identify required chamber
2. List all needed sensors
3. Define calibration requirements

### Step 4: Design Test Sequence
1. Break test into logical steps
2. Specify conditions, durations, and logging intervals
3. Add QC checks for each step

### Step 5: Define Data Logging
1. List all parameters to measure
2. Specify sampling intervals
3. Define aggregation methods
4. Add quality checks

### Step 6: Plan Analysis
1. Define required charts
2. Specify statistics to calculate
3. Create compliance mapping

### Step 7: Review and Validate
1. Validate JSON against schema
2. Peer review for completeness
3. Verify compliance mappings
4. Test with dry-run if possible

## 8. Common Pitfalls to Avoid

1. **Missing Units**: Always specify units for every numerical parameter
2. **Inconsistent Naming**: Use consistent parameter names across protocols
3. **Unclear QC Criteria**: Make QC pass/fail criteria explicit
4. **Incomplete Compliance Mapping**: Map all requirements, not just major ones
5. **Insufficient Data Logging**: Log enough data to verify compliance
6. **Unclear Chamber Requirements**: Be specific about chamber capabilities needed
7. **Missing Safety Specifications**: Document all safety interlocks
8. **Ambiguous Time Specifications**: Be clear about total test duration
9. **Forgotten Traceability**: Plan audit trail and compliance evidence upfront
10. **No Integration Planning**: Plan system integration (LIMS, QMS) early

## 9. File Organization Best Practices

```
protocols/
├── README.md                              # Directory overview
├── test-type-1/
│   ├── protocol-1.json
│   ├── protocol-2.json
│   └── README.md                         # Type-specific notes
├── templates/
│   ├── base-protocol-template.json
│   └── README.md                         # Template usage guide
└── schemas/
    ├── protocol-schema.json
    └── validation-rules.md
```

Each directory should have a README.md explaining:
- Purpose of protocols in that directory
- Common parameters
- Template usage
- Version history

