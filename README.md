# Test Protocols Framework

A comprehensive, modular PV testing protocol framework with JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation.

## ✨ Features

- 📋 **JSON-based Protocol Definitions** - Flexible, version-controlled test protocols
- 🎯 **Dynamic UI Generation** - Auto-generated Streamlit forms from protocol definitions
- ✅ **Automated Validation** - Built-in data validation and quality control checks
- 📊 **Real-time Analysis** - Automatic calculation and pass/fail evaluation
- 🗄️ **Database Integration** - PostgreSQL backend for test data storage
- 📑 **Report Generation** - Automated PDF report generation
- 🔒 **Audit Trail** - Complete audit logging for compliance

## 🧪 Implemented Protocols

### DIEL-001: Dielectric Withstand Test

Based on IEC 61730 MST 15 - Verifies electrical insulation integrity of PV modules.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run ui/app.py
```

## 📚 Documentation

See `docs/protocols/DIEL-001.md` for detailed protocol documentation.

## 🏗️ Project Structure

- `protocols/` - Protocol JSON definitions
- `src/` - Source code (core, analysis, integrations)
- `ui/` - Streamlit application
- `database/` - PostgreSQL schemas
- `tests/` - Test suite
- `docs/` - Documentation

## 📝 License

MIT License
