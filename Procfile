# Railway/Heroku Procfile
# ========================
# Process types for Solar PV Testing LIMS-QMS System
# 
# CRITICAL: Uses health proxy to pass Railway's 5-minute healthcheck
# The health proxy starts immediately and launches Streamlit in background

# Web process - Health proxy (responds to healthchecks instantly)
web: python health_proxy.py

# Alternative: Direct Streamlit (takes 5+ minutes to start - causes healthcheck failures)
# web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false

# Worker process (optional) - for background tasks
# worker: python -m celery -A tasks worker --loglevel=info

# Release process (optional) - run on deployment
# release: python -c "from infrastructure.database import get_db_manager; db = get_db_manager(); db.init_db(); print('Database initialized')"
