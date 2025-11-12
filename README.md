# Test Protocols Master Dashboard & Analytics Engine

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## 🎯 Overview

Comprehensive dashboard and analytics system providing real-time visibility across all 54 test protocols, complete data traceability, KPI tracking, and predictive analytics for photovoltaic (PV) testing operations.

## ✨ Features

### 📊 Master Dashboard
- Real-time protocol execution status (all 54 protocols)
- Active service requests counter
- Pending inspections queue
- Equipment utilization rates
- Completion metrics
- QC/NC register summary
- Interactive Gantt chart for timeline view

### 📈 Protocol Analytics Module
- Individual protocol performance metrics
- Trend analysis (degradation rates, failure modes)
- Comparative analysis across protocols
- Statistical process control charts
- Predictive maintenance indicators

### 🔍 Data Traceability Viewer
- Complete audit trail visualization
- Interactive flowchart: Service Request → Inspection → Protocol → Report
- Searchable by any ID (request, sample, protocol, equipment)
- Timeline view of data journey
- Export complete traceability report
- Compliance audit support (ISO 17025, FDA 21 CFR Part 11)

### 🎯 KPI Dashboard
- Throughput metrics (samples per day/week/month)
- TAT (Turn Around Time) tracking
- Pass/Fail rates by protocol
- Equipment efficiency metrics
- Resource utilization
- Quality metrics (first-time pass rate)

### 📊 Interactive Visualizations
- Plotly-based interactive charts
- Heat maps for protocol execution patterns
- Sankey diagrams for data flow
- Real-time gauges for critical metrics
- Time-series analysis with zoom/pan
- Export charts as PNG/SVG/PDF

### 📄 Report Generator Dashboard
- One-click report generation
- Custom report builder
- Schedule automated reports
- Multi-format export (PDF/Excel/CSV)
- Email distribution

### 🔎 Search & Filter System
- Global search across all modules
- Advanced filters (date range, protocol type, status)
- Saved search presets
- Quick access to recent items

### 🔔 Notification System
- Real-time alerts for critical events
- QC failure notifications
- Equipment maintenance reminders
- Deadline approaching warnings
- Customizable notification preferences

### 🔌 Analytics API
- REST endpoints for dashboard data
- Real-time data streaming
- Export APIs
- Integration with BI tools

### 📱 Mobile-Responsive Design
- Dashboard optimized for tablets/phones
- Touch-friendly controls
- Responsive charts and tables

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Dashboard

Start the Streamlit application:
```bash
streamlit run Home.py
```

The dashboard will be available at `http://localhost:8501`

### Running the Analytics API

Start the Flask API server:
```bash
python api/analytics.py
```

The API will be available at `http://localhost:5000`

## 📁 Project Structure

```
test-protocols/
├── Home.py                    # Main entry point
├── pages/                     # Streamlit pages
│   ├── Dashboard.py           # Master dashboard
│   ├── Traceability.py        # Data traceability viewer
│   ├── KPI_Dashboard.py       # KPI metrics dashboard
│   └── Reports.py             # Report generator
├── analytics/                 # Analytics modules
│   └── protocol_analytics.py  # Protocol performance analytics
├── visualizations/            # Visualization components
│   └── charts.py              # Plotly chart builders
├── search/                    # Search and filter
│   └── search_engine.py       # Global search engine
├── notifications/             # Notification system
│   └── notification_manager.py # Notification management
├── api/                       # REST API
│   └── analytics.py           # Analytics API endpoints
├── models/                    # Data models
│   └── protocol.py            # Protocol data models
├── utils/                     # Utility functions
│   ├── data_generator.py      # Sample data generator
│   └── helpers.py             # Helper functions
├── config/                    # Configuration
│   └── config.py              # Application configuration
├── data/                      # Data storage
│   ├── raw/                   # Raw data
│   └── processed/             # Processed data
├── .streamlit/                # Streamlit configuration
│   └── config.toml            # Theme and server config
└── requirements.txt           # Python dependencies
```

## 📊 Protocol Categories (54 Total)

1. **Electrical Testing** - IV Curve, Insulation Resistance, High Voltage, etc.
2. **Mechanical Testing** - Mechanical Load, Hail Impact, Static/Dynamic Load
3. **Environmental Testing** - Thermal Cycling, Humidity Freeze, Damp Heat, UV Exposure
4. **Performance Testing** - STC Performance, NOCT, Low Irradiance, Temperature Coefficient
5. **Safety & Compliance** - Wet Leakage Current, Bypass Diode, Fire Class Rating
6. **Quality Control** - Visual Inspection, Electroluminescence, Flash Test
7. **Calibration** - Reference Cell, IV Tracer, Multimeter, IR Camera Calibration
8. **Material Analysis** - Cell Material, Backsheet, Encapsulant, Frame Material

## 🔌 API Documentation

### Base URL
`http://localhost:5000/api/v1`

### Key Endpoints

- `GET /health` - Health check
- `GET /statistics` - Overall statistics
- `GET /protocols` - Get all protocols (with filters)
- `GET /protocols/<id>` - Get specific protocol
- `GET /service-requests` - Get service requests
- `GET /equipment` - Get equipment status
- `GET /kpi/metrics` - Get KPI metrics
- `GET /analytics/trends` - Get trend analysis
- `GET /analytics/failure-analysis` - Get failure analysis
- `GET /search?q=<query>` - Global search
- `GET /notifications` - Get notifications

See `api/analytics.py` for complete API documentation.

## 🎨 UI/UX Features

- ✅ Dark/Light theme toggle (coming soon)
- ✅ Customizable dashboard layouts
- ✅ Drag-and-drop widget arrangement (coming soon)
- ✅ Bookmark favorite views
- ✅ Multi-language support ready

## 🔒 Compliance & Security

- ISO 17025 compliance
- FDA 21 CFR Part 11 requirements
- CAPA tracking support
- Full data integrity verification
- Audit trail maintenance

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly, Matplotlib
- **API**: Flask
- **Data Processing**: Pandas, NumPy
- **Database**: SQLite (extensible to PostgreSQL/MySQL)

## 📈 Performance

- Real-time data updates (5-minute cache)
- Optimized for 1000+ protocol records
- Fast search and filtering
- Responsive UI for mobile devices

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

See LICENSE file for details.

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the development team.

## 🗺️ Roadmap

- [ ] Database integration (PostgreSQL/MySQL)
- [ ] Real-time WebSocket updates
- [ ] Advanced machine learning predictions
- [ ] Custom dashboard builder
- [ ] Mobile native apps (iOS/Android)
- [ ] Multi-tenancy support
- [ ] SSO/OAuth integration

---

**Version**: 1.0.0
**Last Updated**: 2024
