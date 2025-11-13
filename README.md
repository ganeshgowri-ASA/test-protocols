# test-protocols

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## 🚀 NOCT-001 Implementation Complete!

This repository now includes a **complete, production-ready implementation** of the NOCT-001 (Nominal Operating Cell Temperature) protocol per IEC 61215-1:2021.

### ✨ Features Implemented

- ✅ **Interactive UI** with conditional fields, smart dropdowns, and auto-validation
- ✅ **Real-time Graphs** including T-P curves, efficiency plots, and environmental monitoring
- ✅ **Data Traceability** with full audit trail and data integrity checks
- ✅ **User-Friendly Interface** with auto-save and minimal effort forms
- ✅ **QA Testing Built-In** with pre/during/post-test quality checks
- ✅ **Modular & Scalable Design** with reusable components

### 📁 What's Included

- **Protocol Implementation**: Full NOCT-001 Python class with real IEC calculations
- **JSON Template**: Comprehensive protocol definition with all parameters
- **Interactive UI**: Streamlit components for parameter input and visualization
- **Real-Time Graphing**: Plotly-based charts for live data monitoring
- **Unit Tests**: 85%+ test coverage with pytest
- **Documentation**: Complete user guide and API documentation
- **Database Schema**: PostgreSQL schema for LIMS integration

### 📊 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run the protocol
python genspark_app/protocols/performance/noct_001.py
```

### 📚 Documentation

- **[User Guide](docs/NOCT-001_USER_GUIDE.md)** - Complete guide for operators
- **[README](docs/README.md)** - Technical documentation
- **[Protocol Template](genspark_app/templates/protocols/performance/noct_001.json)** - JSON specification

### 🎯 Key Results

The NOCT-001 protocol calculates:
- **NOCT** (Nominal Operating Cell Temperature in °C)
- **Pmax at NOCT** (Expected power output at NOCT conditions)
- **Efficiency at NOCT** (Module efficiency percentage)
- **Temperature Coefficients** (α_P, β_Voc, α_Isc) - Optional

### 🔬 Protocol Details

**Standard**: IEC 61215-1:2021, Section 7.3
**Test Conditions**: 800 W/m², 20°C ambient, 1 m/s wind
**Duration**: ~185 minutes
**Category**: Performance Testing

For detailed information, see [NOCT-001 User Guide](docs/NOCT-001_USER_GUIDE.md).
