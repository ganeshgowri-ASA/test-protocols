# PVTP-024: Electroluminescence (EL) Imaging - Pre/Post Test

## Overview
Comprehensive protocol for EL imaging of solar modules with AI/ML-powered defect detection, automated grading, and pre/post-test comparison capabilities.

## Features
- ✅ Advanced image processing (dark frame, flat-field, enhancement)
- ✅ AI/ML defect detection (YOLOv8, U-Net, EfficientNet ensemble)
- ✅ Automated severity classification and grading
- ✅ Pre/post-test comparison with image registration
- ✅ Real-time defect database integration
- ✅ Automated QC and non-conformance management
- ✅ Full traceability and LIMS/QMS integration

## Files
- `protocol.json` - Complete protocol specification
- `el_imaging_processor.py` - Python backend processor
- `README.md` - This file

## Quick Start

```python
from el_imaging_processor import ELImageProcessor
import json

# Load protocol
with open('protocol.json', 'r') as f:
    config = json.load(f)

# Initialize processor
processor = ELImageProcessor(config)

# Run analysis
result = processor.run_full_analysis(
    raw_image_path="path/to/el_image.tif",
    dark_frame_path="path/to/dark_frame.tif",
    flat_field_path="path/to/flat_field.tif",
    test_params={'injection_current': 9.0},
    module_serial="MOD123456",
    test_sequence="pre_test"
)

print(f"Grade: {result.grade.value}")
print(f"Defects: {len(result.defects)}")
```

## Defect Types Detected
- Cell cracks
- Finger interruptions
- Busbar interruptions
- Inactive areas
- Shunts
- Dark cells
- Corrosion
- Solder bond failures

## Grading System
- **Grade A**: Excellent - No significant defects
- **Grade B**: Good - Minor defects only
- **Grade C**: Acceptable - Some defects within limits
- **Grade D**: Marginal - Near rejection limits (requires review)
- **Grade F**: Fail - Exceeds defect limits (automatic NC)

## Integration
- Streamlit UI dashboard
- REST API endpoints
- LIMS integration (LabVantage)
- QMS integration (ETQ)
- Project management sync

## Standards Compliance
- IEC 60904-13
- IEC TS 60904-13
- SEMI PV50-0611
- ASTM E2667
