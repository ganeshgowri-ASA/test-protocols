#!/bin/bash

###############################################################################
# Stop PV Testing Protocol Framework Services
###############################################################################

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Stop API server
if [ -f /tmp/pv_testing_api.pid ]; then
    log_info "Stopping API server..."
    kill $(cat /tmp/pv_testing_api.pid) 2>/dev/null || true
    rm /tmp/pv_testing_api.pid
fi

# Stop Celery worker
if [ -f /tmp/pv_testing_celery.pid ]; then
    log_info "Stopping Celery worker..."
    kill $(cat /tmp/pv_testing_celery.pid) 2>/dev/null || true
    rm /tmp/pv_testing_celery.pid
fi

# Stop Streamlit dashboard
if [ -f /tmp/pv_testing_streamlit.pid ]; then
    log_info "Stopping Streamlit dashboard..."
    kill $(cat /tmp/pv_testing_streamlit.pid) 2>/dev/null || true
    rm /tmp/pv_testing_streamlit.pid
fi

log_info "All services stopped"
