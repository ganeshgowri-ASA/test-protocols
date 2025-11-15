# Solar PV Testing LIMS-QMS System

> **Unified Streamlit Application for Managing 54 Solar PV Testing Protocols**

A comprehensive, production-ready Laboratory Information Management System (LIMS) and Quality Management System (QMS) for solar PV module testing. This application integrates all 54 testing protocols into a unified workflow system with complete data traceability.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🌟 Features

### Core Capabilities
- **📋 Service Request Management** - Create and track testing service requests
- **📦 Incoming Inspection** - Visual inspection with QR code generation
- **⚙️ Equipment Booking** - Calendar-based equipment reservation system
- **🔬 54 Test Protocols** - Complete protocol execution framework
- **📊 Real-time Analytics** - Cross-protocol analytics and KPIs
- **📱 QR Code Integration** - Sample tracking and traceability
- **📝 Audit Trail** - Complete data traceability and change logging
- **📄 Report Generation** - Automated PDF report generation
- **🔐 User Management** - Role-based access control

### Protocol Categories
1. **Performance Testing (P1-P12)** - I-V curves, P-V analysis, efficiency
2. **Degradation Testing (P13-P27)** - LID, PID, thermal cycling
3. **Environmental Testing (P28-P39)** - Humidity freeze, UV exposure, salt mist
4. **Mechanical Testing (P40-P47)** - Load tests, hail impact, wind pressure
5. **Safety Testing (P48-P54)** - Insulation, leakage current, fire resistance

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager
- 2GB free disk space

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/test-protocols.git
   cd test-protocols
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python -c "from config.database import init_database; init_database()"
   ```

6. **Run Application**
   ```bash
   streamlit run app.py
   ```

7. **Access Application**
   - Open browser to: `http://localhost:8501`
   - Default credentials: `admin` / `admin123`

---

## 📖 User Guide

### Workflow Overview

```
1. Service Request → 2. Incoming Inspection → 3. Equipment Booking → 4. Test Execution → 5. Report Generation
```

### 1. Creating a Service Request

1. Navigate to **Service Request** page
2. Fill in client information
3. Select sample details
4. Choose testing protocols from 54 available options
5. Submit request for approval

### 2. Incoming Inspection

1. Link to approved service request
2. Complete visual inspection checklist
3. Record physical measurements
4. Upload photos
5. Generate QR code for sample tracking

### 3. Equipment Booking

1. View available equipment
2. Select equipment for your test
3. Choose booking period
4. Specify purpose and notes
5. Confirm booking

### 4. Test Protocol Execution

1. Select protocol from catalog
2. Link to service request
3. Enter test parameters
4. Upload data files
5. Review auto-calculated results
6. Generate visualizations
7. Complete QA validation

### 5. Analytics & Reporting

- View dashboard metrics
- Analyze cross-protocol trends
- Export data (Excel, CSV, JSON)
- Generate PDF reports
- Review audit trail

---

## 🏗️ Architecture

### Project Structure

```
test-protocols/
├── app.py                      # Main application entry point
├── config/                     # Configuration files
│   ├── settings.py            # Global settings
│   ├── database.py            # Database configuration
│   └── protocols_registry.py  # Protocol registry
├── pages/                      # Streamlit pages
│   ├── 2_📋_Service_Request.py
│   ├── 3_📦_Incoming_Inspection.py
│   ├── 4_⚙️_Equipment_Booking.py
│   └── 5_🔬_Test_Protocols.py
├── components/                 # Reusable components
│   ├── navigation.py          # Navigation sidebar
│   ├── analytics_engine.py    # Analytics engine
│   ├── data_traceability.py   # Audit trail
│   ├── visualizations.py      # Plotting components
│   └── qr_generator.py        # QR code generation
├── database/                   # Database layer
│   ├── models.py              # SQLAlchemy models
│   └── migrations/            # Alembic migrations
├── protocols/                  # Protocol implementations
│   ├── performance/           # P1-P12
│   ├── degradation/           # P13-P27
│   ├── environmental/         # P28-P39
│   ├── mechanical/            # P40-P47
│   └── safety/                # P48-P54
├── utils/                      # Utility functions
├── tests/                      # Test suite
├── static/                     # Static assets
├── data/                       # Data storage
└── requirements.txt           # Dependencies
```

### Technology Stack

- **Frontend**: Streamlit 1.31+
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **Visualization**: Plotly
- **PDF Generation**: ReportLab/WeasyPrint
- **QR Codes**: python-qrcode
- **Data Processing**: Pandas, NumPy

---

## 🔧 Configuration

### Database Configuration

#### SQLite (Default - Development)
```python
DATABASE_URL="sqlite:///./data/solar_pv_lims.db"
```

#### PostgreSQL (Production)
```python
DATABASE_URL="postgresql://user:password@localhost:5432/solar_pv_lims"
```

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `APP_ENV`: Development, staging, or production
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET_KEY`: Secret key for sessions (change in production!)
- `ENABLE_AUTHENTICATION`: Enable/disable user authentication
- `MAX_UPLOAD_SIZE_MB`: Maximum file upload size

---

## 📊 Database Schema

### Core Tables

1. **users** - User authentication and profiles
2. **service_requests** - Testing service requests
3. **incoming_inspections** - Visual inspections
4. **equipment** - Equipment inventory
5. **equipment_bookings** - Equipment reservations
6. **test_protocols** - Protocol definitions
7. **test_executions** - Test execution records
8. **test_data** - Detailed test measurements
9. **audit_logs** - Complete audit trail
10. **qr_codes** - QR code mappings

### Relationships

```
service_request (1) ←→ (N) incoming_inspection
service_request (1) ←→ (N) test_execution
equipment (1) ←→ (N) equipment_booking
test_protocol (1) ←→ (N) test_execution
test_execution (1) ←→ (N) test_data
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database.py
```

### Test Categories

- Unit tests for models and utilities
- Integration tests for workflows
- UI component tests
- Database migration tests

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t solar-pv-lims:latest .

# Run container
docker run -d -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --name solar-pv-lims \
  solar-pv-lims:latest
```

---

## 📝 Protocol Development

### Adding a New Protocol

1. **Create Protocol Module**
   ```python
   # protocols/category/pXX_protocol_name.py

   def get_metadata():
       return {
           "protocol_id": "PXX",
           "name": "Protocol Name",
           "category": "performance",
           "description": "Description",
           "standard_reference": "IEC XXXXX"
       }

   def render_form():
       # Render input form
       pass

   def validate_inputs(data):
       # Validate inputs
       pass

   def execute_test(data):
       # Execute test logic
       pass

   def generate_visualizations(results):
       # Generate charts
       pass

   def calculate_results(raw_data):
       # Calculate results
       pass

   def generate_report(results):
       # Generate PDF report
       pass
   ```

2. **Register Protocol**
   - Protocol is auto-discovered by registry
   - Or manually register in `protocols_registry.py`

3. **Test Protocol**
   - Execute through UI
   - Verify calculations
   - Check visualizations

---

## 🔐 Security

### Best Practices

1. **Change Default Credentials**
   - Update admin password immediately
   - Use strong, unique passwords

2. **Secure Database**
   - Use PostgreSQL in production
   - Enable SSL for database connections
   - Regular backups

3. **Environment Variables**
   - Never commit `.env` file
   - Use strong `SESSION_SECRET_KEY`
   - Rotate secrets regularly

4. **Authentication**
   - Enable authentication in production
   - Implement role-based access control
   - Log all user actions

---

## 📈 Performance Optimization

### Caching

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_expensive_data():
    return compute_data()
```

### Database Optimization

- Use indexes on frequently queried fields
- Implement pagination for large datasets
- Use database connection pooling
- Regular VACUUM/ANALYZE operations

### Streamlit Optimization

- Lazy loading of protocol modules
- Pagination for large tables
- Optimize image sizes
- Use `st.cache_resource` for connections

---

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check DATABASE_URL in .env
   # Ensure database file/server is accessible
   # Verify permissions
   ```

2. **Module Import Error**
   ```bash
   # Ensure virtual environment is activated
   # Reinstall requirements: pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Change port: streamlit run app.py --server.port 8502
   ```

4. **File Upload Error**
   ```bash
   # Check MAX_UPLOAD_SIZE_MB in .env
   # Verify file permissions in data/uploads/
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Maintain backward compatibility

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Ganesh Gowri** - [ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)

---

## 🙏 Acknowledgments

- IEC 61215 Standard Committee
- Streamlit Community
- Solar PV Testing Community

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Documentation**: [Wiki](https://github.com/ganeshgowri-ASA/test-protocols/wiki)
- **Email**: support@solarpv.com

---

## 🗺️ Roadmap

### Version 1.1 (Upcoming)
- [ ] Advanced analytics dashboard
- [ ] Custom report templates
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Mobile app

### Version 1.2
- [ ] AI-powered data validation
- [ ] Predictive maintenance
- [ ] Integration with external LIMS
- [ ] Cloud deployment templates

### Version 2.0
- [ ] Real-time collaboration
- [ ] Advanced workflow automation
- [ ] Machine learning for test optimization
- [ ] IoT device integration

---

**Built with ❤️ for the Solar PV Testing Community**
