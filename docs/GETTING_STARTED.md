# Getting Started with PV Testing Protocol System

## Introduction

Welcome to the PV Testing Protocol System! This guide will help you get started with creating and using testing protocols.

## Installation

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation:**
   ```bash
   python backend/protocol_parser.py
   ```

3. **Launch Application:**
   ```bash
   streamlit run streamlit_app/main.py
   ```

## Your First Protocol

### Step 1: Understand the Schema

The protocol schema is defined in `templates/base_protocol_schema.json`. All protocols must follow this schema.

### Step 2: Use the Sample Protocol

A sample I-V Curve protocol is provided in `templates/sample_iv_curve_protocol.json`. This is a great starting point to understand the structure.

### Step 3: Create Your Protocol

1. Copy the sample protocol
2. Modify the `protocol_metadata` section
3. Add your fields to `general_data` and `sample_info`
4. Define test parameters in `protocol_inputs`
5. Add validation rules in `quality_control`

### Step 4: Validate Your Protocol

```python
from backend.protocol_parser import ProtocolParser

parser = ProtocolParser()
protocol = parser.load_protocol("templates/your_protocol.json")
is_valid, error = parser.validate_protocol(protocol)

if is_valid:
    print("Protocol is valid!")
else:
    print(f"Validation error: {error}")
```

## Key Concepts

### Protocol Metadata
- **protocol_id**: Unique identifier (use snake_case)
- **protocol_name**: Human-readable name
- **category**: One of: electrical, mechanical, environmental, optical, thermal, reliability, quality_control
- **standard_reference**: Reference to testing standard (e.g., IEC 61215)

### Field Types
- **text**: Simple text input
- **number**: Numeric input with optional min/max validation
- **date**: Date picker
- **select**: Dropdown with predefined options
- **checkbox**: Boolean yes/no
- **textarea**: Multi-line text
- **file_upload**: File attachment

### Sections
- **general_data**: Basic test information
- **sample_info**: Sample identification
- **protocol_inputs**: Test parameters
- **live_readings**: Data collection tables
- **analysis**: Calculations and formulas
- **charts**: Visualization configurations
- **quality_control**: Validation rules

## Example: Creating a Simple Protocol

```json
{
  "protocol_metadata": {
    "protocol_id": "visual_inspection",
    "protocol_name": "Visual Inspection",
    "version": "1.0.0",
    "category": "quality_control",
    "description": "Visual inspection of PV modules"
  },
  "general_data": {
    "fields": [
      {
        "field_id": "inspector",
        "field_name": "Inspector Name",
        "field_type": "text",
        "required": true
      },
      {
        "field_id": "inspection_date",
        "field_name": "Inspection Date",
        "field_type": "date",
        "required": true
      }
    ]
  },
  "sample_info": {
    "fields": [
      {
        "field_id": "module_id",
        "field_name": "Module ID",
        "field_type": "text",
        "required": true
      }
    ]
  }
}
```

## Tips

1. **Start Simple**: Begin with basic fields and add complexity gradually
2. **Use Validation**: Add validation rules to ensure data quality
3. **Test Often**: Validate your protocol frequently during development
4. **Document**: Use the `description` field to provide clear instructions
5. **Reuse**: Copy successful protocols as templates for new ones

## Common Issues

### Protocol Not Appearing
- Check JSON syntax (use a JSON validator)
- Ensure file is in `templates/` directory
- Verify `protocol_metadata` section is present
- Restart Streamlit application

### Validation Errors
- Check required fields are present
- Verify field_type values are valid
- Ensure all IDs are unique within protocol

### Form Not Rendering
- Check field definitions are complete
- Verify field_type is supported
- Look for console errors in Streamlit

## Next Steps

1. Explore the sample protocol in detail
2. Create a simple protocol for your test
3. Add validation rules
4. Configure charts and visualizations
5. Test data entry and report generation

## Resources

- **Schema Reference**: `templates/base_protocol_schema.json`
- **Sample Protocol**: `templates/sample_iv_curve_protocol.json`
- **API Documentation**: See docstrings in Python files
- **Main README**: `README.md`

## Support

For questions or issues:
1. Check the troubleshooting section in README.md
2. Review example protocols
3. Create an issue in the repository

Happy Testing! 🔬
