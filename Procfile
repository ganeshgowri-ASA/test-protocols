# Railway/Heroku Procfile
# ========================
# Process types for Solar PV Testing LIMS-QMS System

# Release phase - runs ONCE on each deployment (before web starts)
# This runs database migrations automatically
release: python scripts/run_migration.py --verify

# Web process - Streamlit application with migrations
web: bash scripts/start_with_migrations.sh

# Worker process (optional) - for background tasks
# worker: python -m celery -A tasks worker --loglevel=info
