# Railway/Heroku Procfile
# ========================
# Process types for Solar PV Testing LIMS-QMS System

# Web process - Streamlit application
web: streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.enableXsrfProtection=true --server.enableCORS=false
# Worker process (optional) - for background tasks
# worker: python -m celery -A tasks worker --loglevel=info

# Release process (optional) - run on deployment
# release: python -c "from infrastructure.database import get_db_manager; db = get_db_manager(); db.init_db(); print('Database initialized')"
