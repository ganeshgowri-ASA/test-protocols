# Quick Start Guide - PV Testing Protocol Framework

## ⚡ Get Started in 5 Minutes

### Step 1: Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/your-org/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize System (1 minute)

```bash
# Initialize database and configuration
python src/master_orchestrator.py --init

# Verify installation
python src/master_orchestrator.py --status
```

Expected output:
```json
{
  "protocols_loaded": 54,
  "active_tests": 0,
  "modules": {
    "dashboard": true,
    "traceability": true,
    "project_mgmt": true,
    "qms_lims": true,
    "continuous_improvement": true
  },
  "database": "healthy"
}
```

### Step 3: Launch Dashboard (1 minute)

```bash
# Launch the master dashboard
python src/master_orchestrator.py --dashboard
```

Open your browser to: **http://localhost:8501**

### Step 4: Execute Your First Protocol (1 minute)

#### Option A: Using the Dashboard
1. Navigate to "Protocol Status" tab
2. Click on "PVTP-048: Energy Rating & Bankability"
3. Fill in sample information
4. Click "Start Test"
5. View real-time results

#### Option B: Using Python API

```python
from src.master_orchestrator import MasterOrchestrator

# Initialize
orchestrator = MasterOrchestrator()

# Execute PVTP-048
result = orchestrator.execute_protocol(
    protocol_id='PVTP-048',
    sample_id='QUICK-START-001',
    test_data={
        'manufacturer': 'Quick Start Demo',
        'model': 'QS-400W',
        'nameplate_power': 400,
        'technology': 'Mono-Si',
        'manufacturer_data': {
            'tier': 1,
            'years_operation': 10,
            'production_capacity_gw': 2.5,
            'certifications': ['IEC 61215', 'IEC 61730'],
            'product_warranty_years': 12,
            'performance_warranty_years': 25,
            'degradation_guarantee': 0.50
        }
    },
    user_id='quickstart@lab.com'
)

# View results
print(f"Status: {result['status']}")
print(f"Session ID: {result['session_id']}")
```

---

## 🎯 Common Tasks

### Execute a Warranty Claim Test (PVTP-049)

```python
result = orchestrator.execute_protocol(
    protocol_id='PVTP-049',
    sample_id='CLAIM-2025-001',
    test_data={
        'claim_number': 'WC-2025-001',
        'failure_type': 'Delamination',
        'warranty_type': 'performance',
        'installation_date': '2020-01-15',
        'failure_date': '2025-01-10',
        'visual_inspection': {...},
        'electrical_testing': {...}
    },
    user_id='analyst@lab.com'
)
```

### Compare Multiple Manufacturers (PVTP-050)

```python
result = orchestrator.execute_protocol(
    protocol_id='PVTP-050',
    sample_id='COMPARE-2025-001',
    test_data={
        'manufacturers': [
            {'name': 'Mfg A', 'model': 'A-400W', 'samples': 6},
            {'name': 'Mfg B', 'model': 'B-405W', 'samples': 6},
            {'name': 'Mfg C', 'model': 'C-410W', 'samples': 6}
        ],
        'test_conditions': 'STC',
        'performance_metrics': ['pmax', 'efficiency', 'fill_factor']
    },
    user_id='analyst@lab.com'
)
```

### Run Partial Shading Analysis (PVTP-052)

```python
result = orchestrator.execute_protocol(
    protocol_id='PVTP-052',
    sample_id='SHADE-2025-001',
    test_data={
        'shading_patterns': [
            'single_cell',
            'partial_row',
            'corner_shading',
            'diagonal'
        ],
        'baseline_power': 400,
        'thermal_imaging': True
    },
    user_id='analyst@lab.com'
)
```

---

## 📊 View Results

### In Dashboard
1. Go to "Analytics" tab
2. Select your test session
3. View charts, tables, and reports
4. Download PDF report

### Via API

```python
# Get test results
from src.master_orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()

# Query by session ID
session_id = 'TEST-20250115103000-PVTP-048'
results = orchestrator.get_test_results(session_id)

print(results['summary'])
print(results['pass_fail'])
print(results['violations'])
```

---

## 🔍 Monitor System

### Dashboard Overview
- Real-time test status
- KPI metrics
- Active alerts
- Resource utilization

### Command Line

```bash
# System status
python src/master_orchestrator.py --status

# Protocol statistics
python src/master_orchestrator.py --protocol-stats PVTP-048

# Active tests
python src/master_orchestrator.py --active-tests
```

---

## ⚙️ Configuration

### Basic Configuration

Edit `config/master_config.json`:

```json
{
  "database_path": "./data/master.db",
  "log_level": "INFO",
  "max_concurrent_tests": 10,
  "enable_notifications": true
}
```

### Email Notifications

Edit `config/alerts.json`:

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "recipients": ["alerts@lab.com"]
  }
}
```

---

## 🚀 Next Steps

### 1. Explore All Protocols
- Browse `protocols/` directory
- Read protocol specifications
- Review acceptance criteria

### 2. Customize for Your Lab
- Configure equipment integration
- Set up user accounts
- Define workflow approvals

### 3. Production Deployment
- Set up PostgreSQL database
- Configure web server (Nginx)
- Enable SSL/TLS
- Set up backup automation

### 4. Training
- Review protocol guides in `docs/protocols/`
- Watch tutorial videos
- Schedule hands-on training

---

## 📚 Resources

- **Full Documentation:** `docs/MASTER_README.md`
- **Project Index:** `PROJECT_INDEX.md`
- **API Reference:** `docs/api/`
- **Examples:** `examples/`

---

## ❓ Troubleshooting

### Dashboard Won't Start

```bash
# Check if port 8501 is in use
netstat -an | grep 8501

# Use different port
streamlit run integrations/dashboard/master_dashboard.py --server.port 8502
```

### Database Error

```bash
# Reinitialize database
python src/master_orchestrator.py --init-db --force
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Support

**Issues:** Create GitHub issue
**Email:** support@pvtestinglab.com
**Docs:** `docs/`

---

## ✅ Checklist

- [ ] Installation complete
- [ ] System initialized
- [ ] Dashboard accessible
- [ ] First protocol executed
- [ ] Results reviewed
- [ ] Configuration customized
- [ ] Ready for production use

---

**Quick Start Guide Version:** 1.0.0
**Last Updated:** January 15, 2025

🎉 **Congratulations! You're ready to start testing!**
