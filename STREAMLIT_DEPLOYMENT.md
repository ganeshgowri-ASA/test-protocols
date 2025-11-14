# Streamlit Cloud Deployment Guide
## Solar PV Testing LIMS-QMS System

**Version:** 1.0.0
**Last Updated:** 2024
**Deployment Target:** Streamlit Cloud

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Database Setup](#database-setup)
4. [Streamlit Cloud Configuration](#streamlit-cloud-configuration)
5. [Secrets Configuration](#secrets-configuration)
6. [Custom Domain Setup](#custom-domain-setup)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides step-by-step instructions for deploying the Solar PV Testing LIMS-QMS system to Streamlit Cloud. The application includes:

- **54 Solar PV Testing Protocols** (IEC 61215-2:2021 compliant)
- **Complete LIMS workflow**: Service Request → Inspection → Equipment → Testing
- **QMS features**: Traceability, QR codes, PDF reports, analytics
- **Production-ready**: Optimized for cloud deployment with proper error handling

**Target URL:** `https://pv-testing-lims-qms.streamlit.app`

---

## Pre-Deployment Checklist

Before deploying to Streamlit Cloud, ensure:

- ✅ All code is committed to the `deployment/streamlit-cloud` branch
- ✅ PostgreSQL database is provisioned (Supabase/Railway/Neon recommended)
- ✅ Database schema is created and migrations are run
- ✅ All secrets are documented (but NOT committed to git)
- ✅ Local testing completed successfully
- ✅ Dependencies are up to date in `requirements.txt`
- ✅ `.gitignore` includes `.streamlit/secrets.toml`

---

## Database Setup

### Option 1: Supabase (Recommended)

**Why Supabase?**
- Free tier with 500MB storage
- Built-in PostgreSQL database
- Automatic backups
- Easy to use dashboard
- Connection pooling included

**Setup Steps:**

1. **Create Account**
   - Go to [supabase.com](https://supabase.com)
   - Sign up with GitHub account (for easier integration)

2. **Create New Project**
   - Click "New Project"
   - Choose a project name: `pv-testing-lims-qms`
   - Set a strong database password (save it securely!)
   - Choose region closest to your users
   - Wait 2-3 minutes for provisioning

3. **Get Connection String**
   - Go to Project Settings → Database
   - Find "Connection string" section
   - Copy the "URI" format connection string
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

4. **Configure Database**
   ```sql
   -- Run these commands in the SQL Editor on Supabase dashboard

   -- Enable required extensions
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

   -- The application will create tables automatically via SQLAlchemy/Alembic
   -- Or you can run migrations manually (see below)
   ```

5. **Run Migrations (Optional - if auto-migration is disabled)**
   ```bash
   # Set your database URL
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

   # Run Alembic migrations
   alembic upgrade head
   ```

### Option 2: Railway

1. Create account at [railway.app](https://railway.app)
2. Create new project → Add PostgreSQL
3. Copy connection string from Variables tab
4. Format: `postgresql://postgres:[PASSWORD]@containers-us-west-xxx.railway.app:5432/railway`

### Option 3: Neon

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string
4. Format: `postgresql://[user]:[password]@[host]/[database]`

### Option 4: Local Development (SQLite)

For testing purposes only:

```toml
[database]
url = "sqlite:///lims_qms.db"
```

**⚠️ WARNING:** SQLite is not recommended for production on Streamlit Cloud as the file system is ephemeral.

---

## Streamlit Cloud Configuration

### Step 1: Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub account
3. Authorize Streamlit to access your repositories

### Step 2: Deploy New App

1. **Click "New app"** button
2. **Configure deployment:**
   - **Repository:** `ganeshgowri-ASA/test-protocols`
   - **Branch:** `deployment/streamlit-cloud`
   - **Main file path:** `app.py`
   - **App URL (custom):** `pv-testing-lims-qms` (if available)

3. **Advanced settings:**
   - **Python version:** 3.11 (recommended) or 3.10
   - Click "Advanced settings" before deploying

### Step 3: Configure Secrets (CRITICAL)

Before clicking "Deploy", you MUST configure secrets:

1. In the deployment dialog, click **"Advanced settings"**
2. Scroll to **"Secrets"** section
3. Paste your secrets configuration (see [Secrets Configuration](#secrets-configuration) below)
4. Click **"Save"**
5. Now click **"Deploy"**

---

## Secrets Configuration

### Production Secrets Template

Copy and customize this template in the Streamlit Cloud secrets editor:

```toml
# Database Configuration (REQUIRED)
[database]
url = "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
pool_size = 5
max_overflow = 10
pool_recycle = 3600

# Authentication (REQUIRED)
[auth]
secret_key = "GENERATE-A-STRONG-SECRET-KEY-HERE-USE-RANDOM-STRING"
cookie_name = "lims_qms_auth"
cookie_expiry_days = 30

# Admin credentials for initial setup (REQUIRED)
admin_username = "admin"
admin_password = "CHANGE-THIS-TO-STRONG-PASSWORD"
admin_email = "admin@yourcompany.com"

# Application Settings (REQUIRED)
[app]
debug_mode = false
max_upload_size_mb = 200
session_timeout_minutes = 60
environment = "production"

# Feature flags
enable_notifications = true
enable_analytics = true
enable_audit_logging = true

# File Storage (OPTIONAL)
[storage]
local_path = "./uploads"

# Email Notifications (OPTIONAL)
[email]
enabled = false
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "notifications@yourcompany.com"
sender_password = "YOUR-EMAIL-APP-PASSWORD"

# Logging (OPTIONAL)
[logging]
level = "INFO"
log_to_file = false
```

### How to Generate Strong Secret Key

Use Python to generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Updating Secrets After Deployment

1. Go to your app dashboard on Streamlit Cloud
2. Click ⋮ (three dots) → **Settings**
3. Navigate to **Secrets** section
4. Update the TOML configuration
5. Click **Save**
6. App will automatically restart with new secrets

---

## Custom Domain Setup (Optional)

### Using Streamlit Cloud Subdomain

Your app will be available at:
```
https://pv-testing-lims-qms.streamlit.app
```

### Using Your Own Domain

1. **In Streamlit Cloud:**
   - Go to app settings → **Sharing**
   - Find "Custom domain" section
   - Enter your domain: `lims.yourcompany.com`

2. **In Your DNS Provider:**
   - Add CNAME record:
     ```
     Type: CNAME
     Name: lims (or your subdomain)
     Value: streamlit.app
     TTL: 3600
     ```

3. **Wait for Propagation:**
   - DNS changes take 5-60 minutes
   - Verify with: `dig lims.yourcompany.com`

4. **SSL Certificate:**
   - Automatically provisioned by Streamlit Cloud
   - No configuration needed

---

## Post-Deployment Verification

### 1. Application Health Check

Visit your deployed app and verify:

- ✅ App loads without errors
- ✅ Home page displays correctly
- ✅ Database connection indicator shows "🟢 System Healthy"
- ✅ All navigation pages are accessible:
  - 📋 Service Request
  - 📦 Incoming Inspection
  - ⚙️ Equipment Booking
  - 🔬 Test Protocols

### 2. Test Core Features

**Test Protocol Selector:**
```
1. Go to "Test Protocols" page
2. Select protocol category (e.g., "Performance Testing")
3. Verify protocols are listed
4. Select a protocol (e.g., "P1 - I-V Performance")
5. Verify protocol form renders
```

**Test Database Operations:**
```
1. Create a new service request
2. Fill in required fields
3. Submit and verify data is saved
4. Reload page and verify data persists
```

**Test File Uploads:**
```
1. Go to Incoming Inspection
2. Upload a test file (any PDF/image)
3. Verify upload completes without errors
```

### 3. Performance Verification

- Page load time < 3 seconds
- No timeout errors
- Smooth navigation between pages
- Charts and visualizations render correctly

### 4. Health Dashboard

Visit the health dashboard (if implemented as a separate page):
- All system checks show green ✅
- Protocol count: 54/54 or as expected
- Database: Connected
- Dependencies: All available

---

## Monitoring & Maintenance

### Application Logs

**View Logs in Streamlit Cloud:**

1. Go to your app dashboard
2. Click ⋮ → **Logs**
3. View real-time application logs
4. Filter by date/time or search for errors

**Common Log Patterns to Monitor:**

```
✅ Good:
"Database connection established successfully"
"Application startup initiated"

⚠️ Warning:
"Protocol registry is empty"
"Database connection retry attempt"

🔴 Error:
"Database connection failed"
"Import error"
```

### Performance Monitoring

**Built-in Metrics:**
- Streamlit Cloud provides basic metrics:
  - Active users
  - Total views
  - Response times

**Access Metrics:**
1. App dashboard → **Analytics**
2. View usage trends
3. Monitor peak usage times

### Database Monitoring

**For Supabase:**
1. Go to Project Dashboard
2. Check Database size usage
3. Monitor active connections
4. Review slow queries

**Connection Pool Monitoring:**
- Monitor logs for "pool exhausted" errors
- Adjust `pool_size` in secrets if needed

### Regular Maintenance Tasks

**Weekly:**
- ✅ Review application logs for errors
- ✅ Check database storage usage
- ✅ Verify all features working

**Monthly:**
- ✅ Review and rotate secrets/passwords
- ✅ Update dependencies (`requirements.txt`)
- ✅ Backup database (if not auto-backed up)
- ✅ Review user feedback and issues

**Quarterly:**
- ✅ Security audit
- ✅ Performance optimization
- ✅ Feature updates based on user needs

---

## Troubleshooting

### Issue: App Won't Start / Stuck Loading

**Symptoms:**
- App shows "Running..." indefinitely
- Deployment fails during build

**Solutions:**

1. **Check Build Logs:**
   ```
   - Look for package installation errors
   - Verify Python version compatibility
   - Check for missing dependencies
   ```

2. **Verify requirements.txt:**
   ```
   - Ensure all packages have version specifiers
   - Check for conflicting dependencies
   - Try pinning exact versions if issues persist
   ```

3. **Review Secrets:**
   ```
   - Ensure all required secrets are configured
   - Verify TOML syntax is correct
   - Check for typos in secret keys
   ```

### Issue: Database Connection Failed

**Symptoms:**
- "Database connection failed" error
- Red indicator on dashboard

**Solutions:**

1. **Verify Connection String:**
   ```toml
   # Check format in secrets
   [database]
   url = "postgresql://user:password@host:port/database"

   # Common mistakes:
   - Missing password
   - Wrong host/port
   - Incorrect database name
   ```

2. **Check Database Status:**
   - Verify database is running (Supabase dashboard)
   - Check connection limits not exceeded
   - Test connection from another tool

3. **Firewall/Network:**
   - Ensure database allows connections from Streamlit Cloud IPs
   - Supabase: Check if "Allow all IP addresses" is enabled
   - Railway/Neon: Usually no restrictions needed

### Issue: Import Errors / Module Not Found

**Symptoms:**
- "ModuleNotFoundError: No module named 'X'"
- Import errors in logs

**Solutions:**

1. **Add to requirements.txt:**
   ```bash
   # Add the missing package
   echo "missing-package>=1.0.0" >> requirements.txt
   git commit -am "Add missing dependency"
   git push
   ```

2. **Trigger Reboot:**
   - Go to app settings → **Reboot app**

### Issue: File Upload Fails

**Symptoms:**
- Upload hangs or times out
- "File too large" errors

**Solutions:**

1. **Check Upload Size Limit:**
   ```toml
   # In .streamlit/config.toml
   [server]
   maxUploadSize = 200  # MB
   ```

2. **Verify File Type:**
   - Ensure file type is allowed
   - Check file format validation in code

### Issue: Slow Performance

**Symptoms:**
- Pages load slowly
- Timeout errors
- High latency

**Solutions:**

1. **Add Caching:**
   ```python
   @st.cache_data(ttl=300)
   def load_data():
       # Your data loading code
       pass
   ```

2. **Optimize Database Queries:**
   - Add indexes to frequently queried columns
   - Use query result pagination
   - Implement lazy loading

3. **Reduce Chart Complexity:**
   - Limit data points in visualizations
   - Use data aggregation
   - Implement data sampling for large datasets

### Issue: Secrets Not Loading

**Symptoms:**
- KeyError when accessing st.secrets
- Missing configuration values

**Solutions:**

1. **Verify Secrets Syntax:**
   ```toml
   # Correct:
   [database]
   url = "postgresql://..."

   # Incorrect:
   database.url = "postgresql://..."  # ❌ Wrong syntax
   ```

2. **Check Access Pattern:**
   ```python
   # Correct:
   db_url = st.secrets["database"]["url"]

   # Or with get() for optional secrets:
   debug = st.secrets.get("app", {}).get("debug_mode", False)
   ```

3. **Reboot App:**
   - After updating secrets, always reboot the app

### Issue: App Crashes / Unexpected Restarts

**Symptoms:**
- App randomly restarts
- "Oh no!" error page

**Solutions:**

1. **Check Memory Usage:**
   - Streamlit Cloud free tier: 1GB RAM limit
   - Reduce data loading
   - Clear cached data periodically

2. **Review Logs:**
   - Look for exception stack traces
   - Check for uncaught exceptions
   - Add try-except blocks around risky operations

3. **Add Error Handling:**
   ```python
   try:
       # Risky operation
       result = perform_operation()
   except Exception as e:
       logger.error(f"Operation failed: {e}")
       st.error("An error occurred. Please try again.")
   ```

### Getting Help

**Streamlit Community:**
- Forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- Documentation: [docs.streamlit.io](https://docs.streamlit.io)

**GitHub Issues:**
- Repository: `ganeshgowri-ASA/test-protocols`
- File issues for bugs or feature requests

**Direct Support:**
- Streamlit Cloud support: Available for paid tiers
- Email: support@streamlit.io

---

## Deployment Upgrade Path

### From Free Tier to Team/Enterprise

**When to Upgrade:**
- Need more resources (RAM/CPU)
- Custom authentication required
- Private repositories
- Multiple deployed apps
- Advanced analytics

**Benefits of Paid Tiers:**
- Increased resource limits
- Priority support
- SSO authentication
- Team collaboration features
- Advanced monitoring

**How to Upgrade:**
1. Go to Streamlit Cloud dashboard
2. Click on your account → **Billing**
3. Select appropriate plan
4. Follow upgrade instructions

---

## Backup & Recovery

### Database Backups

**Supabase:**
- Automatic daily backups (retained for 7 days on free tier)
- Manual backup: Project Dashboard → Database → Backups
- Download SQL dump for off-site storage

**Manual Backup:**
```bash
# Using pg_dump
pg_dump -h db.xxxxx.supabase.co -U postgres -d postgres > backup.sql

# Restore
psql -h db.xxxxx.supabase.co -U postgres -d postgres < backup.sql
```

### Application State

- Session data: Stored in Streamlit's session state (ephemeral)
- Uploaded files: Store in database or cloud storage (S3, GCS)
- Configuration: Version controlled in Git

### Disaster Recovery Plan

1. **Database Restore:**
   - Restore from Supabase backup
   - Or restore from manual SQL dump

2. **Application Redeploy:**
   - Code is in Git (always recoverable)
   - Redeploy from `deployment/streamlit-cloud` branch

3. **Secrets Restore:**
   - Keep encrypted backup of secrets.toml
   - Or maintain secrets in password manager

---

## Security Best Practices

### Secrets Management

- ✅ NEVER commit secrets to Git
- ✅ Use strong, unique passwords
- ✅ Rotate secrets regularly (quarterly)
- ✅ Use environment-specific secrets
- ✅ Document secrets in password manager

### Database Security

- ✅ Use SSL/TLS for database connections
- ✅ Restrict database access by IP (if possible)
- ✅ Use strong database passwords
- ✅ Enable connection pooling
- ✅ Regular security updates

### Application Security

- ✅ Enable XSRF protection (already configured)
- ✅ Validate all user inputs
- ✅ Sanitize file uploads
- ✅ Use parameterized database queries
- ✅ Implement rate limiting (if needed)
- ✅ Regular dependency updates

### Monitoring Security

- ✅ Monitor logs for suspicious activity
- ✅ Track failed authentication attempts
- ✅ Alert on unusual database queries
- ✅ Regular security audits

---

## Appendix

### A. Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `database.url` | PostgreSQL connection string | Yes | `postgresql://user:pass@host/db` |
| `database.pool_size` | Connection pool size | No | `5` |
| `auth.secret_key` | Session encryption key | Yes | `random-32-char-string` |
| `auth.cookie_name` | Authentication cookie name | No | `lims_qms_auth` |
| `app.debug_mode` | Enable debug logging | No | `false` |
| `app.environment` | Deployment environment | No | `production` |

### B. Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| Streamlit App | 8501 | HTTP/HTTPS |
| PostgreSQL | 5432 | TCP |

### C. Useful Commands

```bash
# Test database connection
psql "postgresql://user:pass@host/db" -c "SELECT version();"

# Check app status
curl -I https://pv-testing-lims-qms.streamlit.app

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# View requirements
pip list --format=freeze

# Export environment
pip freeze > requirements.txt
```

### D. Resource Links

- Streamlit Documentation: https://docs.streamlit.io
- Streamlit Cloud: https://share.streamlit.io
- Supabase: https://supabase.com
- Railway: https://railway.app
- Neon: https://neon.tech
- PostgreSQL: https://www.postgresql.org

---

## Conclusion

You should now have a fully deployed Solar PV Testing LIMS-QMS system running on Streamlit Cloud!

**Next Steps:**
1. ✅ Verify all features working
2. ✅ Configure custom domain (optional)
3. ✅ Set up monitoring and alerts
4. ✅ Document for your team
5. ✅ Train users on the system

**Support:**
- For deployment issues: Check [Troubleshooting](#troubleshooting) section
- For application bugs: File issue on GitHub
- For feature requests: Contact development team

---

**Document Version:** 1.0.0
**Last Updated:** 2024
**Maintained By:** Development Team
