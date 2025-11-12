# Quick Protocol Creation Guide

## 5-Minute Overview

A PV testing protocol is a JSON file that specifies:
1. **What** to test (metadata & objectives)
2. **Where** to test it (chamber specs)
3. **How** to test it (test sequence)
4. **What** to measure (data logging)
5. **How** to evaluate quality (QC checks)
6. **How** to prove compliance (traceability)

## Protocol Creation Steps

### Step 1: Create Basic Structure
```bash
cp templates/base-protocol-template.json protocols/{test_type}/{protocol_id}.json
```

Update metadata:
```json
{
  "metadata": {
    "protocol_id": "XXX-2024-001",        // Your protocol ID
    "name": "Your Test Name",
    "version": "1.0.0",
    "created_date": "2024-11-12",
    "created_by": "Your Name",
    "description": "Brief description"
  }
}
```

### Step 2: Define Objectives
```json
{
  "objectives": {
    "primary": "What are you trying to test?",
    "secondary": [
      "Additional goals",
      "What should be detected?"
    ],
    "success_criteria": {
      "criterion_1": "Quantitative goal (e.g., <5% power loss)",
      "criterion_2": "Visual inspection (e.g., No cracks)"
    }
  }
}
```

### Step 3: Specify Chamber Requirements
```json
{
  "test_chamber_integration": {
    "chamber_type": "Temperature-Humidity Cycling Chamber",
    "chamber_id": "THC-001",
    "specifications": {
      "temperature_range": {
        "min_celsius": -40,
        "max_celsius": 85,
        "ramp_rate_celsius_per_minute": 15,
        "stability_celsius": 2
      }
    },
    "sensors": {
      "temperature": {
        "sensor_id": "TEMP-001",
        "type": "PT100 RTD",
        "accuracy_celsius": 0.5,
        "calibration_status": "valid"
      }
    },
    "pre_test_requirements": [
      "List items that must be checked before test"
    ]
  }
}
```

### Step 4: Design Test Sequence
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
      "qc_checks": [
        {
          "check_id": "QC-1.1",
          "parameter": "temperature_stability",
          "target": "23±2°C",
          "pass_threshold": "Maintain for 30 minutes"
        }
      ]
    },
    {
      "step_id": 2,
      "name": "Main Test",
      "repeat_count": 100,
      "sub_steps": [
        {
          "sub_step_id": "2a",
          "name": "Heat Phase",
          "duration_minutes": 60,
          "conditions": {
            "temperature_celsius": 85,
            "humidity_rh_percent": 50
          }
        },
        {
          "sub_step_id": "2b",
          "name": "Cool Phase",
          "duration_minutes": 60,
          "conditions": {
            "temperature_celsius": -40,
            "humidity_rh_percent": 50
          }
        }
      ]
    }
  ]
}
```

### Step 5: Define Data Logging
```json
{
  "data_logging": {
    "parameters": [
      {
        "parameter_id": "temp_internal",
        "parameter_name": "Chamber Temperature",
        "source": "chamber_sensor_1",
        "unit": "Celsius",
        "data_type": "float",
        "sampling_interval_seconds": 60,
        "aggregation_methods": [
          {"method": "raw"},
          {"method": "mean", "window_minutes": 10},
          {"method": "min_max", "window_minutes": 10}
        ],
        "quality_checks": [
          {"check": "range_validation", "valid_range": [-50, 100]},
          {"check": "rate_of_change", "max_change_per_minute": 20}
        ]
      }
    ],
    "storage": {
      "format": "CSV with ISO8601 timestamps",
      "location": "/data/test_results/{protocol_id}/{test_run_id}/raw_data.csv",
      "retention_years": 5
    }
  }
}
```

### Step 6: Define Quality Control
```json
{
  "quality_control": {
    "pre_test_checks": [
      {
        "check_id": "QC-Pre-1",
        "description": "Verify chamber calibration",
        "requirement": "Calibration not older than 12 months",
        "pass_fail": true
      }
    ],
    "in_test_checks": [
      {
        "check_id": "QC-In-1",
        "description": "Temperature ramp rate",
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
        "requirement": "No cracks or delamination"
      }
    ]
  }
}
```

### Step 7: Set Up Compliance Mapping
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
        "Barcode for tracking",
        "Photos"
      ]
    },
    "compliance_mapping": [
      {
        "standard": "IEC 61215",
        "requirement": "Thermal Cycling: -40 to 85°C, 200 cycles",
        "test_sequence_step": 2,
        "evidence_location": "raw_data.csv"
      }
    ]
  }
}
```

### Step 8: Add Analysis (Optional but Recommended)
```json
{
  "analysis": {
    "charts": [
      {
        "chart_id": "temp_profile",
        "title": "Temperature Profile Over Time",
        "type": "line",
        "x_axis": {"parameter": "elapsed_time", "unit": "Hours"},
        "y_axis": {"parameter": "temp_internal", "unit": "Celsius"},
        "series": [
          {
            "name": "Chamber Temperature",
            "data_source": "temp_internal",
            "color": "red"
          }
        ],
        "reference_lines": [
          {"value": 85, "label": "Max Spec"},
          {"value": -40, "label": "Min Spec"}
        ]
      }
    ],
    "statistics": [
      {
        "stat_id": "temp_stats",
        "title": "Temperature Statistics",
        "parameters": ["temp_internal"],
        "calculations": ["mean", "std_dev", "min", "max"]
      }
    ]
  }
}
```

## Common Parameter Reference

### Temperature Cycling
```json
{
  "temperature_celsius": 23,
  "humidity_rh_percent": 50,
  "ramp_rate_celsius_per_minute": 15,
  "dwell_time_minutes": 30
}
```

### Salt Fog Corrosion
```json
{
  "temperature_celsius": 35,
  "humidity_rh_percent": 95,
  "salt_concentration_percent": 5,
  "fog_collection_rate_ml_per_80cm2_per_day": 1.5
}
```

### Electrical Performance
```json
{
  "voltage_v": 600,
  "current_a": 10,
  "power_w": 6000,
  "illumination_w_m2": 1000
}
```

## Naming Conventions

### Protocol ID Format
```
{TYPE}-{YEAR}-{SEQUENCE}

Types:
  THC   = Temperature-Humidity Cycling
  SFCORR = Salt Fog Corrosion
  UV    = UV Exposure
  IR    = Insulation Resistance
  IV    = IV Curve Measurement
  WL    = Wind Load
  VIB   = Vibration Testing

Examples:
  THC-2024-001
  SFCORR-2024-001
  UV-2024-001
```

### Chamber ID Format
```
{ABBREV}-{SEQUENCE}

Examples:
  THC-001    (Temperature-Humidity Chamber 1)
  SFOG-001   (Salt Fog Chamber 1)
  UV-001     (UV Chamber 1)
```

### Parameter ID Format
```
{abbrev}_{location}_{type}

Examples:
  temp_internal      (internal temperature)
  humidity_internal  (internal humidity)
  temp_module        (module temperature)
```

### Check ID Format
```
QC-{PHASE}-{SEQUENCE}

Phases: Pre, In, Post

Examples:
  QC-Pre-1   (pre-test check 1)
  QC-In-1    (in-test check 1)
  QC-Post-1  (post-test check 1)
```

## Validation Checklist

Before finalizing your protocol:

### Metadata
- [ ] Protocol ID follows format: TYPE-YEAR-SEQUENCE
- [ ] Version is semantic (X.Y.Z)
- [ ] Created date is ISO8601 format
- [ ] All compliance standards are listed with section numbers

### Objectives
- [ ] Primary objective is clear and measurable
- [ ] Success criteria are quantitative where possible

### Chamber Integration
- [ ] Chamber ID is unique and follows naming convention
- [ ] All specification ranges have min and max values
- [ ] Sensor calibration status is documented
- [ ] Pre-test requirements are checkable items

### Test Sequence
- [ ] Steps are in logical order
- [ ] Step IDs are numeric (1, 2, 3) for main steps
- [ ] Sub-step IDs are hierarchical (2a, 2b, 2c)
- [ ] All durations are in consistent units
- [ ] QC checks are defined for critical steps

### Data Logging
- [ ] Every parameter has ID, name, unit, data type
- [ ] Sampling intervals are specified in seconds
- [ ] Quality checks are defined for each parameter
- [ ] Aggregation methods support analysis needs
- [ ] Storage location uses template variables

### Quality Control
- [ ] Pre-test checks are binary (pass/fail)
- [ ] In-test checks have numeric ranges
- [ ] Post-test checks reference observable criteria

### Traceability
- [ ] Audit trail tracks operator, chamber, calibration
- [ ] Sample ID format includes project and batch info
- [ ] Every compliance requirement is mapped to test steps
- [ ] Evidence locations point to data files

### Analysis (if included)
- [ ] Charts reference valid parameter_ids
- [ ] Reference lines show specification limits
- [ ] Statistics specify meaningful calculations

## Common Mistakes to Avoid

1. **Missing units** - Always specify units for numbers
2. **Inconsistent naming** - Use standard naming conventions
3. **Unclear QC criteria** - Make pass/fail criteria explicit
4. **Incomplete compliance mapping** - Map ALL requirements
5. **No pre-test requirements** - Document what must be checked
6. **Wrong timestamp format** - Use ISO8601 (YYYY-MM-DD)
7. **Ambiguous durations** - Be clear: minutes vs hours
8. **Missing quality checks** - Every parameter needs checks
9. **No storage specification** - Define where data goes
10. **Forgotten safety interlocks** - Always specify safety procedures

## Testing Your Protocol

### Validate JSON
```bash
# Use a JSON validator
jsonschema protocol-json-schema.json your-protocol.json
```

### Peer Review
- [ ] Have another engineer review objectives
- [ ] Verify chamber capabilities match requirements
- [ ] Check that QC criteria are achievable
- [ ] Confirm compliance mapping is complete

### Dry Run (if possible)
- [ ] Run protocol without test specimen
- [ ] Verify chamber can achieve all setpoints
- [ ] Check data logging works correctly
- [ ] Validate QC check calculations

## Template Reference

For a new protocol, start with the appropriate template:

- **Environmental Tests**: `templates/environmental-template.json`
- **Electrical Tests**: `templates/electrical-template.json`
- **Mechanical Tests**: `templates/mechanical-template.json`
- **Generic**: `templates/base-protocol-template.json`

Copy, rename with your protocol_id, then customize.

## Questions to Ask Before Creating a Protocol

1. **What standard are you trying to comply with?** → Add to compliance_standards
2. **What do you want to measure?** → List in data_logging.parameters
3. **How often do you need to measure it?** → Set sampling_interval_seconds
4. **What chamber or equipment do you need?** → Detail in test_chamber_integration
5. **How will you know the test passed?** → Define in objectives.success_criteria
6. **What could go wrong?** → Add safety_interlocks
7. **How will you track the samples?** → Define in sample_tracking
8. **What reports do you need to generate?** → Plan in analysis section
9. **Where will the data be stored?** → Specify in storage section
10. **How long do you need to keep the data?** → Set in retention_years

