# PV Test Protocols Framework

Modular, JSON-based testing protocol framework for photovoltaic (PV) module testing with GenSpark UI integration, automated analysis, charting, QC validation, and report generation.

## Overview

This framework provides a comprehensive suite of test protocols for PV module reliability and performance testing. Each protocol is defined in JSON format with corresponding Python implementations, database schemas, and UI components.

## Implemented Protocols (P21-P30)

### Environmental Testing
- **CORR-001**: Salt Mist Corrosion Testing (IEC 61701)
- **TC-001**: Thermal Cycling (-40°C to +85°C, IEC 61215 MQT11)
- **DH-001**: Damp Heat 1000h (85°C/85%RH, IEC 61215 MQT13)
- **DH-002**: Damp Heat 2000h Extended (85°C/85%RH, IEC 61215)

### Characterization
- **CHALK-001**: Backsheet Chalking Assessment (ASTM D4214)
- **YELLOW-001**: EVA Yellowing Index Measurement (ASTM E313)
- **CRACK-001**: Cell Crack Propagation Analysis (IEC TS 60904-13)

### Reliability Testing
- **SOLDER-001**: Solder Bond Degradation Testing (IEC 62790)
- **JBOX-001**: Junction Box Degradation Testing (IEC 61215-2)
- **SEAL-001**: Edge Seal Degradation Assessment (IEC 61215-2 MQT12)

## Directory Structure

```
test-protocols/
├── protocols/                    # Protocol definitions
│   ├── corr-001/                # Corrosion testing
│   ├── chalk-001/               # Chalking assessment
│   ├── yellow-001/              # EVA yellowing
│   ├── crack-001/               # Crack detection
│   ├── solder-001/              # Solder bond testing
│   ├── jbox-001/                # Junction box testing
│   ├── seal-001/                # Edge seal testing
│   ├── tc-001/                  # Thermal cycling
│   ├── dh-001/                  # Damp heat 1000h
│   └── dh-002/                  # Damp heat 2000h
├── backend/                     # Backend services
│   ├── models/                  # Database models
│   └── services/                # Business logic
├── frontend/                    # Streamlit UI components
├── tests/                       # Integration tests
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Features

- **JSON-Based Protocol Definition**: Declarative specifications with validation
- **Python Implementation**: Async support, modular design, comprehensive logging
- **Database Integration**: SQLAlchemy ORM, execution tracking, results storage
- **GenSpark UI**: Streamlit interface with real-time monitoring and charts
- **Quality Control**: Automated validation with standard compliance checks
- **Report Generation**: Automated analysis and report creation

## Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Loading a Protocol

```python
from backend.services.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("CORR-001")
print(protocol["name"])
```

### Running a Test

```python
import asyncio
from protocols.corr001.python.corrosion import run_corrosion_test

config = {
    "sample_id": "MODULE_001",
    "test_severity": "Level 6",
    "salt_concentration": 50.0,
    "chamber_temperature": 35.0,
    "exposure_duration": 720.0
}

results = asyncio.run(run_corrosion_test(config))
```

## Standards Compliance

- IEC 61215-2: PV module design qualification
- IEC 61701: Salt mist corrosion testing
- IEC 62790: Junction box safety requirements
- IEC TS 60904-13: Electroluminescence testing
- ASTM E313: Yellowness index calculation
- ASTM D4214: Chalking evaluation
- ASTM B117: Salt spray testing

## Testing

```bash
pytest tests/
```

## License

See LICENSE file for details.
