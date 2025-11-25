# Deployment Guide: PostgreSQL on Railway/Render

## Why PostgreSQL for Streamlit Cloud?

Streamlit Cloud uses an **ephemeral filesystem** - this means:
- SQLite databases are **deleted on every redeploy**
- Data loss occurs when the app sleeps or restarts
- ORM session objects become detached, causing `DetachedInstanceError`

**Solution**: Use an external PostgreSQL database (Railway, Render, Supabase, etc.)

---

## Option 1: Railway Deployment

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click **"New Project"** > **"Provision PostgreSQL"**
3. Once created, click on the PostgreSQL service
4. Go to **"Variables"** tab and copy `DATABASE_URL`

### Step 2: Configure Streamlit Cloud

1. Go to your Streamlit Cloud app settings
2. Navigate to **"Secrets"** section
3. Add the following secret:

```toml
# .streamlit/secrets.toml (for local testing)
# Or add in Streamlit Cloud Secrets UI

DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@YOUR_HOST.railway.app:5432/railway"
```

### Step 3: Update Environment Variables

In Streamlit Cloud:
1. Go to App Settings > Secrets
2. Add:
```
DATABASE_URL = "postgresql://..."
```

### Railway Pricing
- **Hobby Plan**: $5/month with $5 free credits
- **Pro Plan**: Usage-based pricing

---

## Option 2: Render Deployment

### Step 1: Create Render PostgreSQL

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** > **"PostgreSQL"**
3. Configure:
   - Name: `solar-pv-lims-db`
   - Region: Choose closest to your users
   - PostgreSQL Version: 15 or latest
   - Plan: Free (90-day) or Starter ($7/month)
4. Click **"Create Database"**
5. Copy the **"External Database URL"**

### Step 2: Configure Streamlit Cloud

Same as Railway - add the DATABASE_URL to Streamlit Cloud Secrets:

```toml
DATABASE_URL = "postgresql://solar_pv_lims_db_user:PASSWORD@HOST.render.com:5432/solar_pv_lims_db"
```

### Render Pricing
- **Free**: 90-day expiration, 1GB storage
- **Starter**: $7/month, persistent

---

## Option 3: Supabase (Recommended for Free Tier)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click **"New Project"**
3. Configure:
   - Name: `solar-pv-lims`
   - Database Password: Generate secure password
   - Region: Choose closest
4. Click **"Create new project"**
5. Go to **Settings > Database > Connection string**
6. Copy the **URI** connection string

### Step 2: Configure

```toml
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres"
```

### Supabase Pricing
- **Free**: 500MB database, unlimited API requests
- **Pro**: $25/month, 8GB database

---

## Configuration in Code

The `config/database.py` module automatically handles both SQLite and PostgreSQL:

```python
# Automatic detection from DATABASE_URL environment variable
# No code changes needed!

# For local development (SQLite):
# Leave DATABASE_URL unset or use config/settings.py default

# For production (PostgreSQL):
# Set DATABASE_URL environment variable
```

### How It Works

1. **Environment Variable Priority**: `DATABASE_URL` env var overrides config file
2. **URL Normalization**: Handles `postgres://` to `postgresql://` conversion
3. **Connection Pooling**: Optimized for Streamlit Cloud limits
4. **Session Management**: Proper cleanup to prevent connection leaks

---

## Local Development

### Using SQLite (Default)

No configuration needed. The app uses SQLite by default:
```
data/solar_pv_lims.db
```

### Using PostgreSQL Locally

1. Install PostgreSQL or use Docker:
```bash
docker run --name postgres-dev -e POSTGRES_PASSWORD=devpassword -p 5432:5432 -d postgres:15
```

2. Create database:
```bash
docker exec -it postgres-dev psql -U postgres -c "CREATE DATABASE solar_pv_lims;"
```

3. Set environment variable:
```bash
export DATABASE_URL="postgresql://postgres:devpassword@localhost:5432/solar_pv_lims"
```

4. Run app:
```bash
streamlit run app.py
```

---

## Streamlit Cloud Secrets Setup

### Method 1: Via UI

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app > Settings > Secrets
3. Add:
```toml
DATABASE_URL = "postgresql://user:password@host:5432/database"
```

### Method 2: Via secrets.toml

Create `.streamlit/secrets.toml` (DO NOT commit to git!):
```toml
DATABASE_URL = "postgresql://user:password@host:5432/database"
```

Add to `.gitignore`:
```
.streamlit/secrets.toml
```

---

## Troubleshooting

### DetachedInstanceError

**Cause**: Accessing SQLAlchemy ORM objects after session is closed.

**Fix**: Extract data to dicts INSIDE the session context:
```python
# WRONG - causes DetachedInstanceError
with get_db() as db:
    service_requests = db.query(ServiceRequest).all()
# Session closed here!
for sr in service_requests:
    print(sr.client_name)  # ERROR!

# CORRECT - extract data inside session
with get_db() as db:
    service_requests = db.query(ServiceRequest).all()
    sr_data = [
        {'id': sr.id, 'client_name': sr.client_name}
        for sr in service_requests
    ]
# Session closed, but we have plain dicts
for sr in sr_data:
    print(sr['client_name'])  # Works!
```

### Connection Pool Exhausted

**Cause**: Too many concurrent connections.

**Fix**: The database.py is configured with:
- `pool_size=5`: Base connections
- `max_overflow=10`: Burst capacity
- `pool_timeout=30`: Wait time for connection

### Foreign Key Constraint Errors

**Cause**: Data from previous sessions references deleted records.

**Fix**:
1. Use PostgreSQL for persistent storage
2. Clear session state on app restart:
```python
if 'initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.initialized = True
```

---

## Database Schema Migration

When deploying to a new PostgreSQL database:

```python
# The app automatically creates tables on first run
# via init_database() in app.py

# For manual migration:
from config.database import init_database
init_database()
```

---

## Security Best Practices

1. **Never commit credentials**: Add `secrets.toml` to `.gitignore`
2. **Use environment variables**: Set `DATABASE_URL` via hosting platform
3. **Rotate passwords**: Change database passwords periodically
4. **Use SSL**: Most hosted PostgreSQL requires SSL (automatic with Railway/Render)

---

## Quick Start Checklist

- [ ] Create PostgreSQL database (Railway/Render/Supabase)
- [ ] Copy DATABASE_URL connection string
- [ ] Add to Streamlit Cloud Secrets
- [ ] Redeploy app
- [ ] Verify with database health check in app
