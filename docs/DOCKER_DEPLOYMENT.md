# Docker Deployment Guide

## Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check status
docker-compose ps

# Access application
# Dashboard: http://localhost:8501
# API: http://localhost:8000
```

## Docker Compose Configuration

The `docker-compose.yml` file defines 6 services:

1. **postgres** - PostgreSQL database
2. **redis** - Cache and session storage
3. **api** - FastAPI backend
4. **celery_worker** - Background task processing
5. **streamlit** - Web dashboard
6. **nginx** - Reverse proxy and load balancer

## Environment Variables

Edit `.env` file:

```bash
# Database
DB_PASSWORD=your_secure_password

# API
SECRET_KEY=your_secret_key_here

# External Integrations (optional)
LIMS_API_KEY=
QMS_API_URL=
PM_API_TOKEN=
```

## Individual Service Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api python manage.py --help
```

## Database Initialization

```bash
# Run database migrations
docker-compose exec api python manage.py db upgrade

# Load initial data
docker-compose exec api python manage.py load_fixtures

# Create admin user
docker-compose exec api python manage.py create_user \
    --username admin \
    --email admin@company.com \
    --role admin
```

## Production Deployment

### 1. Use Production-Ready Images

Build optimized production images:

```bash
docker build -f deploy/docker/Dockerfile.prod -t pvtesting/framework:1.0 .
```

### 2. Enable HTTPS

Configure SSL certificates in `deploy/nginx/ssl/`:

```bash
# Copy certificates
cp /path/to/cert.pem deploy/nginx/ssl/
cp /path/to/key.pem deploy/nginx/ssl/

# Update nginx config
nano deploy/nginx/nginx.conf
```

### 3. Configure External Database

For production, use external managed database:

```yaml
# docker-compose.prod.yml
services:
  api:
    environment:
      DATABASE_URL: postgresql://user:pass@external-db-host:5432/pv_testing
```

### 4. Resource Limits

Set resource limits:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Monitoring and Logging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Health Checks

```bash
# Check service health
docker-compose ps

# API health endpoint
curl http://localhost:8000/health
```

## Backup and Restore

### Backup Database

```bash
docker-compose exec postgres pg_dump -U pv_user pv_testing > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U pv_user pv_testing
```

### Backup Volumes

```bash
docker run --rm -v pv_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/pv_data_backup.tar.gz -C /data .
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Remove old containers
docker-compose down -v
docker-compose up -d
```

### Database Connection Errors

```bash
# Verify postgres is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec api python -c "from pv_testing.db import engine; print(engine)"
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
