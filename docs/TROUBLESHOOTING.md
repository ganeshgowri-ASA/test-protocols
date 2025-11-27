# Troubleshooting Guide
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Last Updated:** November 2024

---

## Table of Contents

1. [Common Issues](#1-common-issues)
2. [Database Issues](#2-database-issues)
3. [Authentication Issues](#3-authentication-issues)
4. [Performance Issues](#4-performance-issues)
5. [Deployment Issues](#5-deployment-issues)
6. [Railway-Specific Issues](#6-railway-specific-issues)
7. [Diagnostic Commands](#7-diagnostic-commands)
8. [Getting Help](#8-getting-help)

---

## 1. Common Issues

### 1.1 Application Won't Start

**Symptoms:**
- Blank page or error on load
- "Application error" message
- 502 Bad Gateway

**Diagnosis:**
```bash
# Check logs
railway logs --since 1h

# Check health endpoint
curl https://your-app.railway.app/healthz
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Missing environment variables | Add required variables in Railway dashboard |
| Database connection failed | Check DATABASE_URL, verify PostgreSQL service |
| Port binding issue | Ensure using `$PORT` environment variable |
| Memory exhaustion | Increase memory limit or optimize code |

**Fix Port Issue:**
```bash
# Procfile should use $PORT
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

### 1.2 Page Loads But Shows Errors

**Symptoms:**
- "st.exception: ..." errors
- Red error boxes in UI
- Partial page rendering

**Diagnosis:**
```python
# Check specific error in logs
railway logs | grep -i error

# Test locally with same environment
export DATABASE_URL="your_url"
streamlit run app.py
```

**Common Fixes:**

1. **Import Error**
   ```bash
   # Ensure all dependencies installed
   pip install -r requirements.txt
   ```

2. **Module Not Found**
   ```python
   # Check sys.path in app.py
   import sys
   sys.path.insert(0, '/app')
   ```

3. **Database Model Error**
   ```bash
   # Run migrations
   railway run alembic upgrade head
   ```

---

### 1.3 Slow Performance

**Symptoms:**
- Pages take >5 seconds to load
- Timeout errors
- Streamlit spinner stuck

**Quick Diagnosis:**
```python
# Add timing to identify slow operations
import time

start = time.time()
# ... operation ...
print(f"Operation took: {time.time() - start}s")
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Uncached database queries | Add `@st.cache_data` decorator |
| Large data processing | Use pagination, lazy loading |
| Missing indexes | Add database indexes |
| Memory pressure | Increase instance size |

---

## 2. Database Issues

### 2.1 Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
# Check database status
railway status

# Test connection
railway run python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.environ['DATABASE_URL'])
engine.connect()
print('Connected!')
"
```

**Solutions:**

1. **Check DATABASE_URL**
   ```bash
   # Verify URL format
   railway variables | grep DATABASE

   # Should be: postgresql://user:pass@host:port/db
   ```

2. **Fix postgres:// to postgresql://**
   ```python
   # In code
   url = os.getenv('DATABASE_URL', '')
   if url.startswith('postgres://'):
       url = url.replace('postgres://', 'postgresql://', 1)
   ```

3. **Check service linking**
   - Go to Railway Dashboard
   - Ensure PostgreSQL service is linked
   - Verify shared variables

---

### 2.2 Connection Pool Exhausted

**Error:**
```
QueuePool limit of size 10 overflow 20 reached
```

**Diagnosis:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity
WHERE datname = 'your_database';

-- See who's connected
SELECT pid, usename, application_name, state
FROM pg_stat_activity
WHERE datname = 'your_database';
```

**Solutions:**

1. **Increase pool size**
   ```bash
   # Set environment variables
   railway variables set DB_POOL_SIZE=20
   railway variables set DB_MAX_OVERFLOW=40
   ```

2. **Reduce connection leaks**
   ```python
   # Always use context manager
   with db_session() as session:
       # ... queries ...
   # Connection automatically returned
   ```

3. **Add connection timeout**
   ```bash
   railway variables set DB_POOL_TIMEOUT=30
   ```

---

### 2.3 Migration Errors

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision
```

**Solutions:**

1. **Reset migrations (development only)**
   ```bash
   # Delete migration versions
   rm -rf alembic/versions/*

   # Regenerate
   alembic revision --autogenerate -m "initial"
   alembic upgrade head
   ```

2. **Fix broken migration**
   ```bash
   # Check current revision
   alembic current

   # Manually set revision
   alembic stamp head
   ```

---

## 3. Authentication Issues

### 3.1 Login Fails

**Symptoms:**
- "Invalid credentials" for correct password
- Session immediately expires
- Can't access protected pages

**Diagnosis:**
```python
# Check password hash
from infrastructure.security import PasswordManager
pm = PasswordManager()

# Verify hash
is_valid = pm.verify_password("test_password", stored_hash)
print(f"Password valid: {is_valid}")
```

**Solutions:**

1. **Reset password**
   ```python
   # Generate new hash
   new_hash = pm.hash_password("new_password")

   # Update in database
   with db_session() as session:
       user = session.query(User).filter_by(username="admin").first()
       user.password_hash = new_hash
   ```

2. **Check SECRET_KEY**
   ```bash
   # Ensure consistent key
   railway variables | grep SECRET

   # If missing, set it
   railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   ```

---

### 3.2 Rate Limit Exceeded

**Error:**
```
429 Too Many Requests
```

**Diagnosis:**
```python
from infrastructure.security import rate_limiter

# Check rate limiter stats
stats = rate_limiter.get_stats()
print(f"Active clients: {stats['active_clients']}")
```

**Solutions:**

1. **Increase limits**
   ```bash
   railway variables set RATE_LIMIT_REQUESTS=200
   railway variables set RATE_LIMIT_WINDOW=60
   ```

2. **Reset specific client**
   ```python
   rate_limiter.reset("client_ip_address")
   ```

3. **Clear all limits**
   ```python
   rate_limiter.reset()  # Resets all
   ```

---

## 4. Performance Issues

### 4.1 Memory Usage Too High

**Symptoms:**
- OOM (Out of Memory) kills
- Slow garbage collection
- Increasing memory over time

**Diagnosis:**
```bash
# Check memory in Railway dashboard
# Or via metrics endpoint
curl https://your-app.railway.app/metrics | grep memory
```

**Solutions:**

1. **Clear Streamlit cache**
   ```python
   st.cache_data.clear()
   st.cache_resource.clear()
   ```

2. **Optimize data loading**
   ```python
   # Use chunked processing
   for chunk in pd.read_csv('large.csv', chunksize=1000):
       process(chunk)
   ```

3. **Profile memory**
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... code ...
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')[:10]
   ```

---

### 4.2 Slow Database Queries

**Diagnosis:**
```python
from infrastructure.database import get_db_manager

db = get_db_manager()
stats = db.metrics.get_stats()
print(f"Avg query time: {stats['avg_query_time_ms']}ms")
print(f"Slow queries: {stats['slow_query_count']}")
```

**Solutions:**

1. **Add indexes**
   ```sql
   -- Find slow queries
   EXPLAIN ANALYZE SELECT * FROM test_executions WHERE status = 'in_progress';

   -- Add index
   CREATE INDEX idx_test_status ON test_executions(status);
   ```

2. **Use eager loading**
   ```python
   # Instead of lazy loading
   session.query(TestExecution).options(
       joinedload(TestExecution.protocol)
   ).all()
   ```

3. **Cache results**
   ```python
   @st.cache_data(ttl=300)
   def get_protocols():
       return session.query(TestProtocol).all()
   ```

---

## 5. Deployment Issues

### 5.1 Build Fails

**Error:**
```
Build failed: pip install returned non-zero exit status
```

**Solutions:**

1. **Check requirements.txt**
   ```bash
   # Verify syntax
   pip check

   # Test install locally
   pip install -r requirements.txt
   ```

2. **Pin versions**
   ```text
   # Bad: numpy
   # Good: numpy==1.26.3
   ```

3. **Check Python version**
   ```bash
   # Ensure compatible Python version
   # In railway.toml or nixpacks.toml
   [build]
   pythonVersion = "3.11"
   ```

---

### 5.2 Deploy Succeeds But App Crashes

**Diagnosis:**
```bash
# Check deployment logs
railway logs --deployment

# Check for startup errors
railway logs | head -100
```

**Common Causes:**

| Issue | Fix |
|-------|-----|
| Missing env vars | Add to Railway dashboard |
| Wrong start command | Check Procfile/railway.toml |
| Import errors | Verify all modules in requirements.txt |
| Database not ready | Add startup delay or retry logic |

---

## 6. Railway-Specific Issues

### 6.1 Service Won't Deploy

**Symptoms:**
- Deployment stuck in "Building"
- "No matching service" error

**Solutions:**

1. **Link service**
   ```bash
   railway link
   # Select project and service
   ```

2. **Check build logs**
   ```bash
   railway logs --build
   ```

3. **Force redeploy**
   ```bash
   railway redeploy
   ```

---

### 6.2 Environment Variables Not Working

**Diagnosis:**
```bash
# List all variables
railway variables

# Check specific variable
railway run printenv DATABASE_URL
```

**Solutions:**

1. **Check variable scope**
   - Project-level vs Service-level
   - Ensure variable is in correct scope

2. **Reference syntax**
   ```bash
   # Railway variable reference
   ${{POSTGRES.DATABASE_URL}}
   ```

3. **Restart after changes**
   ```bash
   railway restart
   ```

---

### 6.3 Custom Domain Issues

**Symptoms:**
- SSL errors
- Domain not resolving
- "Site can't be reached"

**Solutions:**

1. **Verify DNS settings**
   ```bash
   nslookup your-domain.com
   dig your-domain.com
   ```

2. **Check Railway domain settings**
   - Go to Service Settings → Domains
   - Verify CNAME record points to Railway

3. **Wait for propagation**
   - DNS changes can take up to 48 hours
   - SSL certificates auto-provision after DNS

---

## 7. Diagnostic Commands

### Quick Health Check

```bash
#!/bin/bash
# health-check.sh

echo "=== Application Health ==="
curl -s https://your-app.railway.app/health | jq .

echo "\n=== Recent Errors ==="
railway logs --since 1h | grep -i error | tail -10

echo "\n=== Resource Usage ==="
railway status
```

### Database Diagnostics

```bash
#!/bin/bash
# db-diagnostics.sh

railway run python << 'EOF'
from infrastructure.database import get_db_manager

db = get_db_manager()

print("=== Connection Health ===")
health = db.health_check()
print(f"Status: {health['status']}")
print(f"Latency: {health.get('latency_ms', 'N/A')}ms")

print("\n=== Pool Stats ===")
pool = db.get_pool_stats()
for k, v in pool.items():
    print(f"{k}: {v}")

print("\n=== Query Metrics ===")
metrics = db.metrics.get_stats()
for k, v in metrics.items():
    print(f"{k}: {v}")
EOF
```

### Full System Check

```python
# system_check.py
from infrastructure.database import connection_health_check
from infrastructure.monitoring import health_checker, metrics_collector
from infrastructure.security import rate_limiter

def run_diagnostics():
    print("=" * 50)
    print("SYSTEM DIAGNOSTICS")
    print("=" * 50)

    # Database
    print("\n[Database]")
    db_health = connection_health_check()
    print(f"  Status: {db_health['status']}")

    # Health Checker
    print("\n[Health Checks]")
    health = health_checker.check_readiness()
    print(f"  Status: {health['status']}")
    for check in health.get('checks', []):
        print(f"  - {check['name']}: {check['status']}")

    # Metrics
    print("\n[Metrics]")
    metrics = metrics_collector.get_all_metrics()
    print(f"  Counters: {len(metrics.get('counters', {}))}")
    print(f"  Gauges: {len(metrics.get('gauges', {}))}")

    # Rate Limiter
    print("\n[Rate Limiter]")
    rl_stats = rate_limiter.get_stats()
    print(f"  Active clients: {rl_stats['active_clients']}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    run_diagnostics()
```

---

## 8. Getting Help

### Self-Service Resources

1. **Check documentation**
   - This troubleshooting guide
   - RAILWAY_DEPLOYMENT_RUNBOOK.md
   - MAINTENANCE_GUIDE.md

2. **Search logs**
   ```bash
   railway logs | grep -i "your error"
   ```

3. **Test locally**
   ```bash
   # Replicate environment
   export DATABASE_URL="..."
   streamlit run app.py
   ```

### Support Channels

| Resource | URL |
|----------|-----|
| Railway Documentation | https://docs.railway.app |
| Railway Status | https://status.railway.app |
| Railway Discord | https://discord.gg/railway |
| GitHub Issues | https://github.com/your-repo/issues |

### Information to Include in Support Requests

```
1. Error message (exact text)
2. Steps to reproduce
3. Environment (production/staging)
4. Recent changes
5. Relevant logs (last 100 lines)
6. Screenshot if UI issue
```

---

## Quick Reference: Error Code Lookup

| Error Code | Meaning | First Action |
|------------|---------|--------------|
| 500 | Internal Server Error | Check railway logs |
| 502 | Bad Gateway | Restart service |
| 503 | Service Unavailable | Check health endpoint |
| 504 | Gateway Timeout | Increase timeout, check DB |
| DATABASE_ERROR | DB operation failed | Check connection |
| AUTH_ERROR | Authentication failed | Verify credentials |
| RATE_LIMIT_EXCEEDED | Too many requests | Wait or increase limits |
| VALIDATION_ERROR | Invalid input | Check request data |

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 2024 | System | Initial release |
