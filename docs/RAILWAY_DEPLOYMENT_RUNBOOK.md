# Railway Deployment Runbook
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Last Updated:** November 2024
**Target Platform:** Railway.app

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Initial Setup](#2-initial-setup)
3. [Environment Configuration](#3-environment-configuration)
4. [Database Setup](#4-database-setup)
5. [Deployment Steps](#5-deployment-steps)
6. [Post-Deployment Verification](#6-post-deployment-verification)
7. [Scaling Configuration](#7-scaling-configuration)
8. [Monitoring Setup](#8-monitoring-setup)
9. [Rollback Procedures](#9-rollback-procedures)
10. [Cost Optimization](#10-cost-optimization)

---

## 1. Prerequisites

### 1.1 Accounts Required
- [ ] Railway account (https://railway.app)
- [ ] GitHub account (for repository)
- [ ] (Optional) Custom domain provider

### 1.2 Local Tools
```bash
# Install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version

# Login to Railway
railway login
```

### 1.3 Repository Requirements
- [ ] `requirements.txt` - Python dependencies
- [ ] `Procfile` or `railway.toml` - Process configuration
- [ ] `.env.example` - Environment variable template

---

## 2. Initial Setup

### 2.1 Create Railway Project

```bash
# Create new project
railway init

# Or link to existing project
railway link
```

### 2.2 Create railway.toml Configuration

```toml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[service]
internalPort = 8501
```

### 2.3 Create Procfile (Alternative)

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

---

## 3. Environment Configuration

### 3.1 Required Environment Variables

Set these in Railway Dashboard → Variables:

```bash
# Database (Auto-set by Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Application Settings
ENVIRONMENT=production
APP_VERSION=1.0.0
SECRET_KEY=<generate-secure-key>

# Security
SESSION_SECRET_KEY=<generate-secure-key>
TOKEN_EXPIRY_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 3.2 Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate SESSION_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3.3 Railway-Specific Variables (Auto-Set)

These are automatically available in Railway:
- `RAILWAY_ENVIRONMENT` - Current environment name
- `RAILWAY_SERVICE_NAME` - Service name
- `RAILWAY_DEPLOYMENT_ID` - Unique deployment ID
- `PORT` - Assigned port number

---

## 4. Database Setup

### 4.1 Add PostgreSQL Service

1. Go to Railway Dashboard
2. Click "New Service" → "Database" → "Add PostgreSQL"
3. Railway auto-provisions and links DATABASE_URL

### 4.2 Database Configuration

```bash
# Verify connection (Railway CLI)
railway run python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
print('Database connected successfully!')
"
```

### 4.3 Initialize Database Tables

```bash
# Run initialization
railway run python -c "
from infrastructure.database import get_db_manager
db = get_db_manager()
db.init_db()
print('Database initialized!')
"
```

### 4.4 Database Migration (Using Alembic)

```bash
# Generate migration
railway run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
railway run alembic upgrade head
```

---

## 5. Deployment Steps

### 5.1 Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database provisioned and connected
- [ ] Local tests passing
- [ ] Security scan completed
- [ ] Dependencies frozen in requirements.txt

### 5.2 Deploy via CLI

```bash
# Deploy current directory
railway up

# Deploy specific branch
railway up --branch main

# Deploy with environment
railway up --environment production
```

### 5.3 Deploy via GitHub Integration

1. Connect GitHub repository in Railway Dashboard
2. Enable automatic deployments on push
3. Configure branch triggers:
   - `main` → staging
   - `production` → production

### 5.4 Deployment Verification

```bash
# Check deployment status
railway status

# View logs
railway logs

# Open deployed app
railway open
```

---

## 6. Post-Deployment Verification

### 6.1 Health Check Verification

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Expected response:
{
  "status": "healthy",
  "checks": [...],
  "uptime_seconds": 123
}
```

### 6.2 Functionality Verification

- [ ] Home page loads correctly
- [ ] Service Request page accessible
- [ ] Database queries working
- [ ] User authentication functional
- [ ] All 54 protocols visible

### 6.3 Performance Baseline

```bash
# Response time check
time curl -s https://your-app.railway.app > /dev/null

# Target: < 2 seconds for initial load
```

---

## 7. Scaling Configuration

### 7.1 Horizontal Scaling

Railway supports automatic scaling based on load:

```yaml
# In railway.toml
[deploy]
numReplicas = 2  # Multiple instances
```

### 7.2 Vertical Scaling

Adjust resources in Railway Dashboard:

| Tier | vCPU | RAM | Recommended For |
|------|------|-----|-----------------|
| Starter | 0.5 | 512MB | Development |
| Pro | 2 | 2GB | Small production |
| Team | 4 | 8GB | Enterprise |

### 7.3 Database Scaling

```sql
-- Monitor connection count
SELECT count(*) FROM pg_stat_activity;

-- Recommended pool settings by traffic:
-- Low: pool_size=5, max_overflow=10
-- Medium: pool_size=10, max_overflow=20
-- High: pool_size=20, max_overflow=40
```

---

## 8. Monitoring Setup

### 8.1 Railway Native Monitoring

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network I/O
- Request count

### 8.2 Application-Level Monitoring

The infrastructure module provides:

```python
from infrastructure.monitoring import health_checker, metrics_collector

# Get health status
status = health_checker.get_full_status()

# Get metrics
metrics = metrics_collector.get_all_metrics()
```

### 8.3 Log Aggregation

```bash
# View live logs
railway logs -f

# Filter by level
railway logs | grep ERROR
```

### 8.4 Alert Configuration

Set up alerts for:
- [ ] Error rate > 5%
- [ ] Response time > 5s
- [ ] Memory usage > 80%
- [ ] Database connections > 80%

---

## 9. Rollback Procedures

### 9.1 Quick Rollback

```bash
# List deployments
railway deployments

# Rollback to previous
railway rollback
```

### 9.2 Specific Version Rollback

1. Go to Railway Dashboard → Deployments
2. Find the target deployment
3. Click "Redeploy"

### 9.3 Database Rollback

```bash
# Rollback last migration
railway run alembic downgrade -1

# Rollback to specific revision
railway run alembic downgrade <revision_id>
```

### 9.4 Emergency Procedures

```bash
# Stop service immediately
railway service stop

# View error logs
railway logs --error

# Restart service
railway service restart
```

---

## 10. Cost Optimization

### 10.1 Railway Pricing Overview

| Resource | Pricing |
|----------|---------|
| Compute | $0.000463/vCPU/minute |
| Memory | $0.000231/GB/minute |
| Network | $0.10/GB egress |
| Storage | $0.25/GB/month |

### 10.2 Optimization Strategies

1. **Right-size resources**: Start small, scale as needed
2. **Use sleep mode**: For non-production environments
3. **Optimize queries**: Reduce database load
4. **Enable caching**: Reduce repeated computations
5. **Compress responses**: Reduce network transfer

### 10.3 Resource Limits

```toml
# railway.toml
[deploy]
# Set memory limit (prevents runaway costs)
memoryLimit = "512Mi"

# CPU limit
cpuLimit = "1000m"  # 1 vCPU
```

### 10.4 Estimated Monthly Costs

| Workload | Compute | Database | Total |
|----------|---------|----------|-------|
| Development | $5 | $5 | ~$10/mo |
| Small Production | $20 | $15 | ~$35/mo |
| Medium Production | $50 | $50 | ~$100/mo |
| Enterprise | $200+ | $200+ | $400+/mo |

---

## Quick Reference Commands

```bash
# Deploy
railway up

# View logs
railway logs -f

# Run command
railway run <command>

# Open app
railway open

# Check status
railway status

# Rollback
railway rollback

# Environment variables
railway variables
railway variables set KEY=value

# Connect to database
railway connect postgres
```

---

## Support Resources

- Railway Documentation: https://docs.railway.app
- Railway Status: https://status.railway.app
- Community Discord: https://discord.gg/railway

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 2024 | System | Initial release |
