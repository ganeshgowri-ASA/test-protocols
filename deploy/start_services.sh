#!/bin/bash

###############################################################################
# Start PV Testing Protocol Framework Services
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Activate virtual environment
source venv/bin/activate

# Start Redis (if not running)
if ! pgrep -x "redis-server" > /dev/null; then
    log_info "Starting Redis..."
    redis-server --daemonize yes
fi

# Start PostgreSQL (if not running)
if ! pgrep -x "postgres" > /dev/null; then
    log_info "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Start API server
log_info "Starting API server on port 8000..."
uvicorn pv_testing.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
echo $API_PID > /tmp/pv_testing_api.pid

# Start Celery worker (for background tasks)
log_info "Starting Celery worker..."
celery -A pv_testing.tasks worker --loglevel=info &
CELERY_PID=$!
echo $CELERY_PID > /tmp/pv_testing_celery.pid

# Start Streamlit dashboard
log_info "Starting Streamlit dashboard on port 8501..."
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!
echo $STREAMLIT_PID > /tmp/pv_testing_streamlit.pid

sleep 3

log_info "=========================================="
log_info "Services Started Successfully!"
log_info "=========================================="
log_info "API Server: http://localhost:8000"
log_info "API Docs: http://localhost:8000/docs"
log_info "Dashboard: http://localhost:8501"
log_info "=========================================="
log_info "To stop services: ./deploy/stop_services.sh"
