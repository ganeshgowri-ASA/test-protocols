# Installation Guide

## Quick Start

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Run automated setup
chmod +x deploy/setup.sh
./deploy/setup.sh

# Start services
./deploy/start_services.sh

# Access dashboard at http://localhost:8501
```

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, or Windows 10+ with WSL2
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 50GB available space
- **Network**: Internet connection for initial setup

### Software Dependencies
- Python 3.8 or higher
- PostgreSQL 12+ (or SQLite for development)
- Redis 6+ (optional, for caching)
- Docker 20.10+ (optional, for containerized deployment)
- Node.js 14+ (for documentation generation)

## Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Download and run setup script
curl -sSL https://raw.githubusercontent.com/ganeshgowri-ASA/test-protocols/main/deploy/setup.sh | bash
```

### Method 2: Manual Installation

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3.8 python3-pip python3-venv \
    postgresql postgresql-contrib redis-server \
    libpq-dev build-essential
```

**macOS:**
```bash
brew install python@3.8 postgresql redis
brew services start postgresql
brew services start redis
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

#### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Database Setup

```bash
# Create database
createdb pv_testing

# Run migrations
python manage.py db upgrade

# Load initial data
python manage.py load_fixtures
```

#### Step 6: Configuration

```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit configuration
nano config/config.yaml
```

#### Step 7: Start Application

```bash
# Start API server
python -m pv_testing.api &

# Start Streamlit dashboard
streamlit run streamlit_app.py
```

### Method 3: Docker Installation

```bash
# Build and start containers
docker-compose up -d

# Access at http://localhost:8501
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pv_testing

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# External Integrations
LIMS_API_KEY=your-lims-key
QMS_API_URL=https://qms.company.com
PM_API_TOKEN=your-pm-token

# Storage
FILE_STORAGE_PATH=/data/pv_testing
S3_BUCKET=pv-testing-data

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration

Edit `config/database.yaml`:

```yaml
database:
  engine: postgresql
  host: localhost
  port: 5432
  database: pv_testing
  username: pv_user
  password: ${DB_PASSWORD}
  pool_size: 10
  max_overflow: 20
```

## Post-Installation

### Create Admin User

```bash
python manage.py create_user \
    --username admin \
    --email admin@company.com \
    --role admin \
    --password
```

### Load Protocol Templates

```bash
python manage.py load_protocols --path templates/protocols/
```

### Verify Installation

```bash
# Run health check
python manage.py health_check

# Run test suite
pytest tests/
```

## Upgrading

```bash
# Backup database
pg_dump pv_testing > backup_$(date +%Y%m%d).sql

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py db upgrade

# Restart services
./deploy/restart_services.sh
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
