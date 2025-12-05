#!/bin/bash
# =============================================================================
# Railway Startup Script with Database Migrations
# =============================================================================
# This script runs database migrations before starting the Streamlit app.
# It ensures the database schema is up-to-date on each deployment.
#
# Usage: ./scripts/start_with_migrations.sh
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "Solar PV Testing LIMS-QMS - Railway Startup"
echo "=============================================="
echo "Timestamp: $(date -Iseconds)"
echo ""

# Run database migrations
echo "Step 1: Running database migrations..."
python scripts/run_migration.py --verify

MIGRATION_STATUS=$?
if [ $MIGRATION_STATUS -ne 0 ]; then
    echo "WARNING: Migration had issues, but continuing with app startup..."
fi

echo ""
echo "Step 2: Starting Streamlit application..."
echo ""

# Start Streamlit with Railway's PORT
exec streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
