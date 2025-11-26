# Deployment Guide - Solar PV Testing LIMS-QMS System

This guide covers deployment options for the Solar PV Testing LIMS-QMS application.

## Multi-Platform Support

The application automatically detects and configures for these platforms:
- **Railway** (Recommended - $5/month free credits)
- **Streamlit Cloud** (Free)
- **Replit** (Free tier available)
- **GenSpark**
- **Local Development**

---

## Table of Contents

1. [Railway Deployment (Recommended)](#railway-deployment-recommended)
2. [Rollback Mechanism](#rollback-mechanism)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Security Considerations](#security-considerations)
8. [Backup and Recovery](#backup-and-recovery)

---

## Railway Deployment (Recommended)

Railway offers $5/month free credits - ideal for cost-effective production deployment.

### Quick Start (5 Minutes)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```
   1. Click "New Project"
   2. Select "Deploy from GitHub repo"
   3. Choose: ganeshgowri-ASA/test-protocols
   4. Railway auto-detects Streamlit and deploys
   ```

3. **Add PostgreSQL Database**
   ```
   1. In your project, click "New"
   2. Select "Database" -> "Add PostgreSQL"
   3. Railway automatically sets DATABASE_URL
   ```

4. **Configure Domain**
   ```
   1. Go to your service settings
   2. Under "Networking", generate a domain
   3. Your app is live at: https://your-app.railway.app
   ```

### Cost Optimization ($4.98 Budget)

The application is pre-configured for minimal resource usage:

| Setting | Value | Purpose |
|---------|-------|---------|
| Pool Size | 3 | Minimal DB connections |
| Max Overflow | 5 | Limited connection burst |
| Pool Recycle | 1800s | Prevent connection leaks |

**Estimated Monthly Cost:**
- Web Service: ~$2-3 (based on usage)
- PostgreSQL: ~$1-2 (minimal tier)
- **Total: ~$3-5/month**

### Railway Environment Variables

Railway automatically sets these when you add PostgreSQL:
- `DATABASE_URL` or `POSTGRES_URL`
- `DATABASE_PRIVATE_URL` (for internal networking)

**Optional variables:**
```
FORCE_SQLITE=1          # Emergency rollback to SQLite
DB_ECHO=true            # SQL query logging (debugging)
SESSION_SECRET_KEY=xxx  # Custom session secret
```

---

## Rollback Mechanism

### Instant Rollback to SQLite

If PostgreSQL has issues, you can instantly rollback:

**Method 1: Environment Variable**
```bash
# In Railway dashboard, add variable:
FORCE_SQLITE=1

# Then restart the service
```

**Method 2: Use backup branch**
```bash
# The backup branch preserves working state:
git checkout preserve/working-app-backup-main
```

### Rollback Decision Matrix

| Scenario | Action |
|----------|--------|
| PostgreSQL connection issues | Set `FORCE_SQLITE=1` |
| Data corruption | Restore from Railway backup |
| Complete failure | Deploy from backup branch |
| Cost overrun | Set `FORCE_SQLITE=1` (free tier) |

---

## Platform Comparison

| Feature | Railway | Streamlit Cloud | Replit | GenSpark |
|---------|---------|-----------------|--------|----------|
| Free Tier | $5/month credits | Yes | Yes | Varies |
| PostgreSQL | Built-in | External only | External only | Varies |
| Custom Domain | Yes | Yes | Paid | Yes |
| Persistent Storage | Yes | No | Paid | Yes |
| Recommended For | Production | Demo/Testing | Prototyping | Custom |

---

## Local Development

### Prerequisites
- Python 3.9+
- pip
- Virtual environment tool

### Steps

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python -c "from config.database import init_database; init_database()"

# Run application
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## Production Deployment

### System Requirements

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 20 GB storage

**Recommended:**
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB SSD storage

### Production Setup

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash solarpv
sudo usermod -aG sudo solarpv
```

#### 2. Application Setup

```bash
# Switch to application user
sudo su - solarpv

# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # If using gunicorn instead of streamlit server
```

#### 3. Database Setup (PostgreSQL)

```bash
# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE solar_pv_lims;
CREATE USER solarpv_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE solar_pv_lims TO solarpv_user;
\q
```

Update `.env`:
```bash
DATABASE_URL=postgresql://solarpv_user:strong_password_here@localhost:5432/solar_pv_lims
```

#### 4. Supervisor Configuration

Create `/etc/supervisor/conf.d/solarpv-lims.conf`:

```ini
[program:solarpv-lims]
directory=/home/solarpv/test-protocols
command=/home/solarpv/test-protocols/venv/bin/streamlit run app.py --server.port=8501 --server.address=localhost
user=solarpv
autostart=true
autorestart=true
stderr_logfile=/var/log/solarpv-lims.err.log
stdout_logfile=/var/log/solarpv-lims.out.log
environment=
    PATH="/home/solarpv/test-protocols/venv/bin",
    DATABASE_URL="postgresql://solarpv_user:password@localhost:5432/solar_pv_lims"
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start solarpv-lims
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/solarpv-lims`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/solarpv-lims /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

---

## Docker Deployment

### Quick Start

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Docker Setup

#### 1. Build Image

```bash
docker build -t solarpv-lims:1.0.0 .
```

#### 2. Run with Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    image: solarpv-lims:1.0.0
    container_name: solarpv-lims-prod
    ports:
      - "8501:8501"
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/solar_pv_lims
      - SESSION_SECRET_KEY=${SESSION_SECRET_KEY}
    volumes:
      - app-data:/app/data
      - app-logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: solarpv-db-prod
    environment:
      POSTGRES_DB: solar_pv_lims
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: solarpv-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  app-data:
  app-logs:
  postgres-data:
```

```bash
# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (or larger)
   - Storage: 30 GB SSD

2. **Configure Security Groups**
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)

3. **Follow Production Setup** steps above

#### Option 2: ECS/Fargate

1. **Push Docker Image to ECR**

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag solarpv-lims:1.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/solarpv-lims:1.0.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/solarpv-lims:1.0.0
```

2. **Create ECS Task Definition**
3. **Deploy to Fargate**

#### Option 3: Elastic Beanstalk

```bash
# Initialize
eb init -p docker solar-pv-lims

# Create environment
eb create solarpv-lims-prod

# Deploy
eb deploy
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/solarpv-lims

# Deploy
gcloud run deploy solarpv-lims \
  --image gcr.io/PROJECT_ID/solarpv-lims \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure

#### Container Instances

```bash
# Create resource group
az group create --name solarpv-rg --location eastus

# Deploy container
az container create \
  --resource-group solarpv-rg \
  --name solarpv-lims \
  --image solarpv-lims:1.0.0 \
  --dns-name-label solarpv-lims \
  --ports 8501
```

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from GitHub repository
4. Configure secrets in Streamlit Cloud dashboard

---

## Security Considerations

### 1. Environment Variables

```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update `.env`:
```bash
SESSION_SECRET_KEY=<generated-key>
```

### 2. Database Security

```sql
-- Use strong passwords
-- Limit database access
CREATE USER solarpv_user WITH PASSWORD 'strong_random_password_here_12345678';

-- Grant minimal privileges
GRANT CONNECT ON DATABASE solar_pv_lims TO solarpv_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO solarpv_user;
```

### 3. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Regular Updates

```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Application updates
cd /home/solarpv/test-protocols
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo supervisorctl restart solarpv-lims
```

---

## Backup and Recovery

### Database Backup

#### Automated Daily Backups

Create `/home/solarpv/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/solarpv/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/solar_pv_lims_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

pg_dump -U solarpv_user -h localhost solar_pv_lims > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

```bash
# Make executable
chmod +x /home/solarpv/backup-db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/solarpv/backup-db.sh
```

#### Restore from Backup

```bash
# Uncompress
gunzip solar_pv_lims_20240101_020000.sql.gz

# Restore
psql -U solarpv_user -h localhost solar_pv_lims < solar_pv_lims_20240101_020000.sql
```

### Application Backup

```bash
# Backup data directory
tar -czf solar_pv_data_backup.tar.gz /home/solarpv/test-protocols/data/

# Backup to S3 (AWS)
aws s3 cp solar_pv_data_backup.tar.gz s3://your-backup-bucket/
```

---

## Monitoring

### Application Logs

```bash
# Streamlit logs
tail -f /var/log/solarpv-lims.out.log

# Error logs
tail -f /var/log/solarpv-lims.err.log
```

### System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor resources
htop
```

### Health Checks

```bash
# Check application
curl http://localhost:8501/_stcore/health

# Check database
psql -U solarpv_user -h localhost -d solar_pv_lims -c "SELECT 1;"
```

---

## Troubleshooting

### Common Issues

#### Application won't start
```bash
# Check supervisor status
sudo supervisorctl status solarpv-lims

# Check logs
tail -100 /var/log/solarpv-lims.err.log
```

#### Database connection errors
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U solarpv_user -h localhost -d solar_pv_lims
```

#### Performance issues
```bash
# Check resources
htop

# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Optimize database
VACUUM ANALYZE;
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check disk space
- Review system metrics

**Weekly:**
- Review backup logs
- Check database size
- Update dependencies

**Monthly:**
- System updates
- Security patches
- Performance review
- Backup testing

---

## Support

For deployment issues:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Email: support@solarpv.com
- Documentation: https://github.com/ganeshgowri-ASA/test-protocols/wiki

---

**Last Updated:** 2024
