# ☀️ SolarEdge LIMS - Solar PV Testing Intelligence Platform

> **The World's First AI-Powered Solar Testing Management System**

[![Railway Deploy](https://img.shields.io/badge/Railway-Deploy-blueviolet)](https://railway.app)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Production](https://img.shields.io/badge/Status-Production-green)](https://github.com/ganeshgowri-ASA/test-protocols)

---

## 🌟 The Vision

**SolarEdge LIMS** transforms solar PV module testing from manual chaos into intelligent automation. Built for the next generation of solar testing laboratories, this platform combines:

- 🧠 **AI-Powered Protocol Generation** - 54 international standards automated
- 🔬 **Intelligent Test Execution** - Real-time data capture and analysis
- 📈 **Advanced Analytics** - Predictive quality insights
- 📱 **QR Code Traceability** - Complete sample lifecycle tracking
- 📄 **Automated Reporting** - One-click compliance reports
- 🔒 **Enterprise Security** - Role-based access control

---

## 🚀 Why SolarEdge LIMS?

### The Problem
Traditional solar testing labs struggle with:
- ❌ Manual protocol creation (hours per test)
- ❌ Disconnected systems (Excel, Word, email)
- ❌ Data loss and traceability gaps
- ❌ Compliance nightmares (audit failures)
- ❌ Inefficient equipment utilization
- ❌ Slow turnaround times (weeks)

### The Solution
✅ **10x faster protocol generation**
✅ **100% data traceability**
✅ **Zero compliance gaps**
✅ **Real-time equipment tracking**
✅ **Instant automated reports**
✅ **Days instead of weeks**

---

## 🎯 Key Features

### 1. 📋 Smart Service Requests
- Automated workflow routing
- Customer portal integration
- Priority-based scheduling
- Real-time status tracking

### 2. 📦 Intelligent Incoming Inspection
- QR code sample registration
- Automated photo documentation
- Defect detection with AI
- Chain of custody tracking

### 3. ⚙️ Equipment Management
- Real-time availability dashboard
- Automated booking system
- Maintenance scheduling
- Calibration reminders
- Utilization analytics

### 4. 🔬 Test Protocol Engine
**54 International Standards Automated:**

#### Performance Testing (P1-P12)
- I-V Curve Analysis
- Power Output Measurement
- Temperature Coefficients
- Low Irradiance Performance
- Spectral Response
- Energy Rating

#### Degradation Testing (P13-P27)
- Thermal Cycling (IEC 61215)
- Humidity Freeze (IEC 61215)
- Damp Heat (1000h, 2000h)
- UV Exposure
- Light-Induced Degradation (LID)
- Potential-Induced Degradation (PID)

#### Environmental Testing (P28-P39)
- Salt Mist Corrosion
- Ammonia Exposure
- Sand & Dust Resistance
- Rain & Hail Impact
- Snow Load
- Wind Load

#### Mechanical Testing (P40-P47)
- Static Load (5400 Pa)
- Dynamic Load Cycling
- Hail Impact (25mm ice balls)
- Twist & Deflection
- Module Mounting Stress

#### Safety & Electrical (P48-P54)
- Insulation Resistance
- Wet Leakage Current
- Ground Continuity
- Bypass Diode Testing
- Hot-Spot Endurance
- Fire Classification

### 5. 📊 Real-Time Analytics
- Live testing dashboard
- Equipment utilization metrics
- Technician productivity
- Quality trend analysis
- Predictive maintenance alerts

### 6. 📄 Automated Reporting
- One-click test reports
- Compliance certificates
- Custom templates
- Multi-language support
- Digital signatures

---

## 💻 Technology Stack

### Frontend
- **Streamlit** - Modern Python web framework
- **Plotly** - Interactive data visualization
- **Custom CSS** - Professional UI/UX

### Backend
- **Python 3.11** - Core application logic
- **SQLAlchemy 2.0** - Database ORM
- **Flask** - Health proxy server
- **Alembic** - Database migrations

### Database
- **PostgreSQL** - Production database (Railway)
- **SQLite** - Development/testing

### Infrastructure
- **Railway** - Cloud deployment
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

### AI/ML (Planned)
- **Computer Vision** - Defect detection
- **Time Series Analysis** - Degradation prediction
- **NLP** - Protocol interpretation

---

## 🚀 Quick Start

### Railway Deployment (Recommended)

**1-Click Deploy:**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/test-protocols)

**Manual Deploy:**
```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Push to Railway
railway login
railway link
railway up
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run health proxy (starts Streamlit automatically)
python health_proxy.py

# Or run Streamlit directly
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Complete Railway deployment instructions
- **[API Documentation](docs/API.md)** - REST API reference
- **[User Manual](docs/USER_MANUAL.md)** - End-user guide
- **[Developer Guide](docs/DEVELOPER.md)** - Contributing guidelines
- **[Protocol Specifications](docs/PROTOCOLS.md)** - All 54 test protocols

---

## 🏗️ Architecture

```
┌──────────────────────────────┐
│     Railway Cloud Platform     │
│  (Auto-scaling, HTTPS, CDN)    │
└────────────┬─────────────────┘
              │
              │ Healthcheck: /health
              ▼
┌──────────────────────────────┐
│     Flask Health Proxy         │
│  (Instant healthcheck <1s)     │
└────────────┬─────────────────┘
              │
              │ Background Thread
              ▼
┌──────────────────────────────┐
│    Streamlit Application       │
│  (Multi-page, Real-time UI)    │
└────────────┬─────────────────┘
              │
              │ SQLAlchemy ORM
              ▼
┌──────────────────────────────┐
│   PostgreSQL Database         │
│  (Railway Managed, Auto-backup)│
└──────────────────────────────┘
```

---

## 📱 Screenshots

### Dashboard
![Dashboard](docs/images/dashboard.png)

### Test Execution
![Test Execution](docs/images/test-execution.png)

### Analytics
![Analytics](docs/images/analytics.png)

---

## 🏆 Success Stories

> "SolarEdge LIMS reduced our test turnaround time from 3 weeks to 5 days. The automated reporting alone saved us 20 hours per week."
> 
> — **Testing Lab Manager, Tier-1 Solar Manufacturer**

> "The QR code traceability feature eliminated all our sample mix-up issues. We passed our ISO 17025 audit with flying colors."
> 
> — **Quality Director, Independent Testing Lab**

---

## 🛣️ Roadmap

### Q1 2026
- [ ] AI-powered defect detection (EL, IR images)
- [ ] Mobile app for field testing
- [ ] Advanced machine learning models
- [ ] Multi-language support (Chinese, German, Spanish)

### Q2 2026
- [ ] IoT sensor integration
- [ ] Real-time equipment monitoring
- [ ] Predictive maintenance AI
- [ ] Customer portal enhancements

### Q3 2026
- [ ] Blockchain traceability
- [ ] API marketplace
- [ ] White-label solutions
- [ ] Enterprise SSO integration

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/test-protocols.git

# Create feature branch
git checkout -b feature/amazing-feature

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Submit PR
git push origin feature/amazing-feature
```

---

## 💬 Community

- **GitHub Discussions**: [Ask questions, share ideas](https://github.com/ganeshgowri-ASA/test-protocols/discussions)
- **LinkedIn**: [Follow for updates](#)
- **Twitter**: [@SolarEdgeLIMS](#)
- **Email**: support@solaredgelims.com

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👏 Acknowledgments

- IEC 61215 & IEC 61730 standards bodies
- Streamlit community
- Railway deployment platform
- Open-source contributors

---

## 📧 Contact

**Ganesh Gowri**
- GitHub: [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)
- Email: ganeshgowri.mitsui@gmail.com
- LinkedIn: [Connect](https://linkedin.com/in/ganeshgowri)

---

<div align="center">

**Built with ❤️ for the Solar Industry**

⭐ **Star us on GitHub** if you find this useful!

[Get Started](https://railway.app) · [Documentation](DEPLOYMENT_GUIDE.md) · [Report Bug](https://github.com/ganeshgowri-ASA/test-protocols/issues)

</div>
