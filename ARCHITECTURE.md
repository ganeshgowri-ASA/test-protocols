# PV Testing Protocol Framework - Architecture Guide

## Overview
This is a modular, JSON-based framework for dynamic testing protocols in photovoltaic (PV) testing environments. The framework integrates with:
- **UI**: Streamlit/GenSpark
- **Analysis**: Automated analysis, charting, QC
- **Integration**: LIMS, QMS, Project Management systems
- **Data**: Time-series logging and traceability

## Directory Structure

```
test-protocols/
├── protocols/                              # Protocol definitions
│   ├── environmental/                      # Environmental testing protocols
│   │   ├── temperature-humidity-cycling.json
│   │   ├── salt-fog-corrosion.json
│   │   ├── uv-exposure.json
│   │   └── thermal-stress.json
│   ├── electrical/                         # Electrical testing protocols
│   │   ├── iv-curve-measurement.json
│   │   ├── insulation-resistance.json
│   │   ├── leakage-current.json
│   │   └── performance-degradation.json
│   ├── mechanical/                         # Mechanical testing protocols
│   │   ├── wind-load.json
│   │   ├── impact-resistance.json
│   │   └── vibration-testing.json
│   └── templates/                          # Base templates for protocol creation
│       ├── base-protocol-template.json
│       ├── environmental-template.json
│       ├── electrical-template.json
│       └── mechanical-template.json
├── schemas/                                # JSON schemas for validation
│   ├── protocol-schema.json
│   ├── chamber-config-schema.json
│   ├── data-logging-schema.json
│   └── analysis-schema.json
├── configs/                                # Configuration files
│   ├── test-chambers.json                  # Chamber specifications
│   ├── data-loggers.json                   # Logger configurations
│   ├── analysis-templates.json             # Analysis configurations
│   └── integration/
│       ├── lims-integration.json
│       ├── qms-integration.json
│       └── pms-integration.json
├── examples/                               # Complete example protocols
│   ├── salt-fog-corrosion-example.json
│   └── temperature-humidity-example.json
├── analysis/                               # Analysis and charting specifications
│   ├── statistical-analysis.json
│   ├── charting-templates.json
│   └── qc-rules.json
├── traceability/                           # Traceability specifications
│   ├── audit-trail-schema.json
│   ├── sample-tracking.json
│   └── compliance-mapping.json
└── docs/                                   # Documentation
    ├── protocol-creation-guide.md
    ├── json-format-specification.md
    ├── data-logging-guide.md
    ├── time-series-analysis.md
    └── integration-guide.md
```

## Key Components

### 1. Protocol Structure
Each protocol JSON file contains:
- **Metadata**: ID, name, version, author, creation date, compliance standards
- **Objective**: Testing goals and success criteria
- **Chamber Configuration**: Test chamber settings and monitoring
- **Test Sequence**: Ordered test steps with durations and conditions
- **Data Logging**: Specification of what to measure and how often
- **QC Checks**: Quality control rules and pass/fail criteria
- **Analysis**: Automated analysis and charting specifications
- **Traceability**: Audit trail and compliance mapping

### 2. Test Chamber Integration
Protocols specify:
- Chamber type and specifications
- Required sensors and instruments
- Parameter ranges (temperature, humidity, pressure, etc.)
- Calibration requirements
- Real-time monitoring specifications
- Safety interlocks and alarms

### 3. Data Logging
Specifications include:
- Parameters to log (sensors, measurements)
- Sampling rates and intervals
- Data quality requirements
- Storage specifications
- Time-series data structure

### 4. Time-Series Analysis
Implementations provide:
- Aggregation functions (mean, min, max, std dev)
- Trend analysis
- Anomaly detection
- Degradation rate calculation
- Statistical summaries

### 5. Traceability
Features include:
- Sample identification and tracking
- Operator/user tracking
- Chamber and instrument calibration status
- Compliance standard mappings
- Audit trail with timestamps
- Report generation templates

## JSON Structure Patterns

### Pattern 1: Hierarchical Parameter Definition
```json
{
  "parameters": {
    "category": {
      "parameter_name": {
        "type": "float|int|string|boolean",
        "unit": "°C|%RH|V|A|etc",
        "min": 0,
        "max": 100,
        "default": 50,
        "description": "Parameter description"
      }
    }
  }
}
```

### Pattern 2: Time-Based Sequence
```json
{
  "test_sequence": [
    {
      "step_id": 1,
      "name": "Step name",
      "duration_minutes": 60,
      "conditions": { /* parameters */ },
      "logging_interval_seconds": 60,
      "qc_checks": [ /* checks */ ]
    }
  ]
}
```

### Pattern 3: Data Logging Specification
```json
{
  "data_logging": {
    "parameters": [
      {
        "parameter_id": "temp_internal",
        "source": "chamber_sensor_1",
        "unit": "°C",
        "sampling_interval_seconds": 30,
        "aggregation": ["mean", "min", "max", "std_dev"]
      }
    ]
  }
}
```

### Pattern 4: Analysis and Visualization
```json
{
  "analysis": {
    "charts": [
      {
        "chart_id": "temperature_trend",
        "type": "line|scatter|histogram|heatmap",
        "title": "Temperature Trend Over Time",
        "x_axis": "timestamp",
        "y_axis": "temperature",
        "series": [ /* data series definitions */ ]
      }
    ],
    "statistics": [
      {
        "stat_id": "temp_stats",
        "parameters": ["temperature"],
        "calculations": ["mean", "median", "std_dev", "slope"]
      }
    ]
  }
}
```

### Pattern 5: Traceability and Compliance
```json
{
  "traceability": {
    "audit_trail": {
      "track_operator": true,
      "track_chamber_id": true,
      "track_instrument_calibration": true,
      "timestamp_format": "ISO8601"
    },
    "compliance_standards": [
      {
        "standard_id": "IEC61215",
        "mapping": {
          "test_sequence_step": 1,
          "requirement": "Temperature cycling -40°C to 85°C"
        }
      }
    ]
  }
}
```

## Common Patterns and Best Practices

1. **Modular Design**: Protocols reference templates to avoid duplication
2. **Parameterization**: Environmental conditions are fully parameterized
3. **Validation**: JSON schemas enforce structure and types
4. **Version Control**: Each protocol has version tracking
5. **Compliance Mapping**: Standards requirements are explicitly mapped
6. **Data Quality**: Logging specifications include QC parameters
7. **Time-Series Format**: Uses consistent timestamp formats (ISO8601)
8. **Aggregation Strategy**: Multiple aggregation levels (raw, summary, statistical)
9. **Error Handling**: Specifications for sensor failures and data gaps
10. **Audit Trail**: Complete traceability with timestamps and user tracking

