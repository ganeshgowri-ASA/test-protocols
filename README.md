# PV Testing Protocol System

A comprehensive, modular framework for managing and executing Photovoltaic (PV) testing protocols with dynamic form generation, real-time data analysis, and automated reporting.

## 🌟 Features

- **Dynamic Protocol Loading**: JSON-based protocol templates that auto-generate forms
- **Modular Architecture**: Scalable design supporting 50+ protocols
- **Real-time Data Entry**: Interactive forms with validation and conditional logic
- **Data Analysis**: Built-in calculations, statistical analysis, and visualizations
- **Quality Control**: Automated validation rules and acceptance criteria
- **Report Generation**: Export data to PDF, Excel, CSV, and JSON formats
- **Session Management**: Auto-save functionality and session recovery
- **Standards Compliant**: Support for IEC 61215, IEC 61730, and other testing standards

## 📁 Project Structure

```
test-protocols/
├── templates/              # JSON protocol templates
│   └── base_protocol_schema.json
├── streamlit_app/         # Main Streamlit application
│   ├── main.py           # Application entry point
│   ├── pages/            # Dynamic page generation
│   ├── components/       # Reusable UI components
│   │   └── protocol_viewer.py
│   └── utils/            # Helper functions
│       ├── form_generator.py
│       └── session_manager.py
├── backend/              # Data processing & analysis
│   ├── protocol_parser.py  # Protocol JSON parser
│   ├── parsers/         # Protocol-specific parsers
│   ├── analyzers/       # Data analysis modules
│   └── validators/      # QC validation
├── config/              # Configuration files
├── data/                # Data storage
│   ├── sample_data/     # Sample test data
│   ├── outputs/         # Generated reports
│   └── sessions/        # Session data
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd test-protocols
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run streamlit_app/main.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

## 📋 Creating Protocol Templates

### Protocol JSON Structure

Each protocol is defined as a JSON file following the `base_protocol_schema.json` schema. Here's a minimal example:

```json
{
  "protocol_metadata": {
    "protocol_id": "iv_curve_test",
    "protocol_name": "I-V Curve Characterization",
    "version": "1.0.0",
    "category": "electrical",
    "standard_reference": "IEC 61215-2",
    "description": "Measurement of current-voltage characteristics",
    "tags": ["electrical", "performance", "characterization"]
  },
  "general_data": {
    "fields": [
      {
        "field_id": "test_date",
        "field_name": "Test Date",
        "field_type": "date",
        "required": true
      },
      {
        "field_id": "operator",
        "field_name": "Operator Name",
        "field_type": "text",
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
      },
      {
        "field_id": "manufacturer",
        "field_name": "Manufacturer",
        "field_type": "text"
      }
    ]
  }
}
```

### Supported Field Types

| Field Type | Description | Use Case |
|------------|-------------|----------|
| `text` | Single-line text input | Names, IDs, short descriptions |
| `number` | Numeric input with validation | Measurements, counts |
| `date` | Date picker | Test dates, deadlines |
| `datetime` | Date and time picker | Timestamp recordings |
| `select` | Dropdown selection | Predefined options |
| `multiselect` | Multiple selection | Tags, categories |
| `textarea` | Multi-line text input | Notes, observations |
| `checkbox` | Boolean checkbox | Yes/No questions |
| `file_upload` | File upload widget | Images, data files |
| `calculated` | Auto-calculated field | Derived values |

### Protocol Sections

1. **protocol_metadata**: Core identification and configuration
2. **general_data**: General test information
3. **sample_info**: Sample identification and specs
4. **protocol_inputs**: Test parameters and configurations
5. **live_readings**: Real-time data capture tables
6. **analysis**: Calculations and statistical analysis
7. **charts**: Visualization configurations
8. **quality_control**: Validation rules and acceptance criteria
9. **maintenance**: Equipment maintenance tracking
10. **project_management**: Project tracking and milestones
11. **nc_register**: Non-conformance tracking

## 🔧 Configuration

### Application Settings

Edit `config/app_config.json` (create if doesn't exist):

```json
{
  "app_name": "PV Testing Protocol System",
  "data_directory": "./data",
  "auto_save": true,
  "auto_save_interval": 300,
  "theme": "light",
  "enable_notifications": true
}
```

### Adding New Protocols

1. Create a new JSON file in `templates/` directory
2. Follow the schema defined in `base_protocol_schema.json`
3. Validate your JSON using the protocol parser:
   ```python
   from backend.protocol_parser import ProtocolParser

   parser = ProtocolParser()
   is_valid, error = parser.validate_protocol(your_protocol_data)
   ```
4. Restart the Streamlit application
5. Your protocol will appear in the dropdown

## 📊 Usage Guide

### 1. Select Protocol

- Launch the application
- Choose a protocol category (if applicable)
- Select the desired protocol from the dropdown

### 2. Enter Data

- Navigate to "📝 Data Entry" section
- Fill in required fields (marked with *)
- Use tabs to switch between different sections
- Data is auto-saved at regular intervals

### 3. Run Analysis

- Go to "📊 Analysis & Charts" section
- View calculated results
- Generate visualizations
- Export charts as images

### 4. Quality Control

- Navigate to "✅ Quality Control" section
- Run validation checks
- Review any warnings or errors
- View acceptance criteria status

### 5. Generate Reports

- Go to "📄 Generate Report" section
- Select report format (PDF, Excel, CSV, JSON)
- Choose sections to include
- Configure report settings
- Click "Generate Report"

## 🎨 Architecture

### Backend Components

#### Protocol Parser (`backend/protocol_parser.py`)
- Loads and validates JSON protocols
- Extracts form structures
- Manages protocol cache
- Handles schema validation

#### Form Generator (`streamlit_app/utils/form_generator.py`)
- Dynamically generates Streamlit forms
- Handles all field types
- Implements conditional logic
- Manages data tables

#### Session Manager (`streamlit_app/utils/session_manager.py`)
- Tracks user sessions
- Saves/loads form data
- Manages data persistence
- Handles exports

### Frontend Components

#### Main Application (`streamlit_app/main.py`)
- Application entry point
- Routing and navigation
- Page rendering
- State management

#### Protocol Viewer (`streamlit_app/components/protocol_viewer.py`)
- Displays protocol information
- Shows validation status
- Renders summaries

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=streamlit_app

# Run specific test file
pytest tests/test_protocol_parser.py
```

### Creating Tests

Add test files to a `tests/` directory:

```python
# tests/test_protocol_parser.py
from backend.protocol_parser import ProtocolParser

def test_load_protocol():
    parser = ProtocolParser()
    protocol = parser.load_protocol("templates/sample_protocol.json")
    assert protocol is not None
    assert "protocol_metadata" in protocol
```

## 📈 Extending the System

### Adding Custom Analyzers

1. Create a new file in `backend/analyzers/`:
   ```python
   # backend/analyzers/custom_analyzer.py
   class CustomAnalyzer:
       def analyze(self, data):
           # Your analysis logic
           return results
   ```

2. Import and use in your protocol

### Adding Custom Validators

1. Create a new file in `backend/validators/`:
   ```python
   # backend/validators/custom_validator.py
   class CustomValidator:
       def validate(self, value, rule):
           # Your validation logic
           return is_valid, message
   ```

2. Register in validation system

### Custom Field Types

To add a new field type:

1. Add field type to schema
2. Create renderer in `FormGenerator`:
   ```python
   def _render_custom_field(self, field_def, field_key):
       # Implement custom field rendering
       pass
   ```
3. Register in field_renderers dictionary

## 🔐 Data Management

### Data Storage

- **Session Data**: Stored in `data/sessions/`
- **Output Reports**: Stored in `data/outputs/`
- **Sample Data**: Stored in `data/sample_data/`

### Data Export

Export data using the Session Manager:

```python
from streamlit_app.utils.session_manager import SessionManager

manager = SessionManager()
manager.export_session_data(session_id="your_session_id")
```

### Data Backup

Regular backups recommended:
```bash
# Backup data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

## 🤝 Contributing

### Adding Protocols

1. Create protocol JSON following schema
2. Test with validation tool
3. Add to templates directory
4. Update documentation

### Code Contributions

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings
- Write tests for new features

## 📚 Documentation

### Additional Resources

- **Schema Documentation**: See `templates/base_protocol_schema.json`
- **API Documentation**: Generate with `pdoc backend/`
- **User Guide**: See `docs/user_guide.md` (when created)

### Protocol Examples

Example protocols will be added to `templates/examples/`:
- I-V Curve Characterization
- Thermal Cycling Test
- Damp Heat Test
- Mechanical Load Test
- UV Pre-conditioning

## 🐛 Troubleshooting

### Common Issues

**Issue**: Protocol not appearing in dropdown
- **Solution**: Check JSON syntax, validate against schema

**Issue**: Form not saving data
- **Solution**: Check file permissions in data directory

**Issue**: Import errors
- **Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`

**Issue**: Validation errors
- **Solution**: Check that all required fields are present in protocol JSON

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

See LICENSE file for details.

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review example protocols

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core framework
- ✅ Dynamic form generation
- ✅ Protocol parser
- ✅ Session management

### Phase 2 (Upcoming)
- [ ] Add 54 protocol templates
- [ ] Advanced data analysis
- [ ] Real-time charting
- [ ] PDF report generation

### Phase 3 (Future)
- [ ] Multi-user support
- [ ] Database integration
- [ ] API endpoints
- [ ] Mobile app

## 🙏 Acknowledgments

Built for photovoltaic testing laboratories following international standards including:
- IEC 61215: Terrestrial PV modules - Design qualification
- IEC 61730: PV module safety qualification
- IEC 61853: PV module performance testing

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Status**: Active Development
