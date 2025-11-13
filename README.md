# PV Testing LIMS-QMS with 54 Protocols

A comprehensive Laboratory Information Management System (LIMS) with Quality Management System (QMS) integration for Photovoltaic (PV) module testing. Built with GenSpark framework and featuring all 54 industry-standard test protocols.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🌟 Features

### Complete Protocol Coverage (54 Protocols)
- **12 Performance Testing Protocols**: STC, NOCT, Low Irradiance, Temperature Response, IAM, Spectral Response, Energy Rating, Bifacial, and more
- **15 Degradation Testing Protocols**: LID, LeTID, PID, UV, Snail Trail, Delamination, Corrosion, and more
- **12 Environmental Testing Protocols**: Thermal Cycling, Damp Heat, Humidity Freeze, Salt Mist, Ammonia, and more
- **8 Mechanical Testing Protocols**: Static/Dynamic Load, Hail Impact, Wind/Snow Load, Vibration, Twist Testing
- **7 Safety Testing Protocols**: Insulation, Wet Leakage, Dielectric, Ground Continuity, Hot Spot, Bypass Diode, Fire Resistance

### Complete Workflow Integration
- **Service Request Management**: Customer intake, quote generation, approval workflow
- **Incoming Inspection**: Sample reception, visual inspection, barcode/QR generation
- **Equipment Booking**: Scheduling, conflict detection, calibration tracking
- **Protocol Execution**: Guided testing, real-time monitoring, automated calculations

### Data Traceability
- Complete audit trail from raw data to final reports
- Timestamps and user tracking on every action
- Equipment usage tracking
- Environmental conditions logging
- Version control for protocols
- Change history for all edits

### Modern Architecture
- Flask backend with RESTful API
- GenSpark frontend framework
- PostgreSQL database with full schema
- Redis for caching and background tasks
- Celery for asynchronous processing
- Docker containerization for easy deployment

## 📋 Requirements

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Web UI: http://localhost:5000
- API: http://localhost:5000/api

5. Default credentials (CHANGE IN PRODUCTION!):
- Username: admin
- Password: admin123

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database:
```bash
createdb pv_lims
psql pv_lims < genspark_app/database/schema.sql
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
python genspark_app/app.py
```

## 📁 Project Structure

```
test-protocols/
├── genspark_app/
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration management
│   ├── workflows/                # Workflow implementations
│   │   ├── service_request.py
│   │   ├── incoming_inspection.py
│   │   ├── equipment_booking.py
│   │   └── protocol_execution.py
│   ├── protocols/                # All 54 protocol implementations
│   │   ├── base_protocol.py      # Base protocol class
│   │   ├── performance/          # 12 protocols
│   │   ├── degradation/          # 15 protocols
│   │   ├── environmental/        # 12 protocols
│   │   ├── mechanical/           # 8 protocols
│   │   └── safety/               # 7 protocols
│   ├── templates/
│   │   └── protocols/            # JSON templates for all protocols
│   ├── utils/                    # Utility modules
│   │   ├── data_processor.py
│   │   ├── report_generator.py
│   │   ├── equipment_interface.py
│   │   └── traceability.py
│   ├── database/
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schema.sql            # Database schema
│   │   └── migrations/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── tests/                        # Test suite
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── genspark.config.json          # GenSpark configuration
└── README.md                     # This file
```

## 🧪 All 54 Protocols

### Performance Testing (12 Protocols)
| Protocol ID | Name | Standard | Duration |
|------------|------|----------|----------|
| STC-001 | Standard Test Conditions | IEC 61215-1:2021 | 2h |
| NOCT-001 | Nominal Operating Cell Temperature | IEC 61215-1:2021 | 4h |
| LIC-001 | Low Irradiance Conditions | IEC 61215-1:2021 | 3h |
| PERF-001 | Performance at Different Temperatures | IEC 61215-1:2021 | 5h |
| PERF-002 | Performance at Different Irradiances | IEC 61215-1:2021 | 4h |
| IAM-001 | Incidence Angle Modifier | IEC 61853-2:2016 | 6h |
| SPEC-001 | Spectral Response | IEC 60904-8:2014 | 8h |
| TEMP-001 | Temperature Coefficients | IEC 60891:2021 | 4h |
| ENER-001 | Energy Rating | IEC 61853-1:2011 | 12h |
| BIFI-001 | Bifacial Performance | IEC TS 60904-1-2:2019 | 5h |
| TRACK-001 | Tracker Performance | Custom | 8h |
| CONC-001 | Concentration Testing | IEC 62108:2016 | 6h |

### Degradation Testing (15 Protocols)
All degradation protocols are fully implemented with JSON templates and Python classes.

### Environmental Testing (12 Protocols)
All environmental protocols are fully implemented with JSON templates and Python classes.

### Mechanical Testing (8 Protocols)
All mechanical protocols are fully implemented with JSON templates and Python classes.

### Safety Testing (7 Protocols)
All safety protocols are fully implemented with JSON templates and Python classes.

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Service Requests
- `POST /api/service-requests` - Create new service request
- `POST /api/service-requests/{id}/protocols` - Add protocol to request
- `GET /api/service-requests/{id}/quote` - Generate quote

### Samples
- `POST /api/samples` - Register new sample
- `POST /api/samples/{id}/inspection` - Perform inspection

### Equipment
- `GET /api/equipment/{id}/availability` - Check availability
- `POST /api/bookings` - Create booking

### Protocol Execution
- `GET /api/protocols` - List available protocols
- `POST /api/executions` - Create test execution
- `POST /api/executions/{id}/start` - Start execution
- `GET /api/executions/{id}/status` - Get execution status
- `POST /api/executions/{id}/run` - Run complete protocol

## 🚢 Deployment

### Production Deployment with Docker

```bash
docker-compose up -d
```

All services will start automatically:
- PostgreSQL database
- Redis cache
- Flask application
- Celery workers
- Nginx reverse proxy

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- GenSpark LIMS Team

---

**Made with ❤️ for the PV Testing Community**
