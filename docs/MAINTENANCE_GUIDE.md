# Maintenance Guide
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Last Updated:** November 2024

---

## Table of Contents

1. [Daily Operations](#1-daily-operations)
2. [Weekly Maintenance](#2-weekly-maintenance)
3. [Monthly Tasks](#3-monthly-tasks)
4. [Database Maintenance](#4-database-maintenance)
5. [Performance Tuning](#5-performance-tuning)
6. [Security Maintenance](#6-security-maintenance)
7. [Backup Procedures](#7-backup-procedures)
8. [Incident Response](#8-incident-response)
9. [Update Procedures](#9-update-procedures)

---

## 1. Daily Operations

### 1.1 Morning Health Check

```bash
# Check system status
curl https://your-app.railway.app/health | jq .

# Verify database connectivity
railway run python -c "
from infrastructure.database import connection_health_check
print(connection_health_check())
"

# Check error logs from last 24h
railway logs --since 24h | grep -i error | tail -20
```

### 1.2 Key Metrics to Monitor

| Metric | Target | Critical |
|--------|--------|----------|
| Response Time | < 500ms | > 2000ms |
| Error Rate | < 1% | > 5% |
| Memory Usage | < 70% | > 90% |
| CPU Usage | < 60% | > 85% |
| DB Connections | < 80% | > 95% |

### 1.3 Daily Checklist

- [ ] Review error logs
- [ ] Check health endpoints
- [ ] Verify backup completion
- [ ] Monitor active users
- [ ] Review pending service requests

---

## 2. Weekly Maintenance

### 2.1 Performance Review

```python
# Get performance metrics
from infrastructure.monitoring import performance_monitor

summary = performance_monitor.get_summary()
print(f"Total Requests: {summary['requests']['total']}")
print(f"Error Rate: {summary['errors']}")
print(f"Avg Response Time: {summary['requests']['duration']['avg']}ms")
```

### 2.2 Database Statistics

```sql
-- Table sizes
SELECT
    schemaname || '.' || tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;

-- Slow queries
SELECT
    query,
    calls,
    mean_time,
    total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 2.3 Log Analysis

```bash
# Error summary
railway logs --since 7d | grep -i error | sort | uniq -c | sort -rn | head -20

# Warning summary
railway logs --since 7d | grep -i warning | sort | uniq -c | sort -rn | head -10
```

### 2.4 Weekly Tasks

- [ ] Review weekly metrics report
- [ ] Update dependencies if needed
- [ ] Test backup restoration
- [ ] Review user access logs
- [ ] Clean up temp files/uploads

---

## 3. Monthly Tasks

### 3.1 Dependency Updates

```bash
# Check outdated packages
pip list --outdated

# Update requirements
pip install --upgrade -r requirements.txt

# Verify no breaking changes
python -m pytest tests/
```

### 3.2 Security Review

```bash
# Run security audit
pip install safety
safety check -r requirements.txt

# Run bandit security scan
pip install bandit
bandit -r . -x ./tests,./venv
```

### 3.3 Database Optimization

```sql
-- Reindex tables
REINDEX DATABASE solar_pv_lims;

-- Update statistics
ANALYZE VERBOSE;

-- Vacuum to reclaim space
VACUUM ANALYZE;
```

### 3.4 Monthly Tasks

- [ ] Full security audit
- [ ] Dependency updates
- [ ] Performance baseline comparison
- [ ] Database maintenance
- [ ] Certificate renewal check
- [ ] Disaster recovery drill

---

## 4. Database Maintenance

### 4.1 Connection Pool Management

```python
from infrastructure.database import get_db_manager

db = get_db_manager()

# Get pool status
pool_stats = db.get_pool_stats()
print(f"Active connections: {pool_stats['checked_out']}")
print(f"Available: {pool_stats['checked_in']}")
print(f"Pool size: {pool_stats['size']}")

# Health check
health = db.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health['latency_ms']}ms")
```

### 4.2 Query Performance

```sql
-- Identify missing indexes
SELECT
    schemaname || '.' || relname AS table,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    seq_tup_read / NULLIF(seq_scan, 0) AS avg_seq_tuples
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;

-- Unused indexes
SELECT
    schemaname || '.' || relname || '.' || indexrelname AS index,
    idx_scan AS scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 4.3 Data Archival

```python
from datetime import datetime, timedelta
from infrastructure.database import db_session

# Archive old audit logs (older than 90 days)
cutoff_date = datetime.utcnow() - timedelta(days=90)

with db_session() as session:
    # Export to archive table/file first
    old_logs = session.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).all()

    # Then delete
    session.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).delete()
```

---

## 5. Performance Tuning

### 5.1 Application-Level Tuning

```python
# Cache configuration
import os

# Adjust based on traffic
os.environ['CACHE_DEFAULT_TTL'] = '600'  # 10 minutes
os.environ['CACHE_MAX_SIZE'] = '2000'    # items

# Database pool tuning
os.environ['DB_POOL_SIZE'] = '15'
os.environ['DB_MAX_OVERFLOW'] = '30'
```

### 5.2 Streamlit Optimization

```python
# config/.streamlit/config.toml
[server]
maxUploadSize = 100
maxMessageSize = 100
enableStaticServing = true

[browser]
gatherUsageStats = false

[runner]
fastReruns = true
```

### 5.3 Query Optimization

```python
from infrastructure.database import QueryOptimizer

# Use pagination for large queries
results = QueryOptimizer.paginate(
    session.query(TestExecution),
    page=1,
    per_page=50
).all()

# Use batching for bulk inserts
QueryOptimizer.batch_insert(session, large_list, batch_size=500)

# Stream large results
for batch in QueryOptimizer.stream_results(query, batch_size=1000):
    process(batch)
```

---

## 6. Security Maintenance

### 6.1 Access Review

```python
from infrastructure.database import db_session
from database.models import User, AuditLog

# Review user access
with db_session() as session:
    # Users not logged in for 90 days
    inactive_users = session.query(User).filter(
        User.last_login < datetime.utcnow() - timedelta(days=90)
    ).all()

    for user in inactive_users:
        print(f"Inactive user: {user.username} - Last login: {user.last_login}")
```

### 6.2 Password Policy Enforcement

```python
from infrastructure.security import PasswordManager

pm = PasswordManager()

# Validate password strength
is_valid, issues = pm.validate_password_strength("userpassword")
if not is_valid:
    print("Password issues:", issues)
```

### 6.3 Session Management

```python
from infrastructure.security import auth_manager

# Get session statistics
session_stats = auth_manager.session_manager.get_stats()
print(f"Active sessions: {session_stats['active_sessions']}")

# Force logout all sessions for a user
auth_manager.session_manager.invalidate_user_sessions("user_id")
```

### 6.4 Security Checklist

- [ ] Review access logs for anomalies
- [ ] Check for failed login attempts
- [ ] Verify SSL/TLS certificate validity
- [ ] Update security dependencies
- [ ] Rotate API keys if needed
- [ ] Review rate limiting effectiveness

---

## 7. Backup Procedures

### 7.1 Database Backup

```bash
# Manual backup via Railway CLI
railway run pg_dump -Fc > backup_$(date +%Y%m%d_%H%M%S).dump

# Restore from backup
railway run pg_restore -d $DATABASE_URL backup_file.dump
```

### 7.2 Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
RETENTION_DAYS=30

# Create backup
pg_dump -Fc $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.dump

# Compress
gzip $BACKUP_DIR/db_backup_$DATE.dump

# Clean old backups
find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: db_backup_$DATE.dump.gz"
```

### 7.3 Backup Verification

```bash
# List backups
ls -la /backups/*.dump.gz

# Verify backup integrity
pg_restore -l backup_file.dump.gz > /dev/null && echo "Backup is valid"

# Test restore to temporary database
createdb test_restore
pg_restore -d test_restore backup_file.dump.gz
dropdb test_restore
```

---

## 8. Incident Response

### 8.1 Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| P1 | Critical | 15 minutes | System down, data loss |
| P2 | High | 1 hour | Major feature broken |
| P3 | Medium | 4 hours | Minor feature issue |
| P4 | Low | 24 hours | UI bugs, typos |

### 8.2 Incident Response Steps

1. **Identify**: Determine scope and impact
2. **Communicate**: Notify stakeholders
3. **Mitigate**: Apply temporary fix
4. **Resolve**: Implement permanent fix
5. **Review**: Post-incident analysis

### 8.3 Common Issues and Resolutions

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Memory exhaustion | OOM errors, slow response | Restart service, investigate queries |
| Database connection exhausted | Connection refused | Check pool settings, restart |
| High CPU | Slow response, timeouts | Scale up, optimize queries |
| Disk full | Write failures | Clean logs, archive old data |

### 8.4 Emergency Contacts

```
# Update with your team contacts
On-Call Engineer: [Name] - [Phone]
DevOps Lead: [Name] - [Phone]
Database Admin: [Name] - [Phone]
```

---

## 9. Update Procedures

### 9.1 Pre-Update Checklist

- [ ] Backup database
- [ ] Test in staging environment
- [ ] Review changelog
- [ ] Prepare rollback plan
- [ ] Notify users of maintenance

### 9.2 Update Process

```bash
# 1. Backup current state
railway run pg_dump -Fc > pre_update_backup.dump

# 2. Deploy update
git push origin main

# 3. Run migrations
railway run alembic upgrade head

# 4. Verify deployment
curl https://your-app.railway.app/health

# 5. Monitor for errors
railway logs -f
```

### 9.3 Rollback Process

```bash
# 1. Revert to previous deployment
railway rollback

# 2. Rollback database if needed
railway run alembic downgrade -1

# 3. Verify system stability
curl https://your-app.railway.app/health
```

---

## Maintenance Schedule Summary

| Task | Frequency | Duration |
|------|-----------|----------|
| Health check | Daily | 5 min |
| Log review | Daily | 15 min |
| Performance review | Weekly | 30 min |
| Backup verification | Weekly | 15 min |
| Security scan | Monthly | 1 hour |
| Database optimization | Monthly | 1 hour |
| Dependency updates | Monthly | 2 hours |
| Full DR test | Quarterly | 4 hours |

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 2024 | System | Initial release |
