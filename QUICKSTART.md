# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run Home.py
```

Open your browser to `http://localhost:8501`

### 3. Explore the Dashboard

#### Home Page
- Overview of all features
- Quick statistics
- Navigation links

#### Master Dashboard (`pages/Dashboard.py`)
- Real-time protocol status
- Equipment utilization
- Service requests
- Notifications

#### Data Traceability (`pages/Traceability.py`)
- Search by ID (e.g., SR-2024001)
- View complete audit trail
- Export traceability reports

#### KPI Dashboard (`pages/KPI_Dashboard.py`)
- Performance metrics
- Trend analysis
- Quality metrics
- Resource utilization

#### Reports (`pages/Reports.py`)
- Generate quick reports
- Build custom reports
- Schedule automated reports
- Configure distribution

### 4. Use the API (Optional)

```bash
# Start the API server
python api/analytics.py
```

Test the API:
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get statistics
curl http://localhost:5000/api/v1/statistics

# Search
curl http://localhost:5000/api/v1/search?q=SR-2024001
```

### 5. Sample Data

The application comes with pre-generated sample data including:
- 20 service requests
- 100+ protocols
- 20 equipment units
- 30 days of KPI metrics
- Real-time notifications

### Common Use Cases

#### 1. Track a Service Request
1. Go to **Traceability** page
2. Enter service request ID (e.g., `SR-2024001`)
3. View complete journey from request to report

#### 2. Monitor Protocol Performance
1. Go to **Master Dashboard**
2. View real-time protocol status
3. Check completion rates and QC results

#### 3. Analyze KPIs
1. Go to **KPI Dashboard**
2. Select time period (7, 30, or 90 days)
3. View trends and performance metrics

#### 4. Generate Reports
1. Go to **Reports** page
2. Choose report type (Executive, Protocol, QC, Equipment)
3. Select format (PDF, Excel, CSV)
4. Download or schedule for email

### Customization

#### Change Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"  # Change to your color
```

#### Configure KPI Targets
Edit `config/config.py`:
```python
TAT_TARGET_HOURS = 48
PASS_RATE_TARGET = 95.0
```

#### Add Custom Protocols
Edit `utils/data_generator.py` to add your protocol names and types.

### Troubleshooting

**Port already in use?**
```bash
streamlit run Home.py --server.port 8502
```

**Missing dependencies?**
```bash
pip install -r requirements.txt --upgrade
```

**Data not loading?**
- Refresh the page (F5)
- Clear cache from sidebar
- Check console for errors

### Next Steps

- Explore all dashboard pages
- Try the search and filter features
- Generate sample reports
- Integrate with your LIMS/QMS system
- Configure automated notifications

### Need Help?

- Check the main README.md for detailed documentation
- View API documentation in `api/analytics.py`
- Open an issue on GitHub

---

**Ready to go?** Start with `streamlit run Home.py` and explore! 🚀
